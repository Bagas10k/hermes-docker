# Analisis Laporan Keuangan, Deteksi Kualitas Laba & Valuasi

Panduan diagnostik kinerja korporasi, pendeteksian risiko kebangkrutan, kualitas laba akrual, dan valuasi arus kas.

---

## 1. Analisis DuPont 5-Way
Mengurai Return on Equity (ROE) menjadi 5 pendorong fundamental untuk mengidentifikasi sumber kekuatan atau kerentanan laba:

### Formula 5 Komponen:
`ROE = (Net Income / EBT) x (EBT / EBIT) x (EBIT / Sales) x (Sales / Total Assets) x (Total Assets / Equity)`

1. **Tax Burden = `Net Income / EBT`:** Mengukur persentase laba sebelum pajak yang tersisa setelah beban pajak penghasilan. Nilai mendekati 1 menandakan beban pajak rendah atau fasilitas perpajakan.
2. **Interest Burden = `EBT / EBIT`:** Mengukur beban bunga utang. Nilai 1,0 berarti tidak ada utang berbunga. Penurunan tajam menandakan tekanan pembayaran bunga pinjaman tinggi.
3. **Operating Profit Margin = `EBIT / Sales`:** Mengukur efisiensi laba operasi inti dari penjualan murni.
4. **Asset Turnover = `Sales / Total Assets`:** Mengukur produktivitas pemanfaatan total aset untuk menghasilkan penjualan.
5. **Financial Leverage (Equity Multiplier) = `Total Assets / Equity`:** Mengukur seberapa besar aset dibiayai oleh utang.

*Wawasan Manajerial:* Kenaikan ROE yang hanya didorong oleh kenaikan *Equity Multiplier* tanpa perbaikan margin operasi adalah sinyal risiko tinggi (rekayasa finansial berisiko utang).

---

## 2. Model Prediksi Kebangkrutan (Altman Z-Score)
Digunakan oleh analis kredit dan auditor untuk mengukur probabilitas gagal bayar entitas dalam rentang 1-2 tahun ke depan.

### A. Model Modifikasi untuk Perusahaan Manufaktur Privat (1983):
`Z' = 0.717(X1) + 0.847(X2) + 3.107(X3) + 0.420(X4) + 0.998(X5)`
- **X1:** Modal Kerja Bersih / Total Aset (`(Aktiva Lancar - Utang Lancar) / Total Aset`).
- **X2:** Saldo Laba Ditahan / Total Aset (`Retained Earnings / Total Aset`).
- **X3:** EBIT / Total Aset (Kekuatan produktivitas laba aset).
- **X4:** Nilai Buku Ekuitas / Total Liabilitas (Ketahanan permodalan terhadap kewajiban).
- **X5:** Penjualan / Total Aset (Perputaran aset).

**Kriteria Zona Z':**
- `Z' > 2.90`: **Zona Aman (Safe Zone)** - Risiko default sangat rendah.
- `1.23 <= Z' <= 2.90`: **Zona Abu-Abu (Grey Zone)** - Waspada, rentan mengalami tekanan likuiditas.
- `Z' < 1.23`: **Zona Bahaya (Distress Zone)** - Probabilitas tinggi mengalami kegagalan keuangan.

### B. Model Modifikasi Z'' (Perusahaan Non-Manufaktur & Jasa, 1993):
`Z'' = 6.56(X1) + 3.26(X2) + 6.72(X3) + 1.05(X4)`
- *Zona:* `Z'' > 2.60` (Aman), `1.10 <= Z'' <= 2.60` (Abu-abu), `Z'' < 1.10` (Distress).

---

## 3. Kualitas Laba & Beneish M-Score (Deteksi Manipulasi Laporan)
Model kuantitatif berbasis 8 rasio akuntansi untuk mendeteksi potensi pemolesan laba (*earnings manipulation*):
- `DSRI` (Days Sales in Receivables Index): Menguji lonjakan piutang tak wajar dibanding penjualan.
- `GMI` (Gross Margin Index): Penurunan margin kotor sering memicu manajemen memanipulasi laba.
- `AQI` (Asset Quality Index): Proporsi aset non-lancar selain tanah/mesin (kapitalisasi biaya tak berwujud).
- `SGI` (Sales Growth Index): Pertumbuhan omzet drastis menciptakan ekspektasi laba semu.
- `DEPI` (Depreciation Index): Memperlambat tarif depresiasi untuk mendongkrak laba.
- `SGAI` (Sales, General and Administrative expenses Index).
- `LVGI` (Leverage Index): Peningkatan utang total terhadap total aset.
- `TATA` (Total Accruals to Total Assets): `(Laba Bersih - Arus Kas Operasi) / Total Aset`.
*Batas Kritis:* `M-Score > -1.78` mengindikasikan probabilitas tinggi terjadinya rekayasa manipulasi laporan keuangan.

---

## 4. Valuasi Korporasi Berbasis Arus Kas Bebas
- **Free Cash Flow to Firm (FCFF):**
  `FCFF = EBIT x (1 - Tarif Pajak) + Penyusutan/Amortisasi - Belanja Modal (CapEx) - Kenaikan Modal Kerja Bersih (ΔNWC)`
- **Free Cash Flow to Equity (FCFE):**
  `FCFE = FCFF - Beban Bunga(1 - t) + Penarikan Utang Baru - Pelunasan Pokok Utang`
- **Economic Value Added (EVA):**
  `EVA = NOPAT - (WACC x Modal yang Diinvestasikan)`
  EVA positif membuktikan bisnis menghasilkan imbal hasil di atas biaya modal riil (*creating economic wealth*).
