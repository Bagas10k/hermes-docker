---
name: ui-ux-execution-standard
description: "Use when implementing UI/UX. Preserve behavior; verify UI."
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ui, ux, execution, accessibility, browser-verification, design-system]
    related_skills: [ui-ux-design-vault, upnormal-ui-architecture, design-qa-gatekeeper, browser-keyboard-accessibility-verification]
---

# UI/UX Execution Standard

## When to Use

Use when implementing, polishing, or verifying web/app UI/UX. Preserve existing behavior and verify the real interaction in a browser.

This standard governs execution and verification; it does not impose one universal visual theme.

## 1. Start from the actual product

- Read applicable repository instructions, current design tokens, shared components, target route/view, and existing behavior before editing. Record navigation placement and the form-opening model (inline, popup, or separate page) alongside visual tokens; refinement does not authorize changing either interaction contract.
- Treat explicit user references, brand rules, accessibility, and security requirements as hard constraints. Record an approved palette/direction once and carry it into implementation and delegated work; do not reopen the same theme choice after a checkpoint or context handoff. Reuse the product's visual language; do not copy a component palette into unrelated products. A download landing page is not the visual authority for the working application unless the user explicitly makes it so.
- Classify the request before editing: refinement preserves the working interface; restoration returns to the approved incumbent; redesign replaces it only with explicit approval. Adding roles, permissions, or operational modules does not authorize replacing an already-working primary workflow.
- When asked to match the old interface, render the actual old route and the candidate in the same isolated runtime before changing code. Match the complete composition—navigation states, monitoring, catalogue/cart, history, typography, control density, and popup sequence—not merely the palette or pane order. Prefer reusing incumbent components/styles with a narrow data adapter over independently rebuilding lookalikes.
- Resolve rejection against the already-authorized scope. If refinement/restoration was requested and feedback is nonspecific, ask one focused question with incumbent preservation first; a low score alone does not authorize a redesign. If the user already requested a redesign and supplied its direction, continue one bounded corrective revision within that brief instead of restarting discovery or asking for the same approval again. Describe the observed mismatch, not an invented reason for the user's score.
- For a fun, non-boring working app, inspect one real product surface and one interaction reference before choosing the composition; search snippets, curator labels, or a landing-page screenshot alone do not establish the underlying app's behavior. Extract task placement, density, typography, and state continuity. Do not equate fun with more accent colors, thick borders around every section, a generic face mascot, decorative badges, or confetti; these can leave the same repetitive structure intact. True delight comes from:
  1. Primary work visible immediately above the fold with zero friction.
  2. Dynamic organic/botanical growth metaphors tied to real milestone progress.
  3. In-place physical morphing (sliding pill indicators on active segmented tabs/week strips with spring easing `cubic-bezier(0.16, 1, 0.3, 1)` and tactile squash-and-stretch toggles) instead of jumpy state changes.
  4. Clean, command-bar style input controls (custom pills with live category color dots) instead of raw stacked dropdowns.
  Treat the revised aesthetic as a candidate until owner review, not a proven improvement.
- Prefer one shared, small primitive when the same interaction belongs across pages. Avoid a project-wide redesign when the request is a bounded component change. For the ordered comparison and reuse procedure, see [Incumbent interface preservation](references/incumbent-preservation.md).
- For multi-step work, state concrete scope and binary checks before broad edits. Preserve unrelated dirty work.

## 2. Preserve the behavior contract

- Keep form actions, methods, names, IDs, validation, data attributes, events, and URL/query contracts unless the user explicitly changes them.
- For enhanced inputs, retain a semantic successful form control as source of truth. A visual layer may localize or theme it, but must not change submitted values or bypass listeners.
- For calendars/custom selects inside a native modal dialog, place the picker under that open dialog before opening its supported popover top layer; a larger z-index on a body-mounted picker does not escape modal inertness. Reset popover UA margin/inset before positioning, measure the settled picker bounds, and keep Escape scoped to the picker with focus returned to its trigger. Verify the parent dialog remains open and the canonical control receives its normal events. Scope dialog listeners to the newly owned component rather than re-registering handlers on every existing dialog.
- Keep a usable fallback when enhancement is unavailable. Do not hide or disable the base control before enhancement initializes successfully.
- Do not add fake interactions, unsupported fields, or persistence claims to make a preview look complete. Compute progress/streak indicators from real records or omit them; a static achievement label is not a feature. Do not add unrelated timer, sound, or gamification features merely to compensate for rejected visual composition.
- For browser-persisted UI, inventory the existing storage keys and full record schema before rewriting the view. Validate the entire payload before permitting writes; never silently filter invalid records, coerce a string into a boolean, or fall back to an empty writable state after a parse failure, because the next mutation can erase recoverable data. Preserve corrupt originals, report session-only behavior when storage is blocked, and require an explicit conflict/deletion policy before merging multiple keys. Prove old-data reload and mutate/reload behavior with isolated fixtures before claiming compatibility or no data-loss risk.
- Keep local calendar navigation in local calendar components; converting local midnight through `toISOString()` can select the previous date in positive UTC offsets. Test a forward/backward day round trip in the target timezone. If adding a countdown, derive remaining time from a deadline rather than counting interval callbacks, because background tabs throttle callbacks.
- Use neutral synthetic fixtures only; never put personal or real business data in demos/tests.

## 3. Make interaction accessible and bounded

- Use native semantic controls where they satisfy the product contract; add a custom surface only when a real design or platform-consistency need warrants it.
- Verify keyboard access, focus visibility/restoration, accessible name/state, disabled/read-only behavior, validation, and boundary values for the interaction.
- Respect `prefers-reduced-motion`; keep transitions finite and tied to a user action. Do not claim frame rate or hardware acceleration without measurement.
- Test relevant edge cases such as empty/required values, min/max, reset, dynamic insertion, and known JavaScript consumers.

### Task-based operational workspaces

- When a long operational screen is reorganized into task panels, retain its established visual language and separate navigation changes from domain calculations, permissions, and database changes. Choose panel grouping inside the approved shell; do not infer that task separation requires horizontal tabs or permanently visible input forms.
- Preserve unsaved work by moving existing DOM nodes rather than rebuilding forms with `innerHTML` or remounting them. Verify a typed-value round trip between panels with zero mutation requests; this proves in-page retention, not persistence after reload.
- For tabs, provide labelled tab/panel relationships, one roving tab stop, arrow/Home/End navigation, and non-focusable inactive panels. Keep active state distinct from keyboard focus, and enable panel hiding only after enhancement initializes.
- Check navigation labels and child-control bounds, not only page overflow: a fixed bar or narrow table can clip useful content while the document still fits the viewport. Reserve space for fixed navigation and prove the final form action can scroll clear of it.
- Use the ordered recipe and DOM probes in [Task workspaces](references/task-workspaces.md) when applying this pattern.

## 4. Keep project build documentation useful

When UI work changes a project's setup, build/test commands, routes, design-system contracts, or reusable component behavior, update the existing canonical documentation in the same change. Read docs first; document verified commands and behavior only; link to focused architecture notes rather than repeating them. For visual-only changes that do not alter how the project is built or maintained, avoid unnecessary doc churn. Follow `project-build-documentation`.

## 5. Verify the running UI, not just source text

- Complete one integrated vertical slice before expanding polish: markup, CSS, runtime, and the primary action must work together. When those files are delegated separately, lock required selectors, emitted class names, state attributes, and visibility conventions; helper-unit tests cannot detect a `.show`/`.is-visible` mismatch. Reserve execution budget for one real browser pass and delivery instead of spending it all on skill loading, research, or candidate files.
- Run the smallest relevant automated check in a verified isolated environment; never point tests at a live business database. Preserve any pre-existing browser storage before synthetic tests and restore it afterward; do not clear an origin's keys merely because the current tasks look like test data.
- Open the rendered target route in a browser when access exists; confirm the target URL and an application-specific element before recording a UI result. Browser startup, `about:blank`, or a saved stylesheet proves tool/file availability, not a rendered application. Exercise the control as a user would, then assert visible output and underlying form/API value. A DOM click alone does not prove keyboard operation.
- Capture and inspect screenshots at relevant narrow and wide viewports; check clipping, overlap, and horizontal overflow. Use the real route where possible. Label a synthetic preview as a preview, not live-page verification. For popup-based tasks, capture both the idle page and the requested open form after its entry transition settles; an older screenshot must be labelled older, not presented as the latest revision.
- Treat automated results, screenshots, and QC as evidence for the source version they exercised. After a visual correction, invalidate affected earlier evidence, batch the remaining fixes, then run the relevant regression and browser checks once against the final version; do not restart unrelated audits. Report automated results, browser/visual evidence, untested gates, and whether production state or deployment changed as separate facts.
- If screenshot capture times out after successful interactions, retain those interaction results and retry capture separately with a bounded timeout; do not repeat mutations to recover a picture. Inspect the actual saved image before claiming visual success.
- **Differentiate Auth Gates from Active App Surfaces:** Never present a screenshot of an authentication lock screen, login modal, or connection error card as visual verification of an underlying application view (such as a chat canvas or timeline dashboard). If live authentication cannot be bypassed in an automated test, explicitly create a verified local fixture or mock boundary that unlocks the actual active application surface so the user can inspect the real layout, colors, and controls.
- **Verify Asset Delivery and Router Whitelists:** When adding new CSS or JS assets, verify that the backend router / privacy boundary actively serves the new asset path (e.g. check for HTTP 200 via `curl -I`, not just local file existence). If backend routes restrict static files by exact filename whitelist, bundle new styles directly into existing whitelisted files (`app.css`, `chat.css`) and update cache-buster query strings (`?v=...`) to avoid silent 404s in production client webviews.
- If authenticated access is unavailable, do not invent a session or claim the live authenticated screen was verified.

## 6. Approved date-picker reference

The green-and-white Kasir Bangunan date picker is the approved visual reference for date selection in that product: a clean white popover, Indonesian month and weekday labels, weekly date grid, restrained deep-green selected state, visible month navigation, and disabled dates outside `min`/`max`. Its native date input remains the source of form values (`YYYY-MM-DD`), with localized display and existing `input`/`change` events preserved.

For another product, reuse the interaction and verification lessons only; adopt that product's colors, typography, density, and motion. Do not impose the Kasir palette or a custom picker where the product does not need one.

## Completion gate

Call UI work complete only when requested scope is implemented and relevant behavior checks pass. Separate verified, not tested, and remaining scope in the handoff. A shared CSS foundation or screenshot alone does not prove every page or interaction complete. For packaged applications, distinguish source changes, browser checks, rebuilt/signed package, public download, and native-device checks; the existing download remains the old release until the new artifact is built, published, and read back. Load `android-apk-packaging` for Android release and WebView boundaries.

## Related workflows

For Kasir Bangunan form contracts, live bind-mount safety, and date input specifics, also load `kasir-bangunan-app-workflow`. For visual quality gates, load `design-qa-gatekeeper`; for real keyboard verification, load `browser-keyboard-accessibility-verification`.

Skipped: no universal palette or custom-control mandate. Add either only when the product brief or evidence requires it.

## Design Principles

Follow the design system's current project references and required research gate for interaction design; do not treat this execution standard as permission to reuse a default aesthetic.