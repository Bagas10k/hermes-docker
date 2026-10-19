# Hermes spatial 3D direction — visual specification v2

## Scope: optional spatial mode
Use this reference only after choosing the spatial/isometric mode for a relationship-heavy overview. It is not the default palette or composition for every interface; explicit references and `dimensional-composition.md` take precedence. Proportions, colors, and timing below are starting choices, not universal requirements.

## Visual target
Create a **playful, cinematic operations command center**, not a generic SaaS card grid. Reference concept: isometric mini-world of a warehouse / factory / fleet in the center; holographic status tags anchored to meaningful sites; luminous road/flow traces; navy/indigo atmosphere; cyan, electric blue, violet, mint and amber accents. Keep the surrounding sidebar, actions, charts, KPIs and alerts crisp and readable. Depth must communicate spatial relationships, not merely decoration.

## Composition
- Desktop: left compact navigation rail; top command/search bar; dominant hero diorama (~50-65% of main content width and ~40-55% of first viewport height, adjust to actual data); right operational summary/activity; lower analytics row. Avoid blocking controls with 3D overlays.
- Tablet: collapse sidebar, simplify diorama, stack summaries. Mobile: default to compact 2D operations overview and an optional 'Explore 3D' affordance; no horizontal overflow.
- Foreground: typography, KPIs, filters, accessible call-to-action. Midground: contextual floating cards and connection lines. Background: diorama and subtle atmospheric lighting. Use occlusion, size, shadow and blur judiciously to establish depth.
- No more than 1 main hero 3D scene per screen. Keep transactional forms, dense tables and finance approvals primarily 2D.

## Design tokens and palette (starting values, validate contrast)
- Canvas `#080F20`, deep surface `#101C34`, raised surface `#182844`, borders `#314565`, primary text `#F4F8FF`, muted text `#B8C7DD`.
- Electric blue `#397BFF`, cyan `#2DDAFF`, violet `#9A63FF`, mint `#28D9AD`, amber `#FFB454`, danger `#FF657C`.
- Radii 12/18/24px; surfaces use restrained 1px strokes, occasional backdrop blur only where performant; shadows with clear hierarchy. Do not use neon as the only signal for state.
- Headings bold, confident; body comfortable at 14-16px; numeric KPI tabular; labels never rendered as tiny unreadable 3D texture.
- Strict visual constraints:
  - No emoji in UI: use clean SVG icons or semantic glyphs instead.
  - No rainbow or neon text gradients: typography must maintain solid, high-contrast legibility.
  - No ornamental kicker badges: avoid frivolous decorative badges that lack operational meaning.
  - Neutral synthetic dummy data ONLY: use fictional tokens (e.g. Node-01, Region-A), never user personal information or real business entities.
- Precedence: explicit project briefs and existing brand guidelines override default art directions. 3D is progressive enhancement and never mandatory on transactional flows. Supplements existing UI/UX skills (`ui-layout-intelligence`, `typography-ux-copy`, `color-intelligence`, `ui-ux-design-vault`, `design-qa-gatekeeper`).

## Interaction language
- Hover/focus: gentle lift or light sweep (120-220ms); press: tactile scale or elevation shift (80-140ms); panel entrance: opacity + small translate (180-320ms).
- Anchor status labels to actual nodes; selecting a node reveals the corresponding 2D detail panel, keyboard-operable with clear focus state.
- Scene camera: modest orbit/pan only when useful; constrain bounds; add Reset View; avoid auto-spinning camera. Highlight live changes without flashing.
- User-facing mode switch: `2D / 3D` with preference persistence where supported. Reduced motion: static scene or 2D view; never remove access to information.

## Data and meaning
- Production: machine/building utilization; inventory: storage locations/low-stock; delivery: fleet/route status; sales: regional distribution. Only visualize fields backed by the application's real data model. Distinguish simulated/demo data visibly.
- Every 3D indicator has a textual equivalent; charts retain tooltips plus readable tables or summaries. Critical warnings cannot depend solely on color or scene exploration.

## Rendering and asset strategy
1. Prefer CSS + SVG layered isometric illustrations for simple or static scenes. Use SVG paths for route lines, CSS transforms for cards.
2. For genuinely interactive 3D, use Three.js / React Three Fiber where already appropriate; evaluate dependency and bundle cost first. In Laravel/Blade, isolate scene as a progressively enhanced component, not a framework migration.
3. Use glTF/GLB with compressed geometry/textures where possible; provide poster/thumbnail and fallback. Avoid heavy postprocessing, enormous shadows, unnecessary transparency, per-frame React state updates and unbounded pixel ratio.
4. WebGPU is optional experimental enhancement; feature detect, handle device loss and fall back to WebGL or static 2D. Never claim CSS itself is a GPU programming language.
5. Lazy load scene after primary KPIs/controls. Stop animation on hidden tabs, offscreen scenes and reduced motion; release listeners, textures and GPU resources on teardown.

## Deliverables for each redesign
- One-page style brief; token diff; desktop/mobile wireframes; functional component implementation; meaningful 3D-to-data mapping; 2D fallback; scene budget; before/after screenshots if actual browser available; QA report.
- Verify keyboard controls, 200% zoom, 320px layout, readable contrast, labels, empty/loading/error states, CPU/GPU usage and interaction latency where measurable.
- Do not invent measured FPS or assert fidelity based on a generated concept image. Treat visual reference as art direction, not exact implementation specification.

## Visual acceptance evidence
Review identity, useful depth, operational meaning, hierarchy, discoverable interactions, responsive behavior, accessibility, measured performance/fallback, token consistency, and functional integrity. For each applicable concern record an actual screenshot/test finding and any blocker. Do not invent numeric scores or let decorative polish offset a functional or accessibility failure.
