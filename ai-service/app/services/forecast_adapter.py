from functools import lru_cache
from app.config import settings
from app.ml_forecast.inference_service import HidjiRestockForecaster
from app.schemas import ForecastDailyRequest, ForecastDailyResponse, ForecastPredictionItem


@lru_cache(maxsize=1)
def get_forecaster() -> HidjiRestockForecaster:
    return HidjiRestockForecaster(
        bundle_path=str(settings.forecast_bundle_path),
        master_path=str(settings.forecast_master_path),
    )


def _scale_factor_to_base(meta: dict, requested_unit: str) -> float:
    """Return multiplier from requested unit to DS base unit (Satuan_Baku)."""
    req = requested_unit.strip().lower()
    base = str(meta["Satuan_Baku"]).strip().lower()
    sheet = str(meta["Satuan_di_Lembar"]).strip().lower()

    if req == base:
        return 1.0
    if req == sheet and sheet != base:
        return float(meta["Isi_per_Kemasan"])
    return 1.0


def run_daily_forecast(payload: ForecastDailyRequest) -> ForecastDailyResponse:
    forecaster = get_forecaster()
    predictions: list[ForecastPredictionItem] = []
    model_versions_used: set[str] = set()

    for mat in payload.materials:
        if mat.material_id not in forecaster.master_bahan:
            raise ValueError(f"Material ID '{mat.material_id}' tidak terdaftar di master_bahan_ref.json")

        meta = forecaster.master_bahan[mat.material_id]
        scale = _scale_factor_to_base(meta, mat.unit)

        sorted_history = sorted(mat.history, key=lambda h: h.date)
        ds_history = [
            {"tanggal": h.date, "pemakaian_baku": h.used_qty * scale}
            for h in sorted_history
        ]

        # HidjiRestockForecaster requires sisa_stok_closing_baku; 0.0 is neutral for demand prediction
        ds_result = forecaster.predict_item({
            "id_bahan": mat.material_id,
            "sisa_stok_closing_baku": 0.0,
            "riwayat_pemakaian": ds_history,
        })

        model_versions_used.add(ds_result["model_digunakan"])
        pred_in_req_unit = round(ds_result["proyeksi_pemakaian_besok_baku"] / scale, 2)

        last_7 = sorted_history[-7:]
        ma7 = round(sum(h.used_qty for h in last_7) / len(last_7), 2) if last_7 else 0.0

        predictions.append(
            ForecastPredictionItem(
                material_id=mat.material_id,
                forecast_next_day=pred_in_req_unit,
                unit=mat.unit,
                baseline_ma7=ma7,
            )
        )

    # Normalize DS model version label to match API contract naming when Ridge was used
    if forecaster.model_version in model_versions_used:
        version_label = "ridge-regression-v1.0"
    elif model_versions_used:
        version_label = next(iter(model_versions_used)).replace("_", "-")
    else:
        version_label = "ridge-regression-v1.0"

    return ForecastDailyResponse(
        target_date=payload.target_date,
        model_version=version_label,
        predictions=predictions,
    )
