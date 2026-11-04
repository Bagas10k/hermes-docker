---
name: sputarai-content-system
description: "Use when producing, auditing, or maintaining Sputar AI."
version: 1.0.0
author: Bagas & Hermes Agent
---

# Sputar AI Content System (@sputarai)

Sputar AI adalah mesin kurasi dan produksi warta inovasi teknologi serta gawai konsumen otomatis untuk akun Instagram `@sputarai`.

## 1. Lokasi Proyek & Layanan Inti
- **Direktori Kode Aktif:** `/home/ubuntu/hermes-backup/projects/penelitian-pola-pikir-ai/`
- **Layanan PM2:** `sputarai-ml-scorer` (ID 5, port HTTP `127.0.0.1:3055`)
  - Skrip server ML: `/home/ubuntu/sputarball/ml_scorer/server.py`
  - Venv: `/home/ubuntu/ml-resource-kit/.venv/bin/python`
  - Model: `sentence-transformers/all-MiniLM-L6-v2`
- **Database Utama:** SQLite `/home/ubuntu/hermes-backup/projects/penelitian-pola-pikir-ai/data/db/chronicle.sqlite`
- **Catatan Arsitektur Obsidian:** `/home/ubuntu/otak-koding/BUKU_CATATAN/010-arsitektur-sputarai-ml-trend-scorer.md`

## 2. Struktur Berkas Kunci
- `server.js`: Web server Express & endpoint API internal.
- `scripts/editorial-ai.js`: Generator naskah warta berbahasa Indonesia alami berbasis LLM.
- `scripts/instant-news-dispatcher.js`: Pengirim otomatis dan pemicu publikasi Instagram.
- `scripts/content-cms.js`: Pengelola artikel dan pipeline status berita.
- `public/carousel.html`: Template visual carousel 4 slide untuk rendering Puppeteer.

## 3. Standar Konten Warta 4 Slide (@sputarai)
Carousel warta teknologi konsumen wajib tepat 4 slide (rasio 4:5):
- **Slide 1:** Headline gebrakan inovasi teknologi & gawai dalam Bahasa Indonesia lugas.
- **Slide 2:** Konteks arsitektur dan terobosan fitur cerdas (prosesor, on-device AI, fabrikasi chip).
- **Slide 3:** Observasi data kunci, efisiensi sistem, dan perbandingan performa terukur.
- **Slide 4:** Dampak industri & Call to Action (CTA) khas `@sputarai`.

## 4. Gaya Bahasa & Anti-AI Slop
- Wajib 100% Bahasa Indonesia alami, santai, dan cerdas.
- Dilarang frasa klise terjemahan LLM kaku (seperti 'merevolusi lanskap', 'menyelam lebih dalam', 'game changer').
- Jangan gunakan emoji pada teks grafis UI/render.
