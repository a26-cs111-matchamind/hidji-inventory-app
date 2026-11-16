# API Contract & Schema — Matchamind x Hidji

Dokumen ini membekukan kontrak pertukaran data (JSON Request/Response) antara **Frontend**, **Backend**, **Data Science**, dan **AI Service** pada Minggu 1.

---

## 1. Backend ➔ AI Service: Restock Advice & WhatsApp Drafter

* **Endpoint:** `POST /v1/restock/advice`
* **Request Payload (JSON):**
```json
{
  "date": "2026-11-20",
  "items": [
    {
      "id": 1,
      "name": "Susu Segar UHT",
      "unit": "Liter",
      "current_stock": 2.0,
      "minimum_stock": 5.0,
      "forecast_next_day": 4.5,
      "lead_time_days": 1,
      "pack_size": 1,
      "supplier_id": "SUPP-01",
      "supplier_name": "Supplier Susu Diamond"
    }
  ]
}
```

* **Response Payload (JSON):**
```json
{
  "status": "success",
  "summary": "Terdapat 1 bahan kritis yang berada di bawah ambang batas aman. Disarankan melakukan restok 8 Liter Susu Segar UHT sebelum kedai dibuka esok hari.",
  "items": [
    {
      "id": 1,
      "recommended_qty": 8,
      "unit": "Liter",
      "reason": "Sisa 2 Liter di bawah batas aman 5 Liter dengan estimasi kebutuhan esok hari 4.5 Liter."
    }
  ],
  "drafts": [
    {
      "supplier_id": "SUPP-01",
      "supplier_name": "Supplier Susu Diamond",
      "message": "Halo Supplier Susu Diamond, kami dari Hidji Coffee & Matcha ingin memesan Susu Segar UHT sebanyak 8 Liter untuk pengiriman besok pagi. Mohon konfirmasi ketersediaan stoknya. Terima kasih!",
      "wa_link": "https://wa.me/6281234567890?text=Halo%20Supplier%20Susu%20Diamond..."
    }
  ],
  "fallback_used": false
}
```

---

## 2. Frontend ➔ Backend: Input Sisa Stok Closing (< 2 Menit)

* **Endpoint:** `POST /api/stock/closing`
* **Headers:** `Authorization: Bearer <jwt-token>`
* **Request Payload (JSON):**
```json
{
  "closing_date": "2026-11-20",
  "notes": "Operasional lancar, tidak ada kendala tumpah",
  "entries": [
    {"material_id": 1, "remaining_stock": 2.0},
    {"material_id": 2, "remaining_stock": 0.8},
    {"material_id": 3, "remaining_stock": 1.2},
    {"material_id": 4, "remaining_stock": 0.5},
    {"material_id": 5, "remaining_stock": 85.0}
  ]
}
```
