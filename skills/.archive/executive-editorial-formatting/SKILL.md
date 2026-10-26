---
name: executive-editorial-formatting
description: "Use when formatting summaries, workflows, or chat reports."
version: 1.0.0
author: Hermes Curator
license: MIT
metadata:
  hermes:
    tags: [formatting, editorial-clean, readability, telegram-chat, scannability]
---

# Executive Editorial Formatting

Panduan formatting teks dan rangkuman agar mudah dipindai mata, rapi, dan tidak padat berjejal.

## Prinsip Utama
1. **Anti-Wall of Text:** Hindari paragraf panjang yang menggabungkan beberapa konsep dalam satu blok teks rapat. Format inline yang berjejal (misal: "1. A -> B. 2. C -> D" dalam satu blok paragraf) sangat tidak tertata dan mengganggu keterbacaan.
2. **Hirarki Visual Berjarak (Spacious Hierarchy):**
   - Gunakan pemisah horizontal (`---`) antar bagian atau tahapan besar.
   - Gunakan penomoran tebal dan judul sub-tahap yang kontras (misal: `**1. Penebusan Kuota (Hulu)**`).
   - Beri jarak baris kosong yang cukup agar tampilan di chat/layar mobile lega dipindai mata (*scannable*).
3. **Poin Berbutir Ringkas (1-2 Baris):**
   - Setiap poin penjabaran maksimal 1-2 baris per butir.
   - Format sub-poin menggunakan daftar berbutir (*bullet points*), bukan kalimat beranak pinak dalam satu baris.
   - Paparkan hubungan aksi dan dampak menggunakan panah alur logis atau kalimat terstruktur.
   - **Tolak Format Run-on Sentences:** Jangan pernah menggabungkan nomor beruntun (misal `1. ... 2. ... 3. ...`) ke dalam satu paragraf berjalan. Format tersebut membuat mata pembaca cepat lelah dan terlihat berantakan di layar obrolan.
4. **Visual & Media Editorial (Carousel & Social):**
   - **Slide Kontekstual Berbasis Visual Nyata:** Saat membuat infografis/carousel berita atau slide penjelasan (misal Slide 2), utamakan foto dokumentasi nyata, skema arsitektur otentik, atau foto laboratorium teknis dibanding diagram kotak SVG generik.
   - **Proporsi Gambar Tanpa Terpotong (Anti-Crop):** Pastikan seluruh teks judul dan elemen dalam aset gambar tidak terpotong oleh batas bingkai dengan menerapkan `object-fit: contain`, latar belakang bersih, serta *padding* aman di dalam wadah pembungkus.
   - **Relevansi Konteks Semantik:** Visual wajib cocok dengan inti peristiwa (contoh: berita medis/bedah menggunakan foto ruang operasi klinis, bukan komponen PC generik).
   - **Variasi Aset & Deduplikasi:** Lakukan kurasi dinamis dan lacak riwayat aset (minimal 30 postingan terakhir) agar visual tidak berulang (*itu-itu saja*).
   - **Stopping Power & Layering 3D:** Pada Slide 1 (Cover), ciptakan ilusi kedalaman (subjek di midground menonjol ke depan / *foreshortening*, judul tebal berkarakter, dan kartu UI mengambang).
   - **Formula Hook Copywriting:** Judul cover carousel edukasi menggunakan pola `[Angka / Listicle] + [Manfaat / Solusi Spesifik] + [Pemicu Urgensi / Tren (FOMO)]`.
   - **Mesin Komentar (Lead-Magnet):** Gunakan pemicu kata kunci tunggal di komentar (misal: *Komen "CLAUDE"*, *Komen "SLIDE"*) untuk memicu distribusi algoritma organik.
5. **Disiplin Bahasa & Redaksi:**
   - Hapus kata pengantar/penutup klise.
   - Sampaikan substansi secara langsung, berbobot, dan enak dibaca.
