---
name: spatial-canvas-ui-physics
description: "Compose 3D spatial canvas and UI card spring physics."
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [spatial-physics, canvas-2d, spring-dynamics, tactile-ui, living-interfaces]
    related_skills: [bento-grid-spatial-composer, tactile-microinteraction-studio, dynamic-canvas-backdrop]
---

# Spatial Canvas UI Physics Skill

Engine perancangan antarmuka hidup (*living interfaces*) berbasis kanvas spasial 2D 60 FPS, kinematika pegas teredam multi-body (*damped spring physics*), dan kartu 3D reaktif kursor dengan efisiensi CPU terkendali.

## When to Use

- Membangun antarmuka landing page, dashboard hero, atau showcase visual dengan efek kedalaman taktil 3D.
- Menghadirkan dinamika latar belakang hidup tanpa membebani GPU/CPU (<1ms per frame compute, auto-sleep idle 45 detik).
- Mengintegrasikan interaksi tilt kursor halus pada kartu atau elemen DOM tanpa memicu getaran osilasi (*hunting jitter*).
- Menjamin kepatuhan aksesibilitas WCAG 2.1 AA dan eliminasi anti-pattern desain generik AI.

Don't use for:
- Antarmuka dokumen statis atau cetak yang tidak memerlukan interaksi pointer dinamis.
- Render 3D masif multi-megabyte berbasis WebGL shader berat yang melanggar batas daya perangkat mobile.

## Prerequisites

- Tidak memerlukan dependensi biner eksternal untuk runtime dasar (menggunakan Canvas 2D murni dan CSS 3D Transforms).
- Browser modern dengan dukungan HTML5 Canvas dan CSS Custom Properties.

## Quick Reference

- **Kanvas Partikel Eulerian**:
  Partikel melayang dengan redaman gesekan viskos $v_{t+1} = v_t 	imes 0.99$ dan pemulihan batas tepi melingkar (*toroidal wrapping*).
- **Kinematika Sudut Kartu 3D**:
  Membatasi deviasi sudut rotasi maksimal $7^\circ$ berbasis koordinat pointer ternormalisasi $(-1 \le x, y \le 1)$:
  `rotateX(-dy * 7deg) rotateY(dx * 7deg) translateZ(8px)`.
- **Auto-Sleep State Sentinel**:
  Menghentikan requestAnimationFrame jika tidak ada interaksi kursor selama $>45$ detik untuk menjamin 0% konsumsi CPU latar belakang.
- **Prefers-Reduced-Motion**:
  Wajib menonaktifkan transform dan transisi ketika pengguna mengaktifkan mode reduced motion.

## Procedure

1. **Kanvas Latar Belakang Tetap**:
   Inisialisasi kanvas fixed layar penuh berindeks tumpukan `z-index: 0` dengan `pointer-events: none` agar tidak menghalangi klik antarmuka.
2. **Skalasi Device Pixel Ratio (DPR)**:
   Kalibrasi ukuran buffer kanvas terhadap `window.devicePixelRatio` untuk ketajaman visual di layar retina.
3. **Loop Animasi Terikat Anggaran (<16.6ms)**:
   Batasi jumlah partikel ($16 - 128$) agar komputasi per-frame konsisten di bawah 1.0ms.
4. **Interaksi Taktil Kartu Reaktif**:
   Terapkan pendengar event `pointermove` pada elemen kartu untuk menghitung sudut perspektif 3D yang mulus.
5. **Verifikasi Aksesibilitas**:
   Uji halaman dengan Axe-Core untuk memastikan rasio kontras warna dan struktur heading memenuhi standar WCAG AA.

## Pitfalls

- **Jitter Osilasi Hover**: Memaksa reset sudut miring secara mendadak saat kartu di-hover dapat memicu siklus getaran tanpa akhir. Gunakan redaman easing `cubic-bezier(0.2, 0.8, 0.2, 1)`.
- **Kebocoran Daya Latar Belakang**: Jangan biarkan loop kanvas terus berputar ketika tab tidak aktif atau pengguna meninggalkan layar. Pasang deteksi inaktivitas 45 detik.
- **Horizontal Overflow di Mobile**: Pastikan kartu dan grid menggunakan `minmax(min(100%, 240px), 1fr)` agar tidak memicu overflow di layar sempit 320px.

## Verification

Buktikan keberhasilan implementasi melalui:
1. Pengujian Playwright di 7 ukuran viewport (320px, 390px, 640px, 768px, 1000px, 1024px, 1440px) dengan `scrollWidth === innerWidth` (nol horizontal overflow).
2. Audit Axe-Core menghasilkan 0 pelanggaran aksesibilitas WCAG 2.1 AA.
3. Pemeriksaan Impeccable menghasilkan 0 anti-pattern desain.
