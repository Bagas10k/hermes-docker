# Architecture and evidence

## Contract and scope
Real JSON input -> JSON.parse -> static semantic status -> optional bounded motion. Parsing happens independently from effects; a motion preference can never change validation outcome. Integrate a real compiler via an adapter only after testing its event semantics; no fake build completion is shipped.

## Mechanistic model
Feedback latency = result delivery + synchronous text update + next rendered frame. Animation duration is not compiler latency. Optimizing visual feedback cannot speed up parsing or compilation: Amdahl S=1/((1-p)+p/s), with p measured on the actual pipeline, not assumed. The component owns at most one animation, no rAF loop and no recurring timer. Explicit finite duration and cancellation bound work; this does not prove zero total CPU/GPU.

## Evidence and predictions
Prediction before tests: invalid JSON produces error, corrected JSON success; 100 rapid status updates produce the latest text without a queue; reduced-motion cancels WAAPI; dispose prevents updates. Chromium browser results confirmed these local properties. Initial foreground test failed because browser document.hidden was true; bringing the actual page to front made the same test pass. This is negative evidence that the visibility guard is active, not a reason to remove it.

A second harness race checked media state before the asynchronous change event arrived. Await the media-query change event, not a guessed sleep. In browser_exec, js automatically awaits a returned promise: register a future-event promise using `void 0` as the last expression, change emulation, then await it separately; otherwise the harness waits for an event it has not triggered yet.

Known: MDN API semantics and local Chromium checks. Likely: restrained optional displacement is less distracting than continuously scrambled text. Uncertain: subjective comfort, productivity, hardware rendering costs, cross-browser behavior and screen-reader announcement quality. No invented confidence percentage or certification.

## Design trade-offs
DOM text + native WAAPI beats Canvas for selectable, accessible status messages. A small fixed spring-like keyframe sequence is not a physical spring solver. Use a dedicated motion library for interactive interruption/velocity continuity. Avoid per-letter DOM expansion, random glyph mutation, color flashes and duplicated screen-reader content. Effects are off by default; reduced-motion always wins. Cooldown suppresses motion only; latest diagnostic text remains immediate. Fixed 2000-character display cap bounds status size; preserve full logs separately in a production adapter.

## Sources
Retrieved from primary documentation during this cycle:
- https://developer.mozilla.org/en-US/docs/Web/API/Element/animate — animate creates independent Animation instances.
- https://developer.mozilla.org/en-US/docs/Web/API/Animation/cancel — cancel clears effects; an accessed finished promise may reject with AbortError.
- https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion — OS/user-agent motion preference.
- https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html — non-essential interactive motion can be disabled (AAA criterion, not certification).

## Reproduction
Open templates/studio.html in a foreground Chromium tab. Execute scripts/browser-checks.js with awaitPromise, then emulate reduced-motion during an effect and await the MediaQueryList change event. Check 390px and 1440px overflow. Evidence in browser-results.json. Tests cover actual JSON validation/recovery, default-off, bounded effect, burst cooldown, natural completion, text-only injection handling, semantic attributes, absent API, manual disable, invalid kind, disposal, two widths and live preference changes. No visual aesthetics, browser fleet, human comfort, throughput or compiler integration claims.
