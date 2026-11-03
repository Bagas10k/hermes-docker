---
name: animated-vector-icons
description: Create animated SVG vector icons with CSS spring physics.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [SVG, VectorAnimation, MicroInteractions, MotionDesign, CSSKeyframes, 60fps]
    related_skills: [universal-icon-morphing, procedural-vector-graphics, upnormal-ui-architecture, living-editorial-diorama]
---

# Animated SVG Vector Icons Studio

Build resolution-independent animated SVG icons with measured export size and deliberate micro-interactions. Prefer SVG/CSS for compact web icons; select Lottie or another format when the brief or animation requires it. Measure the self-contained export, including required CSS/JS, before making a size claim.

## When to Use

- "buatkan icon animasi SVG (eye, menu, bell, basketball, sun-moon, dll)"
- "rancang animasi micro-interaction vektor murni tanpa library berat / video"
- "buatkan aset SVG interaktif yang merespons hover, click, atau mouse tracking"
- "terapkan prinsip animasi fisik (squash & stretch, orthographic 3D spin, pendulum inertia)"

## Core Architecture Principles

1. **Self-contained vector export:** For SVG delivery, include its styles, keyframes, namespace, unique IDs and required interaction code. Extracting only `outerHTML` from a page does not copy external animation CSS. Exercise the copied/downloaded result in an isolated document before describing it as ready to embed; raw SVG is not automatically valid JSX.
2. **Explicit physical anchors:** Pin CSS transforms to the intended SVG pivot and group parts that move together; define `transform-box` deliberately. XML `rotate(angle cx cy)` already has an explicit pivot and is not invalid merely because CSS `transform-origin` is absent. Measure attachment points in initial, intermediate, and final states, not only full-size state.
3. **Measured motion quality:** Prefer transform/opacity when suitable, but do not guarantee GPU backing or60 FPS from the property names. Path morph/draw may legitimately update geometry. Distinguish physical simulation from hand-authored easing; CSS cubic-bezier is not proof of a spring solver.
4. **Intentional interaction:** Provide finite click/hover/focus state changes and reduced-motion handling; idle loops are optional, not mandatory. Pause animation offscreen or in hidden documents. Use semantic controls with keyboard activation and `aria-pressed` for toggles. Keep animation triggers separate from code inspection/copy controls so a modal does not obscure the very interaction being demonstrated.
5. **Reference evidence:** A screenshot proves shape/composition only. Inspect video frames or the actual interactive source before asserting blinking, cursor tracking, collision physics, motion direction, size, or performance; do not turn a vision model's enthusiastic description into test evidence.

## Essential Animation Formulas

### 1. Organic Eye Tracking & Eyelid Blink
- **Blink Keyframes:** Eyelids stay fully open (100% scaleY) for 94% of the cycle, swiftly compressing to 8% scaleY at 97%, and opening again by 100%.
- **Pupil Pointer Delta:** Calculate normalized mouse offset from card center:
  $$\Delta x = \frac{x-x_{\text{center}}}{W}\,\text{range}_x, \quad \Delta y = \frac{y-y_{\text{center}}}{H}\,\text{range}_y$$
  Equivalently use `(pointerX - rect.left)/rect.width - 0.5`; do not subtract0.5 again after already subtracting the center. Clamp movement inside the iris mask, move pupil/highlight together, and reset on pointer leave. Avoid a hover keyframe animation overriding the same transform used by tracking.

### 2. Squash & Stretch Bounce (Basketball / Ball Physics)
- **Falling vs Impact Timing:**
  - Fall: `translateY(-16px) scale(0.94, 1.06)` (elongated stretch).
  - Ground Impact: `translateY(12px) scale(1.18, 0.82)` (horizontal compression).
  - Rebound: Spring curve `cubic-bezier(0.28, 0.84, 0.42, 1)`.
- **Contact Shadow Scaling:** Ground ellipse expands (`scale(1.2)`) and darkens at contact, shrinking (`scale(0.5)`) and fading at peak altitude.

### 3. Planar Seam Rotation (Tennis Ball / Globe)
- A fixed sphere outline with rotating inner paths gives a flat in-plane spin, not an orthographic3D projection:
  ```css
  @keyframes tennis-spin {
    100% { transform: rotate(360deg); }
  }
  ```
- Two opposing curves can give a stylized spin. For a true sphere-turn illusion, project seam points under3D rotation and clip/hide the rear hemisphere; do not label plain `rotate(360deg)` as3D geometry.

### 4. Damped Pendulum Clapper Swing (Bell Notification)
- Clapper and bell body rotate around top pivot with alternating decay:
  $+14^\circ \to -12^\circ \to +8^\circ \to -4^\circ \to 0^\circ$.

## Pitfalls

- **Pivot drift:** Check computed transform origin, transform-box and ancestor transforms together; use the intended attachment point, which may not be the shape's center. Refer to `canvas-spatial-grounding` for coordinate spaces and SVG screen bounds.
- **Dash jitter:** Inspect actual rendered frames before attributing flicker to fractional dash values. Prefer consistent pathLength/units and measured geometry; rounding every dash length is not a universal fix.
- **Excess idle work:** Bound loops and expose pause/reduced-motion behavior. Measure runtime cost before claiming thermal throttling or performance improvements; inspect paused descendants and transitions, not only the outer `<svg>` animation state.
