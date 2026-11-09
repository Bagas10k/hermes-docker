---
name: news-editorial-copywriting
title: News Editorial Framing & Copywriting
description: "Use when writing or transforming news into engaging content."
author: Bagas Cihuy
version: 1.0
tags: [copywriting, editorial, journalism, framing, sputar-ai, content-creation]
related_skills:
  - seo-expert
  - content-intelligence
  - instagram-publishing-automation
  - tiktok-content-extraction
---

# News Editorial Framing & Copywriting

Panduan operasional untuk merombak teks berita kaku (press release, dokumen birokrasi, laporan angka) menjadi konten media yang sangat *engaging*, tajam, dan menarik perhatian. Ini adalah tulang punggung pengelolaan bahasa untuk media berita modern Sputar AI.

Ketika diminta untuk membuat, meringkas, atau menulis ulang konten berita, **wajib** terapkan teknik-teknik pengelolaan bahasa (*copywriting* dan *framing*) berikut ini:

## 1. Humanization (Dampak pada Manusia)
Berita membosankan karena terlalu fokus pada institusi, angka statistik, atau proses birokrasi.
- **Aturan:** Jangan mulai dari gedungnya atau rapatnya; **mulai dari manusianya**.
- **Praktik:** Bingkai berita birokrasi yang kering menjadi narasi tentang ancaman, perubahan, atau keuntungan langsung bagi keseharian audiens.
- **Contoh:** 
  - ❌ *DPR mengesahkan revisi UU Perpajakan No. 12 Tahun 2026 siang ini.*
  - ✅ *Mulai bulan depan, potongan pajak di slip gajimu bakal berubah. Ini 3 hal yang diam-diam disahkan siang tadi.*

## 2. Wall Street Journal (WSJ) Formula
Formula jurnalisme yang terbukti ampuh mengubah topik paling makro dan garing menjadi cerita yang mengikat empati.
- **Langkah 1 (Anekdot):** Buka dengan cerita satu individu atau kejadian mikroskopis yang sangat spesifik. (Contoh: *Keluhan Pak Budi yang wartegnya sepi karena harga telur naik gila-gilaan*).
- **Langkah 2 (Nut Graf):** Pada paragraf kedua/ketiga, lakukan *zoom-out* secara drastis. Jelaskan bagaimana cerita individu tersebut adalah bagian/dampak dari berita atau tren makro yang jauh lebih besar. (Contoh: *Apa yang dialami Pak Budi adalah efek domino dari Inflasi Pangan...*)

## 3. Spiky Point-of-View (Sudut Pandang Tajam)
Media tradisional mengambil judul yang *neutral* dan "aman" (sehingga membosankan). Konten modern harus punya *hook* yang melawan arus pikiran umum.
- **Aturan:** Temukan kontradiksi dari sebuah berita. Gunakan paradoks tersebut sebagai *Lead* (kalimat pembuka) atau Headline.
- **Contoh:**
  - ❌ *Pertumbuhan Ekonomi Q2 Melambat Jadi 4,9%.*
  - ✅ *Gaji Naik tapi Terasa Makin Miskin? Laporan Ekonomi Q2 Ini Menjelaskan Kenapa Dompetmu Bocor Halus.*

## 4. Show, Don't Tell (Analogi Visual)
Pengelolaan bahasa di berita tidak butuh hiperbola yang menipu, tapi butuh analogi visual yang gampang dicerna otak untuk metrik yang abstrak.
- **Aturan:** Terjemahkan angka raksasa atau metrik teknis ke dalam ukuran fisik atau barang sehari-hari.
- **Contoh:**
  - ❌ *Proyek ini memakan biaya overhead hingga Rp 10 Triliun.*
  - ✅ *Biaya proyek ini setara dengan membangun 10.000 puskesmas baru di pelosok desa.*

## 5. Workflow AI (NotebookLM / Gemini Notebook)
Saat mengembangkan portal berita atau membedah dokumen PDF tebal:
1. **Research & Extract:** Gunakan NotebookLM untuk mencerna dokumen mentah dan merangkum *insights*.
2. **Prompt Spesifik:** Perintahkan AI dengan instruksi: *"Ekstrak 3 poin paling berdampak langsung bagi rakyat dari dokumen ini. Lalu buatkan 3 alternatif judul menggunakan gaya Spiky POV dan analogi Show, Don't Tell."*

## 6. Standar Produksi & Keamanan Konten Otomatis (Zero-Slop & Anti-Crash)
Saat menyusun *pipeline* pembuatan konten berita otomatis (seperti skrip CMS, *Instant Dispatcher*, atau generator narasi AI), patuhi protokol berikut:
- **Terjemahan & Lokalisasi Total**: WAJIB 100% Bahasa Indonesia jurnalistik yang lugas. DILARANG KERAS menyalin mentah-mentah (*copy-paste*) abstrak berbahasa Inggris, metadata ArXiv (seperti `arXiv:2609... Announce Type:`), atau istilah teknis/LaTeX asing yang merusak bacaan. Wajib dicerna menjadi narasi cerita.
- **Zero Fluff (Tanpa Basa-Basi)**: Hindari pembukaan dramatis AI (seperti *"Kabar mengejutkan datang dari..."* atau *"Di tengah persaingan sengit..."*). Langsung hantam ke inti peristiwa teknis/angka konkret.
- **Batasan Panjang Karakter (Graceful Slicing)**: Jika *prompt* AI meleset dan menghasilkan narasi yang melebihi batas karakter *field* atau layout grafis, **DILARANG melemparkan *Error Exception* (throw Error) yang membuat seluruh skrip/cronjob hancur dan terhenti (crash)**. Alih-alih, potong *string* tersebut secara mulus pada batas maksimal (misal menggunakan `.slice(0, 2000)`).
