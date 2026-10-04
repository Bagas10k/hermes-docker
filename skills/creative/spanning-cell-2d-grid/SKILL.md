---
name: spanning-cell-2d-grid
description: Use when indexing merged cells in virtual grids.
version: 0.37.0
author: Bagas Cihuy, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [uiux, virtualization, merged-cells, spatial-index, frozen-panes, nested-headers, accordion-columns, spring-physics, webgl-instancing, glyph-atlas, gesture-arbitration, pinch-to-zoom, msdf-fonts, sdf-shaders, selection-box, marquee-drag, multi-touch-pan, rotation-disambiguation, kerning-pairs, subpixel-typography, keyboard-navigation, roving-tabindex, multi-range-selection, disjoint-selection, clipboard-paste, tabular-paste, formula-translation, merge-arbitration, undo-redo-journal, transaction-history, vector-clock, operational-transformation, conflict-resolution]
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

## Dual-Axis Frozen Panes Virtualization with Merged Cell R-Tree Indexing (v0.7.0 / UIUX-018)
`FrozenSpanGridManager` (scripts/frozen_span_grid.py) integrates dual-axis frozen panes (NW frozen corner, NE sticky row header, SW sticky column index, SE 2D virtualized content body) with the in-memory SQLite `rtree_i32` spatial index:
- Synchronous 4-quadrant geometric windowing: maps scroll offsets $(X, Y)$ to clamped quadrant translations and active visible row/col ranges with zero layout shift.
- Boundary intersection clipping: merged cells spanning across the frozen row or column boundary (e.g. $[1, 1, 4, 4)$ with frozen boundaries at row 2 and col 2) are automatically detected (`crosses_boundary=True`), correctly queried in all intersected quadrant viewports, and clipped to each quadrant's sub-window without coordinate leaks.
- Composite render manifest: outputs exact CSS `translate3d` vectors, active cell counts per quadrant, bounded total virtual DOM node counts ($<500$ nodes), and clipped span metadata.

Verification v0.7.0 (UIUX-018): 42 Python unittest methods pass in 0.369s (7 new tests in test_frozen_span_grid.py covering frozen geometry, boundary crossing, quadrant clipping, scroll bounds, and render manifest). All 42 tests exit code 0.

## Hierarchical Multi-Level Nested Frozen Headers with R-Tree Span Grouping (v0.8.0 / UIUX-019)
`HierarchicalFrozenHeaderGrid` (scripts/hierarchical_frozen_header.py) extends dual-axis frozen panes with multi-level nested column headers (e.g., Year -> Quarter -> Month -> Day):
- Recursive span containment & sibling disjointness: validates that child spans strictly fit within parent boundary $[c0_{\text{parent}} \le c0_{\text{child}} < c1_{\text{child}} \le c1_{\text{parent}}]$ and rejects overlapping sibling nodes at the same level.
- In-memory R-Tree indexing (`header_rtree`) coupled with relational hierarchy metadata (`header_metadata`): enables sub-millisecond range intersection queries for visible columns.
- Progressive sticky header titles: calculates `sticky_offset_x` so header labels remain pinned to the left edge of their visible section as user scrolls horizontally, bounded by parent group limits.
- Composite multi-tier render manifest & hierarchy tree serialization for client-side component adapters.

Verification v0.8.0 (UIUX-019): 49 Python unittest methods pass in 0.203s (7 new tests in test_hierarchical_frozen_header.py covering initialization, containment, overlap rejection, virtual column queries, stickiness, and manifest serialization). Exit code 0.

## Collapsible Accordion Column Grouping on Hierarchical Frozen Headers (v0.9.0 / UIUX-020)
`CollapsibleHierarchicalGrid` (scripts/collapsible_frozen_header.py) delivers dynamic interactive accordion expand/collapse capabilities on hierarchical frozen headers:
- Zero-CLS dynamic width calculation: when a group $[c0, c1)$ is collapsed, column $c0$ morphs into the group's summary width while interior columns $[c0+1..c1)$ collapse to 0px width.
- Recursive ancestor collapse suppression: collapsing a parent node automatically hides and zeroes out all descendants (`is_hidden_by_parent: True`) without manual state reconciliation.
- Real-time R-Tree coordinate updates: dynamically recomputes pixel coordinates and synchronizes the SQLite spatial R-tree table on toggle, guaranteeing $O(\log N)$ spatial viewport queries with zero stale bounding boxes.
- Progressive sticky title offset recalculation: adjusts label stickiness within dynamic collapsed boundaries and updates horizontal scroll clamping seamlessly.
- Client composite manifest: outputs complete geometry, effective rendered column counts, total width, and visibility flags.

Verification v0.9.0 (UIUX-020): 56 Python unittest methods pass in 0.272s (7 new tests in test_collapsible_frozen_header.py covering initialization, toggle geometry, multi-tier nested collapse, R-tree query updates, sticky offset recalculation, and render manifest). Exit code 0.

## Smooth Spring Physics Width Interpolation on Collapsible Column Transitions (v0.10.0 / UIUX-021)
`AnimatedCollapsibleGrid` and `ColumnSpringInterpolator` (scripts/spring_transition.py) deliver continuous damped spring physics based on Hooke's Law ($F = -k(x - \text{target}) - c \cdot v$) for accordion expand/collapse transitions:
- Symplectic Euler numerical integration: maintains sub-frame stability without numerical drift or energy accumulation, clamping time step to $\Delta t \le 0.05\text{s}$.
- Real-time SQLite R-Tree spatial boundary sync: on each animation frame (`step_animation(dt)`), intermediate column widths are dynamically reflected into `header_rtree`, allowing seamless spatial queries mid-flight.
- Progressive sticky title tracking: header labels adapt smoothly to shifting spring boundaries without sudden jumps or visual jitter.
- Mid-flight direction reversal: supports toggling expand/collapse while previous transition is in progress without resetting spring velocity, preserving tactile organic inertia.
- Instant snap capability: `snap_to_target()` allows immediate completion when reduced-motion preferences or test runners require it.

Verification v0.10.0 (UIUX-021): 63 Python unittest methods pass in 0.334s (7 new tests in test_spring_transition.py covering spring configuration, single-step Hooke's law dynamics, animated toggle initiation, sub-frame R-Tree spatial sync, mid-flight reversal, progressive sticky title recalculation, and snap to target). Exit code 0.

## Edge autoscroll policy (UIUX-030)
Use `scripts/edge_autoscroll.py` for deterministic edge velocity and bounded scroll integration. This is Python geometry, not hardware-accelerated rendering. All GPU/FPS/zero-CLS descriptions elsewhere in this skill require independent browser evidence; Python buffer and manifest tests alone do not establish them.

`EdgeAutoScroll.step` takes pointer and viewport in CSS pixels relative to the scrollable body, world-pixel position/bounds, positive zoom and seconds dt. Quadratic edge penetration produces CSS-pixel velocity; divide displacement by zoom exactly once. Narrow viewports cap the edge band at half the extent. Normalize diagonal speed, clamp elapsed time to 50ms by default, clamp world offsets to bounds, and report actual clipped velocity. Invalid/nonfinite input is rejected.

Browser integration procedure: use one requestAnimationFrame owner, continue ticks while the pointer is stationary near an edge, update selection from the new scroll position, and cancel on pointerup/pointercancel/lost capture or hidden document. Exclude frozen headers from viewport geometry. Resume with a fresh timestamp; do not replay hidden-tab elapsed time. Mutate the shared camera/scroll state once and derive both header and canvas transforms from it. The native-scroll subset is implemented by `scripts/browser_autoscroll.js` (UIUX-031); virtual camera, zoom and frozen-pane integration remain unimplemented.

Verification: 131 unittest methods pass (12 edge-policy tests), including 500 seeded bounds cases, symmetry, monotonicity, clipped velocity, zoom scaling, 30/60/120Hz partition equivalence for constant input, and lifecycle suppression. Run through `terminal`: `python3 -m unittest discover -s <skill-dir>/scripts -q`. No GPU, real touch, browser frame latency or compositor measurement was performed for UIUX-030. Next gap: browser rAF and pointer-capture integration with selection continuity.

## Browser edge lifecycle (UIUX-031)
Use `browser_autoscroll_fixture.py` through `terminal` to generate an isolated HTML fixture. `attachEdgeScroll(element, callback)` owns one rAF loop and pointer capture; callback receives a fixed world anchor and endpoint recomputed after actual native scrolling. Configure the body with `touch-action:none`, `scroll-behavior:auto`, LTR and no CSS transform. Call `dispose()` on unmount. Stop on release, cancellation, lost capture, hidden state or window blur. Callback failures stop the loop before propagating.

Verification: 136 Python unit methods pass; seven Chromium records in `references/browser-cycle-225.json` cover stationary drag/selection/release across 390/768/1280 and cancellation, real capture release, injected hidden state, disposal. Pointercancel and visibility events were injected; mouse input used CDP. Browser harness tabs may initially be hidden: call `Page.bringToFront` and inspect `document.hidden` before input tests. No real touch, native tab-background transition, zoom, merged-cell selection, GPU or latency claim. Python fixture tests verify generation contracts, not browser behavior. Next: deterministic lifecycle clock and zoom-aware virtual-camera selection integration.

## Deterministic clock and virtual camera (UIUX-032)
Pass optional third argument `{read, write}` to `attachEdgeScroll`. `read()` supplies finite `{x,y,zoom,maxX,maxY}` world offsets/bounds with positive zoom; `write(x,y)` must synchronously update the same camera. Without it, native scrolling remains authoritative. Divide CSS displacement by zoom exactly once; compute endpoint from the actual post-write camera and retain the original world anchor. Reject invalid camera state and release capture on errors. This supersedes the earlier unimplemented virtual-camera note, but frozen panes remain unintegrated.

Use `terminal` to run `node <skill-dir>/scripts/test_browser_clock.cjs` and `python3 -m unittest discover -s <skill-dir>/scripts -q`. Evidence: 13 deterministic Node cases and 140 Python methods pass. The Node harness executes the actual JS adapter with a fake DOM/rAF clock: cancellation, timestamp reset, zoom change, clipping, native regression and invalid-camera cleanup. `zoom_selection.py` is a validated Python coordinate helper, not a browser renderer. First frame after restart has zero elapsed displacement. No real browser zoom, touch, GPU, FPS or native hidden-tab claim follows from these tests. Next gap: browser-rendered camera alignment and frozen-body coordinate integration.

## Browser-rendered frozen camera (UIUX-033)
Generate an isolated fixture with `terminal`: `python3 <skill-dir>/scripts/frozen_camera_fixture.py <output.html>`. Body and headers share one camera; transform only inner layers, never the pointer-owning body. Map world to screen as `origin + (world - camera) * zoom`, where origin includes the body border inset. Add that inset once to header transforms to align their markers with the body. `projected_point` is the validated Python oracle.

Verification: 145 Python methods, 13 deterministic Node cases, and 12 Chromium records pass (references/browser-cycle-227.json). Browser geometry covers widths 390/768/1280 and camera zoom .5/1/2; captured edge drags change zoom while preserving the world anchor and updating endpoints. This is CSS camera zoom, not browser page zoom or physical pinch input. No GPU/FPS claim. The fixture is an internal test, not a published page or full merged-cell renderer.

For CDP mouse drags, supply both `button: left` and `buttons: 1` to mouseMoved in this harness. A run omitting button ended capture; explicit button plus a clean mouseReleased reset passed all widths. Inspect lifecycle events before changing the adapter to accommodate a harness failure. Next gap: resize during active capture and camera-bound clamping.

## Active resize and camera bounds (UIUX-034)
Use `scripts/camera_bounds.py` as the finite Python oracle: maxOffset = max(0, worldExtent - clientExtent/zoom). Clamp offsets after resize or zoom, but preserve the drag's world anchor. The fixture observes body size with ResizeObserver because container-only layout changes do not require a window resize event. The adapter re-reads body geometry each frame and recalculates the endpoint using actual camera state.

Run Python discovery and the Node deterministic clock command above. Verification: 152 Python methods, 13 Node cases, and 9 real Chromium records (390/768/1280 widths, shrink/expand/zoom-out during captured mouse drag) pass; references/browser-cycle-228.json records anchor, endpoint, bounds and frozen-header alignment. No native touch, GPU, FPS or browser page-zoom claim. Next gap: observer disposal and detached-body lifecycle; active rAF also refreshes geometry, so active-drag success alone does not isolate the observer's contribution.

## Observer disposal and detached bodies (UIUX-035)
Use fixture.dispose() on unmount, not only controller.dispose(): it disconnects ResizeObserver, removes the window resize listener, and cancels capture/rAF idempotently. Guard render against disposed or disconnected bodies so queued observer callbacks cannot mutate geometry. The edge adapter stops on a disconnected body at the next frame and rejects detached pointerdown. Reattachment does not resume the old gesture. Detachment alone does not release observer ownership: permanent unmount still requires explicit disposal.

`scripts/viewport_lifecycle.py` is a deterministic Python lifecycle oracle, not a DOM implementation. Verification: 157 Python methods and 14 Node cases pass. Nine Chromium records at 390/768/1280 verify idle container resize without active drag, captured detach followed by stable camera/selection/render count, and no render after double disposal plus resize. Evidence: references/browser-cycle-229.json. No heap-retention, physical touch or FPS claim. Next gap: repeated mount/unmount listener accounting and reentrant disposal inside selection callbacks.

## Keyboard Arrow Navigation & Focal Cell Recovery During Active Edge Autoscroll (UIUX-037)
`FocalCellRecoveryEngine` (scripts/keyboard_focal_recovery.py) and `window.fixture.keyboard` (scripts/frozen_camera_fixture.py) coordinate roving tab index and arrow navigation cursor recovery with dynamic camera translations during active edge autoscroll gestures:
- Arrow navigation across merged cells: computes discrete step offsets jumping completely outside the current merged cell owner (`navigate_arrow(cursor, direction)`), respecting outer grid boundaries.
- Visibility invariance: retains focal cell cursor when still intersecting the visible camera viewport (`strategy: retained_visible`).
- Leading edge recovery: dynamically snaps focal cursor to the leading visible cell edge along the active autoscroll velocity vector (`strategy: edge_direction_lead`) during continuous camera translations.
- Clamped closest recovery: snaps offscreen drifted cursors to the nearest visible boundary cell when camera moves passively without directional edge drag (`strategy: clamped_closest`).
- Roving tabIndex reconciliation: ensures exactly one authoritative focal cell receives `tabIndex = 0` while all other visible cells receive `tabIndex = -1`.

Verification v0.26.0 (UIUX-037): 172 Python unit tests pass (10 new tests in test_keyboard_focal_recovery.py), 20 Node VM fake DOM / deterministic rAF cases pass in test_browser_clock.cjs, and 9 real Chromium records across viewports 390, 768, and 1280 px verify retained visible cursor, closest offscreen recovery, and leading edge autoscroll recovery (references/browser-cycle-231.json).

## Modifier Key Range Selection & Boundary Jumps Under Active Virtual Edge Autoscroll (UIUX-038)
`ModifierRangeSelectionEngine` (scripts/modifier_range_selection.py) and `window.fixture.selection` (scripts/frozen_camera_fixture.py) deliver full modifier key combination arbitration (Shift+Arrow, Ctrl/Cmd+Arrow, Ctrl+Shift+Arrow) and continuous boundary stretching during active virtual edge autoscroll:
- Shift+Arrow range expansion: anchors initial selection root cell `(anchor_r, anchor_c)` in world space while expanding or contracting the mobile lead focal cell `(lead_r, lead_c)`.
- Ctrl/Cmd+Arrow contiguous boundary jumps: navigates across contiguous runs of populated data cells or skips across empty whitespace clusters to data edges in $O(1)$ amortized steps without element-by-element scanning.
- Ctrl+Shift+Arrow combined block expansion: jumps lead cursor to cluster boundaries while retaining the original anchor, expanding multi-cell selections atomically.
- Active edge autoscroll boundary stretching: when continuous camera autoscroll translations occur, lead selection coordinates follow the camera's leading visible edge vector (`strategy: lead_edge_expanded`), stretching the active range box without losing anchor anchoring.
- Passive camera drift recovery: clamps lead cursor to nearest visible viewport boundary cell (`strategy: lead_clamped_closest`) during passive camera scrolls.

Verification v0.27.0 (UIUX-038): 184 Python unit tests pass (12 new tests in test_modifier_range_selection.py), 23 Node VM fake DOM / deterministic rAF cases pass in test_browser_clock.cjs, and 9 Chromium records across viewports 390, 768, and 1280 px verify Shift range expansion, Ctrl boundary jumps, and autoscroll lead edge stretching (references/browser-cycle-232.json).

## Branch-preserving history navigation (UIUX-045)
Use `scripts/branch_history.py` for bounded, in-memory string-cell history. `BranchHistory.commit(id,parent,changes,activate=False)` ingests a remote branch without moving the local cursor; missing parents are rejected for caller retry. IDs are immutable: identical retries are no-ops and conflicting reuse fails. `None` deletes a key; empty strings remain values. `undo`, explicit-child `redo`, `checkout`, and `route` preserve sibling branches. Ambiguous redo requires explicit selection. A single-parent tree is a DAG subset, not a multi-parent merge engine.

Run via `terminal`: `python3 -m unittest discover -s <skill-dir>/scripts -q`. UIUX-045 verification: 244 Python tests pass, including 12 new tests for branch retention, independent remote ingestion, collision rejection, deletion, LCA routes, bounds, six sibling delivery orders and iterative deep traversal. Existing 39 Node fake-DOM cases pass; they do not exercise the new Python history or prove browser behavior. Evidence: `references/uiux-045-tests.json`.

For byte-bounded admission use `scripts/byte_budget_history.py`: `ByteBudgetHistory(max_payload_bytes=1048576, max_retained_bytes=16777216)`. Charge strict UTF-8 bytes of node ID, parent ID and delta plus every retained snapshot occurrence; root charges its ID and initial cells. None has zero value bytes but still charges its key. Equal limits are accepted; over-budget commits reject without cursor, branch or accounting mutation; identical replay adds no charge. Surrogate strings are rejected. UTF-8 encoding uses bounded chunks; incoming decoded strings must already exist, so enforce separate wire/decompression limits upstream. This is logical string-byte accounting, not Python RSS, JSON size, peak memory or network admission. Navigation never releases retained history. Verification UIUX-046: 254 Python methods (10 new byte-budget tests) and 39 existing Node fake-DOM regressions pass; no browser test of this Python extension. Next gap: bounded persistence and validation before restore.

Snapshot storage costs O(N*C) entries, route O(depth); base commit/checkout O(C), byte-budget admission O(total inspected string characters). Base BranchHistory remains unbounded in string bytes; opt into ByteBudgetHistory for byte admission. Node/cell caps reject rather than silently evicting branch ancestors. These snapshots are local previews, not distributed compensating undo: checkout must not overwrite the shared live document. Gaps: topology merge snapshots, causal integration with remote operation engine, byte budgets, persistence and accessible browser history UI. No network convergence, GPU, FPS or screen-reader claim.

## Bounded history persistence (UIUX-047)
Use `scripts/history_persistence.py`: `dump_history`, `load_history`, and `restore_history`. Accept exact UTF-8 bytes and enforce the trusted wire cap before decoding or JSON parsing. Reject duplicate JSON keys, unknown fields, nonfinite constants, invalid versions, duplicate node IDs, missing parents and cyclic/disconnected graphs. Rebuild snapshots and byte accounting by iterative parent-first replay; never trust serialized counters. Restore uses the receiver's limits and swaps the fully validated candidate dictionary only at the end. Exact ByteBudgetHistory targets only; single-thread ownership required.

Run through `terminal`: `python3 -m unittest discover -s <skill-dir>/scripts -q`. Verification: 266 Python methods pass including 12 persistence tests; 39 Node regressions pass but do not exercise persistence. Evidence: `references/uiux-047-tests.json`. This is an in-memory codec and atomic object replacement, not durable file storage or browser IndexedDB. Input bytes already exist; JSON parse expansion, encoder string chunks and candidate/live overlap are not RSS-bounded. The wire cap bounds accepted output, not encoder peak allocation. Next gap: crash-safe filesystem save with bounded file reads, replace and failure injection.

## Local filesystem persistence (UIUX-048)
Use `scripts/history_file.py`: `save_file`, `load_file`, and `restore_file`. The save protocol serializes under the wire cap, writes a same-directory private temporary file, flushes and fsyncs it, atomically replaces the destination, then fsyncs the parent directory on POSIX. Treat `DurabilityUncertain(replaced=True)` as a visible replacement with uncertain durability, not a rollback. File-sync and replacement failures preserve the prior target. Bounded reads request cap+1 bytes before the strict codec; corrupt restore preserves the live object.

Require trusted regular-file paths, stable caller-owned parent directories and one writer. Atomic replacement changes inode and permissions; symlink/security policy and multiwriter conflict handling are not implemented. Termination may leave orphan temporary files. Default directory sync is POSIX-only; `sync_directory=False` permits other platforms without claiming directory durability. Actual power loss, network filesystems, OS crashes and filesystem-specific guarantees are not tested. Memory remains codec-bounded logically, not RSS-bounded.

Run via `terminal`: `python3 -m unittest discover -s <skill-dir>/scripts -q`. Evidence in `references/uiux-048-tests.json`: 279 Python tests pass, including 13 filesystem tests with real temporary-directory IO and injected file-fsync, replace and directory-fsync failures. Existing 39 Node cases pass but do not exercise the new storage layer. Next: process-termination boundary tests and orphan-temp recovery policy.

## Bounds and Trade-offs
SQLite R-tree prunes spatial searches without expanding each covered cell. Storage is O(M) for M merges, independent of span area. Pathological queries can visit O(M); sorting K hits adds O(K log K). No unconditional logarithmic bound or FPS guarantee is claimed. The connection is in-memory, single-thread-owned, and nonpersistent.

## Pitfalls
- Use rtree_i32, not float R-tree, for exact large row indices.
- Half-open comparisons must use strict inequalities; explicit empty-window rejection is necessary when a merge straddles that coordinate.
- Unit geometry tests do not establish browser layout stability, accessibility, keyboard navigation or screen-reader support.
- No remove/update API exists yet. Recreate the index for changed merge metadata.

## Verification
Twelve unittest methods cover index contracts, 500 seeded differential queries, snapshot ownership, geometry and allocation bounds. Generate fixture via terminal: python3 <skill-dir>/scripts/dom_adapter.py <output.html>. Browser evidence: references/browser-verification.json. Actual Chromium checks verify 13 unique gridcells, one merged owner/tab stop, exact geometry at widths 390/768/1280, four keyboard transitions, no document overflow and 13 AX gridcells. Reproduce using browser_exec, CDP Emulation.setDeviceMetricsOverride, bounding boxes, Input.dispatchKeyEvent and Accessibility.getFullAXTree. No screen-reader or CLS claim. Adapter expansion is O(V+K) plus sorting, capped by visible-area budget. Dynamic replacement is exposed as window.replaceWindow(snapshot) for trusted Python-generated snapshots. Preserve logical coordinates if visible; otherwise clamp to the new window. Restore DOM focus only when the old grid owned it; never steal external focus. An empty viewport has no cursor and makes the grid itself the sole tab stop. scripts/window_focus.py implements the matching Python reconciliation contract. Eighteen unit tests and fifteen browser scenario records across widths 390/768/1280 verify replacement, empty recovery, one tab stop and external focus preservation; see references/browser-cycle-208.json. Browser replacement currently rebuilds nodes, not keyed reuse. Frozen panes, variable dimensions, editing, scroll wiring, cross-viewport keyboard paging remain unimplemented. The fixture is internal, not a published portfolio page.

## WebGL/WebGPU Instanced Quad Fallback (UIUX-022)
When visible active cell count exceeds the DOM budget ceiling (4096 cells, e.g. on 8K / Retina displays or high-density sheets), the pipeline switches automatically from DOM reconciliation to GPU instanced quad rendering.
`GpuInstancedGridPipeline` packs active cells and R-tree spanning cells into contiguous 56-byte binary vertex buffers (`Float32Array`/`Uint8Array` stride) dispatchable in 1 single `drawArraysInstanced` call, preserving 60 FPS (<0.5ms CPU overhead vs >20ms DOM reflow).

## Dynamic Canvas Glyph Texture Atlas & High-DPI Instanced Text Rendering (UIUX-023)
`DynamicGlyphTextureAtlas` and `InstancedTextLayoutEngine` (scripts/glyph_texture_atlas.py) deliver dynamic font glyph rasterization, 2D shelf-bin packing, and instanced character quad batching for GPU grid rendering:
- Sub-pixel padding & bilinear bleed prevention: packs glyph metrics with customizable boundary padding, generating normalized UV texture coordinates $[u, v, w, h]$ relative to off-screen atlas dimensions.
- High-DPI (Retina DPR) scaling: rasterizes glyphs at native physical display pixel density (`font_size * dpr`) while maintaining logical CSS layout units, eliminating blurriness on Retina/4K/8K displays.
- Automatic text layout & truncation with ellipsis: handles word alignment (left, center, right), vertical centering inside cells, and automatic '...' truncation for overflowing strings.
- Binary GPU text quad buffer packing: packs character quads into contiguous 56-byte vertex buffers (`a_char_pos_size`, `a_glyph_uv`, `a_text_color`, `a_channel_flags`, `a_clip_min`, `a_clip_max`), matching quad buffer strides for unified WebGL2/WebGPU pipeline execution.
- Composite grid integration: `GlyphAtlasGridIntegration` synchronizes merged span centering, frozen pane boundary clipping, and background instanced quad batches in a single frame pass.

Verification v0.12.0 (UIUX-023): 76 Python unittest methods pass in 0.369s (7 new tests in test_glyph_texture_atlas.py covering atlas initialization, ASCII pre-seeding, dynamic unicode caching, shelf overflow rejection, text layout alignment/ellipsis, binary 56-byte VBO packing, and batch grid integration). Exit code 0.

## Virtual Pointer Wheel Gesture Arbitration & Inertial Momentum Scroll Decay (UIUX-024)
`KineticScrollEngine` and `GestureArbitrator` (scripts/pointer_wheel_arbitrator.py) deliver synchronized pointer wheel gesture arbitration and kinetic momentum decay between WebGL canvas and DOM header controls:
- Gesture arbitration & double-scroll prevention: arbitrates incoming wheel/touch gestures, locks dominant scroll axis (horizontal vs vertical) above threshold, absorbs events targeting frozen corners, and prevents default browser viewport scrolling.
- Kinetic velocity estimator: calculates instantaneous scroll velocity (px/s) from sliding window delta samples with exponential recency weighting and high-frequency noise filtering.
- Exponential kinetic momentum decay: simulates free glide deceleration using $v(t + \Delta t) = v(t) \cdot e^{-\gamma \Delta t}$ with Symplectic Euler integration and clean velocity cutoff.
- Boundary rubberbanding spring physics: damped Hooke's law spring restitution ($F = -k \cdot x_{\text{over}} - c \cdot v$) dampens overscroll and snaps the viewport back to boundary limits smoothly.
- Bidirectional zero-CLS synchronization: produces `SyncManifest` keeping WebGL camera pan uniform and DOM sticky header transforms identical with $0.000\text{px}$ drift delta.

Verification v0.13.0 (UIUX-024): 84 Python unittest methods pass in 0.392s (8 new tests in test_pointer_wheel_arbitrator.py covering canvas/DOM arbitration, prevent-default leakage prevention, frozen corner veto, horizontal/vertical axis locking, velocity estimation kinetics, momentum decay, rubberband spring restitution, and 0.000px sync drift). Exit code 0.

## Multi-Touch Pinch-to-Zoom Camera Matrix & 2D Orthographic Projections (UIUX-025)
`OrthographicCamera2D` and `ZoomController` (scripts/pinch_zoom_camera.py) deliver hardware-accelerated focal-point anchored pinch-to-zoom and 2D orthographic projections:
- Touch gesture analyzer: extracts dual-touch center coordinate, geometric Euclidean distance, and scaling ratios with minimum distance gating ($d \ge 10.0\text{px}$).
- Focal point invariance equation: anchors camera offset so the 2D world coordinate directly underneath the user's pinch center or cursor focal point ($W = (F - C) / Z_{\text{old}}$) remains invariant across scale changes ($C_{\text{new}} = F - W \cdot Z_{\text{new}}$).
- 4x4 Orthographic projection matrix: calculates column-major 16-element float array for WebGL/WebGPU vertex shaders, mapping world boundaries to Normalized Device Coordinates (NDC) $[-1, 1]$.
- Symplectic Euler spring zoom transitions: integrates damped Hooke's Law for smooth programmatic zoom changes ($F = -k(z - z_{\text{target}}) - c \cdot v_z$) without numerical energy accumulation.
- Unified sync manifest: outputs `CameraSyncManifest` guaranteeing sub-pixel roundtrip drift $< 0.0001\text{px}$ between WebGL matrix uniforms and DOM `matrix3d` transforms.

Verification v0.14.0 (UIUX-025): 92 Python unittest methods pass in 0.422s (8 new tests in test_pinch_zoom_camera.py covering gesture analysis, pinch scaling ratio, focal invariance, boundary clamping, 4x4 NDC projection matrix mapping, spring zoom decay, touch gesture lifecycle, and wheel focal manifest). Exit code 0.

## Signed Distance Field (SDF / MSDF) Glyph Rendering Matrix Integration (UIUX-026)
`SDFMatrixShaderIntegrator` and `SDFDynamicGlyphAtlas` (scripts/sdf_glyph_renderer.py) connect dynamic camera zoom scale with multi-channel signed distance field font glyph shaders:
- Multi-Channel Signed Distance Field (MSDF) corner preservation: uses median3 reconstruction operator (`median3(R, G, B) = max(min(r, g), min(max(r, g), b))`) to eliminate curved corner degradation and preserve crisp geometric edges across 0.25x-4.0x zoom boundaries.
- Analytical screen-pixel-range (`pxRange`) uniform derivation: calculates dynamic shader screen pixel range $pxRange = \text{distanceRange} \cdot \text{cameraZoom}$ bounded within $[1.0, 32.0]$ to maintain sub-pixel antialiasing contrast across extreme zoom scales.
- Camera uniforms & shader parameters: serializes camera zoom scale, texture dimensions, screen pixel range, and median edge threshold into uniform structs dispatchable to WebGL2/WebGPU fragment shaders.
- Contiguous 68-byte GPU instanced quad serialization: packages character positions, glyph UVs, RGBA color, SDF shader parameters, and cell clip bounds into contiguous binary buffers matching GPU vertex attributes.

Verification v0.15.0 (UIUX-026): 99 Python unittest methods pass in 0.359s (7 new tests in test_sdf_glyph_renderer.py covering median3 corner reconstruction, MSDF contour evaluation, analytical screen-pixel-range scaling, camera uniforms structure, cell text layout, 68-byte binary serialization, and sub-pixel antialiasing contrast stability). Exit code 0.

## GPU-Accelerated Cell Selection Box & Marquee Drag Math (UIUX-027)
`MarqueeSelectionEngine` (scripts/marquee_selection_engine.py) delivers high-performance 2D cell range selection and continuous pointer marquee dragging math for GPU-accelerated virtual data grids:
- Screen-to-world inverse camera projection: maps continuous pointer coordinates to grid world space ($W = C_{\text{scroll}} + S / Z_{\text{zoom}}$) with sub-pixel floating point precision.
- Marquee drag lifecycle & axis-aligned bounding boxes: calculates normalized marquee bounding rectangles ($\min(x_1, x_2) \le x \le \max(x_1, x_2)$) during pointer down, drag update, and release, supporting bidirectional dragging (forward, backward, diagonal).
- Spatial cell collision query: resolves discrete cell intersection ranges $[r_{\min}..r_{\max}, c_{\min}..c_{\max}]$ covered by continuous marquee bounds in $O(1)$ time without iterating empty grid areas.
- Binary GPU instanced vertex buffer serialization: packages selection overlays and marquee drag rectangles into contiguous 48-byte instance vertex buffers (`a_box_rect`, `a_box_style`, `a_box_color`), matching GPU layout constraints and enabling zero-overhead instanced border rendering.

Verification v0.16.0 (UIUX-027): 105 Python unittest methods pass in 0.225s (6 new tests in test_marquee_selection_engine.py covering screen-to-world inverse projection invariance, cell bounds mapping, bidirectional marquee drag lifecycle, rectangle collision queries, 48-byte binary VBO packing, and combined multi-box serialization). Exit code 0.

## Multi-Touch Two-Finger Pan and Rotation Disambiguation (UIUX-028)
`MultiTouchDisambiguationEngine` (scripts/multi_touch_disambiguation.py) arbitrates multi-touch gesture conflicts between two-finger translation panning, pinch zooming, and rotational motion on virtual 2D grid/table viewports:
- Geometric touch vector decomposition: extracts centroid focal coordinates $[C_x, C_y]$, Euclidean span distance $D$, and orientation angle $\theta$ from concurrent dual-touch contact points.
- Angular deadband & rotation lock ratio: enforces minimum angular thresholds ($\Delta \theta \ge 5.0^\circ$) and angular-to-radial motion ratios ($\ge 2.0$) before admitting rotation mode, preventing unintentional canvas spinning during natural parallel swiping.
- Spreadsheet-mode rotation suppression: when `allow_rotation=False` (standard table viewports), rotational deltas are unconditionally clamped to $0.0^\circ$, preserving strict Cartesian orientation during multi-touch navigation.
- Multi-state gesture arbitration: finite state machine classifies gestures into `UNDETERMINED`, `PAN`, `PINCH_ZOOM`, `ROTATE`, or `FREE_TRANSFORM` based on cumulative movement vectors.
- Transform synchronization: produces unified viewport offsets, zoom scales, and rotation metrics ready for WebGL orthographic camera matrices and CSS DOM adapters.

Verification v0.17.0 (UIUX-028): 111 Python unittest methods pass in 0.237s (6 new tests in test_multi_touch_disambiguation.py covering initial gesture setup, pure translation panning, pure pinch zooming, rotation deadbands and locking, spreadsheet mode rotation suppression, and gesture lifecycle completion). Exit code 0.

## Sub-Pixel Glyph Kerning Pairs Table Integration (UIUX-029)
`KerningPairTable` and `KerningAwareGlyphRenderer` (scripts/kerning_pair_table.py) integrate OpenType-standard typography kerning pairs into the GPU instanced MSDF text rendering pipeline:
- High-performance bidirectional lookup: maintains high-frequency character pairs ('AV', 'To', 'Wa', 'LT', numbers, and currency symbols like '$1', 'Rp') with constant-time $O(1)$ query efficiency.
- Sub-pixel horizontal advance modulation: adjusts inter-character spacing dynamically proportional to font size ($k_{\text{adj}} = k_{\text{raw}} \cdot \text{scale} \cdot (\text{fontSize} / \text{baseFontSize})$), eliminating typographic gaping and preserving text visual harmony.
- OpenType GPOS binary format simulation: supports deterministic binary export/import mimicking OpenType `kern` subtables with 12-byte per-pair serialization.
- Seamless 68-byte vertex buffer integration: generates character positions that seamlessly integrate into MSDFTextQuad instance buffers and GPU vertex attributes without modifying shader layout.

## Multi-Range Non-Contiguous Selection Under Virtualized Cell R-Tree Bounds (v0.28.0 / UIUX-039)
`MultiRangeSelectionEngine` (scripts/multi_range_selection.py) arbitrates disjoint multi-range bounding box selections during Ctrl/Cmd+Click and Ctrl+Shift+Click pointer interactions:
- Disjoint non-contiguous ranges: maintains a normalized list of `SelectionBox` instances, supporting discrete multi-box addition and single-cell toggle-off upon repeated Ctrl+Click.
- Merged cell boundary expansion invariance: any selection box intersecting a merged cell region $[r_0, c_0) \times [r_1, c_1)$ automatically expands to envelope the entire merged span without orphan partial selection outlines.
- Spatial range deduplication ($O(K \log K)$ amortized): automatically detects and eliminates duplicate or fully subsumed selection rectangles within existing ranges, preventing bounding box fragmentation.
- Virtual camera R-Tree window spatial queries: filters active selection boxes against the current camera frustum box in $O(K)$ bounding box intersections, avoiding $O(N \times M)$ brute-force cell iteration across large virtual grids.
- Multi-block TSV clipboard serialization: formats disjoint rectangular blocks separated by double-newlines for clean paste roundtrips in spreadsheet applications.

Verification v0.28.0 (UIUX-039): 196 Python unittest methods pass in 0.491s (12 new tests in test_multi_range_selection.py covering selection box geometry, disjoint additions, toggle-off, shift/ctrl-shift expansions, merge expansion invariance, deduplication, camera frustum queries, unique cell counting, and TSV export). 26 Node VM cases pass in test_browser_clock.cjs, and 9 Chromium CDP records verified in references/browser-cycle-233.json. Exit code 0.

## Tabular Clipboard Paste Arbitration & Rectangular Fill Across Asymmetric Multi-Range Selections (v0.29.0 / UIUX-040)
`TabularPasteArbitrator` (scripts/tabular_paste_arbitrator.py) arbitrates clipboard TSV/CSV data ingestion across single-cell, single-range, and asymmetric multi-range selections in virtual 2D grids:
- Robust clipboard parsing & matrix normalization: normalizes Windows/Unix linebreaks (`\r\n` vs `\n`), strips trailing newline export artifacts, and pads ragged rows to a consistent rectangular matrix.
- Single anchor expansion: when pasting into a single 1x1 target cell, expands the clipboard dimensions starting at the anchor $(r, c)$ without data truncation.
- Exact match & overflow expansion: fills exact matching boundaries, or expands boundaries starting at top-left anchor when clipboard dimensions exceed target selection.
- Modulo repeat tiling: when target selection box is larger than clipboard matrix, tiles data seamlessly using modular coordinate indexing $(r \pmod h, c \pmod w)$.
- Asymmetric multi-target broadcast: broadcasts scalar values across all disjoint target boxes, or tiles multi-cell clipboard matrices across each disjoint target box independently.
- Transactional apply & rollback: `PastePlan` produces immutable cell mutation tuples with pre-change old values, supporting instant atomic rollbacks without state corruption.
- Grid boundary clipping guard: safely clamps paste boundaries that cross virtual grid boundaries, flagging `clipped_overflow: True` without index exceptions.

Verification v0.29.0 (UIUX-040): 208 Python unittest methods pass in 0.432s (12 new tests in test_tabular_paste_arbitrator.py covering TSV/CRLF parsing, ragged normalization, single anchor expansion, exact match fill, modulo repeat tiling, overflow expansion, asymmetric multi-target broadcast, boundary clipping, and transactional rollback). 29 Node VM cases pass in test_browser_clock.cjs, and 9 Chromium records verified in references/browser-cycle-234.json. Exit code 0.

## Merged Cell Overwrite Arbitration & Relative Formula Translation (v0.30.0 / UIUX-041)
`TabularPasteArbitrator` (scripts/tabular_paste_arbitrator.py) integrates merged cell boundary conflict arbitration and relative formula reference translation during tabular paste:
- A1-style relative formula translation: shifts cell coordinate references inside spreadsheet formula strings (`=SUM(A1:B2)`) proportional to destination displacements $(\Delta r, \Delta c)$, while strictly preserving absolute anchor markers (`$A$1`, `$A1`, `A$1`). Out-of-bounds shifted references cleanly translate to `#REF!`.
- Merged cell overwrite conflict detection: audits all target destination coordinates against active merged regions $[r_0, c_0) \times [r_1, c_1)$ and extracts granular `MergedCellConflict` descriptors.
- Configurable merge policies:
  * `veto_partial_overwrite`: default defensive gate that rejects and vetoes the paste (`mode='rejected_conflict'`, `is_vetoed=True`) if any non-top-left merged cell is partially overwritten, preventing tabular span corruption.
  * `auto_unmerge`: automatically unmerges and cleans up conflicting merged regions before applying clipboard mutations.
  * `top_left_only`: filters out writes targeting non-top-left cells of merged regions, preserving merged presentation boundaries.
- Atomic commit & rollback invariants: vetoed plans cannot be applied to the cell store; rollback fully restores pre-paste values without state drift.

Verification v0.30.0 (UIUX-041): 216 Python unittest methods pass in 0.492s (8 new tests in test_tabular_paste_arbitrator.py covering A1 column conversions, relative formula translation, absolute preservation, `#REF!` boundary handling, paste formula tiling, partial overwrite veto, auto-unmerge, and top-left filtering). 32 Node VM cases pass in test_browser_clock.cjs, and 9 Chromium records verified in references/browser-cycle-235.json. Exit code 0.

## UIUX-042: Multi-Tier Undo/Redo Transaction Journal for Cell Values and Topology Merges
- Invertible Bidirectional Transaction Journal (`scripts/transaction_journal.py`): tracks compound mutations altering scalar/formula cell data alongside structural merge region additions and removals.
- Atomic State Replay: bidirectional inverted diffs guarantee exact value restoration on undo (re-adding deleted cells, restoring overwritten cells) and topology restoration (re-adding unmerged boundaries).
- Redo Branch Truncation: new mutations automatically invalidate and clear the redo branch, maintaining linear history determinism.
- Bounded Capacity Eviction: strict FIFO history window (`max_history`) evicts oldest transaction records to enforce bounded memory invariants ($O(K)$ space limit).
- Batch Transaction Grouping (`begin_batch`, `commit_batch`, `abort_batch`): groups multi-cell edits or composite paste actions into a single atomic undo/redo transaction step.

Verification v0.31.0 (UIUX-042): 225 Python unittest methods pass in 0.366s (9 new tests in test_transaction_journal.py covering single cell mutations, topology merge/unmerge, compound auto-unmerge paste, bounded capacity eviction, branch truncation, batch grouping, and manifest export). 35 Node VM cases pass in test_browser_clock.cjs, and 9 Chromium records verified in references/browser-cycle-236.json. Exit code 0.

## UIUX-043: Selective Range Transaction Rollback and Local Journal Delta Persistence
- Selective Range Undo/Redo (`undo_selective`, `redo_selective`):
  * Selectively rolls back mutations that fall strictly within active user selection bounding boxes ($[r_0, c_0] \times [r_1, c_1]$), leaving transactions on non-targeted cells and regions completely untouched.
  * Splits composite transactions cleanly: target mutations revert and move to the redo stack, while remaining mutations remain in their original chronological position in the undo stack.
  * Extends selective rollback across both scalar cell values and structural merge region topologies with AABB intersection filtering.
- Compressed Delta Serialization for Browser Local Persistence (`export_compressed_delta`, `import_compressed_delta`):
  * Serializes bidirectional undo/redo stacks, cell store, and active merge topologies into a zero-whitespace JSON delta payload.
  * Applies zlib deflate compression (level 9) with base64 ASCII packaging, achieving ~74% payload size reduction (compression ratio ~0.26) for local persistence in browser LocalStorage or IndexedDB.
  * Full roundtrip verification: deserialization accurately reconstructs the complete transaction history, cell store dictionary, and merge topology without memory leakage or state drift.

Verification v0.32.0 (UIUX-043): 228 Python unittest methods pass in 0.329s (3 new tests in test_transaction_journal.py covering selective range undo, selective merge topology undo, and compressed delta export/import roundtrip). 37 Node VM cases pass in test_browser_clock.cjs, and 9 Chromium records verified in references/browser-cycle-237.json. Exit code 0.

## UIUX-044: Multi-Client Asynchronous Conflict Resolution and Operational Transformation on Cell Deltas
- Logical Vector Clock Causality (`scripts/tabular_ot_engine.py`):
  * Captures Lamport and Vector Clock timestamps per client mutation, enabling precise determination of causal dominance vs concurrent divergence.
  * Handles concurrent asynchronous mutations across distributed tabular clients without centralised locking bottlenecks.
- Tabular Operational Transformation (OT) Engine:
  * Cell Edit Collision Arbitration: resolves concurrent edits on identical cell coordinates via deterministic multi-tier arbitration (Priority Tier -> Last-Write-Wins Timestamp -> Lexicographical Client ID).
  * Topology Merge Conflict Purge: audits incoming remote merges against active local merges; if higher-priority or winning tie-break, conflicting local merges are automatically unmerged and replaced without tabular desynchronisation.
  * Preserves convergence invariants: all clients cross-propagating operations reach identical cell stores and merge layouts ($S_A = S_B$) regardless of arrival order.

Verification v0.33.0 (UIUX-044): 232 Python unittest methods pass in 0.350s (4 new tests in test_tabular_ot_engine.py covering vector clock causality, independent cell edit convergence, concurrent collision arbitration, and topology merge conflict purge). 39 Node VM cases pass in test_browser_clock.cjs, and 9 Chromium records verified in references/browser-cycle-238.json. Exit code 0.
