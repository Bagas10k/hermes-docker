---
name: zero-layout-shift-artifacts
description: CLS-0 live sandbox rendering and viewport clamping.
version: 1.0.0
author: Bagas Cihuy, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [creative, ui-ux, sandbox, cls0, web-vitals, live-preview]
    related_skills: [live-sandbox-hot-preview, bento-grid-spatial-composer]
---

# Zero-Layout-Shift (CLS 0) Live Artifact Sandbox & Virtual Viewport Paging

Sistem sandboxing iframe mandiri dan streaming live-code preview dengan deterministik aspect ratio clamping, skeleton reservation, dan touch-safe virtual viewport paging untuk menjamin Cumulative Layout Shift (CLS) = 0.000.

## 1. Latar Belakang & Motivasi
Saat merender live artifact, grafik interaktif, atau bento visual di antarmuka web modern, pemuatan asinkron (kompilasi skrip, lazy-loading gambar, dan dynamic iframe rendering) kerap memicu lonjakan layout mendadak (*layout jumps*). Hal ini merusak pengalaman visual pengguna, melanggar batas Web Vitals, dan memicu ketidaknyamanan navigasi.

## 2. Sintesis Tiga Mindset Matematis
1. **Lensa Mekanistik-Kausal**:
   - Modelkan CLS:
     $$\text{CLS} = \text{Impact Fraction} \times \text{Distance Fraction} = \frac{\text{Area}(\text{Union})}{\text{Area}(\text{Viewport})} \times \frac{\max(\Delta x, \Delta y)}{\max(W_v, H_v)}$$
   - Kendala deterministik: Untuk menjamin $\text{CLS} = 0$, maka $\max(\Delta x, \Delta y)$ harus identik dengan $0$. Seluruh dimensi kanvas wadah wajib di-*clamp* secara statis sebelum DOM anak terisi (*skeleton pre-reservation*).
2. **Lensa Bayesian-Eksperimental**:
   - Verifikasi melalui kalkulasi deterministik: perubahan posisi elemen diuji apriori. Setiap komponen yang gagal mengunci `aspect-ratio` dan `contain-intrinsic-size` langsung ditolak pada tahap kompilasi wadah.
3. **Lensa Desain Sistem & Optimasi**:
   - Terapkan CSS containment level keras:
     `contain: paint layout style size; content-visibility: auto; transform: translateZ(0);`
   - Gunakan isolasi iframe `srcdoc` dengan batasan ketat CSP dan atribut sandbox untuk mencegah *style leak* atau *script escalation*.

## 3. Komponen Utama
- `scripts/zero_layout_shift.py`:
  - `ViewportSpec`: Spesifikasi dimensi, rasio aspek, dan safe-area.
  - `SkeletonReservation`: Alokasi ruang pra-render dengan penjepit min/max aspect ratio.
  - `LayoutShiftCalculator`: Pengukur deviasi pergeseran piksel CLS standar W3C.
  - `VirtualViewportManager`: Generator envelope wadah sandbox zero-shift dan kalkulasi virtual paging.
- `tests/test_zero_layout_shift.py`:
  - Pengujian unit deterministik 7/7 lulus (100% pass rate).

## 4. Cara Penggunaan
```python
from zero_layout_shift import ViewportSpec, SkeletonReservation, VirtualViewportManager

spec = ViewportSpec(width=1080.0, height=1920.0)
manager = VirtualViewportManager(spec)

res = SkeletonReservation(
    component_id="preview-canvas",
    min_width=400.0,
    min_height=300.0,
    aspect_ratio=16.0 / 9.0
)
manager.register_reservation(res)
html_sandbox = manager.generate_iframe_sandbox_html("preview-canvas", "<h1>Hello</h1>", 800.0)
```
