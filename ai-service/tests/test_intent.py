from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_intent_cek_stok_with_slang_and_entities():
    res = client.post("/v1/intent", json={"text": "susu uht sama sirup karamel sisa brp ya?", "top_k": 3})
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "success"
    assert body["intent"] == "cek_stok"
    assert "KOP03" in body["entities"]
    assert "KOP15" in body["entities"]
    assert len(body["top_k"]) == 3
    assert body["latency_ms"] >= 0


def test_intent_buat_draf_pesanan():
    res = client.post("/v1/intent", json={"text": "buatin draf whatsapp order ke supplier dong"})
    assert res.status_code == 200
    assert res.json()["intent"] == "buat_draf_pesanan"


def test_intent_tanya_resep_sop():
    res = client.post("/v1/intent", json={"text": "takaran resep matcha latte brp ml ya?"})
    assert res.status_code == 200
    assert res.json()["intent"] == "tanya_resep_sop"


def test_intent_lapor_kendala_stok():
    res = client.post("/v1/intent", json={"text": "lapor susu uht tumpah 1 liter di bar"})
    assert res.status_code == 200
    assert res.json()["intent"] == "lapor_kendala_stok"


def test_intent_di_luar_konteks():
    res = client.post("/v1/intent", json={"text": "siapa presiden indonesia sekarang?"})
    assert res.status_code == 200
    assert res.json()["intent"] == "di_luar_konteks"


def test_intent_validation_error_format():
    res = client.post("/v1/intent", json={"text": ""})
    assert res.status_code == 422
    body = res.json()
    assert body["status"] == "error"
    assert body["error"]["code"] == "VALIDATION_ERROR"
