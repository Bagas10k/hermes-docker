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

## CLI Commands (Tersedia Global)
```bash
# 1. Ajukan usulan pembaruan berdasarkan manifes aktual (package.json, pyproject.toml, Cargo.toml, go.mod)
docbuddy propose . --proposal /tmp/proposal.json

# 2. Tinjau diff yang dihasilkan di terminal. Jika disetujui, terapkan:
docbuddy apply . --proposal /tmp/proposal.json
```

## Prosedur Penerapan pada Repositori Baru
1. Salin template dasar dari `/home/ubuntu/docbuddy/`:
   ```bash
   cp /home/ubuntu/docbuddy/AGENTS.md .
   cp /home/ubuntu/docbuddy/CLAUDE.md .
   cp -r /home/ubuntu/docbuddy/.onefreq .
   ```
2. Jalankan pemindaian manifes:
   ```bash
   docbuddy propose . --proposal /tmp/onefreq-proposal.json
   ```
3. Periksa diff, lalu terapkan perubahan:
   ```bash
   docbuddy apply . --proposal /tmp/onefreq-proposal.json
   ```
4. Lengkapi tujuan bisnis di `.onefreq/PROJECT_BRIEF.md` dan batasan risiko di `.onefreq/SAFETY_BOUNDARIES.md`.

## Batasan & Prinsip
- `propose` tidak pernah memodifikasi file target secara sepihak.
- `apply` menolak perubahan jika file sumber di repositori berubah setelah proposal dibuat (anti-stale).
- Tidak membaca berkas `.env` atau kunci rahasia (*secret-safe*).
