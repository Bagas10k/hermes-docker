# Color Science, OKLCH, and Calibrated Harmonious Palettes

## 1. The Perceptual Uniformity Defect in sRGB / HSL
Standard HSL/RGB models fail in perceptual brightness:
- Pure yellow (`#FFFF00`) has a relative luminance of ~0.93.
- Pure blue (`#0000FF`) has a relative luminance of ~0.07.
In standard HSL, setting Lightness to 50% (`hsl(60, 100%, 50%)` vs `hsl(240, 100%, 50%)`) results in wildly different perceived contrast against light backgrounds. Yellow washes out, while blue is uncomfortably dark.

## 2. The OKLCH Advantage in Modern CSS
OKLCH (Lightness, Chroma, Hue) maps colors along a perceptually uniform axis:
```css
/* Constant perceptual lightness across hues */
--accent-amber: oklch(0.75 0.16 75);
--accent-emerald: oklch(0.75 0.16 155);
--accent-cyan: oklch(0.75 0.16 220);
--accent-violet: oklch(0.75 0.16 295);
--accent-rose: oklch(0.75 0.16 25);
```
When `--lightness` and `--chroma` are kept constant, shifting `--hue` guarantees that all accents share uniform visual weight, preventing "rainbow kitsch" or eye-straining uneven contrast.

## 3. WCAG 2.1 vs APCA (Accessible Perceptual Contrast Algorithm)
- **WCAG 2.1 AA Requirements**:
  - Normal text (< 18pt / 24px regular): Minimum contrast ratio 4.5:1.
  - Large text (>= 18pt / 24px regular or >= 14pt / 18.5px bold): Minimum contrast ratio 3.0:1.
  - UI components and graphical objects: Minimum contrast ratio 3.0:1.
- **Badge Foreground Rule**:
  - High-luminance accents (Amber, Emerald, Cyan) MUST use Deep Charcoal Slate (`#0F172A`) foreground text to achieve >= 7:1 contrast.
  - Low-luminance accents (Violet, Rose, Dark Indigo) MUST use Crisp White (`#FFFFFF`) foreground text to achieve >= 4.5:1 contrast.

## 4. User Preference Benchmark (Triad Red-White-Yellow & Clean Slate)
- **Dark Mode Showcase**:
  - Canvas: `#0B0A10`
  - Cards: `#15131D`
  - Crimson Accent: `#EF4444` / `#DC2626`
  - Amber Accent: `#F59E0B` / `#D97706`
  - Text & Accents: `#FFFFFF`
- **Light Mode Enterprise**:
  - Canvas: `#FAF8F5` (Warm Paper)
  - Cards: `#FFFFFF` (Solid White with `#E2E8F0` border and layered soft shadow)
  - Heading: `#0F172A` (17.85:1 contrast ratio, WCAG AAA compliant)
  - Semantics: Emerald (RAM/Healthy), Amber (CPU/Notice), Cyan (Storage/Links), Violet (Agent/AI).
