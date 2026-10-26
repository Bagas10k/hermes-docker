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
- **Deployment Maturity Segregation**: Always segregate projects cleanly into distinct tiers:
  1. **Produksi & Publikasi (Live)**: Customer-facing apps and published media with live endpoints.
  2. **Internal & Uji Coba (Lab)**: System daemons, schedulers, and active cognitive research labs.
  3. **Layanan Terpisah (Standalone)**: Projects executed on separate hosts/instances; do not run duplicate processes or proxy to non-existent local ports.
- **Micro-Status Indicators**: Use tiny 6px status dots paired with clean mono text (`Live`, `Internal`, `Uji Coba`, `Mandiri`), never cluttered multi-badge ribbons.
- **Responsiveness**: Use an Adaptive Liquid Interface. Desktop gets a Dual-Sidebar; mobile gets a bottom tab-bar (like native apps).
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
- **Multi-Entity Tree / Catalog Propagation**: When providing clone/duplication for nested tree structures (e.g., Menu Trees, interactive flow nodes, or category catalogs) across groups or tenants:
  - Add a dedicated action button in the visual editor toolbar right beside group selection and save controls.
  - Open a modal showing source statistics (source group ID, total node count) and a scrollable target checklist supporting 1-to-many propagation with "Pilih Semua / Batal Semua".
  - Provide an option to include accompanying template elements (e.g. category & content footers).
  - Perform deep cloning on the backend (`JSON.parse(JSON.stringify(tree))`), emit socket update events for each target, and verify the clone in the database (matching child node counts) before declaring completion.

## 4. Backend & Security
- **Public Showcase / Portfolio Dashboard Boundary (Akses Umum)**:
  - When exposing a showcase dashboard to the public (`akses umum`), strictly decouple public navigation from internal administrative / privileged interfaces.
  - **Rule**: Never expose raw port numbers, internal reverse-proxy admin routes (e.g. `/admin`, `/hermes`, PM2 endpoints, 9Router keys/tokens, or local system paths) in public HTML/DOM.
  - Public cards must point exclusively to read-only endpoints (e.g. `/research`, `/buku`, public live demos) or sanitized external links, keeping administrative controls protected behind authenticated subdomains or Zero Trust tokens.
- **Multi-Database Isolation**: Use SQLite with one file per modular compartment (e.g., `db_telemetry.sqlite`, `db_9router.sqlite`) to prevent cross-contamination and simplify backups.
- **Zero-Password Authentication**: Implement "Magic Link" or approval flows via Telegram Bot API. When a user requests access from a browser, the system sends an approval button to the owner's Telegram. Do not rely on basic static passwords for high-privilege command centers.

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