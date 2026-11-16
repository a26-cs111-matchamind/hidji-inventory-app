# Data Science — Hidji Inventory Analysis & Forecasting

## Deskripsi
Ruang kerja analisis data eksploratif (EDA), pembuatan dataset sintetis berlabel, dan pemodelan peramalan (*forecasting*) kebutuhan bahan baku harian kedai kopi Hidji.

## Tech Stack & Library
* **Python 3.10+**
* **Data Wrangling:** Pandas, NumPy
* **Visualisasi:** Matplotlib, Seaborn
* **Modeling & Evaluasi:** Scikit-learn (Moving Average, Linear/Ridge Regression, Random Forest Regressor)
* **Jupyter Notebook:** Eksplorasi data dan dokumentasi eksperimen

## Pembagian Kerja & Output
1. **Dataset Sintetis Berlabel:** Dataset simulasi konsumsi 5 bahan baku utama berbasis pola harian kedai (Senin–Jumat).
2. **Komparasi Model:** Membandingkan minimal 2 model kandidat regresi + 1 baseline Moving Average dievaluasi dengan MAE & RMSE.
3. **Model Export:** Model peramalan terbaik diekspor dalam format `.pkl` atau diintegrasikan sebagai fungsi helper time-series.

## Setup Virtual Environment
```bash
cd data-science
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook
```
