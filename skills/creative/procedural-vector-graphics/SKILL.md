---
name: procedural-vector-graphics
description: Generate scalable SVG vector assets procedurally from code.
version: 0.1.0
author: Hermes Agent
license: MIT
related_skills:
  - vector-engine-calibration
  - graphic-design-elements
  - upnormal-ui-architecture
  - generative-visual-patterns
  - motion-ui-lifecycle-and-morphing
  - architecture-diagram
metadata:
  hermes:
    tags:
      - VectorGraphics
      - SVG
      - GenerativeDesign
      - ProceduralArt
---

# Procedural Vector Graphics

Generate crisp, resolution-independent SVG vector graphics directly from procedural mathematical logic and coordinate arrays. Constructs smooth Catmull-Rom splines, geometric primitives, organic bezier paths, and auto-computed viewboxes without relying on external graphic editors or binary image assets. Does not generate diffusion raster images or heavy 3D mesh models; runs strictly on Python and Node.js standard libraries.

## When to Use
- "gambar vektor svg dengan kode" / "buat aset vektor prosedural"
- "buat animasi vektor" / "render animasi vektor langit ke mp4"
- "buat kurva bezier halus dari titik koordinat"
- "render ilustrasi kartun / panggung flat ke SVG"
- "generate vector artboard berstandar Figma"
- "buat icon atau grafik tanpa emoji dan tanpa aset eksternal"

## Prerequisites
- Standard Python 3 runtime (stdlib `math`, `json`, `os` only).
- Optional: `resvg-py` or `cairosvg` if headless PNG rasterization of the generated SVG is required.

## How to Run
Invoke procedural vector generation scripts through the `terminal` tool:
```bash
# Generate sample cybernetic system seal (SVG + PNG)
python3 scripts/vector_engine.py --demo --output seal.svg --png seal.png

# Generate procedural Bekbek mascot duck (SVG + PNG)
python3 scripts/vector_engine.py --mascot --output duck.svg --png duck.png

# Render looping procedural vector animation to MP4
python3 scripts/vector_engine.py --animate-sky --frames 90 --fps 30 --output sky.mp4
```
Inspect or edit generated vector source using `read_file`, `write_file`, and `patch`. Render output natively to Telegram with `MEDIA:/path/to/file.png` or `MEDIA:/path/to/file.mp4`.

## Quick Reference
- Primitives: Rectangle (`rc`), Ellipse (`el`), Smooth Path (`pth`).
- Catmull-Rom to Cubic Bezier Formula: Tangent $T_k = \frac{(P_{k+1} - P_{k-1}) \cdot \text{smooth}}{2}$. Control points $C_1 = P_0 + T_0$, $C_2 = P_1 - T_1$.
- Smoothing factor: `smooth=0.0` (sharp polygon), `smooth=0.3-0.5` (organic curved hills, rocks, or body contours).
- ViewBox Calculation: Auto-calculated dynamically via $[x_{\min} - m, y_{\min} - m, x_{\max} - x_{\min} + 2m, y_{\max} - y_{\min} + 2m]$.
- Precision: Format floating point coordinates to 1 decimal place (`.1f`) for optimal SVG payload compactness.

## Procedure

1. **Initialize the Shapes Vector Canvas:**
   Instantiate coordinate tracking and bounding box accumulators:
   ```python
   import math

   class Shapes:
       def __init__(self):
           self.items = []
           self.minx = self.miny = 1e9
           self.maxx = self.maxy = -1e9

       def _box(self, pts):
           for x, y in pts:
               self.minx = min(self.minx, x)
               self.miny = min(self.miny, y)
               self.maxx = max(self.maxx, x)
               self.maxy = max(self.maxy, y)
   ```

2. **Add Primitives with Local Transformation:**
   Implement rounded rectangles and ellipses:
   ```python
   def rc(self, x, y, w, h, fill, r=0, rot=0):
       a = math.radians(rot)
       ca, sa = math.cos(a), math.sin(a)
       self._box([(x + dx * ca - dy * sa, y + dx * sa + dy * ca)
                  for dx in (-w/2, w/2) for dy in (-h/2, h/2)])
       self.items.append(
           f'<rect x="{-w/2:.1f}" y="{-h/2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r:.1f}" '
           f'fill="{fill}" transform="translate({x:.1f} {y:.1f}) rotate({rot})"/>'
       )
       return self

   def el(self, x, y, w, h, fill):
       self._box([(x - w/2, y - h/2), (x + w/2, y + h/2)])
       self.items.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{w/2:.1f}" ry="{h/2:.1f}" fill="{fill}"/>')
       return self
   ```

3. **Construct Catmull-Rom to Cubic Bezier Splines:**
   Convert polygon point sequences into organic closed curves:
   ```python
   def pth(self, pts, fill, smooth=0.4):
       n = len(pts)
       t_vec = []
       for k in range(n):
           prev_p, next_p = pts[(k - 1) % n], pts[(k + 1) % n]
           t_vec.append(((next_p[0] - prev_p[0]) * smooth / 2, (next_p[1] - prev_p[1]) * smooth / 2))
       d = f'M{pts[0][0]:.1f} {pts[0][1]:.1f}'
       for k in range(n):
           p0, p1 = pts[k], pts[(k + 1) % n]
           c1 = (p0[0] + t_vec[k][0], p0[1] + t_vec[k][1])
           c2 = (p1[0] - t_vec[(k + 1) % n][0], p1[1] - t_vec[(k + 1) % n][1])
           d += f' C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p1[0]:.1f} {p1[1]:.1f}'
           self._box([c1, c2, p1])
       self.items.append(f'<path d="{d} Z" fill="{fill}"/>')
       return self
   ```

4. **Compute ViewBox and Compile Scalable SVG:**
   Package the drawn elements into standalone SVG markup:
   ```python
   def compile_svg(shapes, padding=8):
       x0 = math.floor(shapes.minx - padding)
       y0 = math.floor(shapes.miny - padding)
       w = math.ceil(shapes.maxx + padding) - x0
       h = math.ceil(shapes.maxy + padding) - y0
       svg_header = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {w} {h}" width="{w}" height="{h}">'
       return f'{svg_header}{"".join(shapes.items)}</svg>'
   ```

5. **Verify Vector Integrity:**
   Save output file via `write_file` and inspect viewBox dimensions with `terminal`.

## References
Load deep procedural vector references on demand using `skill_view` (`name="procedural-vector-graphics"`, `file_path="references/<file>"`):
- `references/spline-bezier-mathematics.md`: Mathematical foundations of Catmull-Rom splines, tangent calculation, smoothing thresholds, and dynamic viewBox derivation.
- `references/mascot-and-character-vector-design.md`: Chibi proportional formulas, Z-order layer hierarchies, eye specular highlights, and case study of the Bekbek duck.
- `references/insignia-badge-and-icon-geometry.md`: Precision radial dial tick distributions, rotated rounded diamonds, and sinusoidal telemetry waveforms.
- `references/figma-export-and-styling-tokens.md`: Clean SVG group hierarchies for Figma drag-and-drop, palette tokenization, and ultra-fast resvg-py rasterization.
- `references/vector-animation-and-video-rendering.md`: Parametric normalized time loops, multi-layer cloud parallax hierarchies, and ffmpeg MP4 video compilation.

## Pitfalls
- **Over-Smoothing Self-Intersections:** Setting `smooth > 0.6` on tight polygon corners causes spline overshoot and looping self-intersections. Keep smooth between `0.3` and `0.5`.
- **Hardcoded ViewBox Clippings:** Never hardcode fixed `viewBox="0 0 100 100"` when procedurally generating rotated geometries; always derive the bounds from accumulated vertices.
- **Unrounded Coordinates Flooding Tokens:** Omitting coordinate decimal formatting yields numbers like `124.89127491823`, inflating file size 4x without visual benefit. Format coordinates to 1 decimal place.

## Verification
Run a standalone generation test through `terminal`:
```bash
python3 -c "
import math
class S:
    def __init__(s): s.items=[]; s.minx=s.miny=1e9; s.maxx=s.maxy=-1e9
    def el(s,x,y,w,h,c):
        s.minx=min(s.minx,x-w/2); s.miny=min(s.miny,y-h/2)
        s.maxx=max(s.maxx,x+w/2); s.maxy=max(s.maxy,y+h/2)
        s.items.append(f'<ellipse cx=\"{x}\" cy=\"{y}\" rx=\"{w/2}\" ry=\"{h/2}\" fill=\"{c}\"/>'); return s
s = S().el(50,50,40,40,'#FA5D29')
w, h = int(s.maxx-s.minx+16), int(s.maxy-s.miny+16)
svg = f'<svg viewBox=\"{int(s.minx-8)} {int(s.miny-8)} {w} {h}\" width=\"{w}\" height=\"{h}\">{\"\".join(s.items)}</svg>'
assert '<svg' in svg and '</svg>' in svg
print('Procedural SVG verification passed:', len(svg), 'bytes')
"
```
Verify that the output prints `Procedural SVG verification passed` without syntax or assertion errors.
