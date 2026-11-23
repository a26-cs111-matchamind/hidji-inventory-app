from fastapi import APIRouter
from app.schemas import IntentRequest, IntentResponse
from app.services.intent_baseline import classify_intent

router = APIRouter(prefix="/v1", tags=["Intent NLP"])


@router.post("/intent", response_model=IntentResponse)
def detect_intent(payload: IntentRequest) -> IntentResponse:
    return classify_intent(payload.text, top_k=payload.top_k)
