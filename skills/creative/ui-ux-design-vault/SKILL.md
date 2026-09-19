---
name: ui-ux-design-vault
description: "Use when designing web UI components, buttons, and layouts."
version: 1.0.0
author: Hermes Agent + User
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ui, ux, design-system, components, buttons, cards, typography, tokens, oklch, styling]
---

# UI/UX Design System & Component Vault

Gunakan panduan ini sebagai repositori standar saat merancang antarmuka web, tombol, kartu, input, dan tata letak agar berkarakter kuat, presisi, dan bebas dari kebiasaan template AI generik (anti-slop).

## 1. Fondasi Arsitektur Permukaan (Surface Archetypes)
Sebelum menentukan warna atau font, kunci satu arketipe permukaan:
- **Operate / Console**: Densitas tinggi, glanceable, tabel instrumen, tombol aksi tegas (misal: Dasbor Finansial, Admin Sekolah, Workbench Token).
- **Monitor**: Status live, observabilitas, grafik visual, latensi rendah, visualizer audio/canvas.
- **Decide / Learn**: Editorial terkurasi, tipografi berkarakter kuat (Newsreader / Syne), rasio visual luas, storytelling bahan/produk.

## 2. Taksonomi 50 Gaya Tombol Teruji
Gunakan varian tombol yang sesuai dengan karakter produk:

### A. Minimalist & Precision Software (Dev Tools / SaaS)
- `btn-linear`: Achromatic ghost, border 1px rgba(255,255,255,0.08), bg transparan 0.03 -> hover 0.08.
- `btn-vercel-stark`: Kontras ekstrem hitam pekat/putih murni, font monospace, border tegas.
- `btn-raycast-pill`: Kapsul gelap dengan lambang hotkey keyboard (`↵`, `⌘K`).
- `btn-outline-minimal`: Hairline border 1px dengan pembalikan warna (*inverse hover*).
- `btn-arc-capsule`: Kapsul squircle semi-transparan dengan border pastel halus.

### B. High-Conversion & Fintech
- `btn-revolut-pill`: Radius 9999px, padding lebar (14px 32px), sans-serif tebal tanpa drop-shadow berlebihan.
- `btn-stripe-glow`: Ungu indigo (`#635bff`) dengan diffused soft shadow berjarak 14px.
- `btn-success-check`: Hijau zamrud (`#059669`) dengan ikon centang terintegrasi.
- `btn-danger-solid`: Merah rubi (`#dc2626`) dengan glow hover untuk aksi destruktif.

### C. Apple Frosted & Glassmorphism
- `btn-glass`: `backdrop-filter: blur(16px)`, border putih 0.25, inner-glow inset 0 1px 1px.
- `btn-glass-sunset`: Kaca frosted dengan semburat gradien hangat senja Web3.
- `btn-aurora-glow`: Latar void-black dengan diffused glow aurora hijau-ungu.

### D. Playful, Neo-Pop & Neo-Brutalist
- `btn-neo-brutal`: Border hitam tebal 2.5px, hard offset shadow 4px (tanpa blur), kuning lemon `#fde047`.
- `btn-clay-3d`: Bevel shadow bawah 6px timbul dengan efek push down `translateY(4px)` saat ditekan.
- `btn-paper-sticker`: Stiker kertas miring -2° dengan bayangan potongan tangan.
- `btn-pixel-arcade`: Border 3px solid hitam dengan bayangan stepped pixel tanpa anti-aliasing.

### E. Hardware, Studio & Mechanical
- `btn-cherry-switch`: Profil tombol keyboard mekanikal 3D nyata dengan kedalaman tekan.
- `btn-brushed-metal`: Gradien logam reflektif vertikal dengan inset highlight.
- `btn-toggle-lever`: Sakelar toggle analog hardware audio rekaman studio.
- `btn-beacon-pulse`: Tombol status live dengan titik merah berkedip animasi `beaconFlash`.

## 3. Bank Gaya Kartu (Card Archetypes)
- **Interactive Spotlight Card**: Lapisan `radial-gradient` yang mengikuti koordinat kursor mouse (`--mouse-x`, `--mouse-y`) secara dinamis.
- **Bento Metric Card**: Kompartemen modular padat dengan penekanan angka display tebal.
- **Warm Editorial Parchment**: Kertas krim hangat (`#fdfbf7`), batas karamel halus, dan tipografi serif untuk brand artisan/luxury.
- **Neo-Brutalist Chunky Card**: Frame garis hitam 2.5px dengan bayangan blok tanpa blur.
- **Dark Glassmorphism**: Latar `rgba(18,24,38,0.55)` dengan blur optik 14px.
- **3D Perspective Tilt**: Kartu yang berputar miring mengikuti koordinat mouse (*3D parallax tilt*).
- **Ticket Voucher Stub**: Kartu berbingkai dashed border dengan lubang sobekan tiket (*notch*) di kiri & kanan.

## 4. Standar Tipografi Berpasangan
- **Precision Software**: Inter Variable (`font-feature-settings: "cv01", "ss03"`) + Space Grotesk.
- **Luxury Editorial**: Newsreader (Serif Humanist) + Plus Jakarta Sans.
- **High-Impact Pop**: Syne 800 (Extra Bold) + Space Grotesk.
- **Finansial & Telemetri**: JetBrains Mono dengan `font-variant-numeric: tabular-nums` wajib aktif.

## 5. Standar Mode Gelap vs Terang
- Jangan hanya membalik warna hitam dan putih secara mentah.
- Pada mode terang: Tombol transparan wajib menggunakan tinta Slate pekat (`#0f172a`) dengan latar transparan terkalibrasi (`rgba(15, 23, 42, 0.04)`), bayangan neumorphic harus memiliki bayangan terang (`#ffffff`) dan bayangan gelap (`#d1d5db`).
- Pada mode gelap: Gunakan elevasi luminansi bertingkat (`rgba(255,255,255, 0.03 -> 0.08)`), bukan bayangan hitam pekat.
