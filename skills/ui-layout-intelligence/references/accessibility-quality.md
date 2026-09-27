# Accessibility and Quality Checks

## Pointer target size

WCAG 2.2 Success Criterion 2.5.8 (Level AA) requires pointer targets to be at least 24 x 24 CSS pixels, with defined exceptions including sufficient spacing for undersized targets.

WCAG 2.2 Success Criterion 2.5.5 (Level AAA) uses 44 x 44 CSS pixels for enhanced target size, with exceptions.

Do not interpret these as a reason to make every visible icon 44px. The hit area can be larger than the visible glyph.

Apple's current Human Interface Guidelines generally call for at least a 44 x 44 pt hit region for buttons on iOS/iPadOS and emphasize sufficient space between controls.

## Quality checklist

Before accepting a layout, verify:

- page edge spacing is intentional;
- repeated components have consistent internal padding;
- sibling spacing is owned by the parent where possible;
- no accidental double-spacing from margin + gap;
- hierarchy is visible without relying entirely on borders;
- interactive hit areas are adequate;
- neighboring targets are not too easy to activate accidentally;
- keyboard focus is not clipped by overflow or tight containers;
- 200% zoom/reflow does not cause overlap or loss of content;
- text expansion does not destroy button/action layouts;
- RTL uses logical positioning where feasible;
- sticky bars respect safe areas and do not cover content;
- compact mode does not erase semantic grouping;
- large whitespace does not push essential information unnecessarily far apart.

## Touch vs visible geometry

A 20px icon can live inside a 44px or larger interactive region. Keep visual density separate from motor accessibility.

## Spacing as accessibility

Spacing helps users distinguish controls, scan groups, and avoid accidental activation. Accessibility is not only a minimum target-size checkbox; the surrounding spatial system also matters.
