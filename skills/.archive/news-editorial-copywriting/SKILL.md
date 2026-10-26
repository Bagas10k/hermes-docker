---
name: news-editorial-copywriting
title: News Editorial Framing & Copywriting
description: "Use when writing or transforming news into engaging content."
author: Bagas Cihuy
version: 1.0
tags: [copywriting, editorial, journalism, framing, sputar-ai, content-creation]
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

## 5A. Tipe Konten 1 — Education-Led Commerce
Untuk media edukasi yang menjual kelas atau produk pengetahuan, perlakukan berita/edukasi gratis sebagai **pemantik minat dan pintu masuk funnel**, bukan sebagai produk akhir semata.

1. **Tarik perhatian melalui realitas aktual:** Mulai dari berita, perubahan aturan, kesalahan umum, atau masalah yang sedang dirasakan audiens.
2. **Berikan kemenangan kecil yang nyata:** Konten gratis wajib tetap berguna dan tuntas pada satu masalah; dilarang menjadi clickbait kosong atau sengaja menyembunyikan jawaban inti.
3. **Bangun kesadaran akan celah:** Setelah memberi insight, tunjukkan secara jujur batas pengetahuan audiens—apa risiko jika salah mengambil keputusan dan kemampuan apa yang perlu mereka kuasai.
4. **Posisikan kelas sebagai kelanjutan:** Produk berbayar menjual struktur, kedalaman, latihan, alat, pendampingan, dan percepatan hasil; bukan menjual ulang informasi gratis yang sengaja dipotong.
5. **CTA harus menyatu dengan materi:** Hubungkan kompetensi yang baru dibahas dengan hasil kelas. Hindari CTA generik yang terasa ditempel di akhir.

Formula naskah: `HOOK aktual → EDUKASI praktis → GAP/konsekuensi → BRIDGE ke metode → CTA kelas`.

Contoh CTA: *“Kalau kamu ingin bisa membedah keputusan finansial seperti ini sendiri—bukan sekadar mengikuti opini—kelas ini mengajarkan kerangkanya langkah demi langkah.”*

Gunakan metrik `save/share → profile visit → DM/klik → lead → pembelian` untuk menilai apakah konten benar-benar memindahkan audiens dari perhatian menuju kepercayaan dan transaksi.

Label internal: **TIPE 1 — EDUCATION-LED COMMERCE**. Konsep strategi ini berasal dari observasi dan arahan Bagas Cihuy.

## 6. Standar Produksi & Keamanan Konten Otomatis (Zero-Slop & Anti-Crash)
Saat menyusun *pipeline* pembuatan konten berita otomatis (seperti skrip CMS, *Instant Dispatcher*, atau generator narasi AI), patuhi protokol berikut:
- **Terjemahan & Lokalisasi Total**: WAJIB 100% Bahasa Indonesia jurnalistik yang lugas. DILARANG KERAS menyalin mentah-mentah (*copy-paste*) abstrak berbahasa Inggris, metadata ArXiv (seperti `arXiv:2609... Announce Type:`), atau istilah teknis/LaTeX asing yang merusak bacaan. Wajib dicerna menjadi narasi cerita.
- **Zero Fluff (Tanpa Basa-Basi)**: Hindari pembukaan dramatis AI (seperti *"Kabar mengejutkan datang dari..."* atau *"Di tengah persaingan sengit..."*). Langsung hantam ke inti peristiwa teknis/angka konkret.
- **Format Caption & Baris Baru (Clean Newlines)**: WAJIB menggunakan karakter line break / newline murni (karakter enter nyata). DILARANG KERAS membiarkan karakter escape literal `\n`, `\\n`, atau `/n` muncul di takarir (caption) maupun teks visual, karena akan tercetak mentah dan merusak estetika publikasi.
- **Batasan Panjang Karakter (Graceful Slicing)**: Jika *prompt* AI meleset dan menghasilkan narasi yang melebihi batas karakter *field* atau layout grafis, **DILARANG melemparkan *Error Exception* (throw Error) yang membuat seluruh skrip/cronjob hancur dan terhenti (crash)**. Alih-alih, potong *string* tersebut secara mulus pada batas maksimal (misal menggunakan `.slice(0, 2000)`).
- **Pencegahan Kebocoran Escape Karakter (`\n\n`)**: Saat merakit payload JSON atau naskah multiline, hindari *double-escaping* string yang menyebabkan teks literal `\n\n` tercetak di kanvas grafis. Pastikan template dan generator selalu menormalkan baris baru (`replace(/\\n/g, '\n')`) agar paragraf terpisah bersih secara visual.
- **Pencegahan Double-Encoding Entitas HTML**: Hindari *double-escaping* karakter khusus seperti ampersand (`&`) pada takarir (*visual caption*) atau metadata agar tidak muncul teks cacat seperti `&AMP;` di kanvas render.
- **Struktur Standar 4 Slide Carousel**: Tepat 4 slide: Slide 1 (Hook/Headline), Slide 2 (Konteks Peristiwa - 2 paragraf padat tanpa poin bullet), Slide 3 (Dampak & Signifikansi - 2 paragraf padat tanpa poin bullet), Slide 4 (Penutup Substantif & CTA Arsip). Dilarang menyisipkan kata "RADAR" pada seluruh naskah publik.
- **Eksekusi Tuntas & Langsung Posting (Zero-Friction Publishing)**: Saat alur pembuatan warta disetujui atau dipicu, selesaikan siklus hingga penerbitan riil ke Instagram secara langsung tanpa berhenti untuk menanyakan konfirmasi opsi ulang yang memperlambat alur ("Apakah mau diterbitkan sekarang?"). Selesaikan render, setujui, unggah via API, dan laporkan bukti tautan publikasi aktif (*live link*).
