# Frontend Service — Hidji Inventory App (PWA)

## Deskripsi
Layanan frontend aplikasi inventori **Hidji Coffee & Matcha** berbasis **Progressive Web App (PWA)** dengan pendekatan *mobile-first*.

## Tech Stack
* **Framework:** React 18 + Vite
* **Styling:** Tailwind CSS + Lucide Icons / Heroicons
* **State Management:** React Context / Zustand
* **PWA:** vite-plugin-pwa (offline caching & mobile add-to-homescreen)

## Fitur Utama
1. **Form Input Closing Barista:** Pencatatan sisa fisik 5 bahan baku utama saat closing (< 2 menit).
2. **Form Stok Masuk:** Pencatatan penerimaan bahan dari supplier.
3. **Dasbor GM:** Pemantauan status stok terkini (Aman / Menipis / Habis) & grafik proyeksi.
4. **Tombol Kirim WhatsApp:** Integrasi tautan `https://wa.me/<nomor>?text=<draf>` untuk pengadaan sekali klik.

## Setup & Menjalankan Lokal
```bash
cd frontend
npm install
npm run dev
```
Port default: `http://localhost:5173`
