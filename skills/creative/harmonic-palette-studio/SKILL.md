---
name: harmonic-palette-studio
description: Calibrate colorful harmonious palettes and WCAG contrast.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ui-ux, color-palette, design-system, oklch, wcag-contrast, vibe-coding]
    related_skills: [vibe-coding-accelerator, design-md, ui-ux-design-vault]
---

# Harmonic Palette Studio Skill

Synthesize vivid, colorful, yet mathematically harmonious UI color palettes with automated WCAG contrast validation and perceptual lightness calibration.

## When to Use

- User asks for bright, colorful, vibrant web UI that remains harmonized, elegant, and comfortable to read.
- Implementing dashboard color schemes, status accents, or landing page branding.
- Auditing contrast ratios for accessible badges, cards, buttons, and typography.
- Don't use for: pure monochrome grayscale wireframes with zero color accents.

## Prerequisites

- Python 3.8+ with standard library (`math`, `json`, `sys`).
- Optional helper script: `python3 ~/.hermes/skills/creative/harmonic-palette-studio/scripts/palette_calibrator.py`.

## Quick Reference

- **Generate Calibrated Palette**:
  `terminal(command="python3 ~/.hermes/skills/creative/harmonic-palette-studio/scripts/palette_calibrator.py '#F59E0B' triadic light")`
- **Light Mode Foundations**:
  - Canvas: `#FAF8F5` (Warm Paper)
  - Card: `#FFFFFF` (1px `#E2E8F0` border, soft drop-shadow)
  - Text: `#0F172A` (Heading, WCAG AAA 17.8:1), `#334155` (Body), `#64748B` (Muted)
- **Dark Mode Foundations**:
  - Canvas: `#0B0A10` (Deep Obsidian)
  - Card: `#15131D` (Layered Slate)
  - Primary Accents: Crimson `#EF4444`, Amber `#F59E0B`, Pure White `#FFFFFF`

## Procedure

1. **Establish Foundation Contrast**:
   - Set canvas and card background. Verify primary text achieves >= 7:1 contrast (WCAG AAA).
2. **Select Semantic Hue Anchors**:
   - Emerald (`#10B981`): Healthy, success, safe allocation.
   - Amber (`#F59E0B`): Primary warning, CPU, active focus.
   - Sky Cyan (`#0EA5E9`): Network, links, storage download.
   - Violet (`#8B5CF6`): AI processing, agent orchestration.
   - Coral Rose (`#F43F5E`): Critical status, errors, high latency.
3. **Calibrate Perceptual Uniformity**:
   - Use OKLCH or lightness-clamped HSL to avoid blinding fluorescent spikes.
   - Run the calibrator script to verify badge text contrast: automatically choose `#0F172A` text on high-luminance pills and `#FFFFFF` on dark pills.
4. **Deploy Zero-Emoji Semantic Badges**:
   - Pair each color accent with geometric status glyphs (`[•]`, `[OK]`, `[RUN]`, `[WARN]`) or SVG monokrom lines.

## Pitfalls

- **Rainbow Clutter**: Dumping uncalibrated bright hues across adjacent elements confuses hierarchy. Always anchor 80% of the surface in clean neutral cards, reserving vivid colors for status pills, charts, and key focal points.
- **Pure Yellow on White**: Yellow/Amber text directly on white backgrounds drops below 2:1 contrast. Use Amber backgrounds with `#0F172A` text instead.

## Verification

- Run `palette_calibrator.py` against the selected base hex.
- Check `wcag_aaa_text` is `true` and all badge contrast ratios exceed 4.5:1.
