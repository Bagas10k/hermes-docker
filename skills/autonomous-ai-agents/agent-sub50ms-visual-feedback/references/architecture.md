# Measurement contract and bounded perception

## Sources consulted
- MDN requestVideoFrameCallback: https://developer.mozilla.org/en-US/docs/Web/API/HTMLVideoElement/requestVideoFrameCallback — callbacks follow composited video, bounded by video/paint cadence; captureTime for remote video uses clock estimation.
- MDN VideoFrame.close: https://developer.mozilla.org/en-US/docs/Web/API/VideoFrame/close — release media resources explicitly.
- W3C WebRTC Stats, Candidate Recommendation Draft: https://www.w3.org/TR/webrtc-stats/ — cumulative jitterBufferDelay and emitted counts measure a component, not full feedback latency. Use window deltas with positive count and reset detection; do not call a ratio a percentile.

## Mechanistic model
T_feedback = T_capture_wait + T_encode + T_network + T_jitter + T_decode + T_queue + T_perception + T_render.
T_verified_action additionally includes grounding, policy, dispatch, application response and postcondition verification. A faster pixel comparison changes only its own fraction. Amdahl S = 1 / ((1-p) + p/s). Without measured p, numerical speedup claims are unjustified. At sampling frequency f, ideal random-phase capture wait spans 0..1/f, before any scheduling jitter. Sum of component p95 values is not end-to-end p95; measure correlated complete traces.

Per pixel D(x,y)=max_c |I_t(x,y,c)-I_prev(x,y,c)|. Mark D>tau and emit tiles containing at least one marked pixel. Complexity O(W*H*C), state O(W*H*C), plus temporary signed buffers. This deliberately prioritizes tiny-change recall over noise rejection. Each emitted half-open box is clipped to frame bounds. A frame must be within max_age and newer than the accepted sequence before baseline mutation. Geometry changes establish a new baseline and require full regrounding.

## Production topology and trade-offs
Authorized source -> WebRTC decode -> latest-only frame slot -> bounded worker -> delta ROI invalidation -> semantic grounding -> policy/action -> authoritative postcondition.
Commands and receipts travel a distinct reliable, idempotent channel. Keep session/epoch plus sequence: a new session explicitly resets the detector. Never accept a random sequence reset as current. Do not serialize raw full-frame arrays to JSON or retain unbounded screenshots. Avoid exposing captures and private DOM in public dashboards.

CPU NumPy is a portable reference, not a zero-copy implementation. GPU compute can avoid readbacks only if the consumer remains GPU-side; getImageData/readback may dominate. Compare native ROI, full-frame CPU, and GPU paths using the same labeled samples and measured readback cost. Latest-frame dropping reduces queue age but may miss transients; periodic semantic refresh and task-specific event capture compensate, not prove completeness.

## Bayesian evidence
Known: cited API semantics and executed synthetic detector assertions. Likely: bounded latest-only observations improve age under overload; requires a load experiment. Uncertain: sub-50ms live feedback, UI false-negative rate, and model task success. Do not fabricate probability estimates from heuristic scores. Calibrate on labeled changes and unchanged animations; stratify by font size, codec, DPI, and motion. An unchanged frame after a successful server-side mutation is a necessary negative control for any success classifier.

## Experiment design
Before running: predict identical frames produce unchanged, one-pixel mutation produces changed, age violations preserve baseline, and shape change produces baseline. Benchmark only observe() on prepared synthetic RGB inputs; exclude construction and clearly state this exclusion. Use perf_counter for durations and independent per-frame samples. Run browser tests later with action_id, frame sequence, geometry version, capture estimate, callback time, worker start/end, and verified postcondition time. Do not subtract unrelated machine clocks. Stop optimization when perception is not the dominant latency fraction; optimize the measured bottleneck instead.
