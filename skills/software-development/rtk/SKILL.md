---
name: rtk
description: "RTK (Rust Token Killer) - Compress CLI outputs and save 60-90% LLM tokens on shell commands."
version: 1.0.0
author: rtk-ai & Hermes
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [rtk, token-savings, cli, optimizer, rust]
---

# RTK (Rust Token Killer) CLI

RTK adalah proxy CLI ultra-cepat berbasis Rust yang memotong kebisingan output terminal sebelum masuk ke context window LLM, menghemat 60-90% token.

## Perintah Utama

- `rtk git <subcommand>`: Ringkas status, diff, log, commit tanpa dekorasi berlebih.
- `rtk ls [path]`: Menampilkan daftar berkas ringkas terkompresi.
- `rtk tree [path]`: Struktur direktori padat.
- `rtk read <file>`: Membaca berkas dengan menyaring komentar atau baris kosong jika diminta.
- `rtk grep <pattern> [path]`: Menampilkan kecocokan grep secara terkelompok per file tanpa whitespace boros.
- `rtk find [pattern]`: Pencarian file dengan output pohon kompak.
- `rtk diff`: Diff ultra-padat (hanya baris yang berubah).
- `rtk json <file>`: Kompresi format JSON (opsi `--keys-only` untuk melihat skema).
- `rtk err <command>`: Jalankan perintah dan hanya tampilkan error / warning jika gagal.
- `rtk gain`: Menampilkan total penghematan token yang berhasil diperoleh.
