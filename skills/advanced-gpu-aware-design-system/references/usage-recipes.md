# Usage recipes: choose the smallest rendering tier

Sources and retrieval dates: `verified-sources.md`. Composition and inspected reference: `dimensional-composition.md`. Examples below are patterns to adapt, not measured performance results.

## 1. Start with the interface, not the GPU

1. Inspect the actual route, framework, components, tokens, content, target devices, and existing tests. Preserve routes, authorization, data contracts, and business behavior.
2. Load `ui-layout-intelligence`, `typography-ux-copy`, `color-intelligence`, `ui-ux-design-vault`, and `design-qa-gatekeeper` when relevant. The dimensional skill supplements them.
3. Write a small contract: user task, information hierarchy, visual reference, chosen dimensional treatment, responsive behavior, essential controls, fallback, and verification method.
4. Choose the first tier that satisfies the need:
   - **HTML + CSS:** layout, typography, forms, tables, tactile cards, restrained transforms/shadows.
   - **SVG:** crisp process paths, illustrated isometric blocks, topology, scalable diagrams.
   - **CSS 3D:** a small number of genuinely layered planes or elevated labels.
   - **Canvas 2D / WebGL:** dense dynamic drawing, meshes, custom shaders, or interaction that simpler tiers cannot reasonably provide.
   - **WebGPU:** a specific compute/rendering requirement and measured benefit on supported target devices; otherwise skip it.
5. Use one chosen programmable tier plus a useful DOM/SVG alternative. A successful `getContext()` fixes that canvas's context mode; a failed request returning null does not establish a context. Do not build an unnecessary five-engine fallback chain. WebGPU can also run compute without a canvas.

Transactions, dense numeric data, critical actions, and labels stay legible 2D. A small decorative tilt is not permission to distort input fields or obscure controls.

## 2. Build dimensionality with native elements

**Tactile/editorial 2.5D:** controlled asymmetry, staggered meaningful cards, directional offset shadows, restrained rotations, and background SVG connectors. See the inspected-reference breakdown in `dimensional-composition.md`.

**Spatial overview:** establish a viewport boundary, a transformed world, and elevated children. Keep clipping outside the preserve-3d chain; a root viewport may clip the final composition, so reserve space for labels and focus outlines.

```css
.scene-viewport { position: relative; overflow: clip; }
.scene-world {
  position: relative;
  transform: rotateX(60deg) rotateZ(-45deg);
  transform-style: preserve-3d;
}
.scene-node {
  position: absolute;
  transform: translateZ(var(--elevation, 24px));
  transform-style: preserve-3d;
}
.scene-label { transform: rotateZ(45deg) rotateX(-60deg); }
```

This is a transform-hierarchy pattern, not a complete responsive page. Set dimensions, origins, placement, and focus clearance for the actual content. `perspective: none` means no perspective foreshortening; the example is an isometric-style view, not a claim of exact equal-axis geometry. A large finite perspective remains perspective.

**Flattening traps:** MDN lists grouping values that force the used transform-style to flat: overflow other than visible/clip; opacity below 1; filter other than none; clip other than auto; clip-path other than none; isolation:isolate; mask-image/mask-border-source other than none; mix-blend-mode other than normal; paint containment and values causing it, including content-visibility:hidden. `transform-style` is not inherited: set it on needed intermediate elements. Do not infer flattening from a computed `preserve-3d` string alone. `backdrop-filter` is not included in that verified MDN list; it still needs paint/performance review.

Use viewport-level cropping or separate 2D overlay panels rather than adding opacity/filter/containment to intermediate 3D ancestors. Keep fixed tooltips/dialogs outside transformed/perspective ancestors or use correctly tested native top-layer behavior.

## 3. Semantic state and motion

- Keep essential heading, supporting text, and primary action visible in initial HTML. Entrance animation must not be a prerequisite for reading or using them.
- Use native HTML buttons with accessible names, visible focus, and `aria-pressed` for selected/toggle state. `aria-selected` is not valid on a plain button.
- When a scene duplicates information, keep it decorative and provide full semantic controls/details in DOM. If the scene itself is interactive, test its real accessibility tree instead of placing controls inside a parent exposed only as an image.
- Keep selection synchronized between DOM controls, optional scene interactions, and the detail panel. Use a restrained live region for changed information, not noisy announcements for every animation frame.
- Honor reduced motion at startup and when the preference changes. Stop nonessential movement, not access to information. Static depth can remain; offer an independent 2D option.

```css
@media (prefers-reduced-motion: reduce) {
  .scene-world, .scene-node, .scene-label, .tactile-card {
    animation: none;
    transition: none;
  }
}
```

For JavaScript-driven motion, read `matchMedia('(prefers-reduced-motion: reduce)').matches`, listen for changes, and remove that listener on teardown. Restore only the user's previously chosen motion setting; do not automatically enable auto-rotation when reduced motion turns off. WCAG SC 2.3.3 is AAA; SC 2.2.2 separately addresses qualifying automatic motion.

## 4. When programmable graphics are justified

Use the project's existing engine; don't migrate frameworks for a scene. In React/Next, initialize after mount on the client and return cleanup from the effect; in Blade/Livewire, preserve framework ownership and tear down effects on navigation. Avoid per-frame framework state updates.

**Initialization:** reserve container size before loading. Feature-detect secure context and `navigator.gpu` for WebGPU; request adapter, handle null/rejection, request device, and handle device loss. A presence check alone is not proof that rendering works. Keep DOM fallback usable before initialization and after failure.

**Resize:** use container dimensions, update camera aspect/projection, and resize the drawing buffer without resizing its CSS box recursively. A DPR cap such as 1.5 or 2 is a tunable project starting choice, not a standard. Avoid applying DPR twice. Request a render after resize.

**Rendering:** static/user-driven scenes should render on initial load and relevant changes; coalesce multiple requests into one pending requestAnimationFrame per scene. Cancel pending frames on teardown. Damped controls may need additional frames until settled. Continuous simulations need a loop only while active; suspend offscreen/hidden-tab work and resume safely.

**Resource ownership:** dispose the geometries, materials, textures, render targets, and renderer owned by this view; detach observers/listeners and stop loops. Material disposal does not dispose textures. Do not dispose shared assets. Three.js resources need explicit disposal during a running page; do not rely on JavaScript garbage collection as a lifecycle policy. Internal caches mean renderer.info.memory need not reach zero.

**Loss:** if implementing WebGL recovery, preventDefault in webglcontextlost, stop rendering and show fallback; rebuild resources on webglcontextrestored. For WebGPU, observe device.lost and avoid retrying intentionally destroyed devices. Recovery needs an attempt limit and an unmounted/stale-generation guard; do not resurrect a closed view.

## 5. Run the included example and audits

Resolve `<skill-dir>` from skill_view. The example is standalone and contains only neutral synthetic data:

- Open `<skill-dir>/examples/spatial-interface.html` in a browser, or serve that directory locally with `terminal(command="python3 -m http.server 8765 --bind 127.0.0.1 --directory <skill-dir>/examples")` when a local HTTP surface is needed. Do not publish it implicitly.
- Run `terminal(command="python3 <skill-dir>/scripts/self_check.py")` for the bundled positive/negative script checks.
- Run `terminal(command="python3 <skill-dir>/scripts/token_audit.py <project-tokens.json>")` for nested plain JSON whole-value aliases such as `{primitive.color.ink}`. It is not a full DTCG/type/contrast validator; composite interpolation is not covered.
- Run `terminal(command="python3 <skill-dir>/scripts/css_motion_audit.py <project-css-path>")` for advisory CSS warnings. Exit 0 means scan completed, not performance passed; empty scans and invalid inputs are distinct outcomes. Regex heuristics do not parse every nested/minified CSS construction or prove GPU use.

## 6. Verification that changes decisions

- Desktop and 320/390px mobile: no horizontal overflow; content-driven mobile height; controls do not cover content. Size clearance from the actual fixed control plus safe-area inset, not a universal pixel constant.
- Real Tab/Enter/Space input: focus reaches native controls; selection/detail changes; no keyboard trap. DOM dispatchEvent alone is insufficient keyboard acceptance.
- Toggle 2D/3D and reduced motion; test startup defaults and preference changes. Disable JS: essential content remains readable, dead controls do not masquerade as working actions.
- Check loading/empty/error states, long labels, browser console exceptions, contrast, zoom, and real screenshots. Automated checks do not establish WCAG conformance.
- If programmable graphics are actually used, test unsupported initialization, context/device loss, hidden tabs, route teardown, and repeated mount/unmount with owned-resource accounting.

Profile a representative interaction in DevTools Performance, inspect main-thread tasks, paint flashing, and layer composition. Prefer transform/opacity where appropriate, but verify actual paint/layout behavior. Use will-change only for a demonstrated need and remove unnecessary hints. Choose frame/layer budgets for target hardware and refresh rate; no fixed count guarantees speed.

Report environment, method, actual results, and limitations. Headless is not inherently software-only, but this task's --disable-gpu functional run cannot prove physical GPU acceleration. Hardware FPS, thermal behavior, and field p75 INP/LCP/CLS remain NOT RUN without suitable device/RUM evidence. Microtasks/Promise.resolve do not yield to rendering; use an available scheduler.yield or a supported task-yield fallback for noncritical long work.
