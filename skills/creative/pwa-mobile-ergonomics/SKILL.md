---
name: pwa-mobile-ergonomics
description: Build tactile mobile PWAs with offline precache and sheets.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [pwa, service-worker, tactile-ux, mobile-ergonomics, bottom-sheet, zero-emoji]
    related_skills: [tactile-microinteraction-studio, ambient-sonification-flow, live-sandbox-hot-preview]
---

# PWA & Mobile Web Tactile Ergonomics

Build high-performance Progressive Web Apps (PWAs) tailored for mobile flow: offline-first asset precaching, strict dynamic API/SSE bypass, standalone Web App Manifest with maskable icons, spring-physics tactile bottom sheets replacing native select/modals, and zero-emoji SVG typography.

## When to Use

- Developing mobile web apps or progressive web apps requiring offline resilience.
- Eliminating browser chrome and enabling tactile standalone mobile experience.
- Replacing clunky native `<select>` and `<dialog>` forms with finger-friendly spring bottom sheets.
- Ensuring dynamic SSE/WebSocket/API traffic is never trapped or corrupted by Service Worker caches.

Don't use for:
- Pure desktop administration dashboards without touch ergonomics requirements.
- Native mobile applications (Swift/Kotlin/React Native).

## Prerequisites

- Modern browser supporting Service Workers and Touch/Pointer Events.
- HTTPS context or `localhost` (Service Worker requirement).
- Zero-emoji SVG icon system (Heroicons / Lucide SVG) and strict font stack (`Plus Jakarta Sans` or `Poppins`).

## Quick Reference

- **Audit PWA Artifacts**:
  ```bash
  python3 ~/.hermes/skills/creative/pwa-mobile-ergonomics/scripts/pwa_scaffold.py --audit /path/to/webroot
  ```
- **Scaffold PWA Skeleton**:
  ```bash
  python3 ~/.hermes/skills/creative/pwa-mobile-ergonomics/scripts/pwa_scaffold.py --scaffold /path/to/webroot --app-name "My Tactile PWA"
  ```

## Architecture & Core Mechanics

### 1. Service Worker Cache Partitioning (Bypass Invariant)
A common PWA failure is stale caching of streaming endpoints (`/api/stream`, `/sse`, `/ws`).
- **Precaching Tier (`CACHE_STATIC_vX`)**: HTML shell, CSS, bundle JS, manifest, SVG icons, fonts.
- **Dynamic Bypass Tier**: Any request matching `/\/api\/|\/sse|\/stream|\/ws/` MUST use Network-Only with zero cache fallback to prevent frozen state.

### 2. Spring Physics Bottom Sheet Sheet
- **Touch Geometry**: Sheet height clamped between `40vh` (peek) and `85vh` (expanded).
- **Inertial Snapping**: Velocity threshold $>0.5\text{px/ms}$ or displacement $>30\%$ triggers instant snap to destination using cubic-bezier `cubic-bezier(0.32, 0.72, 0, 1)`.
- **Haptic Simulation**: Dual tactile feedback: light haptic vibration (`navigator.vibrate([8])`) on threshold crossing and subtle synthesized audio tick.

### 3. Standalone Ergonomics & Safe Areas
- Viewport configuration: `viewport-fit=cover, width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no`.
- CSS Environment Insets:
  ```css
  padding-top: env(safe-area-inset-top);
  padding-bottom: env(safe-area-inset-bottom);
  ```

## Procedure

1. **Scaffold Web App Manifest (`manifest.json`)**:
   - Set `display: standalone`, `orientation: portrait-primary`.
   - Include high-res SVG maskable icons with `purpose: any maskable`.
2. **Register Service Worker (`sw.js`)**:
   - Implement `skipWaiting()` and `clients.claim()` on lifecycle events.
   - Enforce explicit regex routing: Static Cache-First vs API Network-Only.
3. **Mount Tactile Bottom Sheet Container**:
   - Bind touch event handlers (`touchstart`, `touchmove`, `touchend`) to sheet drag handle.
   - Clamp translateY between zero and sheet height.
4. **Enforce Zero-Emoji Policy**:
   - Sanitize dynamic strings and render pure vector SVGs with `stroke-width: 2.2`.

## Pitfalls

- **Service Worker Stale Loop**: Failing to update cache name (`CACHE_STATIC_v2`) causes mobile browsers to serve outdated JS bundles indefinitely.
- **Rubber-Banding Overscroll**: Forgetting `overscroll-behavior-y: contain` causes iOS Safari address bar bouncing during sheet gestures.
- **Broken SSE Streams**: Intercepting SSE or streaming fetch in `FetchEvent` without immediate pass-through corrupts real-time events.

## Verification

1. Run automated PWA audit script:
   `python3 ~/.hermes/skills/creative/pwa-mobile-ergonomics/scripts/pwa_scaffold.py --audit <dir>`
2. Test touch physics and service worker registration in headless Chromium.
