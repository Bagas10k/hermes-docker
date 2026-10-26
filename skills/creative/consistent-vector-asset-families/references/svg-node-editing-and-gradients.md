# SVG Node Editing, Anchor Points, and Gradient Layers

This reference provides rules for structuring SVG code so it remains 100% editable by designers in vector tools (Figma, Illustrator, Inkscape, Penpot) rather than acting as flat rasterized shapes.

---

## 1. Clean Bézier Topology vs Auto-Traced Slop

A major defect in generative vector tools is auto-tracing bitmaps into thousands of jagged microscopic polylines. Editable SVGs require deliberate spline topology:

1. **Node Budget:** Keep major anatomical parts under 12–24 anchor points.
2. **Smooth Tangent Handles:** When two curves meet smoothly, ensure control handles share an angle ($\theta_1 = \theta_2 \pm 180^\circ$) to avoid accidental kinks.
3. **Semantic Grouping:** Structure each asset into logical `<g>` elements:
   - `<g id="contact-shadow">`: Grounding shadow ellipses.
   - `<g id="chassis-or-base">`: Structural foundation.
   - `<g id="metal-accents">`: High-contrast metallic chrome trims.
   - `<g id="glass-elements">`: Translucent shells.
   - `<g id="specular-highlights">`: Sharp white glare shapes.

---

## 2. Gradient Layering Architecture

To create the illusion of ray-traced 3D depth inside flat 2D vector code:

```
[Layer 4: Specular Glares]   <path fill="url(#sharpGlare)" opacity="0.9" />
           ▲
[Layer 3: Glass Housing]     <path fill="url(#glassGrad)" stroke="url(#glassRim)" />
           ▲
[Layer 2: Core Metallic]     <path fill="url(#roseGoldMetal)" />
           ▲
[Layer 1: Occlusion Base]    <path fill="#5A2319" opacity="0.6" />
           ▲
[Layer 0: Contact Shadow]    <ellipse fill="url(#contactShadow)" />
```

---

## 3. Anchor Node Manipulation Guidelines

When adjusting curves via code or GUI:
- Use relative cubic Bézier commands (`c dx1 dy1, dx2 dy2, dx dy`) for modular, scalable sub-components.
- Use explicit coordinates (`M x y C x1 y1, x2 y2, x y`) for the primary silhouette to allow deterministic bounding box calculations.
- Maintain consistent stroke-width ratios when scaling: always declare `vector-effect="non-scaling-stroke"` if strokes must preserve visual weight across different viewports.
