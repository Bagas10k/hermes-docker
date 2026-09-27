# Reference-Based Color Adaptation

## Contents
1. Goal
2. Analyze before extracting
3. Reference color fingerprint
4. Mapping to a new design
5. What to copy vs not copy
6. Image-heavy references
7. Multi-reference synthesis
8. Validation

## 1. Goal

The goal is not pixel-level imitation. The goal is to understand what color relationships create the reference's character and rebuild those relationships for the target design.

## 2. Analyze before extracting

Before sampling colors, answer:
- What occupies the largest area?
- Where is the brightest region?
- Where is the darkest region?
- What is the strongest accent?
- Is the palette warm, cool, mixed, or neutral?
- How saturated is the overall composition?
- Are surfaces separated by tone, border, shadow, or hue?
- How often does the accent appear?
- Does the design use one accent or several?
- Are gradients, transparency, blur, glow, or imagery affecting perceived color?

## 3. Reference color fingerprint

Represent the source with a compact fingerprint:

- **Neutral temperature**: warm / cool / balanced
- **Canvas lightness**: very light / light / mid / dark / near-black
- **Surface delta**: subtle / medium / strong
- **Text contrast**: soft / standard / stark
- **Primary hue family**: description
- **Accent hue family**: description
- **Chroma ceiling**: low / medium / high
- **Accent ratio**: rare / moderate / frequent
- **Semantic strategy**: muted / conventional / vivid / monochrome + labels
- **Effects**: flat / gradient / glass / glow / material / image-driven

This fingerprint is often more transferable than raw swatches.

## 4. Mapping to a new design

Map source roles to target roles:

`reference canvas` → `target bg.canvas`
`reference card` → `target bg.surface`
`reference heading` → `target text.primary`
`reference CTA` → `target action.primary`
`reference highlight` → `target accent`

Then adapt for:
- target content density;
- platform size;
- brand constraints;
- accessibility;
- new semantic states;
- light/dark mode;
- different imagery.

## 5. What to copy vs not copy

Usually worth preserving:
- tonal hierarchy;
- neutral temperature;
- accent scarcity;
- chroma rhythm;
- contrast mood;
- gradient character;
- warm/cool balance.

Usually unsafe to copy blindly:
- exact background values when target content is denser;
- text colors that fail readability;
- screenshot compression artifacts;
- colors produced by image overlays rather than actual tokens;
- brand-specific identity colors when creating a distinct brand;
- semantic colors that have no matching meaning in the target product.

## 6. Image-heavy references

If the reference contains photography/illustration:
- separate image palette from UI palette;
- identify whether UI colors harmonize with, neutralize, or contrast the imagery;
- sample representative regions, not random pixels;
- account for overlays and color grading;
- create stable UI tokens that still work when imagery changes.

## 7. Multi-reference synthesis

When multiple references are supplied, assign each one a role:
- layout reference;
- color/mood reference;
- component/state reference;
- typography reference.

Do not average all references into a generic result. Extract the relevant design law from each.

## 8. Validation

A successful adaptation should answer yes to most of these:
- Does it evoke the source without looking copied?
- Does the accent occupy a similar visual weight?
- Is the tonal hierarchy preserved?
- Does it work with the target content?
- Are interactions/states more complete than the static reference?
- Did accessibility repairs preserve the intended vibe?
