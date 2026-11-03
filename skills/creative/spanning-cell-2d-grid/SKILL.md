---
name: spanning-cell-2d-grid
description: Use when indexing merged cells in virtual grids.
version: 0.61.0
author: Bagas Cihuy, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [uiux, virtualization, merged-cells, spatial-index, frozen-panes, nested-headers, accordion-columns, spring-physics, webgl-instancing, glyph-atlas, gesture-arbitration, pinch-to-zoom, msdf-fonts, sdf-shaders, selection-box, marquee-drag, multi-touch-pan, rotation-disambiguation, kerning-pairs, subpixel-typography, keyboard-navigation, roving-tabindex, multi-range-selection, disjoint-selection, clipboard-paste, tabular-paste, formula-translation, merge-arbitration, undo-redo-journal, transaction-history, vector-clock, operational-transformation, conflict-resolution, dag-visualization, svg-topology, click-to-checkout, diff-badge, hover-diff-inspector, spatial-navigation, popover-tooltip, breadcrumbs-trail, viewport-auto-centering, minimap-radar, drag-viewport-pan, collapsible-minimap, breadcrumb-shortcuts, breadcrumb-badges, localstorage-persistence, minimap-scale-presets, clipboard-export, search-omnibar, filter-highlight]
    related_skills: [dynamic-fenwick-2d-grid, unified-2d-virtual-panes]
---

# Spanning Cell 2D Grid

## When to Use
Use for discovering merged cells whose anchor is outside a virtual viewport. Includes a bounded fixed-size DOM snapshot adapter, not a production spreadsheet or proof of zero CLS.

## Prerequisites
Python 3 with SQLite compiled with R-tree support. `rtree_i32` stores exact signed-32-bit coordinates; no package installation or production database is needed.

## How to Run
Use `terminal` with `python3 -m unittest discover -s <skill-dir>/scripts -v`.
Import `SpanIndex` from `scripts/spanning_grid.py`; use it as a context manager.

## Contract
`SpanIndex(rows, cols)` accepts positive integers below 2**31. `add(id,r0,c0,r1,c1)` stores nonempty half-open rectangles. IDs are nonnegative signed-64-bit integers. Bools, fractional coordinates, duplicate IDs, out-of-bounds and overlapping merges raise ValueError without mutation.
`query(r0,c0,r1,c1)` returns sorted unique IDs, original anchor, full bounds and clipped bounds. Empty windows return no matches. Touching edges do not intersect.

## Procedure
1. Convert scroll pixel coordinates to row/column windows using the separate dimension index; keep one consistent geometry snapshot.
2. Insert merge rectangles using stable IDs. Verify overlap rejection before accepting metadata.
3. Query by rectangle intersection, never anchor containment. Verify that an offscreen anchor still yields one logical cell.
4. Render one logical owner per ID, preserve its original origin, and clip presentation to the returned clip. Suppress ordinary cells covered by the merge. Use scripts/dom_adapter.py: snapshot(index, window, row_px=32, col_px=96, budget=4096), then render_html(snapshot). Reject visible area above budget before allocation. String IDs preserve large integer identity. Group cells under ARIA rows with global one-based indices and full span attributes; keep one roving tab stop. Arrow navigation skips covered positions within the viewport.
5. Run deterministic tests before integration. Compare against a brute-force rectangle oracle.

## Asynchronous snapshot admission
Call beginSnapshotRequest() before dispatch and capture its token locally. Pass that token and the trusted snapshot to applySnapshot(token, snapshot) on completion; never use direct replaceWindow for async responses. Only the latest issued, not-yet-applied token can commit. A newer pending request invalidates older responses even before it finishes; failure leaves the previous display intact and requires retry or a new request, not an old-response fallback. Rejection happens before payload access or DOM replacement, preserving node identity and focus. Tokens are per-grid positive JS-safe integers, not server revisions; remount resets scope. Do not accept caller-invented tokens or mix resources in one gate. scripts/revision_gate.py supplies the matching synchronous Python model; commit callbacks must not reenter the gate and are responsible for mutation safety on failure.

Verification for v0.4.0: 24 unittest methods pass, including all 24 permutations of four responses, duplicate/future/invalid tokens, failure retry and exhaustion. Chromium checks at 390/768/1280 verify stale rejection before mutation, latest acceptance with focus preservation, duplicate/future rejection, external focus and one tab stop (references/browser-cycle-209.json). These are controlled response-order checks, not a real network integration or transactional DOM rollback proof.

## Bounded snapshot validation
Validate every decoded JSON snapshot before reading focus or creating DOM nodes. scripts/snapshot_schema.py and scripts/snapshot_schema.js enforce exact fields, finite bounded pixel geometry, integer logical bounds, unique safe IDs, coverage without overlap, and exact ownership. Visible area is capped at 4096. Empty windows require zero corresponding pixel dimension. Python and JS agree for JSON number semantics except Python intentionally requires int for integer fields; producers should serialize integer values without decimal notation.

Verification v0.5.0: 29 Python unittest methods pass; 14 malformed payloads at each of 3 Chromium widths preserve DOM identity, attributes, focus, logical state and applied revision with zero MutationObserver records. Valid retry using the same token succeeds. See references/browser-cycle-210.json. This is validation-before-mutation, not rollback for unexpected DOM API exceptions. Input must be decoded JSON, not objects with getters/proxies; byte limits before JSON parsing remain an integration responsibility. No network, screen-reader, CLS or latency guarantee follows from this evidence.

## DOM commit failure injection & transactional state restoration
Transactional checkpointing in scripts/dom_adapter.py and scripts/commit_recovery.py ensures that if an exception occurs during the DOM commit phase (detached node creation, container replaceChildren, geometry/attribute mutation, or focus selection), the entire pre-commit DOM tree, styles, ARIA attributes, logical cursor, focused element, and appliedRevision are restored atomically. The token remains valid and uncommitted, allowing an immediate clean retry without stale drift or desynchronization.

Verification v0.6.0 (UIUX-017): 35 Python unittest methods pass (6 new deterministic commit recovery and rollback tests in test_commit_recovery.py). Real Chromium tests across viewports 390, 768, and 1280 px verify that injected exceptions at `create_nodes`, `dom_mutation`, and `focus_restore` result in complete state/DOM restoration, zero revision advancement, and subsequent retry success with exactly 1 tab stop (references/browser-cycle-211.json).

## Dynamic status and unbroken revision IDs
- Mirror escaped idle/reset text in one aria-hidden reservation sibling before clipboard activation; synchronize on cursor changes. Use `min-width:0; overflow-wrap:anywhere` to wrap tokens without expanding the grid. Never clip status or breadcrumb text to pass geometry gates.
- Use normal inline text flow for long breadcrumb labels; an inline-flex badge can consume the label width under explicit font scaling. Verify text Range bounds and focused-neighbor outlines, not only scroll offsets. Reserving height costs space and does not make arbitrary text fit a viewport.
- Reject missing/zero dimensions, mismatched phase/measurement text, stale reservation and wrong breadcrumb identity. Short-ID evidence cannot satisfy a long-ID gate.
- Via `terminal`, run `python3 -B -m unittest discover -s scripts -q`, `NODE_PATH=<installed Playwright node_modules> node scripts/test_dynamic_status_chromium.cjs`, and `python3 -B scripts/clipboard_dynamic_status.py references/uiux-073-browser.json`. Retain event/neighbor, native clipboard and accessibility regressions.
- Evidence: 432 Python methods, 36 bounded Chromium sequences/288 phases, ten negative controls, one opt-out comparison; 18 parent commands exit 0 with unchanged source hashes. One long active payload is covered, not all localizations or pending cursor races. Details: [references/dynamic-status-reservation.md](references/dynamic-status-reservation.md).

## Clipboard ownership across checkout and disposal
- Invalidate the request token and cancel its feedback timer before replacing the copy node. An old OS write cannot be cancelled; its result must not mutate the current revision's status, reservation or button.
- Give one layer responsibility for focus: `draw(true)` selects the destination, so call `renderBreadcrumbs(cursor, !focus)` to suppress intermediate copy-button focus. Final snapshots alone miss a focus detour.
- Observe real timer registration, cancellation and deadlines. A cancelled flag before the deadline is insufficient. Inject negative faults into behavior, not reported timestamps; track node identity separately from DOM attributes.
- Keep font magnification on replacement nodes. Reject absent traces, missing suffix counters, nonfinite clocks, stale idle text, enabled disposed controls and late geometry changes. Compare heights within a revision, not across different revision text.
- Run via `terminal`: `python3 -B -m unittest discover -s scripts -q`; `NODE_PATH=<installed Playwright node_modules> node scripts/test_status_ownership_chromium.cjs`; `python3 -B scripts/clipboard_status_ownership.py references/uiux-074-browser.json`. Retain dynamic-text, event/neighbor and native clipboard regression runners.
- Scope and evidence: [references/status-ownership-races.md](references/status-ownership-races.md). API-triggered checkout is not proof of keyboard checkout, nested-scroll race geometry, arbitrary strings or screen-reader speech.


## Supporting References
- `references/uiux-milestones-specification.md`: Full 81KB detailed specifications for UIUX-018 through UIUX-072 milestones.

## Bounds and Trade-offs
SQLite R-tree prunes spatial searches without expanding each covered cell. Storage is O(M) for M merges, independent of span area. Pathological queries can visit O(M); sorting K hits adds O(K log K). No unconditional logarithmic bound or FPS guarantee is claimed. The connection is in-memory, single-thread-owned, and nonpersistent.

## Pitfalls
- Use rtree_i32, not float R-tree, for exact large row indices.
- Half-open comparisons must use strict inequalities; explicit empty-window rejection is necessary when a merge straddles that coordinate.
- Unit geometry tests do not establish browser layout stability, accessibility, keyboard navigation or screen-reader support.
- No remove/update API exists yet. Recreate the index for changed merge metadata.

## Verification
Twelve unittest methods cover index contracts, 500 seeded differential queries, snapshot ownership, geometry and allocation bounds. Generate fixture via terminal: python3 <skill-dir>/scripts/dom_adapter.py <output.html>. Browser evidence: references/browser-verification.json. Actual Chromium checks verify 13 unique gridcells, one merged owner/tab stop, exact geometry at widths 390/768/1280, four keyboard transitions, no document overflow and 13 AX gridcells. Reproduce using browser_exec, CDP Emulation.setDeviceMetricsOverride, bounding boxes, Input.dispatchKeyEvent and Accessibility.getFullAXTree. No screen-reader or CLS claim. Adapter expansion is O(V+K) plus sorting, capped by visible-area budget. Dynamic replacement is exposed as window.replaceWindow(snapshot) for trusted Python-generated snapshots. Preserve logical coordinates if visible; otherwise clamp to the new window. Restore DOM focus only when the old grid owned it; never steal external focus. An empty viewport has no cursor and makes the grid itself the sole tab stop. scripts/window_focus.py implements the matching Python reconciliation contract. Eighteen unit tests and fifteen browser scenario records across widths 390/768/1280 verify replacement, empty recovery, one tab stop and external focus preservation; see references/browser-cycle-208.json. Browser replacement currently rebuilds nodes, not keyed reuse. Frozen panes, variable dimensions, editing, scroll wiring, cross-viewport keyboard paging remain unimplemented. The fixture is internal, not a published portfolio page.

## Minimap, breadcrumb shortcuts and search
Use `minimapFrameBounds`/`minimapPan` for SVG/world-coordinate synchronization; keep client pixels separate from world units. `toggleMinimap` and `setMinimapScale` expose collapse and scale state with localStorage persistence; tolerate unavailable storage. `breadcrumbJump` supports Alt+1..9 with bounds checks. `search(query)` filters node IDs/diffs; Escape restores visibility. Await `copyLineage()` before reporting clipboard success (see lifecycle contract below).
Historical feature details and milestone evidence: [references/legacy-minimap-breadcrumb-milestones.md](references/legacy-minimap-breadcrumb-milestones.md). Historical timings are not current performance guarantees.
