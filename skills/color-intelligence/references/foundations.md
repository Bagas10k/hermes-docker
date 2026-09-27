# Color Foundations

## Contents
1. Color dimensions
2. Color spaces and formats
3. Perception
4. Harmony
5. Contrast and hierarchy
6. Temperature
7. Saturation and chroma
8. Lightness and tonal structure
9. Proportion
10. Mixing and derivation
11. Practical heuristics

## 1. Color dimensions

Think about color as multiple controllable dimensions rather than as a named hue.

- **Hue**: the family of color, such as red, orange, green, cyan, blue, violet.
- **Lightness/value**: how light or dark the color appears. Often the strongest driver of readable hierarchy.
- **Saturation/chroma**: how colorful/intense a color appears. High chroma attracts attention quickly.
- **Alpha**: transparency. It changes the resulting color because the background contributes to the final appearance.
- **Temperature**: warm/cool impression. It is contextual, not absolute.
- **Area**: the amount of screen occupied by a color. A highly saturated color can be pleasant as a 3% accent and overwhelming at 60% area.

Never assess a swatch in isolation. Judge it in its actual size, neighboring colors, and background.

## 2. Color spaces and formats

### HEX / RGB
Useful for implementation and interoperability in sRGB. Poor for manually constructing perceptually even scales because equal numeric steps are not equal perceived steps.

### HSL / HSV
Useful for intuitive hue/saturation/lightness editing, but their lightness/saturation are not perceptually uniform. Two colors with the same HSL lightness may look very different in brightness.

### Lab / LCH
Designed around human perception more than RGB/HSL. LCH gives lightness, chroma, and hue-like angle.

### OKLab / OKLCH
Useful for modern digital color systems because changing lightness and chroma generally behaves more predictably to the eye. Prefer it when constructing systematic web palettes if compatibility is acceptable. Still verify gamut and actual rendered results.

## 3. Perception

Color is relational:
- the same gray can look warm next to blue and cool next to orange;
- a mid-tone color can appear lighter on black and darker on white;
- saturated accents look stronger when surrounded by low-chroma neutrals;
- small text needs stronger luminance separation than large decorative shapes.

Account for simultaneous contrast, adaptation to ambient brightness, display variability, and user vision differences.

## 4. Harmony

Harmony models are starting structures, not automatic quality guarantees.

- **Monochromatic**: one hue family with changing lightness/chroma. Cohesive and easy to control.
- **Analogous**: neighboring hue families. Smooth and atmospheric.
- **Complementary**: opposing hues. Strong energy; usually let one side dominate and use the other as accent.
- **Split complementary**: one base plus two near-opposites. More flexible than direct complements.
- **Triadic**: three broadly spaced hue families. Can become noisy unless chroma and area are disciplined.
- **Tetradic**: four families. Use only when the system genuinely needs many roles/categories.

For product UI, semantic role clarity is usually more important than textbook harmony.

## 5. Contrast and hierarchy

Hierarchy can be created through:
1. lightness contrast;
2. chroma contrast;
3. hue contrast;
4. temperature contrast;
5. area/proportion;
6. isolation/whitespace;
7. edge/border contrast.

Lightness is the most robust foundation. Use hue and chroma to reinforce hierarchy rather than carry it alone.

## 6. Temperature

Warm colors often feel nearer, energetic, social, tactile, or urgent. Cool colors often feel distant, calm, technical, clean, or spacious. These are tendencies, not universal truths.

Neutral temperature matters too:
- warm gray → softer, editorial, organic, hospitality, lifestyle;
- cool gray → technical, corporate, analytical, precise;
- near-neutral → minimal, adaptable, product-focused.

A palette often feels more coherent when neutrals share a subtle temperature relationship with the primary family.

## 7. Saturation and chroma

High chroma:
- attracts attention;
- feels energetic;
- can look cheap/noisy when overused;
- can cause vibration against another intense color;
- is more suitable for small action/status accents than large reading surfaces.

Low chroma:
- supports long viewing sessions;
- gives space for accents to work;
- can feel premium or calm when contrast remains sufficient;
- can become lifeless if all roles collapse into similar grayness.

Use a **chroma hierarchy**: neutral structure < secondary/supporting color < primary action < exceptional alert, adjusted for context.

## 8. Lightness and tonal structure

Build a lightness ladder before obsessing over hue. Typical UI relationships:
- canvas differs from surface;
- elevated surface differs slightly from base surface;
- border is visible but subordinate;
- primary text is much stronger than secondary text;
- muted text stays readable;
- selected/active state has a clear tonal change.

Check the composition in grayscale. If the intended hierarchy disappears, hue is doing too much work.

## 9. Proportion

The classic 60/30/10 idea can be a loose composition heuristic, not a fixed law. Digital interfaces often work better with much more neutral area and far less accent area.

Think in relative visual weight:
- dominant foundation: canvas/surfaces;
- supporting structure: secondary surfaces, borders, muted regions;
- identity/action: primary family;
- rare emphasis: accent/status.

The brighter or more saturated a color, the less area it usually needs.

## 10. Mixing and derivation

Do not create lighter colors by simply adding white in every case or darker colors by adding black. That can produce chalky tints and muddy shades.

Prefer controlled changes in perceptual lightness and chroma:
- lighter steps often need slightly reduced chroma;
- very dark steps may also need chroma adjustment because display/gamut behavior changes;
- preserve hue identity across the middle steps, then allow gentle hue drift if it improves natural appearance.

## 11. Practical heuristics

- Establish neutrals first for UI-heavy work.
- One strong accent family is often enough.
- Let accent scarcity create value.
- Do not judge a palette from five square swatches only; test it on real components.
- Build with roles, not color names: `text.secondary`, not `gray-500` inside component logic.
- A successful palette survives content changes, hover states, disabled states, charts, empty states, and error states.
