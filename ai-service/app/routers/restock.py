from fastapi import APIRouter
from app.schemas import RestockAdviceRequest, RestockAdviceResponse
from app.services.gemini_drafter import generate_summary_and_drafts
from app.services.restock_calculator import calculate_restock_items

router = APIRouter(prefix="/v1", tags=["Restock Advisor"])


@router.post("/restock/advice", response_model=RestockAdviceResponse)
def restock_advice(payload: RestockAdviceRequest) -> RestockAdviceResponse:
    advices = calculate_restock_items(payload.items)
    summary, drafts, fallback_used, fallback_reason, model_version = generate_summary_and_drafts(
        payload.items,
        advices,
    )
    return RestockAdviceResponse(
        summary=summary,
        items=advices,
        drafts=drafts,
        fallback_used=fallback_used,
        fallback_reason=fallback_reason,
        model_version=model_version,
    )
