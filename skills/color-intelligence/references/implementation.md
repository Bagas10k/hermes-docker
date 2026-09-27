# Color Implementation and Handoff

## Contents
1. Choosing formats
2. Token architecture
3. CSS variables
4. Tailwind mapping
5. JSON tokens
6. OKLCH strategy
7. Naming
8. Handoff checklist

## 1. Choosing formats

- **HEX**: concise, common handoff, sRGB.
- **RGB/RGBA**: useful for programmatic opacity or legacy APIs.
- **HSL**: intuitive manual adjustments but not perceptually uniform.
- **OKLCH**: useful for perceptually controlled modern palette generation.

When compatibility matters, provide HEX fallback even if OKLCH is the design source.

## 2. Token architecture

Use two layers when the system is non-trivial.

### Primitive
```text
neutral.50
neutral.100
...
brand.500
brand.600
red.500
```

### Semantic
```text
bg.canvas
bg.surface
text.primary
text.secondary
border.default
action.primary.bg
action.primary.text
action.primary.hover
status.danger.bg
status.danger.text
```

Do not bind components directly to `brand.600` unless the project intentionally has a tiny system.

## 3. CSS variables

Example:
```css
:root {
  --bg-canvas: #f8fafc;
  --bg-surface: #ffffff;
  --text-primary: #0f172a;
  --text-secondary: #475569;
  --border-default: #cbd5e1;
  --action-primary: #2563eb;
  --action-primary-hover: #1d4ed8;
  --action-primary-text: #ffffff;
}

[data-theme="dark"] {
  --bg-canvas: #0f172a;
  --bg-surface: #111827;
  --text-primary: #f8fafc;
  --text-secondary: #cbd5e1;
  --border-default: #334155;
}
```

These are examples of structure, not universal palette recommendations.

## 4. Tailwind mapping

Map semantic variables into the Tailwind theme or use CSS variables inside utility classes. Prefer semantic naming at the component boundary.

Example concept:
```js
colors: {
  canvas: 'var(--bg-canvas)',
  surface: 'var(--bg-surface)',
  primary: 'var(--action-primary)',
}
```

## 5. JSON tokens

Example:
```json
{
  "color": {
    "bg": {
      "canvas": { "value": "#f8fafc" },
      "surface": { "value": "#ffffff" }
    },
    "text": {
      "primary": { "value": "#0f172a" },
      "secondary": { "value": "#475569" }
    }
  }
}
```

If the consumer follows a specific design-token schema, match that schema instead of forcing this example.

## 6. OKLCH strategy

For a base color, vary perceptual lightness deliberately and adjust chroma so extreme light/dark steps do not look fluorescent or muddy.

Example source form:
```css
--brand-500: oklch(62% 0.18 255);
```

Use actual visual testing and gamut checks. Do not assume every high-chroma OKLCH value is representable in every output gamut.

## 7. Naming

Good semantic names describe purpose:
- `text.muted`
- `border.strong`
- `surface.selected`
- `status.warning`

Avoid names that encode appearance into semantics:
- `blue-button`
- `light-gray-text`
- `red-card`

Those names break when themes change.

## 8. Handoff checklist

Deliver what the implementer needs:
- primitive palette if used;
- semantic mapping;
- state mapping;
- light/dark theme mapping;
- contrast notes for critical pairs;
- opacity/overlay values;
- gradient definitions;
- chart palette if relevant;
- exact output format (CSS/Tailwind/JSON/Figma naming convention) requested by the user.
