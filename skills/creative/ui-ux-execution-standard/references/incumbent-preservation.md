# Preserving and restoring an approved interface

Use for feature additions, role upgrades, visual refinement, or restoration when the user wants the existing working product retained. The incumbent is the reference; this is not a new art-direction exercise.

## 1. Establish visual authority before implementation

1. Identify the actual incumbent route and source revision, the candidate route, and which paths are served by production. Keep production read-only; compare in a disposable runtime with neutral synthetic records.
2. Render the incumbent through its real controller when possible. If a fixture is required, provide the full view contract rather than rendering a fragment that omits navigation, shared CSS, or data-dependent sections.
3. Open the primary task with realistic content and its next interaction state: for a cashier, inspect populated catalogue/cart and the open payment form, not only an empty dashboard.
4. Record the components to preserve in visual order: shell/navigation states, monitoring, working panes, history, filters, and overlays. Preserve existing features even when the requested addition concerns another module.
5. Separate three contracts: presentation to match, interaction to preserve, and authorized domain changes. Replacing the visual baseline or dropping working controls requires explicit approval.

## 2. Measure the reference, then reuse it

Read computed styles and bounding boxes for the same viewport and interaction state. Record:

- Loaded font family, weight, size, and line height; await `document.fonts.ready` before comparison.
- Sidebar collapsed/expanded widths, header height, content padding, grid columns/gaps, and scroll-container ownership.
- Card bounds, padding, border/radius/shadow, search/filter heights, table columns, cart steppers, total and checkout position.
- Payment/review dimensions, field grouping, action order, visible-value formatting and canonical submitted values.

Prefer the existing shared layout, components, tokens and control primitives. Adapt their data boundary to new services without copying old financial calculations or bypassing new authorization. If direct reuse would alter production, use an isolated candidate adapter and document the source of the reused rules. Avoid accumulating full duplicate stylesheets plus speculative overrides; inspect the cascade and retain only the compatibility differences the candidate actually needs.

Do not turn a fast transactional workbench into a list-first CRUD page. A supporting record editor may belong in a popup while the catalogue/cart remains visible; classify each task rather than applying a blanket popup rule.

## 3. Keep adapters safe

- Preserve field ownership, events and canonical values. A formatted currency field may show a localized value while the named successful control remains an exact decimal string; verify both before final submission.
- Treat Blade includes as separate render scopes: variables created inside a child include do not become available to its parent or siblings. Define a formatting helper in the owning view or pass it explicitly, then exercise the real route.
- Preserve the authorized data source when restoring monitoring or history. Do not point a new ledger's dashboard at legacy transactions merely because the old component already queries them.
- Use the authoritative server role, not a guessed `user.role` property. Bound date-range reads and calculate totals before display limits; verify two distinct actors so a single-user fixture cannot hide a role-scope bug.
- Keep exact decimal arithmetic through formatting. Normalize chart heights separately into bounded geometry values; never cast the monetary payload to float to draw a chart. Do not catch data/query failures and replace them with zero-valued successful dashboards.

## 4. Compare equivalent browser states

1. Reapply device emulation after navigation when needed; read `innerWidth`/`innerHeight` immediately before capture.
2. Set the intended scroll container to its required position, wait for finite transitions and fonts, and measure again. Focus or `scrollIntoView()` may have moved the page after an earlier `scrollTo(0, 0)`.
3. Capture the actual old and new pages at equal dimensions. Verify the saved PNG's pixel dimensions, not its filename. Label differences in fixture data, selected period, populated cart, or navigation expansion instead of presenting unequal states as pixel-equivalent.
4. Check critical child controls against their pane bounds, not only page overflow. Prove the catalogue's select action is visible/reachable and the cart's quantity buttons, total and checkout are accessible.
5. Check apparent overlap or transparency against scroll position, stacking, computed opacity/background and animation state before editing CSS from a screenshot diagnosis.

A compact readout for each render:

```js
({
  viewport: [innerWidth, innerHeight],
  scroll: [scrollX, scrollY],
  font: getComputedStyle(document.body).fontFamily,
  pageWidth: document.documentElement.scrollWidth,
  boxes: [...document.querySelectorAll('aside, header, main, .pos-workspace, .summary-box')]
    .map(e => {
      const r = e.getBoundingClientRect(), s = getComputedStyle(e);
      return {tag: e.tagName, class: e.className, x:r.x, y:r.y,
        width:r.width, height:r.height, padding:s.padding, fontSize:s.fontSize};
    })
})
```

Use the existing [task-workspace probes](task-workspaces.md) for cancellation, keyboard focus and mutation counts; do not replace interaction tests with geometry checks.

## 5. Deliver one bounded revision

Batch the observed differences into one correction pass, run the smallest relevant isolated regression once, and confirm the affected browser states. An added test after the passing run remains NOT RUN until executed; an editor diagnostic is neither a runtime failure nor a passing test. Keep this evidence separate from asset builds, source hashes, independent review and owner approval.

Provide the comparison images with a short statement of what matches and what still differs. Stop for owner review when the requested restoration is implemented; do not keep redesigning or imply that restoring the interaction pattern proves pixel identity, production deployment, or release readiness.
