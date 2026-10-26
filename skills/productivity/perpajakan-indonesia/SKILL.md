---
name: perpajakan-indonesia
description: Hitung PPh, PPN, dan rekonsiliasi fiskal usaha.
version: 0.1.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags: [Taxation, Indonesia, Accounting, Compliance]
---

# Perpajakan Indonesia

Skill ini memandu analisis kewajiban, perhitungan tarif, penyesuaian fiskal, penyusunan jurnal akuntansi pajak, dan kepatuhan administrasi perpajakan usaha di Indonesia berdasarkan UU HPP, UU PPh, UU PPN, PP 55/2022, PP 58/2023, PMK 168/2023, dan aturan turunan DJP. Skill ini berfokus pada draf perhitungan dan kepatuhan internal usaha, bukan opini hukum formal atau penandatanganan SPT resmi. Seluruh perhitungan numerik menggunakan pustaka standar Python `decimal`.

## When to Use
- Menghitung PPh Final UMKM 0,5% (PP 55/2022) untuk WP Orang Pribadi (batas 500 jt) atau Badan.
- Menghitung pemotongan PPh 21 skema TER bulanan, rekonsiliasi Masa Desember, atau Tenaga Ahli (DPP 50%).
- Menghitung pemotongan PPh Pasal 23 (jasa 2%, dividen/bunga/royalti 15%) dan PPh 4 ayat (2) final.
- Melakukan rekonsiliasi fiskal (koreksi positif & negatif, natura PMK 66/2023, DER 4:1) ke PPh Badan Pasal 31E.
- Menyusun ayat jurnal akuntansi perpajakan berpasangan (double-entry) komersial vs fiskal.
- Menghitung PPN 11% (DPP, PPN Masukan/Keluaran, offsetting akhir masa).
- Memeriksa batas waktu setor/lapor SPT dan simulasi sanksi bunga KUP UU HPP.

## Prerequisites
- Bentuk entitas usaha (PT, CV, Koperasi, Orang Pribadi) dan status pengukuhan PKP/Non-PKP.
- Peredaran bruto tahun berjalan serta tahun pajak sebelumnya.
- Rincian akun laba-rugi komersial untuk analisis biaya deductible vs non-deductible.
- Python 3 terpasang untuk mengeksekusi kalkulator pajak CLI (`scripts/kalkulator_pajak.py`).

## How to Run
- Muat berkas referensi topikal menggunakan `skill_view` pada path `references/<nama-file>.md`.
- Jalankan perhitungan tarif deterministik via `terminal` menggunakan skrip di `scripts/kalkulator_pajak.py`.
- Lakukan rekonsiliasi angka dan uji integritas jurnal debit-kredit melalui `execute_code`.

## Quick Reference
- `references/pph-final-umkm.md`: PP 55/2022, threshold omzet Rp500 juta bebas pajak OP, jangka waktu tarif 0,5%.
- `references/withholding-tax.md`: PPh 21 TER A/B/C, PPh 21 Masa Desember, Tenaga Ahli (DPP 50%), PPh 23, PPh 4(2).
- `references/pph-badan-rekonsiliasi.md`: Tarif Badan 22%, fasilitas Pasal 31E, tabel amortisasi & penyusutan fiskal.
- `references/matriks-koreksi-fiskal.md`: Matriks biaya deductible vs non-deductible (natura PMK 66, DER 4:1, nominatif).
- `references/jurnal-akuntansi-pajak.md`: Siklus jurnal PPh 21, 23, 4(2), UMKM, PPN, PPh 25, dan PPh 29 tutup tahun.
- `references/ppn-dan-faktur.md`: Batasan PKP Rp4,8 M, tarif 11%, upload e-Faktur tanggal 15, kompensasi/restitusi.
- `references/administrasi-kup.md`: Kalender jatuh tempo setor/lapor SPT, sanksi denda, formula bunga KMK (maks 24 bln).
- Jalankan kalkulator: `python3 scripts/kalkulator_pajak.py [pphumkm|pph21ter|pph21tahunan|pph21ahli|pph23|pphbadan|ppn|sanksikup]`

## Procedure
1. **Identifikasi Entitas & Skema Pajak:**
   Tentukan bentuk badan usaha, batas omzet, dan kelayakan fasilitas (PP 55/2022 vs Pasal 31E). Buka `references/pph-final-umkm.md` atau `references/pph-badan-rekonsiliasi.md`.
2. **Hitung Pemotongan / Pemungutan Pajak (Withholding):**
   Gunakan `references/withholding-tax.md` dan jalankan perhitungan melalui `terminal`:
   ```bash
   python3 scripts/kalkulator_pajak.py pph21ter --bruto 10000000 --kategori A
   python3 scripts/kalkulator_pajak.py pph23 --nilai 15000000 --jenis jasa
   ```
3. **Analisis Biaya & Rekonsiliasi Fiskal:**
   Periksa akun beban komersial menggunakan `read_file` dan cocokkan dengan panduan di `references/matriks-koreksi-fiskal.md`. Buat kertas kerja koreksi positif dan negatif.
4. **Hitung PPh Badan Terutang:**
   Hitung laba kena pajak dan PPh terutang memanfaatkan fasilitas Pasal 31E:
   ```bash
   python3 scripts/kalkulator_pajak.py pphbadan --omzet 3000000000 --pkp 350000000
   ```
5. **Pencatatan Jurnal & Kepatuhan Pelaporan:**
   Buka `references/jurnal-akuntansi-pajak.md` untuk mencatat jurnal akuntansi pajak secara seimbang. Cek batas setor dan lapor SPT di `references/administrasi-kup.md`.

## Pitfalls
- Mengabaikan threshold Rp500 juta: WP Orang Pribadi UMKM mendapat pembebasan omzet s.d. Rp500 juta per tahun, sedangkan WP Badan UMKM langsung terutang 0,5% sejak rupiah pertama.
- Jangka waktu PP 55/2022: WP PT dibatasi 3 tahun pajak, CV/Firma 4 tahun, dan OP 7 tahun sejak terdaftar. Setelah lewat batas, wajib pembukuan tarif umum.
- PPh 21 Masa Desember: TER hanya berlaku Jan-Nov; Masa Desember wajib menghitung ulang dengan tarif progresif Pasal 17 setahun penuh dikurangi pemotongan Jan-Nov.
- Kenaikan tarif tanpa NPWP: Pemotongan PPh 23 naik 100% (efektif 4% untuk jasa/sewa) bila rekanan tidak memiliki NPWP.
- Natura setelah PMK 66/2023: Jangan mengoreksi positif semua natura secara membabi buta; makanan seluruh karyawan dan sarana kerja resmi dapat dibiayakan secara fiskal.

## Verification
Jalankan pengujian integritas perhitungan melalui `terminal`:
```bash
python3 scripts/kalkulator_pajak.py verify
```
Pastikan seluruh 10 modul pengujian (PPh UMKM Badan/OP threshold, PPh 21 TER, PPh 21 Tahunan Desember, PPh 21 Tenaga Ahli, PPh 23 NPWP/Non-NPWP, PPh Badan 31E, PPN, dan Sanksi KUP) mencetak status `PASSED`.
