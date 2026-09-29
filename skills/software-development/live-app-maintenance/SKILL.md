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
  - **Thumbnail Property Aliasing & Fallback Traps:** When a backend enricher generates lightweight WebP thumbnails, frontend templates often fall back to raw external images if property names diverge (e.g. `item.thumbnail_url` vs `item.thumb_url`). In galleries with 100+ items, this silent failure triggers massive multi-megabyte downloads from external CDNs, spiking initial page load from <300ms to >30,000ms navigation timeouts. Always alias both `thumb_url` and `thumbnail_url` in backend middleware and expose a local `media_url` (`/media/${rel_path}`) so even high-res lightbox modals never depend on fragile external CDNs.

### 18. Middleware Route Shadowing in Express Proxies
- When an Express API endpoint unexpectedly returns 404 or `Cannot GET /path` even though the route handler is correctly defined, search the entire server file for earlier middleware registrations on the same path prefix.
- An earlier `app.use('/api/x', createProxyMiddleware(...))` or broad route mounted near the top of `server.js` will intercept incoming requests before lower router declarations are reached, silently routing them to the wrong upstream target. Always place specific local routers ahead of broad catch-all proxies or remove obsolete proxy definitions.

### 19. WebGL 3D Force Graph & Interactive Physics Standards
- **Dual-Bundle Collision Avoidance:** Libraries like `3d-force-graph` bundle their own internal instance of Three.js. Loading a global `<script src="three.min.js">` alongside it creates dual-instance constructor collisions (`Timer is not a constructor`). Load peripheral 3D extensions (such as `three-spritetext`) via ESM imports (`import SpriteText from 'https://esm.sh/three-spritetext'`) inside a `<script type="module">` block to let module resolution handle shared dependencies cleanly.
- **Dynamic Spring Elasticity on Node Drag:** To give users a realistic physical spring experience when dragging nodes, call `Graph.d3ReheatSimulation()` inside `onNodeDrag`. This forces the force-directed physics engine to continuously recalculate link tensions and pull connected nodes dynamically while the user holds the pointer.
- **Artifact-Free Text Sprites:** Set `sprite.material.depthWrite = false` on all billboard text labels in 3D WebGL scenes to prevent opaque bounding boxes from occluding neighboring nodes.
- **Digit-Leading Element Selectors in Automated Testing:** In Puppeteer/Playwright test scripts, querying container elements with IDs starting with a digit (such as `#3d-graph`) throws a DOM `SyntaxError: Failed to execute 'querySelector'`. Always query via `document.getElementById('3d-graph')` or attribute selector `[id="3d-graph"]`.

### 20. Multi-Next.js Reverse Proxy Routing & Asset Collision
- **Problem**: When proxying multiple Next.js applications (e.g., admin consoles, AI routers, studio interfaces) behind a unified Express gateway, both apps serve client chunks from `/_next/static/chunks/*`. Directing `/_next` to one upstream breaks React hydration in the other with 404s, leaving the UI stuck on initial HTML fallbacks (e.g. "Loading...").
- **Rule**: Implement referer-aware routing on `/_next`:
  1. Inspect `req.headers.referer` against upstream path prefixes (e.g. `/project`, `/supabase` vs `/login`, `/dashboard`).
  2. Fall back to an asynchronous local HEAD probe against upstream loopback ports before forwarding.
  3. Ensure authentication headers (e.g. Basic Auth for admin gateways) are injected transparently on static asset proxy requests when required by upstream proxies.

### 21. Non-Blocking 3D Background Canvas & Scroll Synchronization
- **Problem**: WebGL canvas layers (Three.js, 3d-force-graph) attach internal `wheel`, `pointerdown`, and `touch-action: none` listeners. Even when set to `z-index: 0`, cursor hover over empty document margins captures gestures, causing WebGL camera zoom instead of native page scroll.
- **Rule**:
  1. Apply `pointer-events: none !important; touch-action: auto !important; user-select: none !important;` to the canvas container and all descendant scene elements in CSS.
  2. Explicitly disable and dispose camera controls in JavaScript (`Graph.controls().enabled = false; if (ctrl.dispose) ctrl.dispose();`).
  3. Drive camera angle/perspective shifts strictly via native window scroll progress (`window.scrollY / maxScroll`) using 60fps linear interpolation (LERP) in the render loop.

### 22. Deterministic Hash-Based Selection & Archetype Curation
- **Problem**: Interactive mini-apps (e.g. personality quizzes, "Cek Khodam", profile matchers) that rely solely on `Math.random()` frustrate users because re-entering the same name produces inconsistent results, while relying on dark/spooky occult tropes degrades the brand image.
- **Rule**:
  1. Use deterministic string hashing (`hash = ((hash << 5) - hash) + charCode; index = Math.abs(hash) % dbCount`) so the same input name consistently yields the same outcome while dynamically adapting across database growth.
  2. Support an optional explicit `random: true` salt parameter for "Kocok Ulang / Re-roll" actions so users can still explore the full database.
  3. Log checks into a dedicated SQLite table to provide live telemetry (total checks, top results, recent activity) in the admin dashboard.
  4. **Quirky Non-Occult Archetypes with Deep Philosophical Meaning**: When curating database content for viral personality or archetype generator apps (such as "Cek Khodam" or spirit checks), completely avoid dark, spooky, or occult tropes (no ghosts, demons, or curses). Instead, use creative, humorous, relatable everyday objects and modern archetypes (e.g., 'Kulkas 2 Pintu', 'Kompas Penunjuk Arah', 'Charger Fast Charging', 'Kunci Duplikat Cerdas') paired with deeply philosophical, reflective, and motivating life descriptions that elevate the user experience into an uplifting, insightful takeaway.

### 23. Single-Card Utility Web Apps: Viewport Centering & Zero-Fluff Doctrine
- **Problem**: Utility web tools (e.g. name generators, check tools, calculators, mini-quizzes) often suffer from awkward top-anchored positioning, verbose instructional subtitles, and unnecessary decorative counter badges that push the real content out of sight or create visual clutter.
- **Rule**:
  1. **Strict Viewport Centering**: Wrap the card container in a flex layout centered both vertically and horizontally (`body { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; }` and `.container { margin: auto; }`). The card must sit dead-center in the viewport on desktop and tablet, while naturally allowing scroll on mobile when content expands.
  2. **Zero-Fluff Hierarchy**: Omit instructional subtitles, explanatory paragraphs, and distracting footer badges unless explicitly requested by the user. Keep the visual flow direct: **Judul → Input Field → Tombol CTA → Hasil**.
  3. **Direct, Punchy Outcomes**: Format the generated output directly and concisely (e.g. `Khodam dari atas nama [X] adalah: [Y]` with badge/highlight). Keep descriptions strictly to one single, punchy, philosophical sentence (max 7-10 words, e.g. "Kepala dingin, penjaga kejernihan ide di tengah masalah.") rather than embedding multi-sentence narrative essays.
  4. **Strict Zero-Emoji**: Never inject cartoon or Unicode emojis into UI headings, buttons, or result cards. Use clean, monochrome Lucide SVG vector icons exclusively.

### 24. Knowledge Vault Graph Search Indexing (Title vs Basename)
- **Problem**: When scanning Markdown/Obsidian vaults to construct neural or 3D knowledge graphs, indexing nodes solely by their file basename causes ingested notes named with IDs/UUIDs (e.g. `7d78d371-2839-45e3-8ea8.md`) to be completely unfindable when users search by topic or title.
- **Rule**: Always extract and prioritize the frontmatter `title:` property or the first Markdown `# Heading` as the primary searchable node name and label. Retain the file path only as an internal unique identifier.

### 25. Creative 3D Web & Iridescent Fluid Shaders (Awwwards Style)
- **Problem**: Interactive 3D hero visual assets (such as fluid morphing blobs or holographic crystal models seen in award-winning digital studios) cause severe GPU thermal throttling, jerky scroll stutter, or visual distortion if built without proper math bounds.
- **Rule**:
  1. **Vertex Shader Deformation**: Use 3D Simplex noise displacement on high-detail sphere geometry (`IcosahedronGeometry(radius, 64)`). Always recompute surface normals analytically or via finite differences so specular reflections do not break.
  2. **Fragment Shader Optics**: Compute Schlick's Fresnel approximation ($F(\theta) = F_0 + (1-F_0)(1-\cos\theta)^p$) and generate iridescent/holographic color shifts algorithmically using cosine palettes ($C = a + b \cdot \cos(2\pi(c \cdot t + d))$) rather than heavy bitmap textures.
  3. **Performance Limits**: Enforce strict DPR clamping (`Math.min(window.devicePixelRatio, 2.0)`), pre-allocate all math vectors outside the render loop (zero GC allocation per frame), and pause the animation loop completely on `document.hidden` to maintain 60 FPS and 0% idle GPU load.

### 26. Interactive Design DNA & Client-Side Canvas Palette Extraction
- **Problem**: In visual design and reference galleries, users cannot take immediate action on design assets because they only see static pixels without actionable design tokens (color palettes, contrast ratios, and implementation CSS variables). Forcing server-side computer vision or external API calls creates latency and high CPU load.
- **Rule**:
  1. **Zero-CORS Client-Side Quantization**: Serve assets and thumbnails from the same domain (`/media/` and `/thumb/`). In browser JS, draw images to an offscreen 48x48 Canvas 2D and quantize RGB channels to 4-bit levels (16 bins).
  2. **Distinct Color Clustering**: Filter out near-blacks and near-whites unless dominant. Select 5 distinct colors using Euclidean distance thresholds ($\Delta E^2 > 1600$) to map functional roles: Canvas Background, Surface Card, Primary Brand Accent, Secondary Accent, and Contrast Text/Border.
  3. **WCAG Relative Luminance**: Compute $L = (0.2126R + 0.7152G + 0.0722B)/255$ on each swatch to dynamically set high-contrast white or dark text on interactive color chips.
  4. **Instant Token Export**: Provide 1-click clipboard actions to generate clean `:root { ... }` CSS variables and Tailwind theme color configuration objects.
  5. **Floating Multi-Item Comparison Dock**: Provide a sticky dock allowing users to select 2 to 4 designs and compare them in a parallel split-screen Reference Board with synchronized palette rows and layout specs.

### 27. Action Button Dimension Collision in Component Evolution
- **Problem**: In existing CSS design systems, utility action classes (such as `.btn-neo-action`) often declare rigid square dimensions (`width: 32px; height: 32px;`) optimized for single icons. Reusing these classes for new text-labeled buttons (e.g. "Salin :root CSS Variables") forces the container to shrink, causing severe text wrapping, vertical clipping, or multi-line stacking.
- **Rule**: Never overload icon-only square utility classes on elements containing text labels. Create dedicated, self-contained action classes (e.g., `.btn-dna-token-action`) with `width: auto; padding: 8px 14px; white-space: nowrap; font-size: ...;` to guarantee horizontal text integrity across all viewport widths.

### 28. DOM Partial Node Replacement Dynamic Sub-Component Rehydration
- **Problem**: When updating partial DOM nodes in place via template replacement (e.g., `card.replaceWith(temp.firstElementChild)` or rewriting `innerHTML`), asynchronous or post-render dynamic hydration (such as canvas palette extraction, tooltips, intersection observers, or event listeners) attached to children of the old node is completely destroyed, leaving newly inserted nodes stuck on unhydrated placeholder states (e.g. "DNA...").
- **Rule**:
  1. Whenever a component performs `element.replaceWith(...)` or rewrites a container's `innerHTML`, explicitly re-invoke the component's asynchronous hydration pipeline (e.g., `loadPaletteForCard(item)`) on the newly inserted node.
  2. Cache asynchronous extraction results in a fast in-memory store (e.g. `Map`) so post-replacement re-hydration resolves synchronously in 0ms without redundant network or canvas computation.
  3. Re-observe newly inserted DOM elements in relevant `IntersectionObserver` instances to maintain entrance transitions and lazy loading.

### 29. Sub-Path Mounted Single Page Apps & API Privacy Boundary Routing
- **Problem**: When a single-page monitoring dashboard, IDE, or studio portal is mounted under a public sub-path (e.g. `/kanvas`, `/organisasi/aoms.html`), the initial HTML shell loads, but dynamic widgets stay permanently stuck on loading spinners or crash with `Galat jaringan: Unexpected token '<', "<!DOCTYPE "... is not valid JSON`.
- **Mechanism**:
  1. **Security Boundary & Gateway Interception**: Edge tunnels/reverse proxies route sub-path traffic (e.g. `/kanvas/*` and `/api/kanvas/*`) to the dedicated application port, but route root `/api/*` to the main gateway/dashboard. Client frontend code executing un-prefixed root-relative requests (e.g. hardcoded `fetch('/api/fs/tree')`) escapes the sub-path proxy scope. The root gateway intercepts the request and, because it requires session authentication, returns an HTML 401 or login page (`<!DOCTYPE html>...`). Calling `res.json()` on that HTML string triggers the JSON parse syntax error.
  2. **Express Mount Prefix Stripping**: Mounting reverse proxy middleware via `app.use(['/api/aoms', '/aoms'], createProxyMiddleware(...))` strips the mounted prefix by default, causing the upstream daemon to receive `GET /traces` instead of `GET /api/aoms/traces`, triggering `404 Cannot GET /traces`.
- **Rule & Dual-Layer Implementation**:
  1. **Mandatory Dynamic Base in Frontend (`API_BASE`)**:
     Never hardcode root-relative `/api/...` in frontend JavaScript. Always derive the prefix dynamically:
     ```javascript
     const API_BASE = window.location.pathname.startsWith('/kanvas') ? '/api/kanvas' : '/api';
     const res = await fetch(`${API_BASE}/fs/tree?path=${encodeURIComponent(path)}`);
     ```
     Ensure every single `fetch()` and WebSocket call strictly prepends `${API_BASE}`.
  2. **Transparent URL Rewrite in Upstream Backend (`server.js`)**:
     In the upstream Express server, register URL rewrite middleware before all route definitions to normalize all potential sub-path permutations (`/api/kanvas` AND `/kanvas/api`) back to the canonical `/api` prefix:
     ```javascript
     app.use((req, res, next) => {
       if (req.url.startsWith('/api/kanvas')) req.url = req.url.replace('/api/kanvas', '/api');
       if (req.url.startsWith('/kanvas/api')) req.url = req.url.replace('/kanvas/api', '/api');
       next();
     });
     ```
  3. **Privacy Boundary Whitelist**: In gateway privacy boundaries, explicitly register the subsystem's API pattern (e.g., `/api/aoms(?:\/.*)?`) in the public route whitelist.
  4. **Express Reverse Proxy Functional Rewriting**: In Express reverse proxies, use functional path rewriting (`pathRewrite: (p) => '/api/aoms' + (p.startsWith('/') ? p : '/' + p)`) to guarantee the upstream daemon receives the exact pathname it expects.
  5. **Direct Remote Verification**: Always probe the public tunnel URL (`curl -sI https://<public-domain>/api/kanvas/<endpoint>`) and run a real headless browser session to assert that dynamic dropdowns, file trees, and asynchronous tables populate with live data rather than throwing JSON parse errors or remaining stuck on loading spinners.

### 30. Interactive Navigation Rails & Feedback Synchronization in Single-Page Portals
- **Problem**: In dense operational dashboards, sidebar navigation items and tabs often display styled badges (e.g., `DAG`, `DIFF`, `AQS`, `98.2%`) and active indicators, but clicking them fails to navigate, leaves the active pill stuck on the first menu, or throws `ReferenceError` due to missing stub functions (e.g. `filterBottomTable is not defined`). Users perceive the dashboard as broken or unresponsive.
- **Rule**:
  1. **Centralized Navigation Dispatcher**: Unify all sidebar actions under a single function (`navTo(section)`). When a link is clicked, synchronously transfer the `.active` class across navigation items so visual state instantly reflects user action.
  2. **Transient Glow Feedback for In-Page Anchors**: When navigating to in-page containers (e.g., scrolling to DAG Graph or telemetry tables), apply a brief CSS transition glow (e.g. `box-shadow: 0 0 25px rgba(56, 189, 248, 0.4); border-color: var(--color-cyan)`) that clears after 1.5 seconds so the user immediately spots the target panel.
  3. **Functional Filter Binding**: Forensic actions (such as "Failure & Recovery") must execute concrete filtering logic (e.g. isolating table rows containing `FAILED` or displaying a verified zero-failure banner) rather than being dead links.
  4. **Automated Click-Through QA**: Verify every sidebar link and modal opener with an automated Puppeteer script that clicks each element sequentially and asserts zero `pageerror` events.

### 31. Chat Gateway Progress Formatting & Agent Attribution
- **Problem**: Default messaging platform adapters (e.g. Telegram stream consumers) emit raw, low-level shell execution lines (e.g., `💻 terminal`, `Shell: curl ...`, `Shell: node ...`) in progress bubbles, obscuring multi-agent roles and causing confusion about which sub-agent is active.
- **Rule**:
  1. Intercept the gateway's progress builder (`run_turn_runner.py` / `adapter.py`) to map tool invocations to explicit organizational roles:
     - Shell execution, file editing, patching (`terminal`, `patch`, `write_file`) → **`⚡ Si Eksekutor`**
     - Reading files, codebase inspection, search (`read_file`, `search_files`, `web_search`) → **`🧠 Si Pintar`**
     - Visual inspection, screenshots, exploratory QA (`vision_analyze`, `dogfood`) → **`🛡️ Si Pengawas`**
     - Sub-agent delegation, planning, user queries (`delegate_task`, `clarify`, `memory`) → **`👑 General Manager`**
  2. Format progress lines with clean role prefixes (e.g. `⚡ Si Eksekutor • 💻 terminal`) so users monitoring chat execution immediately know which component of the system is actively working.

### 32. High-Frequency Real-Time Telemetry & SSE Proxying Pipeline
- **Problem**: When proxying high-frequency Server-Sent Events (SSE) telemetry streams (e.g., 100ms system snapshots) through Express backends, client requests hang indefinitely or edge proxies return 524 timeouts. Furthermore, testing these streams with headless browsers hangs forever on navigation.
- **Rules**:
  1. **Explicit Request Dispatch in Node.js Client Proxying**: When creating an outbound HTTP stream via `http.request({ ... }, (proxyRes) => proxyRes.pipe(res))`, the request is **never dispatched** until `proxyReq.end()` is explicitly called. Prefer `http.get(...)` for GET stream proxying to automatically invoke `.end()`.
  2. **Anti-Buffering Edge Headers**: In the SSE response header, explicitly set:
     - `'Content-Type': 'text/event-stream'`
     - `'Cache-Control': 'no-cache, no-transform'`
     - `'Connection': 'keep-alive'`
     - `'X-Accel-Buffering': 'no'` (instructs Nginx/Cloudflare not to buffer chunked stream events).
     Call `res.flushHeaders()` immediately before piping chunks.
  3. **Headless Browser Testing (`waitUntil` Trap)**: In Puppeteer/Playwright tests against pages containing active `EventSource` or persistent stream connections, **never use `waitUntil: 'networkidle2'` or `'networkidle0'`**; persistent stream chunks guarantee the network is never idle, causing a guaranteed 30s navigation timeout. Always use `{ waitUntil: 'domcontentloaded' }` followed by an explicit `setTimeout` or element selector wait.
  4. **Multi-Transport Fallback**: Always pair real-time Socket.IO broadcasts with direct `EventSource` SSE streaming and a graceful HTTP polling fallback (`/api/metrics` every 200-300ms) in case WebSocket upgrades or SSE connections drop over edge tunnels.
  5. **State Mutability Guard**: Never declare mutable state flags (e.g. `is_busy`, `active_agent`) with `const` in event-driven snapshot getters. An uncaught `TypeError: Assignment to constant variable` inside WebSocket connection or tick events crashes the Node process and triggers cascading PM2 restart loops.

### 33. Dense TUI Cockpit Tables & Terminal Log Stream Layouts
- **Problem**: In high-density developer cockpits or terminal dashboards, wide table payloads blow out container boundaries, and terminal log streams suffer from clipped top/bottom lines or inverted scrolling.
- **Rules**:
  1. **Mandatory `table-layout: fixed` for Text Truncation**: Applying `white-space: nowrap; overflow: hidden; text-overflow: ellipsis;` to table cells (`<td>`) **has no effect** in standard HTML tables unless the table element explicitly has `table-layout: fixed; width: 100%;`. Without this, long file paths or JSON arguments stretch the table horizontally, breaking panel grids.
  2. **Strict Column Count Parity**: Ensure the count and width percentages of `<th>` elements in `<thead>` strictly match the number of `<td>` cells dynamically emitted by JavaScript render functions. A mismatch causes trailing columns to escape headers and clip abruptly against panel edges.
  3. **Flexbox `column-reverse` Top Clipping Trap**: In scrollable terminal stream boxes (`overflow-y: auto;`), setting `display: flex; flex-direction: column-reverse;` causes browser layout engines to ignore or clip `padding-top` when overflowing, cutting the top characters of log lines in half. Use standard `flex-direction: column;` with prepending (`streamBox.insertBefore(newLine, streamBox.firstChild)` for newest-first) and generous container padding (`padding: 10px 12px; box-sizing: border-box; gap: 2px;`) to guarantee pristine vertical line visibility.

### 34. Stutter-Free 60 FPS Real-Time HUDs & Decoupled Telemetry Pipelines
- **Problem**: Real-time dashboards (telemetry HUDs, audio VU meters, core activity monitors) stutter, drop frames, or freeze periodically every second ("patah-patah setiap detik") despite low reported CPU load.
- **Root Causes & Mechanisms**:
  1. **Synchronous Server-Side Event Loop Freezing**: Calling synchronous CLI commands (e.g. `execSync('pm2 jlist')` taking ~350-400ms, or `execSync('free -b')` taking ~35ms) inside short recurring intervals (e.g. `setInterval(..., 1000)`) freezes the single-threaded Node.js event loop for 40%+ of every second. High-frequency SSE/WebSocket ticks buffer during the freeze and fire all at once in bursts, causing periodic stutter.
  2. **Collector Daemon Sampling Loop Spikes (Python/Host Level)**: Calling `subprocess.run(['ps', ...])` (~60ms) or querying disk databases (`sqlite3.connect`) synchronously inside a 100ms metric collector loop leaves only a tiny margin (<40ms) before missing the interval tick, causing periodic latency spikes and jittered frame delivery.
  3. **Heavy Inspection / Execution Graph Ingestion**: Rebuilding DAG graphs or querying historical message tables synchronously on every telemetry tick or API request creates 80–100ms pauses and SQLite lock contention.
  4. **Direct DOM Mutation in Ingestion Handlers**: Directly updating DOM text/styles in `EventSource.onmessage` or WebSocket callbacks whenever 100ms packets arrive triggers layout thrashing and jarring step-changes.
  5. **CSS Transition Conflict with Frame Animations**: Applying `transition: height 70ms ease-out;` in CSS on elements driven by JavaScript `requestAnimationFrame` creates an interpolation conflict between the CSS transition engine and JS per-frame updates, resulting in visual jitter.
  6. **Multi-Channel Split-Brain**: Streaming identical high-frequency metrics simultaneously over both SSE and WebSocket causes double-parsing and out-of-order DOM overwrites.
  7. **Redundant Client-Side Polling**: Running separate `setInterval(fetchStats, 10000)` polling loops when the live stream already supplies metrics triggers unnecessary network overhead and layout recalculations.
- **Rules & End-to-End Non-Blocking Architecture**:
  1. **Zero Synchronous CLI Calls in Server Loops**: Never run `execSync` in server intervals. Read `/proc/meminfo` directly via `fs.readFileSync` for instant kernel memory stats (0.1ms vs 35ms shell invocation). Offload heavy commands (`pm2 jlist`) to an asynchronous background worker (`exec`) updating an in-memory cache at a relaxed cadence (e.g. 5-10s). Use asynchronous `fs.readFile` instead of `fs.readFileSync` on API endpoints (e.g. cronjob listings) to prevent blocking request cycles.
  2. **Daemon Collector Decoupling (Threaded Workers)**: In 100ms collector daemons, restrict the hot sampling path exclusively to Linux `/proc` pseudo-files (`/proc/stat`, `/proc/net/dev`, `/proc/diskstats`, `/proc/meminfo`, `statvfs`) which resolve in ~0.3ms. Move slow external operations (`ps -eo` process tables, SQLite database checks, JSON file sweeps) into a dedicated background worker thread (`threading.Thread(target=..., daemon=True)`) that updates thread-safe cache variables every 1.2–2.0 seconds.
  3. **Short-TTL Query Caching for Execution DAGs & State**: Cache heavy DAG calculations and database inspection snapshots in memory with a short TTL (1.0–1.5s). Pass pre-computed graphs directly to downstream inspectors rather than recalculating them twice in the same telemetry tick, reducing repeated query latency to 0ms.
  4. **In-Memory File State with mtime Invalidation**: For organizational state or configuration files, store the parsed object in memory. Validate `fs.statSync(path).mtimeMs` before re-reading from disk to avoid redundant file I/O on every API request.
  5. **Decouple Ingestion from Rendering (Dual-Phase Engine)**:
     - **Phase 1 (Ingestion)**: The 100ms SSE listener only writes raw values into an in-memory `targetState` object. Perform zero DOM reads or writes in the stream handler.
     - **Phase 2 (60 FPS Render Loop)**: Drive DOM updates via `requestAnimationFrame(frame)`. Pre-cache all DOM element references once at startup.
  6. **Exponential Moving Average (EMA/Lerp) Smoothing**: Smooth numeric targets inside the 60 FPS loop using `current += (target - current) * Math.min(1, dt * alpha)` (where `dt` is delta time in seconds, `alpha = 8-12`). This produces silky, analog-grade meter motion instead of jerky stepping.
  7. **Remove CSS Transitions on Frame-Animated Elements**: Strip CSS `transition` properties from equalizer bars and VU meters animated via JS `requestAnimationFrame`. Use `will-change: height;` to promote elements to hardware-accelerated compositor layers without transition lag.
  8. **Single Stream Authority & Zero Redundant Polling**: Designate SSE as the sole delivery channel for high-frequency (100ms) telemetry streams. Remove client-side polling intervals (`fetchSystemStats`) when the 60 FPS loop already renders current metrics smoothly.

### 35. Live Sports Streaming Hubs & Match Center Embed Integration
- **Problem**: Deploying public live match viewing hubs ("nobar bola yang bisa di-share untuk match lainnya") requires responsive video players, multi-source redundancy, real-time match switching, and direct shareable deep links without incurring massive video bandwidth bills or getting blocked by security boundaries.
- **Rules & Implementation Protocol**:
  1. **Dual-Layer Privacy Boundary & Route Registration**:
     - When mounting new public frontend tools (e.g. `/nobar`, `/nobar.html`) and their supporting APIs (`/api/nobar`), immediately register the route patterns in both the Express route table AND the security boundary whitelist (`isPublic(p)` regex in `privacy-boundary.js`). Failing to register in the security boundary returns `401 Unauthorized` on API fetches before reaching the route handler.
  2. **In-Memory Caching API Proxy**:
     - Never allow the client browser to query third-party sports stream providers directly.
     - Front external aggregators with an Express router (`/api/nobar/matches`, `/api/nobar/detail/:id`) backed by in-memory TTL caching (45s for match lists, 30s for stream details) with an `AbortController` timeout (5–6s). This eliminates upstream rate limits and guarantees sub-2ms response times for all clients.
  3. **Iframe Permissions Protocol & The Sandbox Trap**:
     - Sports stream embed iframes require explicit capabilities: `allow="autoplay; fullscreen; encrypted-media; picture-in-picture"`, `allowfullscreen="true"`, and `referrerpolicy="no-referrer"`.
     - **The Sandbox Danger**: NEVER add the `sandbox` attribute to sports video iframes. Sandboxing breaks cross-origin player scripts, DRM handshakes, and anti-bot verification tokens, causing the player to remain stuck on a blank black screen.
  4. **The `display: none` / `frame.onload` Deadlock Trap**:
     - Never hide the video iframe with `style="display: none"` while waiting for `frame.onload` to reveal it. Third-party stream players often load auxiliary ad trackers, analytics, or popups that client adblockers or network filters drop, preventing `onload` from ever resolving. The user is trapped staring at an infinite loading spinner.
     - Protocol: Render the iframe immediately visible (`display: block; z-index: 2;`). Make the loading placeholder overlay non-blocking (`pointer-events: none; z-index: 1;`) and dismiss it unconditionally after 600–800ms so the user sees the native HTML5/JW player and play button immediately.
  5. **Upstream Feed Health & Priority Sorting**:
     - Third-party aggregators routinely return 5–10 mirrors where several feeds are dead (returning HTTP 404 or 500 on their `.m3u8` playlists) mid-match.
     - If the default selected Server 1 (index 0) points to a dead feed, the player loads a blank black screen with an unresponsive play button, misleading users into believing the entire platform is broken.
     - Protocol: In backend router enrichment, sort and prioritize verified high-stability server feeds (e.g. official network mirrors, ESPN+, LaLiga TV) to index 0, demoting flaky secondary mirrors.
  6. **Multi-Source Redundancy & Server Switcher**:
     - Always parse and expose all stream sources returned by upstream providers as explicit server buttons (`[S1] ESPN HD`, `[S2] DAZN HD`, `[S3] LaLiga TV HD`). When one source buffers or drops, users can instantly switch without reloading the page. Provide an in-page `[RELOAD STREAM]` button that resets the iframe `src` to clear player buffer stalls.
  7. **Direct Pop-Out Fail-Safe for Mobile & Strict Browsers**:
     - Cross-origin iframes on mobile devices (iOS Safari / Android Chrome) frequently restrict autoplay with audio and trigger popup blockers on initial user clicks.
     - Always provide a prominent `[BUKA TAB BARU]` button calling `window.open(streamUrl, '_blank')`. This gives users an instant 1-tap escape hatch to watch the stream in a native browser window without iframe security or sandbox constraints.
  8. **Stateful Deep-Linking & Shareability**:
     - Sync the currently viewed match to the URL query parameter using `window.history.replaceState({}, '', '?match=' + matchId)`.
     - On page boot, inspect `window.location.search` for `?match=` or `?id=` to auto-load the shared match. If no match is specified, auto-select the headline match (e.g. Real Madrid or highest-priority match).
     - Include a 1-click `[BAGIKAN LINK]` button that writes the active full URL to the clipboard with toast feedback.
  9. Zero-Emoji Compliance & Cinema Aesthetics:
     - Maintain strict 100% compliance with the Zero-Emoji rule across all match cards, status pills, and headers. Use clean monospace ASCII brackets (`[LIVE]`, `[HD]`, `[MATCH CENTER]`, `[S1]`) and SVG icons exclusively.
     - Implement a Theater/Cinema Mode toggle (`[MODE BIOSKOP]`) that collapses layout constraints to full viewport width for immersive viewing on desktop and mobile.
  10. Popunder / Clickjack Ad Hijack Mitigation (Shopee/Affiliate Redirects):
     - **Mechanism**: Free sports stream embeds (`embed.st`, `streamapi.cc`, etc.) monetize by injecting popunder ad networks (`aclib.runPop`, transparent `ad-overlay` DOM layers). On the user's FIRST click/tap on the player or play button, the ad script executes `window.open` to launch an advertising redirect chain (which in Indonesia/Southeast Asia commonly resolves to Shopee app/affiliate links or betting sites). On mobile devices, the browser switches active focus to the new Shopee tab, making users think clicking play failed and only opened an advertisement.
     - **The Sandbox Trap**: Do NOT attempt to block these popups by adding `sandbox` without `allow-popups` to the `<iframe>`. Upstream embed player scripts actively detect iframe sandboxing (inspecting `window.frameElement.hasAttribute('sandbox')`, `"null" === String(window.origin)`, or checking failed plugin initialization like base64 PDF loads). When sandboxed, the embed script aborts entirely with an explicit blocking screen: `"Remove sandbox attributes on the iframe tag"`.
     - **Resolution & UX Protocol**:
       1. **Anti-Redirect Guard on Parent Window**: Attach `window.addEventListener('beforeunload', (e) => { if (!window.allowPageExit) { e.preventDefault(); e.returnValue = 'Yakin ingin meninggalkan siaran langsung?'; } })` to ensure the host page itself is never silently redirected by malicious top-level navigation scripts.
       2. **Smart Focus Shield (Dynamic Tab Focus Tracker)**:
          - Track ad tab activation automatically in frontend JavaScript:
            ```javascript
            let adTabTriggered = false;
            window.addEventListener('blur', () => { adTabTriggered = true; });
            window.addEventListener('focus', () => {
              if (adTabTriggered) {
                // Dynamically transform UI banner to bright green [STATUS: TAB IKLAN SUDAH DIBERSIHKAN ✓]
                // and instruct user to click PLAY now for uninterrupted playback.
                showToast('Iklan dibersihkan! Tekan tombol Play di video.');
              }
            });
            ```
          - This eliminates user confusion after returning from a closed Shopee/popunder tab by providing instant positive feedback that the ad stage is cleared.
       3. **In-App 1-Click DNS Shield Guide (`[ANTI-IKLAN 100%]` Modal)**:
          - Provide an explicit control bar button that opens an in-page modal detailing the 10-second OS-level Private DNS trick:
            - Android: Settings -> Connections -> Private DNS -> `dns.adguard-dns.com`.
            - iOS / PC: Private DNS profile or Brave / uBlock Origin.
          - Include a 1-click clipboard copy button for `dns.adguard-dns.com`. Network-level DNS filtering blocks all popunders and affiliate redirects 100% at the socket layer without breaking DRM tokens or triggering sandbox detection screens.
       4. **Touch Shield Architecture (Combating Persistent 2nd+ Click Popunders)**:
          - **Problem**: Even if the initial play click succeeds or the first popup is dismissed, free stream providers attach recurring click listeners inside the iframe. On the 2nd click and subsequent taps (e.g., trying to unmute, pause, seek, or click the player's native fullscreen icon), the ad script continuously fires new Shopee / affiliate tabs.
          - **Mechanism**: Cross-origin parent pages cannot remove click listeners inside an external iframe, but they CAN intercept clicks before they reach the iframe.
          - **Resolution**:
            - Once stream playback begins (or 4–5s after initial play interaction / window refocus), automatically engage a transparent DOM overlay (`touch-shield`, `position: absolute; inset: 0; z-index: 20; background: transparent;`) covering the video viewport.
            - The overlay swallows all user clicks (`e.preventDefault()`, `e.stopPropagation()`), completely preventing the iframe's ad scripts from ever seeing click events. Subsequent clicks drop from infinite popups to **0 popups**.
            - Place a floating HUD with clean parent-controlled actions over the video canvas:
              - **Native Fullscreen Button**: Calls `viewportElement.requestFullscreen()`, giving users flawless fullscreen video without clicking the iframe's trapped fullscreen button.
              - **Unlock / Lock Toggle (`[BUKA KONTROL] / [KUNCI IKLAN]`)**: Allows users to lower the shield if they need to access native audio volume controls, and re-lock it immediately.
       5. **Mobile OEM Browser Forced Sandboxing Trap (Vivo / Xiaomi Browser "Remove sandbox")**:
          - **Problem**: Even when the parent web app does NOT specify a `sandbox` attribute on the `<iframe>`, users on certain Android OEM browsers (notably `VivoBrowser` / `MintBrowser`) encounter a red blocking screen: `"Remove sandbox attributes on the iframe tag"` accompanied by the client's User-Agent.
          - **Mechanism**: The mobile OEM browser's built-in security layer automatically imposes sandbox restrictions (blocking popups and top-navigation) on third-party iframe embeds loading ad-heavy scripts. The upstream stream's anti-sandbox detection script misidentifies this browser-level restriction as a developer-configured `sandbox` attribute and aborts video playback.
          - **Resolution**:
            - Emphasize a prominent, high-contrast escape button directly beneath the video canvas: **`[BUKA TAB BARU (BEBAS ERROR)]`** invoking `window.open(src.embedUrl, '_blank')`.
            - In a top-level browser tab, the video URL runs as a primary window rather than an embedded frame. Mobile OEM browsers do not apply iframe sandbox policies to top-level tabs, enabling immediate, smooth HD playback.
            - Document clear fallback guidance in the in-app guide banner recommending users switch to Google Chrome or Brave if their default device browser enforces restrictive iframe sandboxing.

### 36. Dual-Layer Auto-Device Adaptation & Viewport Routing
- **Problem**: In complex monitoring dashboards and operational cockpits (e.g. RADAR/AOMS), opening a desktop-optimized multi-pane TUI layout on a mobile phone breaks readability, while forcing users to memorize separate URLs (`/mobile` vs `/radar`) leads to repeated frustration when switching devices.
- **Rules & Protocol**:
  1. **Dual-Layer Auto-Routing**:
     - **Server/Reverse Proxy Layer**: Inspect incoming `req.headers['user-agent']`. If matched against mobile patterns (`/mobile|android|iphone|ipad|ipod|blackberry/i`) and no explicit `?view=desktop` parameter is present, redirect immediately to the mobile route (`/organisasi/mobile.html`).
     - **Client-Side Immediate Viewport Fallback**: Place a zero-latency script in `<head>` before CSS evaluation:
       ```javascript
       const isMobile = /Android|iPhone|iPod/i.test(navigator.userAgent) || window.innerWidth < 768;
       const forceDesktop = localStorage.getItem('radar_view_mode') === 'desktop';
       if (isMobile && !location.search.includes('view=desktop') && !forceDesktop) {
         window.location.replace('/organisasi/mobile.html');
       }
       ```
  2. **Loop-Free Persistent Overrides**:
     - Provide explicit toggle buttons (`[DESKTOP COCKPIT]` on mobile, `[MOBILE]` on desktop).
     - Clicking the override sets `localStorage.setItem('radar_view_mode', 'desktop')` and navigates with `?view=desktop`. The router and client script honor `localStorage` to prevent infinite redirect loops.
  3. **Vertical Viewport Bounds for Laptops (1366x768 & 1280x800)**:
     - Fullscreen terminal layouts locking `html, body { height: 100vh; overflow: hidden; }` crush lower panels on standard laptop displays.
     - Enforce `@media (max-height: 860px) { html, body { height: auto !important; min-height: 100vh; overflow-y: auto !important; } .cockpit-container { height: auto !important; min-height: 100vh; } }` so laptops scroll smoothly without clipping panel headers or action buttons.

### 37. Isolated Per-Job Inference Model Pinning for Autonomous Tasks
- **Problem**: Users want to benchmark or assign specialized AI models (e.g., deep math reasoning, low-level systems architecture, high-throughput exploratory search) specifically for background tasks or autonomous research cycles, without corrupting or resetting the inference model used by primary interactive conversational bots.
- **Rules & Protocol**:
  1. **Hermes Native Per-Job Model Pinning with Mandatory Provider Pairing**:
     - Never alter the global `config.yaml` or inject process-wide environment variables to change a model for a specific task.
     - Use Hermes' per-job cron model override with paired provider:
       `hermes cron edit <job_id> --model "<model_name>" --provider "custom:lk"`
     - **Critical Authentication & Silent Fallback Pitfall**: When targeting models hosted on authenticated proxies (like local 9Router or OpenAI-compatible gateways), ALWAYS supply `--provider "custom:lk"` alongside `--model`. Omitting `--provider` causes Hermes scheduler to fall back to the generic `custom` profile which sends `"no-key-required"`. 9Router rejects this with `HTTP 401: Invalid API key`, triggering Hermes's silent failover to `fallback_providers` (running an unintended model without throwing an explicit error).
     - Clear the pin to revert to fleet default:
       `hermes cron edit <job_id> --model "" --provider ""`
  2. **Exposing Model Switching via API**:
     - Implement REST endpoints (`GET /api/.../models` and `POST /api/.../model`) that update task metadata in `state.json` and invoke `hermes cron edit <job_id> --model "<model>"` via `child_process.exec`.
     - Sanitize model input strings against strict allowlists (`/^[a-zA-Z0-9_\-\/\.:]+$/`) to prevent shell injection.
  3. **Multi-Interface UI Synchronization**:
     - Expose the model selector directly in both Desktop Mission Control modals and Mobile dashboard cards.
     - Always display a clear isolation badge (e.g. `*Khusus siklus riset berlangsung. Chat bot utama tidak berubah.`) to reassure the user that core chat sessions remain stable.

### 38. Mobile Studio & Single-Page Canvas Ergonometrics (Zero Feature Pruning & Virtual Keyboard Bounds)
- **Problem**: When adapting a complex desktop studio/canvas (editor, AI discussion stream, scratchpad, transformation templates, file import/export) to mobile viewports, naive responsive layouts crush the screen with multi-tiered button bars, break virtual keyboard scrolling, or prune features to make space.
- **Rules & Protocol**:
  1. **Dynamic Viewport Height (`100dvh`) & Virtual Keyboard Anti-Distortion**:
     - Never use rigid `100vh` on mobile web apps with text inputs. The mobile virtual keyboard resizing the window triggers layout shifts, clipped textareas, and scroll bounce.
     - Pair `<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover, interactive-widget=resizes-content">` with root CSS `display: flex; flex-direction: column; height: 100dvh; overflow: hidden;`.
     - Set `-webkit-overflow-scrolling: touch; overscroll-behavior-y: contain;` on inner scrollable panes to eliminate parent window scroll bounce and rubber-banding.
  2. **Chat-Driven Intent Auto-Routing vs Obstructive Mobile Dropdowns**:
     - Do not force multi-tier actions or transformations into native `<select>` dropdowns on mobile. Tapping a `<select>` triggers fullscreen native OS wheel/radio picker popups that completely cover the workspace.
     - **Protocol**: Prioritize **Natural Language Intent Auto-Detection** directly through the chat/command input. Accompany it with a single, sleek horizontal row of 1-tap quick chips (`[+ PRD]`, `[+ Web Mini]`, `[+ Plan]`, `[+ Tugas]`) positioned right above the input field. Tapping a chip immediately populates and dispatches the instruction with 0 modal popups.

  3. **Explicit Action Labels & Flex-Wrap Ergonomics**:
     - Cryptic 3-4 letter button abbreviations (`[CHK]`, `[TBL]`, `[CODE]`, `[QTE]`) confuse users and degrade readability.
     - **Protocol**: Use explicit, instantly recognizable Indonesian or English labels (`[Tebal]`, `[Miring]`, `[Judul]`, `[Subjudul]`, `[Poin •]`, `[Checklist]`, `[Tabel]`, `[Kode]`, `[Kutipan]`).
     - Decouple text statistics badges from the formatting bar. Apply `flex-wrap: wrap; gap: 4px;` to the toolbar container so buttons naturally flow into compact rows on small viewports without horizontal clipping or scroll overflow.
  4. **Multi-Source File Import Pipeline (Local-First FileReader)**:
     - For web studios accepting external files (`.md`, `.txt`, `.json`), pair a hidden `<input type="file">` with window drag-and-drop event listeners (`e.dataTransfer.files`).
     - Process via browser `FileReader.readAsText()` into an interactive confirmation modal offering 3 explicit placement paths: `[1. BUAT CATATAN BARU]`, `[2. GANTIKAN DRAF INI]`, or `[3. SAMBUNGKAN KE AKHIR DRAF]`. This eliminates server upload latency and works offline.
  5. **Decoupling Artifact Generation from Authoring Utilities (The Ambiguous `[AKSI]` Trap)**:
     - Merging export options (APK container, live web sandbox, markdown export, PDF) and editing utilities (vault sync, templates, zen mode) into a single generic `[AKSI ▼]` dropdown confuses users because the mental models for "taking work outside" and "improving the work inside" are orthogonal.
     - Decouple into two distinct, predictable menus:
       * `[EKSPOR ▼]`: Purely for exporting or packaging documents (.md, HTML, PDF, APK container).
       * `[ALAT ▼]`: Purely for editor-enhancing utilities (templates, vault sync, import, zen focus).
     - Place ultra-frequent actions (e.g. `[UNDUH .MD]` or `[AUDIT AI]`) directly on the editor toolbar as instant 1-tap buttons to eliminate unnecessary dropdown traversal.

### 39. Pre-Transform Database Flush & Action Identifier Consistency
- **Problem**: When triggering asynchronous streaming transformations (e.g., AI PRD/Action Plan generation) immediately after typing in draft editors, active debounced auto-save timers haven't written to SQLite yet. The backend receives stale or unpersisted document state, causing the SSE stream to crash or abort mid-sentence with generic errors (e.g. "Galat saat transformasi dokumen").
- **Rule**:
  1. Always execute an explicit synchronous persistence flush (`await performSave()`) before dispatching streaming AI calls to guarantee canonical database state.
  2. Normalize action parameter aliases (e.g. `critic` and `critique`) across frontend select options and backend routing switch/if branches to prevent unhandled action drop-offs.

### 40. Per-Document Conversation Ledger & In-Place Thread Purging
- **Problem**: In collaborative AI studios, chat histories that are un-scoped or global across documents cause cross-document context pollution and runaway token accumulation.
- **Rule**:
  1. Scope conversation rows strictly by document ID (`WHERE note_id = ? ORDER BY id ASC`).
  2. Provide a dedicated endpoint and UI control (`DELETE /api/notes/:id/conversations`) allowing users to reset the conversation thread in-place without deleting the parent document.

### 41. Node.js Express SSE Lifecycle & Client Abort Pitfall (`res.on('close')` vs `req.on('close')`)
- **Problem**: When adding client abort/stop buttons to streaming SSE proxy endpoints (e.g. LLM chat completions), the server immediately drops the connection right after receiving the user prompt with `socket hang up` or triggers a 180s timeout, even though the user never clicked stop.
- **Mechanism**:
  - In Node.js Express POST endpoints carrying a JSON body, the `req.on('close')` event fires as soon as the incoming request stream has finished uploading and was parsed by the server.
  - Attaching `proxyReq.destroy()` or stream teardown to `req.on('close')` causes the server to kill its own upstream connection at the exact millisecond the request body completes, before the upstream AI engine can stream back the first token.
  - Furthermore, targeting `http://localhost:<port>` on Linux hosts often resolves to IPv6 loopback (`::1`), which fails with `ECONNREFUSED` / exit code 7 when the internal daemon only binds to IPv4 (`127.0.0.1`).
- **Rule & Implementation Protocol**:
  1. **Listen to `res.on('close')`, Never `req.on('close')` for Client Disconnects**:
     ```javascript
     let proxyResEnded = false;
     proxyRes.on('end', () => { proxyResEnded = true; res.end(); });
     res.on('close', () => {
       if (!res.writableEnded && !proxyResEnded) {
         try { proxyReq.destroy(); } catch (e) {}
       }
     });
     ```
  2. **Strict IPv4 Loopback**: Always use explicit `127.0.0.1` for local microservice and model router proxying to prevent IPv6 DNS fallback delays.
  3. **Preserve Partial Response**: On client abort, persist whatever tokens have already accumulated up to that point into the database tagged with a notice (e.g. `*(Respon dihentikan oleh pengguna)*`) so partial work is never lost.

### 42. In-Page Unified Command Hub & Multi-Agent Workspace Ergonomics
- **Problem**: When migrating user workflows from chat apps (like Telegram) to an in-page web studio command hub, users lose context if multi-agent routing, session histories, system diagnostics, and code/document generation are scattered across separate pages or hidden behind heavy modal popups.
- **Rule & Implementation Protocol**:
  1. **Segmented 5-Tab Command Architecture**:
     - Organize the command hub into 5 clear tab views: `[CHAT]`, `[SESI]`, `[BOTS]`, `[GRUP]`, `[PROFIL]`.
     - `[CHAT]`: Live conversation stream with active bot badge, quick prompts (`[+ PRD]`, `[+ Web Mini]`, `[+ Plan]`), and streaming controls (`[JEDA]`, `[LANJUT]`, `[HENTIKAN]`).
     - `[SESI]`: Dedicated thread ledger enabling users to switch topics, spin up isolated tasks, or purge stale conversations without altering documents.
     - `[BOTS]`: Discrete agent personas with specialized system prompts (e.g. General Manager, Vault Curator, Systems Architect, Field Coder, QC Gatekeeper).
     - `[GRUP]`: Multi-agent collaborative discussion rooms uniting multiple personas into a single collective context.
     - `[PROFIL]`: Live server telemetry displaying CPU, memory headroom against limits (e.g. $\le 9.0$ GB RAM), uptime, and standing system rules.
  2. **Zero-Dependency In-Browser File Context Extraction**:
     - Do not introduce heavy server-side multipart middleware (like `multer`) for simple text/code/document analysis.
     - Read user attachments directly in browser JavaScript via `FileReader` (`readAsText` for `.py`, `.js`, `.md`, `.json`, `.csv`, `.txt`; `readAsDataURL` for images) and package the contents directly into the JSON payload (bounded to 50KB). Display a removable attachment chip in the UI before sending.
  3. **Actionable Code Block Headers & Document Ingestion**:
     - Format AI code fences with a dark container header containing the language badge and a trio of 1-click actions:
       * `[SALIN]`: Copies raw code to clipboard.
       * `[-> EDITOR]`: Wraps code with markdown fences and injects directly into the active editor draft.
       * `[UJI LIVE]` (conditionally rendered for HTML/Web/Canvas code): Immediately opens an interactive mini web sandbox without navigating away.
     - **Assistant Message Action Footers & Single-Row Flex Containment**:
       * Equip every assistant response bubble with a footer action bar: `[SALIN]`, `[+ DOKUMEN]` (persists a new note in SQLite, extracts title from the first `# Heading`, and opens it in the editor), `[-> EDITOR]` (appends to the active draft with auto-save), and conditional `[SANDBOX]` (renders only when HTML/Web code is present).
       * On mobile viewports ($\le 390\text{px}$), long button labels or `flex-wrap: wrap` cause trailing buttons to drop onto an asymmetric second row. Use `display: flex; gap: 5px; overflow-x: auto; white-space: nowrap; scrollbar-width: none; -webkit-overflow-scrolling: touch;` with compact labels (`[SALIN]`, `[+ DOKUMEN]`, `[-> EDITOR]`, `[SANDBOX]`) so actions remain aligned in a single row without clipping.
     - **Post-Render Scroll Timing**:
       * Because markdown parsing and action footer insertion alter DOM height after streaming ends, fire `scrollHermesToBottom()` inside a `setTimeout(..., 50-60ms)` after DOM mutation and view switches. Without this delay, the scroll calculation uses the pre-mutation height, leaving the action footer clipped behind the fixed composer dock.
  4. **Multimodal Image Context Pipeline**:
     - Accept image uploads (`.png`, `.jpg`, `.jpeg`, `.webp`) up to 4 MB via `FileReader.readAsDataURL()`.
     - In backend LLM proxying, format the user message into OpenAI/Claude-compatible multimodal arrays: `content: [{ type: "text", text: ... }, { type: "image_url", image_url: { url: data_url } }]`.
  5. **Strict Zero-Emoji Doctrine**: Enforce 100% emoji-free UI elements and system prompts, using clean alphanumeric badges (`[...]`), bullets (`•`), and geometric arrows (`▼`, `→`).

### 43. Progressive Web App (PWA) Deployment for Sub-Path Mounted Web Studios
- **Problem**: Converting an existing live web app mounted at a sub-path (e.g. `/kanvas`) behind reverse proxies (Nginx/Cloudflare Tunnel) into an installable Progressive Web App (PWA) often fails silently: Service Workers fail to register, icons return 404, browsers refuse install prompts, or pre-caching crashes offline support.
- **Root Causes & Mechanisms**:
  1. **Scope & Path Root Mismatch**: Registering with default root scope (`/`) from a sub-path page triggers `DOMException: The path of the provided scope ('/') is not under the max scope allowed ('/kanvas/')`.
  2. **Express & Proxy Header Requirements**:
     - Service worker scripts served without `Service-Worker-Allowed: /` cannot control ancestor or sibling scopes.
     - Web App Manifests must be served with exact MIME type `application/manifest+json; charset=utf-8` and `Cache-Control: public, max-age=0` (or dynamic), otherwise browsers reject or aggressively stale-cache them across updates.
     - `sw.js` must be served with `Cache-Control: no-cache, no-store, must-revalidate` so client devices immediately discover updates instead of serving stale workers for 24+ hours.
  3. **Pre-Cache URL Resolution Trap**:
     - Using root-relative paths (`/`, `/index.html`) in `cache.addAll()` inside `install` fails with 404 if the server root hosts another service (e.g. the main portal). In Service Worker lifecycle, if *any single URL* in `addAll` fails (404/500), the entire install step aborts, leaving 0 assets cached.
     - **Rule**: All pre-cache shell URLs must be explicitly qualified with the sub-path mount (`/kanvas`, `/kanvas/manifest.webmanifest`, `/kanvas/icons/...`). Use `Promise.all(STATIC_PRECACHE.map(url => cache.add(url).catch(...)))` so a transient asset error does not fail the entire installation.
  4. **The `window.addEventListener('load')` Race Condition**:
     - In SPAs or dynamically initialized pages where registration scripts run inside `DOMContentLoaded` or deferred modules, `document.readyState` may already be `'complete'`. Attaching `window.addEventListener('load', registerSw)` after the browser has completed loading means the listener **never triggers**.
     - **Rule**: Check `if (document.readyState === 'complete') { registerSw(); } else { window.addEventListener('load', registerSw); }`.
  5. **Dynamic API & SSE Streaming Bypass**:
     - In the Service Worker `fetch` handler, any request matching non-GET methods or paths containing `/api/` (such as `/api/hermes/chat` SSE token streams or `/api/notes` state mutations) must immediately bypass cache (`if (req.method !== 'GET' || url.pathname.includes('/api/')) return;`). Attempting to intercept or cache SSE streams buffers tokens indefinitely and breaks real-time AI responses.
  6. **Installability Prompt & Platform Guidance**:
     - Store the `beforeinstallprompt` event in `deferredInstallPrompt` to show a dedicated `[PASANG APP]` button.
     - When `deferredInstallPrompt` is not available (e.g. iOS Safari which does not support the automated prompt, or desktop browsers), provide an explicit modal/toast guide:
       * iOS: *"Tekan tombol Bagikan (Share) lalu pilih 'Tambahkan ke Layar Utama'"*.
       * Android/Desktop: *"Buka menu browser (titik tiga) lalu pilih 'Pasang Aplikasi' / 'Instal'"*.
     - Detect standalone mode (`window.matchMedia('(display-mode: standalone)').matches || navigator.standalone`) to replace install buttons with an active native app status indicator.

### 44. Tactile Bottom-Sheet Pickers vs Native Mobile `<select>` Popups
- **Problem**: Using standard HTML `<select>` elements for agent selectors, tone switches, or model pickers on mobile browsers (Android Chrome, PWA standalone, iOS WebKit) triggers an OS native modal dialog (e.g. an Android radio-button popup floating rigidly in the center of the screen with a dark scrim, or an iOS wheel). This breaks custom themes (Neo-Brutalis, dark mode), obstructs the chat/editor context, and feels clunky and disconnected.
- **Root Cause**: Mobile browsers intercept `<select>` taps by invoking system-level dialog controllers outside the web document DOM.
- **Rules & Implementation Protocol**:
  1. **Dual-Layer Architecture (Custom Trigger + Hidden Native Select)**:
     - Replace the visible `<select>` element with a tactile custom button trigger:
       ```html
       <button class="picker-btn" id="btn-pick-agent" onclick="openCustomPicker('agent', event)" type="button">
         <span class="picker-label" id="lbl-pick-agent">HERMES CORE</span>
         <span class="picker-caret">▼</span>
       </button>
       <!-- Retain hidden native select/input so existing JS or form logic reading .value works with zero code changes -->
       <select id="agent-select" style="display:none;"></select>
       ```
  2. **Tactile Bottom-Sheet Drawer (Thumb-Zone Native)**:
     - Mount a fixed overlay (`custom-picker-overlay`) with `align-items: flex-end;` and a slide-up drawer (`animation: slideUp 0.2s cubic-bezier(0.16, 1, 0.3, 1)`).
     - Anchor in the comfortable lower third of the screen, bound by `max-height: 80vh` and respecting `padding-bottom: calc(14px + env(safe-area-inset-bottom, 0px))`.
     - Tap outside on the overlay, tap the `[TUTUP]` header button, or press `Escape` to dismiss instantly without lag.
  3. **Rich Metadata & Distinct Persona Badges**:
     - Unlike plain-text native `<select>` options, custom bottom sheets allow rich item cards:
       * **Distinct Alphanumeric Badge**: Color-coded badges with unique initials. In multi-agent systems, ensure distinct 2-letter codes (e.g. `[QC]` for SI PENGAWAS / Gatekeeper to avoid collision with `[SP]` for SI PINTAR).
       * **Primary Title**: Bold, readable font.
       * **Functional Role / Subtitle**: Clear description of what the agent or mode does.
       * **Active State Indicator**: High-contrast indicator (`[AKTIF]`) with border and background highlights on the active choice.
  4. **Instant Event Binding & Label Synchronization**:
     - On item selection, immediately update the hidden `<select>.value`, update the trigger button text label (`updatePickerButtonLabels()`), dispatch any change events, close the drawer, and display a non-blocking toast.
     - Call `updatePickerButtonLabels()` on `DOMContentLoaded` and after any dynamic bot list reload (`loadHermesBots()`).

### 45. Automated Chat Session Topic Detection & Real-Time Auto-Titling (Two-Tier SSE Architecture)
- **Problem**: In multi-agent workspaces and conversational web studios, chat histories default to generic labels (e.g. "Sesi Utama", "Sesi Baru", "Chat 1"). Without automated contextual naming, users lose track of discussions, clutter their history list, and must manually rename sessions one by one.
- **Root Causes & Mechanisms**:
  1. Relying exclusively on an asynchronous background job leaves a delay where the session list displays a stale generic label until manual page reload.
  2. Relying exclusively on heavy LLM calls can stall if the inference router is busy, while relying exclusively on naive substring truncation captures leading conversational filler (e.g. "Tolong buatkan saya...", "Bagaimana cara...", "Halo admin...").
- **Rules & Implementation Protocol**:
  1. **Two-Tier Title Generation Architecture**:
     - **Tier 1 (Instant Heuristic Extraction Baseline)**:
       Strip conversational filler prefixes (`/^(halo|hai|tolong|bisa\s+gak|bagaimana\s+cara|buatkan\s+saya|saya\s+mau|jelaskan|apa\s+itu)\s+/i`), strip code fences and attachment tags, extract the first 4–6 semantic words, and apply Title Case bounded to 40–45 characters.
     - **Tier 2 (Asynchronous Lightweight LLM Synthesis)**:
       Prompt a fast, lightweight model with a strict system prompt: *"Buat judul ringkas 3-5 kata dalam Bahasa Indonesia yang merangkum topik pembahasan. ATURAN: Jawab HANYA judulnya saja, tanpa tanda petik, tanpa titik, tanpa kata pembuka, tanpa emoji."* Limit to `max_tokens: 25` and `temperature: 0.3`. Sanitize the response by stripping quotes, terminal punctuation, and non-alphanumeric noise.
  2. **Streaming In-Flight SSE Delivery**:
     - Deliver the generated title over the active SSE connection immediately before the terminal chunk (`data: {"session_title": "..."}\n\n` followed by `data: [DONE]\n\n`).
     - In frontend stream readers, listen for `data.session_title`, immediately update the active header badge (`document.getElementById('active-session-title').textContent = data.session_title`), update the session in the in-memory array, and re-render session cards in 0ms without page reloads.
  3. **Auto-Trigger Guard on Initial Exchanges**:
     - Trigger auto-titling when the session title matches known generic patterns (`'Sesi Utama'`, `'Sesi Baru'`, starts with `'Sesi '`, `'Tanpa Judul'`) OR when the session has <= 2 messages. Once a custom title is established, preserve it across subsequent messages unless the user explicitly clicks `[AUTO]`.
  4. **On-Demand & Flexible Controls**:
     - Provide a 1-tap `[AUTO]` button in both the chat header and on individual session drawer cards to allow users to refresh the title as discussions evolve.
     - Allow creating sessions with blank titles (`+ SESI`), defaulting them to auto-titling upon the first user message.
  5. **Header Layout Collision & Tooltip Guard**:
     - On desktop viewports, give the title badge generous width (`max-width: 220px;`) with `text-overflow: ellipsis; white-space: nowrap;` and assign the full string to the `title` attribute (`title="Topik: ${fullTitle} (Klik untuk ubah)"`) so users can hover to read long titles.
     - Keep adjacent header control labels compact (`[AUTO]`, `[UBAH]`, `ONLINE`, `[BERSIH]`) to prevent header wrapping on narrow laptop or mobile screens.

### 46. IDE-Grade Vanilla Textarea Ergonomics (Line Number Gutter, Indentation & Pair Wrapping)
- **Problem**: In-browser document editors and code scratchpads using standard HTML `<textarea>` elements feel stiff and frustrating for technical writing and coding: there are no line numbers, pressing `Tab` loses keyboard focus to another element, pressing `Enter` resets indentation to column 0, and typing brackets or quotes does not close them.
- **Rules & Implementation Protocol**:
  1. **Synchronized Line Number Gutter**:
     - Place a non-editable, non-selectable line number container (`.editor-gutter`, `user-select: none; pointer-events: none;`) directly adjacent to the `<textarea>`.
     - Count newline characters (`editor.value.split('\n').length`) and render line index spans `1` through `N`.
     - Synchronize vertical scrolling in real time: `textarea.addEventListener('scroll', () => { gutter.scrollTop = textarea.scrollTop; });`.
  2. **Tab & Shift+Tab Indentation Handling**:
     - Intercept `keydown` when `e.key === 'Tab'`. Prevent default focus shifting (`e.preventDefault()`).
     - **Single-cursor indent**: Insert 2 spaces at `selectionStart` and advance the cursor position by 2.
     - **Multi-line selection**: For `Tab`, prepend 2 spaces to every line touched by the selection; for `Shift+Tab`, strip up to 2 leading spaces from each line. Recalculate selection offsets so the text block stays highlighted after indenting.
  3. **Smart Enter Auto-Indentation & Block Expansion**:
     - On `e.key === 'Enter'`, inspect the text of the current line before the cursor. Extract leading whitespace: `const match = currentLine.match(/^(\s+)/);`.
     - If the preceding line ends with an opening block symbol (`{`, `[`, `(`, or `:`), append an additional 2 spaces of indentation on the new line.
     - Preserve and auto-increment Markdown lists (`- `, `* `, `1. `, `[ ] `), but clear the marker if `Enter` is pressed on an empty list item.
  4. **Auto-Closing & Text-Wrapping Character Pairs**:
     - Map pairs: `(` to `)`, `[` to `]`, `{` to `}`, `"`, `'` to `'`, and ``` ` ``` to ``` ` ```.
     - **With Active Selection**: Wrap the highlighted text within the pair without replacing it, keeping the wrapped block selected.
     - **Without Selection**: Insert both opening and closing characters, placing the cursor cleanly in between.
     - **Pair Backspace**: When pressing `Backspace` with the cursor directly between an empty pair (e.g. `(|)`), delete both characters simultaneously.

### 47. Dynamic Workspace & Project Discovery vs Rigid Preset Triggers
- **Problem**: Hardcoding fixed preset buttons (e.g., three static pills `[FOUNDRY]`, `[KANVAS]`, `[VAULT]`) into a developer workspace or file explorer header is an anti-pattern. It breaks scalability as soon as the user creates new projects, clutters UI space with arbitrary names, and requires code changes whenever projects are added or renamed.
- **Rule & Implementation Protocol**:
  1. **Zero Hardcoded Preset Buttons**: Never hardcode project-specific buttons into IDE, file explorer, or workspace sidebars.
  2. **Automated Server-Side Project Scanner (`/api/fs/projects`)**: Implement an endpoint scanning the server workspace root (`/home/ubuntu`) for directories with project markers (`.git`, `package.json`, `Cargo.toml`, `pyproject.toml`, `requirements.txt`, `.obsidian`). Classify directories into clean tags (`[RUST]`, `[NODE]`, `[PYTHON]`, `[VAULT]`, `[GIT]`, `[DIR]`) and return them sorted (projects first).
  3. **Two-Tier Dynamic Selector (Recents + Server Inventory)**:
     - Store a persistent "Recently Opened Workspaces" array in `localStorage` (`kanvas_recent_workspaces`, bounded to 8–10 items).
     - Populate a dynamic dropdown (`<select id="fs-project-dropdown">`) with `<optgroup label="PROYEK TERAKHIR DIBUKA">` followed by `<optgroup label="SEMUA REPOSITORI & FOLDER SERVER">`.
  4. **Open-Ended Custom Path Input**: Accompany the dropdown with an open path input bar (`[ /home/ubuntu/... ]` + `[BUKA]`). Any arbitrary new directory typed or pasted by the user immediately opens the file tree, records the folder in recents, and binds the workspace state.

### 48. Contextual Project Boundary Guard & Explicit Workspace Pinning
- **Problem**: When an autonomous AI coding assistant operates in an environment containing multiple adjacent repositories or projects, ambiguous user prompts (e.g. "perbaiki modul auth", "tambahkan fitur logging", "jalankan unit test") easily cause the AI to guess the wrong project, touch files in another repository, or generate cross-project confusion.
- **Rule & Implementation Protocol**:
  1. **Tactile In-Page Boundary Bar**: Mount a persistent, high-contrast boundary pin bar directly above the chat input dock:
     - Target project indicator: `[TARGET PROYEK] <project_name>`
     - Bound active file (when a file is opened in editor/code mode): `• <file_name>`
     - Quick controls: `[GANTI]` (opens dynamic project switcher) and `[TERKUNCI [v]]` (toggles strict boundary lock).
  2. **Strict System Prompt Injection (`project_context`)**:
     - Transmit `project_context: { project_name, project_root, active_file, is_locked }` in every chat payload.
     - Backend system prompt injects hard invariant rules:
       * All analysis, code generation, and commands must target exclusively `project_root`.
       * **Ambiguity rejection**: If the user mentions a component or file not present in `project_root`, the AI is forbidden from assuming another repository and must explicitly ask for confirmation first.
       * **Out-of-bounds mutation prohibition**: Modifying or creating files outside `project_root` without explicit user permission is strictly barred.
  3. **Synchronized 1-Click Project Switching**: Selecting a new project from either the explorer dropdown or the boundary modal instantly synchronizes both the file explorer and the AI boundary bar in 0ms without page reloads.

  ### 49. Full-Bleed Natural Web Page vs Floating Canvas Frame (Natural Webpage Doctrine)
  - **Problem**: When implementing landing pages or web surfaces from design mockups/screenshots that show a white card floating over a colored background (e.g. lavender canvas surround with card drop-shadow), recreating the outer frame and body padding literally makes the published site look like a "framed presentation poster" or "floating sheet" rather than a real, edge-to-edge website ("bikin seperti sebuah page asli, itu kan di luar page ada marginnya, saya mau seperti page pada umumnya").
  - **Rule**:
  1. For production web deliverables, always treat the canvas as a **natural full-bleed web page**:
    - Root `body` background must seamlessly match the primary page surface (e.g., pure `#ffffff` or the intentional page theme).
    - Never apply artificial outer margins, thick `body { padding: ... }`, or wrapper drop-shadows that make the page float inside a colored frame, unless the user explicitly requests an in-canvas presentation deck or throwaway mockup.
  2. Implement standard responsive container centering: `max-width: 1240px; margin: 0 auto; padding: 0 <side_gutter>; box-shadow: none;` so headers and footers stretch naturally and content breathes cleanly on all viewport widths without unnatural surrounding borders.

  ### 50. Unified Master Portfolio Hub & Showcase Catalog Pattern
  - **Problem**: When an engineer or designer accumulates multiple independent web applications, experimental micro-sites, and tools across different sub-paths, clients or stakeholders have no single cohesive entry point to inspect the full body of work as an organized professional portfolio.
  - **Rule**:
  1. Build a centralized master portfolio catalog project (e.g. `/katalog/` or `/portofolio/`) that comprehensively aggregates and showcases all live web artifacts in one place:
    - Provide original, lightweight vector SVG visual previews for each project to eliminate slow-loading raster images or broken external CDN links.
    - Include dynamic category filtering (Landing Page, Experiential & 3D, Design System, Data & Media) and instant real-time search across titles, summaries, and tech tags.
    - Support a dual-view switcher: **Grid View** (tactile visual cards with live color palette swatches) and **Ledger View** (high-density Swiss Editorial tabular view with metrics and year).
    - Implement a comprehensive **Case Study / Architecture Modal** per project displaying design philosophy, technical highlights, calibrated hex swatches, tech stack chips, and a direct `[Buka Live]` launch link with focus-trapping and keyboard Escape dismissal.
  2. Maintain strict production invariants: 100% Zero-Emoji compliance (pure SVG icons only), zero horizontal overflow across mobile (390px), tablet (768px), and desktop (1440px), and automated Axe Core WCAG 2.1 AA accessibility verification.

### 51. Permissions-Policy Microphone Delegation & Real-Time Web Telephony Pipeline
- **Problem**: When deploying browser-based voice assistants, live telephone simulators, or WebRTC/Web-Speech tools on live servers, microphone access is completely blocked or fails silently (`NotAllowedError`), even on HTTPS, without ever displaying a browser permission prompt. Furthermore, AI voice responses feel robotic or un-interruptible when played back in full.
- **Root Causes & Mechanisms**:
  1. **Global Security Header Lockout**: Production reverse-proxy middleware (Express/Nginx) often enforces a strict global header: `'Permissions-Policy': 'camera=(), microphone=(), geolocation=()'`. This tells modern browsers (Chrome, Edge, Safari) to strictly forbid microphone capture document-wide, regardless of user consent.
  2. **Un-Interruptible Monologue**: Playing back audio blobs without tracking active microphone speech input forces the user to listen to the entire generated response before they can speak again, breaking natural conversational cadence.
- **Rules & Implementation Protocol**:
  1. **Route-Specific Permissions-Policy Unlocking**:
     In server middleware, inspect incoming `req.path`. Selectively allow `microphone=(self)` strictly on voice routes while keeping default security headers intact for the rest of the application:
     ```javascript
     const isVoiceRoute = req.path.startsWith('/telepon') || req.path.startsWith('/voice') || req.path.startsWith('/api/telepon');
     res.set({
       'Permissions-Policy': isVoiceRoute ? 'camera=(), microphone=(self), geolocation=()' : 'camera=(), microphone=(), geolocation=()'
     });
     ```
  2. **Dual-Layer Speech Pipeline (Web Speech API + Fast Model + Edge-TTS)**:
     - **Client-Side STT**: Use browser-native `webkitSpeechRecognition` (`lang: 'id-ID'`, `continuous: true`, `interimResults: true`) with an 800–1100ms silence timer. This eliminates megabytes of raw audio uploads and achieves ~0ms client transcription latency.
     - **Voice-Specific System Prompt**: Enforce strict voice constraints in the LLM prompt: *"Maksimal 1-2 kalimat pendek, santai, dan alami. Dilarang menggunakan markdown, tanda bintang, atau bullet points karena teks langsung dibacakan suara telepon."*
     - **High-Fidelity Audio Streaming**: Stream synthesized audio via Edge-TTS (`id-ID-GadisNeural` / `id-ID-ArdiNeural`) encoded as Base64 MP3, with a client toggle fallback to `window.speechSynthesis` for zero-latency local synthesis.
  3. **Instant Conversational Interruption**:
     - Attach an immediate cancellation hook inside the speech recognition `onresult` listener:
       ```javascript
       if (isSpeaking && currentAudio) {
         currentAudio.pause();
         currentAudio.currentTime = 0;
         isSpeaking = false;
       }
       ```
     - If the user speaks while the AI is talking, immediately kill the active audio playback, reset the visualizer, and transition the state directly to listening.






