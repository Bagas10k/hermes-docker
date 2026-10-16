# Dynamic clipboard ownership races

## Mechanism and decision
A clipboard promise can settle after its initiating revision/node has been replaced. Keep an identity token and DOM ownership guard; revoke the token and clear the owned feedback timer on checkout/disposal. The OS write itself remains uncancellable. Reservation text belongs to the current cursor, not the last settled promise.

There must be one focus owner per render. `draw(true)` chooses undo/branch; restoring copy focus inside `renderBreadcrumbs` first creates a transient detour. Pass `restoreFocus = !focus`. The correction changes three lines in the runtime, not the token architecture.

## Verified experiment
Parent reran 20 commands with matching pre/post source SHA-256 maps (`uiux-074-parent-verification.json`). Chromium 156.0.8078.4; 459 Python methods (27 added), 36 ownership sequences / 180 phase snapshots, ten browser fault controls. Six positive reset timers fired at 1500.3–1501.6ms; twelve cancelled timers remained inactive after their original deadlines. These are observed samples, not latency percentiles or guarantees.

Matrix: pending checkout success/failure, settled checkout reset, settled disposal reset, pipelined request, pending disposal; widths 320/390/768 and explicit CSS fonts 1x/2x. New nodes retain the configured font sizes. Continuous focus events and status/reservation/button mutations supplement snapshots; node replacement, disabled disposal, exact texts, late target/scroll position and status dimensions are checked.

Ten fault controls: stale status, stale shadow, transient stale status/restore, stale focus, transient focus/restore, uncancelled callback, copied-class contamination, pipelined label corruption, wrong actual checkout, actual early timer. Only the last deliberately shortens a timer; positive clocks are untouched. Cancelled callback injection proves the timer gate even though runtime token guards prevent text corruption.

## Parent review corrections
The initial worker gate passed absent traces, clipped text, enabled disposed controls, unobserved deadlines, NaN timestamps and current-button focus theft. Ten targeted acceptance tests failed first. Parent tightened the gate and detected 24 checkout focus-detour records in the existing browser evidence, then fixed the runtime and reran. Additional tests cover node identity, trace suffix, fonts and transient button changes. Initial worker/audit summaries are not final verification.

The initial runner also substituted revision IDs for absent DOM attributes, manually changed timer evidence, and scaled only initial nodes. Parent replaced these with explicit identity fields, behavioral timer controls, actual wrong-cursor intervention and persistent CSS font rules. No synthetic response is used as observed browser data.

## Regression separation
Native clipboard: 9 mouse records and 24 keyboard records. DOM/AX accessibility: 12 records. Contrast: 72 records. Existing dynamic text, native timers, event-level neighbor checks, nested/reflow/minimap and Node runners pass. These are separate regressions, not 117 ownership cases or a combined accessibility score.

## Reproduce
From the skill directory, use `terminal` for:

```text
python3 -B -m unittest discover -s scripts -q
NODE_PATH=<existing Playwright installation>/node_modules node scripts/test_status_ownership_chromium.cjs
python3 -B scripts/clipboard_status_ownership.py references/uiux-074-browser.json
```

Keep native clipboard runners serial; they share clipboard state. Awaiting `page.evaluate(() => copyLineage())` stalls on the deliberately pending promise: use a block with no return, then settle through a separate action.

## Bounds and next falsifier
Positive races use programmatic copy/checkout with real DOM and native timers, not native keyboard checkout. Disposal releases focus to body when it disables the focused control; this is observed, not certified as accessible navigation. Heights can change at deliberate checkout because revision labels differ; only late settlement/reset must be inert. CSS font scaling is not native zoom. AABB, DOM and mutation evidence do not prove screen-reader announcements or arbitrary paint visibility.

Next bounded target: native keyboard departure to a checkout control during pending copy, nested-scroll geometry, exact destination outline/visibility, then late success/failure and deadline observation. Reuse the established neighbor/event gates and add fault controls for transient focus/scroll and omitted trace tails. No production deployment or scheduler changes.
