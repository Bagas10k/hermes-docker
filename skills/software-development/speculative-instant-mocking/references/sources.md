# Official Documentation Sources & Research

## 1. Mock Service Worker (MSW 2.x)
- **Browser Integration:** https://mswjs.io/docs/integrations/browser/
  - Key finding: Service workers intercept at the network boundary. Browser requires `npx msw init <PUBLIC_DIR> --save` to place `mockServiceWorker.js` in the public root.
  - Workers activate via `worker.start({ onUnhandledRequest: 'bypass' })`. Initializing is asynchronous and must be awaited before firing app queries.
- **HTTP Response API:** https://mswjs.io/docs/api/http-response/
  - Drop-in standard for `fetch` responses using standard `Response` or `HttpResponse.json(body, init)`.
- **Streaming in MSW:** https://mswjs.io/docs/http/mocking-responses/streaming/
  - MSW supports returning a `ReadableStream` directly in `HttpResponse` when wire-level byte streaming is needed.
- **WebSocket Mocking in MSW:** https://mswjs.io/docs/websocket/
  - MSW provides `ws.link(url)` implementing the WHATWG WebSocket standard for duplex client/server events.

## 2. Web Streams Standard (WHATWG / MDN)
- **ReadableStream Constructor:** https://developer.mozilla.org/en-US/docs/Web/API/ReadableStream/ReadableStream
  - Standard `pull(controller)` loop for pull-based backpressure.
  - High water mark regulates buffer sizing (`highWaterMark: 1`).
  - Cancellation is handled via `cancel(reason)`.

## 3. Scope Boundaries & Protocol Realities
- **In-Memory Streams vs Wire SSE / WebSockets:**
  - In-memory fake streams operate in JS engine space; they bypass network stacks, proxy buffers, CORS headers, TLS handshakes, and framing parsers.
  - While ideal for deterministic, low-latency UI iteration, integration tests must verify real wire transports before production deployment.
