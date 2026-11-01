---
name: tma-mobile-design-system
description: Use when building Telegram Mini Apps with modern mobile UI.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags:
      - TelegramMiniApp
      - TMA
      - MobileUI
      - DynamicIsland
      - Typography
      - CSP
---

# TMA Mobile Design System & Engineering

Standard procedures and critical pitfalls when architecting, redesigning, and deploying Telegram Mini Apps (TMA) in production environments.

## Core Directives

1. **Floating Pill Dynamic Island Architecture:**
   - On mobile TMAs, avoid rigid edge-to-edge navbar headers. Use centered floating capsule pills (`border-radius: 9999px; margin: 6px auto; backdrop-filter: blur(28px) saturate(180%);`).
   - Pair floating headers with a bottom floating tactile composer and translucent frosted-glass modal cards.

2. **Spatial Hierarchy, Margins & Padding (Anti-Cramped / Anti-Dead Space):**
   - **Eliminate Artificial Dead Space:** Never use arbitrary fixed viewport subtraction like `max-height: calc(100dvh - 320px)` or unconditional `flex: 1` on empty/sparse data cards. Use content-adaptive height with structured vertical rhythm (`min-height: auto; padding: 16px 14px; margin-bottom: 12px; gap: 12px;`) so the viewport remains balanced.
   - **Horizontal Pill Overflow & Clipping Prevention:** Touch targets and filter pills (e.g. time range controls `1m, 3m, 5m, 10m, 30m`) must be sized with compact, proportional paddings (`min-width: 36px; height: 30px; padding: 0 10px; gap: 4px;`) and an intentional overflow strategy so the last pill does not get clipped awkwardly at the viewport edge.
   - **Consistent Inter-Card Spacing:** Maintain a uniform 12–16px vertical gap between stacked surface cards (Header ➔ Main Content ➔ Telemetry ➔ Legend), preventing visual weight imbalance.

3. **Typography Quality Floor (Anti-System-Blandness):**
   - **Never default to bare OS system fonts alone** (`-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `sans-serif`) for fun, elegant, or editorial interfaces; they look like flat internal server dashboards.
   - Always load modern characterful typefaces:
     - **Display / Headers:** `Outfit` (geometric, warm, playful elegance) or `Syne`.
     - **Body / Interactive:** `Plus Jakarta Sans` (clean, highly legible, structured rhythm).
     - **Telemetry / Timestamps / Code:** `JetBrains Mono` with tabular numbers.
   - Pair with explicit letter-spacing (tighter tracking `-0.01em` to `-0.02em` on large headings, generous `0.06em` to `0.12em` on micro-labels).

3. **Content-Security-Policy (CSP) Font & Style Whitelist:**
   - When loading fonts from Google Fonts (`fonts.googleapis.com` / `fonts.gstatic.com`), verify and update the backend router's CSP headers:
     `style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' data: https://fonts.gstatic.com;`
   - Failing to whitelist font sources causes the browser to silently block the webfont request, falling back to Times or generic system sans.

4. **Static Asset Bundle vs. Router Whitelist:**
   - Production Express routers often protect public static files via strict route allowlists (e.g. only serving `/app.css` and `/chat.css`).
   - Adding a new external stylesheet (e.g. `<link href="/tma/floating-island.css">`) will fail with **HTTP 404** if not registered in the router.
   - **Rule:** Either explicitly declare the new route in the router or bundle new CSS rules directly into the existing primary stylesheets (`app.css` / `chat.css`).

5. **Cache-Busting Discipline on Mobile Telegram:**
   - Mobile Telegram webviews aggressively cache static assets.
   - When updating stylesheets or scripts, always update the cache-buster query parameter (e.g. `?v=<timestamp>-<slug>`) across all HTML entrypoints, restart upstream Node/PM2 processes, and verify `HTTP 200` via `curl -sI`.
