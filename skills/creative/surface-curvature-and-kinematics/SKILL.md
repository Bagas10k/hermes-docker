---
name: surface-curvature-and-kinematics
description: Use when smoothing UI curvature and kinematics.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [curvature, squircle, g2-continuity, concentric-radius, lerp-physics, specular-lighting, ui-craft]
    related_skills: [bento-grid-spatial-composer, color-intelligence, ui-layout-intelligence]
---

# Surface Curvature & Kinematics Engine

Achieve apex-tier smoothness in digital surfaces by eliminating G1 circular arc discontinuities, optical pinching, jagged borders, and jerky pointer tracking.

## When to Use
- User asks for high-craft UI/UX, spatial dashboards, bento grids, glassmorphism, or tactile cards.
- User critiques UI smoothness or rates previous designs low due to stiff corners, awkward nesting, or abrupt motion.
- Designing elevated cards, modals, or floating controls that need molded acrylic or crystal depth.
- Implementing interactive tilt, parallax, magnetic buttons, or cursor-follow atmospheric lighting.

## Core Procedures & Mathematical Formulations

### 1. G2 Squircle Curvature Continuity
Standard CSS `border-radius: 12px` creates a circular arc meeting a straight line. At the tangent point, curvature jumps instantaneously from $0$ to $1/R$ (G1 tangent continuity, G2 curvature discontinuity). The human visual cortex detects this as an unnatural, harsh corner shoulder ("knick").

- **Continuous Transition Standard**:
  Use generous squircle radii (`24px - 32px` for outer cards, `14px - 20px` for inner modules, `9999px` for pills) paired with cubic-bezier transition shoulders.
- **CSS Smoothing Strategy**:
  When SVG clip-path squircles are impractical, combine `border-radius: clamp(20px, 2.5vw, 32px)` with subtle sub-pixel rim highlights that feather curvature edges.

### 2. Concentric Nested Radius Equation
Never assign arbitrary border-radii to child elements inside rounded parent containers. When the gap between container curves and child curves varies, it creates an optical pinching defect.

- **Strict Concentric Rule**:
  $$R_{\text{inner}} = \max(0, R_{\text{outer}} - \text{padding})$$
- **Example**:
  If a parent card has `padding: 16px` and `border-radius: 28px`:
  $$R_{\text{inner}} = 28\text{px} - 16\text{px} = 12\text{px}$$
- If child padding exceeds outer radius, set $R_{\text{inner}} = 0$ or small squircle ($4\text{px}-6\text{px}$) to prevent inverted curves.

### 3. Molded Acrylic & Specular Rim Lighting
Harsh solid strokes (`border: 1px solid rgba(...)`) reveal pixel stepping along curved shoulders. Replace them with layered specular rims:

```css
/* Molded Crystal / Frosted Glass Depth Token */
box-shadow:
  inset 0 1px 1px 0 rgba(255, 255, 255, 0.28),   /* Top specular light reflection */
  inset 0 0 0 1px rgba(255, 255, 255, 0.04),       /* Soft sub-pixel perimeter stroke */
  0 20px 50px -10px rgba(0, 0, 0, 0.50);          /* Diffused ambient drop shadow */
```

### 4. Continuous LERP Inertia Loop (60–120 FPS)
Never mutate transform styles directly inside a `pointermove` event listener. Raw mouse event polling rates do not align with monitor refresh cycles (VSync), causing micro-stutter and snapping when the pointer leaves the card.

- **Inertia Kinematics Implementation**:
  Decouple input sampling from render execution using a continuous `requestAnimationFrame` loop with Linear Interpolation (LERP):
  $$V_{\text{current}} \leftarrow V_{\text{current}} + (V_{\text{target}} - V_{\text{current}}) \times \alpha$$
  Set damping factor $\alpha \in [0.06, 0.08]$ for liquid silk motion, or $[0.10, 0.14]$ for snappy responsiveness.
- **Spring Decay on Pointer Exit**:
  On `pointerleave`, smoothly glide target coordinates back to `(0, 0)` so cards coast into equilibrium rather than snapping abruptly.

See `references/concentric-and-kinematics-cheatsheet.md` for precomputed concentric radius pairings and a reusable DampedSurfacePhysics class.

## Pitfalls & Hard Constraints
- **Zero Raw Event DOM Writes**: Direct DOM mutations on `pointermove` cause dropped frames under high pointer polling rates (1000Hz gaming mice). Store normalized target coordinates in memory and interpolate inside RAF.
- **Zero Nested Interactive Controls in Clickable Cards**: Placing `<button>` or `<a>` inside `<div role="button">` causes critical Axe-core WCAG AA `nested-interactive` failures. Badges inside clickable cards must be semantic `<span>` with layout styling.
- **Sticky Header Clearance**: When sticky navigation bars (`position: sticky; top: 0`) exist, automated tests or hash links will trigger click interception unless interactive targets declare `scroll-margin-top: 100px`.
- **Permanent Accessible Names**: Responsive styles that hide text on narrow viewports (`display: none`) strip the element's accessible name. Always bind explicit `aria-label` to icon buttons and segmented mode switchers.
