from fastapi import APIRouter
from app.config import settings
from app.schemas import ChatAction, ChatRequest, ChatResponse
from app.services.intent_baseline import classify_intent
from app.services.kb_loader import get_knowledge_base

router = APIRouter(prefix="/v1", tags=["Chat Assistant"])

OUT_OF_CONTEXT_ANSWER = (
    "Maaf, saya hanya dapat membantu informasi stok bahan baku, "
    "resep menu, dan penyusunan draf pesanan supplier untuk Hidji Coffee & Matcha."
)


@router.post("/chat", response_model=ChatResponse)
def assistant_chat(payload: ChatRequest) -> ChatResponse:
    intent_res = classify_intent(payload.text)
    kb = get_knowledge_base()
    snapshot_map = {s.id: s for s in payload.stock_snapshot}
    forecast_map = {f.id: f for f in payload.forecast}

    if intent_res.intent == "di_luar_konteks":
        return ChatResponse(
            intent="di_luar_konteks",
            confidence=intent_res.confidence,
            answer=OUT_OF_CONTEXT_ANSWER,
            sources=[],
            actions=[],
            fallback_used=False,
            model_version=settings.intent_model_version,
        )

    sources: list[str] = []
    actions: list[ChatAction] = []

    if intent_res.intent == "tanya_resep_sop":
        matched_menus = kb.find_menus_in_text(intent_res.normalized_text)
        if matched_menus:
            menu = matched_menus[0]
            recipes = kb.get_recipes_for_menu(menu["id"])
            sources.append(f"Menu:{menu['id']}")
            if recipes:
                ing_list = ", ".join(
                    f"{ing['material_name']} {ing['amount']} {ing['unit']}"
                    for ing in recipes[0].get("ingredients", [])[:5]
                )
                answer = f"Resep {menu['name']} ({recipes[0]['variant']}): {ing_list}."
            else:
                cands = ", ".join(menu.get("candidate_ingredients", []))
                answer = f"Komposisi utama {menu['name']}: {cands}."
        elif intent_res.entities:
            mat_id = intent_res.entities[0]
            mat = kb.materials[mat_id]
            affected_records = kb.get_affected_menu_records(mat_id)
            sources.append(f"Master_Bahan:{mat_id}")
            sources.extend(f"Menu:{m['id']}" for m in affected_records[:5])

            if affected_records:
                menu_desc = ", ".join(f"{m['name']} ({m['id']})" for m in affected_records)
                answer = f"{mat['name']} dipakai di {len(affected_records)} menu: {menu_desc}."
            else:
                answer = f"{mat['name']} ({mat_id}) merupakan kebutuhan operasional bar dan belum terikat ke menu spesifik."

            if mat_id in snapshot_map:
                snap = snapshot_map[mat_id]
                answer += f" Sisa stok saat ini {snap.current_stock:g} {snap.unit} (batas minimum {snap.minimum_stock:g} {snap.unit})."
                actions.append(ChatAction(type="navigate", target="/restock", label="Buka Menu Restock"))
        else:
            answer = "Sebutkan nama menu atau bahan baku Hidji yang ingin dicek resep dan dampaknya."

        return ChatResponse(
            intent=intent_res.intent,
            confidence=intent_res.confidence,
            answer=answer,
            sources=sources,
            actions=actions,
            fallback_used=False,
            model_version=settings.intent_model_version,
        )

    if intent_res.intent in ("cek_stok", "minta_rekomendasi", "buat_draf_pesanan"):
        if intent_res.entities:
            lines: list[str] = []
            for mat_id in intent_res.entities:
                sources.append(f"Master_Bahan:{mat_id}")
                mat_name = kb.materials[mat_id]["name"]
                if mat_id in snapshot_map:
                    snap = snapshot_map[mat_id]
                    fc_note = ""
                    if mat_id in forecast_map:
                        fc = forecast_map[mat_id]
                        fc_note = f", proyeksi besok {fc.forecast_next_day:g} {fc.unit}"
                    lines.append(
                        f"{mat_name}: sisa {snap.current_stock:g} {snap.unit} "
                        f"(min {snap.minimum_stock:g} {snap.unit}{fc_note})"
                    )
                else:
                    lines.append(f"{mat_name} ({mat_id}) terdaftar di master bahan, tetapi data stok terbaru belum tersedia di sesi ini.")
            answer = " ".join(lines)
        elif payload.stock_snapshot:
            low_items = [s for s in payload.stock_snapshot if s.current_stock <= s.minimum_stock]
            if low_items:
                names = ", ".join(f"{s.name} ({s.current_stock:g} {s.unit})" for s in low_items[:5])
                answer = f"Terdapat {len(low_items)} bahan menipis/habis: {names}."
            else:
                answer = "Seluruh bahan pada snapshot stok saat ini berada di atas batas minimum."
        else:
            answer = "Belum ada data snapshot stok yang dikirim. Silakan buka halaman Restock untuk melihat rekomendasi terbaru."

        if intent_res.intent in ("minta_rekomendasi", "buat_draf_pesanan"):
            actions.append(ChatAction(type="navigate", target="/restock", label="Buka Menu Restock"))

        return ChatResponse(
            intent=intent_res.intent,
            confidence=intent_res.confidence,
            answer=answer,
            sources=sources,
            actions=actions,
            fallback_used=False,
            model_version=settings.intent_model_version,
        )

    # lapor_kendala_stok
    actions.append(ChatAction(type="navigate", target="/closing", label="Catat Penyesuaian Closing"))
    return ChatResponse(
        intent="lapor_kendala_stok",
        confidence=intent_res.confidence,
        answer="Laporan kendala bahan dicatat. Silakan perbarui angka sisa fisik di menu Closing Stok agar selisih tercatat akurat.",
        sources=[f"Master_Bahan:{mid}" for mid in intent_res.entities],
        actions=actions,
        fallback_used=False,
        model_version=settings.intent_model_version,
    )
