# UIUX-072 Study Plan: Stable Clipboard Status Layout Under Default Scroll Anchoring, Feedback Reset Continuity & Neighbor Geometry Audit

Target: UIUX-072 bounded regression, default scroll anchoring stabilization & focus continuity research
Author: Bagas Cihuy & Hermes Agent

## 1. Objectives and Scope
1. **Default Scroll Anchoring Stabilization**: Eliminate settlement and reset scroll displacement under browser default `overflow-anchor: auto` by structurally reserving status layout space via CSS Grid stacking, without guessing fixed pixel heights or hiding overflow.
2. **Three-Way Anchoring Comparison**: Honestly contrast:
   - Stable layout under default `overflow-anchor: auto` (new target).
   - Unstable layout under default `overflow-anchor: auto` (reproducing the 38px settlement scroll jump on viewport 390 / scale 2 / failure / forward).
   - Anchor opt-out under `overflow-anchor: none` (prior workaround).
3. **Feedback Timer Reset Continuity**: Extend observation through the 1500ms feedback timeout reset phase using controlled virtual timer advance that executes the real registered app callback (`window.setTimeout`). Validate that button text, status text, and visual feedback cleanly return to idle state with zero unsolicited scroll, zero focus theft, and unbroken event continuity.
4. **Focused Neighbor Geometry & Focus Cue Audit**: Validate geometry and accessibility gates for the active focused element across all phases:
   - For `stay`: Copy button (`button.dag-breadcrumb-copy-btn`).
   - For `forward`: SVG node item (`g.node-item[data-node="alpha"][role="button"]`), with explicit focus cue fix (`outline: 2px solid #2563eb`).
   - For `backward`: Breadcrumb button (`button.dag-breadcrumb-item.active[data-breadcrumb-node="anak-雪"]`).
   - Gates: Exact target identity, activeElement match, `:focus-visible` match, `outlineStyle === 'solid'`, `outlineWidth >= 2`, no clipping within active container bounds, no occlusion by known opaque overlays.
5. **Full Matrix Verification**: Test the complete 36-cell matrix under default `overflow-anchor: auto` across 8 lifecycle phases:
   `initial` -> `pending` -> `scrolled` -> `shrunk` -> `regrown` -> `departed` -> `settled` -> `reset`.
6. **Negative Controls**: Validate 6 explicit negative controls:
   - `oldUnstableAuto`: Old unreserved layout under default `overflow-anchor: auto` shifts scroll offset during settlement.
   - `transientBlurRefocus`: Transient blur/focus cycle during container resize.
   - `completionFocusTheft`: Focus stolen back to copy button during promise settlement.
   - `resetFocusTheft`: Focus stolen back to copy button during feedback timer reset.
   - `transientResetScroll`: Scroll position disturbed and restored during timer reset.
   - `wrongDepartureIdentity`: Focus departed to an unintended element (`#outside`).

## 2. Matrix Definition
- Viewports: 320, 390, 768 CSS px
- Font scales: 1x, 2x computed font scaling
- Outcomes: 'success', 'failure'
- Departure modes: 'stay', 'forward', 'backward'
- Matrix size: 3 × 2 × 2 × 3 = 36 sequences
- Phases per sequence (8 phases):
  1. `initial`: Native Tab navigation from `#outside` to `.dag-breadcrumb-copy-btn`.
  2. `pending`: Native Enter key activation; controlled clipboard promise held.
  3. `scrolled`: Nested outer (`scrollTop += 30`) and inner (`scrollLeft += 25`) scroll offsets applied.
  4. `shrunk`: Outer container width narrowed to test container resize stability.
  5. `regrown`: Outer container width restored to 100%.
  6. `departed`: Deliberate departure action:
     - `stay`: No departure key pressed; copy button retains focus.
     - `forward`: Native Tab key pressed to `g.node-item[data-node="alpha"][role="button"]`.
     - `backward`: Native Shift+Tab key pressed to `button.dag-breadcrumb-item.active[data-breadcrumb-node="anak-雪"]`.
  7. `settled`: Controlled promise settlement (`resolve` on success, `reject` on failure); status updated.
  8. `reset`: Controlled virtual timer advance executing registered 1500ms callback; status and copy button restored to initial state.
- Total positive measurements: 36 × 8 = 288 phase measurements.

## 3. Node Identities & Geometries Audited
- Copy button: `button.dag-breadcrumb-copy-btn`
- Forward neighbor: SVG `g.node-item[data-node="alpha"][role="button"]` inside `#dag-view`
- Backward neighbor: HTML `button.dag-breadcrumb-item.active[data-breadcrumb-node="anak-雪"]` inside `#dag-breadcrumbs`
- Focus cues:
  - Copy button: `outline: 2px solid #2563eb`, `outline-offset: 2px`
  - SVG node: `.node-item:focus-visible { outline: 2px solid #2563eb; outline-offset: 2px }`
  - Breadcrumb button: Native focus ring / `outline: 3px solid #1669e8`

## 4. A Priori Predictions
1. **Structural Reservation Prevents Scroll Anchoring Drift**:
   - Reserving space via CSS Grid stacking (`.dag-status-region` with invisible template items `.dag-status-reserve` sharing `grid-area: status` with `#status`) establishes an invariant bounding box across all text variants ("Menyalin...", "Silsilah...", "Gagal...", "Versi...").
   - With delta height = 0px above the scroll anchor, browser default `overflow-anchor: auto` produces delta scroll = 0px across both settlement and reset phases.
2. **Old Unreserved Layout Fails Under Default Anchoring**:
   - In unreserved layout, `#status` text changes cause a 38px height jump at viewport 390 / scale 2 / failure, causing `outer.scrollTop` to jump from 340 to 378px under `overflow-anchor: auto`.
3. **Timer Reset Preserves Event and Scroll Invariants**:
   - Virtual timer advance fires the real registered timeout callback without stealing focus or altering scroll offsets (`reset.scroll === settled.scroll === departed.scroll`).
   - Zero `focusin` or `focusout` events will occur during `reset` when focus has departed (`stay` retains focus on copy button without blur/refocus).
4. **Focused Neighbor Geometry Adherence**:
   - The active neighbor in `departed`, `settled`, and `reset` phases meets all geometry gates: non-clipped, visible focus outline (`outlineStyle === 'solid'`), non-occluded by `#dag-diff-popover`.
5. **Fail-Closed Validation**:
   - All 6 negative controls will be cleanly rejected by the Python validator with deterministic failure reasons.
   - Non-contiguous sequence IDs, clock reversals, or untrusted events will immediately fail validation.
6. **Backward Compatibility**:
   - All existing 400 Python unit tests and existing Chromium suites (`test_focus_events_chromium.cjs`, `test_nested_reflow_chromium.cjs`, etc.) remain 100% passing.

## 5. Limitations and Truth Preserved
- Tested in Chromium headless (Playwright) on Linux; not cross-engine or cross-OS physical clipboard.
- Explicit computed CSS font scaling (`1x`, `2x`), not native browser pinch-zoom or OS DPI scaling.
- Does not test screen reader speech output or certify full WCAG compliance.
- Virtual timer advance triggers the exact application callback registered in `setTimeout(..., 1500)`, marked explicitly in evidence.
