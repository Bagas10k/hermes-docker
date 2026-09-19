---
name: swiss-editorial-carousel
title: Swiss Editorial & Modern Magazine Carousel Design System
description: "Use when designing editorial magazine carousel slides."
author: Bagas Cihuy
version: 1.0
tags: [carousel, instagram, editorial, typography, swiss-style, magazine, minimal]
---

# Swiss Editorial & Modern Magazine Carousel Design System

Sistem desain carousel Instagram (1080×1350, rasio 4:5) berbasis standar majalah cetak internasional, Swiss Modernism (*International Typographic Style*), dan editorial fashion agency (*The Editorial Drop*, *Meraki*, *Die Ende*).

Filosofi inti: **"When nothing screams, everything feels intentional."** Mengeliminasi semua AI slop (pendaran neon, badge melayang sintetis, gradasi murahan) dan menggantinya dengan gravitasi visual cetak otentik.

---

## 1. Skala Tipografi Ekstrem (*The 98/100 Typography Rule*)

Tipografi adalah tulang punggung estetika ini. Kuncinya adalah **kontras skala yang sangat tajam**: teks judul masif dan berbobot dipadukan langsung dengan baris metadata mikroskopis.

### Pilihan Pasangan Font (*Typeface Pairings*)
- **Varian Neo-Grotesque (Swiss Modern):**
  - Display/Headline: *Inter Tight / Neue Haas Grotesk / Inter* (Black 900 atau ExtraBold 800).
  - Body: *Inter* (Regular 400 atau Medium 500, line-height 1.55–1.65×).
  - Metadata & Angka: *JetBrains Mono / Space Mono* (Medium 500, all-caps, tracking 0.15em).
- **Varian Editorial Luxury (High-Fashion / Intellectual Magazine):**
  - Display/Headline: *Newsreader / Playfair Display / Editorial New* (SemiBold 600 atau Bold 700 italic/upright, contrast tinggi).
  - Subhead/Body: *Inter* (Regular 400).
  - Metadata: *JetBrains Mono* (Tracking 0.18em).

### Skala Ukuran Font (Kanvas 1080 × 1350 px)
```
Cover Headline:    68 - 84px   Weight 800/900   Line-height 1.05 - 1.12×  Tracking -0.03em
Slide Subhead:     40 - 48px   Weight 700/800   Line-height 1.20×         Tracking -0.015em
Body Copy:         34 - 38px   Weight 400       Line-height 1.55 - 1.65×  Tracking normal
Micro-Metadata:    20 - 22px   Weight 600       Line-height 1.0×          Tracking 0.15 - 0.20em (ALL CAPS)
Pagination Pill:   18 - 20px   Weight 700       Mono                      Contoh: "01 / 04"
```

### Aturan Tipografi Anti-Slop
- **Tracking Ketat pada Judul:** Judul besar harus memiliki kerning rapat (*tight but not touching*) untuk menciptakan blok visual yang solid.
- **Micro-Copy Lebar:** Semua label penanda (kategori, tanggal, sumber) dibuat kecil (20px) dengan huruf kapital dan *letter-spacing* longgar (+0.15em).
- **Nol Badge Kicker:** Jangan pernah membungkus kategori berita ke dalam kotak pill berwarna neon. Kategori cukup berupa teks mikroskopis murni dengan separator tajam (`SAINS & TEKNOLOGI // EDISI 04`).

---

## 2. Palet Warna (*Disciplined Tri-Tone System*)

Desain editorial papan atas tidak memakai lebih dari 3 warna inti per komposisi.

### Varian A: Matte Obsidian (Gelap Editorial Mewah)
```
--bg-canvas:      #0D0E12    (Hitam arang matte, bukan hitam digital #000 atau navy neon)
--text-primary:   #F5F5F7    (Putih porselen hangat dengan kontras tinggi)
--text-secondary: #9E9EA8    (Abu-abu perak kalem untuk teks panjang)
--hairline:       rgba(255, 255, 255, 0.12)  (Garis pemisah ultra-tipis 1px)
--accent-red:     #D02424    (Merah editorial ceri/vermilion untuk aksen tunggal)
```

### Varian B: Warm Alabaster / Heritage Paper (Majalah Cetak Klasik)
```
--bg-canvas:      #F5F3ED    (Kertas majalah hangat bertekstur, bukan putih silau)
--text-primary:   #111215    (Tinta cetak obsidian pekat)
--text-secondary: #52535A    (Abu-abu arang untuk teks narasi)
--hairline:       rgba(17, 18, 21, 0.15)     (Garis pemisah tinta 1px)
--accent-red:     #B91C1C    (Merah carmine klasik)
```

---

## 3. Struktur Grid & Komposisi Ruang (*Swiss Modular Grid*)

### Safe Margin & Framing Fisik
- **Outer Margin:** 64px dari tepi kanvas (ruang aman jempol pengguna Instagram).
- **Hairline Framing:** Garis batas 1px tipis yang membingkai area kerja, memberikan sensasi sasis cetak fisik (*physical printed sheet*).

### Komposisi Slide per Peran (*Slide Anatomy*)

#### Slide 1: HOOK / COVER
- **Bagian Atas (680px):** Foto jurnalistik nyata, terpotong presisi tanpa gradien buram yang memudar ke warna latar.
- **Pemisah Garis Tipis:** 1px hairline horizontal di bawah foto.
- **Bagian Bawah:**
  - Baris metadata: `KATEGORI BERITA // TANGGAL` (20px, all-caps, tracking 0.15em).
  - Headline editorial masif: 2–3 baris, ekstra tebal, langsung ke substansi berita.

#### Slide 2 & 3: CONTEXT & NARRATIVE (Isi Berita)
- **Bukan kartu melayang:** Teks mengalir di dalam kolom majalah yang lapang (*broadsheet column*).
- **Struktur:**
  - Penanda bab tipis: `02 — KONTEKS PERISTIWA` (Mono, merah editorial atau putih muted).
  - Subhead penjelas tebal (42px, hitam/putih tegas).
  - Paragraf isi berita yang terstruktur: margin lega, spasi baris 1.6×, nyaman dibaca tanpa silau.
  - Garis aksen vertikal tipis (1.5px) di sisi kiri untuk memandu mata.

#### Slide 4: TAKEAWAY & CALL TO ACTION
- **Struktur:**
  - Penanda penutup: `04 — KESIMPULAN EDITORIAL`.
  - Teks rangkuman padat berukuran 44px dengan kutipan tajam.
  - Baris penutup CTA minimalis: Bukan tombol game berbayang, melainkan tautan editorial bergaris bawah tegas:
    `BACA DOKUMEN LENGKAP PADA JAJANDIGITAL.WEB.ID →`

---

## 4. Arsitektur Copywriting Mandiri (*The 98/100 Self-Contained Rule*)

Prinsip fundamental: **Carousel berita adalah media publikasi mandiri (Zero-Click Content), BUKAN funnel/alat pancing trafik web.**

### 4 Aturan Penulisan Mutlak:
1. **Tuntas & Mandiri (Self-Contained):** Pembaca harus memahami 100% fakta, konteks 5W+1H, dampak, dan kesimpulan langsung dari 4 slide tanpa perlu membuka rujukan luar.
2. **Nol Cliffhanger & Nol Elipsis:** Dilarang menggunakan kalimat menggantung, dilarang tanda elipsis (`...`), dan dilarang mengarahkan pembaca ke web untuk membaca kelanjutan berita.
3. **Format Poin Kunci Vertikal (Listicle 3 Poin):**
   - **Slide 2 (Konteks Peristiwa):** 3 poin fakta kunci `[ 01 ]`, `[ 02 ]`, `[ 03 ]`. Setiap poin memiliki judul tebal singkat (3–4 kata) diikuti deskripsi 1–2 baris yang padat.
   - **Slide 3 (Dampak & Signifikansi):** 3 poin implikasi nyata masa depan `[ 01 ]`, `[ 02 ]`, `[ 03 ]`.
   - Lencana nomor menggunakan kotak merah pekat (`#C5221F`) dengan angka putih tegas (`01`, `02`, `03`) sebagai *visual anchor*.
4. **CTA Retensi & Simpan:** Call-to-action di slide 4 diarahkan untuk konsumsi dan sirkulasi internal platform media sosial:
   `SIMPAN & BAGIKAN ARSIP RISET THE CHRONICLE` (dengan ikon bookmark, bukan link web).

---

## 5. Checklist Kualitas Anti-Slop (Pantangan Mutlak)

1. **Nol Pendaran Neon / Blur:** Tidak boleh ada `box-shadow: 0 0 30px #00D4FF` atau radial glow biru yang kabur.
2. **Nol Emoji:** Ikon hanya berupa vektor garis sederhana (panah tipis 1.5px SVG).
3. **Nol Teks Gradasi:** Teks harus 100% solid (putih, arang, atau merah aksen).
4. **Nol Kicker Badge Berlebihan:** Jangan gunakan wadah bulat warna-warni untuk teks metadata.
5. **Whitespace Percaya Diri:** Jika teks sudah selesai, biarkan sisa kanvas bernapas lega. Jangan isi kekosongan dengan dekorasi acak.
