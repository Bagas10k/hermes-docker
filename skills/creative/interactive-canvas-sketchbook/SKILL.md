---
name: interactive-canvas-sketchbook
description: Creative 2D/WebGL canvas sketchbook with 60 FPS physics.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [creative-coding, canvas, vibe-coding, generative-art, interactive]
    related_skills: [p5js, genjutsu, tactile-microinteraction-studio]
---

# Interactive Canvas Sketchbook Skill

Prosedur penciptaan kanvas generatif dan visual taktil interaktif 60 FPS (Canvas 2D / WebGL) dalam satu berkas HTML mandiri (*single-file artifact*) yang langsung dapat dijalankan di browser untuk memicu *flow-state* dan visualisasi vibe koding.

## When to Use

- Membutuhkan visualisasi interaktif cepat (partikel, audio-reactive canvas, visual grafis, matematika visual, animasi generatif).
- Memvalidasi ide konsep visual sebelum diintegrasikan ke landing page atau dashboard publik.
- Menguji interaksi pointer, mouse trailing, physics spring, atau shader eksperimen tanpa overhead bundler (React/Vite).

Don't use for:
- Antarmuka dokumen teks statis biasa tanpa elemen canvas atau visualisasi matematika dinamis.
- Produksi aplikasi SPA enterprise penuh dengan routing multi-halaman.

## Prerequisites

- Browser modern (Chromium, Firefox, Safari) berkemampuan HTML5 Canvas 2D atau WebGL.
- Server lokal sederhana (misal `python3 -m http.server`) atau akses berkas langsung via `file://`.

## Quick Reference

| Kebutuhan | API Rekomendasi | Optimasi Performa |
|---|---|---|
| Partikel & Fisika 2D | `ctx.arc`, `ctx.fillRect` | Object pooling, loop mundur `splice` |
| Mouse / Touch Trailing | Pointer Events (`pointerdown`, `pointermove`) | Pointer capture, DPR scaling `devicePixelRatio` |
| Zero-Lag Loop | `requestAnimationFrame(loop)` | Delta timing `performance.now()`, tab blur pause |
| HUD Metrik Vibe | HTML overlay CSS `pointer-events: none` | Update textContent maksimal 2 Hz (500ms jeda) |

## Procedure

1. **Inisialisasi Kanvas & Resolusi High-DPI:**
   - Ambil konteks: `const ctx = canvas.getContext('2d', { alpha: false });`.
   - Kalibrasi Retina / High-DPI:
     ```javascript
     const dpr = window.devicePixelRatio || 1;
     canvas.width = rect.width * dpr;
     canvas.height = rect.height * dpr;
     ctx.scale(dpr, dpr);
     ```
2. **Setup State & Palet Warna Terkalibrasi:**
   - Gunakan palet cerah harmonis terstandar (Amber `#F59E0B`, Emerald `#10B981`, Cyan `#0EA5E9`, Violet `#8B5CF6`, Rose `#F43F5E`).
   - Latar belakang pekat Obsidian `#14120E` atau Warm Paper `#FAF6EF` untuk kontras tinggi tanpa halation.
3. **Loop Animasi Deterministik:**
   - Implementasikan peredam jejak cahaya (*motion blur trail*): `ctx.fillStyle = 'rgba(20, 18, 14, 0.2)'; ctx.fillRect(0,0,w,h);`.
   - Gunakan delta-time untuk fisika independen dari refresh rate layar (60Hz vs 120Hz).
4. **Interaksi Pointer Taktil:**
   - Pasang event listener `pointerdown`, `pointermove`, dan `pointerup`.
   - Hubungkan aksi burst partikel atau gaya gravitasi pegas ke koordinat pointer.
5. **HUD Diagnostik Ringkas:**
   - Sediakan indikator FPS dan jumlah objek di sudut kanvas untuk verifikasi instan integritas runtime.

## Pitfalls

1. **Alokasi Objek di Tiap Frame (`new Object` Loop Heap Bloat):**
   - Membuat ribuan objek partikel per frame di dalam `requestAnimationFrame` memicu siklus Garbage Collection (GC stutter) yang menjatuhkan framerate dari 60 FPS ke <30 FPS.
   - *Solusi:* Gunakan *object pooling* terikat kapasitas tetap (`maxParticles = 500`) dan daur ulang partikel mati.
2. **TextContent DOM Thrashing:**
   - Mengubah `element.textContent` untuk metrik FPS pada setiap frame (60 kali per detik) memicu browser layout recalibration.
   - *Solusi:* Hitung delta akumulasi dan perbarui teks DOM hanya setiap 500ms.
3. **Canvas Blur pada Layar Retina / 4K:**
   - Menyetel atribut `width` dan `height` kanvas hanya lewat CSS tanpa menyelaraskan atribut elemen kanvas terhadap `devicePixelRatio` menghasilkan teks dan garis buram.
4. **Memory Leak pada Tab Latar Belakang:**
   - Animasi yang terus menumpuk array partikel saat tab tidak aktif memboroskan RAM. Hentikan emisi saat `document.hidden === true`.

## Verification

Buktikan bahwa sasis kanvas berfungsi penuh:
1. Simpan berkas HTML mandiri dan buka via peramban (`file://` atau server lokal).
2. Periksa bahwa kanvas ter-render tanpa error di konsol DevTools.
3. Klik pada kanvas dan amati partikel meledak secara interaktif.
4. Pastikan metrik FPS stabil di angka 60 FPS (atau refresh monitor target) dan konsumsi CPU tetap rendah.
