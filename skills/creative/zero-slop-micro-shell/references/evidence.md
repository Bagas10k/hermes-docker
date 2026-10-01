# Tested evidence and reusable matrix
LIVING-003 lab artifact: ~/autopilot-sandbox/living-003/index.html. Runner: test.cjs; short-viewport follow-up: scroll-test.cjs. Invoke through terminal: `node ~/autopilot-sandbox/living-003/test.cjs && node ~/autopilot-sandbox/living-003/scroll-test.cjs`. Set TEST_DEPS to a directory containing playwright and axe-core, CHROMIUM_PATH to a browser binary, to override local defaults.

Six viewport cases: 390x844,1440x900,320x568,390x420,844x390,320x300. Main and expanded-dialog axe scans; preserve raw violations and incompletes. Verify counts, boundary, undo, reset, Space/Enter, focus, Escape, idle DOM silence, DPR cap and reduced motion. A separate short-height test checks heading and last diagnostics row through internal scroll at 320x300,320x568,390x420.

Visual references inspected: REF-071 dashboard modal for inset and action hierarchy; ui-layouts responsive-modal source for desktop/mobile adaptation. Do not copy its custom modal semantics without testing focus. Official native dialog is smaller for a static microapp.

Scope is Chromium headless, not physical touch, Safari, screen-reader certification, hardware haptics, or perceived latency. No backend and no production deployment.
