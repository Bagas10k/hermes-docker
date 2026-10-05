---
name: kinetic-typography-glitch
description: Use when adding bounded kinetic status typography.
version: 0.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [vibe-coding, typography, motion, accessibility]
    related_skills: [css-native, spring-physics-motion-lab, live-sandbox-hot-preview]
---

# Kinetic Typography Glitch

Add bounded, opt-in motion to build status text without scrambling source code or concealing diagnostics. Ships an operational JSON editor integration, not a simulated build feed.

## When to Use
- Provide restrained error micro-displacement and spring-like success feedback in live coding tools.
- Don't use for body text, editor contents, flashing banners, or continuous decorative loops.

## Prerequisites
- Browser DOM; Web Animations API is optional and feature-detected.
- Copy `scripts/kinetic.js` with `templates/studio.html`, preserving relative paths.
- No package install, network, microphone, or credentials required for the component.

## Quick Reference
- Open `templates/studio.html` with `browser_exec` or a local static server.
- `const cue = new KineticStatus(statusElement)`; `cue.update('success', 'Build passed')`.
- `cue.setEnabled(true)` opts into motion; default is static.
- `cue.dispose()` on unmount; updates after disposal return false.
- Run `scripts/browser-checks.js` in the studio browser with Runtime.evaluate + awaitPromise.

## Procedure
1. Establish the semantic contract: status element has role=status and aria-live=polite. Update text synchronously using textContent. Pass when diagnostics remain readable without JS animation support.
2. Map real terminal/build results to success/error/idle. The supplied editor uses JSON.parse on user input and reports validation, never compilation. Pass when invalid input produces error and corrected input produces success.
3. Bind the explicit motion checkbox. Reduced-motion and hidden-document state override opt-in. Pass when preference changes immediately cancel active motion and return does not replay stale feedback.
4. Enforce a global 1500ms animation cooldown per component; latest text always wins. One animation maximum; cancel before replacing. Pass when an event burst cannot accumulate animations.
5. Keep error displacement within 2px over 160ms, success displacement within 3px over 280ms. No flashing, luminance pulsing, random glyphs, or opacity changes. Treat these as conservative defaults, not medically validated thresholds.
6. On teardown cancel animation and remove visibility/media listeners. Pass when repeated mounts leave no running animation or stale handler.
7. Test actual editor controls, narrow widths, disabled motion, mid-animation reduced-motion, animation replacement, unsafe-looking diagnostic strings, unsupported API, and disposal. Save real results and distinguish browser behavior from perceived comfort.

## Pitfalls
- Element.animate permits multiple simultaneous effects; explicitly cancel the prior owned animation.
- Cancel rejects an accessed finished promise; use onfinish/onCancel or catch AbortError. This component never accesses finished.
- CSS reduced-motion alone does not cancel imperative WAAPI effects; listen to matchMedia changes.
- Transforming an existing component can override its own transforms. Give status a dedicated wrapper.
- Short motion is still non-essential: default off, never animate editor text or repeatedly shake errors.
- Do not infer compiler correctness, focus improvement, total CPU use, or WCAG certification from a successful animation test.

## Verification
Bring the test page to the foreground first (document.hidden must be false). Use `scripts/browser-checks.js` against the supplied studio and require every returned check to pass. Also emulate reduced-motion in browser devtools while an effect is active and verify getAnimations().length is zero. Verify no horizontal overflow at 390px and 1440px. Real build adapters require separate integration tests; this package validates JSON only.

See [architecture and sources](references/architecture.md) and [recorded browser evidence](references/browser-results.json).
