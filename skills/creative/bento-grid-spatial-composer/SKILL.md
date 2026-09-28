---
name: bento-grid-spatial-composer
description: "Compose tactile bento grids with spatial CSS math."
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bento-grid, spatial-design, css-grid, tactile-ui, visual-rhythm, enterprise-ui]
    related_skills: [enterprise-ui-architecture, ui-ux-design-vault, popular-web-designs]
---

# Bento Grid Spatial Composer Skill

Engine perancangan tata letak bento grid responsif berbasis hierarki visual deterministik, matematika rasio aspek modular, dan mikrointeraksi taktil tanpa ketergantungan framework berat.

## When to Use

- Merancang antarmuka dashboard, showcase portofolio, atau landing page produk modular dengan kepadatan informasi tinggi.
- Membagi ruang visual dengan variasi ukuran kartu (1x1, 2x1, 1x2, 2x2, 3x1) tanpa layout drift atau ruang kosong (whitespace imbalance).
- Membutuhkan sistem bento grid yang beradaptasi mulus dari 1 kolom (mobile), 2-3 kolom (tablet), hingga 4-6 kolom (desktop).
- **Don't use for:** Tabel data tabular berulang seragam (gunakan DataGrid biasa), form input transaksi linear, atau layout dokumen artikel teks murni.

## Prerequisites

- Browser modern dengan dukungan CSS Grid (`grid-template-columns: repeat(...)`, `grid-column: span ...`, `subgrid`, `container-queries`).
- Node.js atau vanilla HTML/CSS canvas. Tidak membutuhkan pustaka UI eksternal.

## Quick Reference

- **Grid Base Matrix Desktop (12 Kolom Sub-unit atau 4 Kolom Modul):**
  - Kotak Standard (1x1): `col-span-1 row-span-1` (rasio aspek 1:1 atau 4:3).
  - Kartu Lebar (2x1): `col-span-2 row-span-1` (fitur utama, grafik horizontal, metrik primer).
  - Menara Vertikal (1x2): `col-span-1 row-span-2` (feed riwayat, daftar status sistem, telemetri real-time).
  - Kartu Unggulan Hero (2x2): `col-span-2 row-span-2` (visual 3D, canvas interaktif, produk centerpiece).
  - Pita Horisontal Penuh (4x1 atau 3x1): `col-span-full` (ticker status, omnibar pencarian, audit telemetri).
- **Pola CSS Grid Baku:**
  ```css
  .bento-container {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    grid-auto-rows: 240px;
    gap: 16px;
  }
  @media (max-width: 1024px) {
    .bento-container {
      grid-template-columns: repeat(2, minmax(0, 1fr));
      grid-auto-rows: 220px;
    }
  }
  @media (max-width: 640px) {
    .bento-container {
      grid-template-columns: 1fr;
      grid-auto-rows: auto;
    }
  }
  ```

## Procedure

1. **Definisikan Matriks Densitas & Komposisi Bobot Visual:**
   - Petakan hierarki data ke dalam 3 tier:
     - Tier 1 (Hero / Centerpiece): 1 item (bobot 40% area, ukuran 2x2).
     - Tier 2 (Metrik Utama / Visual Aktif): 2-3 item (ukuran 2x1 atau 1x2).
     - Tier 3 (Micro-metric / Kontrol Taktil): 2-4 item (ukuran 1x1).
   - Pastikan total luas kartu memenuhi kuota grid tanpa celah kosong (`dense packing` via `grid-auto-flow: dense` jika modular dinamis).

2. **Terapkan Sasis Taktil & Depth Elevation:**
   - Gunakan border radius terukur: `border-radius: 16px` (kartu luar) dan `border-radius: 10px` (elemen inset dalam).
   - Terapkan inner highlight dan kontras WCAG AA:
     ```css
     .bento-card {
       background: #FFFFFF;
       border: 1px solid rgba(15, 23, 42, 0.08);
       box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.04), 0 1px 3px rgba(15, 23, 42, 0.02);
       position: relative;
       overflow: hidden;
       transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s cubic-bezier(0.16, 1, 0.3, 1);
     }
     .bento-card:hover {
       transform: translateY(-2px);
       box-shadow: 0 12px 30px -4px rgba(15, 23, 42, 0.08);
     }
     ```

3. **Injeksi Spot-Color Harmonis & Zero-Emoji Policy:**
   - Berikan aksen fungsional pada header atau visual internal kartu (Amber `#F59E0B`, Emerald `#10B981`, Cyan `#0EA5E9`, Violet `#8B5CF6`).
   - Gunakan 100% SVG line icons presisi (stroke 2.0-2.4px). Tolak karakter emoji unicode.

4. **Verifikasi Responsivitas & Aspect Ratio Collapse:**
   - Pastikan di layar mobile kartu 1x2 atau 2x2 tidak mempertahankan tinggi kaku ribuan piksel. Kolaps ke tinggi proporsional (`min-height: 200px; height: auto;`).

## Pitfalls

- **Bento Kitsch / Candy Overdose:** Mengisi setiap kartu dengan warna latar gradasi neon berbeda-beda. Bento grid profesional menggunakan kanvas kartu netral seragam (putih bersih atau arang obsidian) dan hanya menonjolkan konten/grafik internalnya.
- **Fixed Height Content Clipping:** Menentukan `height: 240px` kaku pada kartu yang memuat teks dinamis. Gunakan `min-height` dan `overflow-hidden` dengan strategi layout fleksibel agar teks tidak terpotong.
- **Span Collapse Collision:** Menyetel `col-span-2` di mobile 1 kolom tanpa media query akan menyebabkan grid overflow atau layout berantakan. Pastikan selalu me-reset `col-span-1 row-span-1` pada breakpoint mobile.

## Verification

- Jalankan pengujian visual pada resolusi 1440px (desktop), 768px (tablet), dan 375px (mobile).
- Pastikan `scrollWidth <= clientWidth` tanpa menyembunyikan overflow root. `overflow-x:hidden` bukan bukti layout benar.
- Ikuti kontrak browser dan koreksi terbaru di [responsive-shell-evidence.md](references/responsive-shell-evidence.md); kontrak ini menggantikan saran dense packing, fixed-height clipping, dan pemeriksaan geometris saja di atas.
- Verifikasi kontras teks terhadap kartu memenuhi rasio kontras 4.5:1 (WCAG AA).
