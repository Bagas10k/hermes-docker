---
name: advanced-gpu-aware-design-system
description: "Use when creating interfaces. GPU-aware design system & UI."
---

# Hermes Advanced GPU-Aware Design System Engineer

## Precedence & UI/UX Foundation
- **Default interface workflow:** Hermes's default art direction and GPU-aware workflow when creating interfaces. Follow `ui-ux-execution-standard` for scope, behavior preservation, accessibility, and runtime verification; it does not override the brief or impose a universal palette.
- **Explicitly apply existing UI/UX skills:** Applies existing skills by name: `ui-layout-intelligence`, `typography-ux-copy`, `color-intelligence`, `ui-ux-design-vault`, and `design-qa-gatekeeper`. Apply spacing, typography scales, semantic tokens, accessibility, and design QA before adding spatial/GPU effects.
- **UI/UX motion as integrated core quality:** Motion is a primary UX dimension, not an afterthought. Design keyframes at start; test static composition, actual motion, and interaction separately; don't cut motion for convenience or pass bare functional tests as experience quality. Adapt technique and intensity for reduced motion and performance constraints while preserving user agency; avoid gratuitous particles or perpetual forced motion. Load existing motion skills on-demand when relevant:
  - `motion-principles`: Timing, easing, enter/exit, and reduced motion. Qualifies 'transform/opacity only' compositing vs GPU canvas pipelines managing coordinate buffers internally.
  - `motion-visual-systems`: Scene beats, storytelling hierarchy, and multi-state object continuity.
  - `creative-motion-lab`: Canvas shaders, particle kinematics, and spring physics.
- **Precedence:** Explicit briefs, brand guidelines, functional/security requirements, and WCAG standards override defaults.
- **Transactional safety:** 3D is NEVER mandatory on transactional workflows (checkout, billing, forms, dense data grids). Keep workflows clean, fast, and accessible in 2D.
- **Subagent delegation:** `skills.auto_load` resolves once per lifecycle; child delegates skip pinned `auto_load`. Propagate this visual contract and UI/UX standards into delegated contexts.

## Dimensional Design Grammar & Guardrails
- **Dual-mode dimensional grammar:** Select the mode matching the project brief:
  1. **Mode A (Tactile 2.5D):** Story/product UI. Asymmetric hero, staggered cards tilted -1.5deg to 2deg, hard offset shadows, layered occlusion, SVG process connectors. Pure HTML+CSS+SVG; zero canvas/WebGL. See `references/dimensional-composition.md`.
  2. **Mode B (Spatial Isometric):** Relationship/topology dashboards. Parallel projection (`perspective: none`), 3D diorama stacking, and upright billboard tags.
- **Reference precedence:** User visual references override older default templates. Never force all creations into a dark navy diorama or clone external brand assets/mascots.
- **Strict negative constraints:**
  - **No emoji in UI:** Never use emoji as icons, badges, or decoration. Use clean SVG icons or accessible glyphs.
  - **No rainbow/neon text gradients:** Never apply rainbow or high-intensity neon gradients to text. Keep typography high-contrast.
  - **No ornamental kicker badges:** Avoid frivolous floating kicker tags or badge clutter lacking operational meaning.
  - **Restrained semantic accents:** Status beacons, subtle borders, luminous route traces with verified WCAG contrast.
- **Synthetic dummy data ONLY:** Use strictly neutral synthetic data (e.g. "Cluster Node-04", "Warehouse Zone B", "Latency: 18ms"). NEVER use personal info, real names, or real business entities.

## Technical Clarifications & Core Principles
- **"GPU Style Sheets" / GCC:** Informal shorthand, not an official CSS/W3C standard. Standard CSS handles styling/layout; compositors may use GPU; WebGL/WebGPU handle programmable canvas graphics via GLSL/WGSL.
- **Compositor friendliness:** CSS `transform` and `opacity` are generally compositor-friendly, avoiding layout/paint work, but hardware GPU backing is not guaranteed. Verify via DevTools traces.
- **Canvas context locking:** Once initialized, a canvas context is locked to its initial API (`webgl2`, `webgpu`, `2d`). Do not assume multi-API cascading on one canvas. Pick the single required tier and pair it with a semantic DOM/SVG fallback.
- **Tunable starting constraints:** DPR caps (e.g. `Math.min(window.devicePixelRatio, 2.0)`) and compositor layer limits (e.g. 8–16 layers) are tunable starting constraints, not universal browser standards.

## Mandatory Workflow
1. **Discover:** Inspect repository framework (React, Next, Vue, Blade, HTML), tokens, brand guidelines, and accessibility constraints.
2. **Specify:** Define visual direction, token taxonomy, responsive breakpoints, component inventory, and 2D fallback contract. For stateful interactions, establish an explicit written motion contract with four stable keyframes (`initial`, `intermediate`, `review`, `final`) and preserved object identity at the start.
3. **Choose rendering tier:** Start with semantic HTML+CSS; use SVG for vectors or CSS 3D for light spatial work. Use Canvas/WebGL/WebGPU when the experience requires it or the user explicitly requests it; an explicit request is a hard deliverable, not permission to substitute CSS silently. Keep a functional fallback. Consult `references/usage-recipes.md` and `references/motion-keyframe-webgpu.md`. Load `motion-principles`, `motion-visual-systems`, or `creative-motion-lab` only when relevant.
4. **Architect:** Define tokens; isolate 3D/canvas effects from transactional logic; place modals outside 3D containers; enforce semantic DOM for interaction/text and decorative canvas (`aria-hidden="true"`, pointer-events none).
5. **Implement:** Follow detected framework conventions without unnecessary migrations. Build vertical slices with immediate static illustration before JS hydration (`.motion-ready` gating). For progressive enhancement of native form controls, preserve the original control's `name`, `id`, `type`, validation, and submitted value when existing scripts/backend depend on them; keep that native control as the source of truth and layer presentation/behavior around it. Ensure dynamically inserted controls are initialized too.
6. **Verify:** Run lint, unit, integration, and accessibility checks, then exercise the actual target in a real browser. For interactive controls, test the action/result path—not just markup or styling—including keyboard/focus, constraints, event propagation, and fallback behavior where relevant. A synthetic fixture proves only isolated component behavior; label it as a preview and do not present it as verification of the integrated application. If time or tool limits prevent the interaction test, report it as unverified rather than infer success from a render test. For visual revisions, apply changes directly and verify a basic render; avoid repeated multi-width screenshot/vision loops unless requested. When screenshots are requested or expected, capture the actual target page and distinguish it clearly from synthetic previews; then hand it to the user for visual review.
7. **Measure:** Profile with real browser DevTools traces. Mark unexercised hardware metrics as NOT RUN. Never fabricate FPS or claim universal speedups.
8. **Deliver:** Supply source changes, token updates, test evidence, known limitations, and rollback notes.

## Guardrails
- **Accessible motion:** Respect `prefers-reduced-motion` (WCAG 2.2 SC 2.3.3 Level AAA). Halting nonessential motion disables auto-rotation and transitions, but does NOT require deleting static 3D scenes. Provide an independent 2D layout alternative.
- **Ambient mesh & fluid background visibility:** Never apply opaque background colors (`background-color: var(--bg-canvas)`) on parent state containers (e.g., auth screens, loading/error states, app shells) that sit above ambient canvas or mesh blob layers. Use transparent backgrounds with progressive frosted glass (`backdrop-filter: blur(...)`) so underlying fluid motions remain visible; verify via visual screenshots (opaque traps cause flat, dead renders).
- **Floating pill & dynamic island geometry:** When designing floating navigation pills or dynamic island capsules, explicitly isolate the header/controls (`margin: auto; width: calc(100% - X); border-radius: 9999px;`) away from viewport edges with tactile elevation shadows, rather than stretching full-width flush bars.
- **Landing & auth viewport clamping (Zero-Scroll Entry):** Never let portal entry or auth landing pages overflow `100vh`/`100dvh` causing unintentional scrollbars and truncated bottom copy. Clamp layout height to `100dvh` using flex/grid vertical centering. Eliminate redundant branding within the same viewport (never duplicate the brand logo in both the top bar and inside the form card). Decouple heavy monolithic raster images into lightweight layered vector/DOM badges with CSS spring floating and subtle pointer parallax to maximize initial load speed and 60 FPS fluidity.
- **Swiss Brutalist Grid Balance & Asset Harmonization:**
  - *Balanced badge grids:* Never leave orphaned badge pills in feature/service lists via unstructured `flex-wrap` (e.g. 5 items on row 1, 1 lonely item on row 2). Enforce structured modular CSS grids (`grid-cols-3 sm:grid-cols-6` for 6 items) to preserve Swiss architectural grid rhythm.
  - *Soft asset harmonization in brutalist frameworks:* When placing 3D clay, cartoon, or soft pastel renders into Swiss Brutalist containers, avoid unmediated style collisions. Frame the asset with architectural HUD chips (`NODE: ...`, `FEED: LIVE`, monospaced coordinates), crisp 1.5–2px dark borders, and a subtle contrast boost (`contrast-[1.05]`) so the asset integrates organically into the technical brutalist composition.
  - *Zero-Jank Brutalist Micro-Interactions:* Use pure CSS hardware transforms for brutalist button presses (`active:translate-x-0.5 active:translate-y-0.5 active:shadow-none`) and hover offsets (`hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-[5px_5px_0px_#111]`) on top of hard offset shadows (`box-shadow: 4px 4px 0px #111`), delivering 60 FPS feedback with zero CPU overhead.
- **Keyframe gate & lifecycle:** Motion transitions must be finite with explicit cause/action/result. Stop at review gates; never auto-approve transactional states. Pause or halt rAF when document is hidden (`document.hidden`), offscreen, or disposed. WebGPU must handle device loss (`device.lost`) by falling back to SVG/CSS 2D cleanly.
- **Dual-sync selection:** Canvas has `aria-hidden="true" tabindex="-1"`. Interactive controls use semantic HTML buttons with `aria-pressed="true|false"` (not `aria-selected` for buttons) and `focus-visible` indicators.
- **Render-on-demand:** Default 3D views to event-driven rendering with dirty-flag coalescing (`requestRenderIfNotRequested`). Never run idle 60fps loops.
- **Resource lifecycle:** Explicitly dispose owned geometries, materials, and textures on unmount. Note `material.dispose()` does not dispose textures; `renderer.info.memory` need not reach 0 due to internal caches.
- **Delegation:** Partition by independent files; define explicit ownership and test contracts; merge only after verification.

## Reference Router
- Practical recipes & patterns: `references/usage-recipes.md` (section 7: live mini-demos on static case-study pages, with seeded data, invariant check hooks, and a verification gate)
- Dimensional composition & 2.5D case study: `references/dimensional-composition.md`
- Source ledger & verified grounding matrix: `references/verified-sources.md`
- Motion keyframing, DOM semantics & WebGPU contract: `references/motion-keyframe-webgpu.md`
- CSS, rendering, and shader technology map: `references/gpu-rendering.md`
- Visual principles and token taxonomy: `references/design-system.md`
- Framework integration (React, Next, Blade): `references/frameworks.md`
- Screenshot-to-code & existing workflows: `references/workflows.md`
- Performance, accessibility, and quality gates: `references/quality-gates.md`
- Cinematic playful 3D visual specification: `references/spatial-3d-direction.md`
- Reusable seed token set: `assets/tokens.example.json`
- Runnable companion assets: `examples/spatial-interface.html` (native CSS/SVG teaching example, not a finished visual showcase) and `scripts/self_check.py` (token/CSS audit regression checks). Resolve `<skill-dir>` from skill_view; open the HTML in a browser and run `terminal(command="python3 <skill-dir>/scripts/self_check.py")`.
