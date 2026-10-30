# Task-based operational workspaces

Use this recipe when a working cashier/admin or other transactional screen contains too many simultaneous forms. It reorganizes presentation without changing the transaction model; it does not prescribe a palette or require tabs for every application.

## 1. Map tasks and freeze contracts

1. Read the current rendered page, form handlers, shared styles, and role conditions before choosing panel boundaries.
2. Inventory each form's action, method, names, IDs, validation, data attributes, and JavaScript consumers. Include document links and read-only history in the task map, not just form headings.
3. Group by operator intent rather than implementation modules. Preserve the approved navigation placement and classify the form-opening model per task. Supporting CRUD may be list-first with labelled popup actions; a live cashier workbench keeps its catalogue, cart, quantity controls, total and checkout visible, with payment/review alone in popups. Do not generalize a popup preference into hiding the entire primary transaction or choose horizontal tabs merely because panel grouping is useful.
4. Keep roles server-controlled. A hidden panel is not authorization; build available navigation from authorized content and validate a stored/hash-selected task against that same available set.

Completion: every original form and action belongs to an available task, and no domain service, money calculation, permission, or schema change is needed for the navigation change.

## 2. Enhance without discarding form state

1. Keep a usable all-sections fallback before JavaScript initializes.
2. Create panel containers and move existing sections with `append(existingSection)` rather than copying HTML. Existing nodes preserve typed values, listeners, and form-control identity; verify form ownership if any section is moved across ancestors.
3. If the chosen interaction is tabs, use stable tab and panel IDs, `role=tablist`, `role=tab`, `aria-controls`, `aria-selected`, and labelled `role=tabpanel` containers. Maintain one tab with `tabIndex=0`; use ArrowLeft/ArrowRight for horizontal tabs, ArrowUp/ArrowDown with `aria-orientation=vertical` for vertical tabs, and Home/End. Do not relabel ordinary page-navigation links as tabs unless they actually control in-page panels.
4. Hide and make inactive panels inert only after the enhancement succeeds. Do not leave controls in hidden panels reachable by Tab. Keep focus indication visibly different from the active-task marker.
5. Resolve hash or session-storage requests through the available-task allowlist. Treat storage as optional; navigation must still work if storage access fails. Storing the selected tab does not persist unsaved form data after reload.
6. Tie a short finite transition to a user selection and honor `prefers-reduced-motion`. Preserve the same objects across the transition; do not replace forms just to animate them.

Interaction reference: https://www.w3.org/WAI/ARIA/apg/patterns/tabs/

### Popup inputs within task workspaces

1. Inventory write forms separately from GET filters and one-click actions. Use explicit selectors or attributes to classify them; read an HTML method with `form.getAttribute('method')`, not `form.method.toLowerCase()`, because a successful control named `method` shadows the form property and can abort initialization midway.
2. Reuse the existing popup primitive when present. Otherwise, a labelled native `<dialog>` opened with `showModal()` can supply top-layer placement and modal semantics. Add explicit `type=button` open/close/cancel controls; never nest forms or change their submitted names, action, method, validation, or CSRF handling.
3. Move the existing form node, not a clone. Trace delegated listeners and ancestor queries before choosing its new parent: a handler using `form.closest('tr')` still needs the original row ancestry. Keeping the dialog inside that table cell preserves the row contract while native top-layer rendering escapes clipping.
4. Preserve values on cancel and close, and restore focus to the exact opener. Keep Escape and Tab/Shift+Tab within the popup contract, prevent accidental dismissal during an in-flight save, and honor reduced motion. Verify real keyboard events rather than inferring correctness from native semantics alone.
5. Give the dialog a bounded viewport-relative height with an internally scrolling body and reachable close/save actions. Measure the dialog, its content, and final submit control at narrow and wide widths; page-level no-overflow is insufficient.
6. Test one complete read-only lifecycle: open → type an exact value → Tab-wrap → Escape/cancel → focus restored → reopen → same value. Assert zero mutation requests during cancellation. Then switch tasks and reopen the same form to verify node and value retention; check a restricted role separately.
7. Confirm the browser received the changed code before interpreting a failed probe. Compare a known source marker with the rendered script, bypass stale HTML cache when needed, and retry only the affected interaction. Capture idle/open screenshots after finite animations settle; diagnose apparent transparency from computed styles and animation state before treating a transitional frame as a CSS defect.

Dialog reference: https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/

## 3. Verify unsaved state and request count

Use `browser_exec` on the actual candidate route with neutral synthetic data. Exercise navigation without submitting the form:

1. Fill a real field through `fill_input`, recording its exact string value, selected product, and relevant form ownership.
2. Install request observation before switching panels. If the application submits through `fetch`, a temporary wrapper can count POST/PUT/PATCH/DELETE calls while forwarding the original receiver and arguments. Use browser network events as well when native form submissions, XHR, or other transports exist; a fetch-only counter cannot prove all network activity absent.
3. Switch task A → B → A. Assert the original value, same control node and form owner, one visible panel, and zero observed mutation requests.
4. Focus a tab, send real keyboard events with `Input.dispatchKeyEvent`, and assert selected state, focused element, and a visible focus outline. A DOM `.click()` does not verify keyboard behavior.
5. Check an authorized restricted-role session separately. Confirm unavailable tasks and privileged controls are absent; the admin screenshot alone cannot prove role safety.
6. Emulate reduced motion, switch panels, and inspect active animations. CSS declarations alone do not prove imperative Web Animations code respects the preference.

Keep these probes read-only with respect to business data. If a mutation flow must be exercised, do so separately in a guarded disposable runtime.

## 4. Inspect layout at the component boundary

Use `js` to collect these observations, then capture actual screenshots:

```js
({
  viewport: document.documentElement.clientWidth,
  page: document.documentElement.scrollWidth,
  visiblePanels: document.querySelectorAll('[role="tabpanel"]:not([hidden])').length
})
```

- Require `page <= viewport`, then inspect each visible navigation label and critical control against its own container rectangle. Page fit does not catch clipping inside `overflow:hidden` containers.
- At narrow widths, measure the real fixed navigation height and reserve at least that much bottom space plus safe-area padding. Scroll to the final form action and confirm it is above the bar and usable.
- Keep important navigation labels discoverable; if navigation intentionally scrolls, demonstrate access to every item instead of treating a partly clipped label as proof of failure or success.
- Measure actual pane width, not just viewport width. A five-column table can be unreadable in a narrow desktop side pane; use a labelled stacked-record presentation when necessary, retaining meaningful values and document actions.
- Keep money amounts together and tabular. Distinguish the original transaction type from current settlement status: a credit-origin sale may be fully paid. Do not infer unpaid status from its original method or hide that distinction merely to make a table fit.
- Inspect screenshots for hierarchy and wording after the bounds checks. A machine no-overflow result is not a visual-quality verdict.

## 5. Close one bounded correction batch

1. Collect the concrete clipping, hierarchy, label, and focus findings before editing again.
2. Apply one coherent correction batch, preserving form and money contracts.
3. Run the relevant isolated regression suite and final browser probes, then capture fresh narrow/wide screenshots. Do not reuse pre-correction screenshots or QC as evidence for the changed source.
4. If capture alone times out, retry capture separately; preserve successful interaction observations and do not resubmit transactions for the picture.
5. Report separately: implemented changes, final-version automated checks, exercised browser behavior, screenshots, untested checks, and production/deployment status. If work stops before final verification, mark the result as an in-progress candidate rather than final UI or publish-ready.
