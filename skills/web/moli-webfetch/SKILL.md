---
name: moli-webfetch
description: "Fetch and crawl JavaScript websites with lightweight Moli."
version: 1.1.18
author: "lexmount & Bagas Cihuy"
license: Apache-2.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [web, scraper, headless-browser, moli, rust, low-memory]
---

# Fetch Websites with Moli

Gunakan perintah `moli fetch` untuk membaca atau mengekstrak konten web berbasis JavaScript. Moli mengeksekusi JavaScript dan memelihara DOM hidup secara bawaan dengan konsumsi RAM sangat rendah (~50 MB vs 700 MB Chromium).

## Kapan Menggunakan
- Scraping halaman SPA/React/Next.js yang membutuhkan rendering JavaScript tanpa membebani RAM VPS.
- Ekstraksi langsung konten web menjadi Markdown bersih (`--dump markdown`).
- Pengambilan screenshot tampilan halaman web (`--dump screenshot`).

## Cara Menjalankan

1. Pastikan biner `moli` tersedia di PATH (`which moli`). Jika belum, biner terpasang di `/home/ubuntu/.local/bin/moli`.
2. Ekstraksi halaman web sebagai Markdown bersih:

```bash
moli fetch --dump markdown --wait done "https://example.com"
```

3. Untuk halaman dinamis dengan AJAX/fetch tertunda, gunakan sinyal kesiapan:

```bash
moli fetch --dump markdown --wait networkidle "https://example.com/app"
moli fetch --dump markdown --wait-selector "main article" "https://example.com/news"
```

4. Untuk screenshot visual (memerlukan kalkulasi layout on-demand):

```bash
moli fetch --layout --dump screenshot "https://example.com" > /tmp/viewport.png
moli fetch --layout --dump screenshot_full "https://example.com" > /tmp/full.png
```

## Format Keluaran (`--dump`)
- `markdown`: Format standar untuk konsumsi LLM, artikel, dan dokumentasi.
- `html`: Format DOM mentah yang telah dirender JS.
- `json`: Data terstruktur lengkap (status HTTP, final URL, headers, network trace).
- `screenshot`: Gambar PNG ukuran viewport (wajib `--layout`).
- `semantic_tree`: Aksesibilitas dan struktur semantik pohon elemen.

## Batasan & Aturan Keamanan
- Moli adalah crawler tier-1 berkecepatan tinggi; gunakan Chromium penuh hanya untuk grafis 3D/WebGL kompleks.
- Selalu buang file screenshot sementara setelah selesai digunakan untuk menjaga kebersihan disk server.
