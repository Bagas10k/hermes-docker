# Clipboard focus geometry and enlarged-text reflow

Author: Bagas Cihuy, Hermes Agent. Target UIUX-069; isolated fixture only.

## Procedure
1. Generate existing `native_clipboard_fixture.py`; keep the source renderer authoritative.
2. Snapshot every HTML element's computed font size BEFORE assigning scaled sizes. Reading children after scaling parents compounds inheritance. Record before/after samples; require exact 1x/2x within 0.01px rounding tolerance. This is a controlled text-size intervention, not browser page zoom.
3. Use real Tab from the outside control, then native Enter for non-idle states. Hold navigator.clipboard.writeText with a controlled promise, settle it for success/failure, and let application callbacks update labels/status. Freeze only the feedback reset timer; do not directly overwrite text/classes/ARIA to simulate state.
4. Measure the button and outline, viewport, breadcrumb box and all clipping ancestor axes. Use outline-width + outline-offset as conservative AABB expansion. Validate positive finite dimensions and reject missing evidence. Numeric/bool coercion and NaN must not become implicit success.
5. Observe 5 interior hit-test samples and explicit known foreground opaque rectangles. Include outline-only overlap, not merely button overlap. Ignore neither pointer-events:none nor nested clipping. This fixture model is NOT a generic CSS stacking-context resolver.
6. Send positive and negative browser records through the SAME Python audit. Require every matrix coordinate once and every named negative control. Do not accept precomputed detectedViolation booleans as proof.
7. Re-run contrast, motion, focus and native clipboard regressions separately. Serialize native clipboard runners to avoid shared clipboard interference.

## Matrix and gates
- 48 records: viewport 320/390/768 × normal/narrow breadcrumb container × 1x/2x computed-font scaling × idle/pending/success/failure.
- Narrow container uses max-width:220px on the breadcrumb content box. Border/padding are measured, not assumed.
- 36 non-idle records each observe one trusted keyboard click and one controlled clipboard write call.
- All records observe :focus-visible, solid 2px outline with 2px offset, reduced-motion query true and reduced transition duration.
- Button horizontal and vertical text extents, breadcrumb horizontal extent, outline clearance, clipping ancestors, sampled hit tests and document horizontal overflow are checked.
- Six negative controls: nested ancestor clipping, opaque standard overlay, pointer-events:none overlay, outline-only overlay, focus elsewhere, and nowrap width constraint. Each fails its named gate. Pointer-transparent and outline-only controls still pass button hit tests, demonstrating the blind spot.

## Actual defect and minimal fix
Parent's corrected runner found six geometry records failing before the renderer change. At 320px / enlarged text, search input intrinsic min-width caused document width 461 CSS px. Native Tab through search horizontally scrolled the document; the focused copy button subsequently extended left of the viewport. Source fix: `.dag-search-input{min-width:0}`. No forced scroll reset, clipping mask, layout rewrite or extra JS handler was needed. A preliminary two-property probe showed the overflow source; final matrix confirmed min-width alone sufficed.

Worker's first pass was rejected: it painted state labels directly, compounded inherited text scaling, ignored ancestor clips and accepted NaN. `references/uiux-069-review-rejection.json` records the audit. The initial import failure is only missing-helper evidence, not a CSS regression. `uiux-069-parent-initial-run.json` records the real pre-fix browser failures; `uiux-069-parent-gate-red.json` records the document-overflow unit assertion failing before the gate was added.

## Reproduction
From this skill directory, use `terminal`:
```text
python3 -B -m unittest discover -s scripts -q
NODE_PATH=<existing Playwright node_modules> node scripts/test_focus_reflow_chromium.cjs
python3 -B scripts/clipboard_focus_reflow.py references/uiux-069-browser.json
```
No installation needed. Runner starts an ephemeral loopback HTTP fixture, closes its browser/server, then invokes the Python gate and propagates failure.

Parent final verification: 364 Python methods (nine new); 48 passing state records and six correctly rejected controls. Chromium 156.0.8078.4. Separate regression records: 72 contrast, 12 accessibility/motion, 27 focus/status, nine native clipboard pointer and 24 native keyboard; minimap nine geometry/three lifecycle/33 controlled clipboard checks. Node: 39 clock cases, history suite with 11 controlled clipboard scenarios, focus suite. All 13 final parent commands exited 0. Exact commands/stdout and tested source hashes are in `uiux-069-parent-verification.json`; browser records in `uiux-069-browser.json`.

## Mechanism, evidence and trade-off
The measured outcome depends on font metrics, flex intrinsic minimum sizing, document scroll offset, native focus, clip ancestors and overlay geometry. Intervening only on the input min-width removes the reproduced horizontal overflow. This is causal evidence for this fixture, not a general guarantee for other pages.

Strict measurement metadata has higher decision value than adding more unvalidated records. Controls distinguish clipping, pointer interception and visual overlay geometry. Python tests prove gate behavior, not browser paint. No Amdahl speedup/p95 claims: neither timing fractions nor latency distributions were measured.

## Limits and next gap
- Known opaque foreground overlays and conservative axis-aligned outline bounds only. Sampled hit tests do not prove arbitrary visual clearance. Curved outline pixels, translucent paint, filters, masks, pseudo-elements and arbitrary stacking contexts require separate proof.
- Explicit font scaling is not native browser zoom, OS text scaling, physical high contrast, device pixel ratio or full accessibility certification.
- No screen-reader speech is exercised. DOM/AX regression evidence cannot establish announcements.
- Document-width check does not prove all page content is accessible or fully reflowed; the scrollable DAG remains a separate data surface.
- Next bounded target: nested scroll containers and container resize during focused/pending copy, with sticky overlay controls and native keyboard continuity. Do not pivot to unrelated drag-and-drop without evidence of that need.

## Primary sources checked
- https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html — supports scaling to 200% by at least one user-agent mechanism; our explicit intervention is narrower than a native zoom claim.
- https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html — AA condition is not entirely hidden; this fixture's full-outline containment gate is deliberately stricter, not a verbatim WCAG requirement.
- https://developer.mozilla.org/en-US/docs/Web/API/Document/elementFromPoint — pointer-events:none elements are ignored by hit testing.
Primary excerpts retrieved by parent via agent-reach/Jina. Reviewer suggestions were treated as hypotheses; a z-index integer comparison is not a general stacking-context proof.
