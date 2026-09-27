---
name: speculative-instant-mocking
description: Use when prototyping UIs with deterministic mock streams.
version: 0.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [VIBE-005, mocking, streams, msw, prototyping]
    related_skills: []
---

# Speculative Instant Mocking

Build zero-backend UI prototypes with explicitly synthetic data. The bundled browser demo uses MSW for REST and an in-memory, pull-driven ReadableStream adapter for incremental updates; it is not wire SSE or a production backend.

## When to Use
- Prototype a UI before its backend exists; reproduce loading, empty, failure and recovery states.
- Exercise cancellation, reset and superseded requests deterministically.
- Do not use synthetic results as real account, financial, operational or production evidence.

## Prerequisites
- Node.js 22.12+ and npm; modern browser with Streams and service workers.
- Initial npm install needs internet; subsequent demo requests need no API backend or credentials.
- Use only an isolated directory. Never install these mocks in a production app without explicit scope approval.

## Quick Reference
Through `terminal`, set workdir to this skill's `scripts/demo` directory:
- `npm ci` — restore pinned dependencies.
- `npm test` — Node contract tests.
- `npm run test:browser` — headless Chromium functional checks; starts and stops its own Vite server.
- `npx playwright install chromium` — only if the browser binary is missing.
- `npm run dev -- --host 127.0.0.1` — open the printed loopback URL with `?mock=1`.
- `npm run build` — production build; mocks remain disabled even with the URL opt-in.

## Procedure
1. Read [references/design.md](references/design.md). Choose the actual client boundary: REST via MSW; stream consumption via adapter. Check: never describe the adapter as SSE/WebSocket.
2. Install in the isolated demo directory. Check: package lock exists and install succeeds.
3. Run unit and browser tests before adapting code. Check: actual passing output, not inferred success.
4. Start demo and opt in with `?mock=1`. Check: visible SYNTHETIC label and successful MSW response marked `synthetic: true`.
5. Choose a seed and scenario. Run twice or reset. Check: identical payload sequence for identical inputs; no clock/random dependence.
6. Exercise error, empty, retry, rapid restart and abort. Check: stale run cannot publish; at most 20 visible records; blocked production guard remains blocked.
7. When integrating, keep a real transport behind the same consumer interface, use app build-mode guards and await `worker.start()` before mounting. Check: no live credentials, remote requests or unhandled API passthrough.
8. Stop the dev process and close browser contexts. Check: no test-owned server/browser process remains.

## Pitfalls
- Native object ReadableStream does not test HTTP chunk framing, EventSource reconnect, proxy buffering, CORS, TLS or WebSocket handshakes.
- MSW intercepts browser requests, not curl; a static Vite server is still needed to serve assets, but no API backend exists.
- Sequence determinism is guaranteed; wall-clock timing is not. Concurrent runs each own their PRNG.
- Pull-based queue limits do not bound unrelated consumer allocations. Keep the supplied bounded view or implement an equivalent cap.
- Service workers require localhost/HTTPS. Use a dedicated origin/context; do not unregister unrelated workers.
- Production is fail-closed: this prototype intentionally provides no production override. See the build guard and test.
- See [references/sources.md](references/sources.md) for official sources and protocol-extension limits.

## Verification
Run `npm test`, `npm run test:browser`, and `npm run build` through `terminal` in `scripts/demo`. Browser tests assert real DOM behavior and MSW interception, not aesthetics. See [references/verification.md](references/verification.md) for recorded execution and precise checks. Re-run after changing fixtures or integration code.
