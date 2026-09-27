# Accessibility and Color Quality

## Contents
1. WCAG contrast
2. Do not rely on color alone
3. Color-vision differences
4. Focus and interactive controls
5. Text over images/gradients
6. Quality audit

## 1. WCAG contrast

Use WCAG 2.2 contrast rules as the default baseline for digital UI unless the user specifies another standard.

For normal text, target at least **4.5:1** against its background for Level AA.
For large-scale text, target at least **3:1**.
Enhanced contrast targets are **7:1** for normal text and **4.5:1** for large text.

Calculate contrast from relative luminance; do not estimate numerically by sight. Use `scripts/color_tools.py` for HEX pairs.

Note: visual attractiveness does not override readability. When a brand color fails as text or button foreground/background, create an accessible functional variant instead of forcing the original swatch into that role.

## 2. Do not rely on color alone

Important meaning needs another cue. Examples:
- error: red + icon + message;
- success: green + checkmark + text;
- selected tab: color + indicator/shape/weight;
- chart category: color + label/pattern/marker;
- HMI alarm: color + symbol + status text + alarm state.

## 3. Color-vision differences

Avoid critical red-vs-green-only, blue-vs-purple-only, or other low-separation distinctions. Add luminance differences and non-color cues.

For charts, test whether categories remain distinguishable when hue discrimination is reduced. Direct labeling is often stronger than a large legend.

## 4. Focus and interactive controls

Focus-visible styling must be clearly perceivable against adjacent colors. A focus ring that disappears on either a light or dark surface is not robust.

Check interactive boundaries and selected states, not just text contrast.

## 5. Text over images/gradients

Contrast can vary across the image. Fix using one or more of:
- localized scrim;
- solid text plate;
- gradient overlay;
- text relocation;
- image crop control;
- alternate image treatment.

Test the lowest-contrast area under the text.

## 6. Quality audit

### Hierarchy
- Is primary text visually dominant over secondary text?
- Is the main action clearer than secondary actions?
- Are accents scarce enough to mean something?

### Readability
- Are text/background pairs sufficient?
- Is muted text still readable?
- Are disabled states understandable without becoming invisible?

### Semantics
- Are success/warning/danger/info clearly differentiated?
- Are state meanings consistent across components?
- Is color reinforced by another cue when meaning is critical?

### Cohesion
- Do neutrals share a coherent temperature?
- Are chroma levels intentional?
- Do gradients and shadows fit the same visual world?

### Scalability
- Can the palette handle hover, active, focus, selection, disabled, charts, empty states, errors, and dark mode?
- Are components using semantic tokens instead of raw values?

### Stress tests
- View in grayscale.
- Shrink the design.
- Inspect under bright and dim conditions.
- Test real content, long labels, error states, and dense screens.
- Check the palette on at least one worst-case screen, not only the hero screen.
