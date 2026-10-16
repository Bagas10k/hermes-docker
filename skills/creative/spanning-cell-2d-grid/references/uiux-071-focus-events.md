# Event-level focus continuity and scroll anchoring

Author: Bagas Cihuy & Hermes Agent. Scope: isolated Chromium fixture using the existing renderer, controlled clipboard promise, native Tab/Enter, explicit computed-font scale. This supersedes the worker's preliminary report and hashes; use `uiux-071-parent-verification.json` for final source hashes and command results.

## Procedure
1. Attach document capture listeners for focusin, focusout, keydown and scroll before keyboard navigation. Assign each event a contiguous counter and observation time. Initial focus on the outside button is programmatic; navigation from there uses Playwright native Tab.
2. Record actual setup focus arrival on the copy button, native Tab count, Enter activation and exactly one trusted click/write. Trusted focus events alone do not establish user intent: programmatic focus() generates them too.
3. Sample initial, pending, scrolled, shrunk, regrown, departed, settled phases. Bind every phase to eventSeq, checkpointTime, scrollEventCount, matrix metadata and expected label/status. Reject missing phases, trace truncation, duplicate/gapped IDs, invalid clocks and nonfinite dimensions.
4. Perturb outer vertical and inner horizontal scrolling; shrink/regrow only the container. Keep focus untouched by the harness. During pending layout interventions, no focusout/focusin may occur.
5. Depart with native Tab to SVG g[data-node=alpha][role=button], or Shift+Tab to button[data-breadcrumb-node=anak-雪]. Stay mode uses no departure key. Correlate exact native key evidence with focusout then focusin as observed in this Chromium, not a universal cross-browser event ordering claim.
6. Allow native keyboard scrolling during departure. After three animation frames, snapshot window X/Y, outer X/Y, inner X/Y and DAG X/Y. Settlement must preserve these offsets and generate no recorded scroll/focus transitions in the opt-out policy fixture. Three frames are a bounded observation interval, not proof of all future asynchronous work.
7. Reuse `clipboard_focus_reflow.audit_record` without forging focus=true. Backward departure can legitimately scroll the unfocused copy button offscreen; only its clipping/hit-test failures are exempted. Known opaque overlay overlap still fails. This does not audit geometry of the newly focused neighbor.
8. Use the same gate for fault controls. Blur/refocus and steal/return must be rejected even though phase-end activeElement is correct. Scroll/restore must be rejected even when final offsets equal the baseline. Require the intended failure reason, not any unrelated exception.

## Anchoring: preserve counterevidence
The positive fixture explicitly uses `overflow-anchor:none` on both test wrappers. Do not present this as default browser behavior. A paired default-auto control at viewport390/font2x/failure/forward moved outer scrollTop from 340 to 378 during settlement; opt-out counterpart stayed at 340. No focus theft occurred. Thus application status reflow and native anchoring can cause scroll without any application focus() call. The parent reproduced this as the sixth negative control instead of hiding the failed condition.

No application renderer code was changed. Opt-out is a tested fixture policy, not an unqualified recommendation: disabling anchoring trades scroll compensation against visual displacement. Investigate stable status layout under default anchoring before production adoption.

## Reproduction
From this skill directory, through `terminal`:
```
python3 -B -m unittest discover -s scripts -q
NODE_PATH=<existing Playwright node_modules> node scripts/test_focus_events_chromium.cjs
python3 -B scripts/clipboard_focus_events.py references/uiux-071-browser.json
```
No package install. Ephemeral loopback server and browser contexts are closed by the runner. Native clipboard regression suites run serially, separate from controlled promises.

## Verified evidence
- 400 Python unittest methods, including 20 deterministic synthetic contract/falsification methods; exit 0.
- 36 sequences = viewport320/390/768 × font1/2 × success/failure × stay/forward/backward; 252 measured phases.
- Six controls detected: transient blur/refocus, completion theft, completion steal/return, transient scroll/restore, wrong departure identity, default native anchoring.
- Chromium 156.0.8078.4. Fourteen parent commands exit 0; source hashes unchanged during execution.
- Separate regression evidence: UIUX-070 12 sequences/84 phases + six controls; UIUX-069 48 geometry records + six controls; contrast72, accessibility12, focus/status27; native clipboard pointer9 and keyboard24; minimap9/lifecycle3/controlled clipboard33; Node clock39 and clipboard11.
- `uiux-071-browser.json`: raw measurements. `uiux-071-parent-verification.json`: exact commands/stdout/exit codes/hashes. `uiux-071-parent-red.json`: original verifier falsely accepting a truncated trace.
- `uiux-071-independent-review.md`: design proposals, not a verification report. Its 288-phase/post-timer proposal was not adopted; actual run is seven phases and 252 positive measurements. No blanket zero-scroll requirement during deliberately scrolled/departed phases.

## Bounds and next gap
- Feedback reset timer1500ms is suppressed here. Event continuity through reset remains untested even though separate native keyboard regressions test reset in another fixture.
- Explicit fonts are not native browser zoom. DOM/AX is not audible screen-reader speech; headless clipboard is not physical OS/cross-app proof.
- Events/checkpoints catch observed transitions, not fabricated coherent traces, arbitrary shadow-root coverage, compositor paint, all delayed events or all browser engines.
- Outline AABB and known opaque overlays are bounded geometry, not general WCAG certification. Newly focused neighbor visibility is not yet measured by the copy-button gate.
- Next: compare stable status geometry with default anchoring and explicit opt-out across settlement plus feedback expiry; audit the new active target, not only the previous button.

## Primary sources checked by parent via agent-reach/Jina
- https://developer.mozilla.org/en-US/docs/Web/API/Event/isTrusted — HTMLElement.focus() may create trusted events; dispatchEvent() does not prove native user action.
- https://developer.mozilla.org/en-US/docs/Web/CSS/overflow-anchor — auto is the default; none opts out of browser scroll-position compensation. The source supports mechanism, while the 38px observation comes from the local experiment.
