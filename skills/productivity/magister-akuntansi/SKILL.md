---
name: magister-akuntansi
description: Analisis laporan keuangan, akuntansi biaya, dan valuasi.
version: 0.1.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags: [Accounting, Finance, Valuation, Governance, SAK, IFRS]
---

# Magister Akuntansi & Keuangan Terapan

Skill ini memandu analisis akuntansi dan keuangan tingkat lanjut berstandar Magister Akuntansi (S2/M.Ak), mencakup telaah standar SAK/IFRS, akuntansi manajemen strategis, diagnostik laporan keuangan, deteksi manipulasi laba, valuasi arus kas, serta pengendalian internal COSO. Skill ini bertindak sebagai alat evaluasi dan perancangan analitis untuk mendukung pengambilan keputusan bisnis strategis, bukan opini audit independen berizin KAP. Seluruh modul perhitungan numerik berbasis pustaka standar Python `decimal`.

## When to Use
- Mengurai kinerja profitabilitas ekuitas menggunakan DuPont 5-Way Analysis.
- Menilai risiko kebangkrutan atau gagal bayar entitas menggunakan Altman Z-Score.
- Menghitung titik impas (BEP), Margin of Safety, dan Degree of Operating Leverage (DOL).
- Mengukur efisiensi modal kerja melalui Siklus Konversi Kas (Cash Conversion Cycle / CCC).
- Menilai kelayakan penerapan standar akuntansi (SAK Umum/IFRS, SAK EP 2025, SAK EMKM) dan PSAK 71/72/73/46.
- Merancang pengendalian internal berbasis COSO 2013 dan mitigasi fraud.

## Prerequisites
- Laporan posisi keuangan (neraca), laporan laba rugi, dan laporan arus kas entitas.
- Rincian klasifikasi biaya tetap vs biaya variabel untuk pemodelan CVP.
- Data periode piutang, persediaan, dan utang usaha untuk analisis CCC.
- Python 3 terpasang untuk menjalankan engine analisis keuangan di `scripts/analisis_keuangan.py`.

## How to Run
- Muat bab referensi topikal menggunakan `skill_view` pada path `references/<file>.md`.
- Jalankan kalkulasi rasio dan model keuangan melalui `terminal` via `scripts/analisis_keuangan.py`.
- Lakukan rekonsiliasi angka dan pemodelan skenario lanjutan melalui `execute_code`.

## Quick Reference
- `references/akuntansi-keuangan-ifrs-sak.md`: SAK IFRS vs SAK EP vs EMKM, PSAK 71 (ECL), PSAK 72 (5-step revenue), PSAK 73 (sewa), PSAK 46 (pajak tangguhan).
- `references/akuntansi-manajemen-strategis.md`: CVP, DOL, Activity-Based Costing (ABC), Cash Conversion Cycle (CCC), variance analysis.
- `references/analisis-laporan-keuangan-valuasi.md`: DuPont 5-way, Altman Z-Score, Beneish M-Score, FCFF, FCFE, WACC, EVA.
- `references/pengendalian-internal-forensik.md`: COSO 2013 framework, fraud diamond, SOP three-way matching, segregation of duties.
- Jalankan analisis keuangan: `python3 scripts/analisis_keuangan.py [dupont5|altmanz|cvp|ccc|verify]`

## Procedure
1. **Klasifikasi Kerangka & Kebijakan Akuntansi:**
   Tentukan standar pelaporan yang tepat (SAK Umum, SAK EP, atau SAK EMKM) berdasarkan akuntabilitas publik dan kebutuhan pemangku kepentingan. Rujuk `references/akuntansi-keuangan-ifrs-sak.md`.
2. **Evaluasi Struktur Biaya & Kapasitas Operasional:**
   Pisahkan biaya tetap dan variabel. Hitung BEP dan risiko leverage operasional via `terminal`:
   ```bash
   python3 scripts/analisis_keuangan.py cvp --fixed-cost 500000000 --price 100000 --var-cost 60000 --actual-units 20000
   ```
3. **Analisis Efisiensi Modal Kerja:**
   Hitung siklus konversi kas untuk mengukur kecepatan perputaran modal kerja:
   ```bash
   python3 scripts/analisis_keuangan.py ccc --dio 45 --dso 30 --dpo 40
   ```
4. **Bedah Kinerja Laba & Diagnostik Risiko Keuangan:**
   Gunakan DuPont 5-Way untuk membedah pemicu ROE dan Altman Z-Score untuk menguji solvabilitas via `references/analisis-laporan-keuangan-valuasi.md`:
   ```bash
   python3 scripts/analisis_keuangan.py dupont5 --ebit 200000000 --ebt 180000000 --net-income 140000000 --sales 1000000000 --assets 800000000 --equity 500000000
   ```
5. **Perancangan Tata Kelola & Mitigasi Fraud:**
   Susun matriks pengendalian internal COSO dan verifikasi pemisahan fungsi sesuai `references/pengendalian-internal-forensik.md`.

## Pitfalls
- Mengandalkan laba akrual tanpa menguji arus kas: Laba bersih tinggi yang tidak diimbangi arus kas masuk operasional nyata mengindikasikan potensi piutang macet atau distorsi pengakuan pendapatan.
- Salah mengasumsikan biaya tetap: Pada kapasitas penuh (*relevant range*), biaya tetap akan melompat (*step-fixed cost*); perhitungkan kapasitas mesin dan ruang kerja saat ekspansi.
- Generalisasi model Altman Z-Score: Model original tahun 1968 diperuntukkan bagi perusahaan manufaktur publik; gunakan formula modifikasi 1983/1993 (Z'') untuk entitas privat atau perusahaan jasa.

## Verification
Jalankan pengujian integritas formula melalui `terminal`:
```bash
python3 scripts/analisis_keuangan.py verify
```
Pastikan seluruh pengujian model matematis (DuPont, Altman Z-Score, CVP, dan CCC) mengembalikan status `PASSED`.
