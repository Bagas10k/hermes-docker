---
name: adaptive-streaming-typography
description: Adaptive streaming typography and smooth token visual flow.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [typography, streaming, tokens, visual-flow, anti-reflow, layout-shift]
    related_skills: [typography-ux-copy, kinetic-typography-glitch]
---

# Adaptive Streaming Typography & Smooth Token Visual Flow

Skill ini mengelola rendering token stream LLM waktu nyata dengan interpolasi opacity bezier halus, dynamic font-weight shifting, pencegahan jarring word reflow, dan baseline clamp untuk mencegah Cumulative Layout Shift (CLS).

## When to Use
- Mengimplementasikan streaming response UI untuk LLM chat atau visual cockpit.
- Menghilangkan efek kedip kaku (jarring word snap/pop-in) saat token datang berkecepatan tinggi.
- Mengamankan metrik CLS (< 0.01) pada tampilan typography responsif.

## How to Run
Gunakan modul buffer penyeimbang token di:
`~/.hermes/skills/creative/adaptive-streaming-typography/scripts/typography_buffer.py`

Contoh eksekusi unit test deterministik:
```bash
python3 -m unittest ~/.hermes/skills/creative/adaptive-streaming-typography/scripts/test_typography_buffer.py
```

## Core Mechanics
1. **Cubic Bezier Eased Fade-In**: Interpolasi $P_1(0.25, 0.1), P_2(0.25, 1.0)$ berdurasi 60-65ms per token node.
2. **Dynamic Weight Shift**: Bobot font meningkat adaptif (400 -> 450 -> 500) saat burst generation (>25 TPS) untuk memandu fokus mata pembaca.
3. **Pre-emptive Baseline Clamp**: Perhitungan alokasi lebar karakter sebelum render aktual untuk mencegah layout jumps vertikal.

## Pitfalls
- Hindari manipulasi DOM synchronous `innerHTML += token` secara langsung karena memicu browser reflow berulang pada 60 FPS.
- Gunakan requestAnimationFrame atau Web Worker queue untuk memisahkan stream ingress dari render compositor.
