# Standar Jurnal Akuntansi Perpajakan Indonesia

Panduan pencatatan ayat jurnal berpasangan (double-entry) untuk transaksi perpajakan usaha di Indonesia, memadukan Standar Akuntansi Keuangan (SAK) dengan kepatuhan Surat Pemberitahuan (SPT).

## 1. Jurnal PPh Pasal 21 (Beban Gaji & Upah)
Pemberi kerja mencatat beban gaji bruto karyawan, memotong PPh 21 dan iuran BPJS, lalu membayarkan sisa neto ke karyawan.

- **Saat Pengakuan Gaji Bulanan (Payroll):**
  - `(D) Beban Gaji & Upah`: Rp10.000.000 (Gaji Bruto)
  - `(D) Beban Iuran BPJS Ketenagakerjaan/Kesehatan (Porsi Perusahaan)`: Rp400.000
  - `(K) Utang PPh Pasal 21`: Rp200.000 (Pemotongan TER)
  - `(K) Utang BPJS (Porsi Perusahaan + Karyawan)`: Rp700.000
  - `(K) Kas / Bank / Utang Gaji`: Rp9.500.000 (Take Home Pay)

- **Saat Penyetoran PPh 21 ke Kas Negara (Maks tgl 10 bulan berikutnya):**
  - `(D) Utang PPh Pasal 21`: Rp200.000
  - `(K) Kas / Bank`: Rp200.000

## 2. Jurnal PPh Pasal 23 (Jasa & Sewa Harta Selain Tanah/Bangunan)

### A. Posisi Perusahaan sebagai Pemotong (Pembeli Jasa)
- **Saat Menerima Tagihan Invoice Jasa Konsultan (DPP Rp10.000.000):**
  - `(D) Beban Jasa Konsultasi`: Rp10.000.000
  - `(K) Utang PPh Pasal 23`: Rp200.000 (2% dari DPP)
  - `(K) Utang Usaha / Kas`: Rp9.800.000
- **Saat Menyetorkan Potongan ke Kas Negara:**
  - `(D) Utang PPh Pasal 23`: Rp200.000
  - `(K) Kas / Bank`: Rp200.000

### B. Posisi Perusahaan sebagai yang Dipotong (Penyedia Jasa)
- **Saat Menerbitkan Invoice & Menerima Pembayaran Bersih:**
  - `(D) Kas / Bank`: Rp9.800.000
  - `(D) Pajak Dibayar di Muka PPh Pasal 23`: Rp200.000 (Aset Lancar / Kredit Pajak)
  - `(K) Pendapatan Jasa`: Rp10.000.000
  *(Bukti Potong e-Bupot Unifikasi dari rekanan wajib disimpan sebagai bukti kredit pajak tahunan di SPT PPh Badan)*.

## 3. Jurnal PPh Pasal 4 ayat (2) (Sewa Tanah dan/atau Bangunan - Final)
- **Saat Membayar Sewa Gedung Kantor (Contoh: Sewa 1 Tahun Rp120.000.000):**
  - `(D) Sewa Dibayar di Muka (Prepaid Expense)`: Rp120.000.000
  - `(K) Utang PPh Final Pasal 4(2)`: Rp12.000.000 (10% x Rp120.000.000)
  - `(K) Kas / Bank`: Rp108.000.000
- **Saat Menyetorkan Pajak ke Kas Negara:**
  - `(D) Utang PPh Final Pasal 4(2)`: Rp12.000.000
  - `(K) Kas / Bank`: Rp12.000.000
- **Amortisasi Beban Sewa Bulanan (Penyesuaian Akhir Bulan):**
  - `(D) Beban Sewa Kantor`: Rp10.000.000
  - `(K) Sewa Dibayar di Muka`: Rp10.000.000

## 4. Jurnal PPh Final UMKM (PP 55/2022)
- **Pengakuan Beban Pajak Akhir Bulan (Misal Omzet Rp50.000.000 x 0,5% = Rp250.000):**
  - `(D) Beban Pajak Penghasilan (PPh Final)`: Rp250.000
  - `(K) Utang PPh Final UMKM`: Rp250.000
- **Penyetoran ke Kas Negara via Billing e-Billing (Maks tgl 15 bulan berikutnya):**
  - `(D) Utang PPh Final UMKM`: Rp250.000
  - `(K) Kas / Bank`: Rp250.000

## 5. Jurnal Siklus PPN (Pengusaha Kena Pajak / PKP)
- **Membeli Barang Dagang (DPP Rp100.000.000 + PPN 11% Rp11.000.000):**
  - `(D) Persediaan Barang Dagang`: Rp100.000.000
  - `(D) PPN Masukan (Pajak Dibayar di Muka)`: Rp11.000.000
  - `(K) Utang Usaha / Kas`: Rp111.000.000

- **Menjual Barang Dagang (DPP Rp150.000.000 + PPN 11% Rp16.500.000):**
  - `(D) Piutang Usaha / Kas`: Rp166.500.000
  - `(K) Penjualan / Pendapatan Usaha`: Rp150.000.000
  - `(K) PPN Keluaran (Utang Pajak)`: Rp16.500.000

- **Offsetting Akhir Masa Pajak (Penyelesaian Saldo PPN):**
  - `(D) PPN Keluaran`: Rp16.500.000
  - `(K) PPN Masukan`: Rp11.000.000
  - `(K) Utang PPN Kurang Bayar`: Rp5.500.000

- **Penyetoran PPN Kurang Bayar (Sebelum Akhir Bulan Berikutnya):**
  - `(D) Utang PPN Kurang Bayar`: Rp5.500.000
  - `(K) Kas / Bank`: Rp5.500.000

*(Jika PM > PK, jurnal penutup mencatat sisi debit `PPN Lebih Bayar / Kompensasi Pajak` sebagai aset lancar).*

## 6. Jurnal Tutup Tahun PPh Badan (Pasal 28A / 29)
Di akhir tahun buku, dihitung total PPh Badan terutang berdasarkan laba fiskal (misal: Rp50.000.000). Saldo kredit pajak yang telah disetor dicatat sebagai pengurang:
- Angsuran PPh 25 disetor: Rp30.000.000
- Kredit PPh 23 dipotong pihak lain: Rp5.000.000
- Kredit PPh 22 impor: Rp3.000.000
- Sisa Kurang Bayar (PPh Pasal 29): Rp12.000.000

- **Jurnal Penyesuaian Akhir Tahun (31 Desember):**
  - `(D) Beban Pajak Penghasilan Badan (Kini)`: Rp50.000.000
  - `(K) Pajak Dibayar di Muka PPh Pasal 25`: Rp30.000.000
  - `(K) Pajak Dibayar di Muka PPh Pasal 23`: Rp5.000.000
  - `(K) Pajak Dibayar di Muka PPh Pasal 22`: Rp3.000.000
  - `(K) Utang PPh Pasal 29`: Rp12.000.000

- **Penyetoran PPh 29 (Sebelum SPT Tahunan Badan Disampaikan, maks 30 April):**
  - `(D) Utang PPh Pasal 29`: Rp12.000.000
  - `(K) Kas / Bank`: Rp12.000.000
