# UIUX-070 Study Plan: Nested Scroll Containers, Container Resize & Focus Continuity

Target: UIUX-070 bounded regression study
Author: Bagas Cihuy & Hermes Agent

## Objectives and Scope
1. Nested scroll containers: Outer scroll container (overflow wrapper around `<section aria-label="Navigasi riwayat">`) and inner scroll container (`#dag-breadcrumbs` with horizontal overflow).
2. Container-only resize: Shrink container width, then regrow to normal width while window dimensions (`innerWidth`, `innerHeight`) remain strictly unchanged.
3. Pending write continuity: Trigger native Enter on focused copy button to invoke real application `copyLineageToClipboard()`, holding controlled `writeText` promise.
4. Focus continuity: Validate that throughout nested scrolling (both outer and inner offsets strictly > 0) and container resize, the copy button maintains identity (`sameNode: true`, `isConnected: true`), remains active element (`document.activeElement === button`), and retains `:focus-visible`.
5. Application settlement: Resolve (`success`) or reject (`failure`) via real application promise settlement (no injected DOM labels).
6. Keyboard navigation roundtrip: Execute native Tab from copy button to expected neighbor and Shift+Tab back, verifying navigation continuity after resize.
7. Real position:sticky overlay negative controls: Deploy `position: sticky` opaque overlays (`pointer-events: auto` and `pointer-events: none`) inside the scroll container, evaluated by the SAME extractor and geometry gate.

## Matrix Definition
- Viewports: 320, 390, 768 CSS px
- Font scales: 1x, 2x computed-font scaling
- Settlement outcomes: 'success', 'failure'
- Matrix size: 3 × 2 × 2 = 12 comprehensive phase-tracked records
- Multi-phase records:
  - `initial`: Initial focus via native Tab from `#outside`
  - `pending`: Enter pressed, controlled `navigator.clipboard.writeText` held pending
  - `scrolled`: Both outer (`scrollTop > 0`) and inner (`scrollLeft > 0`) scroll offsets updated
  - `shrunk`: Outer container width reduced, window size unchanged
  - `regrown`: Outer container width restored, window size unchanged
  - `settled`: Application callbacks settle state ('Tersalin!' on resolve, 'Gagal menyalin' on reject)
  - `roundtrip`: Keyboard Tab to neighbor and Shift+Tab return verified

## Predicted Outcomes
1. Button DOM Identity and Focus:
   - Prediction: Button node identity will remain identical across all phases (`sameNode: true`, `isConnected: true`).
   - Prediction: `document.activeElement` will remain the copy button during scroll and resize operations without requiring programmatic `.focus()` re-invocation.
2. Geometry Containment & Clearance:
   - Prediction: As nested containers scroll, button bounding rect moves in viewport coordinates but remains within the conservative outline bounds and ancestor clipping rectangles.
   - Prediction: At 2x text scale, text fits within button client bounds without horizontal or vertical clipping.
3. Keyboard Navigation Continuity:
   - Prediction: Native Tab from `.dag-breadcrumb-copy-btn` will move focus to the next focusable sibling/descendant (`g` in SVG DAG or breadcrumb item), and Shift+Tab will return focus deterministically to `.dag-breadcrumb-copy-btn`.
4. Sticky Overlay Negative Controls:
   - Prediction: `stickyOcclusionAuto` will fail both `hitTestPassed` (obscured by sticky overlay) and occlusion gate.
   - Prediction: `stickyOcclusionPointerEventsNone` will pass `hitTestPassed` (proving the elementFromPoint blind spot) but will be caught and rejected by the shared geometry AABB occlusion gate.
5. Regressions:
   - Prediction: All existing 364 Python unit tests and existing Chromium suites (contrast, accessibility, native clipboard) will remain 100% green without modification.
