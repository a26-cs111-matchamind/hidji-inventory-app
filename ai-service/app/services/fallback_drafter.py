from collections import defaultdict
from urllib.parse import quote
from app.schemas import RestockItemAdvice, RestockItemInput, WhatsAppDraft


def build_wa_link(phone: str, message: str) -> str:
    clean_phone = "".join(ch for ch in phone if ch.isdigit())
    encoded_msg = quote(message, safe="")
    if not clean_phone:
        return f"https://wa.me/?text={encoded_msg}"
    return f"https://wa.me/{clean_phone}?text={encoded_msg}"


def group_items_by_supplier(
    inputs: list[RestockItemInput],
    advices: list[RestockItemAdvice],
) -> dict[str, dict]:
    input_map = {item.id: item for item in inputs}
    grouped: dict[str, dict] = defaultdict(lambda: {"supplier_name": "", "supplier_phone": "", "items": []})

    for advice in advices:
        if advice.recommended_qty <= 0:
            continue
        src = input_map[advice.id]
        bucket = grouped[src.supplier_id]
        bucket["supplier_name"] = src.supplier_name
        bucket["supplier_phone"] = src.supplier_phone
        bucket["items"].append(advice)

    return dict(grouped)


def build_fallback_summary(advices: list[RestockItemAdvice]) -> str:
    critical = [a for a in advices if a.recommended_qty > 0]
    if not critical:
        return "Seluruh stok bahan baku saat ini berada pada status aman dan belum memerlukan pemesanan."

    highlights = ", ".join(f"{a.name} (saran beli {a.recommended_qty} {a.unit})" for a in critical[:3])
    suffix = " dan lainnya" if len(critical) > 3 else ""
    return (
        f"Terdapat {len(critical)} bahan yang perlu segera dipesan: {highlights}{suffix}. "
        "Prioritaskan pemesanan sebelum operasional besok pagi."
    )


def build_fallback_drafts(
    inputs: list[RestockItemInput],
    advices: list[RestockItemAdvice],
) -> list[WhatsAppDraft]:
    grouped = group_items_by_supplier(inputs, advices)
    drafts: list[WhatsAppDraft] = []

    for supplier_id, group in grouped.items():
        order_lines = ", ".join(
            f"{item.name} sebanyak {item.recommended_qty} {item.unit}"
            for item in group["items"]
        )
        msg = (
            f"Halo {group['supplier_name']}, kami dari Hidji Coffee & Matcha (Farmasi UGM) "
            f"ingin memesan {order_lines} untuk pengiriman besok pagi. "
            "Mohon konfirmasi ketersediaan stoknya. Terima kasih!"
        )
        drafts.append(
            WhatsAppDraft(
                supplier_id=supplier_id,
                supplier_name=group["supplier_name"],
                message=msg,
                wa_link=build_wa_link(group["supplier_phone"], msg),
            )
        )

    return drafts
