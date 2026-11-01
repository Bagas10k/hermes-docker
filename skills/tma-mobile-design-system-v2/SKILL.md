---
name: tma-mobile-design-system
description: Use when building Telegram Mini Apps with modern mobile UI.
version: 1.1.0
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
      - WarmEspresso
---

# TMA Mobile Design System & Engineering

Standard procedures, visual palettes, and critical pitfalls when architecting, redesigning, and deploying Telegram Mini Apps (TMA) in production environments.

## 1. Visual Anchor & Palette Architecture (Warm Espresso & Radiant Amber)

When aiming for a luxurious, warm, and playful ("fun & elegan") mobile dark theme, avoid cold pure blacks (`#000000`) and arbitrary neon gradients. Use the proven **Warm Espresso & Radiant Amber** design system:

- **Canvas Base:** Warm Deep Roasted Espresso (`#140e0b`), reducing eye strain while preserving OLED depth.
- **Surface Cards (Bento Containers):** Deep Roasted Brown (`#221813` or `#291d17`) with 24px–28px rounded corners and subtle 1px border (`rgba(255, 255, 255, 0.07)`).
- **Primary Accent / Radiance:** Radiant Amber Glow (`#ff7a29`) with diffused box-shadow (`rgba(255, 122, 41, 0.4)`) for active pills, CTA buttons, and key timeline indicators.
- **Positive Status / Metric:** Soft Emerald Mint (`#3cd87a` with `rgba(60, 216, 122, 0.12)` background).
- **Zero Foreign Color Leakage:** Eliminate leftover default cyan, teal, or violet glow remnants on chart rules, connectors, or backgrounds when adopting an amber-espresso palette.

## 2. Spatial Hierarchy, Margins & Padding (Anti-Cramped / Anti-Dead Space)

- **Eliminate Artificial Dead Space:** Never use arbitrary fixed viewport subtraction like `max-height: calc(100dvh - 320px)` or unconditional `flex: 1` on sparse data cards. Use content-adaptive height with structured vertical rhythm (`min-height: auto; padding: 16px 14px; margin-bottom: 12px; gap: 12px;`) so the viewport remains balanced.
- **Horizontal Pill Overflow & Clipping Prevention:** Touch targets and filter pills (e.g. time range controls `1m, 3m, 5m, 10m, 30m`) must be sized with compact, proportional paddings (`min-width: 36px; height: 30px; padding: 0 10px; gap: 4px;`) and an intentional overflow strategy so the last pill does not get clipped awkwardly at the viewport edge.
- **Consistent Inter-Card Spacing:** Maintain a uniform 12–16px vertical gap between stacked surface cards (Header ➔ Main Content ➔ Telemetry ➔ Legend), preventing visual weight imbalance.
- **Header Element De-collision:** In responsive floating headers, separate primary brand titles and status pills into dedicated flex rows (`.armada-header-top-row`) or apply explicit flex gaps to prevent overlapping text (e.g. `ARMADA` colliding with `TERHUBUNG`).

## 3. High-Performance Luxury Typography Discipline

- **Never default to bare OS system fonts alone** (`-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `sans-serif`) for fun, elegant, or editorial interfaces; they look like flat internal server dashboards.
- **Single Dominant Family for Visual Unity:** Avoid clashing two similar sans-serifs (like mixing Outfit and Plus Jakarta Sans together across tight mobile cards). Prefer one primary family:
  - **Primary & Labels:** `Plus Jakarta Sans` for clean, disciplined, contemporary hierarchy.
  - **Brand Headings (Luxury Logotype):** All-caps brand titles must use generous letter-spacing (`letter-spacing: 0.18em` to `0.24em`) with sleek `SemiBold` (600–700) weight rather than aggressive `Black`/`Heavy` (900), creating optical breathing room and an executive feel.
  - **Telemetry / Timestamps / Code:** `JetBrains Mono` with `font-variant-numeric: tabular-nums` to ensure numbers do not wobble or jitter during live streaming updates.

## 4. Anti-Jitter Live Streaming & Smooth Timeline Mechanics

When displaying real-time data on canvas or swimlane timelines, visual jitter/twitching ("berkedut") is the primary UX failure:

- **Do Not Trigger Re-render on Tickers:** A 1-second continuous live ticker must ONLY update raw text timestamps (e.g. sync/elapsed time in `#armada-observed-time`). NEVER call full chart `renderTimeline()` or DOM rebuild on tick intervals when payload data hasn't changed.
- **Decouple Data Polling from Entrance Animations:** CSS keyframe animations (like `armada-data-enter`) must ONLY apply on brand new event IDs or initial load. Re-applying scale/transform animations on background polling causes existing historical bars to twitch violently every 2 seconds.
- **CSS Transition Conflict on Live Bounds:** Do not attach CSS `transition: width ..., left ...` to DOM elements whose positions are continuously updated by JavaScript tick loops. The race between JS layout calculation and CSS interpolated transitions causes visible stuttering/jumping. Keep CSS transitions to smooth opacity fade (`animation: armada-arrive-fade 0.4s ease-out`), letting JS cleanly control coordinate bounds.
- **Programmatic Smooth Scrolling:** When pinning the timeline to latest active data, use `viewportEl.scrollTo({ left: targetLeft, behavior: 'smooth' })` rather than instant coordinate snapping.

## 5. Content-Security-Policy (CSP) Font & Style Whitelist

- When loading fonts from Google Fonts (`fonts.googleapis.com` / `fonts.gstatic.com`), verify and update the backend router's CSP headers:
  `style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' data: https://fonts.gstatic.com;`
- Failing to whitelist font sources causes the browser to silently block the webfont request, falling back to Times or generic system sans.

## 5. Static Asset Bundle vs. Router Whitelist

- Production Express routers often protect public static files via strict route allowlists (e.g. only serving `/app.css` and `/chat.css`).
- Adding a new external stylesheet (e.g. `<link href="/tma/floating-island.css">`) will fail with **HTTP 404** if not registered in the router.
- **Rule:** Either explicitly declare the new route in the router or bundle new CSS rules directly into the existing primary stylesheets (`app.css` / `chat.css`).

## 6. Cache-Busting Discipline on Mobile Telegram

- Mobile Telegram webviews aggressively cache static assets.
- When updating stylesheets or scripts, always update the cache-buster query parameter (e.g. `?v=<timestamp>-<slug>`) across all HTML entrypoints, restart upstream Node/PM2 processes, and verify `HTTP 200` via `curl -sI`.

## 7. Authenticated Verification Loop (Anti-Lock Screen Testing)

- When testing TMA screenshots via headless Chromium/Puppeteer, always mock or intercept the Telegram WebApp `initData` or authentication endpoints.
- Verifying an unauthenticated view only captures the error card or auth lock modal, missing actual component layout, font rendering, chart tracks, and responsive padding.
