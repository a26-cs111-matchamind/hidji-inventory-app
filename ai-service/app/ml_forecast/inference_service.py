import json
import math
from pathlib import Path
import joblib
import pandas as pd


# Materials where DS Cell 15 evaluation showed Moving Average 5-day outperforms Ridge
MA5_PREFERRED_MATERIALS: set[str] = {
    "KOP02", "KOP04", "KOP05", "KOP07", "KOP09", "KOP10",
    "KOP12", "KOP16", "KOP18", "KOP19", "KOP20", "KOP22",
    "KOP23", "MAT02", "MAT06", "TMB02",
}


class HidjiRestockForecaster:
    def __init__(self, bundle_path: str = "hidji_ridge_bundle_v1.joblib", master_path: str = "master_bahan_ref.json"):
        bundle = joblib.load(Path(bundle_path))
        self.models = bundle.get("models")
        self.single_model = bundle.get("model")
        self.feature_columns = bundle["feature_columns"]
        self.lag_window = bundle.get("lag_window", 5)
        self.model_version = bundle.get("model_version", "ridge_v2.0")

        with open(Path(master_path), "r", encoding="utf-8") as f:
            self.master_bahan = json.load(f)

    def _build_lag_features(self, sorted_history: list[dict], target_date_str: str | None = None) -> pd.DataFrame:
        last_5 = sorted_history[-5:]
        lag_1 = float(last_5[-1]["pemakaian_baku"])
        lag_2 = float(last_5[-2]["pemakaian_baku"])
        lag_5 = float(last_5[0]["pemakaian_baku"])
        rolling_mean_5 = sum(float(d["pemakaian_baku"]) for d in last_5) / 5.0

        if target_date_str:
            try:
                target_dt = pd.to_datetime(target_date_str)
                dayofweek = int(target_dt.dayofweek) % 5
            except Exception:
                dayofweek = 0
        else:
            try:
                last_dt = pd.to_datetime(last_5[-1]["tanggal"])
                dayofweek = int((last_dt.dayofweek + 1) % 5)
            except Exception:
                dayofweek = 0

        row = {
            "lag_1": lag_1,
            "lag_2": lag_2,
            "lag_5": lag_5,
            "rolling_mean_5": rolling_mean_5,
            "dayofweek": dayofweek,
        }
        return pd.DataFrame([row], columns=self.feature_columns)

    def predict_item(self, item: dict) -> dict:
        id_bahan = item["id_bahan"]
        if id_bahan not in self.master_bahan:
            raise ValueError(f"ID_Bahan '{id_bahan}' tidak terdaftar di master_bahan_ref.json")

        meta = self.master_bahan[id_bahan]
        sisa_stok = float(item["sisa_stok_closing_baku"])
        stok_min = float(meta["Stok_Minimum_Baku"])
        isi_kemasan = float(meta["Isi_per_Kemasan"])

        history = sorted(item.get("riwayat_pemakaian", []), key=lambda x: x["tanggal"])
        n_days = len(history)

        if n_days >= self.lag_window:
            avg_val = sum(float(d["pemakaian_baku"]) for d in history[-5:]) / 5.0

            if id_bahan in MA5_PREFERRED_MATERIALS:
                proyeksi_besok = max(0.0, round(avg_val, 2))
                model_used = "ma5_baseline"
                fallback_reason = "Routing model terbaik per bahan (MA5)"
            else:
                try:
                    target_dt = item.get("target_tanggal_operasional")
                    X_df = self._build_lag_features(history, target_date_str=target_dt)
                    estimator = None
                    if self.models and id_bahan in self.models:
                        estimator = self.models[id_bahan]
                    elif self.single_model:
                        estimator = self.single_model

                    if estimator is not None:
                        raw_pred = float(estimator.predict(X_df)[0])
                        # Guardrail prevents clipped <= 0 or extreme scale drift from Ridge
                        if avg_val > 0 and (raw_pred <= 0.0 or raw_pred < 0.25 * avg_val or raw_pred > 3.0 * avg_val):
                            proyeksi_besok = max(0.0, round(avg_val, 2))
                            model_used = "ma5_guardrail"
                            fallback_reason = f"Guardrail aktif: prediksi Ridge ({round(raw_pred, 2)}) di luar rentang wajar"
                        else:
                            proyeksi_besok = max(0.0, round(raw_pred, 2))
                            model_used = self.model_version
                            fallback_reason = None
                    else:
                        proyeksi_besok = max(0.0, round(avg_val, 2))
                        model_used = "ma5_fallback"
                        fallback_reason = f"Model Ridge khusus {id_bahan} tidak tersedia"
                except Exception as e:
                    proyeksi_besok = max(0.0, round(avg_val, 2))
                    model_used = "ma5_fallback"
                    fallback_reason = f"Error inferensi Ridge: {str(e)}"
        elif n_days > 0:
            avg_val = sum(float(d["pemakaian_baku"]) for d in history) / n_days
            proyeksi_besok = max(0.0, round(avg_val, 2))
            model_used = "ma5_fallback"
            fallback_reason = f"Riwayat pemakaian kurang dari 5 hari kerja (tersedia: {n_days} hari)"
        else:
            proyeksi_besok = 0.0
            model_used = "zero_history_default"
            fallback_reason = "Tidak ada riwayat pemakaian"

        target_stok = proyeksi_besok + stok_min
        defisit_baku = max(0.0, round(target_stok - sisa_stok, 2))
        rekomendasi_kemasan = math.ceil(defisit_baku / isi_kemasan) if defisit_baku > 0 else 0

        return {
            "id_bahan": id_bahan,
            "nama_bahan": meta["Nama_Bahan"],
            "satuan_baku": meta["Satuan_Baku"],
            "sisa_stok_closing_baku": sisa_stok,
            "stok_minimum_baku": stok_min,
            "proyeksi_pemakaian_besok_baku": proyeksi_besok,
            "defisit_baku": defisit_baku,
            "perlu_restock": rekomendasi_kemasan > 0,
            "rekomendasi_beli_kemasan": rekomendasi_kemasan,
            "satuan_kemasan": meta["Satuan_di_Lembar"],
            "isi_per_kemasan": isi_kemasan,
            "total_restock_baku": round(rekomendasi_kemasan * isi_kemasan, 2),
            "model_digunakan": model_used,
            "alasan_fallback": fallback_reason,
        }

    def generate_restock_recommendations(self, payload: dict) -> dict:
        hasil = [self.predict_item(item) for item in payload.get("items", [])]
        return {
            "status": "success",
            "tanggal_closing": payload["tanggal_closing"],
            "target_tanggal_operasional": payload["target_tanggal_operasional"],
            "target_hari": payload["target_hari"],
            "ringkasan": {
                "total_item_diproses": len(hasil),
                "total_item_perlu_restock": sum(1 for r in hasil if r["perlu_restock"]),
                "jumlah_prediksi_ridge": sum(1 for r in hasil if r["model_digunakan"] == self.model_version),
                "jumlah_prediksi_fallback_ma5": sum(
                    1 for r in hasil if r["model_digunakan"] in ("ma5_fallback", "ma5_baseline", "ma5_guardrail")
                ),
            },
            "rekomendasi": hasil,
        }
