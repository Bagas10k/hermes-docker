# PPN dan Faktur Pajak

Rujukan resmi: UU No. 8 Tahun 1983 stdd UU No. 7 Tahun 2021 (UU HPP), PMK 197/PMK.03/2013 (Batasan PKP), PER-03/PJ/2022 stdd PER-11/PJ/2022 (Faktur Pajak).

## 1. Pengukuhan Pengusaha Kena Pajak (PKP)
- **Kewajiban Pengukuhan PKP:** Wajib bagi pengusaha yang melakukan penyerahan Barang Kena Pajak (BKP) dan/atau Jasa Kena Pajak (JKP) dengan jumlah peredaran bruto/omzet melebihi **Rp4.800.000.000** (empat koma delapan miliar rupiah) dalam 1 tahun buku.
- **Pengusaha Kecil (Omzet <= Rp4,8 Miliar):**
  - Tidak wajib PKP (dapat berstatus Non-PKP dan tidak memungut PPN).
  - Berhak secara sukarela memilih dikukuhkan sebagai PKP (misalnya untuk keperluan tender pemerintah/B2B yang mensyaratkan Faktur Pajak).

## 2. Tarif & Dasar Pengenaan Pajak (DPP)
- **Tarif PPN Pokok:**
  - **11%** mulai berlaku sejak 1 April 2022 berdasarkan amanat UU HPP.
  - Ekspor BKP Berwujud, BKP Tidak Berwujud, dan Ekspor JKP: **0%**.
- **Dasar Pengenaan Pajak (DPP):**
  - Harga Jual, Penggantian, Nilai Impor, Nilai Ekspor, atau Nilai Lain yang ditetapkan Menteri Keuangan.
  - Rumus: `PPN Terutang = DPP x 11%`.
  - Jika harga sudah termasuk PPN (gross-up):
    - `DPP = (100 / 111) x Harga Termasuk PPN`
    - `PPN = (11 / 111) x Harga Termasuk PPN`

## 3. Mekanisme Pajak Keluaran (PK) & Pajak Masukan (PM)
- **Pajak Keluaran (PK):** PPN yang dipungut oleh PKP saat menjual BKP/JKP kepada pelanggan.
- **Pajak Masukan (PM):** PPN yang dibayar oleh PKP saat membeli BKP/JKP dari pemasok PKP lain.
- **Kompensasi / Penyetoran:**
  - Jika `PK > PM`: Selisihnya merupakan **PPN Kurang Bayar** yang wajib disetor ke kas negara sebelum SPT Masa PPN disampaikan.
  - Jika `PM > PK`: Selisihnya merupakan **PPN Lebih Bayar**, dapat dikompensasikan ke masa pajak berikutnya atau dimintakan restitusi (pengembalian).

## 4. Ketentuan Faktur Pajak Elektronik (e-Faktur)
- Setiap penyerahan BKP/JKP oleh PKP wajib dibuatkan Faktur Pajak elektronik melalui aplikasi e-Faktur.
- **Batas Waktu Upload Faktur Pajak:**
  - Berdasarkan PER-03/PJ/2022, Faktur Pajak elektronik wajib diunggah (di-upload) dan memperoleh persetujuan (approval) DJP paling lambat **tanggal 15 bulan berikutnya** setelah tanggal pembuatan Faktur Pajak.
  - Faktur Pajak yang di-upload melewati tanggal 15 bulan berikutnya akan ditolak (reject) dan tidak dapat dikreditkan oleh pembeli.
- **Pajak Masukan yang Tidak Dapat Dikreditkan (Pasal 9 ayat 8 UU PPN):**
  - Perolehan BKP/JKP sebelum pengusaha dikukuhkan sebagai PKP.
  - Perolehan BKP/JKP yang tidak mempunyai hubungan langsung dengan kegiatan usaha (3M: mendapatkan, menagih, dan memelihara penghasilan).
  - Perolehan dan pemeliharaan kendaraan bermotor sedan dan station wagon (kecuali barang dagangan atau disewakan).
  - Faktur Pajak cacat (tidak memuat keterangan lengkap, alamat/NPWP salah, atau terlambat upload).

## 5. Jurnal Akuntansi PPN (Entitas PKP)
- **Saat Pembelian dari Pemasok (DPP Rp10.000.000 + PPN 11% Rp1.100.000):**
  - `(D) Persediaan / Beban Pembelian`: Rp10.000.000
  - `(D) PPN Masukan`: Rp1.100.000
  - `(K) Utang Usaha / Kas`: Rp11.100.000
- **Saat Penjualan ke Pelanggan (DPP Rp20.000.000 + PPN 11% Rp2.200.000):**
  - `(D) Piutang Usaha / Kas`: Rp22.200.000
  - `(K) Pendapatan Penjualan`: Rp20.000.000
  - `(K) PPN Keluaran`: Rp2.200.000
- **Saat Tutup Buku Masa Pajak (Penyelesaian PPN):**
  - `(D) PPN Keluaran`: Rp2.200.000
  - `(K) PPN Masukan`: Rp1.100.000
  - `(K) Utang PPN (Kurang Bayar)`: Rp1.100.000
