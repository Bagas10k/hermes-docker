# Pending clipboard under nested scroll and container resize

Author: Bagas Cihuy, Hermes Agent. UIUX-070, isolated fixture, not production certification.

## Contract and reproduction
From the skill directory, call `terminal` with:
```text
python3 -B -m unittest discover -s scripts -q
NODE_PATH=<existing Playwright node_modules> node scripts/test_nested_reflow_chromium.cjs
python3 -B scripts/clipboard_nested_reflow.py references/uiux-070-browser.json
```
The Node runner serves the actual renderer on an ephemeral loopback HTTP server, closes browser/server, then invokes the Python gate. It imports the same geometry extractor used by UIUX-069; that older runner now has a require.main guard. No new package or runtime handler.

## Reusable procedure
1. Snapshot all computed font sizes before applying explicit 1x/2x scaling. This is not page zoom. Put the existing section in an outer vertical scroller and breadcrumbs in an inner horizontal scroller. The stress fixture intentionally sets breadcrumb min-width:1000px, nowrap and right padding; it is not evidence of normal breadcrumb wrapping.
2. Native Tab reaches the copy button. Capture strict node identity and use native Enter to start a controlled write promise. Let real application callbacks own label/status/copy class; never paint expected states manually.
3. Sample initial and pending. Scroll outer vertically by 30px and inner horizontally by 25px in the chosen direction; verify both actual offsets changed, not merely that scroll setters ran.
4. Shrink the outer container to 250/310/660 CSS px at viewport 320/390/768, then remove its max-width to regrow. Verify unchanged window size, preserved perturbed scroll offsets, same connected focused node and geometry. Never call scrollIntoView or focus to repair the intervention.
5. Resolve or reject the controlled promise; inspect the actual application outcome. Tab reaches SVG node alpha (DOM order, not graph root), Shift+Tab returns. Normal native tab scrolling is allowed during this roundtrip and is not a no-scroll guarantee.
6. Bind nested metadata to underlying measurements: viewport, font, container, expected state per phase, window dimensions and activation counters. Audit all phases with the same Python geometry gate. Require complete unique matrix coordinates.
7. For sticky negative controls, insert a known opaque foreground element with zero net flex footprint. Measure normal-flow left with relative positioning, restore sticky, and record left at two actual scroll offsets. Both rectangles must remain at clip-left + inset while normal flow is beyond threshold. Pointer auto must intercept; pointer none must pass hit-testing yet fail rectangle occlusion. Require no unrelated failures.

## Evidence and parent corrections
Worker's initial gate accepted an entire success measurement in the shrink phase, unrelated sequence metadata and an arbitrary next focused element. It also checked only the sticky CSS property, not stuck behavior. `uiux-070-parent-red.json` records five failing regression tests plus one missing-helper error. The missing helper is not evidence of a browser defect.

Parent added phase/metadata binding, extent validation, exact neighbor identity and a sticky threshold proof. The first explicit neighbor assertion expected root and failed; source markup established alphabetical SVG DOM order starts with alpha. The expectation was corrected against the renderer, not loosened to any node. No application source changed.

Final parent evidence: `uiux-070-parent-verification.json` records 15 executed commands, exit codes, stdout, source SHA-256 and browser artifact hashes. `uiux-070-browser.json` holds raw measurements.
- 380 Python unittest methods, including 16 new methods (synthetic gate inputs, not browser observations).
- 12 browser sequences: 3 viewport widths × 2 explicit font scales × 2 settlement outcomes.
- Seven measured phases per sequence: initial, pending, scrolled, shrunk, regrown, settled, roundtrip; 84 phase measurements in total.
- Six browser negative controls: sticky auto, sticky pointer-none, ancestor clipping, outline-only fixed overlay, focus elsewhere and text overflow.
- Sticky controls: scrollLeft 831 → 841; overlay left remains 106.78125; normal-flow left -721.21875; clip left 20 + inset 86.78125. Both controls fail only occlusion.
- Separate regressions: UIUX-069 48 records/six negatives; contrast 72; accessibility/motion 12; focus/status 27; native clipboard pointer nine and keyboard 24; minimap nine geometry, three lifecycle, 33 controlled clipboard checks. Do not sum these into one accessibility score.
- Chromium 156.0.8078.4; all final commands exit zero. Native clipboard checks were serialized.

## Mechanism, belief update and trade-offs
Outcome depends on native focus, scroll offsets, clip rectangles, container constraints, typography and async application state. The measured modest scroll/shrink interventions preserved focus and full outline clearance in this fixture. More severe movement can deliberately clip any nonsticky target; no universal visibility guarantee follows.

Negative tests falsified the initial evidence validator despite its green suite. A phase-bound contract has higher information value than a larger unbound record count. Sticky normal-flow and stuck measurements distinguish CSS property presence from the requested behavior. No numerical Bayesian probability, speedup, p95 or Amdahl claim is supported by these functional tests.

Reuse shared measurement/gates rather than generalizing into a CSS paint engine. Constraints are safety, correct state, finite geometry, exact matrix, native input and no production mutation. Controlled promises freeze only the feedback reset timeout; real completion timing is outside this study.

## Limits and next gap
The gate uses conservative outline AABBs, known opaque foreground rectangles and sampled hit tests. It does not prove arbitrary stacking order, curved pixel coverage, pseudo-elements, translucency, screen-reader speech, native zoom, physical high contrast or full WCAG. The new matrix runs reduced-motion; normal/forced-color/motion transitions are separate regressions, not all nested combinations.

Identity/focus snapshots cannot exclude a transient blur/refocus between phases. Next bounded target: record focusin/focusout events during pending scroll/resize and deliberate user departure; completion must not steal focus or restart scrolling. No scheduler changes are needed.

## Primary reference and review disposition
Parent retrieved MDN via agent-reach/Jina: https://developer.mozilla.org/en-US/docs/Web/CSS/position — sticky uses nearest scrolling mechanism, an inset on its active axis, and behaves relative until threshold. This grounds the measured threshold proof, not a general layout guarantee.

The independent review is a proposal, not execution evidence. Its proposed total of 48 positive records was not a computed acceptance count; the implemented and programmatically counted matrix is 12 sequences/84 phases. It also speculated about the next control: the actual renderer identifies alpha. Synchronous geometry reads can force layout; waiting a frame is coordination, not proof of pixel paint or all ResizeObserver delivery. Retain these limits when reusing the review.
