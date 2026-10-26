---
name: universal-icon-morphing
description: Morph any arbitrary SVG icon into any other shape at 60 FPS.
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [SVG, IconMorphing, UIAnimation, MicroInteractions, VectorMotion, 60fps]
    related_skills: [motion-ui-lifecycle-and-morphing, procedural-vector-graphics, consistent-vector-asset-families]
---

# Universal Icon Morphing Engine

Procedurally animate, interpolate, and morph ANY arbitrary SVG vector icon or shape into ANY other shape in 60 FPS in-place fluid motion. It solves the classic morphing failure where shapes with differing node counts either crash or twist into deformed tangles ("pretzel artifacts"). This skill establishes the exact two-stage mathematical normalization pipeline (Arclength Resampling and Rotational Phase Alignment) required for zero-distortion vector micro-interactions.

## When to Use

- "buatkan animasi morphing antar icon UI"
- "ubah icon A menjadi icon B secara halus (in-place shape transition)"
- "morphing icon sembarang (any shape to any shape)"
- "animasikan micro-interaction tombol (hamburger to close, play to pause, sun to moon, download to checkmark)"
- "cegah distorsi terpelintir saat interpolasi path SVG"

## Prerequisites

- Python standard library (`math`, `re`, `os`).
- Optional rasterization/render engine: `resvg-py` or `ffmpeg` on host system.
- Standalone SVG output runs with native CSS or SMIL `<animate>` without external JS runtime.

## How to Run

1. Generate a 4-card interactive SVG morphing showcase via Python script:
   ```bash
   python3 /home/ubuntu/bekvector-engine/examples/universal_morph_showcase.py
   ```
2. Run automated morphing integrity tests in the engine:
   ```bash
   python3 -m unittest discover /home/ubuntu/bekvector-engine/tests
   ```

## Quick Reference

| Operation | Method / Formula | Purpose |
|---|---|---|
| Arclength Resampling | `resample_polygon(pts, N=72)` | Normalizes node count to $N$ equidistant perimeter samples |
| Rotational Alignment | `align_rotation(poly_a, poly_b)` | Minimizes $\sum \|A_i - B_{i+\text{shift}}\|^2$ to prevent twisting |
| Catmull-Rom Smooth | `polygon_to_smooth_path(pts)` | Converts discrete samples to smooth cubic Bézier `M C ... Z` |
| Timing Function | `cubic-bezier(0.16, 1, 0.3, 1)` | Standard Apple/Linear inertia spring curve for UI transitions |

## Procedure

1. **Polygon Perimeter Normalization:**
   Calculate the cumulative perimeter distance array $D_k = \sum_{i=0}^{k-1} \|P_{i+1} - P_i\|$.
   Resample $N$ points at uniform intervals $\Delta s = D_{\text{total}} / N$ ($N=64$ or $72$).

2. **Rotational Phase Alignment (Anti-Twist):**
   Evaluate all $N$ cyclical shift permutations $k \in [0, N-1]$.
   Select $k^* = \arg\min_k \sum_{i=0}^{N-1} \|A_i - B_{(i+k) \pmod N}\|^2$.
   Reorder Shape B starting from index $k^*$.

3. **Parametric Easing Interpolation:**
   For progress $t \in [0, 1]$, compute $P_i(t) = (1 - E(t)) \cdot A_i + E(t) \cdot B_{(i+k^*) \pmod N}$.
   Apply easing $E(t) = \frac{1 - \cos(2\pi t)}{2}$ or `cubic-bezier(0.16, 1, 0.3, 1)`.

4. **Smooth Bézier Generation:**
   Convert discrete points into continuous cubic Bézier control points via Catmull-Rom tangent vectors:
   $$CP1_i = P_i + \frac{P_{i+1} - P_{i-1}}{6}, \quad CP2_i = P_{i+1} - \frac{P_{i+2} - P_i}{6}$$

## Pitfalls

- **Differing Node Count Crash:** Directly animating `d` attribute in CSS without resampling will fail or snap abruptly if command tokens differ. Always normalize to $N$ samples.
- **Pretzel Inversion Trap:** Without rotational alignment, shapes with opposite starting vertices will flip inside out midway through the transition. Always align rotation phase before interpolating.
- **Over-Sampling Jank:** Resampling to $>200$ nodes creates wavy jitter along straight edges and degrades mobile GPU performance. Keep $N \in [64, 96]$.

## Verification

Verify path interpolation between two arbitrary shapes returns a valid closed cubic Bézier path:
```bash
python3 -c "
from bekvector import UniversalMorph
p = UniversalMorph.morph_between('heart', 'star', 0.5)
assert p.startswith('M ') and p.endswith('Z') and 'C ' in p
print('UniversalMorph verified successfully')
"
```
Output must print `UniversalMorph verified successfully` with exit code 0.
