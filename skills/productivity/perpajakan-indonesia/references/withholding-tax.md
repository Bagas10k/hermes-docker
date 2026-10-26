# Withholding Tax di Indonesia (PPh 21, PPh 23, PPh 4 ayat 2, PPh 22)

Rujukan resmi: UU PPh No. 36/2008 stdd UU HPP No. 7/2021, PP 58/2023 & PMK 168/2023 (PPh 21 TER), PMK 141/PMK.03/2015 (PPh 23), PP 34/2016 & PP 9/2022 (PPh 4 ayat 2).

## 1. PPh Pasal 21 Pegawai Tetap

### A. Masa Pajak Januari s.d. November (Mekanisme TER Bulanan)
Berdasarkan PP 58/2023 dan PMK 168/2023, pemotongan bulanan menggunakan **Tarif Efektif Rata-Rata (TER)** yang dikalikan langsung dengan Penghasilan Bruto sebulan:
`PPh 21 Terutang Bulanan = Penghasilan Bruto Sebulan x Tarif TER`

- **TER Bulanan Kategori A (PTKP TK/0 = Rp54 jt, TK/1 = Rp58,5 jt, K/0 = Rp58,5 jt):**
  - Bruto s.d. Rp5.400.000: **0%**
  - > Rp5.400.000 s.d. Rp5.650.000: **0,25%**
  - > Rp5.650.000 s.d. Rp5.950.000: **0,5%**
  - > Rp5.950.000 s.d. Rp6.300.000: **0,75%**
  - > Rp6.300.000 s.d. Rp6.750.000: **1,0%**
  - > Rp6.750.000 s.d. Rp7.500.000: **1,25%**
  - > Rp7.500.000 s.d. Rp8.550.000: **1,5%**
  - > Rp8.550.000 s.d. Rp9.650.000: **1,75%**
  - > Rp9.650.000 s.d. Rp10.050.000: **2,0%**
  - *(Tabel lengkap tersimpan di kalkulator CLI `scripts/kalkulator_pajak.py`)*.

- **TER Bulanan Kategori B (PTKP TK/2, TK/3, K/1, K/2):**
  - Bruto s.d. Rp6.200.000: **0%**
  - > Rp6.200.000 s.d. Rp6.500.000: **0,25%**, dst.

- **TER Bulanan Kategori C (PTKP K/3):**
  - Bruto s.d. Rp6.600.000: **0%**
  - > Rp6.600.000 s.d. Rp6.950.000: **0,25%**, dst.

### B. Masa Pajak Desember (Penghitungan Tahunan / True-Up)
Pada Masa Pajak Desember (atau saat pegawai berhenti bekerja di tengah tahun), TER tidak lagi digunakan. Pemotong wajib menghitung PPh 21 tahunan dengan tarif progresif Pasal 17 ayat (1) huruf a UU PPh:
1. **Hitung Penghasilan Neto Setahun:**
   `Penghasilan Bruto Setahun - Biaya Jabatan (5%, maks Rp6 jt/th) - Iuran Pensiun/JHT yang dibayar karyawan`
2. **Hitung Penghasilan Kena Pajak (PKP):**
   `Penghasilan Neto Setahun - PTKP (Penghasilan Tidak Kena Pajak)`
3. **Hitung PPh 21 Terutang Setahun (Tarif Progresif Pasal 17 stdd UU HPP):**
   - Lapisan 1: Rp0 s.d. Rp60.000.000 = **5%**
   - Lapisan 2: > Rp60.000.000 s.d. Rp250.000.000 = **15%**
   - Lapisan 3: > Rp250.000.000 s.d. Rp500.000.000 = **25%**
   - Lapisan 4: > Rp500.000.000 s.d. Rp5.000.000.000 = **30%**
   - Lapisan 5: > Rp5.000.000.000 = **35%**
4. **Hitung PPh 21 Kurang/Lebih Potong Masa Desember:**
   `PPh 21 Terutang Desember = PPh 21 Setahun - Total PPh 21 Jan s.d. Nov`

### C. Perlakuan PPh 21 atas THR & Bonus
- Pada bulan diterimanya THR/Bonus, penghasilan bruto bulan tersebut diakumulasikan: `Gaji Pokok + Tunjangan + THR/Bonus`.
- Nilai total bruto gabungan tersebut langsung dikenakan tarif TER sesuai tabel braket bruto gabungannya.

---

## 2. PPh Pasal 21 Bukan Pegawai / Tenaga Ahli
Berdasarkan PMK 168/2023, tenaga ahli (dokter, pengacara, akuntan, arsitek, konsultan, notaris, penilai, aktuaris) dan pekerja lepas profesional:
- **Dasar Pengenaan Pajak (DPP):** **50% dari Penghasilan Bruto**.
- **Perhitungan Pajak:**
  `PPh 21 = 50% x Penghasilan Bruto x Tarif Progresif Pasal 17 UU PPh`
- Jika menerima imbalan lebih dari satu kali dalam tahun kalender yang sama dari pemotong yang sama, tarif progresif Pasal 17 diterapkan secara kumulatif atas DPP 50% tersebut.

---

## 3. PPh Pasal 23 (Jasa, Sewa Non-Tanah/Bangunan, Modal)
- **Tarif 2% (dari Penghasilan Bruto di luar PPN):**
  - Sewa peralatan, kendaraan, mesin, aset selain tanah/bangunan.
  - Imbalan atas 62 jenis jasa lain berdasarkan PMK 141/PMK.03/2015 (jasa manajemen, teknik, akuntansi, hukum, desain grafis, TI/perangkat lunak, kebersihan/cleaning, keamanan/security, dsb).
- **Tarif 15% (dari Penghasilan Bruto):**
  - Dividen (bagi penerima WP Badan dalam negeri non-tax exempt), bunga pinjaman, royalti, dan hadiah/penghargaan bukan objek PPh 21.
- **Kenaikan Tarif Tanpa NPWP:**
  - Penerima penghasilan yang tidak memiliki NPWP dikenakan **kenaikan 100%** (tarif efektif menjadi **4%** untuk jasa/sewa dan **30%** untuk royalti/bunga).

---

## 4. PPh Pasal 4 ayat (2) (Final)
- **Sewa Tanah dan/atau Bangunan:**
  - Tarif mutlak **10%** dari jumlah bruto nilai sewa. Tidak dapat dikreditkan di SPT Tahunan.
- **Pengalihan Hak atas Tanah dan/atau Bangunan:**
  - Tarif **2,5%** dari nilai transaksi bruto.
- **Jasa Konstruksi (PP 9/2022):**
  - Pelaksanaan konstruksi kualifikasi kecil: **1,75%**.
  - Pelaksanaan konstruksi kualifikasi menengah/besar/spesialis: **2,65%**.
  - Pelaksanaan konstruksi tanpa kualifikasi: **4,0%**.
  - Konsultansi konstruksi/pengawasan kualifikasi bersertifikat: **3,5%**.
  - Konsultansi konstruksi tanpa kualifikasi: **6,0%**.

---

## 5. Administrasi Bukti Potong (e-Bupot Unifikasi)
- Pemotong wajib membuat Bukti Pemotongan Berkelanjutan melalui aplikasi DJP Online paling lambat akhir bulan terjadinya transaksi.
- Penyetoran pajak dipotong paling lambat **tanggal 10 bulan berikutnya**.
- Pelaporan SPT Masa Unifikasi paling lambat **tanggal 20 bulan berikutnya**.
