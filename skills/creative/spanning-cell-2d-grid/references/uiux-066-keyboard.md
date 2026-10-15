# Clipboard keyboard verification

Credit: Bagas Cihuy & Hermes Agent.

## Contract
Use one native button click handler. Enter and Space must produce trusted keyboard clicks, then truthful pending/fulfilled/rejected status without moving focus. Mutation of a button's visible label is not equivalent to updating its computed accessible name or a live region. Keep the live status region polite and atomic. Clipboard disposal invalidates UI callbacks, not the native OS/browser write.

## Reproduce
From the skill directory through `terminal`:

```text
python3 -B -m unittest discover -s scripts -q
node scripts/test_browser_clock.cjs
node scripts/test_history_browser.cjs
NODE_PATH=<existing Playwright node_modules> node scripts/test_native_clipboard_chromium.cjs
NODE_PATH=<existing Playwright node_modules> node scripts/test_native_clipboard_keyboard.cjs
NODE_PATH=<existing Playwright node_modules> node scripts/test_minimap_chromium.cjs
```

Resolve an installed Playwright package and matching cached Chromium; do not assume an old cache revision exists or install a dependency without need. Native clipboard suites run sequentially, not against a shared concurrently written clipboard.

## Assertions that prevent false positives
- Distinct seed text makes a no-op copy fail exact read-back.
- A new trusted click is observed for every activation, including repeated denied Space; an old failure label alone is insufficient.
- Save the actual button object, not a locator alone. Locators can silently resolve replacement elements.
- Observe pending state synchronously at the click listener after the application handler; a fast native promise may settle before an asynchronous poll sees pending.
- Check focus during pending, completion, and real timer reset, plus Tab and Shift+Tab continuation.
- Check read granted/write denied independently; verify NotAllowedError and unchanged clipboard contents.
- `refresh()` preserves copy-control continuity. Explicit `checkout()` has a different existing focus contract: branch navigation.
- Controlled promise tests must assert status text as well as button labels after overlap, rerender, timer cancellation and disposal. Clearing timers alone leaves stale pending announcements unless disposal restores status.

## Sources retrieved
- WAI-ARIA APG Button Pattern: https://www.w3.org/WAI/ARIA/apg/patterns/button/ — Enter/Space and context-dependent focus after activation.
- WCAG ARIA22: https://www.w3.org/WAI/WCAG22/Techniques/aria/ARIA22.html — role=status, polite live updates, explicit aria-atomic for compatibility.
- Playwright Keyboard: https://playwright.dev/docs/api/class-keyboard — press/down/up and distinction from input-only insertText.

## Evidence and limits
`uiux-066-parent-verification.json` is the final suite evidence with source hashes; `uiux-066-browser.json` contains 24 native cases across three widths. Earlier worker evidence in `uiux-066-tests.json` has 21 keyboard cases and predates the stronger activation/timer checks. Do not treat it as the final count. DOM/AX text does not prove a screen reader announced anything. No physical paste, permission prompt UI, cross-engine, FPS or latency claim.
