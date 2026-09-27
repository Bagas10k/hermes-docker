# UI Color Systems

## Contents
1. Role-based architecture
2. Neutral systems
3. Brand/action systems
4. Semantic states
5. Interaction states
6. Light mode
7. Dark mode
8. Gradients and transparency
9. Data visualization
10. HMI/SCADA
11. Common system failures

## 1. Role-based architecture

Separate **primitive palette tokens** from **semantic tokens**.

Primitive example:
- `blue.50 ... blue.950`
- `slate.50 ... slate.950`

Semantic example:
- `bg.canvas`
- `bg.surface`
- `text.primary`
- `action.primary.bg`
- `status.danger.text`

Components should consume semantic tokens so themes can change without rewriting component logic.

## 2. Neutral systems

Neutrals usually carry most interface area. Design them intentionally.

Control:
- temperature;
- spacing between lightness steps;
- whether borders are warm/cool/neutral;
- contrast between canvas and surfaces;
- readability of secondary/muted text.

Avoid using a single flat gray for text, border, disabled, and backgrounds.

## 3. Brand/action systems

The primary family should support:
- default action;
- hover;
- active/pressed;
- subtle/tinted surface;
- selected state;
- focus treatment if appropriate;
- readable text/icon pairing.

A logo color is not automatically a good button color. Create functional variants.

## 4. Semantic states

Typical families:
- success;
- warning;
- danger/error;
- info.

Each may need:
- solid background;
- subtle background;
- border;
- icon;
- text.

Do not use semantic colors decoratively if that will weaken their meaning.

## 5. Interaction states

Every actionable color should define behavior for:
- default;
- hover;
- active/pressed;
- focus-visible;
- selected/toggled;
- disabled;
- loading, if relevant.

State differences can use lightness, border, outline, elevation, and shape—not only hue shifts.

## 6. Light mode

Typical design logic:
- bright canvas with slightly differentiated surfaces;
- dark text with a clear primary/secondary hierarchy;
- borders subtle but visible;
- large colored surfaces use moderated chroma;
- selected regions can use pale chromatic tints.

Avoid excessive `#ffffff` blocks separated only by shadows.

## 7. Dark mode

Dark mode is a separate perceptual system.

Guidelines:
- avoid pure black as the automatic canvas; near-black can preserve depth and reduce harsh contrast;
- avoid pure white for all text; slightly softened high-lightness text can reduce glare while remaining readable;
- elevated surfaces often become lighter than the canvas rather than darker;
- saturated brand colors may need reduced chroma or increased lightness to avoid glowing/vibrating;
- borders may need more tonal separation because shadows are less informative;
- check images, charts, semantic colors, focus rings, and disabled states independently.

Do not create dark mode by simply swapping white and black.

## 8. Gradients and transparency

Use gradients when they serve identity, depth, focus, or data meaning.

Good gradient behavior:
- compatible endpoint lightness;
- controlled chroma;
- no dirty midpoint caused by naïve interpolation;
- text placed only where contrast remains stable;
- direction supports composition.

Use overlays/scrims when text sits over imagery. Test the worst-case background region, not only the average image.

## 9. Data visualization

Choose palette by data type:
- **categorical**: distinct hues with comparable visual weight;
- **sequential**: ordered lightness/chroma progression;
- **diverging**: two directions around a meaningful midpoint;
- **status**: semantic meaning with non-color cues.

Avoid too many categorical colors. Add labels, patterns, direct annotations, or grouping when categories exceed reliable color discrimination.

## 10. HMI/SCADA

For operational displays:
- keep normal operation visually calm;
- reserve high-salience color for alarms, abnormal states, and required action;
- use consistent meanings for red/yellow/green or any status family;
- do not depend on color alone—include text, symbol, shape, pattern, or state label;
- avoid decorative gradients/3D effects that reduce scanability;
- maintain readable contrast for long-duration monitoring.

## 11. Common system failures

- too many primitive steps but no semantic architecture;
- every component has custom hex values;
- primary color appears everywhere, destroying emphasis;
- secondary text is too faint;
- hover/active differences are imperceptible;
- disabled controls are indistinguishable from inactive decoration;
- semantic colors clash with brand colors;
- dark theme inherits light-theme saturation unchanged;
- charts use colors that collapse in grayscale or color-vision deficiencies.
