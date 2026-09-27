# Implementation Patterns

## CSS tokens

```css
:root {
  --space-0: 0;
  --space-1: 0.25rem; /* 4px */
  --space-2: 0.5rem;  /* 8px */
  --space-3: 0.75rem; /* 12px */
  --space-4: 1rem;    /* 16px */
  --space-5: 1.25rem; /* 20px */
  --space-6: 1.5rem;  /* 24px */
  --space-8: 2rem;    /* 32px */
  --space-10: 2.5rem; /* 40px */
  --space-12: 3rem;   /* 48px */
  --space-16: 4rem;   /* 64px */
}
```

## Prefer gap for stacks

```css
.form-stack {
  display: grid;
  gap: var(--space-4);
}
```

Instead of giving every child an unrelated `margin-bottom`.

## Logical properties

```css
.card {
  padding-block: var(--space-6);
  padding-inline: var(--space-6);
}

.back-link {
  margin-inline-end: var(--space-2);
}
```

## Responsive page margin

```css
.page-shell {
  width: min(100% - 2 * 16px, 1200px);
  margin-inline: auto;
}

@media (min-width: 768px) {
  .page-shell {
    width: min(100% - 2 * 32px, 1200px);
  }
}
```

## Fluid section spacing

```css
.section {
  padding-block: clamp(32px, 5vw, 72px);
}
```

Use fluid values for large-scale composition only when useful; component internals often remain tokenized and discrete.

## Tailwind

Use the framework scale consistently:

```html
<div class="mx-auto max-w-7xl px-4 md:px-8">
  <section class="py-8 md:py-12 lg:py-16">
    <div class="grid gap-6 lg:grid-cols-3">
      ...
    </div>
  </section>
</div>
```

Avoid excessive arbitrary values such as `gap-[13px]`, `px-[19px]`, and `mt-[27px]` unless a deliberate optical or legacy constraint exists.

Tailwind's current spacing utilities are driven by a shared spacing theme variable, so a project can customize the scale centrally.

## Design token JSON example

```json
{
  "spacing": {
    "primitive": {
      "1": "4px",
      "2": "8px",
      "3": "12px",
      "4": "16px",
      "6": "24px",
      "8": "32px",
      "12": "48px",
      "16": "64px"
    },
    "semantic": {
      "page-inline": "{spacing.primitive.6}",
      "card-padding": "{spacing.primitive.6}",
      "control-gap": "{spacing.primitive.3}",
      "section-gap": "{spacing.primitive.12}"
    }
  }
}
```
