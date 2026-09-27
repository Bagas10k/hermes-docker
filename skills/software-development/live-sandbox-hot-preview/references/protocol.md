# Protocol, evidence, and decision bounds

## Sources read
- MDN Window.postMessage: https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage
- MDN iframe sandbox: https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe
- MDN unhandledrejection: https://developer.mozilla.org/en-US/docs/Web/API/Window/unhandledrejection_event
Retrieved through Agent Reach's Jina Reader route. MDN documents exact origin matching, opaque-origin exceptions, the allow-scripts plus allow-same-origin danger, and cross-origin rejection visibility limits.

## Mechanism
Editor -> new iframe document -> ready(id) -> run(id, html, css, code) -> executed/error(id).
Generation changes on Stop and Run. Parent accepts only its current iframe's WindowProxy, origin null, exact generation, known channel/kind, and bounded text. Child accepts only parent and only its first matching run. Wildcard addressing is necessary for opaque origins; no credentials or host RPC privileges cross the bridge.

Execution creates style, a main element via innerHTML, and a script via textContent. The bootstrap is installed before the user script. Parent keeps error status sticky because script insertion can emit error and then still return. Status is text-only, limited to 8000 characters; each message to 2000; each source field to 100000; accepted-message budget to 100 per generation. These are conservative starting bounds, not measured optimal parameters.

## Three mindsets
Mechanistic: feedback time is debounce + frame initialization + message delivery + execution + rendering. Ack time excludes proof of painted pixels. Replacing only the iframe preserves editor state while eliminating preview-global accumulation. Amdahl bounds any improvement to the fraction actually spent in preview reload; there is no measured end-to-end speedup claim.
Bayesian: predict counter reaches 2, parent DOM access fails, fetch fails, syntax/runtime/rejection errors stay visible. Recorded results support these mechanisms in one Chromium environment. Flow-state improvement, mobile touch comfort, Firefox/Safari parity, and p95 are untested.
System design: minimize disruption and resource retention subject to editor integrity and explicit trust scope. Fresh-document reset sacrifices preview state but reduces leaked listeners/timers. HMR is preferable for framework applications needing state retention; workers support terminate for pure computation but cannot render DOM. Full malicious DOM programs need dedicated isolated infrastructure rather than this local template.

## Empirical lessons
An initial isolation probe replaced document.body then read a detached main node, hiding the SecurityError text. Correct the probe to update the actual counter node; do not weaken isolation to satisfy a broken test. A separate real flaw allowed executed acknowledgement to overwrite the error status; sticky error state fixes it and has a regression check.

The browser evidence file contains ten passing checks. The first batch ran before the small sticky-status patch; the corrected isolation probe, sticky-error regression, and forged-source test ran after it. No throughput benchmark or universal zero-network guarantee is claimed.

## Rerun recipe
Open template with browser_exec, fill #code, click #run, wait for #status result. Use a counter onclick handler followed by two clicks; throw Error; enter invalid `const = ;`; reject Promise; try parent.document and report caught exception in #counter; attempt fetch and surface rejection. Send a fake vibe-preview event from the parent and confirm status unchanged. Stop and assert iframe count zero. Emulate 390px viewport and compare scrollWidth to innerWidth. Save results with environment and time if collecting performance distributions.
