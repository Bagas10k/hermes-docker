---
name: private-saas-architecture
description: Use for building modular private SaaS and admin dashboards.
version: 1.0.0
---

# Private SaaS Architecture

Use this skill when building or extending internal dashboards, modular "command centers", or private SaaS tools (e.g., the "Koper Kerja Digital" concept).

## 1. Modular "Briefcase" Philosophy (Koper Kerja Digital)
- **Compartments (Sekat-sekat)**: Treat the dashboard as a physical briefcase with strict modular compartments. Examples include:
  1. **Hermes Chat Terminal**: The core brain (Hermes Gateway / `9router` API on port 20128).
  2. **Radar Controller**: The specific automation engine (e.g., SputarAI on port 3050).
  3. **DevOps & Server Monitor**: For PM2 and system telemetry (see `references/pm2-integration.md` for API implementation).
  4. **Vault & Code Editor**: For remote file/script management.
- **Do Not Reinvent the Wheel (Integration over Recreation)**: If a target service (like 9Router or Hermes Gateway) already has a mature, open-source Web UI running on its port, **do not build custom HTML/CSS mockups from scratch**. Embed the existing UI directly via a backend proxy and iframe to save time and preserve full native functionality.
- **Extensibility**: The dashboard MUST allow dynamic customization (adding/removing compartments or dragging them to reorder) without hardcoding.
- **Separation of Concerns**: Isolate standalone business applications (e.g., consumer-facing apps like "Dasbor Jajan Digital") from this administrative briefcase to prevent traffic interference. Do not integrate high-traffic consumer projects into the private command center.
- **Terminology Pitfall**: Distinguish between the AI API provider/model (e.g., `9router` / `Hermes Gateway` running on port 20128) and the actual automation projects (e.g., `SputarAI` running on port 3050). Do not use the API provider's name to refer to the automation project.

## 2. Network Infrastructure, Proxies & Tunnels
- **Production/Permanent Tools**: Must run over a secure, dedicated domain via **Cloudflare Zero Trust** (Argo Tunnel, e.g., using a registered token). Do not expose RDP ports directly to the public internet.
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

## 3. UI/UX Mindset ("Bagus" standard)
Interfaces must be functional, data-dense, and zero-slop:
- **Theme**: "Linear/Obsidian" style. Warm Paper (`#FAF6EF` / `#F7F5F0`) and Warm Obsidian black (`#14120E` & `#221E19`) with precise accent colors (`#D97706` amber, `#10B981` emerald).
- **Dasbor vs Halaman Artikel (Bento Workspace Invariant)**: Jangan pernah mereduksi permintaan dasbor menjadi landing page dokumen/artikel teks panjang statis. Pengguna menuntut arsitektur **Dasbor/Workspace interaktif nyata** (Top App-Bar, Omnibar `⌘K`, kartu telemetri operasional 2x2, serta Bento Grid modular berdensitas tinggi). Format dokumen statis dinilai 1/10.
- **CRITICAL PITFALL: The True App-Shell vs Double Navigation Trap**:
  - **Rule**: Never construct a dashboard layout with double navigation (e.g., a top horizontal marketing/landing navbar AND a left app sidebar). A genuine application dashboard uses a **Single Unified Persistent Left Sidebar (100vh)** and a compact **Contextual Action Bar** (~50–56px) for breadcrumbs and global actions. (See `references/app-shell-hierarchy.md` for layout blueprints, vertical allocation formulas, and Anchor Metric rules).
  - **Mechanism**: Placing a public landing navbar above an app sidebar wastes critical vertical viewport space (~60–80px), forces an awkward internal micro-scroll, and dilutes the visual hierarchy between application tools and public marketing.
  - **Action**: Lock the desktop viewport to 100vh (`height: 100vh; overflow: hidden;`). Anchor the left sidebar from top to bottom edge, and constrain top KPI metric tiles to <=25% viewport height (~125–140px) so the operational data workspace (ledger/tables) can render 7–10 full rows without micro-scroll clipping.
- **CRITICAL PITFALL: Holistic Revision Ripple-Effect (Anti-Narrow Patching)**:
  - **Rule**: When executing a structural layout revision (e.g. adding a 240px sidebar, altering grid columns), NEVER patch only the requested container in isolation. Re-calculate the ripple effect on child container aspect ratios, metric-to-table vertical space allocation, and typography scale across the remaining workspace.
  - **Mechanism**: Narrowing workspace width from 1440px to 1200px squashes child cards and expands their vertical height. If top metric tiles are not redesigned into compact KPI boxes, they consume >50% of the screen height, choking operational data tables beneath them to only 3-4 visible rows.
  - **Action**: Re-proportion top KPI cards to compact dimensions, establish an unambiguous Anchor Metric (`24-26px tabular-nums`) as the visual North Star, and allocate >=60% of the vertical canvas to high-utility operational data.
- **Akses Langsung Layanan Tersemat (9Router / Console)**: Ketika menyematkan layanan internal (seperti 9Router atau console API) ke menu dasbor publik:
  - Sediakan dua lapis akses: modal telemetri ringan tanpa login untuk publik/inspeksi cepat (`/api/9router/models`), dan tombol aksi langsung menuju Web Console UI (`/login` -> `/dashboard`).
  - Jangan membiarkan pengguna mengira harus membuka terminal/SSH untuk mengakses panel yang sudah berjalan lokal di server; jelaskan bahwa rutenya sudah diproxy balik via port web publik.
- **CRITICAL PITFALL: 9Router Remote Default Password Lock**:
  - **Rule**: Jangan biarkan password 9Router bernilai default (`123456`) saat diakses lewat domain/tunnel publik. Sistem Next.js 9Router akan otomatis memblokir login remote dengan pesan: *"Default password must be changed before remote access. Change it from the local machine (or set INITIAL_PASSWORD)"*.
  - **Action**: Segera hash password baru via bcrypt (`bcrypt.hashpw(b'...', bcrypt.gensalt(10))`) dan perbarui kolom `data` pada tabel `settings` di `~/.9router/db/data.sqlite` sebelum memberikan URL console ke pengguna.
- **CRITICAL PITFALL: Schema Mismatch pada Halaman Combos 9Router**:
  - **Rule**: Pada tabel `combos` di `~/.9router/db/data.sqlite`, kolom `models` WAJIB berupa JSON array of strings (`["ag/model-id", "cx/model-id"]`), BUKAN array of objects (`[{"provider":"ag","model":...}]`).
  - **Mechanism**: Komponen React Next.js pada halaman `/dashboard/combos` (`combo.models.map(...)`) me-render model secara langsung sebagai React Node. Jika tipenya objek, React melempar uncaught invariant error yang memicu error boundary: *"This page couldn’t load"*.
  - **Action**: Jika halaman combos gagal memuat (*crash*), periksa database SQLite dan normalisasi array objek menjadi string ID murni.
- **No Emojis in UI/UX**: Strictly avoid emojis in UI buttons, headings, badges, and forms. Use clean monochromatic SVG icons (e.g. Lucide Icons) with refined stroke widths (1.5–2px).
- **Anti-AI-Slop & Simplicity Rule**: Avoid bloated marketing cards, neon icon boxes, decorative colored containers, or kicker badges. A real developer workspace must be quiet, restrained, and high-density (centered `max-w-6xl` or `max-w-3xl`, direct headlines, 1-line plain descriptions).
- **Prinsip Desain Super Simple & Hirarki Penempatan Efektif (Anti-Slop)**:
  - Sederhana bukan berarti memotong fitur, melainkan **membuang elemen yang tidak dibutuhkan** (menghapus dekorasi berlebihan, modal berlapis yang tidak perlu, dan menu tersembunyi).
  - Terapkan 4 tingkat hierarki penempatan UI/UX ergonomis:
    1. *Tingkat 1 — Bilah Kendali Utama (Top Bar)*: Identitas brand, pencarian instan global (*live search* saat mengetik), dan tombol aksi primer (*Primary CTA*).
    2. *Tingkat 2 — Bilah Konteks (Context Bar)*: *Breadcrumb trail* satu klik untuk navigasi lokasi, chip filter kategori horizontal, dan saklar layout (Grid vs Ledger Table).
    3. *Tingkat 3 — Kanvas Kerja Langsung (Direct Manipulation Canvas)*: Menampilkan entitas utama (Folder di atas, Berkas di bawah) dengan area *drop zone* drag-and-drop di seluruh kanvas, serta tombol menu aksi 3-titik (*kebab*) di sudut setiap kartu.
    4. *Tingkat 4 — Panel Inspektur Samping (Slide-Out Inspector)*: Menampilkan pratinjau media, metadata, dan aksi lanjutan di panel samping tanpa menutupi layar utama.
  - **Palet Warna Cerah, Hidup, & Terkalibrasi (Cerah & Colorful)**: Gunakan kanvas latar belakang terang yang bersih (`#f8fafc` / `#ffffff`) dipadukan dengan aksen warna semantik yang kontras dan harmonis (Merah mawar untuk dokumen/DOC, Ungu untuk gambar/IMG, Biru untuk kode/DEV, Kuning amber/hijau untuk folder), serta **mutlak 0% emoji** (gunakan ikon garis SVG murni).
- **Deployment Maturity Segregation**: Always segregate projects cleanly into distinct tiers:
  1. **Produksi & Publikasi (Live)**: Customer-facing apps and published media with live endpoints.
  2. **Internal & Uji Coba (Lab)**: System daemons, schedulers, and active cognitive research labs.
  3. **Layanan Terpisah (Standalone)**: Projects executed on separate hosts/instances; do not run duplicate processes or proxy to non-existent local ports.
- **Micro-Status Indicators**: Use tiny 6px status dots paired with clean mono text (`Live`, `Internal`, `Uji Coba`, `Mandiri`), never cluttered multi-badge ribbons.
- **Responsiveness**: Use an Adaptive Liquid Interface. Desktop gets a Dual-Sidebar; mobile gets a bottom tab-bar (like native apps).
- **Dual-Editor Focus (Split-Screen) & Mobile Adaptive Single-View Switcher**:
  - **Rule**: In dense technical workspaces (e.g., Markdown Editor + AI Co-Pilot / PRD Architect), NEVER retain a multi-column flex layout (`flex-direction: row`) on mobile viewports (`<= 768px`).
  - **Mechanism**: Dividing narrow phone screens (360px–412px) across 2 or 3 columns crushes text inputs to ~180px, breaks word wrapping, and pushes sidebars/AI panels completely off-screen.
  - **Action**: Implement an adaptive Liquid interface:
    1. *Desktop*: 3-column split view with draggable resizers and a dedicated **[ZEN FOCUS]** mode toggle (hiding sidebars and centering the editor at max-width ~900px for distraction-free writing).
    2. *Mobile (`<= 768px`)*: Enforce a clean segmented navigation tab bar (`[CATATAN]`, `[EDITOR]`, `[SCRATCHPAD]`, `[AI ARCHITECT]`) where each view renders at 100% full viewport width with zero horizontal scroll.
    3. *CSS Flexbox Input Shrink Trap*: Any text `<input>` placed inside a flex row (`display: flex`) alongside buttons MUST specify `min-width: 0; width: 100%;` alongside `flex: 1`. Without `min-width: 0`, the CSS default `min-width: auto` prevents the input from shrinking below its text content, truncating or displacing adjacent action buttons (e.g. `[HAPUS]`).
- **Mobile Responsive Trading Terminal Architecture**:
  - On screens `<= 900px` (tablets and phones), replace rigid 3-column desktop grids with a native-feeling 5-tab bottom navigation bar (`[CHART]`, `[WATCHLIST]`, `[AI & ORDER]`, `[POSISI]`, `[JURNAL]`).
  - Mobile touch drag on HTML5 Canvas charts: intercept `touchstart`, `touchmove`, `touchend`, `touchcancel` with `e.preventDefault()` to move the crosshair smoothly without triggering browser page scrolling or unwanted zooming.
  - Fluid canvas resizing: attach `ResizeObserver` on the chart container and listen for `resize` / `orientationchange` so DPR and canvas dimensions adjust instantly when switching between portrait and landscape.
- **Zero-Delay High-Frequency Canvas Chart Rendering**:
  - When handling 7-10 market ticks per second via WebSocket, decouple tick ingestion from canvas drawing using a dirty-flag `requestAnimationFrame` loop (`requestChartRender()`). Direct synchronous `renderChart()` on every tick causes stutter, dropped frames, and input lag on mobile devices.
- **Micro-Scalping (1m - 5m) Execution Rules**:
  - When user requests fast / short-range trading (1-5 minutes):
    - Set primary trigger to `1m` with `5m` macro trend confirmation.
    - Calibrate Stop Loss tightly to 1.0x ATR (~0.3% - 0.5%) and Take Profit to 1.8x ATR.
    - Implement an automated dynamic trailing stop (e.g. activate breakeven at +0.2% profit, then trail 0.75x risk distance) to lock in quick scalping profits before momentum fades.
    - Accelerate market scanning cycle to 3 seconds.
- **Components**:
  - **Command Palette (Omnibar / ⌘K)** for global actions.
  - **DataGrids** with pure SVG badges (no neon glows).
  - **Smooth Telemetry Charts** (e.g., Chart.js with dark mode compliance).
- **Loading States**: Prevent the "broken button illusion" with real-time skeletal loaders and streaming progress text (Server-Sent Events or Socket.IO).
- **High-Density Terminal Cockpit Architecture (1-Screen Full Viewport Rule)**:
  - **Rule**: When building an administrative observability radar, AI agent cockpit, or developer monitoring console, DO NOT use airy SaaS marketing layouts with giant banner headers, decorative slogans, or tall cards that force page scrolling.
  - **Form Factor**: Construct a **1-Screen Full Viewport (100vh) Terminal TUI (Text User Interface)**:
    - *Single Viewport Invariant*: 100% viewport height (`height: 100vh; overflow: hidden;`), zero body scrollbar on desktop displays.
    - *Centerpiece Hierarchy (The Process Workflow / DAG is King)*: The active process workflow, DAG execution nodes, and subagent concurrency branch MUST be the absolute central, largest element on the screen (taking ~60-65% width/center).
    - *Ancillary Compaction*: Information like Scheduled Cron Daemons, Supervisor Sentinels, Tool Telemetry, and Live Event Stream must be compactly docked into side rails or lower docking tiers, NEVER displacing or shrinking the core workflow process graph.
    - *Typography & Aesthetics*: Pure monospace (`JetBrains Mono`), dense 10-11px sizing, hairline 1px borders (`#1B2438`), dark slate palette (`#03060E` canvas, `#070B16` surface), and 0% emoji.
- **Interactive Realtime Cabinet Chat & Command Drawer Pattern (Dual-Surface Realtime Architecture)**:
  - **Rule**: When adding an interactive operator/owner chat channel into high-density TUI cockpits (such as RADAR):
    - *Dual Surface UX*: Provide BOTH an in-place docked tab inside the Console/Workspace panel (e.g. Panel [06]) for persistent glanceability alongside stdout streams, AND a dedicated full-screen modal/drawer (e.g. Hotkey `F6`) with auto-focused input for deep conversational interaction without disrupting background telemetry monitoring.
    - *Realtime Duplex with Fallback & State Persistence*: Decouple message submission into Socket.IO duplex event emission (`cabinet_chat_send` -> `cabinet_chat_new_message`) with automatic fallback to REST POST (`/api/radar/chat/messages`) if socket disconnects. Back messages with an append-only SQLite store (`cabinet_chat_messages`) so chat history survives page refreshes and server reboots.
    - *Intelligent Auto-Responding Agent Personas (Kabinet Musyawarah)*: Programmatically route owner messages to the appropriate autonomous agent persona (General Manager for broad coordination, Si Pengawas for QC/data validation, Si Eksekutor for VPS/RAM/infrastructure, Si Pintar for research/architecture) with a slight asynchronous delay (500–750ms) to simulate real deliberative reflection rather than robotic echo.
    - *Zero Emoji Invariant*: In terminal/cockpit aesthetic, preserve the Swiss Editorial monospace style: format each agent bubble with distinct left border accent colors (`--bubble-color`), monospace role badges (`[OWNER]`, `[GM]`, `[SI PENGAWAS]`), and pure text without graphic emojis.
    - *Multi-Input Synchronization*: When rendering both a docked input bar and a modal input bar, ensure event handlers target the active element cleanly without selector collision or double submission.
- **Multi-Entity Tree / Catalog Propagation**: When providing clone/duplication for nested tree structures (e.g., Menu Trees, interactive flow nodes, or category catalogs) across groups or tenants:
  - Add a dedicated action button in the visual editor toolbar right beside group selection and save controls.
  - Open a modal showing source statistics (source group ID, total node count) and a scrollable target checklist supporting 1-to-many propagation with "Pilih Semua / Batal Semua".
  - Provide an option to include accompanying template elements (e.g. category & content footers).
  - Perform deep cloning on the backend (`JSON.parse(JSON.stringify(tree))`), emit socket update events for each target, and verify the clone in the database (matching child node counts) before declaring completion.

## 4. Backend & Security
- **Self-Hosted BaaS (Supabase on Docker) & RAM Ceiling Management**:
  - When self-hosting a full BaaS stack (Supabase Docker Compose: PostgreSQL 15, PostgREST, GoTrue Auth, Studio UI, Envoy, Supavisor, Storage) on a memory-constrained host (e.g. 9.0 GB ceiling on a 15 GB VPS):
    - Run official Supabase Docker Compose (`/home/ubuntu/supabase`) with `API_GW_HTTP_PORT=8000` and `POSTGRES_PORT=5432`.
    - Baseline memory footprint for all 11 healthy containers is ~1.0–1.3 GB RAM. Always audit host RAM (`free -m`) before and after stack startup.
  - **Single-Domain Shared-Host BaaS Deployment ("Setelah /" Pattern)**:
    - **Rule**: When the user explicitly requires hosting a full BaaS (Supabase) under the existing primary domain without provisioning a dedicated subdomain ("diisi setelah /", e.g. `domain.com/supabase`), implement a hybrid root-redirect and predicate reverse-proxy architecture instead of attempting to rewrite Next.js internal subpaths.
    - **Architecture & Invariants**:
      1. *Entry Point & Client Router Compatibility*: Supabase Studio Next.js is precompiled with `basePath: ""` and serves `X-Frame-Options: DENY` (forbidding iframes). Route `GET /supabase` with HTTP 302 redirecting to `/project/default`. This preserves Next.js client-side routing without 404 router mismatch.
      2. *CRITICAL PITFALL: The Express Proxy Mount Stripping & Route Predicate Trap*:
         - **Rule**: Never mount Supabase proxy via `app.use(['/project', ...], proxy)`. Always mount via a root-level middleware with an exhaustive path predicate (`isSupabaseRoute`).
         - **Mechanism**: Express `app.use('/prefix', ...)` strips `/prefix` from `req.url`, so Envoy receives `/default` instead of `/project/default` (Next.js 404) and `/health` instead of `/auth/v1/health` (GoTrue 401). Furthermore, Supabase Studio issues internal API calls (`/api/v1/projects/.../api-keys`, `/api/enabled-features-overrides`, `/api/cli-release-version`, `/api/get-deployment-commit`) and asset requests (`/img/*`) that get intercepted by host application privacy/auth middleware if the predicate is incomplete, causing HTTP 401 and UI crashes.
         - **Action**: Use an exhaustive regex covering all Studio routes, Next.js assets, and BaaS endpoints:
           ```javascript
           const isStudioRoute = (p) => /^\/(?:project|pg|_next|img|monaco-editor|favicon|deno)(?:\/.*)?$/.test(p) ||
                                       /^\/api\/(?:v1\/projects|platform|projects|profile|constants|ai|props|edge-functions|content|enabled-features-overrides|cli-release-version|get-deployment-commit|get-ip-address|get-s3-keys|get-utc-time|connect|check-cname|parse-query|generate-attachment-url|mcp|status-override)(?:\/.*)?$/.test(p) ||
                                       p === '/supabase-logo.svg';
           const isSupabaseRoute = (p) => isStudioRoute(p) || /^\/(?:rest\/v1|auth\/v1|storage\/v1|realtime\/v1)(?:\/.*)?$/.test(p);
           app.use((req, res, next) => {
               if (isSupabaseRoute(req.path)) return supabaseProxy(req, res, next);
               next();
           });
           ```
      3. *CRITICAL PITFALL: Mobile Browser Sub-Resource Script 401 & Auto-Auth Injection*:
         - **Rule**: When reverse proxying Supabase Studio behind a Basic-Auth protected upstream (Envoy), configure the proxy to auto-inject the upstream Basic Auth header (`proxyReq.setHeader('authorization', SUPABASE_AUTH_HEADER)`) for all internal Studio and asset routes.
         - **Mechanism**: Mobile browsers (Android WebKit, VivoBrowser, iOS Safari) do NOT automatically send HTTP Basic Auth credentials on sub-resource script tags (`<script src="/_next/static/chunks/...">`) even after the user enters credentials for `/project/default`. Envoy responds with HTTP 401 to all JavaScript chunks, causing a blank white screen or React hydration crash.
         - **Action**: Inject the header upstream in `createProxyMiddleware`'s `on.proxyReq` hook exclusively for `isStudioRoute`, preserving client-provided tokens on external `/rest/v1` and `/auth/v1` routes:
           ```javascript
           const SUPABASE_AUTH_HEADER = 'Basic ' + Buffer.from('supabase:PASSWORD').toString('base64');
           const supabaseProxy = createProxyMiddleware({
               target: 'http://127.0.0.1:8000',
               changeOrigin: true,
               on: {
                   proxyReq: (proxyReq, req) => {
                       if (isStudioRoute(req.path) && !req.headers['authorization']) {
                           proxyReq.setHeader('authorization', SUPABASE_AUTH_HEADER);
                       }
                   }
               }
           });
           ```
      4. *Headless Browser Automated E2E Verification*:
         - **Rule**: Never certify a subpath-proxied Next.js dashboard as working using simple `curl -sI` of the HTML root alone.
         - **Mechanism**: `curl` verifies only the initial HTML response; it cannot detect missing script bundles, broken CORS, unproxied internal Next.js API routes, or console errors that manifest during client-side hydration.
         - **Action**: Run a quick Puppeteer script in headless mode to load the URL, monitor `page.on('response')` for `status >= 400`, capture `console.error` and `pageerror`, and verify sub-views (Table Editor, SQL Editor, Auth Users) load with 0 errors before reporting completion to the user.
      5. *CRITICAL PITFALL: Body-Parser Payload Consuming & Route Collision*:
         - Mount `supabaseProxy` strictly BEFORE `express.json({ limit: ... })` or any body parser. Placing body parsers before proxies consumes the request stream, causing POST/PUT mutations and multipart file uploads to hang indefinitely.
         - Mount `/auth/v1` before any generic `/auth` proxy (such as Hermes dashboard) to prevent auth requests from being swallowed by sibling tools.
      6. *BaaS Security Boundary & CSRF Exemption*:
         - Application boundary middleware enforcing browser same-origin checks on mutations (POST/PUT/PATCH/DELETE) must explicitly exempt `/rest/v1`, `/auth/v1`, and `/storage/v1` so external API clients and scripts passing `apikey` or `Bearer` tokens are not rejected with HTTP 403.
      7. *Public Environment Synchronization*:
         - Set `SUPABASE_PUBLIC_URL=https://domain.com` and `API_EXTERNAL_URL=https://domain.com/auth/v1` in `/home/ubuntu/supabase/.env` so generated storage download links and auth callbacks resolve cleanly through the public reverse proxy.
      8. *CRITICAL PITFALL: Mobile Browser 401 Sub-Resource Cache & The "Plank Putih" (Blank Screen) Trap*:
         - **Rule**: When resolving 401 auth issues on subpath-proxied Next.js SPAs, always advise users to test in Incognito or an external browser, because mobile web engines cache failed 401 sub-resource chunks persistently.
         - **Mechanism**: In Client-Side Rendered (CSR) Next.js apps, `<div id="__next">` starts empty. If sub-resource script chunks (`/_next/static/chunks/`) initially failed with HTTP 401, mobile browsers (Android WebKit, VivoBrowser, iOS Safari, Telegram/WhatsApp in-app webviews) cache the 401 response. When the user refreshes, the browser re-fetches the HTML (200 OK) but serves the scripts from disk cache as 401, preventing React hydration and leaving the screen completely blank white ("plank putih").
         - **Action**: In addition to configuring proxy auto-auth injection, verify mobile rendering via Puppeteer mobile emulation (`isMobile: true`, mobile User-Agent) and capture screenshot evidence. If the user reports a blank white screen after a fix, instruct them to open the link in an Incognito tab or clear site cache.
  - **Self-Hosted Cloud Storage & Drive Architecture Pattern (Supabase BaaS Foundation)**:
    - When building a private cloud storage service (e.g. Google Drive alternative) on self-hosted Supabase:
      * **Upload Engine**: Use `@uppy/core` with `@uppy/tus` against Supabase Storage's TUS resumable endpoint (`/storage/v1/upload/resumable`) for network-interruption-tolerant multi-gigabyte uploads.
      * **Disk Deduplication (SHA-256)**: Compute the SHA-256 hash client-side before upload; query the `files` metadata table for an existing matching hash. If present, create a new metadata pointer without storing a duplicate physical file, saving VPS disk space.
      * **In-Browser Streaming**: Supabase Storage supports HTTP 206 Partial Content (Range requests) natively, allowing instant video/audio seeking without full file pre-downloads.
      * **Semantic Search & OCR Indexing**: Store chunked embeddings in a `file_embeddings` table using the `VECTOR(1536)` type with HNSW index for high-speed sub-10ms semantic document queries.
    - **CRITICAL PITFALL: CDN Global Script Identifier Shadowing (`SyntaxError: Identifier 'supabase' has already been declared`)**:
      * **Rule**: When integrating `@supabase/supabase-js` via CDN (`<script src=".../supabase-js@2"></script>`), NEVER declare `const supabase = ...` in the global script scope.
      * **Mechanism**: The CDN UMD bundle exposes `window.supabase` as a global variable. Declaring `const supabase = ...` in the top-level script scope triggers an uncatchable `SyntaxError: Identifier 'supabase' has already been declared` during script parsing, halting all JavaScript execution before any function runs.
      * **Action**: Name the client instance `sbClient` or `supabaseClient`:
        ```javascript
        const sbClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
        ```
  - **CRITICAL PITFALL: Supabase Envoy Gateway `/rest/v1/` Root RBAC Denial**:
    - **Rule**: Never use `GET /rest/v1/` to test `ANON_KEY` connectivity. Test with `GET /auth/v1/health` or `GET /rest/v1/<table_name>`.
    - **Mechanism**: The default Supabase Envoy configuration maps the exact root path `/rest/v1/` to `rest-v1-openapi-protected`, which strictly allows ONLY `admin` principals (`SERVICE_ROLE_KEY`). Making a request to `GET /rest/v1/` with an `ANON_KEY` returns `403 RBAC: access denied`, creating a false impression that PostgREST or the anon key is broken. Subpaths matching `/rest/v1/*` (table endpoints) route to `rest-v1-protected` and successfully authenticate with `ANON_KEY`.
  - **CRITICAL PITFALL: Supabase Studio Subpath URL Rewriting & Iframe Embedding**:
    - **Rule**: Never attempt to rewrite Supabase Studio URLs to force client pages under an arbitrary nested subpath prefix (e.g. attempting to rewrite `/project` into `/supabase/project` inside Next.js chunks) and never embed Studio in an `<iframe>`.
    - **Mechanism**: Supabase Studio is a standalone Next.js application precompiled with `basePath: ""` and serves strict headers `X-Frame-Options: DENY` and `Content-Security-Policy: frame-ancestors 'none'`. Client-side Next.js chunk navigation will break if internal route paths are rewritten or iframe-embedded. If a dedicated subdomain (`supabase.domain.com`) is not used, follow the *Single-Domain Shared-Host BaaS Deployment* pattern above: preserve native paths (`/project`, `/_next`, `/pg`, `/api`) via root predicate proxying and provide an entry redirect from `/supabase` to `/project/default`.
  - **CRITICAL PITFALL: Cloudflare Zero Trust Token-Managed Tunnels (`--token-file`)**:
    - **Rule**: When adding new public hostnames for services running behind token-managed tunnels, register the hostname via Cloudflare Zero Trust Dashboard (`one.dash.cloudflare.com` -> Networks -> Tunnels -> Public Hostname). Do not attempt to add local YAML ingress files.
    - **Mechanism**: Cloudflared instances launched with `--token-file` operate in remote-management mode; edge routing rules and DNS CNAMEs are managed centrally in Cloudflare Edge and pushed dynamically to the connector. Local ingress files are ignored in token mode.
  - **Automating Administrative System Tasks via Verified Sudoers Drop-In**:
    - **Rule**: When a root password is provided to unblock administrative tasks (such as installing Docker or system daemons), create a verified non-interactive drop-in file `/etc/sudoers.d/<user>` (`<user> ALL=(ALL) NOPASSWD:ALL`) validated via `visudo -c`.
    - **Mechanism**: Non-pty background shells cannot handle interactive sudo password prompts (`sudo: a terminal is required`). Configuring passwordless sudo through a syntax-checked drop-in permanently enables programmatic commands without piping passwords through stdin (`sudo -S`) or leaving plaintext credentials in scripts or shell history.
- **Public Showcase / Portfolio Dashboard Boundary (Akses Umum)**:
  - When exposing a showcase dashboard to the public (`akses umum`), strictly decouple public navigation from internal administrative / privileged interfaces.
  - **Rule**: Never expose raw port numbers, internal reverse-proxy admin routes (e.g. `/admin`, `/hermes`, PM2 endpoints, 9Router keys/tokens, or local system paths) in public HTML/DOM.
  - Public cards must point exclusively to read-only endpoints (e.g. `/research`, `/buku`, public live demos) or sanitized external links, keeping administrative controls protected behind authenticated subdomains or Zero Trust tokens.
- **Multi-Database Isolation**: Use SQLite with one file per modular compartment (e.g., `db_telemetry.sqlite`, `db_9router.sqlite`) to prevent cross-contamination and simplify backups.
- **Zero-Password Authentication**: Implement "Magic Link" or approval flows via Telegram Bot API. When a user requests access from a browser, the system sends an approval button to the owner's Telegram. Do not rely on basic static passwords for high-privilege command centers.
- **Autonomous AI Agent Containerization & Dual-Path GitHub Portability (Hermes in Docker)**:
  - **Rule**: Decouple the autonomous agent runtime (Hermes) from individual business projects using a dual-track GitHub architecture.
  - **Mechanism**: Bundling source repositories directly into monolithic Docker images makes images bloated (>5-10GB), hard to update, and risks leaking proprietary code or secrets across shared images.
  - **Action**:
    1. *Track 1 (Projects on GitHub)*: Individual repositories for codebases (`jajan-drive`, `sputarball`, `penelitian-ai`), version-controlled with `.gitignore` strictly omitting `.env`, `node_modules`, and caches.
    2. *Track 2 (Hermes Docker Blueprint on GitHub)*: A lightweight, reproducible repo containing `Dockerfile`, `docker-compose.yml`, volume mappings (`/opt/data` for memories, `state.db`, and custom skills), runner scripts, and sanitized `.env.example`.
    3. *Onboarding Invariant*: Any new VPS or laptop requires only 3 steps: `git clone <hermes-docker-repo>`, populate `.env`, and `./run.sh start`. Projects are then cloned inside the workspace on demand.
    4. *Headless VPS CLI Authentication Pattern*: When `gh` CLI is installed on a headless terminal without a web browser, use Personal Access Tokens (PAT with `repo` scope) via `echo $PAT | gh auth login --with-token` or an ED25519 SSH key added to `github.com/settings/keys` to avoid interactive browser redirect loops.

## 5. Engineering Mindset: Empiricism over "ABS"
When developing these systems, adhere to the "Bagus vs Jelek" integrity standard:
- **Bagus (Good)**: Backward and recursive tracing. Isolate minimal reproducible examples, validate single hypotheses with logs/telemetry, and fix root causes. Prioritize function over decoration.
- **Jelek (Bad)**: Symptom patching, guessing, or writing "Asal Bos Senang" (ABS) code that masks errors (e.g., blanket `try/catch` or auto-restarts for memory leaks).
- **CRITICAL PITFALL: The "Ghost UI" (Stale SPA Functions)**
  - **Rule**: When replacing a custom UI block (e.g., a mock dashboard) with an embedded iframe or a new component in a Single Page Application (SPA), you MUST completely delete the old rendering functions and their associated helpers (`fetchData`, `switchTab`, etc.).
  - **Mechanism**: If you use a diff tool to just inject the iframe but leave the old DOM-manipulation functions intact in the file, those old functions will still trigger on load or click, silently overwriting your new iframe with the old HTML layout.
  - **Action**: Always `grep` the frontend JavaScript file for the view's name to find and remove all orphaned helper functions before declaring the UI replaced.

- **CRITICAL PITFALL: The "Blind Success" Claim (Yields 2/10 Rating)**
  - **Rule**: Never claim a new API route, UI fix, or server deployment is working without self-verifying it first in the terminal.
  - **Mechanism**: RDP/localhost is a blind backend; the user controls you via Telegram. If you add `require('node-fetch')` to `server.js` and restart PM2, you MUST run a local `curl` to ensure it returns 200 OK (not a 500 error due to module conflicts). 
  - **Action**: Always dogfood your own endpoints via `curl -s` or `browser_exec` before telling the user to check their phone. Asking the user to QA untested code is a strict violation of this architecture's standards.

## 6. White-Label Commercial AI SaaS & Dynamic Persona Isolation
- **The "Client-Owned Personal AI" Illusion & Zero-Leak Invariant**:
  - **Rule**: When commercializing an internal AI studio into a public quota-selling SaaS where users purchase token allocations, strictly isolate the AI persona between master administrators and external buyers (see `references/white-label-commercial-ai-saas.md` for complete schema, scrypt hashing, and lifecycle hooks).
  - **Mechanism**: If the prompt system blindly passes internal VPS paths, telemetry port mappings, or personal knowledge vaults (e.g. Obsidian) to public users, users immediately perceive that the AI belongs to someone else and proprietary server topology is leaked.
  - **Action**: Dynamically bind the system persona to the authenticated user's role:
    * *Master Admin (`role === 'admin'`)*: Full grounding in internal VPS services, telemetry, and personal knowledge repositories.
    * *Commercial User (`role === 'user'`)*: Address the user by their registered name, presenting the AI as their 100% exclusive personal assistant, completely scrubbing all mentions of backend infrastructure or server topology.
- **Real-Time Token Quota Metering & Streaming Deduction**:
  - Deduct tokens accurately post-stream based on actual response length (`Math.round(fullContent.length / 3.8)` or exact tokenizer count) in an atomic transaction (`token_transactions`).
  - Cut off inference before calling upstream LLMs if `remaining_tokens <= 0` and emit a structured SSE error event (`data: {"error": "..."}`) that renders a graceful quota-exhaustion banner.
  - Expose live quota balances in the UI navbar via a dynamic pill badge (`quota-pill`) with semantic warning states (green > 15k, amber <= 15k, red <= 5k).
- **Standalone Auth Portals over Nested Sidebar Modals**:
  - **Rule**: User registration and login forms for a public SaaS must live on a dedicated standalone page/route (e.g. `login.html`), not buried inside a dashboard sidebar or drawer.
- **Dedicated Multi-Format Attachment Architecture**:
  - Separate attachment controls into distinct Apple SF Symbol icons (e.g. Photo `#btn-attach-photo` with `accept="image/*"` and Document `#btn-attach-doc` with document/code extensions).
  - Never dump uploaded file names directly into the prompt textarea. Render tactile preview chips inside a dedicated attachment tray (`.dock-attachments-tray`) above the input with file type icons and individual removal buttons (`✕`).
  - Implement a `paste` event listener on the textarea to automatically intercept clipboard screenshots (`Ctrl+V`) and convert them into preview chips.
- **Google Sign-In & Zero-Friction Social Onboarding**:
  - Implement dual-mode Google Identity Services (GIS): verify incoming Google ID Tokens server-side via `https://oauth2.googleapis.com/tokeninfo?id_token=...` without external npm bloat.
  - Support instant demo fallback mode when Google Cloud Client ID is pending configuration, plus an in-UI Client ID persistence field (`google_auth.json`) that reloads dynamically without process restarts.
  - Automatically credit new Google sign-ups with initial welcome tokens (50.000 tokens) and bind to dynamic white-label persona (`role === 'user'`).
- **Multi-Tenant Conversation Persistence & P0–P7 Context Builder Engine**:
  - **Rule**: Never use a single global chat history file for multi-user/multi-tenant SaaS. Store conversations in isolated SQLite tables (`conversations`, `messages`, `memories`, `user_profiles`) keyed by `user_id`.
  - **Context Builder Token Budget Ladder (P0–P7)**: Enforce a strict priority ladder before calling LLM completions:
    * *P0 (System Safety & Output Rules)*: Mandatory clean formatting and platform rules.
    * *P1 (Persona Isolation)*: Dynamic white-label personal persona for customers vs master admin persona for owner.
    * *P2 (Current Request)*: User's latest prompt.
    * *P3 (Task State)*: Active goals and status.
    * *P4 (Recent Messages)*: Sliding window of recent turns within remaining budget.
    * *P5 (Conversation Summary)*: Compressed dialogue history for long threads.
    * *P6 (Semantic Memories)*: Extracted user facts and preferences.
    * *P7 (RAG & Tools)*: Selective retrieved documents or tool results.
  - **API & Client Drawer Sync**: Expose `/api/studio/conversations` (list, create, detail, delete) and wire client history slide-over drawers directly to backend SQLite state, ensuring multi-device synchronization and zero cross-tenant contamination.

## 7. High-Compliance B2B / EdTech SaaS & Autonomous Blueprint Execution
- **Autonomous Blueprint Looping Invariant**:
  - When given an end-to-end blueprint or PRD with an instruction to execute autonomously in loops ("eksekusi looping, ngga perlu bertanya-tanya"), decompose the blueprint into ordered functional layers (DB schema -> Backend endpoints -> Self-verification -> Frontend views -> Administrative telemetry).
  - Execute each layer end-to-end and test via `curl` immediately. Never halt execution for cosmetic approval or trivial decisions when the specification already dictates the architecture.
- **Zero-PII Compliance Invariant (Student & Sensitive Data Protection)**:
  - **Rule**: When engineering SaaS platforms that process student assessments, gradebooks, or classroom rosters under privacy regulations (e.g. UU PDP No. 27/2022 Tier C), NEVER store student Personally Identifiable Information (real names, NIK, NISN, phone, address). (See `references/edtech-compliance-saas.md` for complete schema and implementation patterns).
  - **Mechanism**: Storing raw PII on third-party AI or multi-tenant SaaS databases violates data localization and privacy mandates, exposing institutions to severe regulatory liability.
  - **Action**: Anonymize rosters to deterministic opaque codes (`std_cls_viii_a_01`) and neutral labels (`Siswa #01`), isolating learning profiles (e.g. visual/kinesthetic indicators) completely from real-world identities.
- **Human-in-the-Loop AI Grading & Immutable Audit Trail**:
  - **Rule**: In compliance-bound SaaS (education, healthcare, legal), AI must NEVER commit authoritative final decisions, official student grades, or disciplinary marks autonomously.
  - **Mechanism**: Hallucination risks and regulatory statutes require human legal accountability for consequential evaluations.
  - **Action**: Return AI evaluations strictly as `suggested_score` with `evidence_citation` (referencing specific rubric criteria). Provide explicit "Setujui Nilai" controls for the teacher/evaluator. Every mutation, evaluation, export, or deletion must be written synchronously to an append-only `audit_logs` / `audit_events` table recording user ID, action, resource type/ID, and timestamp.
- **Scope-Aware Contextual Copilot & Interactive Action Bridges**:
  - **Rule**: In multi-entity workspaces (e.g. Class VIII-A, Project X), embed an interactive floating/docked copilot that carries the active entity scope into every prompt.
  - **Mechanism**: Ambiguous user commands (e.g. 'buat kuis mendadak', 'cek siswa remedial') fail or hallucinate if disconnected from active entity metrics.
  - **Action**: Inject active context (`class_id`, subject, learning gaps) into copilot requests. Structure copilot responses to return actionable bridges (`suggested_actions` with action type and target view) that trigger frontend workflows (e.g., opening Question Bank or switching to Content Studio) in 1 click.
- **Multi-Output Package Generator (Bundled Teaching Kit Pattern)**:
  - **Rule**: When teachers or content creators request curriculum materials, provide a 1-click bundled generation that concurrently synthesizes all 4 interconnected artifacts: Lesson Plan (RPP 2 JP), Investigation Worksheet (LKPD), Bloom HOTS Question Set & Rubric (C1-C6), and Slide Presentation Deck (5 structured frames: Hook, Concept Map, Case Study, Misconception, Exit Ticket).
  - **Mechanism**: Generating assets individually forces redundant parameter entries and leads to topic drift across teaching documents.
  - **Action**: Execute atomic generation under one transaction, save each item into `artifacts`, and track aggregated token consumption in `background_jobs`.
- **Narrative Competency Report Cards & Zero-Negative-Labeling Invariant (PPA 2026)**:
  - **Rule**: When synthesizing narrative report cards from student assessment logs under Kurikulum Merdeka (PPA 2026), strictly enforce Zero-Negative-Labeling.
  - **Mechanism**: Evaluative deficit labels (e.g. 'anak lambat belajar', 'kurang fokus') stigmatize students, violate pedagogical ethics, and invite regulatory censure.
  - **Action**: State factual achievements, provide specific constructive growth recommendations, attach portfolio evidence citations, and require explicit teacher review (`teacher_reviewed = 1`) before final export.
- **Native Binary Office Document Export (`.docx`) in Node/Express**:
  - **Rule**: When generating official, print-ready administrative documents (e.g., RPP/LKPD for school district compliance), export genuine binary `.docx` buffers instead of converting raw HTML strings.
  - **Mechanism**: Word processors distort pasted HTML or print CSS, breaking official government letterheads, signature blocks, and tabular assessment rubrics.
  - **Action**: Use the `docx` library (`Document`, `Packer`, `Paragraph`, `Table`) to construct formal documents. Stream the buffer directly to the client with `Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document` and `Content-Disposition: attachment; filename="..."`.
- **Client-Facing Tenant Identity & Anti-Internal Jargon Invariant (Dasbor Klien)**:
  - **Rule**: When engineering a client-facing or tenant-facing SaaS dashboard (dasbor untuk klien), NEVER hardcode placeholder institution/client names (e.g., "SMP Negeri 01 Unggulan") or developer pilot/system capacity jargon (e.g., "1 Guru (Pilot Tahap 1) / 1 / 1.000 Guru", "Max 1.000 Teachers • SQLite WAL Mode") in titles, topbars, hero banners, or metric cards.
  - **Mechanism**: The client expects the workspace to represent THEIR institution or team. Displaying another institution's name or developer-centric testing stats ("Pilot Stage 1", backend storage mode) destroys the commercial credibility of the product and makes it look like an unfinished internal staging mockup.
  - **Action**:
    1. *Universal, Professional Titling*: Name panels by their functional capability (e.g., "Pusat Kendali Pembelajaran & Kurikulum", "Panel Kurikulum & Rombel") rather than hardcoded client names.
    2. *Client-Relevant Operational Metrics*: Replace developer capacity counters with operational client metrics (e.g., "Rombongan Belajar (Rombel): 3 Rombel Terkelola / 96 Murid Terdaftar", "Alokasi Kuota Token AI", "Total Dokumen Ajar").
    3. *Self-Serve Identity Customization*: Provide a dynamic profile modal/endpoint (`POST /api/guru/admin/school-profile`) so clients can update their institution name and instructor credentials on the fly, immediately synchronizing to topbars, sidebars, and official exported document letterheads (kop dinas).
    4. *Clean Topbar & Navigation*: Keep topbar pills focused on operational status (e.g., "🏫 Sekolah Mitra Terdaftar", "Kurikulum Merdeka 2026") rather than database storage modes or tenant capacity ceilings.
- **Automated Multi-Format Document Ingestion for RAG Grounding (`.pdf`, `.docx`, `.txt`)**:
  - **Rule**: When allowing clients or teachers to provide reference materials for strict AI RAG grounding, accept direct `.pdf` and `.docx` file uploads in addition to manual text.
  - **Mechanism**: Expecting non-technical users to manually copy-paste multi-page textbook chapters or syllabus documents results in text truncation, missing tables, and resistance to grounding features.
  - **Action**: Accept file uploads via base64 JSON payload or multipart (`POST /api/.../sources/upload`), extract raw text server-side using `pdf-parse` (for PDF) and `mammoth` (for DOCX), normalize whitespace, partition into semantic chunks (~500 characters), and record in `source_documents` with full audit logging.
- **Headless Chromium Server-Side Official PDF Generation (Puppeteer A4)**:
  - **Rule**: Provide a direct 1-click server-side `.pdf` download endpoint (`GET /api/.../export/pdf`) rather than relying exclusively on browser `window.print()` (Ctrl+P).
  - **Mechanism**: Mobile browsers and in-app webviews (Telegram, WhatsApp) do not support desktop print dialogs reliably, often dropping print CSS backgrounds, headers, and page breaks.
  - **Action**: Launch headless Chromium via Puppeteer (`--no-sandbox`, `--disable-setuid-sandbox`, `--disable-dev-shm-usage`), inject an official A4 document template with institutional headers and metadata, render `@page { size: A4; margin: 20mm 15mm; }`, and stream the binary buffer with `Content-Type: application/pdf`.
- **The "Dead-End Dashboard Artifact" Trap & Context-Reuse Action Bridges**:
  - **Rule**: Never render recent project artifacts, lesson plans, or generated outputs on dashboard overviews as static text with mere status badges. Always provide direct contextual action bridges (e.g., "Buka di Studio", "Buat Kuis dari Materi Ini", and instant DOCX/PDF export).
  - **Mechanism**: Showing generated artifacts without actionable next steps breaks the core pedagogical product loop (`PLAN → CREATE → TEACH → ASSESS`), forcing users to re-enter parameters manually from scratch.
  - **Action**: Bind 1-click action triggers on each artifact card that pre-fill subsequent creation prompts, inherit the active class/topic scope, and navigate to the target workspace smoothly (see Section 11 in `references/edtech-compliance-saas.md`).
- **Differentiated Grouping & 4-Scale Performance Rubrics (Permendikdasmen No. 11/2025)**:
  - **Rule**: Support automated student grouping from verified gradebooks into Heterogeneous (serpentine peer-tutoring) and Homogeneous (readiness tiers) with targeted scaffolding strategies, generate 4-scale analytic rubrics with score conversion formulas, and accept bulk Non-PII CSV roster ingestion (see Sections 13–15 in `references/edtech-compliance-saas.md`).
- **Class Mastery Heatmap & Remedial Action Bridges**:
  - **Rule**: Track and visualize real-time mastery across specific learning objectives (Tujuan Pembelajaran / TP) per cohort (`GET /api/.../mastery-heatmap`). Provide 1-click action triggers on lagging indicators to generate targeted remedial modules directly in Content Studio.
  - **Mechanism**: Showing aggregate scores without indicator-level breakdown obscures which specific competency needs intervention, forcing teachers to manually diagnose gaps.
- **Formative Feedback Co-Authoring & Class Pedagogical Memory**:
  - **Rule**: AI assessment evaluation must draft actionable qualitative formative feedback (`formative_feedback`) alongside quantitative scores, and classes must retain persistent pedagogical memories (`classes.class_memory`) detailing cohort learning traits, pacing, and retention gaps (see Sections 16–17 in `references/edtech-compliance-saas.md`).
  - **Mechanism**: Numerical marks alone provide zero diagnostic benefit to learners under Kurikulum Merdeka 2026. Storing class pedagogical memory prevents the AI from resetting to generic recommendations on subsequent instructional planning cycles.
- **Task-Oriented over Feature-Oriented Dashboard Paradigm**:
  - **Rule**: Never construct an education/client dashboard as a cluttered feature-dump. Anchor the workspace homepage around a single operational question: *"Hari ini mau mengerjakan apa, [Nama]?"* with 5 primary task-action cards (Persiapkan Mengajar, Buat Asesmen, Periksa Hasil Siswa, Buat Remedial, Tanya Copilot).
  - **Mechanism**: Showing dozens of disparate tools simultaneously causes choice overload and disorientation for new users. Structuring around primary workflows guides the teacher's natural daily mindset.
  - **Action**: Place the 5 task cards at the top focal point, followed immediately by an AI command input. Prioritize urgent action items ("Yang Perlu Diselesaikan Guru Pekan Ini": students needing remedial, unconfirmed formative submissions, sessions missing lesson plans) and the next class schedule over passive, abstract metric cards.
- **AI Copilot as Central Orchestrator (Single-Command Multi-Feature Synthesis)**:
  - **Rule**: The AI Copilot must act as the primary operational engine of the platform, not an ancillary corner chat bubble. Enable direct execution of multi-step feature workflows from a single natural command.
  - **Mechanism**: Requiring users to navigate separate sub-menus and manually re-enter parameters to build a full teaching kit introduces friction and limits AI adoption.
  - **Action**: Implement command intent detection (e.g. "Buat persiapan mengajar [topik] [kelas]"). Copilot automatically parses topic/cohort and returns a structured multi-output proposal (RPP Merdeka 2026, LKPD 3 Tingkat, 5 Soal HOTS, Slide Tayang, Rubrik 4-Skala) with a 1-click execution bridge (`execute_package_now`) that synthesizes the entire bundle atomically.
- **Zero Developer Jargon in Client Applications (Native Educator Language)**:
  - **Rule**: Strictly eliminate developer-facing engineering terminology from client UI copy, tool labels, and system status badges.
  - **Mechanism**: Exposing technical AI/backend abstractions creates cognitive friction and makes the product feel like a raw software prototype rather than an intuitive, professional teaching tool.
  - **Action**: Replace developer terms with educator-friendly equivalents:
    * *RAG Context* -> **Sumber Materi**
    * *Strict Grounding* -> **Gunakan hanya materi saya (Anti-Halusinasi)**
    * *Suggested Grading Engine* -> **Bantu Periksa Jawaban Siswa**
    * *Audit Trail & Telemetry* -> **Riwayat Aktivitas & Keamanan Data Siswa**
    * *Token Quota Meters* -> Tangible client efficiency metrics: **Dokumen Siap Cetak Dihasilkan** and **Estimasi Jam Kerja Dihemat**.
- **Strict Decoupling of Marketing Landing Page & Application Workspace**:
  - **Rule**: When delivering commercial or multi-tenant SaaS products, completely separate the public marketing landing page (`index.html`) from the application workspace (`app.html` or `/app`).
  - **Mechanism**: Directing first-time visitors straight into a complex workspace causes immediate drop-off because the value proposition and workflow were never explained.
  - **Action**: The landing page must lead with a clear, benefit-driven headline (*"Satu Copilot untuk Seluruh Pekerjaan Guru"*), outline the 5-step workflow (Rencana -> Mengajar -> Asesmen -> Analisis -> Remedial), showcase concrete time savings and regulatory compliance, and provide prominent 1-click CTAs (*Coba Demo Langsung*, *Masuk Ruang Kerja*), devoid of technical jargon.
- **Mobile Ergonomics for Daily Educator Workflows (Thumb-Zone & 5-Tab Dock)**:
  - **Rule**: Mobile must not be a mere scaled-down desktop with squeezed sidebars. Design mobile interfaces specifically for rapid daily educator actions.
  - **Mechanism**: Shrinking multi-column desktop layouts forces micro-scrolling, causes persistent floating buttons to overlap cards, and makes action buttons impossible to tap reliably with one hand.
  - **Action**: Enforce a dedicated 5-tab bottom navigation dock (*Beranda*, *Kelas*, *Copilot*, *Dokumen*, *Profil*) anchored at the bottom edge (`natural thumb zone`). Suppress persistent floating desktop copilot bubbles on mobile viewports (`<= 768px`) to prevent visual collision, provide >=90px bottom clearance, and prioritize the immediate next teaching schedule and urgent tasks on the mobile home screen.
- **First-Time User Guided Onboarding Wizard**:
  - **Rule**: Greet new users with a lightweight, modal onboarding wizard before presenting the full workspace.
  - **Action**: Prompt for Primary Subject, Grade/Cohort level, Curriculum Standard, and Immediate Weekly Need (Lesson Prep, Exam Creation, Remedial, or Grading). Persist the selection to local storage and user profile, automatically scoping subsequent content studio prompts and dashboard filters to the educator's specific domain.
- **Closed Pedagogical Remedial Feedback Loop**:
  - **Rule**: Assessment analytics must directly trigger remediation workflows without manual intervention.
  - **Action**: In the learning gap / mastery view, highlight the single lowest-performing objective across the cohort and present 3 direct 1-click action buttons: *✦ Buat Modul Remedial* (targeted scaffolding for at-risk students), *✦ Buat Pengayaan* (advanced inquiry for master students), and *✦ Penjelasan Alternatif* (concrete everyday analogies for difficult concepts).
- **Dynamic Multi-Jenjang & Multi-Fase Calibration (Anti-Substring Collision Trap)**:
  - **Rule**: In educational SaaS, dynamically calibrate lesson duration (PAUD 150m, SD 35m/JP, SMP 40m/JP, SMA/SMK 45m/JP), cognitive depth (Bloom C1-C3 vs C3-C5 vs C4-C6 HOTS), and prompt scaffolding to the class's educational phase (see Section 19 in `references/edtech-compliance-saas.md`).
  - **Mechanism / Pitfall**: Evaluating grade levels via naive string matching (`grade.includes('kelas 1')`) causes catastrophic substring collisions on high school classes (`'kelas 10'.includes('kelas 1') === true`), erroneously forcing elementary school durations and child-level language onto senior cohorts.
  - **Action**: Evaluate level matching strictly in descending specificity: PAUD -> SMA/SMK (Kelas 10-12, Fase E-F) -> SD (Fase A-C with regex word boundary `/\bkelas [1-6]\b/`) -> SMP (Fase D).
- **Modal Sticky Footer & Overflow Pinning Pattern**:
  - **Rule**: Complex multi-field creation modals must lock container height (`max-height: 88vh; display: flex; flex-direction: column;`), encapsulate form inputs inside a scrollable body (`overflow-y: auto; flex: 1;`), and anchor action buttons in a pinned footer (`border-top: 1px solid ...; margin-top: auto;`).
  - **Mechanism / Pitfall**: On standard laptop viewports (800–900px), multi-field forms push the primary CTA buttons (`Batal` / `Simpan`) below the screen fold or clip them within modal card overflow, creating a severe UX blocker where users cannot submit their data without zooming out.
- **B2B / SaaS Landing Page & Trust Conversion Architecture (Proof-over-Promise)**:
  - **Rule**: Landing pages for institutional clients (Schools, Government, Enterprise) require empirical trust architectures rather than empty marketing slogans (see Section 20 in `references/edtech-compliance-saas.md`).
  - **Proof-over-Promise Math**: Claims like "Hemat ~10 Jam/Minggu" must provide transparent per-task time breakdowns (RPP 180m -> 15m, Soal 150m -> 10m, Remedial 270m -> 15m).
  - **Single Primary CTA**: Eliminate ambiguous duplicate buttons ("Coba Demo" vs "Masuk Ruang Kerja" to same target); use 1 primary action `[ ✦ Coba Demo Gratis (Tanpa Daftar & Tanpa Kartu) ]` with beta status indicators.
  - **Show, Don't Tell**: Feature a working browser mockup of the actual active dashboard at first-fold showing live action cards and 1-click generation outputs.
  - **Humanized Security Copy**: Translate developer jargon into user-friendly terms: Zero-PII -> "Data siswa tidak dikirim ke AI eksternal"; Model Non-Retention -> "Guru memegang kendali 100% hak ekspor/hapus"; Automated Grading -> "Prinsip Human-in-the-Loop: AI hanya draf saran, Guru yang mengesahkan".
  - **Diagnostic Gap Spotlight**: Render actual gap cards ("12 dari 32 Siswa Belum Paham X") with immediate 1-click action triggers `[ ✦ Buat Remedial ]`.
  - **Closed Continuous Teaching Loop**: Extend the 5-step workflow to 6 steps ending in "Evaluasi & Siklus Lanjutan" so the loop is continuous.
  - **Adaptive Mobile Sticky CTA**: Hide bottom sticky CTA on initial mobile load (`scrollY = 0`), and trigger slide-up smoothly only after user scrolls past the hero CTA (`scrollY > 280px`) with min 48px touch targets.
  - **Institutional Branding & Copyright Harmony**: Use professional organization branding (e.g. *Jajan Digital EdTech*) in topbars/footers while preserving creator copyright attribution.
  - **Official Administrative Compliance (Lembar Pengesahan Siap Audit)**: In Indonesian educational and institutional SaaS, exported lesson plans (RPP/Modul Ajar) and exam documents require formal 2-column borderless signature blocks with teacher NIP, headmaster name/NIP, and municipality date (see Section 21 in `references/edtech-compliance-saas.md`). Using bare paragraphs or tab characters causes layout collapse across MS Word versions; always construct a 100%-width borderless table (`Table`, `BorderStyle.NONE`).
  - **Emergency 5-Minute Ready-to-Print Kit (`/quick-prep`)**: Critical educator friction occurs 10–15 minutes before the bell. Provide a 1-click single-topic endpoint (`POST /quick-prep`) that concurrently synthesizes RPP, 3-tier LKPD, and HOTS questions in <2 seconds with direct Word `.docx` download buttons (see Section 22 in `references/edtech-compliance-saas.md`).
  - **Human-in-the-Loop Official Sign-off Gate**: Prevent educator liability fears with an explicit 2-phase state machine (`🟡 Draf Rekomendasi AI` -> `✓ Telah Disahkan Resmi oleh Guru Pengampu`). The sign-off endpoint (`POST /artifacts/:id/verify`) writes to immutable audit logs and stamps the verification seal directly into exported Word/PDF files (see Section 23 in `references/edtech-compliance-saas.md`).