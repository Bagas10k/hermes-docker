---
name: web-agent-chat-runtime
description: Use when building or fixing web chat AI agent interfaces.
version: 0.2.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [web-chat, agents, prompt-engineering, ui-ux, claude-style, runtime]
---

# Web Agent Chat Runtime

Bidirectional web chat interfaces, prompt studios, and streaming runtimes for autonomous AI agents.

## Chat-First Delivery Rules

1. **Room Scope First**: Confirm room scope (app-local room, synced Telegram/WA channel, or multi-human) before designing. Never silently substitute.
2. **Conversation as Primary Surface**: Use persistent sidebar on desktop, slide sheet on mobile. Books, server metrics, and task forms stay companion tools.
3. **Native Agent Runtime Parity**: Bind native Hermes sessions immutably. Preserve tools, skills, memory, plugins, delegation, and approvals. Plain LLM completions is NOT agent parity.
4. **Contract Freeze**: Freeze session/room ownership and SSE event contract before building UI.
5. **Real Evidence Only**: Prove real tool turns, subagent delegation traces, approvals, and reconnects. Exclude raw private credentials.
6. **Zero Slop UI**: Serene empty state, Apple SF Symbols line icons (no emojis in UI), cardless unboxed assistant responses, continuous squircle corners.

## Supporting References
- `references/full-procedure-guide.md`: Unabridged step-by-step engineering procedure.
- `references/pitfalls-and-edge-cases.md`: Complete catalog of 49 runtime traps & edge cases.
- `references/sse-resilience-and-claude-reasoning.md`: SSE handshakes, heartbeats, auto-retry, Claude XML partitioning, rAF 60 FPS streaming queue.
- `references/architecture-recipe.md`: Deep architectural recipe, database schemas, and state transitions.
- `references/chat-first-project-rooms.md`: Multi-agent room access control and state isolation.
- `references/chat-bridge-json-resilience.md`: Messaging bridge adapters (Telegram/WhatsApp) without deadlocks.
- `references/mobile-access-and-public-exposure.md`: Safe reverse proxy and mobile web exposure.
- `references/agent-execution-authority.md`: Permission models and human-in-the-loop approvals.
- `references/telegram-gateway-interactive-feedback.md`: In-chat interactive feedback loops.

---

## Executive Procedure

### 1. Identity, Persistence & Session State
- Reconcile durable session IDs vs ephemeral connection IDs. Bind messages strictly to `(principal_id, room_id, session_id)`.
- Coalesce message completion events by durable message ID. Preserve existing DOM nodes during history reconciliation; never call unconditional `replaceChildren()`.
- Track `activeSessionId` across turns. Sanitize auto-generated titles via regex: `prompt.replace(/^\[(?:Konteks|Gaya)[^\]]*\]\s*/gim, '').slice(0, 36)`.

### 2. Runtime Submission & SSE Streaming
- Stream prompts via native SSE (`POST /api/chat/stream`) with payload-bound idempotency keys (`idempotency_key: uuidv4()`).
- Emit immediate `: keep-alive\n\n` within 100ms. Send periodic heartbeats every 15s to keep proxies/tunnels open.
- Handle stream completion explicitly: handle `event: done` or `data: [DONE]`. Never hang if gateway omits EOF.
- Auto-reconnect with exponential backoff on network drop (`initial: 1s, factor: 1.5, max: 15s`).

### 3. Floating Prompt Dock & Viewport Geometry
- **Floating Dock**: Position with backdrop blur (`backdrop-filter: blur(20px); background: rgba(255,255,255,0.85);`).
- **Container Bottom Clearance**: `#chat-stream` bottom padding must strictly exceed dock height: `padding-bottom: calc(var(--dock-height) + 40px);` (desktop: `180px`, mobile: `185px`).
- **Mobile Virtual Keyboard Pinning (`window.visualViewport`)**:
  - Listen to `resize` and `scroll` on `window.visualViewport`.
  - Calculate: `offsetFromBottom = window.innerHeight - (visualViewport.height + (visualViewport.offsetTop || 0))`.
  - If `offsetFromBottom > 30px`, set `dock.style.bottom = (offsetFromBottom + 6) + 'px'` and scroll feed (`chatStream.scrollTo({ top: chatStream.scrollHeight, behavior: 'smooth' })`). Reset `dock.style.bottom = ''` when keyboard closes.
  - Set `<meta name="viewport" content="width=device-width, initial-scale=1.0, interactive-widget=resizes-content">`.

### 4. Zen Minimalist Canvas (ChatGPT & Claude Parity)
- **Zero Emoji Rule**: Replace all emojis with minimalist SVG line icons (Apple SF Symbols style).
- **Auto-Expanding Squircle Textarea**: Continuous curve `border-radius: 24px-26px`. Smooth expand `transition: height 0.18s cubic-bezier(0.16, 1, 0.3, 1)` up to 140px ceiling.
- **Cardless Assistant Output**: Assistant responses flow freely on canvas without card borders or bubble enclosures. Typography: `margin-bottom: 12px; line-height: 1.7; color: #0f172a;`.
- **Dual-Edge Scroll Gradient Mask**: Apply `-webkit-mask-image: linear-gradient(to bottom, transparent 0px, black 36px, black calc(100% - 90px), transparent 100%);` on `#chat-stream`.
- **Code Block Sandbox & Export**:
  - Isolated opaque-origin iframe preview without `allow-same-origin`.
  - 1-Click `[Unduh File]` button with dynamic extension mapping (`html` -> `landing.html`, `ts` -> `app.ts`, `py` -> `script.py`).
  - Pre elements: `-webkit-overflow-scrolling: touch;` and slim custom scrollbars (`height: 4px;`).
- **Multimodal Image Cards**: Frosted `.chat-image-card`, click-to-expand lightbox, and async blob download (`fetch(url).then(r => r.blob()).then(b => URL.createObjectURL(b))`).
- **KaTeX Formula Typography**: Extract display `$$...$$` and inline `$...$` into collision-free placeholders before HTML escaping. Render offline via local KaTeX bundles.
- **Critically Damped Mascot Kinematics**:
  - Never mix CSS `transition: transform` with rAF JS solvers (causes high-frequency jitter).
  - Use critically damped spring physics (k ≈ 0.065, c ≈ 0.84). Promote to GPU layer (`will-change: transform; transform: translateZ(0);`).
  - Cache geometry anchors outside rAF; update strictly on passive `resize`/`scroll`.
- **Turn-Aware Regeneration**: Pass clicked button to `regenerateResponse(btn)`. Truncate DOM from target turn, slice conversation array to `(0, userIdx + 1)`, and stream in-place.
- **Featherlight 120 FPS Text Animation**: Animate streaming tokens via vertical micro-glide + opacity fade (`@keyframes iosTextReveal { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }`). Forbid animating `filter: blur()` during streaming.

### 5. Table Containment & Micro-Scrollbars
- Wrap markdown tables in `.table-wrap`: `width: 100%; overflow-x: auto; border-radius: 12px; scrollbar-width: thin;`.
- Prevent wide tables from breaking mobile bubble or column width.

### 6. Clipboard Fallback & Utility Toolbars
- Wrap `navigator.clipboard.writeText()` with fallback to hidden `<textarea>` + `document.execCommand('copy')`. Show emerald checkmark (`#10b981`) and 'Tersalin' for 1.8s.
- Bind `Escape` key globally to dismiss lightbox modals, sandboxes, and history drawers.

---

## Top Critical Pitfalls (Summary)
*(Full catalog of 49 traps in `references/pitfalls-and-edge-cases.md`)*

1. **Missing [DONE] Stream Hang**: Gateways dropping `data: [DONE]` cause UI spinners to hang indefinitely. Fallback on HTTP response close event.
2. **Empty Password Admin Bypass**: Passwordless or 1-step registration routes must never treat empty string as valid admin credentials.
3. **CSS Transition vs rAF Solver Jitter**: Attaching CSS `transition: transform` to 60 FPS rAF-animated elements causes violent visual jitter. Use GPU layer promotion and rAF only.
4. **Mobile Scroll Inset & Dock Submersion**: Standard bottom padding leaves media cards cut off behind floating docks. Enforce `padding-bottom: 180px-185px`.
5. **Cross-Origin Image Download Failure**: `<a download>` on cross-origin URLs opens in a new tab instead of downloading. Use `fetch() -> blob() -> createObjectURL()`.
6. **Forced Synchronous Layout Thrashing**: Calling `getBoundingClientRect()` inside an rAF loop forces reflow on every frame. Cache coordinates on passive resize/scroll.
7. **Streaming Code Block Parity Unclosure**: Unclosed backticks during token streaming break markdown rendering. Implement an auto-closing token parser.
8. **Redundant Dropdown Selection Toasts**: Never fire floating toast popups for standard model/thinking effort pill selections. Update pill labels in-place.
9. **Naïve Multi-Turn Regeneration Drift**: Always slice history back to the targeted turn; never append duplicate assistant turns on retry.
10. **HTML Entity Collision in Syntax Highlighting**: Run syntax highlighting before escaping, or unescape entities safely within tokens to prevent double-escaping.

---

## Verification Checklist

- [ ] Zero emoji across entire UI (Apple SF Symbols style SVGs only).
- [ ] Mobile virtual keyboard test on real touch viewport (zero dock overlap or jumping).
- [ ] SSE stream tested with network interrupt (auto-retry reconnects with backoff).
- [ ] Blob export verified for code and media artifacts.
- [ ] KaTeX formulas render offline with zero raw LaTeX string leakage.
- [ ] Mascot kinematics verified at 60 FPS without CSS transition fighting.
- [ ] All 49 detailed pitfalls cross-referenced in `references/pitfalls-and-edge-cases.md`.
