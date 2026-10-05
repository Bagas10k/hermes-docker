# Architecture and evidence

## Sources consulted
- MDN rAF: https://developer.mozilla.org/en-US/docs/Web/API/Window/requestAnimationFrame — one-shot scheduling, timestamps, refresh-rate dependence.
- MDN visibility: https://developer.mozilla.org/en-US/docs/Web/API/Page_Visibility_API — hidden document events; CSS-hidden iframe limitation.
- MDN reduced motion: https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion — remove nonessential motion on user preference.

## Mechanism and bounds
Use psi(x,y,t)=sin(kx+t)sin(ky-t)/k. Its curl velocity is (sin(kx+t)cos(ky-t), -cos(kx+t)sin(ky-t)); analytic divergence cancels. This is a periodic smooth field, not noise. Integrate x += speed*v*dt, dt capped at 0.032 seconds. Preserve elapsed-time energy decay exp(-dt/0.8). The wrap boundary is a visual recycle, not a physical boundary condition.

Position storage is Float32Array(2*N), hence 8*N bytes; default measured 2880 bytes. Two 240-entry Float32 metric rings are bounded. Bitmap raw RGBA storage is at most about eight million bytes; browser surfaces/compositor add overhead, so this is not a process RSS bound. Work is O(N) plus pixel fill. Paths are batched into three strokes. Some small JS allocations remain; no zero-GC claim.

Amdahl: if field evaluation occupies fraction p of total frame time, optimizing it by s bounds whole-frame speedup to 1/((1-p)+p/s). No measured p decomposition is available, so no speedup percentage is claimed. Optimizing field arithmetic cannot remove fill/compositor cost.

## Predictions before acceptance
Pause, reduced motion, idle and disposal must leave pendingRAF=false. Actual editor input must wake the original non-disposed controller. Positive callback progression alone cannot validate pixel correctness or aesthetics. Pixel non-background checks are weak smoke tests, not visual quality review.

## Evidence and belief calibration
Known in local Chromium: initial hidden page blocked scheduling; bringing it to front rendered frames. Pause held frame count constant. Repeated resume retained one controller handle. Reduced-motion emulation stopped scheduling. 390px DPR3 emulation had no horizontal overflow and the bounded bitmap held. Default 45-second inactivity produced idle with no pending rAF; real textarea input resumed the original controller. Repeated dispose/resume/activity stayed disposed.

Measured original desktop run: p95 callback cost approximately 0.4ms and p95 frame interval approximately 16.7ms over the latest 240 samples. Other windows measured callback p95 about 0.6ms and interval p95 about 16.8ms. These are headless/local browser observations, not end-to-end latency or universal 60 FPS certification.

A replaced test controller did not wake through the old editor listener, as expected from the retained closure. A fresh original template passed the full idle/input path; store this negative test to prevent faulty hot-replacement integrations. Raw evidence is in browser-results.json.

Likely: bounded typed buffers reduce allocation pressure relative to unbounded object emission; not a measured GC improvement. Uncertain: phone thermals, battery, Safari/Firefox rendering and subjective flow-state improvement. Do not equate activity counts with cognitive focus.

## Trade-offs and stopping rule
Choose analytic Canvas 2D for deterministic zero-package setup at modest counts. Choose established noise implementations only when visual stochasticity is required, or WebGL when measured bottlenecks justify added complexity. OffscreenCanvas/workers add messaging and lifecycle cost; do not assume they improve latency. Stop after lifecycle/functional acceptance; further performance claims require profiling on the target device. Production integration remains a separately authorized task.
