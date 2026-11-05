---
name: vps-decommission-and-local-migration
description: Use when migrating agent system from VPS to local machine.
version: 1.1.0
author: Bagas Cihuy
license: MIT
metadata:
  hermes:
    tags: [vps, migration, decommission, portability, backup]
    related_skills: [agent-knowledge-portability]
---
# VPS Decommission and Local Migration

## When to Use
Gunakan skill ini saat server/VPS akan dinonaktifkan atau dimatikan, dan seluruh ekosistem agent (skills, SOUL, MCP servers, memori, vault Obsidian, dan repositori proyek) perlu diaudit, dirapikan dari bloat duplikasi, serta dikemas ke dalam bundel portabel untuk dipindahkan ke komputer/laptop lokal.

## Core Migration Workflow

1. **Audit & Checkpoint Repositori Aktif**
   - Periksa perubahan uncommitted di seluruh proyek (`git status`).
   - Lakukan commit pengaman: `git commit -am "chore(vps-backup): checkpoint uncommitted changes before vps decommission"`.
   - Untuk proyek tanpa Git (folder dokumen, vault, dataset): jalankan `git init` dan buat initial commit dengan identitas resmi pengguna agar riwayat berkas terlindungi.

2. **Deduplikasi Bloat Profil Agen (`~/.hermes/profiles`)**
   - **Pitfall:** Sub-profil yang menyalin folder `skills/` secara fisik akan melipatgandakan ukuran disk (~600 MB per profil). 9 profil dapat memakan >2.5 GB.
   - **Solusi:** Ganti folder fisik `~/.hermes/profiles/<nama>/skills` menjadi symlink yang mengarah ke shared `~/.hermes/skills`. Ini memangkas ukuran arsip secara drastis tanpa merusak fungsionalitas sub-profil.

3. **Offline Knowledge Vault Indexing (SQLite FTS5)**
   - Saat memindahkan ribuan berkas catatan (misal vault Obsidian), buat SQLite database lokal berfitur FTS5 (Full-Text Search) dan mode WAL.
   - Sertakan skrip pencarian mandiri Python (`search_vault.py`) yang berjalan instan (<10ms) tanpa dependensi LLM atau internet. Ini memungkinkan penelusuran nalar langsung di terminal lokal.

4. **One-Command Bootstrapper (`setup_local.sh`)**
   - Sediakan skrip instalasi/pemulihan otomatis yang menyalin konfigurasi, SOUL, MCP, memori, dan mengaitkan symlink skills di laptop baru secara otomatis tanpa intervensi manual panjang.

5. **Pengemasan & Verifikasi Biner**
   - Kemas bundel portabel dengan `tar -czf`.
   - Hitung SHA-256 checksum dan ukuran berkas sebagai bukti integritas fisik sebelum menyerahkan perintah SCP/rsync kepada pengguna.