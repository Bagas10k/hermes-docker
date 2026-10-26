---
name: webgpu-fluid-simulation
description: Simulate real-time 2D fluids via WebGPU WGSL compute.
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags:
      - WebGPU
      - FluidSimulation
      - UpnormalDesign
      - CreativeCoding
      - Shaders
---

# WebGPU Fluid Simulation & Upnormal Design

Simulate real-time 2D incompressible fluid dynamics using WebGPU compute shaders in WGSL, and embed fluid dynamics into high-end "upnormal" UI/UX architectures. This skill covers Jos Stam's Stable Fluids pipeline (advection, divergence, Jacobi pressure solve, gradient subtraction) and design integration patterns.

## When to Use
- User asks for "WebGPU fluid simulation", "liquid dynamics", or "interactive fluid background".
- Implementing interactive hero canvases with pointer-driven fluid swirls.
- Building abnormal/upnormal creative web interfaces (Swiss Editorial, Neo-Brutalism, Liquid Gooey) driven by GPU compute.

## Prerequisites
- Modern browser supporting WebGPU (`navigator.gpu`).
- Canvas element in DOM: `<canvas id="fluid-canvas"></canvas>`.
- Basic HTML/JS host environment. Fallback: WebGL2 / CSS-native gooey filter when WebGPU is unavailable.

## How to Run
Invoke generation and verification through the `terminal` tool or inspect in browser using `browser_navigate`.

## Quick Reference
- **Init:** `const adapter = await navigator.gpu.requestAdapter(); const device = await adapter.requestDevice();`
- **Context:** `const ctx = canvas.getContext('webgpu'); ctx.configure({ device, format: navigator.gpu.getPreferredCanvasFormat() });`
- **Pass Order:** `Splat (Mouse Force) -> Advect Velocity -> Divergence -> Jacobi Pressure (20-40x) -> Gradient Subtract -> Advect Dye -> Render`.

## Procedure

1. **Verify WebGPU Support & Fallback:**
   Always test for `navigator.gpu`. If unavailable, gracefully fallback to 2D canvas particle drift or SVG gooey filter.

2. **Setup Ping-Pong Buffers:**
   Maintain double buffers (`read` and `write`) for Velocity (`vec2f`) and Dye (`vec4f` or `f32`), swapping indices each frame:
   ```javascript
   let src = frame % 2;
   let dst = 1 - src;
   ```

3. **Compute Pass Pipeline in WGSL:**
   - **Advection:** Semi-Lagrangian back-tracing with bilinear interpolation.
   - **Divergence:** Central difference `0.5 * ((vR.x - vL.x) + (vT.y - vB.y))`.
   - **Pressure Poisson Solve:** Jacobi relaxation loop (20-40 iterations) warm-started from previous frame.
   - **Gradient Subtraction:** Enforce divergence-free field `v_new = v_old - 0.5 * vec2f(pR - pL, pT - pB)`.
   - **Dye Advection:** Advect color/scalar field along updated velocity.

4. **Upnormal UI/UX Integration (Awwwards / Godly Aesthetic):**
   - **Achromatic Stage + Punchy Accent:** 95% monochromatic surface (Ink `#111111`, Paper `#FFFFFF`, Pale Canvas `#F8F8F8`) paired with a single vibrant punctuation point (Ember `#FA5D29` or Electric Blue `#49B3FC`).
   - **Typographic Dominance:** Pair WebGPU organic fluid swirls with massive display typography (e.g. `Inter Tight` 112px-127px, weight 300-600, tight line-height `0.93`), rendered cleanly on the top layer without filter blur.
   - **Two-Layer Silhouette Architecture:** Fluid simulation canvas sits on bottom layer (`z-index: 0`, `pointer-events: none`); interactive navigation, pill tabs, and sharp typography sit on top (`z-index: 10`).
   - **Zero Drop-Shadows:** Rely on high surface contrast and hairline borders (`#EDEDED`) rather than fuzzy drop-shadows.


## Pitfalls
- **Texture Format Compatibility:** Use `rgba16float` or `r32float` for precision in velocity/pressure; unextended formats may clip negative velocities.
- **Resource Allocation in Render Loop:** Never create pipelines or bind groups inside `requestAnimationFrame`. Pre-allocate all GPU resources during initialization.
- **Mobile Battery Drain:** Throttle simulation to 30 FPS or pause when canvas is scrolled out of viewport using `IntersectionObserver`.

## Verification
Inspect compiled WGSL and canvas mounting:
Verify WebGPU context initialization returns non-null context with `terminal` or headless browser check.
