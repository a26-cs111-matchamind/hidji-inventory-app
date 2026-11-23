import math
from typing import Literal
from app.schemas import RestockItemAdvice, RestockItemInput
from app.services.kb_loader import get_knowledge_base


def determine_stock_status(current_stock: float, minimum_stock: float) -> Literal["aman", "menipis", "habis"]:
    if current_stock <= 0:
        return "habis"
    if current_stock <= minimum_stock:
        return "menipis"
    return "aman"


def calculate_restock_items(items: list[RestockItemInput]) -> list[RestockItemAdvice]:
    """Compute deterministic restock quantities without any LLM involvement."""
    kb = get_knowledge_base()
    results: list[RestockItemAdvice] = []

    for item in items:
        status = determine_stock_status(item.current_stock, item.minimum_stock)
        affected_menus = kb.get_affected_menus(item.id)

        if status == "aman" and (item.forecast_next_day is None or item.current_stock >= item.minimum_stock + item.forecast_next_day):
            recommended_qty = 0
            reason = f"Stok {item.current_stock:g} {item.unit} masih aman di atas batas minimum {item.minimum_stock:g} {item.unit}."
        else:
            if item.forecast_next_day is not None:
                target_stock = max(
                    item.minimum_stock * 2.0,
                    item.forecast_next_day * (item.lead_time_days + 1),
                )
            else:
                target_stock = item.minimum_stock * 2.0

            deficit = max(0.0, target_stock - item.current_stock)
            if deficit > 0:
                packs_needed = math.ceil(deficit / item.pack_size)
                recommended_qty = int(math.ceil(packs_needed * item.pack_size))
            else:
                recommended_qty = 0

            forecast_note = (
                f" dengan proyeksi pemakaian besok {item.forecast_next_day:g} {item.unit}"
                if item.forecast_next_day is not None
                else ""
            )
            reason = (
                f"Sisa {item.current_stock:g} {item.unit} di bawah batas minimum "
                f"{item.minimum_stock:g} {item.unit}{forecast_note}."
            )

        results.append(
            RestockItemAdvice(
                id=item.id,
                name=item.name,
                stock_status=status,
                recommended_qty=recommended_qty,
                unit=item.unit,
                affected_menus=affected_menus,
                reason=reason,
            )
        )

    return results
