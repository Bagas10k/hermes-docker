# Mechanics, trade-offs, and evidence

## Mechanistic model
For displacement from target: m*x'' + c*x' + k*x = 0. Natural frequency is sqrt(k/m); damping ratio is c/(2*sqrt(k*m)). These parameters shape overshoot and settling, not network or build time. End-to-end perceived latency is input dispatch + state work + paint + settling; optimizing only settling cannot remove the other terms. Amdahl bound remains 1/((1-p)+p/s), with p measured rather than guessed.

Use Motion instead of a hand-written frame integrator. The template uses a scalar animation feeding one transform writer; pointerdown stops the running spring first. This prevents two controllers fighting over position. Only open/settling interactions animate; there is no permanent frame loop.

## Bayesian experiment contract
Prediction before execution: a downward handle drag past the threshold closes; a short or cancelled drag stays open and returns to zero. Reduced motion positions immediately and suppresses optional vibration. These predictions were verified using the shipped template in Chromium. This raises confidence in that implementation path, not in all physical devices or user satisfaction.

Known: documented API contracts; automated Chromium outcomes. Likely: native dialog and a mature spring library reduce custom lifecycle bugs. Uncertain: tactile comfort, physical vibration, touch scroll arbitration on Safari/Android, screen-reader experience, p95 frame latency. No probability or satisfaction score is fabricated.

## Design constraints and options
Minimize interruption and implementation cost subject to operable keyboard controls, cancellable gestures, no loss of committed settings, and reduced-motion support. Native dialog plus Motion is chosen over a fully custom modal/focus trap. React projects should reuse their existing accessible dialog library and Motion dependency rather than port this vanilla controller wholesale. CSS-only press feedback remains preferable when no settling/drag is required.

The template intentionally uses distance-only dismissal, not fling velocity: deterministic and easier to verify, at the cost of not treating a short fast flick as dismiss. Candidate threshold is min(120px, 30% sheet height); user testing must calibrate it. No claim of universal optimality.

## Failure handling
Pointer capture requires an active pointer ID; synthetic events alone cannot validate capture. The verifier drives real mouse input, injecting only the cancellation event for that branch. Handle-only gesture ownership leaves content available for native scroll. Keep pinch zoom available. Escape closes via native dialog behavior and the close event performs cleanup. Haptics are capability-detected, opt-in, short, throttled, and nonessential.

## Official sources retrieved 2026-09-23
- https://motion.dev/docs/animate : hybrid animation, scalar onUpdate, stop controls.
- https://motion.dev/docs/spring : physical parameters, generator sampling in milliseconds, unbounded zero-damping caveat.
- https://developer.mozilla.org/en-US/docs/Web/API/Navigator/vibrate : limited availability, sticky activation, return value is not proof of physical vibration.
- https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/dialog : modal inert background, Escape, explicit close button and focus considerations.
- https://developer.mozilla.org/en-US/docs/Web/API/Element/setPointerCapture : active pointer requirement and capture lifetime.
- https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/touch-action : browser gesture negotiation before gesture start and pointercancel.
- https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion : minimizing nonessential motion.

## Reproduction evidence
Node-installed Motion 13.4.1; Playwright Chromium 153.0.8010.12. `scripts/verify.cjs` passed at 390, 768, 1440px; page errors empty. Hardware haptics are explicitly stubbed. Production services were not changed. This original run did not include screenshots or real-device validation. For the later implemented tilt, sheen, screenshots and AA checks, read [TREND-003 source and evidence](tilt-evidence.md); real-device validation remains outstanding.
