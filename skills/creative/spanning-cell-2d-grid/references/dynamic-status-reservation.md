# Dynamic status reservation: bounded evidence

Author: Bagas Cihuy & Hermes Agent. Status: TESTED within the local fixture.

## Mechanism and decision
The status track reserves max(height(pending), height(success), height(failure), height(current idle/reset)). Revision text is not bounded by static feedback templates. Store it in an aria-hidden, visibility:hidden sibling in the same grid area; synchronize via textContent on draw, disposal and native reset. Python initial HTML escapes the ID. Use min-width:0 and overflow-wrap:anywhere. Anchoring remains auto; none is diagnostic only.

This is a local preview fixture, not a deployed service. Wrap status and breadcrumbs instead of ellipsizing. Normal inline text flow prevents a badge consuming the label column under inline-flex. Bottom alignment keeps the copy action near the following graph, and responsive breadcrumb width limits wrapping height within the tested fixture.

## Counterexample and controlled interventions
Parent rerun: Chromium 156.0.8078.4. Same long revision payload across positive records, status length 139 characters. Matrix: 320/390/768px × explicit font1x/2x × success/failure × stay/forward/backward. Eight checkpoints include native 1500ms reset. Clipboard promises controlled here; native clipboard tested separately.

At 390px/font2x/failure/forward:
- Reserved-auto: height 388.6875px throughout; departed/settled/reset scroll 846px and target top 785.4937744140625px remain identical.
- Unreserved-auto: height 388.6875→129.5625→388.6875px; initial→pending scroll 816→557px, reset 587→846px. Anchoring compensates layout changes.
- Unreserved-none: departed/settled/reset scroll remains 846px but target top 526.3687744140625→785.4937744140625px at reset. Stable offset alone is not stable geometry.
- Removing wrapping only, same text at 320px/font1x: status width 539px in 280px container. Positives verify full status and breadcrumb text-fit.

## Acceptance hardening
Initial worker output clipped breadcrumb labels and accepted six invalid payload classes. Parent wrote failing checks before fixes: absent/zero widths, short-text impersonation, mismatched phase text, clipped labels and wrong breadcrumb. Final suite also rejects stale reservation and text-fit false. Restoring wrapping exposed inline-flex label compression; parent corrected this without weakening event/neighbor gates or disabling anchoring.

## Verification
- scripts/clipboard_dynamic_status.py: deterministic Python evidence gate.
- scripts/test_clipboard_dynamic_status.py: six gate tests.
- scripts/test_dynamic_status_contract.py: eight parent acceptance tests.
- scripts/dynamic_status_fixture.py: actual long-ID history fixture.
- scripts/test_dynamic_status_chromium.cjs: browser matrix, ten negative controls, one none comparison.
- references/uiux-073-browser.json: 36 sequences, 288 measurements.
- references/uiux-073-parent-verification.json: all 18 commands exit0, source SHA-256 before/after identical, stdout/stderr, browser evidence hash; native timer 1500.2–1501.8ms observed.
- Python discovery: 432 methods. Native mouse9, native keyboard24, DOM/AX12, contrast72 are separate regression categories, not extra Python tests. Event/nested/reflow/minimap/Node runners also pass.

Invoke commands from SKILL.md through terminal at this skill directory. Reuse installed Playwright via NODE_PATH. Run native clipboard serially to avoid shared-state interference.

## Bounds and next gap
One long active payload with an unbroken suffix and Indonesian feedback is proven, not a multilingual corpus. The fixture's alternate localized branch is not activated in this matrix. Consecutive activations, checkout while clipboard is pending, stale timer after cursor change, RTL/CJK and native zoom need tests. AABB/hit tests and text Range bounds do not prove arbitrary paint, screen-reader speech, full WCAG or performance. Independent audit is historical design critique, not final evidence; use parent-verification hashes.
