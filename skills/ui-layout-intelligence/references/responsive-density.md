# Responsive Layout and Density

## 1. Responsive means relational adaptation

Do not merely scale the desktop layout down. At each meaningful width consider:

- column count;
- pane stacking;
- page margin;
- component padding;
- content priority;
- control wrapping;
- navigation mode;
- reading line length;
- touch reach.

## 2. Suggested density modes

### Compact
Use for expert desktop tools, data tables, monitoring, administration.

Characteristics:

- smaller component gaps;
- reduced panel padding;
- high information density;
- stable alignment;
- interaction targets remain usable.

### Standard
Use for broad productivity and general-purpose interfaces.

Balance scanning efficiency with breathing room.

### Comfortable
Use for touch-first consumer interfaces, onboarding, learning, and low-density workflows.

Use larger vertical rhythm and touch-friendly controls.

## 3. Fluid spacing

Use fluid spacing only when it improves continuity across widths. CSS example:

```css
.page {
  padding-inline: clamp(16px, 4vw, 48px);
}

.section {
  padding-block: clamp(32px, 6vw, 80px);
}
```

Do not use `clamp()` everywhere. Stable component internals often benefit from discrete tokens while page-scale whitespace can be fluid.

## 4. Mobile

Prioritize:

- safe edge insets;
- touch targets;
- reduced side-by-side competition;
- predictable vertical flow;
- enough spacing around sticky/floating controls.

## 5. Desktop

Use the extra width to improve hierarchy, not merely stretch content. Consider max-widths, multiple panes, aligned side content, or denser data presentation.

## 6. Localization

Design for text expansion. Avoid fixed-width buttons or tight inline groups that only fit the original language. Prefer logical properties for RTL:

- `margin-inline-start`
- `padding-inline`
- `inset-inline-end`

instead of assuming left/right semantics.
