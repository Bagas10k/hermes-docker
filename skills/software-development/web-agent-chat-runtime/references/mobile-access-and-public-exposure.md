# Mobile Access & Public Exposure for a Locally-Served Chat App

Making a chat app served from a machine (LAN or VPS) usable from a phone, without
leaking the data. Applies to any hand-rolled HTTP server that stores chat history.

## 1. One send path, and it must match the wire format

The chat endpoint answers **Server-Sent Events**, so only the streaming reader may read it.

- **Pitfall**: routing it through a generic `api()` helper that calls `response.json()`.
  The parse throws; if the caller does not `await` it, the user's message disappears with
  no error at all. A bare `/help` typed by a user is exactly this case.
- **Rule**: never send the chat endpoint through the JSON helper. Delete any "simple
  commands skip the stream reader" shortcut — one path for every message, with the stream
  reader handling the command event. Guard it with a static test that fails if any
  non-streaming caller targets that route.

## 2. Localhost trust is not identity (the leak that matters)

A tunnel, sidecar, or reverse proxy connects **from** `127.0.0.1`. So a shortcut like
`if client_address in ("127.0.0.1", "::1"): return True` hands the entire dataset to the
public internet the moment the service is exposed.

- **Symptom to look for**: an authenticated route answers `200` with no credentials
  through the public URL.
- **Rule**: trust loopback only when the `Host` header is *also* a loopback name
  (`localhost`, `127.0.0.1`, `::1`). Treat the tunnel hostname as untrusted.
- **Parse the port correctly for IPv6**: `Host: [::1]:8765` must strip the brackets and the
  port. A naive `split(":")[0].strip("[]")` turns `::1` into an empty string and the
  loopback check silently fails for IPv6.
- **Apply the same rule to any token-minting route.** A "pairing" or "local setup"
  endpoint that issues a session to loopback callers is the same bypass, one request away.
- **Verify it**: request an authenticated route through the public URL with no credentials.
  Expect `401`, not `200`.

## 3. Rate-limit credential guessing by the REAL client

- **Pitfall**: keying a rate limit on the peer address behind a tunnel. Every attacker and
  every legitimate user looks like `127.0.0.1`, so the limit either never triggers or one
  attacker locks out everybody.
- **Rule**: read the real client from `CF-Connecting-IP`, then `X-Real-IP`, then the first
  entry of `X-Forwarded-For`, falling back to the peer address. A short window (e.g. 10
  attempts per 15 minutes) is enough for a human typing a code once.
- **Provide revocation**: list paired devices and allow revoking one or all, so a lost or
  sold phone can be cut off without restarting the service. A daily-rotating shared code
  alone is not enough once the URL is public.

## 4. HTTPS is not optional on a phone

Browsers expose `getUserMedia` (voice recording) and `navigator.clipboard` only in a secure
context. Over plain `http://` to a LAN IP the mic button cannot work at all.

- **LAN path**: self-signed cert with SANs for every LAN address, generated locally. The
  phone shows a warning — expected, there is no CA to trust.
- **Public path**: a quick tunnel (`cloudflared tunnel --url https://127.0.0.1:PORT`) gives
  a real certificate with no account or DNS, so no browser warning. Its hostname is random
  and **changes on every restart**; read it from the tunnel log, not from memory.
- **A fixed hostname needs a Cloudflare API token with DNS rights.** A tunnel *token*
  cannot create DNS records — it authenticates the connector only. Check for a real API
  token before promising a stable domain.

## 5. Make the QR and the pair page reflect the reachable URL

- A pairing page must show the URL the *phone* can reach. When the request arrives through a
  tunnel or proxy, that hostname is the right one — returning LAN IPs there hands out an
  unreachable QR.
- Generate the QR from the same URL the page displays, and verify the two agree (compare the
  dark-module count of the generated matrix against the embedded SVG).
- A hand-rolled QR encoder is worth testing against a reference implementation at the byte
  level: mask the matrix, then compare cell-by-cell. A single wrong reserved region
  (finder separators, timing, format bits) produces a code that scans as garbage.

## 6. State payload and attachment storage on a phone connection

- **Pitfall**: inlining attachment base64 in the state payload. Every refresh re-sends every
  file, and the server re-reads and deep-copies the whole database to answer. Measured
  0.65s of CPU to deliver 4.6KB with a 32MB db.
- **Rule**: bytes live in files on disk (`data/files/<id>`), the message keeps only
  `{name, mime, kind, size, id}`, and the browser loads them from a blob route. Serialize
  the state body once and cache it, invalidated on every write, revalidated with
  `ETag` / `If-None-Match` (304 with no body). Measured 0.65s → 0.055s.
- **Send only ONE `Cache-Control` header.** A second value makes it ambiguous, and
  `no-store` silently defeats the ETag revalidation you just added.
- **Garbage-collect on delete/clear/edit, and sweep disk orphans at startup only.** Bytes
  written but never referenced by the db (crash between writing the file and saving) are
  unreachable — measured 20 such files after ordinary testing. Do not sweep on every load:
  a blob written but not yet saved would be deleted by a concurrent request.

## 7. Concurrent writes must not share a temp path

- **Pitfall**: every writer renaming the same `db.json.tmp`. Concurrent saves race and die
  with `FileNotFoundError` on the rename — measured 10 of 24 saves failing, i.e. lost
  writes. The same pattern applies to attachment writes and auth-file writes.
- **Rule**: unique temp name per call (`db.json.<pid>.<tid>.tmp`), rename into place, and
  `finally: tmp.unlink(missing_ok=True)`.

## 8. Concurrency and streaming state in the client

- **`localStorage` throws** in Safari private mode and when storage is blocked. A read on a
  path that runs per keystroke (a slash-command hint, a settings toggle) kills the whole
  app on first input. Wrap every access in `try/catch` behind a tiny `ls.get/ls.set` helper.
- **`100vh` is wrong on mobile**: it includes the URL bar and shrinks unpredictably when the
  keyboard opens, pushing the composer off screen. Use `100dvh` with a `--vh` fallback set
  from `visualViewport`.
- **iOS zooms the page** when a field under 16px gets focus. Put
  `input,textarea,select{font-size:16px}` **after** `font:inherit` — equal specificity means
  source order decides, so the shorthand otherwise wins.
- **iOS records `audio/mp4`, not webm.** Probe `MediaRecorder.isTypeSupported` and derive the
  file extension from the real mime (`.m4a`), or the file arrives unplayable.
- **Hover-only actions are unreachable on touch.** Show message action bars unconditionally
  under the mobile breakpoint.

## 9. What to verify before claiming a phone can use it

Run these, and report the actual status codes:

1. Authenticated route through the public URL with no token → expect `401`.
2. Same route with a token obtained from the pair flow → expect `200`.
3. The pair flow end to end in a real browser at phone dimensions: pairing modal appears,
   code accepted, token stored, chat list loads, a message sends, a reply arrives.
4. `POST` to the token-minting route with a wrong code → expect `401`; after N wrong tries
   → expect `429`.
5. Revoke the device, then reuse the old token → expect `401`.

Measure layout rather than trusting a screenshot: read `documentElement.scrollHeight` vs
`innerHeight` (overflow must be 0) and the composer's `getBoundingClientRect().bottom`
(must equal the viewport height). A full-page screenshot renders content that is actually
clipped or scrolled, so it cannot settle whether the composer is on screen.

## 10. Mounting behind a path prefix on a domain you already own

Publishing as `<existing-domain>/<app>` behind a portal router that strips the prefix is the
cheapest way to get a permanent HTTPS URL — no new DNS, no rotating tunnel hostname. Both
sides need work, and the server-side half is a real auth regression, not cosmetics.

**Client**

- Detect the mount from the real path once at boot and route every request through a prefix
  helper: `const BASE = location.pathname.indexOf("/app") === 0 ? "/app" : "";`
  `const U = p => BASE + p;` then `fetch(U("/api/state"))`. One absolute `/api/...` escapes to
  the domain root and 401s or 404s.
- Asset references stay relative (`./manifest.webmanifest`, `./icon.svg`), and the manifest
  needs `"start_url": "./"` and `"scope": "./"` — absolute `"/"` installs a shortcut that
  points outside the mount.
- The service worker's scope is the prefix, so build its precache list from
  `self.registration.scope` (`scope.replace(/\/$/, "") + "/icon.svg"`) rather than `"/icon.svg"`.
- Guard it with a static check that fails on any remaining `fetch("/api/...")`, `href="/"`,
  or `src="/"` in the shell. Scope the check to `fetch(`/`href=`/`src=` — a slash-command list
  (`/help`, `/new`) is chat text, not a URL, and a naive "no absolute paths" rule flags it.

**Server and proxy**

- The router rewrites `Host` to the loopback target, so a loopback-Host trust check passes for
  internet traffic and hands over the whole dataset. When the peer is local, also require
  `X-Forwarded-Host` (first value, port stripped, IPv6 brackets handled) to be a loopback name,
  and set that header explicitly in the proxy config. Verify the public URL with no token → `401`.
- Trust forwarded client-IP headers (`CF-Connecting-IP`, `X-Real-IP`, `X-Forwarded-For`) only
  when the peer is the local proxy. A LAN client can send any header; believing it lets one
  client dodge a rate limit or lock a stranger out.
- The portal's same-origin gate needs an `Origin` header on `POST`. Scripted verification
  without `Origin` gets `403` even with a valid token — send the public origin.
- `http-proxy-middleware` v4 (undici) ignores the legacy `secure: false`. Target
  `https://127.0.0.1:PORT` and pass `agent: new (require("https").Agent)({ rejectUnauthorized: false })`,
  or every request answers `504`. `changeOrigin: true` does not preserve the public hostname by
  itself; set `X-Forwarded-Host` and `X-Forwarded-Proto` in `proxyReq`.

**Verifying through the public URL**

- Cloudflare's bot protection answers `error code: 1010` to `python-urllib`'s user agent. Use
  `curl` for public-URL checks (or set a browser-like `User-Agent`); keep `python-urllib` for
  `127.0.0.1`.
- A `504` from the router with a sub-10ms `time_total` means the upstream is not listening, not
  that it is slow. Check `ss -ltn | grep PORT` before debugging the proxy.

## 11. One process owns the port

- A server started by hand and then also registered with PM2 leaves the second instance
  crash-looping on `Address already in use`: the PM2 entry shows a climbing restart counter and
  a suspicious uptime of `0s` while the hand-started process keeps serving. Free the port
  (`fuser -k PORT/tcp`) or delete the PM2 entry before starting the supervisor, then confirm the
  listening PID is the one the supervisor reports.
- `pm2 start "<shell string>"` runs through `/bin/bash -c`, and `--exp-backoff-restart-delay`
  expects a number, not a string flag — passing the string form aborts the whole start.

## 12. Prove the model gateway, not just the page

- Verify the upstream with a sentinel prompt that has exactly one correct answer ("reply with
  the single word GATEWAY_OK") and assert that word appears in the streamed text. A page that
  renders proves nothing about the gateway.
- When the upstream returns nothing, surface the resolved `base_url` and `model` in the reply
  body itself. A stale endpoint is the most common cause of an empty answer, and it must be
  readable without a debugger.
- `run_tests.sh` staying green says nothing about which endpoint production points at — see the
  test-hygiene rule in the live-app-maintenance skill before trusting a suite that touches
  provider configuration.
