---
name: consistent-vector-asset-families
description: Build consistent, fully editable SVG vector asset families.
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Vector, DesignSystem, SVG, ConsistentStyles, ProceduralGraphics]
    related_skills: [procedural-vector-graphics, vector-engine-calibration, upnormal-ui-architecture, graphic-design-elements]
---

# Consistent Vector Asset Families

Procedurally generate and orchestrate collections of complex vector objects sharing an identical visual DNA, material texture, lighting model, and color temperature. It solves the fragmentation problem where generative tools create mismatched illustrations, by decoupling structural geometry from a unified style signature. This skill does not generate raster bitmaps or uneditable rasterized vectors; all outputs are 100% scalable, layered mathematical SVG curves with exposed anchor nodes and gradient fills. Key dependency stance: Python standard library plus native SVG rendering.

## When to Use

- "buatkan set icon atau aset dengan gaya seragam"
- "buatkan keluarga aset SVG dengan satu tema visual identik"
- "terapkan konsistensi gaya visual 3D glassmorphism pada banyak objek"
- "ekstrak dan standarisasi token gaya material untuk grafis vektor"
- "bangun aset ilustrasi yang bisa di-edit titik path-nya (editable anchor nodes)"

## Prerequisites

- Python 3.9+ (standard library `math`, `os`, `json` for procedural asset family generator).
- Optional raster verification tools: `resvg` CLI or `ffmpeg` installed on the host system.
- No third-party vector API or cloud token required; runs completely offline and deterministically.

## How to Run

1. Generate a coherent 5-subject asset family in the Rose Gold / Glass signature using the script through the `terminal` tool:
   ```bash
   python3 ~/.hermes/profiles/bikagent/skills/creative/consistent-vector-asset-families/scripts/generate_asset_family.py --style rose_gold --output-dir /tmp/asset_family/
   ```
2. Inspect or modify individual SVG paths and gradient definitions through `read_file` or `patch`.
3. Verify visual coherence across all subjects using `vision_analyze` on rasterized renders.

## Quick Reference

| Component | Path / Command | Description |
|---|---|---|
| Family Generator | `scripts/generate_asset_family.py` | CLI engine generating 5+ coherent SVG assets from style tokens |
| Material Spec | `references/material-signature-and-lighting.md` | Formulas for metallic chrome, frosted glass, and studio lighting |
| Node Geometry | `references/svg-node-editing-and-gradients.md` | Bézier curve guidelines, anchor node optimization, and mesh gradients |
| Cohesion Matrix | `references/asset-family-cohesion-matrix.md` | Multi-subject benchmark checklist for style fidelity |

## Procedure

1. **Define the Unified Style Signature:**
   Establish the 5 core tokens: primary metal gradient, specular highlight curve, deep ambient occlusion shadow, frosted glass translucent tint, and contact drop shadow.
   Load details on demand with `skill_view(file_path="references/material-signature-and-lighting.md")`.

2. **Construct Subject Silhouettes via Parametric Geometry:**
   Model subject skeletons (e.g. vintage camera, desk lamp, seashell, wristwatch) using clean Bézier anchors `<path d="M... C... Z"/>`. Ensure consistent corner rounding and line tension.
   Load details on demand with `skill_view(file_path="references/svg-node-editing-and-gradients.md")`.

3. **Bind Global Style Tokens to Local Geometry:**
   Inject shared `<defs>` containing `<linearGradient>` and `<radialGradient>` into every asset file, keeping IDs synchronized across the family.

4. **Batch Generate and Audit Cohesion:**
   Execute `scripts/generate_asset_family.py` via `terminal` and verify the output against the 4 cohesion criteria in `references/asset-family-cohesion-matrix.md`.

## Pitfalls

- **Unique Defs ID Collision:** If multiple SVGs from a family are embedded inline on one HTML page, gradient IDs (e.g. `#metalGrad`) will collide unless namespaced or encapsulated in web components.
- **Over-Complex Paths:** Generative SVG that converts pixel traces into millions of tiny triangles is uneditable. Always enforce smooth cubic Bézier curves (`C` and `S` commands) with under 50 anchor points per component.
- **Inconsistent Light Angle:** Varying light angles between assets breaks the illusion of a family. Strictly lock light vectors to $-45^\circ$ (top-left) across all subjects.
- **FeSpecularLighting Clay Trap:** Never apply `feSpecularLighting` over blurred alpha to simulate glass in SVG. It produces an opaque, clay-like or silicone neumorphic relief, completely destroying glass transparency. Real vector glass requires double-wall contours with dark refractive boundaries.
- **Flat Glass Transparency Trap:** A single outline filled with flat semi-transparent white looks like cheap film or plastic. Vector crystal glass requires double-wall contours (6-8px offset), razor-sharp crescent specular ribbons, and dark refractive edge stops.

## Verification

Run the generator script and verify that all assets render cleanly without missing defs:
```bash
python3 ~/.hermes/profiles/bikagent/skills/creative/consistent-vector-asset-families/scripts/generate_asset_family.py --verify
```
A successful run returns exit code 0 and reports `All 5 asset family SVGs generated and validated successfully`.
