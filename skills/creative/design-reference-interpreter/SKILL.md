---
name: design-reference-interpreter
description: Interpret design references to UI code and visual review.
version: 1.0.0
author: Bagas Cihuy, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ui-ux, design-dna, vibe-mapping, visual-judge, frontend]
    related_skills: [otak-koding, design-vault]
---

# Design Reference Interpreter

## Overview
Menerjemahkan referensi desain visual/gambar ke dalam implementasi kode UI secara otonom dan terstruktur. Agen tidak pasif menunggu instruksi per elemen ("pakai bagian ini"), melainkan secara aktif membedah referensi, mengekstrak Design DNA, melakukan triase **Adopt / Transform / Reject**, memetakan vibe tanpa terjebak template klise, dan memverifikasi hasil render nyata menggunakan **Visual Judge** ("Mata Kedua").

## Alur Kerja Utama (Design Translation Pipeline)

```
Kumpulan Bahan Mentah / Feed Warta
        ↓
[Sub-Agent: Content Selector] -> Filter kebaruan, kredibilitas, & QC gambar awal (bebas watermark)
        ↓
Paket Konten Terpilih
        ↓
Pahami Konteks Produk (Audience, Use-case, Tone)
        ↓
Image Analysis (via vision_analyze / screenshot)
        ↓
Ekstrak Design DNA (Layout, Typography, Color, Interaction, Density)
        ↓
Nilai Kecocokan Konteks + Vibe (vibe-mapping.md)
        ↓
Triase: Adopt / Transform / Reject
        ↓
Bentuk Design Direction Terarah
        ↓
[Builder Agent] -> Build UI / Code (HTML, Tailwind, React, Vue, Svelte)
        ↓
[Visual Judge / Critic] -> Visual Review via browser screenshot (5 Gerbang Audit)
        ↓
Refine (Iterasi hingga lulus acceptance test)
```

---

## 1. Ekstraksi Design DNA

Saat membaca gambar atau mock referensi desain, jangan meniru secara mentah. Bedah DNA desain ke dalam 5 elemen:

1. **Layout & Grid Anatomy**: Struktur hirarki, ritme vertikal, bento grid, split column, asimetri terukur, atau kanvas tunggal.
2. **Typography Hierarchy**: Rasio kontras heading vs body, pelacakan letter-spacing, font pairing (sans-serif netral, mono teknikal, atau editorial serif), serta berat font (*font-weight*).
3. **Color & Lighting System**: Surface layer (background, elevated card), aksen fungsional, rasio kontras WCAG, dan sifat pencahayaan (matte, deep slate, warm paper, subtle glow).
4. **Interaction & Micro-Physics**: Feedback hover, transisi taktil, border highlight, spring animation, atau sudut lipatan kertas (*paper peel*).
5. **Information Density**: Compact enterprise vs spacious marketing, batas padding kartu (maksimal 16-24px untuk dashboard), serta efisiensi ruang layar.

---

## 2. Triase: Adopt / Transform / Reject

Agen wajib mengambil keputusan desain secara tegas dan menyajikan alasannya:

- **ADOPT (Ambil Utuh)**: Elemen referensi yang terbukti meningkatkan keterbacaan, efisiensi alur, atau hierarki informasi yang selaras dengan produk.  
  *Contoh:* "Mengadopsi struktur layout 2-kolom asimetris dari Referensi A karena memisahkan kontrol dan feed secara efisien."
- **TRANSFORM (Sesuaikan)**: Elemen yang konsep dasarnya bagus namun parameternya harus diadaptasi agar cocok dengan konteks produk Bos Bagas.  
  *Contoh:* "Mengubah pola interaksi hover Referensi B: efek neon diganti menjadi border glow cyan halus 1px agar tidak terlalu bising."
- **REJECT (Tolak Tegas)**: Elemen yang menurunkan aksesibilitas, bertentangan dengan tone produk, atau sekadar dekorasi klise AI.  
  *Contoh:* "Menolak palet warna ungu pekat dan glassmorphism tebal dari Referensi C karena membuat teks tabel sulit dibaca di mobile."

---

## 3. Disiplin Pemetaan Vibe (Anti-Template Klise)

Rujuk panduan detail di `references/vibe-mapping.md`. Prinsip utama:
- **Futuristic** ≠ Neon ungu + glassmorphism. Eksekusi sejati: Tipografi monospace rapat, indikator status real-time, zero-delay feedback, clean high-tech grid.
- **Premium / Luxury** ≠ Hitam emas berlebihan. Eksekusi sejati: Spacing lega, tipografi berwibawa, micro-border presisi (0.5px - 1px border subteks), animasi sangat halus.
- **Editorial** ≠ Sekadar font serif kuno. Eksekusi sejati: Kontras kontras tinggi, drop-cap berbobot, asimetris magazine grid, ritme kutipan yang bernafas.
- **Technical / Console** ≠ Terminal hacker hijau hitam. Eksekusi sejati: Density tinggi, tabular numbers, status badge fungsional, keyboard shortcut hints.

---

## 4. Visual Judge / Design Critic ("Mata Kedua")

Setelah kode selesai dibuat dan dirender di browser:
1. Tangkap tampilan aktual layar (desktop & mobile) via browser harness / `vision_analyze`.
2. Evaluasi hasil terhadap 5 kriteria pengujian kritis (`references/acceptance-tests.md`):
   - **Keterbacaan & Kontras (Readability Gate)**: Apakah teks mudah dibaca tanpa squinting?
   - **Kepadatan & Spacing (Density Gate)**: Apakah ada padding kosong berlebih (>50% dead space)?
   - **Responsivitas Mobile**: Apakah layout beradaptasi rapi pada lebar 390px tanpa horizontal scroll?
   - **Konsistensi Vibe**: Apakah artefak mewujudkan vibe yang ditargetkan tanpa elemen klise?
   - **Anti-AI-Slop Check**: Nol emoji di ikon tombol/tabel, nol pill kicker dekoratif di atas heading, nol decorative fluff.
3. Jika ada kegagalan, Visual Judge mengeluarkan daftar perbaikan konkret (*actionable items*), dan agen menjalankan **Refine** secara mandiri.
