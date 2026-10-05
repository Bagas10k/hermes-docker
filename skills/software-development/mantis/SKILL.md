---
name: mantis
description: Use when auditing security. Google Mantis review & patch.
version: 2.0.0
author: Google & Hermes
license: Apache-2.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [mantis, security, vulnerability, audit, patch, threat-model, google, sast, pentest]
    related_skills: [defensive-web-security-audit, application-auth-security, ponytail]
---

# Google Mantis: Unified Autonomous Security Suite

Mantis adalah rangkaian audit dan review keamanan otonom komprehensif dari Google untuk AI Coding Agent. Seluruh tahapan terintegrasi dalam modul tunggal ini melalui referensi modular di `references/`.

## When to Use
Gunakan saat melakukan audit keamanan kode sumber, threat modeling, reproduksi crash/vulnerability (PoC), review celah keamanan, pembuatan patch minimal, atau penyusunan laporan keamanan formal.

## Tahapan Pipeline Mantis (6 Stages)

### 1. Perencanaan & Reconnaissance
Petakan arsitektur, trust boundaries, dan riwayat kode sebelum menganalisis celah:
- `references/plan.md`: Formulasi strategi audit terfokus.
- `references/threat-model.md`: Pemetaan trust boundaries dan attack surfaces.
- `references/architecture.md`: Pemetaan dependensi komponen kritis.
- `references/structural-index.md` & `references/mantis-structural-index.md`: Indeks semantik kontrol aliran dan data sensitif.
- `references/summarize.md` & `references/history.md`: Analisis riwayat komit VCS dan perubahan berisiko tinggi.

### 2. Riset Kerentanan (Vulnerability Research)
Identifikasi kelemahan logika, sanitasi input, dan potensi exploit:
- `references/researcher.md`: Audit kode sumber target berdasarkan pola celah (SAST/Taint analysis).
- `references/chain.md`: Analisis keterkaitan beberapa temuan untuk mengidentifikasi exploit chains multi-tahap.
- `references/mantis-sast-seed.md` & `references/mantis-kb-query.md`: Query basis pengetahuan aturan SAST Mantis.

### 3. Review, Dedup & Kalibrasi Risiko
Saring false positives dan tetapkan tingkat keparahan berdasarkan bukti empiris:
- `references/review.md`: Validasi temuan terhadap kode sumber riil.
- `references/critic.md`: Uji kelayakan temuan di lingkungan produksi.
- `references/dedupe.md`: Konsolidasi temuan serupa agar tidak redundan.
- `references/calibrate.md` & `references/calibration_rules.md`: Kalkulasi skor risiko final (CVSS/CWE).

### 4. Reproduksi Kerentanan (Crash Reproduction / PoC)
Buktikan kerentanan secara empiris tanpa merusak sistem produksi:
- `references/reproduce.md`: Pembuatan reproducer mandiri/PoC di lingkungan sandbox isolasi.

### 5. Patching Minimal & Transaksional
Terapkan perbaikan tuntas dengan intervensi sesedikit mungkin (sejalan dengan prinsip `ponytail`):
- `references/patch.md`: Desain perbaikan dengan isolasi transaksional dan regresi nol.
- `references/patch_rebasing.md`: Penanganan merge dan rebasing patch keamanan.

### 6. Pelaporan, Refleksi & Integrasi CI/CD
Dokumentasikan dan cegah regresi masa depan:
- `references/report.md`: Penyusunan laporan keamanan standar industri (Executive summary, impact, PoC, fix).
- `references/reflect.md` & `references/advise.md`: Ekstraksi pelajaran dan guardrail pencegahan celah baru.
- `references/pipeline-adapter.md`: Integrasi pipeline Mantis ke workflow otomatisasi.

## Standar Operasional & Verification
1. Selalu gunakan `read_file` dan `search_files` untuk memeriksa kode riil sebelum membuat klaim celah.
2. Setiap klaim keparahan (High/Critical) wajib memiliki bukti alur kontrol atau reproducer PoC nyata.
3. Patch keamanan harus meminimalisasi diff kode dan diverifikasi dengan tes fungsional.
