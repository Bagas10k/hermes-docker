# Zero-Downtime Asset Routing Under Strict Privacy Boundaries

## Problem & Mechanism
In multi-tenant or gateway-proxied web environments, production portals often enforce an exact-whitelist security boundary (e.g., Express privacy middleware). The root route (`/` or `/index.html`) is publicly exposed, but unlisted root-level assets (`/style.css`, `/app.js`, `/assets/*`) fail with `401 Unauthorized` or redirect to login.

Restarting the gateway process or modifying core reverse-proxy routing scripts is often prohibited to prevent dropping live background worker jobs, active WebSocket connections, or client sessions.

## The Public Wildcard Prefix Pattern
Instead of modifying core gateway routing or restarting services:
1. **Identify Existing Wildcard Routes:** Find existing public subpath mappings (e.g., `/p/:project` dynamically mapped to `/home/ubuntu/<project>/` or `dist-public/` and whitelisted in the security filter).
2. **Isolate Asset Bundles:** Place the website's complete asset tree (styles, scripts, SVGs, web fonts) in that project directory:
   ```
   /home/ubuntu/<project>/
   ├── index.html
   ├── style.css
   ├── app.js
   └── assets/
       ├── knot.svg
       ├── favicon.svg
       └── studio-*.woff2
   ```
3. **Point Root HTML to Public Subpath:** Update the root serving page (`public/index.html`) to reference assets via absolute paths pointing to the wildcard mount:
   ```html
   <link rel="icon" href="/p/<project>/assets/favicon.svg" type="image/svg+xml">
   <link rel="stylesheet" href="/p/<project>/style.css">
   <script src="/p/<project>/app.js" defer></script>
   <img class="sculpture" src="/p/<project>/assets/knot.svg">
   ```
4. **Preserve Relative Asset Resolution:** Stylesheet `@font-face` rules using relative URLs (`url('assets/font.woff2')`) automatically resolve relative to the stylesheet URL (`/p/<project>/assets/font.woff2`), eliminating the need to rewrite CSS internal URLs.

## Verification Checklist
- **Atomic Dependency Probing:** Curl every asset individually before declaring success:
  ```bash
  curl -s -o /dev/null -w "%{http_code}\n" https://<domain>/
  curl -s -o /dev/null -w "%{http_code}\n" https://<domain>/p/<project>/style.css
  curl -s -o /dev/null -w "%{http_code}\n" https://<domain>/p/<project>/app.js
  curl -s -o /dev/null -w "%{http_code}\n" https://<domain>/p/<project>/assets/<asset>
  ```
  All responses must return `200 OK`. Any `401`, `302`, or `404` indicates a path leak outside the whitelisted prefix.
- **Headless Dual-Viewport Screenshot Verification:** Capture both desktop (1440x900) and mobile (390x844) viewports using headless Chromium/Puppeteer to confirm typography rendering, SVG scaling, and lack of visual shift without needing local GUI access.
