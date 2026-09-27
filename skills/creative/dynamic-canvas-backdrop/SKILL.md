---
name: dynamic-canvas-backdrop
description: "Render reactive WebGL ambient backdrops for vibe coding."
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ambient-backdrop, webgl, canvas-2d, reactive-lighting, vibe-coding, flow-state]
    related_skills: [fluid-interactive-surface, harmonic-palette-studio, popular-web-designs]
---

# Dynamic Canvas Backdrop Skill

Sistem rendering kanvas latar belakang ambient prosedural 60 FPS reaktif kursor dan ketikan keyboard, dilengkapi auto-sleep GPU (0% CPU/GPU saat idle), isolasi pointer gestures tanpa scroll leak, dan kalibrasi palet harmonis cerah anti-silau.

## When to Use

- Membangun antarmuka vibe coding, visual workspace, atau landing page dengan latar belakang hidup yang merespons ketikan kode dan pergerakan pointer.
- Mencegah latar belakang statis kaku tanpa mengorbankan performa render (mempertahankan 60 FPS pada layar resolusi tinggi).
- Menghadirkan efek ambient luminous glow (orbs triad Amber `#F59E0B`, Cyan `#0EA5E9`, dan Violet `#8B5CF6`) yang terisolasi di belakang DOM konten tanpa mengganggu seleksi teks atau klik tombol.
- **Don't use for:** Simulasi fluida Eulerian presisi fisik tinggi (gunakan `fluid-interactive-surface`), visualisasi data grafik formal/bisnis statis, atau dashboard server berbasis teks konsol murni.

## Prerequisites

- Browser modern dengan dukungan HTML5 Canvas 2D atau WebGL 1.0/2.0.
- Zero-dependency: Berjalan murni dengan vanilla JavaScript dan CSS standard.

## Quick Reference

- **Sasis Penempatan Kanvas DOM (Z-Index Negatif & Pointer Events None):**
  ```css
  #backdrop-canvas {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 0;
    pointer-events: none; /* Mencegah intersepsi klik dan scroll leak */
    opacity: 0.85;
  }
  .app-content {
    position: relative;
    z-index: 1; /* Konten interaktif selalu di atas kanvas */
  }
  ```
- **Inisialisasi Cepat Reaktif Ketikan (Flow State Boost):**
  ```javascript
  import { initDynamicBackdrop } from './backdrop.js';
  const backdrop = initDynamicBackdrop(document.getElementById('backdrop-canvas'), {
    palette: ['#F59E0B', '#0EA5E9', '#8B5CF6'],
    autoSleepSeconds: 45
  });
  window.addEventListener('keydown', () => backdrop.pulse(0.2));
  ```

## Procedure

1. **Inisialisasi Kanvas dengan Skala Resolusi DPR (Device Pixel Ratio):**
   - Batasi DPR maksimum ke `Math.min(window.devicePixelRatio || 1, 2)` untuk mencegah ledakan komputasi pada layar Retina/4K.
   - Setel ukuran buffer fisik `canvas.width = rect.width * dpr` dan skala konteks `ctx.scale(dpr, dpr)` agar grafis tajam tanpa beban piksel berlebih.

2. **Pemetaan Lapisan Sumber Cahaya Ambient (Orbs / Shader Fields):**
   - Tetapkan 3-4 titik cahaya mengambang (*ambient luminous orbs*) dengan fungsi osilasi harmonis:
     $$x_i(t) = x_{0,i} + A_x \sin(\omega_{x,i} t + \phi_i)$$
     $$y_i(t) = y_{0,i} + A_y \cos(\omega_{y,i} t + \phi_i)$$
   - Padukan pergeseran lerp (*linear interpolation*) ke arah kursor mouse:
     $$x_{\text{target}} = x(t) + (x_{\text{mouse}} - x(t)) \cdot k_{\text{follow}}$$

3. **Injeksi Energi Ketikan (Typing Energy Surge):**
   - Setiap event `keydown` memicu injeksi energi $\Delta E = 0.15 \sim 0.25$ ke dalam accumulator energi global ($E \le 1.0$).
   - Energi mendilatasikan radius bola cahaya ($R_i = R_{0,i} \cdot (1 + 0.35 E)$) dan meningkatkan saturasi pendaran secara proporsional.
   - Lakukan decay eksponensial halus pada setiap frame: $E_{t+1} = E_t \cdot 0.94$.

4. **Siklus Auto-Sleep Konservasi Daya (Zero-CPU Idle Guard):**
   - Pasang pelacak waktu aktivitas terakhir `lastActiveTimestamp`.
   - Jika tidak ada gerakan mouse atau input ketikan selama lebih dari 45 detik dan energi telah luruh ($E < 0.005$), hentikan siklus `requestAnimationFrame`.
   - Bangunkan kembali siklus render secara instan ketika event `pointermove`, `keydown`, atau `focus` terdeteksi.

## Pitfalls

- **Scroll & Gesture Leak Trap:** Jika kanvas latar belakang tidak memiliki `pointer-events: none;`, event sentuh (touch swipe) pada perangkat mobile atau scroll mouse dapat tertahan oleh kanvas, melumpuhkan interaksi scrolling pengguna.
- **Retina Display GPU Choke:** Merender kanvas ukuran penuh pada monitor 4K/5K dengan DPR asli (3.0x atau 4.0x) membakar jutaan fragment shader per frame. Wajib membatasi DPR maksimum ke 2.0x atau merender pada resolusi 0.5x dengan upscaling filter CSS `image-rendering: auto`.
- **Background Tab CPU Drain:** Lupa mematikan animasi saat tab peramban berada di latar belakang (`document.hidden`). Wajib pasang event listener `visibilitychange` untuk menjeda loop seketika.

## Verification

- Kanvas terpasang di latar belakang dengan `z-index: 0` dan `pointer-events: none`, membiarkan teks dan tombol di atasnya dapat diseleksi/diklik bebas.
- Framerate stabil pada 60 FPS saat pergerakan mouse dan pengetikan teks intensif.
- Konsumsi CPU turun ke 0% saat idle selama >45 detik (auto-sleep aktif terverifikasi).
