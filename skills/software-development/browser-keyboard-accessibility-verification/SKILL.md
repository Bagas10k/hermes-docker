---
name: browser-keyboard-accessibility-verification
description: "Verify web keyboard accessibility in a real browser."
version: 1.0.0
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [accessibility, keyboard, e2e, browser, focus, aria, verification]
    related_skills: [e2e-browser-testing, desktop-principles]
---

# Browser Keyboard & Accessibility Verification

Proving a control is operable by keyboard — and stays operable as focus, permissions and state change. Distinct from unit/DOM-stub testing: only a real engine settles whether the browser's own key handling reaches your handler.

## When to Use

- A control must work without a pointer (Enter/Space activation, Tab order, focus continuity).
- Adding or reviewing a keyboard handler, `tabindex`, `role`, or live region.
- A previous test passed but keyboard operation was never actually exercised.
- Don't use for: pure logic tests with no DOM, or layout/visual auditing.

## Procedure

1. **Assert the surface is real before testing behaviour.** In the browser, check `tagName`, `type`, and `role`. A `<div role="button" tabindex="0">` and a `<button>` need different handling, and a fake DOM stub will happily report either.
2. **Drive real keyboard events**, not programmatic clicks:
   - Playwright: `page.keyboard.press('Enter')` / `'Space'` / `'Tab'` / `'Shift+Tab'`
   - Raw CDP: `Input.dispatchKeyEvent`
   `element.click()` bypasses the browser's key handling entirely, so a suite built on it passes while the keyboard path is completely broken.
3. **Focus the control first, then assert it took focus**, then press. A control that cannot receive focus has no keyboard path at all.
4. **Assert after activation:**
   - `document.activeElement` is the same element and still `isConnected`.
   - The side effect equals the pointer path exactly (same output text, same state).
   - The live region carries the same message as the visible feedback.
   - For `Space`: `window.scrollY` is unchanged.
5. **Walk the tab order**: `Tab` and `Shift+Tab` reach the expected neighbours and return to the control. Assert the neighbour's identity (tag, class, `data-*`), not just "something is focused".
6. **Re-run the matrix across state transitions**, not just the happy path — see below.
7. **Read the accessibility tree** (`Accessibility.getFullAXTree`) to confirm the role and accessible name update with the visual state.

## State matrix — test all of it

Keyboard bugs cluster at transitions. For each key, exercise:

| State | What must hold |
|---|---|
| granted / normal | exact side effect, focus retained |
| denied / rejected | failure surfaced in live region, focus retained, prior state not corrupted |
| recovered | the **new** state is used, not a stale cached one |
| pending (async write in flight) | UI does not claim success early; focus unmoved |
| disposal / unmount mid-flight | callbacks rejected, no write to a detached node |

Assert the *new* value after recovery. A test that only checks "success again" cannot catch a stale-value bug.

## Do not add keydown/keyup handlers to a native button

A `<button>` already activates on `Enter` and `Space`, and already consumes `Space` without scrolling. A page-level `keydown`/`keyup` pair for those keys is dead code.

- `preventDefault()` on `Space` **suppresses the native activation click** — the control stops working entirely. This is a bug, not an accessibility fix.
- The same pair *without* `preventDefault` passes tests while remaining redundant, adding a second code path to maintain.

Use `addEventListener('click', ...)` alone. Focus continuity comes from the renderer restoring focus and from `active.focus()` in an `execCommand` fallback — not from key listeners.

**Lock this decision with an invariant test** that fails if the listener pair reappears. Without it, the next "accessibility" patch reintroduces it. When such an invariant fails against your own patch, the invariant is right: delete your patch, not the test. Loosening an invariant to admit your change is how a regression gets locked in permanently.

## Pitfalls

- **Mock/fake DOM hides initialisation crashes.** Hand-rolled stubs often supply properties that are read-only in a real browser (`SVGRectElement.x`/`.width`, `HTMLButtonElement.type`). The stub passes, the browser throws. Assert element shape in the real engine before behaviour.
- **Fix the stub, not the production code, when the stub is incomplete.** If code calls `removeAttribute` or the harness lacks a `keyup` helper, extend the harness. Removing production behaviour so an outdated stub passes is backwards.
- **Harness tabs may start hidden.** Call `Page.bringToFront` and check `document.hidden` before input or clipboard assertions — `document.hasFocus()` is false in a background tab and focus assertions fail for the wrong reason.
- **`preventDefault()` on Tab** breaks focus escape; never swallow Tab to implement custom ordering.
- **`outline: none` without a replacement** removes the only cue a keyboard user has. Use `:focus-visible` so pointer clicks stay ring-free while keyboard focus is visible.
- **Injected state is not a real transition.** Injecting a hidden tab or a permission change proves the code path, not the browser's own transition. Say which one you did.

## Verification

Report per state and per viewport, and name the evidence class:

- real keyboard events in a real engine → establishes activation, focus continuity, no-scroll
- fake DOM / VM harness → establishes neither of the above
- one headless engine → does not establish another engine, physical input, OS clipboard, or actual screen-reader speech
- CDP permission control → establishes the code path, not the real permission prompt

Aggregate counts that mix these classes overstate the strongest one; state which suite produced each number.
