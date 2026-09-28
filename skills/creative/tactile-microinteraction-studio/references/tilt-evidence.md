# TREND-003 — permission, sheen and verification

## Source evidence
Retrieved through agent-reach web/Jina on this run:
- https://developer.mozilla.org/en-US/docs/Web/API/DeviceOrientationEvent/requestPermission_static — requestPermission needs transient user activation; resolves granted/denied, rejects without required activation; absolute=false avoids unnecessary magnetometer request.
- https://developer.mozilla.org/en-US/docs/Web/API/Window/deviceorientation_event — secure context; beta/gamma orientation event fields. Capability does not guarantee readings.

Visual reference: actual `/home/ubuntu/referensi-desain/03-dashboard-admin/071-dashboard-ui.jpg` inspected. REF-071 shows Upload Files heading/support, bounded input area, then Cancel/Upload group. Borrow hierarchy and shared insets, not dashboard, 32px targets or inferred mobile behavior. Incumbent cream/lime/amber neobrutalist sheet retained. Current mobile, desktop and active-sheen captures inspected: text readable, sheen contained, controls not tilted. Preview's strong amber emphasis is a subjective tradeoff, not a measured preference.

## Causal model and pre-test predictions
Before implementation, isolate sample rotation from dialog translation: competing writers otherwise break drag. Request only on activation; generation invalidation should prevent late permission from restarting a closed preview. Finite baseline-relative deltas should bound the decorative rotation; changing the sheen center with the same inputs should keep lighting causally tied to movement. Static state must remain fully functional if every optional API fails. These are intervention predictions, not correlations about satisfaction.

A single pending RAF coalesces sensor/pointer events. A clipped radial sheen can repaint a small sample; transform does not prove GPU acceleration or a frame budget. No latency/p95, FPS or power numbers were measured. A 1800ms watchdog bounds stale-data behavior at the cost of requiring reactivation after intermittent delivery. Pointer fallback costs no new dependency but does not emulate touch hardware. Native dialog retains modality at the cost of browser-specific focus-to-chrome behavior.

## Executed evidence
`node /home/ubuntu/.hermes/skills/creative/tactile-microinteraction-studio/scripts/verify.cjs /home/ubuntu/autopilot-sandbox/trend-003` exited 0, Chromium 153.0.8010.12. verification.json records existing sheet/audio regression cases, synthetic granted/implicit/denied/rejected/missing/insecure/silent sensor branches, clamping, default off, reduced motion, pending permission cleanup and short viewport footer. Axe WCAG A/AA tags return violations=[] and incomplete=[] in inactive and active states at 390/768/1440px. Page errors empty. Impeccable detector on both template files exited 0 with []. Screenshots: sheet-{390,768,1440}.png and tilt-active-{390,768,1440}.png. Detector capture: impeccable-result.json.

Test harness corrections: empty style can be null or empty string after pointerleave; media-query change dispatch is asynchronous; implicit-permission tests must explicitly remove the method, because Chromium may expose it. Native modal focus may briefly report body when Tab enters browser chrome; assert background opener exclusion instead of an invented focus-loop contract. These were test-assumption failures, not grounds to weaken sensor or accessibility acceptance.

Known: implementation and automated Chromium contract results. Uncertain: Safari/iOS permission UX, physical sensor calibration/landscape, actual speaker/vibration, assistive technology, physical safe areas and user comfort. Synthetic hidden/pagehide and insecure-context property override are not real lifecycle or HTTP security tests. No hardware claims or full WCAG certification. No production/state.json/cron changes.
