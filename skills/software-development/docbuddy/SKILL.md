---
name: docbuddy
description: Use when adopting, proposing, or updating evidence-based repository documentation via DocBuddy CLI.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [docbuddy, onefreq, documentation, manifest-scanner, architecture, verification, offline]
    related_skills: [cabinet-discipline-and-anti-overtesting, structured-project-execution, otak-koding]
---

# DocBuddy & ONEFREQ Documentation Workflow

Kakas baris perintah deterministik berbasis bukti untuk menghasilkan dan memperbarui dokumen proyek `.onefreq/ARCHITECTURE.md` dan `.onefreq/VERIFICATION.md` tanpa API AI eksternal.

## Kapan Digunakan
- Memulai proyek baru atau menata dokumentasi proyek yang sudah ada.
- Menyediakan kontrak kanonik `AGENTS.md` agar seluruh agen (Hermes, Claude Code, Cursor, Codex) memahami batasan dan arsitektur repositori.
- Memperbarui snapshot arsitektur dan kontrak uji setelah penambahan dependensi/framework baru.

## Doktrin Standarisasi: Wajib Full ONEFREQ Pack (Mandat Mas Bagas)
Sesuai ketetapan Mas Bagas, **setiap proyek (baru maupun yang sedang berjalan) wajib mengadopsi Full ONEFREQ Pack secara seragam**. Tidak ada pemotongan tier; seluruh 15 dokumen standar kontrak, arsitektur, verifikasi, batasan keselamatan, dan catatan keputusan wajib hadir di repositori proyek.

## CLI Commands (Tersedia Global)
```bash
# Adopsi Instan Satu Langkah (Menyalin AGENTS.md, CLAUDE.md, .onefreq/ & memindai manifes otomatis)
docbuddy-adopt <path_proyek>

# Pemindaian Manual & Pengajuan Usulan Berbasis Bukti
docbuddy propose <path_proyek> --proposal /tmp/proposal.json

# Penerapan Usulan Setelah Ditinjau
docbuddy apply <path_proyek> --proposal /tmp/proposal.json
```

## Prosedur Penerapan pada Repositori
1. Jalankan adopsi otomatis satu baris:
   ```bash
   docbuddy-adopt /path/ke/proyek
   ```
2. Skrip otomatis akan:
   - Memasang `AGENTS.md` & `CLAUDE.md` sebagai gerbang kontrak lintas-agen.
   - Memasang direktori lengkap `.onefreq/` (15 berkas template standar).
   - Memindai manifes (`package.json`, `pyproject.toml`, dll.) dan memperbarui `.onefreq/ARCHITECTURE.md` serta `.onefreq/VERIFICATION.md` secara deterministik.
3. Lengkapi konteks bisnis di `.onefreq/PROJECT_BRIEF.md` dan batasan risiko di `.onefreq/SAFETY_BOUNDARIES.md`.

## Batasan & Prinsip
- `propose` tidak pernah memodifikasi file target secara sepihak.
- `apply` menolak perubahan jika file sumber di repositori berubah setelah proposal dibuat (anti-stale).
- Tidak membaca berkas `.env` atau kunci rahasia (*secret-safe*).
