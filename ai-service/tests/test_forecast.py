from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_forecast_daily_ridge_with_liter_to_ml_conversion():
    payload = {
        "target_date": "2026-11-24",
        "materials": [
            {
                "material_id": "KOP03",
                "unit": "liter",
                "history": [
                    {"date": "2026-11-18", "used_qty": 4.0},
                    {"date": "2026-11-19", "used_qty": 4.5},
                    {"date": "2026-11-20", "used_qty": 5.0},
                    {"date": "2026-11-21", "used_qty": 4.2},
                    {"date": "2026-11-23", "used_qty": 4.6},
                ],
            }
        ],
    }
    res = client.post("/v1/forecast/daily", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "success"
    assert body["model_version"] == "ridge-regression-v1.0"
    pred = body["predictions"][0]
    assert pred["material_id"] == "KOP03"
    assert pred["unit"] == "liter"
    # Predicted liter demand must remain on liter scale (< 20), not ml scale
    assert 0.0 < pred["forecast_next_day"] <= 20.0
    assert pred["baseline_ma7"] == 4.46


def test_forecast_daily_short_history_falls_back_to_ma5():
    payload = {
        "target_date": "2026-11-24",
        "materials": [
            {
                "material_id": "KOP01",
                "unit": "gram",
                "history": [
                    {"date": "2026-11-21", "used_qty": 200.0},
                    {"date": "2026-11-22", "used_qty": 300.0},
                ],
            }
        ],
    }
    res = client.post("/v1/forecast/daily", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["predictions"][0]["forecast_next_day"] == 250.0


def test_forecast_unknown_material_returns_404():
    payload = {
        "target_date": "2026-11-24",
        "materials": [{"material_id": "UNKNOWN99", "unit": "pcs", "history": []}],
    }
    res = client.post("/v1/forecast/daily", json=payload)
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "NOT_FOUND"


def test_forecast_kop02_routes_safely_without_zero_clip():
    payload = {
        "target_date": "2026-11-24",
        "materials": [
            {
                "material_id": "KOP02",
                "unit": "ml",
                "history": [
                    {"date": "2026-11-18", "used_qty": 19000.0},
                    {"date": "2026-11-19", "used_qty": 19000.0},
                    {"date": "2026-11-20", "used_qty": 19000.0},
                    {"date": "2026-11-21", "used_qty": 19000.0},
                    {"date": "2026-11-23", "used_qty": 19000.0},
                ],
            }
        ],
    }
    res = client.post("/v1/forecast/daily", json=payload)
    assert res.status_code == 200
    assert res.json()["predictions"][0]["forecast_next_day"] == 19000.0
