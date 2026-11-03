## 2. Network Infrastructure, Proxies & Tunnels
- **Production/Permanent Tools**: Must run over a secure, dedicated domain via **Cloudflare Zero Trust** (Argo Tunnel, e.g., using a registered token). Do not expose RDP ports directly to the public internet.
- **Path-mounted auxiliary app (HexChat pattern)**: To expose a secondary local app under `https://domain/app` via the existing router (e.g. `penelitian-ai` on :3050) instead of a new tunnel/subdomain, add a `createProxyMiddleware` with `pathRewrite: { '^/app': '' }`, `X-Forwarded-Prefix`/`X-Forwarded-Host`/`X-Forwarded-Proto` headers, and for self-signed TLS use `new https.Agent({ rejectUnauthorized: false })` as `agent` (undici ignores `secure:false`). On the app side, detect the mount via `location.pathname.indexOf("/app")===0` and prefix all fetches with `BASE+path` (`U()` helper), use relative `href="./..."` and `scope:"./"` in manifest, and make `_is_loopback_host`/`check_auth` reject `X-Forwarded-Host` containing the public domain and only trust `CF-Connecting-IP`/`X-Forwarded-For` from a local peer — otherwise the proxy bypasses pairing/auth.
- **Multi-Tunnel & Multi-Project Ingress**:
  - Prefer ONE central `cloudflared` connector under PM2 (`cf-tunnel`) mapping subdomains to local ports in the Cloudflare dashboard (`localhost:3050`, `localhost:3000`, `localhost:9119`).
  - **Running Multiple Tunnels Concurrently**: When the user requires 2+ distinct tunnels running on the same host (e.g. separate domains/tokens):
    * Store tokens cleanly in `~/.chronicle-secrets/cf-token-1`, `~/.chronicle-secrets/cf-token-2` (`chmod 600`).
    * Cloudflared binds to a local metrics listener. When launching via PM2 or scripts, pass `--metrics 127.0.0.1:<port>` as a **tunnel command option** BEFORE the `run` subcommand (`cloudflared tunnel --metrics 127.0.0.1:20241 run --token-file ...`). Passing `--metrics` after `run` causes `cloudflared` to show its help text and fail.
    * If Cloudflare Edge returns `Unauthorized: Invalid tunnel secret`, the secret was revoked or regenerated in the dashboard; prompt the user to copy the active token from the tunnel install box.
  - **Non-Root Daemon Installation & Edge Registration**:
  - When `sudo` requires a password on headless VPS instances, avoid `sudo apt-get install cloudflared` or `cloudflared service install`. Fetch the standalone binary directly to `~/.local/bin/cloudflared` (`chmod +x`), save the token with `chmod 600` in `~/.chronicle-secrets/cloudflare-tunnel-token`, and supervise via PM2:
    `pm2 start cloudflared --name cf-tunnel -- tunnel run --token-file ~/.chronicle-secrets/cloudflare-tunnel-token`
  - **Edge Registration Invariant**: The connector establishes 4 HA QUIC connections to regional Cloudflare Edge locations immediately. The Cloudflare Zero Trust web UI uses periodic polling; if the browser still shows "No connection detected", refreshing the web page or clicking "Next" moves immediately to the Public Hostname configuration.
- **Single-Domain Ecosystem Dashboard Pattern**:
  - When unifying multiple distinct backend projects under a single root domain, serve a centralized master dashboard on `/` styled identically to the production design system (Warm Paper & Obsidian, Plus Jakarta Sans & JetBrains Mono, pure SVG icons, zero emoji).
  - Reverse-proxy sibling ports internally (`/jajan` -> `:3000`, `/hermes` -> `:9119`, `/buku` -> `:3050/buku`, `/telemetry` -> `:8090`) with `X-Forwarded-Prefix` headers, so users can navigate between all apps from a single HTTPS domain without exposing internal ports.
- **Dynamic URL Prefix Resolution for Subpath-Proxied Dashboards & SSE/WS**:
  - **Rule**: Never hardcode absolute root paths like `fetch('/api/...')`, `new EventSource('/api/stream')`, or `new WebSocket('ws://...')` in dashboards intended to be embedded or proxied under subpaths (e.g., `/telemetry/` or `/trading/`).
  - **Mechanism**: On the public domain, a root-relative path `/api/...` bypasses the reverse proxy prefix and hits the root host instead of the proxied sub-service (`/trading/api/...`), resulting in 404 or routing collision. Likewise, bare WebSocket URLs without the subpath prefix fail to route through the proxy upgrade handler.
  - **Action**:
    1. *Express Proxy Setup*:
       ```javascript
       const appProxy = createProxyMiddleware({
           target: 'http://127.0.0.1:PORT',
           changeOrigin: true,
           ws: true,
           pathRewrite: (path) => path.replace(/^\/subpath/, '') || '/',
           on: { proxyReq: (pReq) => pReq.setHeader('X-Forwarded-Prefix', '/subpath') }
       });
       app.use('/subpath', appProxy);
       ```
    *Pitfall (The `pathRewrite` Empty String Trap)*: Never use `pathRewrite: { '^/subpath': '' }`. When a client requests `/subpath` without a trailing slash, stripping the prefix produces `""` (empty string), which Express/Node HTTP target servers reject with HTTP 404. Always use `(path) => path.replace(/^\/subpath/, '') || '/'`.
    2. *Dual-Compatible Frontend Resolution (Local Standalone & Subpath Proxy)*:
       ```javascript
       const BASE_PATH = window.location.pathname.startsWith('/subpath') ? '/subpath' : '';
       // REST calls:
       fetch(`${BASE_PATH}/api/endpoint`);
       // WebSocket stream:
       const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
       const wsUrl = `${protocol}//${window.location.host}${BASE_PATH}`;
       const ws = new WebSocket(wsUrl);
       ```
    This enables the exact same codebase to operate identically on local standalone ports (`http://localhost:3070`) and behind public subpath reverse proxies (`https://domain.com/trading/`).
- **CRITICAL PITFALL: Multi-Tenant Next.js Asset Route Collision (`/_next/` Collision)**:
  - **Rule**: When hosting two or more independent Next.js applications (e.g. Supabase Studio on `:8000` and 9Router on `:20128`) behind a single Express/Node reverse proxy gateway, NEVER map `/_next` statically to only one upstream service. Multiplex `/_next` dynamically using context-aware Referer routing with an automated fallback probe, and mount at root level (`app.use(async (req, res, next) => { if (!req.path.startsWith('/_next/')) return next(); ... })`).
  - **Mechanism**: Every compiled Next.js application serves client chunks at `/_next/static/chunks/`. If the gateway blindly forwards all `/_next` requests to service A, service B's chunks return HTTP 404. Without client scripts, React hydration fails and the page freezes permanently on the initial static server markup (e.g. infinite "Loading..."). Additionally, mounting via `app.use('/_next', proxy)` strips the prefix from `req.url` in Express, causing requests to reach upstreams as `/static/chunks/...` unless mounted at root.
  - **Action**: Check `req.headers['referer']` to match the initiating subpath/app (`/project` or `/supabase` -> Supabase Studio; `/login` or `/dashboard` -> 9Router). For ambiguous or direct requests, perform a fast HEAD probe to upstream A; if 200 OK proxy to A, otherwise proxy to upstream B. Ensure upstream Basic Auth headers are injected for protected sub-resources.
- **CRITICAL PITFALL: The Multi-Proxy WebSocket Upgrade Dropping Bug**:
  - **Rule**: When hosting multiple sub-services behind a central Node.js reverse proxy gateway (e.g. `server.js` acting as reverse proxy for `/trading`, `/telemetry`, and `/hermes`), NEVER attach a single proxy instance directly to `server.on('upgrade', proxy.upgrade)`.
  - **Mechanism**: Attaching `server.on('upgrade', hermesProxy.upgrade)` routes EVERY incoming WebSocket handshake exclusively to that single proxy, dropping or rejecting WebSocket handshakes for all other proxied subpaths (`/trading`, `/telemetry`). The frontend REST APIs will return HTTP 200 OK, giving a false sense of health, but live charts, tickers, and WS streams in the browser will silently fail or freeze without errors on the server.
  - **Action**: Always multiplex `server.on('upgrade', (req, socket, head) => ...)` by matching `req.url` prefixes:
    ```javascript
    server.on('upgrade', (req, socket, head) => {
      const url = req.url || '';
      if (url.startsWith('/trading')) {
        tradingProxy.upgrade(req, socket, head);
      } else if (url.startsWith('/telemetry')) {
        telemetryProxy.upgrade(req, socket, head);
      } else {
        hermesProxy.upgrade(req, socket, head);
      }
    });
    ```
- **CRITICAL PITFALL: The http-proxy-middleware 'ws: true' Global Upgrade Hijacking Trap**:
  - **Rule**: In Express/Node reverse proxies hosting multiple services or multiplexed WebSocket upstreams, NEVER set `ws: true` inside `createProxyMiddleware({...})` options. Always set `ws: false` on middleware configurations and delegate upgrades explicitly via `proxyInstance.upgrade(req, socket, head)` inside your multiplexed `server.on('upgrade')` handler.
  - **Mechanism**: When `ws: true` is configured in `createProxyMiddleware`, the first HTTP request that hits the middleware causes `http-proxy-middleware` to access `req.socket.server` and register its internal `this.handleUpgrade` listener globally on the `upgrade` event of the underlying `http.Server`. Because this internal listener executes without route prefix scoping, that single proxy hijacks EVERY incoming WebSocket upgrade across the entire application (e.g. a Socket.IO proxy rewriting `/hermes/api/pty` into `/socket.io/...` and routing to an Engine.IO port, returning `400 Transport unknown` or socket drops).
  - **Action**: Set `ws: false` on all `createProxyMiddleware` instances and manually dispatch inside `server.on('upgrade')`:
    ```javascript
    const socketIoProxy = createProxyMiddleware({ target: '...', ws: false, ... });
    server.on('upgrade', (req, socket, head) => {
      if (req.url && req.url.startsWith('/socket.io')) {
        return socketIoProxy.upgrade(req, socket, head);
      }
      // other explicit proxy handlers...
    });
    ```
- **CRITICAL PITFALL: Auth-Boundary WebSocket Whitelisting & The 5-Second Terminal Murder Trap**:
  - **Rule**: When wrapping a subpath-proxied SPA (such as Hermes Agent Dashboard under `/hermes`) behind an authentication boundary (`privacy-boundary.js`), whitelist the full spectrum of real-time WebSocket routes required by the client (`/api/pty` for xterm shells, `/api/ws` for client RPC, `/api/events` for telemetry, and single-use ticket parameters `?ticket=...`). Never attach background interval timers (`setInterval(..., 5000)`) calling `socket.destroy()` on upstream-authenticated terminal streams.
  - **Mechanism**: Modern developer SPAs split real-time concerns across multiple WebSocket endpoints: interactive terminal sessions run on `/api/pty`, whereas background status streams run on `/api/events`. If the privacy boundary only exempts native desktop clients (e.g. checking only `/api/ws` with custom subprotocol headers), web browser connections to `/api/pty` get rejected with HTTP 403 Forbidden, trapping the web UI in an infinite "Chat connection interrupted. Reconnecting..." loop. Furthermore, polling auth cookies every 5 seconds on active sockets drops terminal connections mid-keystroke if cookies are stripped by proxy hops.
  - **Action**: Recognize all app WebSocket routes under the mounted prefix (`prefix === '/hermes' && (p.startsWith('/hermes/api/') || ...)`), exempt them from aggressive portal cookie stripping, and let the upstream service's native ticket lifecycle manage socket authentication.
- **CRITICAL PITFALL: The WebSocket `RSV1 must be clear` Reverse-Proxy Compression Trap**:
  - **Rule**: Explicitly pass `perMessageDeflate: false` when initializing WebSocket servers (`new WebSocketServer({ server, perMessageDeflate: false })`) behind Node reverse proxies (`http-proxy-middleware`), Cloudflare Tunnels, or Nginx.
  - **Mechanism**: The `ws` library enables `perMessageDeflate` compression by default. When WebSocket frames pass through intermediate proxy layers that forward raw TCP frames without negotiating compression extensions symmetrically, the client browser or proxy parser receives unhandled compressed frames and immediately terminates the connection with `Invalid WebSocket frame: RSV1 must be clear` or socket hang up. Disabling perMessageDeflate eliminates RSV1 errors and drops framing overhead for high-frequency JSON ticks.
- **High-Frequency (100ms / 10Hz) Real-Time Market Streaming**:
  - Exchange candlestick / kline streams only update every 1–2 seconds. For true 100ms tick updates (10Hz), subscribe to top-of-book or aggregated trade streams (`bookTicker`, `aggTrade` like `btcusdt@bookTicker`, `xautusdt@bookTicker`), which emit at 10–50Hz (~10–80ms).
  - In the distribution engine, throttle per symbol to ~80–100ms to guarantee 10 updates per second without overflowing client WebSocket buffers.
  - On the frontend: Use in-place DOM mutation (`data-sym` attributes) to update price badges without rebuilding HTML lists, and decouple canvas drawing via `requestAnimationFrame` to maintain a buttery 60 FPS.
- **High-Frequency Real-Time Market Feeds & Forex/Gold Integration**:
  - When streaming live crypto assets (`BTC/USDT`, `ETH/USDT`, `SOL/USDT`), use Binance Spot combined WebSocket streams (`stream.binance.com:9443`).
  - When streaming commodities/forex like Gold (`XAU/USD`), Binance USD-M Futures (`fapi.binance.com/fapi/v1/klines?symbol=XAUUSDT` and `ticker/price?symbol=XAUUSDT`) provides real-time global gold index liquidity ($4,300+/oz).
  - Use a high-frequency (1s) ticker interval to ensure continuous tick-by-tick chart movement even when spot trade frequency is low.
- **High-Frequency (100ms / 10Hz) Telemetry Without Process Bloat**:
  - **Rule**: Never invoke sub-processes (`top`, `ps`, `vmstat`) inside high-frequency monitoring loops (e.g. 100ms / 10Hz).
  - **Mechanism**: Spawning child processes at 10Hz consumes 15-30% CPU and leaks memory over time.
  - **Action**: Read virtual kernel files directly in Python or Node (`/proc/stat` for CPU deltas, `/proc/meminfo` for RAM, `/proc/diskstats` for I/O, `/proc/net/dev` for network, and `os.statvfs('/')` for storage). Use a single shared background daemon loop with non-blocking subscriber queues (`queue.Queue`) so multiple browser tabs share a single `/proc` read cycle, keeping daemon footprint under 10MB RAM and 0.0% idle CPU.
- **Sandbox/Disposable Testing**: Use temporary, auto-generated tunnels (e.g., `cloudflared tunnel --url http://127.0.0.1:PORT` which generates `trycloudflare.com`). Tear down these temporary tunnels immediately after testing to save server memory.
- **CRITICAL PITFALL: The Localhost Iframe Trap**
  - **Rule**: NEVER set an iframe `src` to `http://127.0.0.1:PORT` or `http://localhost:PORT` when building a dashboard intended for remote access (e.g., via Cloudflare HTTPS).
  - **Mechanism**: The user's browser (e.g., on their phone) will attempt to resolve `127.0.0.1` on their *own device*, not the RDP server, resulting in a blank page or connection error. Additionally, HTTPS domains actively block HTTP iframes (Mixed Content).
  - **Action**: Always set up a backend proxy in the host app (e.g., `http-proxy-middleware` in Express) to route traffic internally, and point the frontend iframe to a relative proxy path.
- **CRITICAL PITFALL: Subpath SPA Proxying**
  - **Rule**: When embedding a built SPA under a subpath (e.g., `/hermes/`), proxy both the HTML and every root-relative asset/API/WebSocket route through the same subpath, and pass the app's prefix signal when it supports one (e.g., `X-Forwarded-Prefix: /hermes`).
  - **Mechanism**: Vite/Next dashboards often emit `/assets/...`, `/api/...`, `/login`, or `/dashboard`; if those stay rooted at the public domain, they collide with the host app or another embedded service, producing blank white pages or `Unexpected token '<'` when HTML 404/login pages are parsed as JSON.
  - **Action**: Verify from the public URL that bundle assets return JavaScript/CSS with `200`, API calls return JSON (not `<!DOCTYPE>`), redirects preserve the mounted path, and the rendered DOM contains expected app text before claiming success.
- **CRITICAL PITFALL: Express Proxy Mount Stripping on Static Asset Routes**:
  - **Rule**: When reverse-proxying static asset directories (e.g., `/fonts`, `/fonts-terminal`, `/dashboard-plugins`) to an upstream backend using `app.use('/prefix', createProxyMiddleware({ target: ... }))`, always restore the prefix via `pathRewrite: (path) => '/prefix' + path`.
  - **Mechanism**: Express `app.use('/prefix', ...)` strips the matched mount path from `req.url` before handing off to the middleware. The upstream server receives requests stripped of the directory name (e.g. `/font.woff2` instead of `/fonts/font.woff2`), triggering auth wall 302 redirects or 404s.
  - **Action**: Add explicit path preservation on all non-root static asset proxy mounts:
    ```javascript
    app.use('/fonts', createProxyMiddleware({
        target: 'http://127.0.0.1:PORT',
        changeOrigin: true,
        pathRewrite: (path) => '/fonts' + path
    }));
    ```
- **CRITICAL PITFALL: Express v5 / Path-to-RegExp Wildcard Proxy Crash (`Missing parameter name at index ...`)**:
  - **Rule**: In modern Express and `http-proxy-middleware`, NEVER write unparameterized wildcard route arrays like `app.use(['/kanvas', '/kanvas/*'], proxy)`.
  - **Mechanism**: Modern `path-to-regexp` treats bare `/*` as an invalid anonymous parameter without a capture name, throwing a fatal unhandled startup crash: `PathError: Missing parameter name at index ...`.
  - **Action**: Simply mount to the root prefix: `app.use('/kanvas', proxy)`. Express middleware mounting automatically catches `/kanvas` and all nested subpaths (`/kanvas/api`, `/kanvas/index.html`) without asterisks.
- **CRITICAL PITFALL: Hermes Cron Model Pinning Upstream Router Key Injection**:
  - **Rule**: When overriding or pinning an AI model on a Hermes cron job via CLI (`hermes cron edit <job_id> --model <model>`), ALWAYS explicitly include the provider key (`--provider <custom_provider_key>`, e.g., `--provider custom:lk`).
  - **Mechanism**: If `--provider` is omitted, Hermes defaults to the unauthenticated bare `custom` provider which injects `"no-key-required"` as the API key. Upstream routers (e.g. 9Router on port 20128) reject this with HTTP 401 (`Invalid API key`), silently activating Hermes's `fallback_providers` and executing a different model than the one selected.
  - **Action**: Always execute `hermes cron edit <id> --model "<model>" --provider "custom:lk"`. When clearing back to system default, pass empty strings to both: `--model "" --provider ""`.
- **CRITICAL PITFALL: Multi-Service Cloudflare Ingress Port Identification**:
  - **Rule**: When exposing a new sub-service route (e.g., `/organisasi`), NEVER assume which internal port the public domain/Cloudflare tunnel routes to. Test public ingress directly via `curl -s -i https://domain/subpath` before adding reverse proxy configurations to sibling apps.
  - **Mechanism**: On multi-service VPS environments where multiple node/python servers run concurrently (e.g. port 3000 `jajandigital` vs port 3050 `penelitian-ai`), the Cloudflare tunnel maps the root hostname (`jajandigital.web.id`) to one specific upstream port (3050). Adding reverse proxy rules only on the sibling service (3000) leaves public requests intercepted by the actual ingress server's security boundaries (e.g., `privacy-boundary.js` returning HTTP 401).
  - **Action**: Always inspect incoming response headers (`Server`, `ETag`, error signatures) using `curl -s -i https://domain/subpath` to trace the real entry port, whitelist the new route in the true ingress gateway's privacy boundaries, and configure the proxy there.
- **CRITICAL PITFALL: Socket.IO Engine Mount Path Stripping in Express Proxies**:
  - **Rule**: When reverse proxying Socket.IO endpoints through Express using `app.use('/socket.io', createProxyMiddleware({ target: ... }))`, always supply `pathRewrite: (p) => '/socket.io' + (p.startsWith('/') ? p : '/' + p)`.
  - **Mechanism**: Express `app.use('/socket.io', ...)` strips `/socket.io` from `req.url` before invoking the middleware. An incoming engine handshake (`/socket.io/?EIO=4&transport=polling`) gets forwarded to the upstream target as `/?EIO=4`. If the upstream server serves a Single Page App (`index.html`) on root `/`, it returns HTML text instead of the Engine.IO JSON handshake (`0{"sid":...}`), causing the browser client to fail with `parser error` or disconnect immediately.
  - **Action**: Preserve the `/socket.io` prefix explicitly via `pathRewrite`, enable `ws: true`, and delegate WebSocket upgrade events via `socketProxy.upgrade(req, socket, head)` in `server.on('upgrade', ...)`.
- **High-Density Real-Time Telemetry & Host RAM Allocation Guardrails**:
  - **Rule**: For multi-agent / multi-model architectures operating under a dedicated RAM ceiling (e.g. 9.0 GB limit on a 15 GB host), implement duplex real-time streaming (Socket.IO `telemetry_tick`) reading system memory directly (`/proc/meminfo` or `free -b`) without polling overhead.
  - **Mechanism**: Periodic HTTP client polling (e.g. `setInterval(fetch, 2000)`) introduces UI flicker, request queuing, and delayed alerts. Push-based duplex WebSockets allow 1000ms heartbeat telemetry updates with <10ms UI sync and <15MB daemon RAM footprint.
  - **Action**: Expose visual progress gauges showing real-time GB vs the allocated ceiling, with live capacity headroom and warning indicators when thresholds (e.g., 85% of limit) are approached.
- **Live Autonomous Agent Execution Inspector & Dynamic SVG Relational Tree Pattern**:
  - **Rule**: When building organizational or multi-agent command dashboards where stakeholders must observe backend execution live, never rely on simulated progress bars or manual page refreshes. Connect directly to the agent's persistent internal state database (`~/.hermes/state.db`) and stream active execution paths over duplex WebSockets.
  - **Mechanism**:
    1. *Realtime State Inspection via Read-Only SQLite*: Open `~/.hermes/state.db` using `better-sqlite3` in read-only mode (`readonly: true`). Perform synchronous queries (<0.1ms overhead) on the `messages` table:
       - If latest record has `role: 'user'`: Status is `WORKING` (Reasoning & Strategy Planning).
       - If latest record has `role: 'assistant'` with `tool_calls`: Check if a subsequent `role: 'tool'` row exists with an ID greater than the assistant message ID. If not found, that exact tool is currently `RUNNING` at this millisecond. Map tool signatures directly to organizational departments: `patch`/`write_file`/`terminal` -> Field Technical Execution; `read_file`/`search_files`/`web_search` -> Research & Investigation; `vision_analyze`/`qc` -> Quality Gatekeeper.
       - If latest record has `role: 'assistant'` without `tool_calls`: Turn is complete; all agents transition immediately to `STANDBY (IDLE)`.
    2. *Dynamic SVG Relational Tree Connector Layer*: Place an absolute `<svg>` overlay behind the hierarchy cards. Calculate responsive anchor coordinates (center-bottom of parent to center-top of child) and draw smooth cubic bezier curves (`M x1 y1 C x1 y1+dy, x2 y2-dy, x2 y2`).
       - On active branches in `active_relation_path`: Toggle `.active-flow` with keyframed traveling energy pulses:
         `stroke-dasharray: 10 6; animation: energyPulse 0.8s linear infinite; filter: drop-shadow(0 0 6px var(--accent-glow));`
       - Idle paths remain calm subtle dashed lines (`#cbd5e1`, `stroke-dasharray: 6 6`), providing instantaneous visual clarity on who is working and who is idle.
    3. *Real-Time Mutation & Operations Inspector Table*: Stream the latest 15-20 backend actions over Socket.IO displaying operation type (`PATCH_FILE`, `WRITE_FILE`, `SHELL_EXEC`, `DATA_QUERY`), full target file paths or commands, executing sub-agent, and status (`RUNNING` pulsing badge vs `DONE`), giving complete backend transparency.
- **Hermes Web Dashboard 24/7 Systemd Supervision**:
  - Supervise the dashboard via a systemd user unit (`~/.config/systemd/user/hermes-dashboard.service`) rather than ad-hoc shell sessions that drop on disconnect:
    `ExecStart=<venv>/bin/python -m hermes_cli.main dashboard --no-open --port 9119 --host 127.0.0.1 --skip-build`
  - Enable and start with `systemctl --user enable --now hermes-dashboard.service` (`Restart=always`).
- **CRITICAL PITFALL: Hermes Multi-Profile Dashboard Auth Isolation**:
  - **Rule**: When accessing the Hermes Web Dashboard (`/hermes` -> `:9119`), credentials (`basic_auth.username` and `password_hash`) are strictly bound to the specific profile directory (`HERMES_HOME`) that launched the dashboard process (default `~/.hermes/config.yaml`), NOT the active CLI profile or secondary profiles under `~/.hermes/profiles/<name>/`.
  - **Mechanism**: Profiles in Hermes are independent islands. Switching profiles in CLI or setting passwords in secondary profiles (e.g. `ksatest`, `bikagent`) does not alter the credentials of the running dashboard process. Submitting credentials from a secondary profile against the default dashboard instance triggers 401 Unauthorized (`Invalid username or password`).
  - **Action**: Verify which profile daemon is running on port 9119 (`cat /proc/<pid>/environ | grep HERMES_HOME`). Update credentials in that specific profile's `config.yaml` or run `hermes [-p <profile>] dashboard setup`, then restart the dashboard service.
- **CRITICAL PITFALL: Subpath Proxy Post-Login Target Resolution (`X-Forwarded-Prefix`)**:
  - **Rule**: When authenticating users in an application hosted behind a reverse-proxy subpath (e.g. `X-Forwarded-Prefix: /hermes`), ensure the backend auth completion handler prepends the prefix to the post-login destination URL when the validated target is `/` or lacks the prefix.
  - **Mechanism**: The auth form POST response returns `{"ok": true, "next": target}`. If `target` is resolved as root `"/"`, the browser's `window.location.assign(data.next || '/')` will navigate to the root domain (`https://example.com/`), throwing the user completely out of the proxied dashboard into whatever is hosted at the root path.
  - **Action**: In the auth completion route, inspect the forwarded prefix and attach it to the target:
    ```python
    target = _validate_post_login_target(next_raw) or "/"
    prefix = prefix_from_request(request)
    if prefix and not target.startswith(prefix):
        target = f"{prefix}{target}" if target.startswith("/") else f"{prefix}/{target}"
    ```
- **CRITICAL PITFALL: Do Not Force WebSocket-Heavy Admin Apps Through a Shared Subpath**
  - **Rule**: Put WebSocket-heavy tools such as Hermes Dashboard Chat on a dedicated hostname/tunnel (for example `hermes.example.com -> http://127.0.0.1:9119`) instead of iframe/subpath embedding under a host already serving another admin app.
  - **Mechanism**: Terminal/chat UIs use WebSocket upgrades plus strict Host/Origin guards; subpath reverse-proxy chains (`/hermes/api/pty`, `/api/events`) commonly fail with `origin_mismatch`, `code 1006`, or route collisions even when ordinary HTTP menu pages work.
  - **Action**: Use the Koper/dashboard as a launcher tile for the dedicated app, not as the WebSocket transport. Verify the dedicated hostname by loading `/chat` from the public URL, confirming the DOM shows the chat terminal, and checking logs for no `origin_mismatch` before reporting it ready.
