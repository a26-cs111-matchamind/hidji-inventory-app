# AI Service — Next-Gen AI & Forecast Gateway

## Deskripsi
Microservice **FastAPI** untuk tim Matchamind × Hidji Coffee & Matcha yang menyediakan:
1. **Intent Classification (`/v1/intent`):** Mengklasifikasikan 6 intent operasional barista/GM dengan normalisasi slang dan ekstraksi entitas bahan (`hidji_knowledge_base.json`).
2. **Daily Demand Forecasting (`/v1/forecast/daily`):** Meng-host model Ridge Regression v1.0 (`HidjiRestockForecaster`) dari tim Data Science beserta adapter konversi satuan otomatis.
3. **Restock Advisor (`/v1/restock/advice`):** Perhitungan kuantitas restok deterministik (*zero-hallucination*) + draf pesan WhatsApp supplier via Google Gemini API dengan *numeric guardrail* dan *local template fallback*.
4. **Chat Assistant (`/v1/chat`):** Pipeline intent-router untuk cek stok, dampak resep BOM, dan penolakan pertanyaan di luar konteks.

## Setup & Menjalankan Lokal
```bash
cd ai-service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Swagger UI interaktif: `http://localhost:8000/docs`

## Menjalankan Pengujian
```bash
pytest -v
```
