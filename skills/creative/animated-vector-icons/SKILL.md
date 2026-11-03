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

Standard operating procedure and mathematical recipes for generating ultra-lightweight (<2 KB), zero-dependency, resolution-independent animated SVG vector icons with physical micro-interactions.

## When to Use

- "buatkan icon animasi SVG (eye, menu, bell, basketball, sun-moon, dll)"
- "rancang animasi micro-interaction vektor murni tanpa library berat / video"
- "buatkan aset SVG interaktif yang merespons hover, click, atau mouse tracking"
- "terapkan prinsip animasi fisik (squash & stretch, orthographic 3D spin, pendulum inertia)"

## Core Architecture Principles

1. **Pure Vector Zero-Dependency:** Never use MP4 video, heavy Lottie JSON, or raster GIFs for iconography. Output must be raw SVG with inline CSS `<style>` or `@keyframes`.
2. **Pinned `transform-origin` Absolute Anchor:** Any element undergoing `scale()`, `rotate()`, or `skew()` must explicitly define its pivot point in SVG coordinate space (e.g., `transform-origin: 24px 24px`). Unpinned transforms default to `(0, 0)`, causing detached/floating artifacts.
3. **GPU-Friendly Compositor Properties:** Only animate `transform` and `opacity` to maintain locked 60 FPS performance without triggering DOM layout recalculations.
4. **Interactive Dual-State:** Every icon must support passive looping (breathing/idle) and active triggered states (`.is-active`, `:hover`, or mouse pointer tracking).

## Essential Animation Formulas

### 1. Organic Eye Tracking & Eyelid Blink
- **Blink Keyframes:** Eyelids stay fully open (100% scaleY) for 94% of the cycle, swiftly compressing to 8% scaleY at 97%, and opening again by 100%.
- **Pupil Pointer Delta:** Calculate normalized mouse offset from card center:
  $$\Delta x = \left(\frac{x - x_{\text{center}}}{W} - 0.5\right) \times \text{range}_x, \quad \Delta y = \left(\frac{y - y_{\text{center}}}{H} - 0.5\right) \times \text{range}_y$$

### 2. Squash & Stretch Bounce (Basketball / Ball Physics)
- **Falling vs Impact Timing:**
  - Fall: `translateY(-16px) scale(0.94, 1.06)` (elongated stretch).
  - Ground Impact: `translateY(12px) scale(1.18, 0.82)` (horizontal compression).
  - Rebound: Spring curve `cubic-bezier(0.28, 0.84, 0.42, 1)`.
- **Contact Shadow Scaling:** Ground ellipse expands (`scale(1.2)`) and darkens at contact, shrinking (`scale(0.5)`) and fading at peak altitude.

### 3. Orthographic 3D Seam Spin (Tennis Ball / Globe)
- Sphere remains fixed while inner hyperbolic seams rotate around polar axis:
  ```css
  @keyframes tennis-spin {
    100% { transform: rotate(360deg); }
  }
  ```
- Two opposing curved paths `M 12 15 C 19 20, 29 20, 36 15` and `M 12 33 C 19 28, 29 28, 36 33` create continuous 3D rotation illusions.

### 4. Damped Pendulum Clapper Swing (Bell Notification)
- Clapper and bell body rotate around top pivot with alternating decay:
  $+14^\circ \to -12^\circ \to +8^\circ \to -4^\circ \to 0^\circ$.

## Pitfalls

- **Unanchored Scale Displacement:** Scaling SVG sub-elements without explicit `transform-origin` calculates offsets from the SVG viewBox origin `(0, 0)`, throwing the element completely out of position. Always pin `transform-origin: Xpx Ypx` to the element's geometric center.
- **Stroke-Dasharray Float Jitter:** Animating path drawing with fractional stroke dashes causes subpixel flickering on high-DPI screens. Round dash lengths to nearest integer values.
- **Unbounded Idle Animations:** Running dozens of continuous complex SVG animations simultaneously on mobile causes CPU thermal throttling. Provide an auto-play toggle or use `IntersectionObserver` to pause offscreen animations.
