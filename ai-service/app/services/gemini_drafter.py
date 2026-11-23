import json
import re
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from app.config import settings
from app.schemas import RestockItemAdvice, RestockItemInput, WhatsAppDraft
from app.services.fallback_drafter import (
    build_fallback_drafts,
    build_fallback_summary,
    build_wa_link,
    group_items_by_supplier,
)


def _passes_numeric_guardrail(text: str, expected_quantities: list[int]) -> bool:
    """Verify every server-computed recommended_qty appears verbatim in the LLM draft."""
    numbers_in_text = set(re.findall(r"\b\d+\b", text))
    return all(str(qty) in numbers_in_text for qty in expected_quantities)


def _call_gemini_json(prompt: str) -> dict:
    from google import genai

    client = genai.Client(api_key=settings.gemini_api_key)
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config={"response_mime_type": "application/json"},
    )
    return json.loads(response.text)


def generate_summary_and_drafts(
    inputs: list[RestockItemInput],
    advices: list[RestockItemAdvice],
) -> tuple[str, list[WhatsAppDraft], bool, str | None, str]:
    """Return (summary, drafts, fallback_used, fallback_reason, model_version)."""
    grouped = group_items_by_supplier(inputs, advices)
    if not grouped:
        return build_fallback_summary(advices), [], False, None, settings.gemini_model

    if not settings.is_llm_configured:
        return (
            build_fallback_summary(advices),
            build_fallback_drafts(inputs, advices),
            True,
            "llm_not_configured",
            "local-template-v1.0",
        )

    prompt_payload = {
        "suppliers": [
            {
                "supplier_id": sid,
                "supplier_name": data["supplier_name"],
                "orders": [
                    {"name": it.name, "recommended_qty": it.recommended_qty, "unit": it.unit}
                    for it in data["items"]
                ],
            }
            for sid, data in grouped.items()
        ]
    }
    prompt = (
        "Anda adalah asisten operasional Hidji Coffee & Matcha (Farmasi UGM). "
        "Buat ringkasan singkat restok (key 'summary') dan draf pesan WhatsApp sopan per supplier "
        "(key 'drafts': map supplier_id -> string pesan). "
        "ATURAN KERAS: Jangan mengubah angka recommended_qty yang diberikan. "
        f"Data pesanan: {json.dumps(prompt_payload, ensure_ascii=False)}"
    )

    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(_call_gemini_json, prompt)
            parsed = future.result(timeout=settings.llm_timeout_seconds)
    except FuturesTimeoutError:
        return (
            build_fallback_summary(advices),
            build_fallback_drafts(inputs, advices),
            True,
            "llm_timeout",
            "local-template-v1.0",
        )
    except Exception as exc:
        err_str = str(exc).lower()
        reason = "llm_quota_exceeded" if ("429" in err_str or "quota" in err_str) else "llm_error"
        return (
            build_fallback_summary(advices),
            build_fallback_drafts(inputs, advices),
            True,
            reason,
            "local-template-v1.0",
        )

    summary = str(parsed.get("summary", "")).strip() or build_fallback_summary(advices)
    raw_drafts = parsed.get("drafts", {})
    drafts: list[WhatsAppDraft] = []

    for supplier_id, data in grouped.items():
        msg = str(raw_drafts.get(supplier_id, "")).strip()
        expected_qtys = [it.recommended_qty for it in data["items"]]
        if not msg or not _passes_numeric_guardrail(msg, expected_qtys):
            return (
                build_fallback_summary(advices),
                build_fallback_drafts(inputs, advices),
                True,
                "numeric_guardrail_triggered",
                "local-template-v1.0",
            )
        drafts.append(
            WhatsAppDraft(
                supplier_id=supplier_id,
                supplier_name=data["supplier_name"],
                message=msg,
                wa_link=build_wa_link(data["supplier_phone"], msg),
            )
        )

    return summary, drafts, False, None, settings.gemini_model
