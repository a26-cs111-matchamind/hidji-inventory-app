from fastapi import APIRouter
from app.config import settings
from app.schemas import HealthResponse
from app.services.forecast_adapter import get_forecaster
from app.services.kb_loader import get_knowledge_base

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    kb_ready = bool(get_knowledge_base().materials)
    forecaster = get_forecaster()
    forecast_ready = bool(forecaster.models) or (forecaster.single_model is not None)
    return HealthResponse(
        status="ok",
        model_loaded=kb_ready and forecast_ready,
        model_version=settings.intent_model_version,
        llm_available=settings.is_llm_configured,
        llm_model=settings.gemini_model,
    )
