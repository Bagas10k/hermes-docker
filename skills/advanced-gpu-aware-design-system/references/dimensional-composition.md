# Dimensional composition: learn structure, not a template

Use `visual-reference-decompiler` before implementing from a reference. Then apply layout, typography, color, and design-QA skills. A user-supplied reference overrides an older default palette or visual template, without overriding functionality, security, or accessibility.

## Two useful modes, not a restriction to two styles

- **Tactile/editorial 2.5D:** product/story-led interfaces with an asymmetric typographic anchor, meaningful staggered cards, crisp outlines, directional offset shadows, restrained rotations, and optional SVG process connectors. Native HTML/CSS/SVG often suffices.
- **Spatial/isometric overview:** relationships, locations, topology, or flow where depth clarifies the model. Prefer an SVG illustration or a few CSS layers; use programmable graphics only when its capabilities are required.

Neither mode mandates a color scheme, universal hero ratio, fixed card angle, or a 3D scene on every page. Keep tables, forms, essential controls, and operative numbers straightforward to read.

## Inspected case: https://www.ailene.id/

Observed 2026-10-20 WIB using a real browser, DOM measurements, desktop/mobile screenshots, and visual inspection. This is reference analysis, not a cloned theme or a statement about all routes.

**Observed composition:** forest-green hero, off-white surfaces and lime accents; large stacked heading with a highlighted phrase; orthogonal low-contrast grid; four slightly rotated mini-interface cards with hard offset shadows and connectors tracing a learning sequence. Cards explain product stages, rather than being unrelated decorative blocks.

**Measured state:** at a 1440x1000 viewport, repeated content width was 1180 CSS pixels, h1 computed size64px/weight800, first section height about950px. At390x844, document horizontal overflow was false and first section height about1862px. These are single-state observations, not recommended token values or universal breakpoints. No canvas was observed in that rendered DOM; the visible depth does not establish a need for WebGL/WebGPU.

**Uncertainty:** one desktop capture contained the right-hand cards while primary text was not readable; DOM text existed with per-character transforms. A later mobile capture showed the heading. This does not establish a persistent defect or its cause. It motivates testing essential text before/during/after hydration and entrance motion. Mobile capture also showed substantial vertical whitespace and a floating control overlapping part of a card; don't inherit those tradeoffs blindly.

Do not copy logos, mascots, slogans, screenshots, course/business data, or a brand palette as an automatic preset. Use neutral synthetic content for examples, visibly labeled as demonstration data.

## Decompile before writing CSS

Record six concrete decisions:
1. **Hierarchy:** the user's first task, dominant message, primary action, and supporting content.
2. **Proportion:** content max-width, column balance, readable line length, whitespace, and first-viewport priorities. Measure rather than guessing exact values from memory.
3. **Silhouette:** foreground/background grouping and asymmetry; consistent card scale prevents arbitrary scatter.
4. **Depth:** shadow direction, occlusion, edge contrast, rotation, and elevation. One coherent light/shadow model is better than independent effects everywhere.
5. **Meaning:** what each card, route, or object represents; how it maps to a real task/detail. Remove objects with no communicative role.
6. **Behavior:** pointer, keyboard, touch, resize, reduced motion, and fallback. A reference image does not prove these work.

Adapt the grammar to the target product; do not replace a generic SaaS grid with a generic tilted-card grid.

## Minimal tactile CSS pattern

This illustrates a material treatment, not a runnable product or a promise of performance:

```css
.tactile-card {
  border: 1px solid var(--outline);
  border-radius: var(--radius);
  background: var(--surface);
  box-shadow: 5px 5px 0 var(--shadow);
  transform: rotate(var(--tilt, 0deg));
  transition: transform 180ms ease;
}
@media (hover: hover) and (prefers-reduced-motion: no-preference) {
  .tactile-card:hover {
    transform: rotate(var(--tilt, 0deg)) translateY(-3px);
  }
}
@media (max-width: 48rem) {
  .tactile-card { transform: none; }
}
@media (prefers-reduced-motion: reduce) {
  .tactile-card { transition: none; }
}
```

Define tokens from the project's palette, verify contrast, use small content-appropriate tilts, and prefer a normal flow/grid on mobile. Keep connectors decorative and behind controls. Do not animate box-shadow merely to make depth noticeable; profile paint costs if necessary. Static shadows are not automatically a performance problem.

## Improvement gates

- Heading and primary action are visible before enhancement, with JS disabled, during entrance effects, and under reduced motion.
- Mobile sections are content-driven; don't require long empty scroll to reach essential content.
- Floating controls reserve their actual size plus safe-area clearance; no fixed80px value is universally sufficient.
- Mini-interface labels remain readable; provide semantic text equivalents rather than baking important data into perspective art.
- Depth supports meaning; negative constraints remain no emoji UI, no rainbow/neon-gradient text, no ornamental kicker clutter, and neutral synthetic dummy content only.
- Exercise controls and inspect actual screenshots. A convincing reference and a technical smoke PASS are neither visual approval nor proof of usability.
