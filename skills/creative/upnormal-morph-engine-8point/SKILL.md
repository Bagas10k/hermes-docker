---
name: upnormal-morph-engine-8point
description: Use when building 60 FPS in-place morphing UIs.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [morphing, 60fps, upnormal, spring-physics, flip, web-animations]
---

# Upnormal Morph Engine (8-Point Mandate)

Standar baku penerapan animasi morphing 60 FPS in-place (Target +8 Poin) untuk antarmuka Upnormal tanpa kedip (CLS = 0, No-Blink SPA).

## 8 Poin Peningkatan Mesin Morphing

1. **In-Place FLIP Bounding Box Math (Zero Teleport/Jump)**:
   - Hitung selisih koordinat First vs Last:
     `deltaX = first.left - last.left`, `deltaY = first.top - last.top`, `scaleX = first.width / last.width`, `scaleY = first.height / last.height`.
   - Mengembang langsung dari posisi fisik trigger tanpa jeda lompat.

2. **Continuous Curvature Squircle Morphing**:
   - Transisi kurva lengkung superellipse dari radius tombol asal (8px/24px/pill) menjadi radius modal (16px/24px) selama 60 FPS flight.

3. **Two-Phase Content Stagger & Silhouette Protection**:
   - Cangkang luar bermetamorfosis terlebih dahulu ($t: 0 \to 1.0$), sementara teks dan kontrol di-reveal tertunda pada $t > 0.35$ (`opacity: 0 \to 1`, `translateY: 12px \to 0`).
   - Mencegah distorsi teks dan layout thrashing.

4. **Universal Vector Icon Morphing**:
   - Ikon pemicu (plus ke silang ✕, chevron ke centang, hamburger ke close) melebur mulus 60 FPS menggunakan transisi rotasi-skala aman via `DOMParser` + `replaceChildren` (anti-XSS).

5. **Liquid Gooey & Necking Bridge Option**:
   - Filter SVG `<filter id="up-liquid-filter">` (`feGaussianBlur` + `feColorMatrix`) untuk opsi peleburan cairan elastis pada Layer 0 siluet, menjaga tipografi Layer 10 tetap 100% pixel-sharp.

6. **Calibrated Spring Physics & Critically Damped Inertia**:
   - Persamaan diferensial osilator harmonik teredam: $m x''(t) + c x'(t) + k x(t) = 0$.
   - Damping ratio $\zeta = \frac{c}{2\sqrt{km}}$, natural frequency $\omega_0 = \sqrt{\frac{k}{m}}$.
   - 4 Profil Fisika Empuk di Mata:
     - `tactile_smooth` ($\zeta = 0.88, \omega_0 = 18.0$): `cubic-bezier(0.16, 1, 0.3, 1)`, durasi 420ms (Apple/Linear feel, paling nyaman di mata).
     - `playful_bounce` ($\zeta = 0.72, \omega_0 = 22.0$): `cubic-bezier(0.34, 1.4, 0.64, 1)`, durasi 480ms (rebound kenyal terkendali).
     - `viscous_liquid` ($\zeta = 0.98, \omega_0 = 14.0$): `cubic-bezier(0.2, 0.9, 0.1, 1)`, durasi 520ms (cairan fluida elastis).
     - `critically_damped` ($\zeta = 1.00, \omega_0 = 24.0$): `cubic-bezier(0.08, 0.82, 0.17, 1)`, durasi 360ms (zero-overshoot executive HUD).
   - Ambang batas *dead-zone* ($< 0.001$) untuk menghentikan style writes seketika (anti-jitter).

7. **WCAG AAA Accessible Reduced Motion & Focus Trapping**:
   - Deteksi `prefers-reduced-motion: reduce`: langsung beralih ke transisi crossfade instan (0ms).
   - Fokus keyboard otomatis dikunci di dalam dialog dan dikembalikan dengan tepat ke trigger asal saat ditutup.

8. **4-Layer Progressive Frosted Glass & Anti-White Flash Backdrop**:
   - Backdrop blur bertingkat (`backdrop-filter: blur(16px)` + dark tint) dengan proteksi kanvas putih sistem operasi pada mode gelap.

---

## Doktrin Spasial Upnormal Kreatif (Padding & Margin Rhythm)

1. **Fluid Responsive Spacing Clamp**:
   - Menggunakan formula matematis linier tanpa jeda breakpoint kaku:
     `clamp(min_rem, slope * 100vw + intercept, max_rem)`.
   - Contoh token fluida:
     - Section Vertical Padding: `clamp(3.0rem, 7.191vw + 1.245rem, 7.0rem)` (48px mobile ➔ 112px desktop).
     - Page Lateral Padding: `clamp(1.0rem, 3.596vw + 0.124rem, 3.0rem)` (16px mobile ➔ 48px desktop).
     - Card Internal Padding: `clamp(1.25rem, 1.798vw + 0.812rem, 2.25rem)` (20px mobile ➔ 36px desktop).

2. **Asymmetric Editorial Rhythm (Anti-Bento Simetris Monoton)**:
   - Menerapkan rasio Golden Ratio ($1 : 1.618$) atau Bobot Ganda ($2 : 1$) antara sel utama vs pendukung.
   - Ruang bernafas makro (64px - 128px) untuk menopang tipografi display berbobot ekstrim.

3. **Touch Target Comfort & Bottom Dock Clearance**:
   - Seluruh target interaktif minimal 44px x 44px (WCAG AAA) dengan padding adaptif `py-2.5 px-5` / `py-3 px-6`.
   - Bottom Clearance Invariant: selalu berikan `padding-bottom: calc(var(--dock-height) + 48px)` dan `env(safe-area-inset-bottom)` agar konten bawah tidak terpotong dock melayang atau keyboard ponsel.

