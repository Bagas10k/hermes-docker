---
name: vector-engine-calibration
description: Calibrate, benchmark, and tune procedural vector engines.
version: 0.1.0
author: Hermes Agent
license: MIT
related_skills:
  - procedural-vector-graphics
  - graphic-design-elements
  - upnormal-ui-architecture
  - generative-visual-patterns
metadata:
  hermes:
    tags:
      - VectorCalibration
      - SVGEngine
      - Benchmark
      - SplineTuning
      - Optimization
---

# Vector Engine Calibration & Profiling

Calibrate, benchmark, and optimize procedural vector and SVG generation engines. Diagnoses curve distortion, tunes Catmull-Rom spline tension, prevents viewBox boundary clipping, enforces coordinate decimal quantization, and verifies sub-millisecond rasterization performance.

## When to Use
- "kalibrasi mesin vektor" / "tune vector engine parameters"
- "optimalkan ukuran file SVG prosedural"
- "kalibrasi kehalusan kurva spline dan deteksi overshoot"
- "uji batas performa render resvg headless"
- "verifikasi clipping dan padding viewBox pada aset vektor"

## Prerequisites
- Standard Python 3 runtime (stdlib `math`, `time`, `json`, `os`).
- Optional: `resvg-py` for headless rasterization latency benchmarking.

## How to Run
Invoke the calibration suite through the `terminal` tool:
```bash
# Run full automated calibration & benchmark suite
python3 scripts/calibrate_vector_engine.py --full --output-dir /tmp/vector_calibration

# Calibrate specific spline smoothing parameter
python3 scripts/calibrate_vector_engine.py --tune-smooth 0.35
```
Inspect calibration test cards using `vision_analyze` and verify metrics with `read_file`.

## Quick Reference
- Optimal Smoothing Interval: $0.30 \le \text{smooth} \le 0.45$. Values $> 0.55$ risk acute angle overshoot.
- Coordinate Decimal Budget: Quantize coordinates to 1 decimal place (`.1f`). Reduces payload size by 40%–60% with zero perceptual loss.
- ViewBox Padding Formula: $\text{pad} = \max(8\text{px}, \lceil \text{stroke\_width} \cdot 1.5 \rceil)$ to prevent stroke clipping.
- Performance Invariant: SVG procedural generation latency $\le 5\text{ms}$; 2x PNG rasterization via `resvg-py` $\le 50\text{ms}$.
- Scalability Gate: Non-scaling strokes (`vector-effect="non-scaling-stroke"`) on fine technical scales.

## Procedure

1. **Audit Spline Tension & Curvature Fidelity:**
   Pass varied polygonal geometries (acute $30^\circ$, right $90^\circ$, obtuse $150^\circ$) through Catmull-Rom interpolation. Calculate control point vectors and verify that tangent magnitudes do not induce self-intersecting loops.

2. **Calibrate ViewBox Envelope & Stroke Margins:**
   Execute boundary stress tests on rotated geometries. Ensure accumulated coordinates incorporate stroke thickness and corner radiuses so no element clips against the `viewBox` boundary.

3. **Benchmark Coordinate Quantization & Token Overhead:**
   Compare unrounded floating point output against quantized formats (`.2f`, `.1f`, `int`). Lock precision to `.1f` as the enterprise standard.

4. **Profile Headless Rasterization Throughput:**
   Measure `resvg-py` frame render times across 1x (web), 2x (Retina), and 4x (print) output resolutions. Confirm output file sizes and absence of memory leaks.

5. **Generate Diagnostic Calibration Card:**
   Produce a multi-panel visual calibration card containing concentric dials, sine waves, spline comparison bands, and color contrast swatches for empirical quality inspection.

## References
Load deep calibration references on demand using `skill_view` (`name="vector-engine-calibration"`, `file_path="references/<file>"`):
- `references/spline-tension-and-overshoot.md`: Mathematical error bounds, loop self-intersection prevention, and tangent damping algorithms.
- `references/viewbox-clipping-and-padding.md`: Coordinate bounding box accumulators, stroke dilation compensation, and responsive aspect ratio locking.
- `references/precision-quantization-and-minification.md`: Decimal truncation benchmarks, XML minification, and token efficiency analysis.
- `references/rasterization-latency-benchmarking.md`: Headless renderer benchmarking (resvg-py vs cairosvg), multi-threading throughput, and memory profiling.

## Pitfalls
- **Acute Angle Loop Explosions:** Applying high smoothing (`smooth >= 0.6`) on sharp triangle corners causes Bezier control points to cross backwards, forming unwanted teardrop loops.
- **Stroke Width Edge Clipping:** Calculating viewBox strictly from vertex coordinates while ignoring `stroke-width` causes outer stroke edges to be sheared by the SVG boundary.
- **Floating Point Inflation:** Uncalibrated generators outputting 16-digit floats (`x="142.8912847291823"`), ballooning file size and slowing down DOM parsers.

## Verification
Execute the engine self-calibration probe via `terminal`:
```bash
python3 scripts/calibrate_vector_engine.py --verify
```
Verify that the output reports all diagnostic assertions as `PASSED` with zero clipping and optimal spline tension.
