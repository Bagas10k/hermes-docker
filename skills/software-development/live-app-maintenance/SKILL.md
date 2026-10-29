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
- **Prove server-side changes on a scratch port before touching production**: a copy of the real process on an alternate port (`PORT=3199 node server.js`, background, then `curl` it) exercises the actual new route/module against the real DB read-only path while production still serves the old code. Send the negative cases there too (404 unknown id, 409 when a delete is blocked by a dependency), then kill the scratch process and confirm its listener is gone. Only after that restart production.
- **Resolve restart fears with evidence instead of declining the restart**: when a supervisor reports a suspicious cwd (`pm2 describe` shows `exec cwd` pointing at another project), do not treat that as a blocker. Grep the entrypoint for `process.cwd()` versus `__dirname`: if data/static/config paths are built from `__dirname`, cwd is irrelevant and a scratch-port boot proves it. Report the finding as a corrected assumption; only a real relative-path dependency justifies a controlled cwd fix first.
- Before any production restart, preserve rollback state and plan a readiness check; restart only the named service, then verify its listener, HTTP endpoint, and recent journal/error log. Never issue indiscriminate process kills that disrupt other daemons.
- **State held in memory survives a DB cleanup**: deleting rows directly from the database does not change what an already-running process serves. If an in-memory registry (scheduler, cache, session map) has no delete API, either add one and expose it via a route, or restart to force a reload from DB. Prefer adding the delete path: a missing removal API is a real gap that will bite again, and a route lets you test the removal on the scratch port first.

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
- **Default-Password and Login-Failure Diagnosis**:
  - Before changing credentials, query the app's local documented auth-status endpoint (for 9Router, `curl http://127.0.0.1:<port>/api/auth/status`) and inspect its actual response. `hasPassword:false` means no password is configured; it is not evidence that the user's researched password is wrong. A default-password remote-access block, a same-origin/CSRF rejection, a bad-password response, and a broken public proxy are distinct failure modes; identify which layer returns the error before acting.
  - Never use a reset-to-default endpoint as a password recovery shortcut on a remotely reachable admin app: the reset can install a known public default. Set/change a strong owner-chosen secret only through the app's supported setup flow, with owner authorization and an approved secret vault; never type, request, print, or share credentials in chat or tool output. Do not test candidate passwords. A public login hint or `hasPassword:true` does not prove which password is active or that a session works.
  - Verify in stages without exposing secrets: local auth status/login-page GET, portal or gateway response, public path, then an owner-authorized browser flow to the protected destination. Do not treat HEAD/200 or auth-status as login proof.
  - If the owner explicitly rejects managed Access and asks for code-based protection, stop recommending Access as the only answer; implement a thin, independently maintained auth gateway in front of the service rather than patching generated bundles or adding a brittle app-specific login clone. Bind the gateway to loopback, route the tunnel to it, and ensure the upstream cannot be reached around it.
  - Before choosing an outer auth scheme, inventory dashboard, management APIs, inference APIs, streaming, and WebSocket routes. Do not wrap every route in HTTP Basic Auth when the application clients need `Authorization: Bearer` for API keys; one Authorization header cannot carry both credentials. Protect admin routes with a browser session/cookie or separate admin origin, and preserve inference routes only where their own API-key authorization is verified. Never create broad unauthenticated API exceptions.
  - Put the gate before the actual request handler, and prove it covers ordinary HTTP, streaming, WebSocket upgrades, and any server-specific protocol downgrade/replay path. A gate on the normal request event alone can be bypassed by a separate upgrade or replay handler. If complete coverage cannot be shown, do not attach the public tunnel or claim protection.
  - Configure owner credentials through an owner-operated local interactive setup or approved secret manager; never use defaults, try candidate passwords, pass secrets through command arguments/environment/tool calls, or print them. Missing/malformed/unsafe credential state must fail closed. Back up the exact startup entrypoint before integration, test on an isolated port with scratch data, then restart only through its existing supervisor and verify unauthenticated denial plus authorized browser access and permitted API behavior.
  - When a browser screenshot reports a failure but a later HTTP probe succeeds, do not dismiss it as transient or tell the owner merely to reload. Reproduce the exact public URL in a real browser, inspect rendered DOM and failed resources/console, and report what that current probe proves separately from the earlier screenshot.
- **Gateway Subpath Prefix Awareness**:
  - Before adding a reverse proxy for `/prefix`, inspect the app's built/runtime base-path config, rendered HTML asset URLs, client API/WebSocket URLs, redirects, cookies, and server actions. A root-built app may emit `/_next/*`, `/api/*`, `/login`, or `/dashboard`; forwarding only `/prefix/*` will yield broken assets, wrong-origin routes, or redirects outside the prefix.
  - Prefer an upstream-supported `basePath` build or a dedicated host/subdomain when feasible. Check whether the frontend source is actually available before promising a rebuild; published standalone bundles may omit it. Do not treat editing generated Next.js manifests/runtime metadata as a successful base-path build: emitted HTML/JavaScript can retain root-relative asset/API URLs. A credible isolated proof must fetch the rendered page, enumerate its referenced assets, request those assets and the key APIs through the prefix, and inspect redirects/cookies; page HTTP 200 alone proves only that a route handler responded.
  - If retaining a subpath requires proxy rewriting, cover HTML, static assets, APIs, WebSockets/SSE, request bodies, cookies, and `Location` redirects consistently; check for namespace collisions with the host app and do not broaden public/auth bypasses just to make a route load.
  - Run integration experiments from a scratch copy on a separate loopback port with isolated home/data, never against the live app's DB or build output. Afterward stop the temporary process and verify its listener is gone before reporting the experiment complete.
  - Derive frontend HTTP/WebSocket prefixes from the actual mounted path where the app supports it (for example, `const basePath = location.pathname.startsWith('/telemetry') ? '/telemetry' : '';`). Verify the public path in a real browser, including assets, login form behavior, error rendering, and protected-route redirect; a local upstream success alone is insufficient. A public-network timeout is an unverified external boundary, not proof that DNS, tunnel, origin, or application routing is the cause.

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
- A HEAD/200 check is not enough for interactive pages. If the user flow includes login, form submit, redirect, iframe, or dashboard rendering, reproduce that flow from the public URL and verify the expected DOM text, referenced assets, and relevant API response. Do not ask the user to be the first QA pass.
- For a newly added auth gateway, separately prove fail-closed behavior before credential setup, rejection of absent/invalid credentials, authorized dashboard rendering, permitted API-key clients, and rejection of unauthorized WebSocket/stream paths. Never exercise a real user's password as a test fixture.
- If a user supplies a screenshot of an error, treat it as evidence of the reported experience, not proof of the current server state. Recheck the exact URL in a real browser and inspect resources; a successful curl can coexist with a browser-side failure, and a later render does not retroactively invalidate the screenshot.
- **No-rollback repos**: when a live app has no `.git` (or the change is outside version control), take a dated copy of every file you are about to edit BEFORE the first patch (`cp public/index.html "public/index.html.bak-$(date +%Y%m%d-%H%M%S)"`). Grep can find the file to revert, but a `git diff` claim is impossible — say so instead of implying a revert path exists. Never let an iteration-budget exhaustion leave the deliverable resting on unbacked edits.
- **Static-file edits need no restart — verify that, don't assume**: a server that mounts `express.static` (or any static file handler) serves the new HTML/CSS/JS on the next request; restarting the PM2/service process is unnecessary risk. Confirm by re-fetching the page in the browser with a cache-buster (`?v=<token>`) and asserting the new markup is present. Restart only when the edit touches server modules, routes, or schema.
- **Verify each added UI mode in both directions**: a new workspace/tab mode is not done when it renders — cycle back through every pre-existing mode and assert its container display plus the new mode's `display:none`, so the new mode cannot silently hijack the shell. Then return to the new mode for the final screenshot.

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
