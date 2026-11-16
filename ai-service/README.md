# AI Service — Next-Gen AI Restock Advisor

## Deskripsi
Microservice berbasis **FastAPI** yang menggabungkan:
1. **Model NLP Mandiri (Main Quest):** Model Klasifikasi Intent terlatih sendiri (TF-IDF vs Keras BiLSTM) untuk mengenali perintah dan pertanyaan staf terkait stok.
2. **Generative AI Pipeline (Side Quest):** Google Gemini API untuk menyusun draf pesan WhatsApp supplier yang santun dan profesional.
3. **Zero Hallucination Mechanism:** Kuantitas restok dihitung secara deterministik oleh server; LLM hanya menyusun formulasi narasi teks. Dilengkapi fallback rule-based template deterministik jika layanan AI eksternal/lokal offline.

## Tech Stack & Framework
* **Runtime:** Python 3.10+
* **Framework:** FastAPI + Uvicorn
* **Model NLP Mandiri:** Scikit-learn (TF-IDF + LinearSVC/Logistic Regression) & TensorFlow/Keras (BiLSTM)
* **Generative AI:** Google GenAI SDK (Gemini API via Environment Variable)
* **Dokumentasi API:** Auto-generated Swagger UI di `/docs`

## Endpoint Utama
* `GET /health`: Health check status service & ketersediaan model
* `POST /v1/intent`: Klasifikasi intent ucapan pengguna (`cek_stok`, `minta_rekomendasi`, `buat_draf_pesanan`, `tanya_resep_sop`, `di_luar_konteks`)
* `POST /v1/restock/advice`: Merangkum rekomendasi belanja & menghasilkan draf WhatsApp ke supplier

## Setup & Menjalankan Lokal
```bash
cd ai-service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000
```
Swagger UI interaktif: `http://localhost:8000/docs`
