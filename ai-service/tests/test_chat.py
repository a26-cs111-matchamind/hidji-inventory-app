from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_chat_recipe_impact_with_snapshot():
    payload = {
        "text": "kalau sirup karamel habis, menu apa yang kena?",
        "stock_snapshot": [
            {
                "id": "KOP15",
                "name": "Sirup caramel",
                "current_stock": 0.125,
                "minimum_stock": 0.5,
                "unit": "botol",
                "status": "menipis",
            }
        ],
        "forecast": [],
    }
    res = client.post("/v1/chat", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["intent"] == "tanya_resep_sop"
    assert "Master_Bahan:KOP15" in body["sources"]
    assert len(body["actions"]) >= 1


def test_chat_out_of_context_guardrail():
    res = client.post("/v1/chat", json={"text": "prediksi cuaca yogyakarta hari ini?"})
    assert res.status_code == 200
    body = res.json()
    assert body["intent"] == "di_luar_konteks"
    assert body["actions"] == []
    assert "Hidji Coffee & Matcha" in body["answer"]
