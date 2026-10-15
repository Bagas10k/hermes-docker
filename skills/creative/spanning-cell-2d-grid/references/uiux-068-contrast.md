# Clipboard feedback contrast: bounded rendered-state audit

Author: Bagas Cihuy & Hermes Agent.

## Mechanism and intervention
Output = f(clipboard promise state, hover, keyboard focus, media palette, CSS transition, alpha compositing). Small copy text uses a local 4.5:1 gate; outline against its adjacent bar uses 3:1. Width/offset 2px is the fixture contract, not a general WCAG focus-area certificate.

Existing success was white on #10b981, measured 2.5367:1. Repair success to white/#065f46 (7.6837:1), success-hover white/#047857 (5.4839:1). Retain blue outline against bar #f1f5f9 (4.7179:1). Pending and failure keep their readable neutral fills and distinct labels/live status. This audit does not require aria-busy: the existing implementation uses live status text; do not invent a missing attribute contract to force unrelated code changes.

Do not hide a transition defect by disabling animations only in the test. Dark-on-light to light-on-dark interpolation can cross a low-contrast interval even with compliant endpoints. Restrict the actual component transition to outline-offset; color changes are discrete. Confirm computed transitionProperty in the browser and retain reduced-motion regression.

## Forced colors pitfall
Chromium exposes Highlight as rgba(5,0,73,0.8) in forced-light and rgba(0,230,255,0.8) in forced-dark. A parser that drops alpha and a test that skips all forced-colors ratios both overstate verification. Keep forced-color-adjust:auto. For the known flat adjacent bar, composite each channel C = alpha*foreground + (1-alpha)*background before sRGB luminance. Resulting outline ratios are 11.2993 and 8.7281 respectively; text is 21:1. These numbers are specific to this emulated palette, not all user OS settings.

## Evidence contract
- `test_feedback_contrast_chromium.cjs`: actual Chromium DOM/CSS, controlled clipboard promises and app 1500ms feedback reset timer. Native Tab input and real mouse hover. Wait for actual element animation completion. No CSS override to fake readability.
- Matrix: 390/768/1280 width × normal-light/forced-light/forced-dark × idle/pending/success/failure × hover off/on.
- `feedback_contrast.py`: strict full-matrix gate using existing `accessibility_measure.py` luminance. Reject missing/duplicate coordinates, malformed/transparent backdrops, nonfinite bounds and unsupported gradient/opacity contexts. Evaluate ratios without premature rounding.
- `test_feedback_contrast.py`: eight deterministic methods using explicitly synthetic unit inputs. These are not browser evidence. Negative cases exercise low contrast, false media/hover/focus, wrong labels, empty evidence, duplicate coverage and alpha validation.
- Browser records report observed media match, hover match, focus, text, status, colors, widths, alpha, ancestor opacity and unfinished animations. Shadow/filter/occlusion/pixel fidelity are not comprehensively audited.

## Reproduction
Run through `terminal` from the skill directory, using an already installed Playwright NODE_PATH:

```text
python3 -B -m unittest discover -s scripts -q
NODE_PATH=<installed Playwright node_modules> node scripts/test_feedback_contrast_chromium.cjs
python3 -B scripts/feedback_contrast.py references/uiux-068-browser.json
node scripts/test_browser_clock.cjs
node scripts/test_history_browser.cjs
node scripts/test_clipboard_focus_node.cjs
NODE_PATH=<installed Playwright node_modules> node scripts/test_accessibility_chromium.cjs
NODE_PATH=<installed Playwright node_modules> node scripts/test_clipboard_focus_chromium.cjs
NODE_PATH=<installed Playwright node_modules> node scripts/test_native_clipboard_chromium.cjs
NODE_PATH=<installed Playwright node_modules> node scripts/test_native_clipboard_keyboard.cjs
NODE_PATH=<installed Playwright node_modules> node scripts/test_minimap_chromium.cjs
```

Serialize native clipboard runners to avoid shared clipboard interference. Parent ran every command above: 355 Python methods; 72 new Chromium records; Node clock 39, clipboard 11, focus suite; browser accessibility12, focus27, native-pointer9, native-keyboard24; minimap geometry9/lifecycle3/controlled clipboard33. Browser version 156.0.8078.4. Commands, outputs, exit codes and SHA-256 are in `uiux-068-parent-verification.json`.

## Sources
- https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html — normal text at least 4.5:1, exceptions do not justify unreadable feedback.
- https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html — adjacent non-text contrast.
- https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/forced-colors — native semantics, palette forcing at paint time; shadows are suppressed.

## Limits and next useful test
This is computed-style evidence on a local fixture, not screen-reader speech, OS cross-application clipboard, physical high-contrast mode, Firefox/WebKit, full WCAG, pixel screenshot inspection, FPS or latency. Clipping/occlusion and actual browser zoom/reflow need separate geometric verification. No production service or scheduler changed.
