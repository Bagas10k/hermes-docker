# Pending focus, repeated status and bounded accessibility audit

Credit: Bagas Cihuy & Hermes Agent.

## Contract and verified procedure
- Preserve user-moved focus during asynchronous copy. Promise settlement has no reason to focus the invoking button. Restore a replacement button on refresh only when the old button still owned focus; refresh/disposal neutralizes status and invalidates pending UI ownership, not the native write.
- Keep a preexisting polite atomic status region. Repeated same-route success and denial traverse pending/result DOM states; the final status also appears in Chromium AX. This does not establish assistive-technology speech or repeated-announcement timing.
- Hold a controlled write promise to make pending focus movement deterministic. Do not present this as measured timing of the native clipboard API. Native tests use exact clipboard read-back and CDP permission intervention separately.
- Read the current reduced-motion preference before navigation. Explicit `scrollTo({behavior:'smooth'})` bypasses CSS `scroll-behavior:auto`; the application uses `auto` under reduce. CSS transitions clamp to 0.01ms. No claim about ongoing animation cancellation when preference changes mid-flight.
- Require a genuinely scrollable test container. The first audit had zero scroll range on wider viewports and could not support its scroll conclusion. The final runner injects a 200px container width, asserts positive bounds, checks unguarded smooth as a negative control and actual guarded checkout as an immediate positive control. This injected-width probe is not a responsive-layout audit.

## Measurements and bounds
At widths 390/768/1280 in headless Chromium 156.0.8078.4, idle copy-button keyboard focus has a solid 2px outline, offset 2px, color rgb(37,99,235). Against its adjacent bar rgb(241,245,249), opaque sRGB contrast is 4.7179:1, exceeding the 3:1 non-text threshold. Contrast against the idle button rgb(226,232,240) is 4.1926:1, recorded informationally: the offset separates that fill from the outline.

Contrast = (max(L1,L2)+0.05)/(min(L1,L2)+0.05). The stdlib Python helper rejects nonfinite inputs, boolean numeric values and translucent colors without a compositing model. Empty evidence cannot pass. It requires a focused solid indicator and width >=1px as a local gate; SC 1.4.11 sets contrast, not that width requirement. `compliant` in the JSON means only these local checks pass, never whole-page WCAG conformance.

Parent added negative tests after discovering empty records passed vacuously and string infinities bypassed numeric validation. The tests failed before correction (exit 1) and passed afterward. All 347 Python methods passed in the final run, nine belonging to the new measurement helper. See `uiux-067-parent-verification.json` for exact commands, red/green output and source hashes.

## Evidence taxonomy
- `uiux-067-focus-browser.json`: 27 records: 9 native clipboard, 12 controlled pending-promise, 3 refresh-focus differential, 3 motion decisions. Some records contain multiple keyboard activations; record count is not an assertion count.
- `uiux-067-accessibility-browser.json`: 12 records: 3 idle focus styles, 6 motion styles, 3 scrollable-control/application probes.
- Regressions: 39 Node clock cases; history suite with 11 controlled clipboard scenarios; six additional Node focus scenarios; 24 native keyboard records, nine native mouse records; minimap nine geometry, three lifecycle and 33 controlled clipboard checks.
- Parent reran each command, serializing native clipboard suites. Pending scenarios, native API records and AX checks must not be conflated.

## Reproduce
From the skill directory, use `terminal` with:
```text
python3 -B -m unittest discover -s scripts -q
node scripts/test_browser_clock.cjs
node scripts/test_history_browser.cjs
node scripts/test_clipboard_focus_node.cjs
NODE_PATH=<installed Playwright node_modules> node scripts/test_clipboard_focus_chromium.cjs
NODE_PATH=<installed Playwright node_modules> node scripts/test_accessibility_chromium.cjs
python3 -B scripts/accessibility_measure.py references/uiux-067-accessibility-browser.json
NODE_PATH=<installed Playwright node_modules> node scripts/test_native_clipboard_chromium.cjs
NODE_PATH=<installed Playwright node_modules> node scripts/test_native_clipboard_keyboard.cjs
NODE_PATH=<installed Playwright node_modules> node scripts/test_minimap_chromium.cjs
```
No new dependencies, production writes, daemon restarts or scheduler changes are required.

## Primary sources
- https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html — 3:1 adjacent non-text contrast, evaluate states separately.
- https://www.w3.org/WAI/WCAG22/Techniques/aria/ARIA22.html — preexisting status role, polite updates, explicit atomic support.
- https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion — motion reduction preference.

## Remaining gaps
- Idle focus is not feedback-state text contrast. Static `.copied` white text on #10b981 calculates to 2.5367:1, below 4.5:1 for small text; rendered success/hover/pending/failure and forced-colors need a separate audit and targeted palette repair.
- No actual screen-reader speech, interactive permission prompt, cross-app clipboard, Firefox/WebKit, physical touch or performance evidence.
- Color math does not prove visibility when clipped, occluded, transformed or composited. Full focus area, keyboard usability and all controls remain outside this narrow audit.
