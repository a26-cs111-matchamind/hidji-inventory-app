# Matchamind — Hidji Inventory App & Smart Restock Advisor
> **Sistem Informasi Manajemen Persediaan dan Rekomendasi Restock Bahan Baku Hidji Coffee & Matcha**  
> *Program Capstone Asah 2026 (Led by Dicoding, Supported by GoTo)*  
> **ID Tim:** A26-CS111 | **Nama Tim:** Matchamind

---

## 1. Anggota Tim & Pembagian Peran (6 Orang)

| No | Nama Anggota | ID Peserta | Learning Path | Tanggung Jawab Utama |
| :-: | :--- | :---: | :--- | :--- |
| 1 | **Ilyas Nur Rohman** | `fs183b6y0789` | AI Full Stack Developer | Backend REST API Express, JWT Auth & Database Schema |
| 2 | **Melsindy Aulia Febiola** | `fs183b6x0976` | AI Full Stack Developer | Frontend React PWA (Form Input Closing & Stok Masuk) |
| 3 | **Wasima Juhaina** | `fs183b6x1769` | AI Full Stack Developer | Frontend Dasbor GM, State Management & Integrasi API |
| 4 | **Muhammad Alwi Marom** | `ds183b6y1090` | Data Science Specialist | Data Wrangling, EDA Tren Konsumsi & Dataset Sintetis |
| 5 | **Lulu Noviyanti** | `ds183b6x0921` | Data Science Specialist | Pemodelan Peramalan (Forecasting) & Metrik Evaluasi |
| 6 | **Yudistira Dani Azfa Wibowo** | `ae183b6y1800` | Next-Gen AI Engineer *(Lead AI)* | Model NLP Intent Classifier, Gemini REST API & Fallback |

---

## 2. Struktur Monorepo

```text
hidji-inventory-app/
├── frontend/               # [Full-Stack] React 18 + Vite + Tailwind CSS (PWA Mobile-first)
├── backend/                # [Full-Stack] Node.js + Express REST API (Auth, CRUD, Deterministic Restock)
├── data-science/           # [Data Science] EDA, Synthetic Dataset & Forecasting Models (Scikit-learn)
├── ai-service/             # [Next-Gen AI] FastAPI, Intent Classifier (BiLSTM/TF-IDF), Gemini API & RAG
├── docs/                   # [Semua] API Contract, Skema Database, & Dokumentasi Arsitektur
├── .gitignore              # Unified Git ignore rules (Node.js + Python + Secrets)
└── README.md               # Dokumentasi utama proyek
```

---

## 3. Strategi Kolaborasi (Branching Strategy)

* **`main`**: Kode stabil dan teruji yang siap digunakan untuk demo dan penilaian akhir *(Protected Branch)*.
* **`dev`**: Branch integrasi harian tempat seluruh fitur dari 3 peran digabungkan.
* **Feature Branches (`feat/*`)**: Dibuat dari `dev` untuk tiap tugas:
  * Full-Stack: `feat/fe-closing-form`, `feat/be-auth-jwt`
  * Data Science: `feat/ds-eda-forecasting`
  * Next-Gen AI: `feat/ai-intent-classifier`, `feat/ai-gemini-drafter`

---

## 4. Alur Kerja Kontrak API (Contract-First)
Seluruh skema data request dan response telah dibekukan pada dokumen [`docs/api-contract.md`](docs/api-contract.md) sejak Minggu 1, memungkinkan Frontend, Backend, Data Science, dan AI Service bekerja secara paralel dengan sistem mock tanpa saling menunggu.
