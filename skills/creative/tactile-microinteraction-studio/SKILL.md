---
name: tactile-microinteraction-studio
description: Use when building tactile controls and draggable sheets.
version: 0.2.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [vibe-coding, spring, accessibility, tactile]
    related_skills: [framer-motion, live-sandbox-hot-preview]
---
# Tactile Microinteraction Studio

Build usable press feedback and thumb-operated sheets without sacrificing focus, scrolling, or reduced-motion preferences. This is a user-local Hermes skill, not an upstream bundled release.

## When to Use
- Add spring settling and tactile feedback to live coding previews.
- Implement a cancellable bottom sheet with keyboard equivalents.
- Do not use for cinematic timelines, native mobile haptics, or security sandbox isolation.

## Prerequisites
- A disposable Node.js workspace; inspect existing dependencies before installing.
- Motion, Playwright, and axe-core; validation used Motion 13.4.1 and Chromium 153.0.8010.12.
- Install packages only into the sandbox, not the production application.
- Resolve SKILL_DIR from the loaded skill and SANDBOX to an absolute writable folder.
- Read [mechanics and sources](references/mechanics.md) before changing spring or gesture parameters.

## Quick Reference
Invoke through `terminal`, replacing placeholders with resolved paths:
- `terminal(command="npm install --prefix SANDBOX --no-audit --no-fund motion@13.4.1 playwright axe-core")`
- `terminal(command="npx --prefix SANDBOX playwright install chromium")`
- `terminal(command="node SKILL_DIR/scripts/verify.cjs SANDBOX", timeout=90)`
The verifier serves the actual template on an ephemeral loopback port, exercises Chromium, and closes both browser and server. No persistent service is created.

## Procedure
1. Define intent: reversible setting, dismissal policy, scroll region, motion preference, haptics opt-in. Success: each operation has a non-drag equivalent.
2. Copy `templates/sheet.html` and `sheet.js` into the sandbox. Supply `motion.js` from the installed package's `dist/motion.js`, or adapt the import to the existing bundler. Success: no CDN/runtime network dependency and no page errors. Without Motion, functional instant settling remains available.
3. Retain native `dialog.showModal()` for top-layer modality and inert background. Use a named heading, initial focus, explicit Cancel and Save, Escape, and opener focus restoration. Success: closing without Save leaves committed settings unchanged.
4. Restrict vertical drag to the handle. Use pointer capture, primary-pointer filtering, `pan-x pinch-zoom`, and cleanup on pointercancel/lost capture. Leave content scrolling native. Success: cancelled and short drags return to the open state; long drags dismiss.
5. Start with stiffness 420, damping 38, mass 1 as a candidate, not an optimal constant. Stop previous animations before starting new ones. Success: rapid gestures do not leave stale animations controlling transform.
6. Honor reduced motion immediately and on changes. Disable optional haptics by default; allow brief feedback only on confirmed user actions. Success: absent vibration support cannot block saving; API acceptance is never reported as physical feedback.
7. Keep bright purposeful accents, high-contrast text, visible focus, and controls at least 48px tall in this template. Use no emoji. Success: 390/768/1440px checks show no horizontal overflow. Follow the user's visual-reference workflow before claiming aesthetic approval.
8. Run the verifier and retain its JSON as evidence. Success: exit zero, empty page-error list, and all named cases reported. Re-test touch scrolling, screen reader operation, hardware vibration, and browser targets on real devices before deployment.

## Pitfalls
- `spring().next(t)` uses milliseconds; animate duration generally uses seconds.
- `damping: 0` may never settle; bound sampling loops and reject zero damping.
- Gesture CSS must be set before pointerdown; changing it mid-drag does not renegotiate browser behavior.
- Do not place touch-action:none on the whole page; it can prevent zoom and scrolling.
- The example persists settings only in memory. Add authenticated persistence separately and never label UI confirmation as backend success.
- Native modality does not automatically satisfy all application accessibility requirements. Verify Tab traversal and assistive technology in context.
- Scripts assume one sheet. Nested dialogs require a coordinated scroll-lock owner and focus stack.
- Haptics in headless tests are stubbed contract tests, not a hardware test.

## Optional audio and spatial effects
Read [tested tilt sources and evidence](references/tilt-evidence.md) before adapting sensor lifecycle or fallback behavior.
- Keep confirmation audio off by default. Create/resume AudioContext only after a user action; use a bounded gain envelope and disconnect completed oscillator nodes. Audio failure must never roll back a successfully saved setting.
- Suspend audio when hidden and close on page exit. Test actual Web Audio execution separately from physical speaker output.
- Do not equate cubic-bezier(0.2, 0.8, 0.2, 1) with a physical spring: it is a timing curve, not a differential-equation solver.
- Tilt and sheen are implemented as an explicit opt-in, session-only material preview, off initially and reset on close. Keep the dialog transform exclusively owned by sheet drag/settling; rotate only the noninteractive sample. Its clipped pseudo-element sheen has pointer-events:none and sits behind text.
- Request DeviceOrientation permission synchronously from the toggle activation in a secure context, only when the method exists. A missing requestPermission method is not a missing sensor API. Granted permission is not evidence of receiving sensor data.
- Validate finite beta/gamma, calibrate to the first valid sample, compensate screen angle, wrap angular deltas and clamp visual rotation to ±6 degrees. Coalesce writes with at most one scheduled animation frame; never run a perpetual frame loop.
- Fall back to mouse-over-preview or a fully usable static view on insecure context, missing API, denial/rejection, or 1800ms without usable data. This timeout is a tunable UX policy, not a sensor specification. Do not collect or persist sensor readings.
- Invalidate outstanding permission promises with a generation token; remove sensor listeners, timers and queued frames on off, dialog close, hidden/pagehide, and reduced motion. Require explicit reactivation afterward. Recalibrate on screen orientation changes.
- Test with `scripts/verify.cjs` (which calls `scripts/tilt-checks.cjs`); sensor permissions/events and lifecycle changes are synthetic contract tests, never real-device proof. Wait for the media-query change callback in tests instead of assuming emulateMedia synchronously dispatches it.
- Reference hierarchy: REF-071 upload modal separates title, input area, and footer actions. Adapt grouping, not its surrounding dashboard or claims about mobile behavior.

## Verification
The verifier also writes verification.json and screenshots to SANDBOX and runs axe-core WCAG A/AA rules at three widths. Zero automated violations is not full WCAG certification. Run Impeccable detect on the templates; zero findings is only the mechanical detector result, not proof of zero subjective design defects.
Reproduce the tested run: `node /home/ubuntu/.hermes/skills/creative/tactile-microinteraction-studio/scripts/verify.cjs /home/ubuntu/autopilot-sandbox/trend-003`.
Run `/home/ubuntu/.hermes/skills/impeccable/scripts/impeccable detect --json /home/ubuntu/.hermes/skills/creative/tactile-microinteraction-studio/templates/sheet.html /home/ubuntu/.hermes/skills/creative/tactile-microinteraction-studio/templates/sheet.js`.
Evidence: `verification.json`, `sheet-{390,768,1440}.png`, `tilt-active-{390,768,1440}.png`, `impeccable-result.json` in that sandbox. Both inactive and active states pass axe AA tags at those widths; 390x520 verifies scroll-reachable footer. Native dialog can transfer focus to browser chrome at a tab boundary; test exclusion of background controls, not that document.activeElement always remains inside the dialog. The verifier serves authoritative skill templates, not stale sandbox copies.
Run `scripts/verify.cjs` against the real template. Checks cover save, initial/restored focus, overflow at three widths, default silence, Escape, drag dismissal, snapback, cancellation, opt-in API invocation, reduced motion, and missing vibration API. No claim is made about measured p95 latency, physical vibration, visual approval, or cross-browser compatibility without separate evidence.
