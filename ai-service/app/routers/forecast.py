from fastapi import APIRouter, HTTPException
from app.schemas import ForecastDailyRequest, ForecastDailyResponse
from app.services.forecast_adapter import run_daily_forecast

router = APIRouter(prefix="/v1", tags=["Forecasting"])


@router.post("/forecast/daily", response_model=ForecastDailyResponse)
def forecast_daily(payload: ForecastDailyRequest) -> ForecastDailyResponse:
    try:
        return run_daily_forecast(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": str(exc)},
        ) from exc
