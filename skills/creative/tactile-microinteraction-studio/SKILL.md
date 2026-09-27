---
name: tactile-microinteraction-studio
description: Use when building tactile controls and draggable sheets.
version: 0.1.0
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
- Motion and Playwright; validation used Motion 13.4.1 and Chromium 153.0.8010.12.
- Install packages only into the sandbox, not the production application.
- Resolve SKILL_DIR from the loaded skill and SANDBOX to an absolute writable folder.
- Read [mechanics and sources](references/mechanics.md) before changing spring or gesture parameters.

## Quick Reference
Invoke through `terminal`, replacing placeholders with resolved paths:
- `terminal(command="npm install --prefix SANDBOX --no-audit --no-fund motion@13.4.1 playwright")`
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

## Verification
Run `scripts/verify.cjs` against the real template. Checks cover save, initial/restored focus, overflow at three widths, default silence, Escape, drag dismissal, snapback, cancellation, opt-in API invocation, reduced motion, and missing vibration API. No claim is made about measured p95 latency, physical vibration, visual approval, or cross-browser compatibility without separate evidence.
