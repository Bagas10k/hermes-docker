# Akuntansi Manajemen Strategis & Rekayasa Biaya

Panduan perancangan struktur biaya, analisis sensitivitas manajerial, dan optimasi modal kerja bagi pengambil keputusan bisnis.

---

## 1. Analisis Cost-Volume-Profit (CVP) Lanjutan
CVP memodelkan keterkaitan antara volume produksi/penjualan, struktur biaya, dan laba operasional.

### Formula Kunci:
- **Margin Kontribusi (Contribution Margin / CM):**
  - `CM per Unit = Harga Jual (P) - Biaya Variabel per Unit (VC)`
  - `Rasio CM (CMR) = CM per Unit / Harga Jual`
- **Titik Impas (Break-Even Point / BEP):**
  - `BEP (Unit) = Total Biaya Tetap / CM per Unit`
  - `BEP (Rupiah) = Total Biaya Tetap / Rasio CM`
- **Batas Keamanan (Margin of Safety / MoS):**
  - Mengukur seberapa jauh penjualan aktual/target boleh turun sebelum entitas mulai menderita kerugian.
  - `MoS (Rupiah) = Penjualan Aktual - Penjualan BEP`
  - `Rasio MoS = MoS (Rupiah) / Penjualan Aktual`
- **Derajat Leverage Operasi (Degree of Operating Leverage / DOL):**
  - Mengukur sensitivitas perubahan laba operasional (EBIT) terhadap persentase perubahan volume penjualan.
  - `DOL = Total Margin Kontribusi / EBIT`
  - *Interpretasi:* Jika DOL = 3,0, maka kenaikan penjualan 10% akan meningkatkan EBIT sebesar 30%. Sebaliknya, penurunan penjualan 10% memangkas laba sebesar 30%.

---

## 2. Activity-Based Costing (ABC) vs Biaya Tradisional
- **Kelemahan Biaya Tradisional:** Mengalokasikan biaya overhead pabrik/kantor secara seragam berdasarkan satu ukuran pemicu tunggal (misal jam tenaga kerja langsung atau jam mesin). Hal ini menimbulkan distorsi penetapan harga (*product undercosting* pada produk bervolume rendah/rumit dan *overcosting* pada produk massal).
- **Pendekatan ABC:**
  1. Identifikasi aktivitas utama pembentuk nilai (penerimaan bahan, perakitan, inspeksi mutu, penanganan mesin, pengiriman).
  2. Bebankan biaya sumber daya ke dalam *Cost Pools* per aktivitas.
  3. Identifikasi *Cost Drivers* spesifik (jumlah pesanan pembelian, jumlah batch produksi, jam inspeksi).
  4. Hitung tarif aktivitas: `Tarif Pool = Total Biaya Pool / Total Kapasitas Cost Driver`.
  5. Bebankan biaya overhead ke produk/jasa sesuai intensitas konsumsi aktivitas riil.

---

## 3. Siklus Konversi Kas (Cash Conversion Cycle / CCC)
CCC adalah indikator utama efisiensi manajemen modal kerja (*working capital management*), mengukur durasi kas keluar untuk pengadaan hingga kembali menjadi kas masuk dari penjualan.

### Formula:
`CCC = DIO + DSO - DPO`
- **Days Sales of Inventory (DIO):**
  `DIO = (Rata-rata Persediaan / HPP) x 365` (Berapa hari barang tertahan di gudang).
- **Days Sales Outstanding (DSO):**
  `DSO = (Rata-rata Piutang Usaha / Total Penjualan Kredit) x 365` (Berapa hari piutang ditagih).
- **Days Payable Outstanding (DPO):**
  `DPO = (Rata-rata Utang Usaha / HPP atau Pembelian) x 365` (Berapa hari pembayaran ke pemasok ditunda).

*Sasaran Strategis:* Memperpendek DIO melalui *Just-in-Time* (JIT), memperpendek DSO melalui diskon termin (*2/10 net 30*) dan kontrol batas kredit, serta memperpanjang DPO secara sehat tanpa merusak relasi rantai pasok. CCC negatif mengindikasikan entitas dibiayai oleh pemasok sebelum membayar (contoh: model ritel Amazon / Dell).

---

## 4. Analisis Varian Anggaran Standar (Variance Analysis)
Membedah selisih antara biaya aktual dan biaya standar yang dianggarkan:
- **Varian Bahan Baku:**
  - *Price Variance:* `(Harga Aktual - Harga Standar) x Kuantitas Aktual Dibeli`
  - *Quantity/Efficiency Variance:* `(Kuantitas Aktual Dipakai - Kuantitas Standar yang Diizinkan) x Harga Standar`
- **Varian Tenaga Kerja Langsung:**
  - *Rate Variance:* `(Tarif Jam Aktual - Tarif Jam Standar) x Jam Kerja Aktual`
  - *Efficiency Variance:* `(Jam Kerja Aktual - Jam Standar yang Diizinkan) x Tarif Standar`
- **Varian Overhead Pabrik:**
  - *Spending Variance* (efisiensi harga input energi/pemeliharaan) vs *Volume/Capacity Variance* (tingkat penyerapan kapasitas terpasang).
