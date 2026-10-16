# UIUX-071 Study Plan: Event-Level Focus Continuity, Deliberate Departure & Settlement Stability

Target: UIUX-071 bounded regression & focus continuity research
Author: Bagas Cihuy & Hermes Agent

## 1. Objectives and Scope
1. **Event-Level Continuity**: Instrument real native `focusin` and `focusout` events (bubbled to document/window) across nested scroll and container shrink/regrow operations while clipboard write is pending.
2. **Transient Detection**: Detect transient blur/refocus glitches between discrete DOM snapshots that traditional snapshot-only audits miss.
3. **Deliberate Keyboard Departure**: Validate that deliberate user navigation (Tab forward, Shift+Tab backward) while clipboard write is pending moves focus deterministically to exact target node identities.
4. **Settlement Focus Stability**: Verify that asynchronous promise settlement (`resolve` on success, `reject` on failure) respects deliberate departure without focus theft (no stealing focus back to the copy button, including steal-and-return).
5. **Scroll Stability**: Compare scroll offsets after departure has quiesced to post-settlement offsets to ensure promise settlement introduces zero unsolicited scroll.
6. **Shared Geometry Reuse**: For departed measurements, reuse shared geometry gates after explicitly specifying expected nonfocus without counterfeiting `focused = true`.
7. **Negative Controls**: Validate 4 explicit negative controls:
   - `transientBlurRefocus`: blur() + focus() between good snapshots.
   - `completionFocusTheft`: copy button focus theft on settlement (steal and steal-and-return).
   - `transientScrollRestore`: scroll offset mutation + restoration during settlement.
   - `wrongDepartureIdentity`: focus navigation to unexpected DOM targets.

## 2. Matrix Definition
- Viewports: 320, 390, 768 CSS px
- Font scales: 1x, 2x computed font scaling
- Settlement outcomes: 'success', 'failure'
- Departure modes: 'stay', 'forward', 'backward'
- Matrix size: 3 × 2 × 2 × 3 = 36 comprehensive phase-tracked records
- Multi-phase records (7 phases per record):
  - `initial`: Tab navigation from `#outside` to `.dag-breadcrumb-copy-btn`
  - `pending`: Enter pressed, controlled `navigator.clipboard.writeText` promise held
  - `scrolled`: Nested outer (`scrollTop > 0`) and inner (`scrollLeft > 0`) offsets modified
  - `shrunk`: Outer container width reduced, window dimensions strictly unchanged
  - `regrown`: Outer container width restored, window dimensions strictly unchanged
  - `departed`: Deliberate departure action:
    - `stay`: No navigation key; copy button retains focus
    - `forward`: Native Tab pressed to `g[data-node="alpha"][role="button"]`
    - `backward`: Native Shift+Tab pressed to `button.dag-breadcrumb-item.active[data-breadcrumb-node="anak-雪"]`
  - `settled`: Controlled promise settlement (`resolve` or `reject`), UI status updated

## 3. Node Identities
- Copy button: `button.dag-breadcrumb-copy-btn`
- Forward departure target: SVG element `g[data-node="alpha"][role="button"]`
- Backward departure target: HTML button `button.dag-breadcrumb-item.active[data-breadcrumb-node="anak-雪"]`

## 4. A Priori Predictions
1. **Native Event Order and Monotonicity**:
   - Event listeners attached BEFORE native Tab navigation begins will observe strictly monotonic sequence numbers (`seq`).
   - Observed native event order during focus departure is `focusout` on the departing element followed by `focusin` on the arriving element.
2. **Focus Continuity During Pending Lifecycle**:
   - Zero `focusin` or `focusout` events will occur during `pending`, `scrolled`, `shrunk`, and `regrown` phases.
   - The copy button maintains unbroken focus across nested scrolling and container resizing without requiring programmatic re-focusing.
3. **Respect for Deliberate Departure**:
   - Forward Tab moves focus exclusively to `g[data-node="alpha"][role="button"]`.
   - Backward Shift+Tab moves focus exclusively to `button.dag-breadcrumb-item.active[data-breadcrumb-node="anak-雪"]`.
   - Promise settlement (success or failure) fires exactly zero `focusin` or `focusout` events when focus has departed; active element remains the departed target.
4. **Scroll Stability**:
   - While keyboard departure navigation may legitimately adjust container scroll to bring the newly focused element into view, promise settlement itself will cause zero scroll offset changes (`settled.scroll == departed.scroll`).
5. **Fail-Closed Validation and Negative Controls**:
   - All 4 negative controls (`transientBlurRefocus`, `completionFocusTheft`, `transientScrollRestore`, `wrongDepartureIdentity`) will be caught and rejected by the validator.
   - Non-finite numbers (NaN, Inf), boolean coercion, malformed event traces, or missing phases will raise immediate validation errors.
6. **Regressions**:
   - All existing 380 Python unit tests and existing Chromium suites will remain 100% passing.

## 5. Limitations and Truth Preserved
- Fixture environment with controlled mock clipboard promises (`writeText`).
- Explicit computed CSS font scaling (`1x`, `2x`), not OS DPI or native browser zoom.
- Tested on Chromium headless via Playwright; does not certify screen reader announcement behavior or entire WCAG checklist.
- Conservative geometric bounds and known foreground overlays; not arbitrary CSS 3D/stacking context proof.
