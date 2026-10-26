---
name: live-app-maintenance
description: Use when maintaining or polishing live production web apps.
version: 1.0.0
platforms: [linux, macos, windows]
related_skills:
  - long-horizon-app-building
  - structured-project-execution
  - fullstack-systems
  - fullstack-delivery
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

### 4. Targeted Process Restarts
- First identify the port owner and its supervisor: `ss -ltnp` (or `netstat -ano`), then inspect the process cgroup/parent and `systemctl --user status <unit>` or `pm2 status`. Restart through the **existing supervisor**, not by killing its PID and launching an untracked background copy; competing launches can collide on the same port and trigger a restart loop.
- Before any production restart, preserve rollback state and plan a readiness check; restart only the named service, then verify its listener, HTTP endpoint, and recent journal/error log. Never issue indiscriminate process kills that disrupt other daemons.

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
  - When exposing local tools remotely, check the local auth state first (`curl http://127.0.0.1:<port>/api/auth/status`). If the application requires a first-run password change, use its supported local setup/recovery flow with the owner's authorization and a strong secret handled through an approved vault; never type, request, print, or share credentials in chat or tool output. Verify remote authentication and the protected destination separately. A public login hint or `hasPassword=true` status does not prove the active credential or a working session.
- **Gateway Subpath Prefix Awareness in Frontend**:
  - Web apps running behind subpath proxies fail if client-side code assumes root `/`.
  - In frontend JS, dynamically derive the base prefix: `const basePath = location.pathname.startsWith('/telemetry') ? '/telemetry' : '';` for all `fetch()` and `WebSocket` endpoints (`${basePath}/ws/telemetry`).
  - Always provide high-frequency HTTP polling fallback (e.g., 100ms interval) alongside WebSockets to guarantee seamless data streaming if edge proxies or mobile browsers block WebSocket handshakes.

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

### 9. Session-Independent Daemon Supervision
- For a service that appears to die, inspect the current owner **before installing anything**: `ss -ltnp`, `/proc/<pid>/cgroup`, `systemctl --user show <unit> -p ActiveState -p Restart -p NRestarts -p UnitFileState`, `systemctl --user status <unit>`, and `pm2 status` as applicable. On Linux, check `loginctl show-user <user> -p Linger` if a user service must survive logout/reboot. Use exactly one supervisor per port; a second PM2/systemd/background instance may cause `EADDRINUSE` and repeated downtime.
- If already supervised, correlate restart count with `journalctl --user -u <unit> --since '<window>'` and inspect exit codes, port-bind errors, and relevant kernel OOM evidence. `Restart=always` proves recovery policy, **not stable uptime**; separate process failure from the cause of failure, and do not label a SIGKILL as OOM without evidence.
- If no supervisor exists, install one suited to the host (systemd user/system unit on Linux, PM2 where appropriate; Windows service or Task Scheduler for reboot recovery). Avoid long-lived production daemons as children of an interactive chat session. Verify supervisor enablement, listener ownership, HTTP readiness, and public route; observe restart count over a bounded interval before claiming stability.

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

### 17. Ephemeral Preview Server Cleanup & Process Hygiene
- Ad-hoc local preview servers (such as `python3 -m http.server <port> --bind 127.0.0.1`) started in the background do not self-terminate when the user finishes viewing.
- Leaving ad-hoc servers running leaks loopback ports, retains active systemd/process manager scopes across days, and creates unnecessary process clutter.
- Always inspect active socket listeners (`ss -ltnp`) and process scopes (`systemctl --user list-units 'hermes-worker-*'`) after completing UI previews. Once verification concludes or when auditing background jobs, cleanly terminate unused scopes (`systemctl --user stop <scope>`) and verify the listening port is closed.

### 18. Diagnosing Apparent Agent Stalls & Upstream Retry Backoff
- When an autonomous agent or bot stops replying and appears frozen/stuck in chat, inspect `logs/agent.log` and `logs/gateway.log` before assuming the process crashed or attempting indiscriminate restarts.
- Check for upstream provider disconnections (`APIConnectionError`, timeouts) cascading into fallback model errors. If a fallback model or proxy returns an HTTP 503 or 429 carrying a reset timer (e.g. "reset after 9m 56s"), the agent framework schedules an exponential backoff sleep (`Retrying API call in 600.0s`), pausing the worker thread for 5–10 minutes.
- **Never register unprobed models in `fallback_providers`**: Models in fallback chains must be verified with a live completion probe beforehand (`curl http://localhost:<port>/v1/chat/completions`). If a fallback model returns 503 (e.g. unsupported model on Codex/provider), Hermes's default retry policy schedules an exponential sleep up to `RETRY_AFTER_CAP_S`. To prevent catastrophic 10-minute freezes, cap `RETRY_AFTER_CAP_S = 60.0` in `agent/retry_utils.py` and enforce `tool_loop_guardrails.hard_stop_enabled: true` with `agent.max_turns: 25` in `config.yaml` so failing tool calls fail fast rather than running 100+ turns silently.
- **Context Bloat (>100k tokens) Cascades into Connection Drops**: When context balloons to 150k+ tokens, HTTP requests suffer severe latency and network timeouts, triggering the fallback chain and exacerbating 503 retry traps. Proactively reset or compact sessions when context exceeds threshold rather than letting sessions drag hundreds of turns.
- **Clean Gateway Routing Reset for Frozen Sessions**: When an agent thread is stuck in a 600s sleep or context is bloated, clear the stale turn lease (`session_turn_leases`) and stale routing entries (`gateway_routing`) in `state.db`. This allows the gateway to spawn a 100% fresh, 0-token session on the very next user message.

### 19. Multi-Profile Telegram Bot Provisioning in Multiplexed Gateway
- When adding a dedicated Telegram bot to a profile under a multiplexed gateway (`gateway.multiplex_profiles: true`):
  1. Verify the bot token using a direct Telegram API probe (`curl -sS https://api.telegram.org/bot<token>/getMe`) to confirm the bot username and ID before configuration.
  2. Configure `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USERS`, and `TELEGRAM_HOME_CHANNEL` inside the profile's `.env` (`~/.hermes/profiles/<profile>/.env`).
  3. Ensure the profile has `profile.yaml` with a clear description and `SOUL.md` defining its specific identity and communication principles.
  4. The gateway multiplexer watches `.env` and `config.yaml` changes (`reconcile_served_profiles` every 30 seconds) and hot-attaches the new Telegram adapter (`✓ telegram connected (profile: <profile>)`) without requiring manual service restarts.

### 20. Automated Multi-Profile Git Backup & Confidential Sandbox Air-Gap
- When automating multi-agent ecosystem backups to Git (e.g. `daily_github_backup.py` syncing to `hermes-docker`):
  1. **Instant Multi-Profile Portability**: Package `data/profiles/<profile>/` with core identity and knowledge files (`SOUL.md`, `profile.yaml`, `config.yaml`, and `memories/USER.md` + `MEMORY.md`). On target devices, executing `unpack-state` places profiles directly into `~/.hermes/profiles/`, making them immediately recognized by Hermes without triggering onboarding wizards.
  2. **Multi-Layer Secret & State Sanitization**: Enforce two-layer exclusions in the pack script and `.gitignore` (`data/profiles/**/.env`, `data/profiles/**/state.db*`, `data/profiles/**/sessions/`, `logs/`, `cache/`). Never upload plaintext bot tokens or unpruned conversation histories to Git.
  3. **Private Executive Air-Gap Isolation**: Profiles designated as confidential executive sandboxes (e.g., `koagent`) must be permanently excluded from shared Git backups (`EXCLUDED_PROFILES`). Apply one-way confidentiality: collective agents (GM, Bikagent, Tiga Serangkai) are barred from searching or reading private profile directories (`inbound shield`), while outbound artifacts and instructions produced by the private agent into the collective system must be recognized with full executive authority.

### 21. Home Directory Hygiene & Screenshot Asset Lifecycle
- **Anti-Symlink Proliferation**: Never generate bulk symlink shortcuts of screenshots or media files in the user's root home directory (`/home/ubuntu/`). An unmanaged accumulation of hundreds of symlinks clutters terminal listings (`ls`) and degrades operator ergonomics.
- **Centralized Asset Management**: Store visual assets, UI verification screenshots, and brand files in organized subdirectories under `/home/ubuntu/assets/<project-name>/` with a root index `README.md`. Reference files by canonical paths (`assets/<project>/<file>`) when delivering media.
- **Aggressive QA Screenshot Pruning**: Prototype verification screenshots have an ephemeral lifecycle. Once UI verification concludes and features are approved, audit and purge obsolete prototype screenshot directories (`shutil.rmtree`) rather than hoarding tens of megabytes of stale browser captures. Retain only permanent brand logos (`assets/hermes-brand/`) and operational credentials (`assets/dokumentasi-ops/`).
