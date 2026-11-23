from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_restock_advice_deterministic_and_local_fallback():
    payload = {
        "date": "2026-11-23",
        "items": [
            {
                "id": "KOP03",
                "name": "Susu UHT",
                "unit": "liter",
                "current_stock": 1.5,
                "minimum_stock": 3.0,
                "forecast_next_day": 4.5,
                "lead_time_days": 1,
                "pack_size": 1,
                "supplier_id": "SUPP-01",
                "supplier_name": "Supplier Susu Diamond",
                "supplier_phone": "6281234567890",
            },
            {
                "id": "KOP15",
                "name": "Sirup caramel",
                "unit": "botol",
                "current_stock": 0.125,
                "minimum_stock": 0.5,
                "forecast_next_day": 0.25,
                "lead_time_days": 1,
                "pack_size": 1,
                "supplier_id": "SUPP-02",
                "supplier_name": "Supplier Bahan Kopi Jogja",
                "supplier_phone": "6281987654321",
            },
        ],
    }
    res = client.post("/v1/restock/advice", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "success"

    kop03 = next(it for it in body["items"] if it["id"] == "KOP03")
    assert kop03["stock_status"] == "menipis"
    # max(3*2, 4.5*(1+1)) - 1.5 = 9 - 1.5 = 7.5 -> ceil to 8
    assert kop03["recommended_qty"] == 8
    assert len(kop03["affected_menus"]) > 0

    assert len(body["drafts"]) == 2
    assert body["drafts"][0]["wa_link"].startswith("https://wa.me/")
    assert body["fallback_used"] is True
