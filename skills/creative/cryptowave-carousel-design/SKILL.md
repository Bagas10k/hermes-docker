---
name: cryptowave-carousel-design
title: CryptoWave Carousel Design System
description: "Use when designing dark-mode carousel slides."
author: Bagas Cihuy
version: 1.0
tags: [carousel, instagram, design-system, crypto, dark-mode, fintech]
---

# CryptoWave Carousel Design System

Diekstrak dari analisis visual 9 postingan carousel @cryptowaveid (Juli–Sep 2026, 650K followers).

## Design DNA

**Genre**: Dark Futuristic Crypto — cyberpunk neon + fintech dashboard + editorial infographic.

**Prinsip**:
- Dark-mode first, high-contrast
- Neon glow sebagai bahasa visual utama
- Hierarchy via ukuran + berat + warna
- Mobile-first (generous margins)
- Atmospheric depth (bukan flat)

---

## Color Palette

```
--bg-primary:      #0A0E27    deep navy (bukan pure black)
--bg-card:         #111128    panel semi-transparan
--accent-primary:  #00D4FF    electric cyan (SIGNATURE)
--accent-secondary:#7B2FFF    purple (hanya di gradient blend)
--accent-warm:     #F0C050    gold/amber (hook emosional saja)
--text-primary:    #FFFFFF
--text-secondary:  #B0BEC5    light gray muted
--text-accent:     #00D4FF    keyword highlight
--red:             #FF3B3B    indikator negatif
--green:           #00C853    indikator positif
```

**Aturan**: Cyan muncul di SETIAP slide min 1×. Purple tidak pernah standalone. Gold khusus hook emosional.

---

## Typography (dalam 1080×1350)

**Font**: Poppins/Montserrat (geometric sans-serif).

```
Slide Title:   56-72px  ExtraBold  white  ALL CAPS
Section Head:  36-44px  Bold       white
Subhead/Label: 28-32px  SemiBold   cyan   UPPERCASE
Body Text:     32-40px  Regular    light gray  line-height 1.4-1.6×
Caption:       22-26px  Regular    muted gray
Brand Handle:  20-22px  Medium     white 60% opacity
```

**Rules**: Max 3 level hierarki per slide. Body min 32px (readability mobile). Keyword di body = bold + cyan.

---

## Layout

**Format**: 1080 × 1350px (4:5 portrait). Safe zone: 60px padding semua sisi. Grid: 8px.

```
┌────────────────────────────────┐
│  HEADER (80px)    Brand + ##   │
│  ┌──────────────────────────┐  │
│  │                          │  │
│  │  CONTENT ZONE (1070px)   │  │
│  │  centered vertically     │  │
│  │                          │  │
│  └──────────────────────────┘  │
│  FOOTER (70px)   Source + CTA  │
└────────────────────────────────┘
```

**Spacing**: 8/16/24/32/60px (small/medium/large/xlarge/margin).

---

## Visual Effects

### Neon Glow (efek paling khas)
- Sumber: di belakang elemen utama
- Cyan blur 80-120px, opacity 30-50%
- Secondary purple glow di corner berlawanan, blur 100px, opacity 20%

### 3D Elements
- Kubus isometrik transparan (blockchain)
- Koin metalik mengambang
- Selalu dekorasi, bukan pengganti teks

### Particle/Bokeh
- 10-20 titik bercahaya per slide
- Ukuran 2-6px, opacity 20-40%

### Glass Morphism (card/panel)
- bg: rgba(17,17,40,0.7)
- backdrop-blur: 10-20px
- border: 1px solid rgba(0,212,255,0.15)
- radius: 16-20px

---

## Slide Roles

### Slide 1: HOOK
Stop the scroll. Dipahami < 1 detik.
- **Pola A**: Pertanyaan provokatif + foto emosional + gold palette
- **Pola B**: Angka besar dramatis ($120K) + mega cyan glow
- Max 8 kata. Typography 72px+.

### Slide 2-N: CONTENT
- **Numbered List**: Circle badge cyan + judul bold + deskripsi gray. Max 3 poin/slide.
- **Concept Explain**: Subhead cyan uppercase + judul putih bold + body gray + ilustrasi 3D.
- **Data Dashboard**: Card grid + crypto logos + harga + % color-coded + gauge meter.

### Slide Akhir: CTA
- "Follow / Save / Share" centered, medium size, brand prominent.

---

## Brand Rules

1. Handle selalu visible, kecil, opacity 60-80%
2. Cyan #00D4FF muncul di setiap slide
3. Background SELALU dark navy
4. Tone: edukatif, bukan hype. Indonesia + istilah EN.
5. Template structure konsisten antar post

---

## Adaptasi Non-Crypto

Substitusi accent color + ilustrasi tematik + domain terms. Yang HARUS dipertahankan:
- Dark canvas + neon glow depth
- 60px safe zone
- 3 level tipografi max
- Hook→Content→CTA sequence
- Single accent color consistency

---

## Lessons

- Hook = max 8 kata atau 1 angka besar, < 1 detik comprehension.
- Content = max 3 poin per slide. Jangan compress.
- Glow effect max 1-2 sumber per slide. Lebih = murahan.
- Body text min 32px di 1080px width. Di bawah itu sulit dibaca mobile.
- Konsistensi template > kreativitas per-slide.
- Foto emosional di hook > pure typography untuk engagement.
- Bilingual (ID + EN terms) efektif untuk konten edukatif Indonesia.
