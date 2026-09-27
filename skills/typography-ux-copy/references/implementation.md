# Typography Implementation

## Contents
1. Design tokens
2. CSS
3. Fluid type
4. Tailwind
5. Font loading
6. Variable fonts
7. Localization-safe components

## 1. Design tokens

Prefer semantic tokens.

```json
{
  "font": {
    "family": {
      "sans": "Inter, ui-sans-serif, system-ui, sans-serif",
      "mono": "ui-monospace, SFMono-Regular, Menlo, monospace"
    },
    "size": {
      "body": "1rem",
      "label": "0.875rem",
      "h2": "1.75rem"
    },
    "lineHeight": {
      "body": "1.5",
      "heading": "1.2"
    }
  }
}
```

Use separate semantic alias tokens if the system has a mature primitive/token architecture.

## 2. CSS

Example:

```css
:root {
  --font-sans: Inter, ui-sans-serif, system-ui, sans-serif;
  --text-body-size: 1rem;
  --text-body-line: 1.5;
  --text-label-size: 0.875rem;
  --text-h1-size: clamp(2rem, 1.35rem + 2.6vw, 3.75rem);
  --text-h1-line: 1.05;
}

body {
  font-family: var(--font-sans);
  font-size: var(--text-body-size);
  line-height: var(--text-body-line);
}
```

Avoid fixed heights on components containing copy that can wrap.

## 3. Fluid type

Use `clamp()` for roles that benefit from viewport-sensitive scaling, typically display and large headings.

Do not fluid-scale every control label. Small UI text should remain stable and predictable.

## 4. Tailwind

Map semantic roles through theme variables or component classes rather than scattering arbitrary values.

Example concept:

```css
@theme {
  --font-sans: "Inter", ui-sans-serif, system-ui, sans-serif;
  --text-body: 1rem;
  --text-label: 0.875rem;
}
```

For a mature design system, create semantic utility/component abstractions such as `.type-body`, `.type-label`, and `.type-page-title`.

## 5. Font loading

For web:
- subset only when language coverage remains sufficient
- preload only critical font files
- use modern compressed formats such as WOFF2
- define robust fallbacks
- manage font-display behavior intentionally
- avoid loading many unused weights

Check layout shift when fallback metrics differ greatly from the final font.

## 6. Variable fonts

A variable font can reduce multiple static files and enable optical axes. Only load/use axes that provide value.

## 7. Localization-safe components

Use:
- min-height rather than fixed height where text can wrap
- flex/grid layouts that tolerate expansion
- logical CSS properties for RTL support
- buttons that can widen or wrap where platform conventions allow
- tooltips or full-value views for intentionally truncated data

Avoid concatenating translated fragments such as:
`"Delete " + itemName + " permanently"`
Use complete localizable strings with placeholders.
