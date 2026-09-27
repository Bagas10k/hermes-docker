# Typography and Copy Reference Analysis

## Contents
1. Analyze, do not imitate
2. Typography extraction
3. Copy pattern extraction
4. Reconstruct semantic roles
5. Adapt to a new product
6. Confidence and uncertainty

## 1. Analyze, do not imitate

A screenshot shows outcomes, not the original design tokens. Infer the system.

Do not copy an exact font family, font size, or line-height unless metadata or source code confirms it.

## 2. Typography extraction

Inspect:
- serif/sans/mono/display category
- apparent x-height and density
- relative size ratios
- number of weights
- heading/body contrast
- line-height tightness
- letter spacing
- use of uppercase
- numerical treatment
- text color hierarchy
- alignment
- maximum text width

Map each visible text block to a semantic role.

## 3. Copy pattern extraction

Inspect:
- button grammar
- heading style
- sentence case/title case
- tone
- pronouns
- helper text density
- error style
- empty-state style
- whether descriptions focus on features or outcomes
- terminology consistency

Do not assume the reference's copy is good. Evaluate it.

## 4. Reconstruct semantic roles

Example inference:

Reference appears to use:
- Display: expressive brand face, very large, tight leading
- H1/H2: same family, Semibold
- Body: neutral sans, regular, generous leading
- Label: neutral sans, Medium, compact
- Caption: same body face, lower contrast

Rebuild equivalent roles for the target platform and language.

## 5. Adapt to a new product

Preserve useful principles, not literal values.

Example:
A luxury editorial reference may use large serif display text and tiny labels. For a financial dashboard, preserve the restrained hierarchy and premium whitespace, but replace fragile small labels with legible product UI typography.

## 6. Confidence and uncertainty

When estimating from screenshots, use language such as:
- likely
- approximately
- appears to use
- visually close to

If exact implementation matters, inspect source styles, design tokens, or Figma values when available.
