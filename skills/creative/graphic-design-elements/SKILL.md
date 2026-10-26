---
name: graphic-design-elements
description: Compose and apply core visual graphic design elements.
version: 0.1.0
author: Hermes Agent
license: MIT
related_skills:
  - procedural-vector-graphics
  - upnormal-ui-architecture
  - creative-visual-mindset
  - generative-visual-patterns
metadata:
  hermes:
    tags:
      - GraphicDesign
      - VisualElements
      - Composition
      - Typography
      - ColorTheory
---

# Graphic Design Elements & Visual Composition

Master, orchestrate, and audit the fundamental building blocks of graphic design: Line, Shape, Color, Typography, Space, Texture, Value, and Scale. Bridges classical Swiss/Bauhaus design principles with modern digital vector execution, enforcing deliberate contrast, structural hierarchy, and zero generic AI slop.

## When to Use
- "elemen elemen desain grafis" / "fundamental graphic design"
- "atur komposisi visual dan tata letak"
- "pilih palet warna kontras tinggi dan aturan 95/5"
- "pairing font dan hirarki tipografi editorial"
- "evaluasi ruang negatif dan prinsip Gestalt pada desain"
- "audit kualitas elemen desain grafis pada web atau poster"

## Prerequisites
- Standard Python 3 runtime for the design token auditing script (`scripts/design_audit_tokens.py`).
- Standard web browser and terminal environment.

## How to Run
Invoke the design element audit script via the `terminal` tool:
```bash
python3 scripts/design_audit_tokens.py --file "public/index.html"
```
Inspect and compose vector designs using `write_file`, `patch`, and `vision_analyze`.

## Quick Reference
- The 8 Elements: Line, Shape, Color, Typography, Space (Negative Space), Texture, Value (Light/Dark), Scale.
- Color Rule: 95% Achromatic Canvas (Ink `#111111`, Canvas `#F8F8F8`) + 5% Singular Accent Punch (`#FA5D29` / `#49B3FC`).
- Contrast Floor: WCAG AAA minimum 7:1 against background for text elements.
- Space Doctrine: Active whitespace over passive void; elements group via Gestalt Proximity.
- Typographic Scale: Monolithic display (64px–127px) contrasted against crisp micro-captions (10px–12px).
- Line Standard: Deliberate editorial underline offsets (4px–6px) and 1px hairline structural borders; banish muddy drop shadows.

## Procedure

1. **Establish Negative Space & Canvas Foundation:**
   Define spatial margins and layout boundaries before placing content. Use active whitespace to create breathing room and direct visual focus according to the Gestalt Law of Proximity.

2. **Structure Geometric & Organic Shapes:**
   Combine mathematical primitives (`rc`, `el`) with organic Catmull-Rom Bezier curves (`pth`). Ensure every shape serves a communicative function rather than acting as empty decorative filler.

3. **Deploy Achromatic Palette with Singular Accent:**
   Anchor 95% of the surface in neutral tones (Ink `#0D0E12`, Surface `#16181D`, Canvas `#0A0B0E`). Allocate the remaining 5% to a high-voltage focal accent (Ember `#FA5D29`, Cyan `#49B3FC`, or Lime `#A6FF00`).

4. **Calibrate Typographic Hierarchy & Emphasis:**
   Pair maximum two complementary type families (e.g. Heavy Grotesk Display + Monospace Data). Apply editorial underlines with generous offsets and keyword accent coloring to key concepts.

5. **Infuse Physical Texture & Spatial Depth:**
   Apply tactile frosted blur glass (`backdrop-filter: blur(16px)` with 1px hairline border) and subtle analog noise grain (`feTurbulence`) on Layer 0. Keep text on Layer 10 at 100% crisp sharpness.

6. **Audit Element Cohesion:**
   Run `scripts/design_audit_tokens.py` through `terminal` to verify contrast ratios, zero-emoji policy, and proper spatial rhythm.

## References
Load deep modular references on demand using `skill_view` (`name="graphic-design-elements"`, `file_path="references/<file>"`):
- `references/core-visual-elements.md`: The 8 foundational elements (Line, Shape, Color, Typography, Space, Texture, Value, Scale) and their digital implementations.
- `references/color-theory-and-palettes.md`: Contrast mathematics, chromatic balance, psychological resonance, and digital hex token systems.
- `references/typography-hierarchy-and-pairing.md`: Typeface classification, pairing matrices, line-height ratios, and emphasis techniques.
- `references/composition-gestalt-and-space.md`: Gestalt perceptual laws (Proximity, Similarity, Continuity, Closure, Figure-Ground) and focal gaze steering.

## Pitfalls
- **Decorative Clutter (AI Slop):** Adding floating glow circles or status badges with no semantic reason. Every element must have a clear functional purpose.
- **Low Contrast Traps:** Using trendy light-gray text on white backgrounds that fails WCAG AAA (must achieve >= 7:1).
- **Suffocated Spacing:** Crowding text and shapes against borders without generous padding and breathing room.
- **Emoji As Icons:** Using generic Unicode emojis instead of clean, scalable 1px SVG line vectors.

## Verification
Run a design token audit on a target file via `terminal`:
```bash
python3 scripts/design_audit_tokens.py --verify
```
Verify that the output reports zero contrast failures and confirms adherence to core graphic design elements.
