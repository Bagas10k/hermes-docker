---
name: content-intelligence
description: "Content Learning Loop: analyze, decompose, and optimize content."
version: 1.0.0
author: Bagas Cihuy, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [content-intelligence, analytics, content-learning-loop, instagram, tiktok, performance-audit]
    related_skills: [news-editorial-copywriting, design-reference-interpreter, otak-koding]
---

# Content Intelligence — The Content Learning Loop

## Overview
Transformasi pembuatan konten dari sekadar *generate & post* menjadi **sistem pembelajaran performa berkelanjutan (Content Learning Loop)**. Setiap postingan diperlakukan sebagai eksperimen terkontrol berbasis Content DNA, observasi corong funnel, perbandingan median baseline, dan ekstraksi pola (*Pattern & Failure Library*).

## When to Use
- Merencanakan ide atau sudut pandang (*angle*) konten baru (Carousel, Video/Reels, Foto).
- Mengevaluasi metrik performa pasca-publikasi di Instagram atau TikTok.
- Membedah penyebab drop-off audiens pada retention slide atau watch time video.
- Merumuskan rekomendasi strategi konten mingguan/bulanan berbasis data empiris.

---

## 1. Siklus Kognitif Konten (Content Learning Loop)

```text
IDEA ➔ CONTENT DNA ➔ PUBLISH ➔ OBSERVE ➔ COMPARE ➔ DIAGNOSE ➔ LEARN ➔ EXPERIMENT ➔ REPEAT
```

Setiap tugas pembuatan dan evaluasi konten wajib mengikuti 6 disiplin:
1. **OBSERVE**: Ambil data performa riil (Reach, Impressions, Retention, Saves, Shares, Profile Visits, Follows).
2. **DECOMPOSE**: Bedah struktur DNA: Hook, Angle, Format, Visual, Tone, Structure, CTA, Slide Count/Duration.
3. **COMPARE**: Bandingkan terhadap **median baseline akun sendiri** (dari 30 post terakhir) pada format dan audiens yang sama.
4. **DIAGNOSE**: Lacak anomali pada corong:
   - *Attention lemah:* Masalah pada Hook, Headline, Thumbnail, atau Opening Visual.
   - *Consumption drop:* Pacing lambat, informasi terlalu padat, atau value terlambat.
   - *Save/Share rendah:* Kurang nilai utilitas atau gagal menyentuh identitas audiens.
   - *Action rendah:* CTA tidak relevan atau penempatan payoff tidak memuaskan.
5. **LEARN**: Simpan pola berhasil ke *Pattern Library* dan kegagalan ke *Failure Library* dengan skor keyakinan (*Low/Med/High*).
6. **EXPERIMENT**: Rancang uji komparasi berikutnya dengan mengubah **hanya satu variabel**.

---

## 2. Struktur Spesifikasi Content DNA

Sebelum konten dirakit kodenya atau dipublikasikan, deklarasikan DNA-nya:

```yaml
content_id: [ID-KONTEN]
platform: instagram | tiktok
format: carousel | video | photo
objective: education | awareness | community | conversion
audience: [segmen audiens spesifik]
topic:
  category: [kategori besar]
  subtopic: [sub-topik terarah]
angle:
  type: problem_solution | mistake | comparison | case_study | how_to
  description: [1 kalimat sudut pandang unik]
hook:
  type: problem_based | question | contrarian | curiosity | result
  text: [Teks headline pembuka]
structure:
  - hook
  - problem
  - framework
  - example
  - cta
visual:
  style: minimal | dense | bento | photographic
  theme: dark | warm_paper | monochrome
  dominant_element: diagram | portrait | screenshot | text
tone: [educational, direct, technical, conversational]
cta:
  type: save | share | comment | follow | link
  text: [Kalimat ajakan bertindak]
```

---

## 3. Disiplin Metrik & Normalisasi

- **Gunakan Nilai Median:** Hindari rata-rata (mean) yang terdistorsi oleh satu postingan viral ekstrem.
- **Bandingkan Rasio:**
  - `Save Rate = Saves / Reach`
  - `Share Rate = Shares / Reach`
  - `Profile Visit Rate = Profile Visits / Reach`
  - `Follow Conversion = Follows / Profile Visits`
- **Jendela Usia yang Setara:** Bandingkan performa pada usia yang sama (24 jam vs 24 jam, 7 hari vs 7 hari).

---

## 4. Format Laporan Analisis Konten (Output Template)

```markdown
# Analisis Pembelajaran Konten: [Judul Konten]

## 1. Content DNA & Konteks
- Format: [Carousel / Video / Foto] | Platform: [IG / TikTok]
- Hook Type: [Problem / Question / Contrarian]
- CTA: [Save / Share / Follow]

## 2. Metrik vs Median Baseline Akun
- Reach: [Nilai] (vs Median: [Nilai], Delta: [+X% / -Y%])
- Save Rate: [Nilai%] (vs Baseline: [Nilai%])
- Share Rate: [Nilai%] (vs Baseline: [Nilai%])
- Retention / Drop Point: [Slide/Detik ke-X]

## 3. Diagnosa Funnel & Kausalitas
- Titik Keberhasilan: [Komponen DNA yang paling berkontribusi]
- Titik Kegagalan: [Letak gesekan audiens]
- Faktor Pengganggu (Confounding): [Waktu upload, tren eksternal, format audio]

## 4. Pelajaran & Hipotesis Eksperimen Baru
- Pola Tersimpan: [Pattern Baru / Update Failure Library]
- Status Keyakinan: [Low / Medium / High]
- Rencana Uji Berikutnya: [1 Variabel uji terkontrol untuk konten depan]
```
