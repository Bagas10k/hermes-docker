---
name: vector-field-particle-flow
description: Use when adding bounded reactive particle flow.
version: 0.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [canvas, vector-field, vibe-coding, lifecycle]
    related_skills: [interactive-canvas-sketchbook, dynamic-canvas-backdrop]
---

# Vector Field Particle Flow

Add a reusable Canvas 2D curl-field layer to an editor without capturing code or blocking gestures. This user-local skill supplies a working studio and lifecycle controller; it is not an upstream Hermes release or a fluid solver.

## When to Use
- Add optional activity-reactive flow to a coding sandbox or artifact preview.
- Require bounded particles, idle shutdown and explicit unmount cleanup.
- Do not use for physical fluid simulation, productivity scoring or critical status communication.

## Prerequisites
- Modern browser with Canvas 2D, ResizeObserver, IntersectionObserver and ES modules.
- Python 3 for an isolated HTTP preview; no production changes required.
- Load `references/architecture.md` before adapting the field or claiming performance.

## Quick Reference
Through `terminal`, from this skill directory: `python3 -m http.server 18763 --bind 127.0.0.1`.
Open `/templates/studio.html` on that local preview using `browser_exec`.
Copy `scripts/flow.js` into the target app as an ES module.

```js
import { createFlow } from './flow.js';
const flow = createFlow(canvas, { count: 360, idleMs: 45000 });
const onInput = () => flow.activity();
editor.addEventListener('input', onInput);
// On unmount: remove the application listener as well as engine resources.
editor.removeEventListener('input', onInput);
flow.dispose();
```
Public controls: `activity()`, `pause()`, `resume()`, `stats()`, `dispose()`.

## Procedure
1. Define scope: opt-in decorative layer, no code telemetry, no production service mutation. Pass when editor remains usable with animation disabled.
2. Copy the module and studio into a sandbox. Pass when actual Canvas 2D strokes appear and browser console has no application errors.
3. Connect the editor's input event to `activity`, never to raw code logging. Pass when the original studio sleeps after 45 seconds and real text input restarts it.
4. Preserve the single pending-rAF invariant and reason precedence: disposed, paused, hidden, offscreen, reduced motion, idle. Pass when repeated resume does not add loops and dispose is irreversible.
5. Keep canvas pointer-events disabled and provide HTML controls with visible keyboard focus. Pass at mobile and desktop widths with no horizontal overflow.
6. Measure p95 callback cost separately from p95 frame interval via `stats()`. Pass only for the measured environment; adjust count within 1..1200 or reduce pixel budget before adding workers.
7. Exercise pause/resume, hidden tab, reduced motion, idle, resize and repeated disposal. Remove the preview server when finished. Pass when no controller callbacks remain pending and detached observers cannot restart the controller.

## Pitfalls
- rAF is one-shot, not inherently a 60 FPS guarantee. Use its timestamp and clamp elapsed integration time after stalls.
- A paused background tab is not sufficient lifecycle cleanup. Cancel the stored handle on visibility change and unmount.
- A zero pending callback count is not proof of zero process CPU or GPU usage.
- CSS-hidden iframes do not receive document visibility changes. IntersectionObserver handles the canvas viewport case, not every embedding architecture.
- This analytic streamfunction curl is NOT Perlin/curl noise. Use an established seeded noise library if stochastic structure is required; preserve disposal and measured budgets.
- Do not normalize velocity pointwise while claiming divergence-free flow; normalization generally breaks that property. Euler particle integration is not exactly area-preserving.
- Replacing a controller leaves existing editor closures pointing to the old instance. Remove/rebind the listener during replacement; the shipped studio creates one instance.
- Canvas bitmap area scales with DPR squared. The implementation caps DPR at 2 and total bitmap area at two million pixels.
- Reduced motion suppresses continuous animation even after resume. It must not be silently overridden.
- Re-mount on SPA/BFCache restoration after disposal; this studio disposes on pagehide.

## Verification
Use the browser against the actual template, not an independent numerical toy. Record `stats()` before/after idle, real editor input, pause and dispose; inspect the browser's actual reduced-motion setting through CDP. Confirm count validation rejects invalid or unbounded counts. See `references/browser-results.json` for the recorded Chromium run and `references/architecture.md` for limits. Firefox/Safari, real-device battery use and subjective aesthetics remain unverified.
