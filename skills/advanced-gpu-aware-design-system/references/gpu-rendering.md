# GPU-aware rendering and effects

## Technology map
CSS is a stylesheet language; compositor acceleration depends on browser, element, and property. CSS transform and opacity are often compositor-friendly but are not guaranteed GPU-backed. Layout properties (width, top, left) can force layout/paint. `filter`, `backdrop-filter`, and large shadows can be expensive. SVG is ideal for crisp vector icons/illustrations; SVG morphing requires compatible paths or a dedicated interpolator. Canvas 2D suits dynamic 2D scenes; WebGL uses shaders written in GLSL ES; WebGPU uses WGSL. WebGPU requires a secure context and availability checks; support varies by browser/device.

## Decision ladder
1. Static content -> semantic HTML + CSS.
2. Standard UI motion -> CSS transition/keyframes or Web Animations API; animate transforms/opacity when possible.
3. Vector diagrams/icons -> SVG and optional path animation.
4. Large animated 2D scenes -> Canvas 2D with throttling and DPR caps.
5. Shader-driven 2D/3D effects -> WebGL with progressive enhancement.
6. Advanced compute/render pipelines -> WebGPU only after benchmark proves value and fallback is planned.
Pick the single rendering tier needed plus a functional semantic DOM/SVG fallback; due to canvas context locking, do not assume different rendering APIs can share or cascade on the same canvas element.

## GPU lifecycle
Check `navigator.gpu` before WebGPU initialization; request adapter/device defensively; handle device loss, resize, DPR, page visibility, and teardown. Bound memory and animation loops; release buffers/textures where supported and destroy unused resources. Use feature detection instead of user-agent guessing. In React, cleanup requestAnimationFrame, listeners, observers, and GPU resources on unmount.

## Accessibility and performance
Use static poster/CSS fallback for shader scenes; maintain real DOM for content, selection, screen readers, and forms. Respect reduced motion and low-end devices. Avoid putting essential information exclusively in a canvas. Measure frame duration, long tasks, layout shifts, memory, and input latency in real browsers; do not claim 60fps without trace evidence.

## Example progressive enhancement
```js
// Reduced motion stops nonessential movement, but does not forbid static 3D/GPU rendering.
// Always pair chosen rendering tier with a functional semantic DOM/SVG fallback.
const prefersReducedMotion = typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const canUseWebGPU = typeof navigator !== 'undefined' && !!navigator.gpu && window.isSecureContext;
// Initialize optional visual enhancement only when supported.
// If prefersReducedMotion is true, halt auto-rotation and camera loops while keeping static visualization.
// Keep DOM content and CSS fallback usable either way.
```

## Authoritative references
MDN Web Docs: CSS performance, Web Animations API, WebGL, WebGPU; W3C WebGPU and WGSL specifications; web.dev rendering performance and Core Web Vitals. Check current compatibility documentation for the target browsers before using advanced features.
