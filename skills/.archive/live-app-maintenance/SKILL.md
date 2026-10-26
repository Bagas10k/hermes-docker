---
name: live-app-maintenance
description: Use when maintaining or polishing live production web apps.
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [production, maintenance, live-apps, ui-polish, cache-busting, zero-downtime]
---

# Live Application In-Place Maintenance & UI Polish

## When to Use
Use when updating, bug-fixing, styling, or maintaining an already-running fullstack application in place without disrupting its active background daemons, databases, or client sessions.

## Core Rules & Workflow

### 1. In-Place Project Directory Locking
- Immediately navigate (`cd <project_dir>`) and verify working directory at the start of work. Avoid repeatedly specifying long absolute paths when executing multi-step tasks inside a dedicated repo.
- Verify Git status and remote auth tokens up front (`git remote -v`, `git pull origin <branch>`).

### 2. Surface-Only Modification Boundary
- When instructed to polish visuals or fonts ("untuk tampilannya aja jangan mengganggu sistem"), confine all modifications strictly to CSS stylesheets, font CDN inclusions, and presentation HTML markup.
- Never touch route controllers, database schemas, socket handlers, or server entrypoints unless an explicit backend feature is requested.

### 3. Immediate Cache-Busting for Static Asset Replacements
- Replacing an image file on disk (e.g. `media/Qris.jpeg`, `public/logo.png`) causes browsers to continue serving stale cached assets.
- Pair every static asset update with a dynamic cache-busting query parameter in template rendering (e.g., `src="${rawImageUrl}?t=${Date.now()}"`) or a content-hash revision.
- When replacing assets on the fly, update both the upload storage location and public mirrors (e.g., `media/` and `public/`), verify file checksums, and reload the active view.

### 4. Zero-Downtime Targeted Process Restarts
- When server-side code must be updated (e.g. adding OTP reset endpoints), identify and terminate only the specific PID bound to the application port (`netstat -ano | findstr :<port>`), then immediately relaunch via background terminal.
- Never issue indiscriminate process kills (`taskkill /f /im node.exe`) that disrupt other running daemons or tool servers.

### 5. Script Paths for Hermes Cronjobs
- In cronjob definitions (`cronjob_manage action='create'`), relative script paths resolve strictly under `~/.hermes/scripts/` (e.g., `C:\Users\<user>\AppData\Local\hermes\scripts\`).
- Passing an absolute path or repo-relative path directly into the `script` parameter triggers a schema rejection. Always copy or symlink recurring maintenance scripts into `~/.hermes/scripts/<script_name>.py` before registering the cronjob with `script="<script_name>.py"`.

### 6. Dual-Tunnel Separation & Unified Reverse Proxy Gateway
- Separate permanent services from ad-hoc experimental workspaces:
  - System daemon tunnels (e.g., Windows Service `Cloudflared` bound to production endpoints like port 3000) must remain undisturbed.
  - Temporary exploratory dashboards or high-frequency telemetry tools should not spawn multiple individual ad-hoc tunnels that exhaust memory and scatter URLs.
- **Unified Gateway Pattern**: Combine multiple internal micro-services (e.g., telemetry at 8090, briefing at 8095, design vault at 8085) behind a single reverse proxy gateway (port 8080) routed by URL path prefix (`/telemetry/`, `/briefing/`, `/apex/`), exposed via one single Cloudflare tunnel.
- **Ad-Hoc Local Service Public Exposure via Cloudflare Quick Tunnels**:
  - When exposing an isolated local backend running on loopback (e.g. Next.js/custom daemon on port 20128):
    1. Inspect running `cloudflared.exe` instances and their local metrics ports (`127.0.0.1:20241..20245`).
    2. Terminate stale/dead ad-hoc quick tunnel processes rather than accumulating unneeded tunnels.
    3. Launch a dedicated quick tunnel with `cloudflared.exe tunnel --url http://127.0.0.1:<port> --no-autoupdate` in background.
    4. Retrieve the newly generated public hostname cleanly by querying the loopback metrics API endpoint (`http://127.0.0.1:<metrics_port>/quicktunnel` returning `{"hostname":"..."}`) instead of parsing stderr or guessing.
    5. Verify remote reachability with a fast HEAD probe (`curl -sI https://<hostname>/<path>`) before handing the link to the user.
- **Default Password Remote Access Blockers**:
  - Internal dashboards (such as 9Router and similar admin suites) enforce origin/remote security checks that block public tunnel logins if the system is still on the factory default password (e.g., `123456`), responding with error `Default password must be changed before remote access` or requiring immediate password change.
  - When exposing local tools remotely, check the local auth state first (`curl http://127.0.0.1:<port>/api/auth/status`). If using default credentials, log in via localhost/loopback using an authenticated session (`curl -c cookie.txt -b cookie.txt ...`), update the password to the environment standard via settings PATCH/API from 127.0.0.1, and verify the remote login over the public tunnel URL before sharing credentials with the user.
- **Gateway Subpath Prefix Awareness in Frontend**:
  1. Mount the existing service behind a stable path with a reverse proxy and strip exactly that prefix before forwarding (for example, `/portal/api/x` → upstream `/api/x`). Preserve the standalone local root so the service remains directly testable.
  2. Make static HTML assets subpath-safe with document-relative URLs (`./app.css`, `./app.js`) instead of root-relative `/app.css`; root-relative assets escape the mounted route and hit the gateway application.
  3. In frontend JS, derive one base prefix from `location.pathname` and prepend it to every API, image, download, and WebSocket URL. Do not patch only `fetch()` while leaving generated media URLs rooted at `/`.
  4. Verify the same feature at both layers: upstream root and public subpath. Probe HTML, CSS, JS, API, and one generated media URL independently before browser QA.
  5. In a real browser, assert expected DOM content, zero horizontal overflow on desktop/mobile, and the core interaction (search, detail drawer, form, or login). Scroll lazy-loaded galleries before counting broken images; unloaded offscreen images can have `naturalWidth === 0` without being failures.
  - Provide HTTP polling fallback alongside WebSockets when edge proxies or mobile browsers may block the handshake; choose a frequency appropriate to the data rather than imposing high-frequency polling universally.

### 7. Mobile-First Responsive Standards for Live Portals
- Ensure all live dashboard portals are immediately usable on mobile viewports:
  - Include `<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">`.
  - Minimum touch-target size 44px with active tap feedback (`transform: scale(0.98)`).
  - Use responsive grid layouts (1-column on mobile, multi-column on desktop) and cluster topbar action buttons into a unified segmented chassis rather than loose individual buttons.

### 8. Asynchronous Daemon Startup & Readiness Verification
- Heavy service daemons (e.g. Node.js apps initializing SQLite schemas, cleaning stale headless Chrome sessions, or connecting messaging clients) do not bind ports instantaneously.
- Premature checks immediately after spawning in the background (`terminal(background=true)`) yield false negatives.
- Protocol:
  1. Inspect process PID and execution health with `process_manage(action='poll', session_id=...)` to confirm the runtime didn't crash on boot.
  2. Verify socket listening state via `netstat -ano | grep <port>`.
  3. Confirm HTTP readiness with a targeted status probe (`curl -I http://127.0.0.1:<port>/endpoint`) before declaring the service active or attempting reverse proxy traffic.

### 9. Session-Independent Daemon Isolation (PM2 & Windows Task Scheduler)
- Long-running core production services must never run as bare child processes under Hermes `terminal(background=true)` or active chat sessions — session resets (`/new`), agent reloads, or terminal teardowns terminate child process trees.
- Standalone Service Protocol:
  1. Use a dedicated process manager like PM2 (`pm2 start index.js --name "<app-name>" --time`).
  2. Save daemon state immediately via `pm2 save` (`~/.pm2/dump.pm2`).
  3. Guarantee auto-recovery on Windows reboot/logon via Task Scheduler: create an elevated logon task running `pm2 resurrect` (`schtasks /create /tn "<TaskName>" /tr "<path_to_resurrect_bat>" /sc ONLOGON /rl HIGHEST /f`).
  4. Verify the daemon is running independently via `pm2 status` and probe the port before releasing to the user.

### 10. Third-Party Data Ingestion & Silent Rate Limits
- **Scraping APIs & Free Tiers**: Libraries like `deep-translator` (using Google Translate) or raw scrapers may swallow HTTP 429/500 errors and silently return literal error strings (e.g., `"Error 500 (Server Error)!!"`) instead of raising Python exceptions.
- **Data Corruption Guard**: Always validate ingested payload strings against known failure literals *before* writing to production JSON/databases. If validation fails, gracefully retain the original text or abort the transaction. Do not overwrite valid data blindly.
- **Background Cron Operations**: Move heavy bulk processing (like translating 100+ articles) to a detached background process (`spawn('...', { detached: true, stdio: 'ignore' }).unref()`) rather than blocking the main scraping daemon.

### 11. Instagram Graph API (Publishing & Analytics Workflows)
- **Token Acquisition**: You cannot acquire Long-Lived Access Tokens via CLI/code. The user must manually navigate Meta's *Graph API Explorer*, authorize their linked Facebook Page, grant `instagram_content_publish` + `instagram_basic`, generate the short-lived token, and extend it via the Access Token Tool.
- **Instagram Account ID Extraction**: Run `GET vX.X/me/accounts?fields=instagram_business_account` in the Explorer to extract the numeric ID.
- **Cost & Rate Limits**: The Graph API is free. Standard publishing limit is 50 posts (including carousels) per 24 hours.
- **Analytics Capability**: The API allows bi-directional data flow. Beyond publishing, use `GET /{ig_account_id}/media?fields=id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,like_count,comments_count` to build live dashboards mirroring IG insights.

### 12. Security Audit-Fix Cycle for Live CMS/Admin Systems
- When hardening a live admin system, delegate a **read-only audit subagent** with a specific blocker checklist (not a vague "review everything"). Categories to enumerate: hardcoded secrets, auth middleware enforcement, server-side state machine integrity, race conditions on publish/deploy, XSS via URL schemes, input validation timing, content snapshot immutability, AI field preservation.
- After receiving audit results, fix each blocker in batch, then re-run `node --check` on EVERY modified file AND the full `npm test` suite before restarting PM2. Syntax checks catch broken exports that tests skip if the file isn't directly `require()`d.
- **Rate limiting must live inside the auth middleware itself** (`requireAdmin`), not only on the login endpoint — otherwise attackers brute-force the secret against any admin-gated route.
- **URL scheme allowlisting (`safeUrl()`):** Any URL from user input, RSS feeds, or external APIs rendered as `src`/`href` must pass through a validator rejecting non-http(s) schemes (`javascript:`, `data:`, `vbscript:`). Apply both server-side and in client-rendered HTML.
- **Atomic workflow state claims:** Use `UPDATE ... SET status='PUBLISHING' WHERE status='APPROVED'` (checking rows affected = 1) to prevent concurrent double-publish. The second request sees 0 rows and fails.
### 13. Dynamic Content Rendering & CMS Fallback Values
- When building automated content generators or CMS templates, **never hardcode text** (like "Bagian 1", "Dampak") directly into the fallback logic or HTML renderer if those values should adapt to the topic.
- Extract dynamic titles, summaries, and topics directly from the source material. Use conditional logic tied to the current content context (e.g., `return \`3 Fakta Utama: \${source.title.split(':')[0]}\``) instead of generic static strings.
- Verify that every section header, kicker, and label in a generated visual asset (like an IG Carousel slide) accurately reflects the active content rather than being left behind from a previous template state.

### 14. Anti-Blind Success (Self-Verification Protocol)
- NEVER report a feature, endpoint, or UI fix as "ready" or "done" without independently verifying it yourself.
- Verify both layers before reporting:
  1. Local process health: `curl -sI http://127.0.0.1:<port>/<path>` and inspect the relevant PM2 error log after restart.
  2. Public/user path health: `curl -sI https://<public-domain>/<path>` and, for JS-heavy UIs or auth forms, use a real browser session to inspect DOM text and submit a harmless probe.
- A HEAD/200 check is not enough for interactive pages. If the user flow includes login, form submit, redirect, iframe, or dashboard rendering, reproduce that flow from the public URL and verify the expected DOM text or API response. Do not ask the user to be the first QA pass.

### 15. Integrating Existing Web GUIs (No-Rebuild Rule)
- When integrating a management interface for a backend service (e.g., an API model router, process manager, or database explorer) into a unified dashboard, determine if the service already ships with a built-in Web UI on its port (`curl -sI http://127.0.0.1:<port>/`, follow redirects, and inspect `/login` or `/dashboard`).
- If a built-in dashboard exists, DO NOT write custom HTML/JS from scratch to duplicate its functionality. Rebuilding a manager UI for a tool that already has one wastes time and creates fragile mockups.
- Prefer a direct public route or reverse proxy to the native UI. If embedding in an `iframe`, NEVER put `127.0.0.1` or a private loopback URL in client HTML; browsers resolve that on the user's device, not the server.
- For Next.js/admin apps behind a proxy, proxy root-relative assets and routes (`/_next/*`, `/api/*`, `/login`, `/dashboard`) consistently. Apps often redirect from `/` to `/dashboard` or `/login`; subpath-only proxies can break into `Cannot GET /dashboard` unless redirect locations and fallback routes are handled.
- Register proxy routes that need raw bodies (especially `/api/auth/*` login endpoints) before `express.json()` or body parsers. Once Express consumes the request body, proxying POST login can hang or return wrong 405/404 responses.
- Verify the integrated UI with a browser-level probe: load the public `/login`, inspect the expected text, submit a harmless wrong-password probe, and confirm it returns a visible error instead of infinite loading.

### 16. Live Daemon & Messaging Client Telemetry Verification
- **Log Cross-Verification over Naive State Flags**: Messaging clients and headless browser wrappers (e.g. `whatsapp-web.js`, Puppeteer) can fire transient lifecycle events (like `loading_screen` during background syncs) that leave status variables reporting `INITIALIZING` even while the bot is actively transacting and replying in chats.
- When diagnosing live bot/service health, cross-verify the status endpoint against real-time stdout/stderr (`pm2 logs <app> --lines 50`) for recent ingress/egress traffic (`[DEBUG CHAT]`, incoming transactions) and check `client.info?.wid` rather than assuming the client is down.
- When executing ad-hoc diagnostic scripts against Node.js/SQLite projects, verify if the DB wrapper initializes asynchronously (`await initDatabase()`) before calling `getDb()`, and inspect table schemas (`PRAGMA table_info(...)`) before querying fields.

### 17. High-Volume Media Gallery Performance & Instant Loading
- **Root Cause of Heavy/Slow Web Pages:** Embedding full-resolution raw media (e.g. 10MB-18MB PNGs/JPEGs) directly in grid card `<img>` tags chokes client bandwidth and freezes browser rendering/GPU decoding, even when using native `loading="lazy"`.
- **Pre-Generated WebP Thumbnail Pipeline:**
  - Never serve raw original files in list/grid views.
  - Generate lightweight WebP thumbnails (e.g., width 480-600px, quality 75-80 via Python Pillow or Sharp) stored in a dedicated thumbnail cache directory (reducing total weight by 95%+).
  - Serve thumbnails via a dedicated static route (e.g. `/thumb/`) with aggressive immutable caching: `Cache-Control: public, max-age=2592000, immutable`.
  - Reserve original high-resolution media exclusively for modal/fullscreen detail views upon user click.
- **Frontend Progressive DOM & Layout Shift Elimination:**
  - **Chunked / Virtualized Rendering:** Do not inject 100+ media cards into the DOM at once. Render an initial batch (e.g., 16-20 items) and append subsequent batches progressively on scroll via `IntersectionObserver` or a 'Muat Lebih Banyak' trigger.
  - **Zero CLS:** Enforce strict aspect ratios on image containers and add skeleton placeholders with `decoding="async"` and `loading="lazy"` on all thumbnail elements.
