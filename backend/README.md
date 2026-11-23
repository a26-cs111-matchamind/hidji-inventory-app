# Backend Service — Hidji Inventory App

## Deskripsi
RESTful API Gateway dan server orkestrator inventori Hidji Coffee & Matcha. Bertanggung jawab atas pengelolaan data transaksi persediaan, autentikasi berbasis role (Barista vs GM), kalkulasi deterministik restok, serta menjadi reverse-proxy aman ke AI Service.

## Tech Stack
* **Runtime:** Node.js (LTS)
* **Framework:** Express.js
* **Database & ORM:** PostgreSQL (Neon Serverless) + Prisma ORM
* **Autentikasi:** JSON Web Token (JWT) + bcrypt

## Fitur Utama
1. **Autentikasi & Otorisasi:** Role protection (Barista hanya akses form stok masuk & closing; GM akses master bahan & dasbor).
2. **CRUD Master Bahan & Mutasi:** Pencatatan riwayat stok masuk dan sisa closing.
3. **Kalkulator Restok Deterministik:** Menghitung `reorder_point - current_stock + forecast_ds` secara presisi (Zero Hallucination).
4. **Proxy Aman ke AI Service:** Meneruskan request analitik & draf pesan ke FastAPI tanpa membocorkan API key di sisi client.

## Setup & Menjalankan Lokal
```bash
cd backend
npm install
cp .env.example .env
npm run dev
```
Port default: `http://localhost:5000`
