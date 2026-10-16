# Independent Review: UIUX-070 Research Plan & Focus-Geometry Gate

**Target:** UIUX-070 (*Clipboard focus continuity in nested scrolling and container resize*)  
**Component:** `spanning-cell-2d-grid` (`scripts/history_browser.js`, `scripts/clipboard_focus_reflow.py`)  
**Scope:** Review-only audit of research plan, gate falsification integrity, and false-proof risks.

---

## 1. Executive Summary & Core Mechanism

UIUX-070 investigates whether keyboard focus on `.dag-breadcrumb-copy-btn` and its 2px solid + 2px offset focus outline maintain unbroken visual and DOM continuity while **nested scroll containers** and **container-only resize** shift layout during a controlled pending clipboard write (`navigator.clipboard.writeText`).

### Harness Repositioning vs. Component Resilience (The Core Dilemma)
A critical false-proof risk in browser automation testing is **tautological repositioning**:
- If the test harness invokes `element.scrollIntoView()`, triggers implicit scroll-on-focus, or manually repositions scroll containers after container resizing, the test proves only that *the harness can bring an element back into view*, not that the component's layout architecture withstands nested reflow.
- **Intervention Contract:** The test harness must execute only two physical layout perturbations during the pending state: (a) mutate container box inline styles / parent constraints (shrink and regrow), and (b) scroll nested scrollable parents (`scrollTop` / `scrollLeft`). The harness must NEVER call `scrollIntoView()` or programmatic refocusing after the initial Tab navigation.
- If the component's layout allows the button to be scrolled under an ancestor clip or behind a sticky bar without wrapping or preserving clearance, the audit MUST fail.

---

## 2. Primary Documentation & Standards Grounding

1. **CSS Positioned Layout Module Level 3 (`position: sticky`):**
   - *Spec reference:* [W3C CSS Positioned Layout Level 3 § 6.2](https://www.w3.org/TR/css-position-3/#sticky-pos).
   - A sticky element is positioned relative to its *nearest scrolling ancestor* (flow root) and bounded strictly by its *containing block*.
   - *Key Gotcha:* If any ancestor sets `overflow: hidden`, `auto`, or `scroll`, it establishes the scrolling context. If placed within an incorrect containing block, a sticky element ceases sticking once the block scrolls offscreen. Stacking context rules mean a sticky overlay without explicit `z-index` or DOM precedence will render *below* subsequent positioned siblings, rendering visual occlusion testing invalid.

2. **CSSOM View Module & Hit-Testing (`elementFromPoint`):**
   - *Spec reference:* [W3C CSSOM View Module § 10.1](https://www.w3.org/TR/cssom-view-1/#dom-document-elementfrompoint).
   - `document.elementFromPoint(x, y)` explicitly ignores elements styled with `pointer-events: none`. If an overlay with `pointer-events: none` visually covers the focused outline, `elementFromPoint` returns the button underneath.
   - *Proof Requirement:* The audit cannot rely on hit-testing alone; it must verify bounding box intersection (`intersects(outline, overlay)`) to catch pointer-transparent occlusions.

3. **HTML Event Loop & ResizeObserver Pipeline:**
   - *Spec reference:* [WHATWG HTML Event Loop § 8.1.7.3 (Update the rendering)](https://html.spec.whatwg.org/multipage/webappapis.html#update-the-rendering) & [W3C ResizeObserver § 3.2](https://www.w3.org/TR/resize-observer/#html-event-loop).
   - ResizeObserver callbacks execute during the "update the rendering" phase *after* style/layout calculations and *before* paint.
   - Synchronous DOM reads immediately after container style assignment can read layout geometry from an incomplete frame or trigger layout thrashing. Harness must await `requestAnimationFrame` and `Promise.all(el.getAnimations().map(a => a.finished))` before sampling measurements.

4. **WCAG 2.2 Focus Visibility & Reflow Bounding:**
   - *Spec references:* [WCAG 2.2 SC 2.4.11 Focus Not Obscured (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html) & [SC 1.4.10 Reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html).
   - While WCAG SC 2.4.11 requires that the item is not *entirely* obscured, our fixture gate enforces a stricter zero-occlusion conservative AABB standard.
   - Explicit font scaling (1x / 2x via computed style snapshot) isolates typography reflow from browser zoom engine artifacts; it must NOT be claimed as full WCAG 200% page zoom certification.

---

## 3. False-Proof Risks & Falsification Gates

| # | False-Proof Risk | Mechanism of Failure | Required Falsification Check |
|---|---|---|---|
| **R1** | **Artificial Harness Centering** | Harness calls `scrollIntoView()` or resets scroll after container resize, masking real overflow clipping. | Forbid all `scrollIntoView()` or manual re-centering calls after initial Tab arrival. Audit record must verify container scroll offsets remain at perturbed coordinates. |
| **R2** | **Window Resize Conflation** | Harness calls `page.setViewportSize()` instead of mutating container CSS, triggering media query reflow rather than container reflow. | Assert `window.innerWidth` and `innerHeight` are strictly constant (`=== meta.viewport`). Record container `clientWidth` shrink delta (`deltaWidth < 0`) and regrow delta. |
| **R3** | **Vacuous Nested Scrolling** | Test claims nested scroll testing, but only one container (or zero) actually scrolled. | Record `outerScroll` and `innerScroll` (both X and Y). Assert `(deltaOuterX > 0 || deltaOuterY > 0) && (deltaInnerX > 0 || deltaInnerY > 0)`. |
| **R4** | **DOM Node Identity Churn** | Re-render during resize or state transition destroys the `<button>` and creates a new one, briefly dropping focus to `<body>`. | Capture `const initialNode = document.activeElement;`. Assert `document.activeElement === initialNode` (strict JS object equality) across pending, resize, and settled states. |
| **R5** | **Tab Sequence Disruption** | Flex wrapping or container clipping causes Tab/Shift+Tab to skip elements or jump to offscreen clipped nodes. | After settle, trigger `page.keyboard.press('Shift+Tab')` and verify `activeElement` matches the exact preceding breadcrumb item; then `Tab` returns to copy button, then `Tab` reaches the exact next control (`#dag-search-input` or minimap toggle). |
| **R6** | **Sticky Overlay Ineffective** | Sticky element placed in an unscrollable containing block fails to stick, failing to occlude button in negative control. | Negative controls must use `position: sticky; top: ...` inside an actively scrolled ancestor. Must measure `stickyRect` overlapping `outlineRect` before checking gate failure. |
| **R7** | **Hit-Test Blind Spot on Sticky Overlays** | `pointer-events: none` on sticky overlay bypasses `elementFromPoint()`. | Dedicated negative control `stickyOcclusionNone`: assert `hitTestPassed === true` AND Python audit marks `occlusion` failure via bounding AABB. |
| **R8** | **Asynchronous Layout Race** | Metrics read before ResizeObserver / animation frame finishes. | Await `requestAnimationFrame` + `document.fonts.ready` + animation completion before invoking `measure()`. Assert zero `pageerror` (no `ResizeObserver loop limit exceeded`). |

---

## 4. Concrete Acceptance Checks for UIUX-070 Gate

To prevent regression and guarantee mathematical integrity, the UIUX-070 gate must satisfy:

1. **Matrix Dimensions (48 Positive Records):**
   - Viewport: `[320, 390, 768]`
   - Font scale: `[1, 2]` (pre-snapshotted baseline, exact factor within ±0.01px)
   - Layout sequence: Pending with Nested Scroll + Shrink $\to$ Regrow $\to$ Settle (Success / Failure)
   - Every cell must be validated via the shared Python `clipboard_focus_reflow.py` pipeline.

2. **Negative Control Suite (Minimum 7 Controls, Evaluated by Same Pipeline):**
   - `nestedScrollClipping`: Nested container scrolled such that button outline intersects parent clip edge $\to$ fails `clipping`.
   - `containerShrinkClipping`: Container shrunk below button minimum reflow width $\to$ fails `clipping` or `text-fit`.
   - `stickyOcclusionAuto`: Sticky overlay (`pointer-events: auto`) overlapping outline $\to$ fails `occlusion` (`hitTestPassed: false`).
   - `stickyOcclusionNone`: Sticky overlay (`pointer-events: none`) overlapping outline $\to$ fails `occlusion` while `hitTestPassed: true` (proves blind spot).
   - `outlineOnlySticky`: Sticky overlay intersecting only the outline padding (not button body) $\to$ fails `occlusion` while `hitTestPassed: true`.
   - `unfocusedNode`: Focus shifted away during layout shift $\to$ fails `focus`.
   - `nodeIdentityLoss`: Button replaced in DOM (even with same class/text) $\to$ fails `continuity`.

3. **Numeric Schema Strictness:**
   - All geometry coordinates (`buttonRect`, `barRect`, `clips`, `stickyOverlays`) must be finite positive numbers (`math.isfinite()`).
   - Booleans, strings, `NaN`, or missing keys must fail-closed with explicit `ValueError`.

4. **Claim Boundary Verification:**
   - Manifest must record explicit boundary disclosures:
     - Explicit computed-font scaling, NOT native browser page zoom or OS accessibility text scaling.
     - Axis-aligned bounding box (AABB) outline clearance, NOT full pixel-level shader / curved border anti-aliasing.
     - Known opaque foreground rectangles + sampled hit testing, NOT general CSS stacking-context resolution.
     - Controlled `writeText` promise mocking, NOT OS clipboard daemon integration.
     - DOM active element and keyboard event continuity, NOT screen reader speech announcement verification.

---

## 5. Likely Worker Gaps & Remediation Guide

1. **Gap:** Worker creates sticky overlays attached to `document.body` where no scroll threshold is crossed.
   - *Remediation:* Attach sticky overlays inside the scrolling container (e.g. `.dag-container` or a dedicated sticky header inside `#dag-breadcrumbs`), ensuring scroll offset exceeds `top` threshold so the element enters the stuck state.
2. **Gap:** Worker checks `document.activeElement.tagName === 'BUTTON'` instead of checking exact instance continuity.
   - *Remediation:* Worker must store `window._activeButtonRef = document.activeElement` during initial focus and verify `window._activeButtonRef === document.activeElement` at every subsequent phase.
3. **Gap:** Worker only tests container shrink, omitting container regrow.
   - *Remediation:* Container geometry must be tested after both shrink (`width: 220px`) and regrow (`width: 100%`) to catch CSS flexbox/grid layout latching bugs.
4. **Gap:** Worker uses `setTimeout` instead of event-loop coordination for settle.
   - *Remediation:* Rely on `Promise` resolution of `settleCopy.resolve()` followed by `page.waitForFunction()` on button text change and `requestAnimationFrame`.
