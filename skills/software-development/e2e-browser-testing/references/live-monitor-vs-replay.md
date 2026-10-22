# Live monitor versus replay acceptance

- Treat a live-only requirement as an engine contract, not merely a badge change: remove pause, rewind, speed, scrubber, review state, and replay rAF loops. Automatically follow the latest observed snapshot.
- Distinguish transport freshness from activity freshness. Display last successful synchronization separately from last observed event time; never extend event duration to wall-clock time or infer active work from an open session.
- Test automatic arrival by appending a neutral synthetic session and paired event into a disposable database while a real browser remains open. Wait for the resulting DOM without click, reload, visibility event injection, or accelerated timers. Record observed delay as one local sample, not p95 or production latency.
- Preserve node identity for unchanged snapshots. Changed same-session data must preserve keyboard focus, disclosure, and scroll on the actual scrolling viewport, not the child chart container.
- Test new-data entry motion separately from history rendering: initial snapshot has no sequential replay; new IDs may animate once and must settle. Reduced motion must still update data.
- Enforce zero-duration bounds from raw observed max-minus-min, not a denominator clamped to one for safe geometry.
- On authentication expiry clear text AND attributes (time.dateTime/title), details and session options, invalidate late responses, and stop polling. Verify retries can restart without a stuck in-flight guard.
- Use controlled bounded polling when the existing SSE source only sends periodic invalidations and adding SSE would not improve source freshness. Disclose polling plus network delay; do not call it instantaneous streaming.
- Preserve explicit session deep links even when the capped runs listing is empty or omits that session. Endpoint authorization remains the boundary.
