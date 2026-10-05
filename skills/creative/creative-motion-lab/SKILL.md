---
name: creative-motion-lab
description: Use when building canvas shaders, motion & UI physics.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [creative, canvas, webgl, shaders, motion, spring-physics, particles, fluid, interactive]
    related_skills: [frontend-agent-craft, ui-ux-design-vault, popular-web-designs, ponytail]
---

# Creative Motion Lab & Interactive Canvas Suite

Modul terpadu untuk merancang animasi antarmuka 60 FPS, efek shader WebGL, simulasi partikel, fisika pegas (spring physics), dan kanvas interaktif. Seluruh kapabilitas terintegrasi secara modular melalui referensi di `references/`.

## Panduan Sub-Modul Terintegrasi
1. **WebGL GLSL Shaders & Backdrops**:
   - `references/shader-canvas-flow.md`: Render interaktif shader fragment WebGL untuk ambient backdrop.
   - `references/dynamic-canvas-backdrop.md`: Reactive WebGL ambient background dengan transisi halus.
2. **Fluid Mechanics & Particle Systems**:
   - `references/fluid-interactive-surface.md`: Real-time fluid dynamic surface 60 FPS.
   - `references/vector-field-particle-flow.md`: Aliran partikel reaktif berbasis vektor medan.
3. **UI Physics & Kinematics**:
   - `references/spring-physics-motion-lab.md`: Desain kurva gerak fisika pegas interaktif (damping, stiffness, mass).
   - `references/spatial-canvas-ui-physics.md`: 3D spatial canvas dan spring physics pada kartu antarmuka.
   - `references/surface-curvature-and-kinematics.md`: Smoothing kelengkungan G2/squircle dan pergerakan halus.
4. **Kinetic Typography & Audio-Reactive Visuals**:
   - `references/kinetic-typography-glitch.md`: Efek kinetik status teks dan tipografi responsif.
   - `references/audio-reactive-visual-flow.md`: Visualisasi audio reaktif 60 FPS.
   - `references/interactive-canvas-sketchbook.md`: Kanvas eksperimen 2D/WebGL untuk visual prototipe cepat.

## Standar Performa & Disiplin Koding
- **60 FPS & Zero-Jank**: Gunakan `requestAnimationFrame` dengan delta timing (`dt`), hindari alokasi memori berulang di dalam render loop (Zero GC).
- **Graceful Fallback**: Selalu sediakan fallback CSS statis atau canvas 2D jika konteks WebGL tidak tersedia.
- **Respect User Preferences**: Patuhi `@media (prefers-reduced-motion: reduce)` untuk aksesibilitas pengguna.
