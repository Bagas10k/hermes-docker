---
name: spatial-glass-morphism
description: Compose visionOS fluid glassmorphism and depth physics.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [uiux, spatial, glassmorphism, visionos, optics, depth]
    related_skills: [bento-grid-spatial-composer, spatial-canvas-ui-physics]
---

# Spatial Fluid Glassmorphism & Depth Physics

Skill for modeling and rendering visionOS and iOS 18 fluid glass interfaces with physically accurate optics, microfacet specular reflection, chromatic dispersion falloff, and zero-frame-drop GPU compositing.

## When to Use
- Designing high-depth spatial interfaces, HUD cards, and floating panels.
- Implementing multi-tier elevation with dynamic blur, saturation, and contrast compensation.
- Calculating Fresnel-Schlick reflection highlights and chromatic dispersion deltas.
- Don't use for: Flat 2D retro terminal interfaces or minimal monochrome text documents.

## Prerequisites
- Modern browser supporting CSS `backdrop-filter: blur(...) saturate(...) contrast(...)`.
- Python 3.10+ for computing deterministic optical token sets.

## Quick Reference
Compute material tokens directly using the bundled Python engine:
```bash
python3 ~/.hermes/skills/creative/spatial-glass-morphism/scripts/glass_physics_engine.py
```

## Physical Parameters & Mathematical Model
1. **Fresnel-Schlick Reflectance**:
   $$R(\theta) = F_0 + (1 - F_0)(1 - \cos\theta)^5, \quad F_0 = \left(\frac{n - 1}{n + 1}\right)^2$$
   For optical acrylic ($n = 1.52$), normal reflectance $F_0 \approx 0.0426$ and grazing reflectance reaches $1.0$.

2. **Chromatic Dispersion Offset (Cauchy Approximation)**:
   $$n(\lambda) = A + \frac{B}{\lambda^2}$$
   Simulates subtle RGB edge refraction ($\Delta d \approx 0.045\text{px}$) to prevent flat, artificial rendering.

3. **Multi-Pass Blur & Saturation Compensation**:
   Base blur radius scales with elevation ($8\text{px} - 50\text{px}$). Saturation boost ($120\% - 150\%$) counteracts milky mudiness under low opacity.

## Elevation Token Tiers
- **Tier 1 (Surface / Inset)**: `dp: 8`, `blur: 10px`, `border: rgba(255,255,255,0.18)`, `highlight: 0.45`
- **Tier 2 (Floating Panel / Card)**: `dp: 16`, `blur: 14px`, `border: rgba(255,255,255,0.28)`, `highlight: 0.65`
- **Tier 3 (Modal / Active Focus)**: `dp: 28`, `blur: 24px`, `border: rgba(255,255,255,0.38)`, `highlight: 0.85`

## Verification
Run determinism test suite:
```bash
python3 -m unittest ~/.hermes/skills/creative/spatial-glass-morphism/scripts/test_glass_physics.py
```
