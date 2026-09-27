# VISION-003: technical research and evidence boundaries

## Source ledger

Retrieved source material during implementation; primary-paper HTML introductions/abstracts and selected ending analysis were read, not an exhaustive review of every table. No reported paper score is our measured score.

1. MDN, `Element.getBoundingClientRect`: https://developer.mozilla.org/en-US/docs/Web/API/Element/getBoundingClientRect . A DOMRect encloses padding/border and is relative to the viewport. Scroll invalidates viewport-relative positions. An enclosing rectangle is not necessarily the painted/clickable shape.
2. Chrome DevTools Protocol, Input: https://chromedevtools.github.io/devtools-protocol/tot/Input/ . `dispatchMouseEvent.x/y` are relative to the **main frame viewport in CSS pixels**. The initial extractor omitted parameter details; the same official page was retrieved through Jina Reader and those explicit parameter contracts were inspected. `emulateTouchFromMouseEvent` instead documents DIP; do not generalize one method's contract to every input method. Tip-of-tree docs may differ from a deployed browser; pin the target protocol revision before integration.
3. MDN, `Document.elementFromPoint`: https://developer.mozilla.org/en-US/docs/Web/API/Document/elementFromPoint . Returns the topmost element at viewport-relative coordinates. A hit-test identity, not rectangle overlap alone, is required. Frame/shadow traversal requires adapter-specific handling; a host is not proof of a descendant target.
4. MDN, `devicePixelRatio`: https://developer.mozilla.org/en-US/docs/Web/API/Window/devicePixelRatio . Ratio of physical to CSS pixels; page zoom changes DPR, pinch zoom does not. Display migration can change DPR. It supplies neither screen translation nor a universal OS input contract.
5. MDN, VisualViewport: https://developer.mozilla.org/en-US/docs/Web/API/VisualViewport . Layout and visual viewports differ under pinch zoom; offsetLeft/offsetTop are CSS offsets and scale is pinch scale. The helper does not automatically compose these values; unknown mapping is a rejection condition.
6. Microsoft, SetCursorPos: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setcursorpos . API uses screen coordinates and can clip positions to ClipCursor bounds. Page extraction displayed authorization boilerplate but the API contract and remarks were readable. This does not establish Linux/macOS units or settle every Windows DPI-awareness configuration.
7. Cheng et al., **SeeClick: Harnessing GUI Grounding for Advanced Visual GUI Agents**, arXiv:2401.10935v2 (2024): https://arxiv.org/abs/2401.10935 and https://arxiv.org/html/2401.10935v2 . Screenshot-only grounding and ScreenSpot motivate a visual route when structured observations are inaccessible. ScreenSpot grounding and downstream task evidence do not prove this hybrid gate's calibration, reliability or freshness policy.
8. Xie et al., **OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments**, arXiv:2404.07972v2 (2024): https://arxiv.org/abs/2404.07972 and https://arxiv.org/html/2404.07972v2 . Real application tasks and execution-based evaluation motivate semantic postconditions. Appendix D.6 cautions that set-of-marks can constrain exploration and have erroneous boxes. Historical benchmark numbers are not current model capability estimates and were not reproduced here.
9. Gene M. Amdahl, **Validity of the single processor approach to achieving large scale computing capabilities** (1967): https://doi.org/10.1145/1465482.1465560 . Publisher title/abstract/metadata were retrieved, not the complete PDF. The following standard Amdahl model is an engineering analysis, not an extracted experiment from that paper.
10. Hermes official skills documentation: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/ . Confirms local skills and progressive disclosure; artifacts were created with skill_manage in the explicitly requested default profile.

## Coordinate and admission contract

Store `Point(x,y,Space)`, positive `Box`, immutable `Identity(scope,document,node,role,name)`, generation and monotonic capture time. Capture a frame/document instance identifier rather than reusing node numbers across navigation. Names may legitimately change: reject and reacquire, do not silently normalize. Icon-only controls need a trusted stable semantic name; this helper conservatively rejects empty names.

Spaces are IMAGE (raster coordinates of a particular crop/resize), CSS (main-frame viewport), and OS (declared backend screen units). Negative OS origins are valid. For an axis-aligned region:

`x_out = sx*x_in + tx; y_out = sy*y_in + ty`

Two diagonal anchors determine scale and translation; at least two distinct held-out anchors check residual, including a non-collinear location. Positive scales only. Reject degenerate baselines, repeated anchors, wrong spaces, out-of-domain anchors and excessive L-infinity residual. Independent anchors are a **capture requirement**, not something their numeric distinctness can prove. Direct `Transform` construction is for trusted pre-calibration adapters/tests; untrusted coefficients must never bypass calibration.

`Transform.apply` is geometry-only and does NOT test freshness. Before using an IMAGE→CSS result call `fresh(transform.generation, transform.captured, current_generation, now, max_age)` and likewise validate the screenshot capture generation/time. Then pass its propagated error to `admit`. CSS→OS supplied to `admit` is freshness-checked there. Capture-time source lineage is adapter-owned, not encoded in Point. Never treat a successful geometry conversion alone as admission.

For bounded input error `u`, use `u_out = max(sx,sy)*u + max_heldout_residual + measurement_error`. Bounds are in the destination space. Sum conservative bounds rather than assuming independent Gaussian noise. This finite-sample envelope is not a global mathematical calibration guarantee: a nonlinear distortion can agree at anchors and fail between them. Restrict the domain and validate near the intended target. Add detector, capture synchronization, anchor measurement, and output quantization error to the supplied uncertainty budget. Integer-only OS APIs must be rounded and hit-tested at their actual dispatch point by the adapter; do not round a returned point silently after admission.

Admission requires enabled=True (not truthy), exact identity and point hit, matching generation, finite nonnegative monotonic timestamps, positive age policy, no future/stale evidence, and a strict interior envelope within both target and viewport. Output OS needs a fresh exact OS hit plus fresh CSS→OS map; calibration uncertainty is conservatively projected back into CSS to check target clearance. The helper returns coordinates, never authorization or dispatch.

Generation is global to the evidence bundle. Increment it on any relevant navigation, scroll/layout, animation, window movement, zoom, frame, monitor or focus/occlusion event. Unknown event coverage means the evidence is uncertain: recapture. Even correct generation management cannot eliminate the race after admission; serialization and immediate recheck must be enforced where input is actually dispatched. Bounds/identity checks cannot authenticate a dishonest caller.

## Three mindsets

### 1. First principles / skeptical geometry

Ask what each coordinate measures before asking whether two boxes overlap. CSS-to-CDP is an identity mapping under the explicit main-frame contract; CSS-to-OS requires translation and backend calibration. Overlap is necessary corroboration at best, not identity or hit testing. A stale image is not a recovery path. Prefer rejection over a falsely precise click.

### 2. Bayesian: Known / Likely / Uncertain

- **Known:** official coordinate contracts above; the implementation's deterministic tests pass on their synthetic inputs. A generation mismatch is directly observable and must veto.
- **Likely:** semantic filtering followed by local visual confirmation reduces search and catches some geometry/occlusion mistakes. This is a design hypothesis consistent with research motivation, not a measured uplift.
- **Uncertain:** calibration distribution shift, browser/OS capture synchronization, VLM score calibration, layout events missed by the adapter, and live task success. These require deployment-specific evidence.

A Bayesian model could use posterior odds = prior odds × likelihood ratio of joint evidence. DOM and screenshots are correlated observations of the same UI; multiplying their scores as independent probabilities double-counts evidence. Calibrate joint likelihoods on held-out labeled failures, stratified by platform/zoom/target size, inspect reliability/Brier score and false-accept rate, and choose a loss-sensitive rejection policy. No arbitrary 0.85 score is promoted to probability; this helper uses explicit engineering bounds instead.

### 3. Systems: Amdahl, RAM and latency

Measure stages separately: DOM/AX extraction, screenshot capture/encode/transfer, model inference, matching, hit testing, dispatch and postcondition. For accelerated fraction f and local speedup s, overall speedup is `1 / ((1-f) + f/s)`. Illustrative arithmetic executed in Python: f=0.1 and s=10 yields 1.0989010989010988×, **not a benchmark**. Accelerating this small gate cannot remove remote model or capture latency.

The geometry map and admission have constant-sized state; calibration is O(n) time and O(n) auxiliary memory because distinct-anchor sets are validated. Stream/filter AX candidates and keep a bounded number of evidence generations rather than retaining full histories. One 1920×1080 RGBA raster requires 8,294,400 raw bytes (Python-computed payload size, not measured RSS); encoding/decoding, copies, model tensors and buffers add memory. Cropping reduces payload but requires explicit crop transforms and can remove occluder/context evidence. Parallel capture can reduce wall time but worsen evidence skew; timestamps/generation barriers matter more than theoretical overlap. No RAM ceiling or sub-second target was empirically established.

## Verification and remaining experiments

Command: `python3 -B -m unittest discover -s ~/.hermes/skills/autonomous-ai-agents/agent-multimodal-hybrid-grounding/scripts -p 'test_*.py' -v` through terminal.

Observed 15 tests passing, exit 0 (one run: 0.026s test-runner time, not GUI latency). Includes CSS identity mapping, OS offset/nonuniform scale/negative origin, image resize, no extrapolation, finite/type checks, stale/future captures, semantic collisions, disabled controls, wrong-point hits, error envelopes, stale OS maps/hits, bad/duplicate anchors and deterministic round trips. A duplicate held-out anchor acceptance regression was observed failing, then corrected. Initial missing-helper/calibration/admission tests also demonstrated failures before implementation. Additional adversarial characterization tests were added after the basic implementation; do not claim strict test-first coverage of every branch.

Not performed: live browser/OS integration, real model inference, controlled occlusion injection, heterogeneous DPI monitor tests, nested/OOPIF/closed-shadow mapping, pinch zoom, real animation race injection, measured memory/percentile latency, model probability calibration or OSWorld/ScreenSpot replication. Required sandbox integration matrix: multiple zoom/DPR values; scroll after capture; popup over target; same-caption different node; navigation between capture/action; window movement; fractional coordinates and OS quantization; wrong focused window; multi-monitor negative origin; screenshot crop/resize; intentional desynchronization. Record false admissions and postcondition success, not just gate acceptance.

The agent-reach optional update check could not run because its CLI was absent. Jina Reader via curl and web_extract successfully retrieved the actual sources; no installation was performed. No production input, scheduler state, other profiles or BUKU_CATATAN was changed.
