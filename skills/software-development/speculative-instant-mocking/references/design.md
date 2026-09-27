# Architecture and Design Tradeoffs: Speculative Instant Mocking

## 1. Domain Separation: REST Interception vs Stream Adapter

### MSW (Mock Service Worker 2.x) for HTTP REST
- **Role:** Intercepts outgoing client HTTP fetch calls (`/api/seed`, `/api/health`) at the network worker level via standard Service Worker interception.
- **Tradeoff:** Intercepts real browser `fetch` requests seamlessly without patching global window methods or adding bespoke dev server routes. Requires a Service Worker environment (supported on `localhost` or HTTPS).

### In-Memory ReadableStream Fake vs Wire SSE
- **In-Memory ReadableStream Fake:**
  - Operates as a pull-driven Web Streams API `ReadableStream` yielding discrete JavaScript object chunks directly into the consumer pipeline.
  - Guarantees zero network latency overhead, zero port conflicts, and precise synchronous/microtask abort fanning.
  - Backpressure is governed by the native stream controller's `pull()` loop and `highWaterMark: 1`.
- **Wire SSE (Server-Sent Events) Difference:**
  - Real SSE requires an HTTP response with `Content-Type: text/event-stream`, UTF-8 newline-delimited framing (`data: ...\n\n`), connection reconnect semantics via `Last-Event-ID`, and proxy buffering traversal.
  - The in-memory stream adapter models incremental UI data flow and state machine transitions, but does *not* validate HTTP wire framing, chunk boundaries, or transport disconnection/reconnection cycles.

## 2. Determinism and Seeding Strategy
- **PRNG:** Implements a Lehmer/LCG linear congruential generator (`state = (state * 1664525 + 1013904223) >>> 0`).
- **Idempotency:** Given an identical seed, identical count, and identical scenario, the generator produces the exact same sequence of synthetic records every time across initial runs and resets.
- **Isolation:** Each runner invocation creates a local generator closure state, eliminating global seed corruption across concurrent runs.

## 3. Concurrency, Fencing, and Abort Architecture
- **Superseded Run Fencing:** Every call to `runner.run()` increments a monotonic integer `epoch`. When asynchronous chunk yields occur, incoming values from an earlier epoch are immediately dropped and not published to UI state or buffers.
- **Active Cancellation:** Each invocation aborts the previous active `AbortController`, which triggers reader cancellation, clears pending timers, and errors the underlying stream with an `AbortError`.
- **Clean Resource Teardown:** The consumer loop guarantees reader lock release and cancellation in a `finally` block, preventing memory leaks and orphaned pull intervals.

## 4. Bounded Buffers & Memory Safety
- The UI runner applies a sliding window slice (`rows.slice(-20)`), ensuring that even high-throughput or infinite streams cannot grow the DOM or consumer memory unboundedly.
- Inputs (`seed`, `count`, `delay`, `scenario`) are validated before stream creation with strict bounds (e.g., max 10,000 count, finite delays).

## 5. Explicit Synthetic Labeling & Production Guards
- **Synthetic Marking:** Every object chunk emitted contains `synthetic: true`. Handlers and UI elements display explicit `[SYNTHETIC]` tags and warnings to prevent any conflation with live production data.
- **Fail-Closed Opt-In Guard:** Mocking requires `import.meta.env.DEV === true` AND query parameter `?mock=1`. In production builds (`npm run build`), mocks fail closed and cannot be activated even if the URL parameter is supplied.
