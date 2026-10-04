---
name: zen-agent-companion-interface
description: Use when building zero-scroll zen mobile companion surfaces.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [companion-ui, dynamic-island, zen-interface, spring-physics, zero-emoji, mobile-ergonomics]
---

# Zen Agent Companion Interface

Design and build zero-scroll, high-fidelity mobile companion and mascot surfaces for autonomous AI agents. Prioritizes an uncluttered "zen negative space" home canvas, a prominent living mascot, cohesive multi-agent buddy morphing, and an accessible slide-up bottom sheet for all secondary controls and system configuration.

## When to Use

- Building mobile/desktop web companions, notch HUDs, or mascot interfaces for autonomous AI systems.
- Designing single-screen interactive dashboards where vertical document scrolling ruins the tactile experience.
- Representing multi-agent squads (e.g. Cognitive Engine, Note Clerk, Content Radar, Telemetry Sentinel) as living interactive companions.
- Housing deep system configuration, audio test pads, diagnostics, and emotes inside an unobtrusive slide-up drawer.

Don't use for:
- Traditional multi-page content-heavy blogs, long documentation readers, or tabular admin CRUD grids.
- Native mobile applications requiring platform-specific UIKit/SwiftUI compilation.

## Architecture & Layout Principles

### 1. The 1-Page Zero-Scroll Invariant
- **Viewport Lock & Mobile Keyboard Isolation**:
  ```css
  html, body, .app-viewport {
    width: 100vw;
    height: var(--screen-height, 100lvh) !important;
    min-height: var(--screen-height, 100lvh) !important;
    max-height: var(--screen-height, 100lvh) !important;
    overflow: hidden !important;
    position: fixed !important;
    inset: 0 !important;
    touch-action: none;
  }
  ```
- **The Zero-Scroll Invariant under Mobile Keyboard**: Always add `interactive-widget=overlays-content` to `<meta name="viewport">` and lock `--screen-height` to the initial non-focused window height. Never let `100dvh` or `100svh` shrink the flex layout when the virtual keyboard opens, because shrinking flex containers pushes the central mascot and Dynamic Island upward by ~150px. Only the fixed command bar rises above the keyboard; the mascot stage and header remain 100% frozen in their vertical coordinates.
- No document scrollbar, no bouncing overscroll, no multi-page stacking.
- Three balanced vertical tiers:
  1. **Top**: Dynamic Island stays **hidden in idle**; reveal it only when chat/work is active, then let it act as the agent status/config home with an in-place morphing expansion. Do not add fake phone chrome such as a clock, signal, Wi-Fi, or battery row—the browser/device already supplies system status and duplicating it makes the product feel like a simulator.
  2. **Center**: Spacious Zen Canvas ("home kosongan") housing exactly **one** living central mascot in idle (size ~180x180px, 60 FPS spring physics, continuous eye tracking following touches).
  3. **Bottom**: Clean user command/tool zone: prompt bar, essential session actions, and a minimal utility dock. Do not duplicate the active mascot or scatter agent choices here unless explicitly requested.

### 2. Multi-Agent Ecosystem Parity ("Agent Lain Itu Maskot Juga")
- Every bot or subagent in the ecosystem is represented as a first-class selectable companion identity, not a raw textual list.
- For notch/chat companion UIs, prefer housing the AI agent squad **inside the expanded Dynamic Island** rather than scattering loose agent buttons in the dock:
  - Idle: no Dynamic Island, no duplicate mini mascot; only the one central living mascot is visible.
  - Active chat/work: Dynamic Island appears as the agent's home/status beacon.
  - Expanded Dynamic Island: show a compact 2x2 agent grid (Hermes, Bekagent, SputarAI, SputarBall or project equivalents), response-mode config, and telemetry.
- Tapping any agent tile smoothly morphs:
  - Central mascot theme color, blush intensity, and characteristic eye traits.
  - Dynamic Island identity badge, subtitle, and port/status data.
  - Background radial ambient halo glow.
  - Audio chime signature (e.g. `greet`, `work`, `blip`, `pop`).
- **Independent Per-Agent Visual Identity & Persistence**: Store and synchronize distinct visual customizations (geometry model/shape, body palette, procedural accessories) independently per agent key in persistent storage. When swiping through or opening agent selectors (hold strip, folder modal, island grid), every micro-canvas must immediately reflect that specific agent's saved look rather than defaulting to generic clones. Consolidate bulk appearance morphs into a single `applyLook(look, skipSquash=true)` method to prevent multiple competing `squash()` spring tweens from colliding and causing jerky scale jitter during rapid previews.

### 3. G2 Squircle Bottom Sheet for Settings ("Menu Pengaturan")
- Keep the home canvas radically simple and free of data tables.
- House all rich controls in an off-canvas slide-up drawer:
  - Character geometry morphing (`mochi` squircle, `galet` pill, `lueur` orb, plus extended geometric body shapes such as `prism` hexagonal crystal and `capsule` vertical pill).
  - Procedural character customization: body color palette selector (dynamic 3D gradient recalculation with specular gloss preservation) and zero-emoji procedural accessory layer (e.g. `glasses`, `beret`, `headphone`, `satellite` dish).
  - Eye gaze sensitivity & squash intensity sliders with live numeric feedback.
  - Master volume slider & WAV sound test pads.
  - Instant emote sandbox (happy, wink, proud, surprised, love blush, dizzy).
  - Real backend diagnostic triggers (Ping all bots, PM2 health check).
- Slide-up transition uses rounded corners (`border-radius: 36px 36px 0 0`) and backdrop blur. Border-radius alone is not G2: circular arcs meet straight edges with a curvature jump. Use feature-detected `corner-shape: squircle` for progressive enhancement when appropriate, label the fallback rounded, and do not claim browser pixel geometry is mathematically certified:
  ```css
  .settings-sheet {
    transform: translateX(-50%) translateY(105%);
    transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  }
  .settings-sheet.open {
    transform: translateX(-50%) translateY(0);
  }
  ```

### 4. Integrated Command Bar, Spatial Chat & Telegram Alternative
- **Floating Spotlight Command Input & Auto-Expanding Prompt**:
  - Enclose the input inside a `<form id="cmdForm" action="javascript:void(0);">` so that pressing the virtual software keyboard's "Go", "Search", or "Enter" button on iOS/Android reliably fires the `submit` event.
  - Use an auto-resizing `<textarea class="cmd-input" id="cmdInput" rows="1" placeholder="..." autocomplete="off" spellcheck="false"></textarea>` rather than a rigid `<input type="text">` so long prompts flexibly grow upward when text overflows horizontally:
    * Set the enclosing `.command-bar` to `min-height: 44px; padding: 6px 6px 6px 12px; display: flex; align-items: flex-end; gap: 8px; transition: min-height 0.2s cubic-bezier(0.16, 1, 0.3, 1), border-radius 0.2s;`.
    * Set the textarea to `flex: 1; resize: none; overflow-y: hidden; min-height: 20px; max-height: 110px; line-height: 1.4; word-break: break-word; white-space: pre-wrap; padding: 5px 0;`.
    * Dynamically adjust height on every `input` event:
      ```javascript
      const adjustInputHeight = () => {
        if (!input) return;
        input.style.height = 'auto';
        const scrollH = input.scrollHeight;
        const clampedH = Math.min(Math.max(scrollH, 20), 110);
        input.style.height = `${clampedH}px`;
        input.style.overflowY = scrollH > 110 ? 'auto' : 'hidden';
        const formBar = input.closest('.command-bar');
        if (formBar) formBar.style.borderRadius = scrollH > 35 ? '18px' : '22px';
      };
      ```
    * Keyboard shortcuts: Pressing `Enter` without `Shift` fires `submit` and immediately resets the textarea height back to single-line `height: auto;`; pressing `Shift + Enter` cleanly adds a newline and smoothly expands the input container upward.
  - Explicitly override global touch/selection rules on the text field with `user-select: text !important; -webkit-user-select: text !important; touch-action: manipulation;` to prevent mobile WebKit/Safari from blocking keyboard focus and cursor selection.
  - Docked directly above the bottom companion dock for effortless one-handed thumb reach.
  - **Clean Bottom Tier without Quick-Chip Clutter**: Keep the bottom tier radically uncluttered. Avoid stacking redundant quick-action chip buttons directly beneath the prompt bar—they eat up vertical canvas real estate, produce visual noise, and crowd the dock. The command input bar sits directly and cleanly above the dock in a pure, elegant relationship.
- **Adaptive Spatial Layout Choreography**:
  - **Idle State**: The living mascot stands proud and centered in the spacious zen canvas (`transform: translate(0, 0) scale(1)`).
  - **Chat Entry Timing & Character-to-Island Migration**:
    - Treat the transition from idle to chat as the primary animation, not a fast UI reveal. Use a 1–2 second choreography where the central mascot visibly shrinks/glides into the Dynamic Island before the chat card completes expansion.
    - Use four named motion roles consistently: **EASING** for opacity/text reveal, **TIMING** for fast button taps, **RHYTHM** for loops such as cursor/loading/breathing, and **SPRING/MORPHI** for large shape/state changes such as idle→DI, compact→expanded island, and chat archive→history.
    - Keep collapsed Dynamic Island status text simple (short title + one subline); do not crowd it with verbose operational prose.
  - **Thinking / Processing State (Integrated Exclusively in Dynamic Island)**:
    - The mascot tilts eyes upward in deep focus with a pulsing aura.
    - Enforce a **Guaranteed Minimum Thinking Duration** (at least 1200ms) even if the LLM responds faster, preventing jarring visual flickers and letting progressive stages render palpably.
    - **No Middle Canvas Loading Clutter**: Never mount an obstructive floating thinking card in the middle canvas. All cognitive loading is integrated exclusively into the **Dynamic Island ("Rumah si Agent")**:
      * The Dynamic Island morphs into `.is-thinking` with a pulsing ambient amber glow.
      * Status shifts to `[Agent] • Berpikir di Rumah` with sub-stage feedback (`Menganalisis instruksi...` → `Memanggil kognisi AI...` → `Merumuskan jawaban...`).
      * A neon progress bar (`.island-thinking-bar`) flows across the bottom edge of the island (`25%` → `65%` → `90%` → `100%`), keeping the mascot and chat canvas 100% unobstructed.
  - **Responded / Chat State (Left-Aligned Companion Mascot)**:
    - The canvas switches to flex-column stacking (`.zen-empty-canvas.has-chat { justify-content: flex-start; align-items: center; }`).
    - **Left-Aligned Perch**: Instead of centering the companion above the chat card, anchor the mascot to the **top-left corner** directly above the bot's identity badge (`.zen-empty-canvas.has-chat .big-coucou-stage { width: 76px; height: 76px; transform: scale(0.48); transform-origin: left center; align-self: flex-start; margin-left: 16px; margin-top: -18px; margin-bottom: -12px; z-index: 30; }`). This aligns the mascot with the left-aligned message stream, reinforcing the organic metaphor that the companion is actively speaking the response.
    - When expressing curiosity or asking questions, the mascot transitions to `curious` state: tilted head (`rotate(0.12)`), asymmetric eyes (left eye wide and inquisitive, right eye focused with a raised brow curve).
    - The **Chat Response Card** (`.chat-response-card`) smoothly expands upwards ("molor ke atas") into the central viewport:
      ```css
      .chat-response-card {
        position: relative;
        width: calc(100% - 16px);
        max-width: 375px;
        max-height: 0;
        opacity: 0;
        transform: translateY(20px);
        transition: max-height 0.55s cubic-bezier(0.16, 1, 0.3, 1),
                    opacity 0.35s ease,
                    transform 0.45s cubic-bezier(0.16, 1, 0.3, 1);
        z-index: 20;
      }
      .chat-response-card.expanded {
        opacity: 1;
        transform: translateY(0);
        max-height: calc(100dvh - 265px);
        flex: 1;
      }
      ```
- **In-Browser Telegram Alternative (Full Markdown Threading)**:
  - Render the assistant surface as transparent conversation space, not a dense opaque card: keep the outer thread background/border/shadow transparent, use a light user bubble, and let assistant typography sit directly on the ambient canvas. Add top/bottom opacity masks to the internal scroll viewport so long threads remain readable and clearly scrollable.
  - Support comprehensive multi-turn dialogue with sanitized rich formatting: headings, paragraphs, numbered and bulleted lists, bold, italic, strikethrough, blockquotes, safe links, inline code, and fenced code blocks with language labels.
  - For real Telegram synchronization, emit bounded server-side activity events from the actual private/group bot handlers (`source`, `agent`, `stage`, `summary`, `status`, `timestamp`) into a shared activity store or bus, expose them through authenticated SSE, and render recent work in the Dynamic Island. Never infer or fabricate bot work from telemetry alone; stale events must expire and secrets/chat identifiers must not enter the payload.
  - **Knowledge Engine & Obsidian Vault Parity ("Samakan Knowledge dengan Telegram")**:
    * A browser companion must share the exact same cognitive grounding, facts, and doctrines as the Telegram agent. Do not use an isolated, generic system prompt.
    * Wire the companion's AI inference route directly to the Obsidian vault (`/home/ubuntu/otak-koding/`) using bounded deterministic lexical candidate retrieval (`retrieveCandidates` from `knowledge-analysis.js`).
    * For every incoming user query, scan the vault (`KNOWLEDGE/`, `BUKU_CATATAN/`, `SYSTEM/`), retrieve the top 3 relevant tested notes, and inject their excerpts into the system prompt.
    * Embed the foundational cognitive operating system: user attribution (Bagas Cihuy), Tiga Mindset Problem Solving (Mekanistik-Kausal, Bayesian-Eksperimental, Desain Sistem & Optimasi), exact server port mapping (`:3000`, `:8080`, `:8090`, `:3050`, `:20128`, `/buku`), strict Zero-Emoji compliance, and 98/100 Warm Paper & Obsidian standards.
    * **Real Note Persistence (No Phantom Notes)**: When the user issues a note-taking instruction (`catat: ...` or `/catat ...`), do not simulate the action with static text. Physically write a structured Markdown note with YAML frontmatter (`title`, `status: "CANDIDATE"`, `tanggal`, `penulis`, `agent: "Bekagent"`, `sumber: "Coucou HUD"`) into `/home/ubuntu/otak-koding/BUKU_CATATAN/` with incremented sequence prefixing (e.g. `090-[slug].md`). This ensures the note instantly syncs to the `/buku` web portal and persists for all agents.
    * Support messaging-style slash commands (`/status`, `/catat`, `/buku`, `/ping`, `/help`) seamlessly matching bot conventions.
  - **Integrated Action Controls** in the card header:
    - **Copy Button**: Copies full response text to clipboard in 1 tap with momentary visual feedback.
    - **Speech (TTS) Button**: Triggers browser Web Speech Synthesis (`SpeechSynthesisUtterance`) to voice the response.
    - **Reset Button**: Clears the conversation thread and resets the mascot to center stage.
    - **Minimize / Close Button**: Smoothly collapses the chat card and glides the living mascot back to the center of the zen canvas.

### 5. Dynamic Island ("Rumah si Agent"), Bottom User Tools & Multimodal Engine
- **Dynamic Island as the "Agent's Home" (*Rumahnya si Agent*)**:
  - The Dynamic Island is hidden during idle zen mode; it appears only after chat/work begins.
  - It is the active agent's residence, cognitive status beacon, and compact configuration hub—not a duplicate mascot container.
  - In collapsed state, show only live presence/status and the morph chevron:
    * **Siaga di Rumah**: `[Agent] • Di Rumah` (sub: `Siaga menanti instruksi...` with emerald pulse dot).
    * **Berpikir di Rumah**: `[Agent] • Berpikir di Rumah` (sub: `Menganalisis instruksi...` with amber glow pulse and integrated progress bar).
    * **Merespons**: `[Agent] • Menulis Respon` (sub: `Mengalirkan jawaban ke kartu...`).
    * **Menganalisis Berkas**: `[Agent] • Menganalisis Berkas` (sub: `[nama berkas]`).
  - In expanded state, morph in-place and reveal: AI agent squad selection, response mode config (`Kausal 3-Mindset`, `Ringkas & Cepat`, `Kreatif`), and compact telemetry (CPU/RAM/latency). Keep broad session actions (`+ Baru`, `Riwayat`) near the bottom prompt unless the user asks to move them.
- **Bottom User Controls & Keyboard-Safe Prompt Zone (*Tools User di Bagian Bawah*)**:
  - Put broad session actions beside the prompt as compact icon buttons, not text-heavy pills. Use icon-only `+`/new-chat and history buttons styled like the utility dock, close enough for thumb reach but never overlapping the input field.
  - On mobile keyboard focus, move only the prompt/control block above the virtual keyboard; do not translate the whole page or disturb the zero-scroll canvas. Anchor the command wrapper with fixed positioning and safe-area/keyboard inset handling.
  - `+ Baru`: archives the current thread to `localStorage`, plays a 1–2 second "wrap into history" morph animation, then collapses the chat card and returns to a fresh prompt.
  - `Riwayat`: opens a DI-like compact history panel showing simple conversation titles/snippets.
  - `Mode Respon`: keep active reasoning mode available either in the expanded Dynamic Island or a compact bottom control; avoid duplicating it in multiple places unless the user requests both.
- **Per-Character Monotonic Streaming Engine ("Animasi Ketikan Mengalir Per Huruf")**:
  - Rather than jumping word-by-word or executing full markdown regular expressions on every animation tick (which causes layout thrashing and noticeable freeze/stutter as the response lengthens), use a **Text Node Walker** strategy:
    * Pre-render the full structured Markdown HTML into the chat container once with all styling tags intact (`<p>`, `<strong>`, `<ul>`, `<code>`).
    * Walk the DOM tree using `document.createTreeWalker(container, NodeFilter.SHOW_TEXT)` to collect all text nodes and cache their complete string contents.
    * Temporarily clear each text node's `nodeValue = ''`.
    * Run a monotonic frame loop via `requestAnimationFrame(tick)` with `performance.now()`.
    * Stream characters sequentially across the DOM nodes at calibrated human typing speed (~85–130 chars/sec) with gentle micro-pauses at punctuation marks (`.` `,` `!` `?`), and position a blinking amber cursor (`▌`).
    * Anchor each newly submitted turn once at the top of the internal message viewport, then keep `scrollTop` unchanged while characters stream. Never chase `scrollHeight` during typing—the response must grow downward while the user retains manual control of reading position.
  - Rich accessories such as link cards and file download cards may animate in only after typing completes. Do not append unsolicited follow-up-question chips or recommended replies; they add clutter and undermine the direct conversational flow.
- **DI-Style Simple Morphing History List & Multi-Device Central Sync ("Daftar Simple Morphi Riwayat & Riwayat Tetap Satu")**:
  - **Server-Backed Unified History Across All Devices**: Past conversations must never be trapped exclusively in client-side `localStorage`. In multi-device ecosystems (mobile phone, laptop, tablet), store and synchronize sessions centrally on the server (`GET /coucou/api/sessions`, `POST /coucou/api/sessions`, `DELETE /coucou/api/sessions/:id`, `DELETE /coucou/api/sessions` writing atomically to a state store such as `sessions.json` or SQLite). `localStorage` acts solely as an optimistic cache. Whenever the companion boots or the history sheet opens, sync from the server so a thread started on mobile can be instantly resumed or inspected on desktop with zero fragmentation.
  - Present history as a compact Dynamic-Island-like panel rather than a heavy page. Show simple conversation titles/snippets first; detail can load after selection.
  - Render an ultra-sleek, minimalist list inside the slide-up G2 squircle sheet (`.history-sheet`):
    * **Opening Morph**: Sheet opens with spring physics scaling (`transform: translateY(105%) scale(0.96) -> translateY(0) scale(1); opacity: 0 -> 1;`).
    * **Minimalist Row Layout (`.history-item-simple`)**:
      - Left: Frosted squircle icon with amber chat bubble (`width: 34px; height: 34px; border-radius: 11px;`).
      - Center: Bold single-line session title + subtle timestamp on top; single-line truncated preview snippet below with clean CSS ellipsis.
      - Right: Minimalist delete icon (`✕`) with hover red tint that syncs deletion immediately to the server.
    * **Tactile Spring Squash Feedback**: Tapping an item triggers an instant spring squash (`transform: scale(0.97)`), momentary amber glow border, audio pop, smooth sheet dismissal, and instant thread restoration into the main chat card.
    * Bottom bar: Clean and unobtrusive "Bersihkan Semua Riwayat" action that clears server and local caches simultaneously.
- **File Attachment with Physical Mascot Reaction**:
  - Mount an attach button (`.cmd-attach-btn`) beside the prompt input wired to a hidden file picker.
  - When a file is selected, an emerald preview pill (`.attached-file-pill`) slides in above the command bar with filename, formatted size, and a remove (`✕`) trigger.
  - **Mascot Physical Reaction**: The living mascot immediately reacts physically to the file selection:
    * Eyes tilt downward to look directly at the attachment (`lookY = 1.0`).
    * Body squashes and bounces with surprised delight (`state = 'surprised'; squash(0.55)`).
    * Audio chime `pop` fires.
    * Dynamic Island updates status to `Coucou Menerima Berkas`.
    * Vocal speech bubble asks: *"Wah, ada berkas baru: [filename]! Mau aku analisis apa?"*.
  - When the message is submitted, the attachment metadata is bundled into the API payload so the AI acknowledges and dissects the file with high intellectual curiosity.
- **High Intellectual Curiosity Persona**: The companion AI may explore root causes and propose hypotheses inside the answer, but it must not render separate recommended-response or follow-up-question chips unless explicitly requested.
- **Link Cards**: Structured preview cards with SVG external-link icons, title, and direct URL.
- **File Attachment Cards**: Emerald-tinted file cards (`.chat-file-card`) displaying filename, description, and size. Clicking the download button dynamically synthesizes a `Blob` (`URL.createObjectURL`) for instant, reliable local file download.
- **Reactive Speech & Thought Bubble**:
  - Floats dynamically directly above the mascot's head during casual interactions with a soft pointing tail and spring scale-in animation.
  - Multi-line formatting (`white-space: normal; width: max-content; min-width: 140px; max-width: min(85vw, 320px); word-break: break-word; line-height: 1.4;`). Never apply `white-space: nowrap` or `text-overflow: ellipsis`.
  - Proactive greeting on load (500ms) and playful reactions upon tapping the mascot directly.

### 6. Enlarged Living Agent Folder Container ("Kontainer Pembungkus Agen Hidup")
- **Mobile OS-Style Squircle Folder Architecture**:
  - Wrap the entire multi-agent roster into an **Enlarged Frosted Squircle Folder** inspired by smartphone home screen app folders (HyperOS/iOS/ColorOS).
  - Container box:
    ```css
    .agent-folder-box {
      width: 290px;
      background: rgba(255, 255, 255, 0.12);
      backdrop-filter: blur(36px) saturate(190%);
      -webkit-backdrop-filter: blur(36px) saturate(190%);
      border: 1.5px solid rgba(255, 255, 255, 0.22);
      border-radius: 36px;
      padding: 22px 18px 20px 18px;
      box-shadow: 0 24px 60px rgba(0, 0, 0, 0.75), 0 0 32px rgba(245, 158, 11, 0.12);
    }
    ```
  - Symmetry label: Place the text `"Folder"` (or squad name) directly beneath the container (`font-size: 15px; font-weight: 500; color: #FFFFFF; text-shadow: 0 2px 6px rgba(0, 0, 0, 0.85);`) with clean sans-serif typography.
- **Living Mascot Canvases Inside the Grid ("Agent Tetap Hidup Sesuai Status")**:
  - Inside the grid (e.g. 2x2), **never use static icons or dead illustrations**.
  - Mount an independent 60 FPS micro-canvas (`width: 60px; height: 60px;`) for each agent tile:
    * **Hermes**: White body, glowing amber antenna, focused blush expression, `:80` red badge (*Otak Kognitif*).
    * **Bekagent**: Ice cyan body, curious tilted head, `2` red badge (*Obsidian Vault*).
    * **SputarAI**: Lavender violet body, radar scanning expression, `11` red badge (*Media Radar*).
    * **SputarBall**: Emerald green body, energetic smiling eyes, `:30` red badge (*Portal Skor*).
  - Every micro-mascot runs its own physical loop: blinking independently, breathing, and looking toward pointer interaction.
- **Red Notification Badges ("Lencana Notifikasi Merah")**:
  - Replicate mobile app notification pills mounted at the top-right of each icon wrap (`position: absolute; top: -5px; right: -5px;`):
    ```css
    .agent-noti-badge {
      background: #EF4444;
      color: #FFFFFF;
      font-size: 10px;
      font-weight: 800;
      min-width: 18px;
      height: 18px;
      padding: 0 5px;
      border-radius: 9px;
      border: 1.5px solid #0D1117;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 2px 8px rgba(239, 68, 68, 0.65);
    }
    ```
- **Tactile Pop-in & Two-Tier Glass Peek Interaction**:
  - **Prune Loose Outer Buttons ("Yang di Luar Hapus, Yang di Dalam Dilihat dari Luar")**: Avoid scattering individual agent buttons across the dock alongside a separate folder button. Remove all loose outer agent buttons and consolidate them into a single **Glass Peek Dock Folder** (`.dock-folder-glass`, ~52x52px).
  - **Visible From Outside**: The dock folder features a frosted translucent glass container revealing a 2x2 grid of mini living Coucous directly from the outside, complete with animated eye blinks, signature body colors, active selection ring, and a red notification badge (`4`).
  - **Two-Tier Interaction Architecture**:
    * Direct Quick Switch: Clicking a mini Coucou directly inside the dock folder preview switches the active agent immediately without opening the modal.
    * Modal Expansion: Clicking the surrounding glass container smoothly pops open the full **Enlarged Living Folder Modal** (`@keyframes folderSpringOpen`), displaying large living canvases and complete status diagnostics.
  - Tapping an agent tile triggers tactile squash (`scale(0.92)`), plays that agent's chime signature, smoothly closes the folder, and morphs the main hero mascot to the selected agent.

### 7. Authentic Volumetric Mascot Canvas Engine (Beyond Flat Approximation Trap)
- **Superellipse Curve Formula ($n = 2.7$)**:
  - Never use rigid 2D `ctx.roundRect` or circular `ctx.arc` for organic squircle mascots (Mochi).
  - Trace the perimeter using the superellipse formula over 72 parametric steps to achieve a squishy, dough-like silhouette:
    ```javascript
    for (let i = 0; i <= 72; i++) {
      const a = (i / 72) * Math.PI * 2;
      const ca = Math.cos(a), sa = Math.sin(a);
      const px = rx * Math.sign(ca) * Math.pow(Math.abs(ca), 2 / 2.7);
      const py = ry * Math.sign(sa) * Math.pow(Math.abs(sa), 2 / 2.7);
      i === 0 ? path.moveTo(px, py) : path.lineTo(px, py);
    }
    path.closePath();
    ```
- **4-Layer Volumetric Gradient Lighting**:
  - Layer 1 (Base Tone): Linear gradient from top-right to bottom-left (`createLinearGradient(rx * 0.7, -ry * 0.85, -rx * 0.8, ry * 0.9)`).
  - Layer 2 (Ambient Bottom Tint): Upward fading gradient reflecting agent energy color (`createLinearGradient(0, ry, 0, -ry * 0.25)`).
  - Layer 3 (Radial Inner Shadow): Soft occlusion shadow along bottom perimeter (`createRadialGradient(rx * 0.25, -ry * 0.32, R * 0.15, 0, 0, R * 1.25)`).
  - Layer 4 (Specular Highlight Gloss): Crisp curved gloss reflection at the upper surface (`createRadialGradient(rx * 0.34, -ry * 0.46, 0, rx * 0.34, -ry * 0.46, R * 0.42)`), producing an unmistakable 3D silicone sheen.
- **3D Spherical Gaze Projection & Perspective Foreshortening**:
  - Calculate gaze angles with biological saturation roll-off:
    $$\text{look.x} = \tanh\left(\frac{\Delta x}{260}\right), \quad \text{look.y} = -\tanh\left(\frac{\Delta y}{200}\right)$$
  - Project eyes across a 3D spherical surface:
    $$\text{px} = \sin(\text{yaw}) \cdot \cos(\text{pitch}) \cdot r_x, \quad \text{py} = -\sin(\text{pitch}) \cdot r_y$$
  - Calculate perspective foreshortening scales:
    $$f_x = \operatorname{lerp}(\max(0.18, \cos(\text{yaw})), 1, 0), \quad f_y = \operatorname{lerp}(\max(0.18, \cos(\text{pitch})), 1, 0)$$
  - Clip eye rendering to the body path (`ctx.clip(path)`). When the mascot turns sideways, the far eye realistically foreshortens and wraps around the 3D horizon instead of drifting off into empty air.
- **Kinematic Springs, Organic Breathing & Dynamic Particles**:
  - Use keyframed tweening arrays (`anim(property, [[target, duration, easingFunc], ...], onComplete)`).
  - Continuous differential breathing:
    $$\text{scale}_y = 1 + \sin(t \times 1.8) \times 0.035, \quad \text{scale}_x = 1 - \sin(t \times 1.8) \times 0.02$$
  - Random double-blinks: when a blink triggers, add a 22% chance of firing an immediate second micro-blink 230ms later.
  - Procedural particle emitters (`emit(type, count)`) with velocity, gravity decay, and alpha fading for emotional states: hearts on `love`, stars on `proud`, sparkles on `finish`, sweat droplets on `ratelimit`, and Zzz letters on `sleep`.
  - Waving little hands on greeting (`greet()` sets `s.hands = 1` and oscillates $y$ coordinate by $\sin(t \times 13) \cdot R \times 0.16$).

### 8. Pure CSS/SVG Volumetric Mascot Craft & UI Morphing Kinematics (The Mumu Doctrine)
- **Volumetric 3D Tactile Rendering without Heavy 3D Engines**:
  - Achieve a high-craft tactile robot mascot (like Mumu) using lightweight CSS and SVG rather than heavy WebGL/Three.js bundles:
    * **Ceramic Shell & Subsurface Scattering**: Radial gradient with off-center light source (`radial-gradient(circle at 35% 20%, #ffffff 0%, #fdfcf9 35%, #efe9dd 75%, #ded7ca 100%)`), coupled with multi-tinted inner glow shadows (`inset 0 3px 6px #fff, inset 0 -8px 16px rgba(193, 95, 62, 0.09)`).
    * **Iridescent Rim Aura**: Tri-color gradient blur halo (`#00e5ff`, `#7c3aed`, `#c15f3e`) with soft radial falloff and breathing scale pulse.
    * **Recessed Glass Visor with Inner Bezel & Parallax Depth**: Deep obsidian pill container (`#080c14` with `box-shadow: inset 0 3px 8px #000`), subtle cyan stroke border, and a curved semi-transparent top highlight (`linear-gradient(180deg, rgba(255, 255, 255, 0.28) 0%, transparent 100%)`). Displace the visor within the outer shell with `translateZ(8px)` and directional offsets to generate realistic stereoscopic parallax when the head turns.
    * **Luminous OLED Eyes & Blushing Cheeks**: Cyan-white rounded pills with layered glow (`box-shadow: 0 0 8px #00e5ff, 0 0 16px rgba(0, 229, 255, 0.85)`). Pair with subtle pink/amber blushing cheeks (`.mumu-blush`) that softly illuminate on touch or happy reactions.
- **Anti-Elongation Squircle Proportions ("Anti-Lonjong Invariant")**:
  - Never design mascot dimensions taller than they are wide (e.g. 118px width by 142px height with egg-shaped radii), and never bias harmonic breathing vertically ($scale_y$ expanding while $scale_x$ contracts). An elongated egg silhouette feels stiff, alien, and "lonjong".
  - Enforce chubby, plump squircle geometry (width >= height, e.g. 136px by 124px, with 46%–50% curvature radii) and lateral breathing bias ($scale_x = 1.0 + \sin(t \times 2.0) \times 0.018, scale_y = 1.0 + \sin(t \times 2.0) \times 0.012$) so the mascot looks cuddly, rounded, and living.
- **3D Perspective Rig & Continuous Kinematics (Anti-Stiffness Invariant)**:
  - Never animate the mascot with isolated 2D translation keyframes alone (which makes the character feel rigid, flat, and robotic).
  - Wrap the character in a 3D perspective rig (`perspective: 800px; transform-style: preserve-3d;`).
  - Calculate dynamic 3D head orientation (yaw, pitch, roll) driven continuously by pointer/touch offsets normalized to window dimensions:
    ```javascript
    targetYaw = Math.max(-25, Math.min(25, (deltaX / winW) * 45));
    targetPitch = Math.max(-18, Math.min(18, -(deltaY / winH) * 35));
    targetRoll = Math.max(-12, Math.min(12, (deltaX / winW) * 20));
    currentYaw += (targetYaw - currentYaw) * 0.12;
    currentPitch += (targetPitch - currentPitch) * 0.12;
    currentRoll += (targetRoll - currentRoll) * 0.12;
    ```
  - Apply the dynamic rotation matrix together with harmonic breathing and hovering float:
    `rig.style.transform = translateY(${floatY}px) scale(${scaleX}, ${scaleY}) rotateY(${currentYaw}deg) rotateX(${currentPitch}deg) rotateZ(${currentRoll}deg);`
  - Drive interactive tap/click feedback via Euler-Hooke numerical spring integration ($F = -kx - cv$, impulse $v_0 = -0.38$) rather than canned keyframes to produce an authentic squishy silicone rebound. Enforce coupled volume preservation ($\text{scale}_x = 1.0 + (1.0 - \text{scale}_y) \times 0.6$) so vertical compression forces realistic lateral bulging.
  - Implement biological double-blinking: schedule random intervals (2.4s–5.4s) with a 35% probability of a secondary 110ms micro-blink 120ms after the first, eliminating the uncanny metronome cadence of single-interval CSS animations.
- **Two-Tier Hero-to-Header Morphing Architecture**:
  - **Idle Hero Stage**: Mascot floats centrally in the welcome viewport with synchronized floor contact shadow breathing (`@keyframes mumuShadowPulse`).
  - **Fluid State Migration to Sticky Companion**: When conversation starts or messages populate, morph the hero container out via FLIP or smooth spring contraction (`transform: translateY(-40px) scale(0.65); opacity: 0; max-height: 0;`) using `cubic-bezier(0.16, 1, 0.3, 1)` and `cubic-bezier(0.34, 1.56, 0.64, 1)`.
  - Concurrently, activate the mini companion in the top navigation header (`.mumu-mini-wrapper.active-companion`) with an overshoot spring pop (`animation: miniMumuPop 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)`).
  - Synchronize companion state to AI inference: eyes pulse in `thinking` mode during model generation and celebrate with a squash & stretch `happy` bounce (`^ ^`) upon completion.
  - Resetting chat clears the active thread and smoothly expands the hero mascot back into the center stage with elastic spring overshoot.
- **Physics Pointer Tracking with Spring Easing**:
  - Track pointer/touch coordinates across the window and calculate normalized offsets relative to mascot center.
  - Apply semi-implicit Euler or lerp spring interpolation ($k \approx 0.16$) on `requestAnimationFrame`:
    ```javascript
    eyeCurrentX += (eyeTargetX - eyeCurrentX) * 0.16;
    eyeCurrentY += (eyeTargetY - eyeCurrentY) * 0.16;
    const transform = `translate(${eyeCurrentX.toFixed(2)}px, ${eyeCurrentY.toFixed(2)}px)`;
    ```
  - Apply identical proportional vectors to the header mini companion ($0.35\times$ scale) so all mascot avatars across the UI track the user in unison.
- **Mobile Hero Claustrophobia Defense (Horizontal Suggestion Carousel)**:
  - Stacking multiple prompt or suggestion cards vertically on mobile viewports (`max-width: 640px`) consumes >240px of vertical space, crowding the mascot and causing vertical claustrophobia.
  - Convert prompt cards on mobile into a single-line horizontal swipeable carousel (`display: flex; overflow-x: auto; scroll-snap-type: x mandatory; -webkit-overflow-scrolling: touch; scrollbar-width: none;`). Each card spans ~200px with a 2-line clamped summary, reducing vertical consumption to ~68px (freeing >170px of negative space) and keeping the mascot, greeting, and input cleanly above the fold.
- **Mobile Bottom Dock Safe Area Clearance**:
  - Always enforce `padding-bottom: calc(20px + env(safe-area-inset-bottom, 12px))` on fixed or floating bottom docks on mobile. Standard zero-margin docks directly collide with or graze the iOS Home Indicator and Android gesture bar, triggering accidental navigation instead of prompt submissions.

### 9. Atmospheric Canvas Harmonization & Mobile Messenger Chat Ergonomics
- **Ice Blue & Frosted Slate Crystalline Atmosphere**:
  - When designing high-tech companions with glowing cyan OLED eyes or obsidian visors, avoid warm yellow/terracotta paper backgrounds which clash chromatically with cold cyber-optics.
  - Ground the environment in an Ice Blue atmospheric canvas (`linear-gradient(180deg, #EDF4F9 0%, #E3EDF6 50%, #D8E5F1 100%)`) with frosted crystalline glass surfaces (`rgba(255, 255, 255, 0.88)` + 14px backdrop blur), crisp hairline borders, and deep midnight navy accents (`#0E1B31`). This allows pearlescent ceramic shells and neon visors to look luminous, coherent, and premium.
- **Zero-Asset Multisensory Audio & Haptic Synthesis**:
  - Pair physical mascot interactions with zero-asset Web Audio synthesis (zero external audio file dependencies, instant playback, zero network overhead):
    * **Mascot Bounce / Tap**: Rapid frequency-swept sine wave ($460\text{ Hz} \to 780\text{ Hz}$ over 110ms with exponential gain decay to 160ms) paired with `spring_snap` haptic (`[12, 25, 20]` ms).
    * **Prompt Send**: Soft airy whoosh ($340\text{ Hz} \to 620\text{ Hz}$ over 90ms) paired with `subtle_tap` haptic (`[15]` ms).
    * **Agent Response Arrival**: Crystalline double-tone chime (F#5 $740\text{ Hz} \to$ A#5 $932\text{ Hz}$ over 320ms) paired with `success_double` haptic (`[18, 45, 24]` ms).
  - Wrap audio contexts inside gesture handlers (`pointerdown`/`click`) to comply with browser autoplay security policies without throwing unhandled promise rejections.
- **Authentic WAV Sound Engine & Pre-Decoded AudioBuffers (Zero Latency & 0% Idle CPU)**:
  - When elevating companion tactile feedback from synthetic chimes to authentic character voice recordings (e.g. Coucou's 28 authentic WAV files: `greet`, `think`, `finish`, `love`, `pop`, `wink`, `send`):
    * **Avoid `new Audio(url).play()`**: Instantiating audio elements or fetching on each event creates an 80–250ms playback lag and browser garbage collection churn.
    * **Pre-Decode AudioBuffers on First Gesture**: On the first user touch/pointerdown (`{ once: true }`), fetch and decode all character sound assets into an in-memory `Map<string, AudioBuffer>` via `ctx.decodeAudioData(await res.arrayBuffer())`.
    * **Zero-Latency Playback**: Play sounds via lightweight ephemeral `BufferSourceNode` connected to a shared master `GainNode`, guaranteeing instantaneous 0ms response.
    * **Idle Suspension CPU Guard**: An active running `AudioContext` consumes a continuous 1–3% CPU trickle even when totally silent. Implement a 2000ms idle timer after any sound ends: if no new sound plays, call `ctx.suspend()`. Immediately resume on the next `play()`.
    * **Dual Fallback**: If audio buffers are decoding or fail to load, automatically fall back to Web Audio oscillator frequency sweeps (`playSyntheticFallback`).
- **Asymmetric Mobile Messenger Bubble Ergonomics**:
  - Avoid rendering conversational dialogue as symmetric, full-width document cards or heavy editor boxes.
  - Enforce clear asymmetric mobile messenger styling:
    * **User Bubble**: Strongly right-aligned (`align-self: flex-end; margin-left: 18%; margin-right: 0;`), deep midnight navy (`#0E1B31`) with crisp white text, subtle glowing cyan stroke (`border: 1px solid rgba(0, 229, 255, 0.28)`), and tail border-radius (`18px 18px 4px 18px`).
    * **Assistant Bubble**: Strongly left-aligned (`align-self: flex-start; margin-right: 12%; margin-left: 0;`), frosted crystalline white (`rgba(255, 255, 255, 0.95)`), high-contrast dark navy text (`#0B1528`), soft ambient shadow, and tail border-radius (`18px 18px 18px 4px`), flanked directly by the active mini companion visor avatar.

### 10. Character-as-Container Architecture (The Purrweb Living Body Container)
- **The Living Body Chat Card Concept**:
  - Rather than isolating the mascot into a small corner avatar or letting it crowd the top headroom, the character's physical body forms the **main container card** of the entire chat viewport.
  - Outer Canvas: High-contrast pastel canvas (`#D3E5F6` to `#B7CFEB` light gradient, or dark space aura) framing the character's body.
  - Torso Card (`#mumu-living-container`): Pinned white squircle container (`position: absolute; top: 14px; bottom: 0; left: 16px; right: 16px; border-radius: 40px 40px 0 0;`) holding the conversation inside the character's belly/chest.
  - Stationary Head & Visor Anchor: Top apex of the body container houses the static character head (claymorphic ears, antenna over top border, obsidian visor with tracking OLED eyes and blush). It remains 100% stationary (`position: relative; z-index: 25; flex-shrink: 0;`).
  - Independent Inner Scroll Viewport (`#chat-stream`): Only the messages inside the body container scroll (`overflow-y: auto; flex: 1;`). The character's body and face never budge or translate vertically during scrolling ("waktu gilir ke atas atau bawah itu ngga ngikut tubuhnya").
  - Dual-Stop Upper Gradient Mask: Apply `-webkit-mask-image: linear-gradient(to bottom, transparent 0px, transparent 14px, black 38px, black calc(100% - 24px), transparent 100%)` to the chat stream so messages dissolve smoothly beneath the character's chin/visor without harsh clipping.
  - 2×2 Grid Mobile Welcome Cards: Format preset prompt cards in a compact 2×2 grid (`grid-template-columns: 1fr 1fr; gap: 8px;`) so all 4 core prompts stay visible above the fold on mobile viewports.

## Procedure

1. **Establish Fixed Viewport & Ambient Canvas**:
   - Set `100dvh` flex column, prevent browser default pull-to-refresh and rubberbanding.
   - Lay down an orange radial gradient centered above the content, and expose a persisted Settings control that adjusts its opacity/dimming without changing semantic foreground contrast.
2. **Mount Dual 60 FPS Canvas Objects**:
   - Render the micro-mascot inside the Dynamic Island and the hero living mascot in the central zen canvas.
   - Calculate 3D spherical eye gaze projection:
     $$\text{dx} = \frac{x_{\text{pointer}} - x_{\text{center}}}{w_{\text{window}}}, \quad \text{dy} = \frac{y_{\text{pointer}} - y_{\text{center}}}{h_{\text{window}}}$$
   - Apply spring physics damping for squash & stretch on touch/tap.
3. **Mount Gesture-Driven Living Agent Switcher**:
   - Keep one active hero mascot visible. On a ~500ms hold, reveal the other independently animated mascot canvases fanned behind and beside it; do not replace them with text pills or static icons.
   - Capture the pointer on press. While held, map pointer coordinates to immutable opening-time agent anchor points, preview the nearest agent continuously, then commit on release. Preserve a tap/click fallback and cancel cleanly on `pointercancel`.
   - During preview, suppress repetitive toast/audio, optionally provide a bounded haptic tick, and bring only the candidate mascot forward with spring scale/depth. On close, restore the hero to `idle`, explicitly zero current and target tilt, and retain gaze tracking so switching never leaves it permanently leaning or unable to look around.
4. **Implement Nested Settings Drawer**:
   - Hook settings open button to add `.open` class to drawer and backdrop overlay.
   - Allow dismissal via close button (`✕`), backdrop click, drag handle, or Escape key.
5. **Mount Spotlight Command Bar & Reactive Speech Bubble**:
   - Anchor the command bar directly above a minimal dock containing only session navigation and settings. Put audio, diagnostics/ping, ambient dimming, and other utilities inside Settings; do not expose unexplained utility icons in the primary dock.
   - Keep the interaction hint faint and terse (for example, `Sentuh Coucou untuk berinteraksi`) so it does not compete with the mascot.
   - Mount an absolute-positioned speech bubble container above the mascot canvas.
   - Wire submit event to trigger optimistic "thinking" state (upward eye tilt, work chime), call the backend command endpoint asynchronously, and render the vocalized reply with emotional animation.
6. **Verify Zero-Emoji & Accessibility**:
   - 100% SVG vector icons for every glyph.
   - Minimum 44px touch targets on mobile viewports.

## Pitfalls

- **The Flat 2D Canvas Approximation Trap (Mascot Feels Stiff and Dead)**: Hand-rolling a companion mascot canvas using standard `ctx.roundRect()` with flat color fills and 2D linear eye translation (`lookX * offset`) results in a stiff, lifeless cartoon look that fails the high-fidelity tactile bar. Always implement the authentic mathematical model: parametric superellipse geometry ($n = 2.7$), 4-layer volumetric lighting (linear base gradient, ambient energy tint, radial inner shadow, specular gloss highlight), 3D spherical eye projection with non-linear `Math.tanh` gaze tracking and perspective foreshortening clipped to the body path, keyframed spring physics with organic breathing differential, and dynamic particle emission.
- **Cluttered Outside Dock vs Glass Peek Folder Consolidation**: Scattering individual multi-agent buttons across the outer dock while simultaneously providing a squad folder button creates severe visual clutter, exhausts thumb reach on compact mobile viewports (`390px`), and introduces redundant navigation paths. Remove all individual agent buttons from the outside dock and consolidate them into a single **Glass Peek Dock Folder** (`.dock-folder-glass` with a 2x2 grid of mini living Coucous visible from outside) supporting two-tier interaction: direct click on a mini agent triggers a quick switch, while tapping the glass body expands the full enlarged folder modal.
- **Typewriter Re-parsing Stutter & Word Jumping**: Appending streamed text chunks and re-running markdown parser/regexes on every frame causes exponential CPU overhead, layout thrashing, and noticeable stuttering ("macet") as the message grows. Always pre-render the complete structured HTML once, traverse all `NodeFilter.SHOW_TEXT` nodes, stash their contents, and stream characters monotonically via `requestAnimationFrame(tick)` directly across existing DOM nodes with zero regular expression recalculation per frame.
- **Quick-Chip Bottom Tier Clutter**: Placing rows of quick suggestion chips directly below the prompt bar crowds the bottom margin of the screen, creating visual friction against the dock in a zero-scroll zen interface. Omit prompt chip rows beneath the input bar to maintain vertical negative space and direct proximity between prompt and dock.
- **Overcomplicated Multi-Card History Drawer**: Rendering heavy multi-line cards with separate date rows, sub-headers, and borders inside the history sheet makes mobile browsing clunky and slow. Use a sleek, single-row morphing list (`.history-item-simple`: left icon, top bold title + timestamp, bottom 1-line snippet, right delete icon) combined with tactile squash morphing (`scale(0.97)`) on click for seamless thread restoration.
- **Nested Mini-Button Event Bubbling in Dock Folder**: Nesting clickable mini agent buttons (`.mini-folder-agent`) inside an outer interactive dock folder element (`#btnOpenSquadFolder`) causes clicks on a mini agent to bubble up and trigger the folder's click listener, unintentionally popping open the full folder modal instead of executing a quick switch. Always call `e.stopPropagation()` in the mini agent listener and guard the folder wrapper handler with `if (e.target.closest('.mini-folder-agent')) return;`.
- **Dead Icon Syndrome in Agent Grouping Containers**: Rendering multi-agent rosters as static SVG icons or flat PNG images inside grouping containers destroys the organic illusion of an autonomous companion ecosystem. When wrapping agents in an OS-style folder or squad grid, mount dedicated independent micro-canvases (`60x60` px) for each agent tile so every mascot remains physically alive (independent eye blinks, breathing bounce, characteristic status emotes, and red notification pills) even while contained inside the folder.
- **Playwright Strict Mode Locator Collision on Dual Agent Buttons**: Re-using identical data attributes like `data-agent="bekagent"` across both dock buttons and folder tiles causes test locators like `page.locator('button[data-agent="bekagent"]')` to throw strict mode violations (`resolved to 2 elements`). Always namespace container attributes (e.g. `data-folder-agent="bekagent"`) to keep automated testing unambiguous.
- **Streaming Auto-Scroll Reading Theft**: Updating `scrollTop = scrollHeight` on every typewriter frame drags the reader downward and makes earlier lines impossible to inspect. Place the new turn at the top once, stream into prebuilt text nodes without further scroll writes, and keep the internal chat viewport manually scrollable with subtle top/bottom opacity masks.
- **Multi-Device History Fragmentation & Client-Only Storage Trap**: Storing conversation sessions exclusively in browser `localStorage` isolates conversation logs between mobile, tablet, and desktop devices, causing users to lose conversational context when switching screens. Always back sessions with an authoritative central server API (`/coucou/api/sessions`) saving atomically to a server-side state store (`sessions.json` or SQLite), keeping `localStorage` solely as an optimistic local cache and syncing on initial boot and history drawer reveal.
- **Detached File Picker UX Disconnect**: Providing file upload capability without tactile visual feedback or mascot acknowledgment makes the user uncertain whether the file was accepted. Always mount a floating preview pill above the input, update the Dynamic Island live status to `Menerima Berkas`, and trigger a physical mascot reaction (downward eye tracking, surprised squash bounce, and contextual greeting) upon file selection.
- **Single-Line Prompt Input Horizontal Overflow & Dead Wrapping**: Using a standard `<input type="text">` for user prompts causes longer sentences or multi-clause instructions to scroll horizontally out of view, hiding what the user typed and preventing multi-line drafting. Always use an auto-resizing `<textarea rows="1">` housed in an elastic flex container (`align-items: flex-end; min-height: 44px; max-height: 110px;`), dynamically recalculating `style.height = Math.min(Math.max(scrollHeight, 20), 110) + 'px'` on the `input` event, dispatching submit on `Enter` without `Shift`, and resetting height to `auto` on send.
- **Absolute Floating Mascot Overlapping Message Body**: Translating a floating companion with static absolute offsets (`translate(...)`) over an expanding chat card inevitably collides with or occludes lines of response text on long replies. Always switch the parent canvas container to flex-column stacking (`.has-chat { justify-content: flex-start; }`), shrink the mascot smoothly to a dedicated top companion slot (`width: 80px; height: 80px; transform: scale(0.48); margin-top: -24px; margin-bottom: -16px;`), and make the chat card relative (`position: relative; flex: 1; max-height: calc(100dvh - 265px);`) so text collision is structurally impossible.
- **Duplicate Mascot / Always-Visible Dynamic Island Clutter**: Showing a Dynamic Island in idle mode or placing a second micro-mascot inside it breaks the single-character zen illusion and makes the screen feel busy before any work starts. Hide the Dynamic Island until chat/work is active, keep exactly one visible character in idle, then use the expanded island for agent squad selection, response configuration, and telemetry while keeping broad session actions near the bottom prompt.
- **Jarring Visual Flicker from Sub-Second Model Responses (Omitted Thinking Phase)**: When an upstream local LLM responds faster than ~500ms, a thinking indicator flashes instantaneously and disappears before the user can perceive cognitive engagement. Always enforce a **Guaranteed Minimum Thinking Duration** (`Math.max(1200, elapsed)` ms) so progressive thought stages and mascot eye-tilt animations register clearly before morphing to the response card.
- **Dead Attachment Downloads on Static/Proxy Frontends**: Attempting to route file attachment downloads through backend disk endpoints can fail when files are generated dynamically or session state changes. Synthesize downloads client-side via `new Blob([content], { type: 'text/plain;charset=utf-8' })` with `URL.createObjectURL(blob)` for instant, reliable file downloads without round-trip I/O dependencies.
- **Sequential Model Latency Cascades in Multi-Model Fallbacks**: Chaining reasoning-heavy models sequentially with generous timeouts (e.g. 14s each) in a fallback array causes upstream web clients to hit request timeouts (>15s) when handling long complex answers. Put the fastest reliable model with tight token boundaries (`max_tokens: ~380`, timeout ~8.5s) first to guarantee sub-6s time-to-first-thought while preserving rich formatting.
- **Internal vs External Viewport Scrolling Invariant**: When expanding long multi-paragraph responses in a zero-scroll (`100dvh`) viewport, the outer canvas MUST remain `overflow: hidden; touch-action: none;` while the inner message body of the chat card uses `overflow-y: auto; -webkit-overflow-scrolling: touch;`. Never let document body scrollbar leak out when chat expands.
- **Speech Bubble Ellipsis Truncation**: Setting `white-space: nowrap; overflow: hidden; text-overflow: ellipsis;` on a companion speech bubble truncates multi-word conversational AI replies mid-sentence with `...`. Always use multi-line wrapping with auto-height (`white-space: normal; width: max-content; max-width: min(85vw, 320px); word-break: break-word; line-height: 1.4;`).
- **Mobile Virtual Keyboard Dead Submit**: Placing a bare `<input>` without an enclosing `<form>` causes mobile virtual keyboards (iOS Safari, Android Chrome) to ignore the "Go", "Search", or "Enter" soft key. Always enclose the input in `<form id="cmdForm" action="javascript:void(0);">` and listen to the `submit` event.
- **Global `user-select: none` Input Freeze**: Applying `user-select: none` across all elements globally disables cursor placement, text selection, and virtual keyboard focus on mobile WebKit/iOS. Always exempt input elements with `user-select: text !important; -webkit-user-select: text !important; touch-action: manipulation;`.
- **Premature Bubble Timeout on Async LLM**: Setting a short (e.g. 3-second) dismissal timer on the "Sedang berpikir..." state while an upstream LLM takes 4-5 seconds causes the speech bubble to vanish prematurely into an empty gap before the reply arrives, misleading the user into thinking the companion failed to respond. Keep the thinking bubble visible until the resolution callback fires.
- **Speech Bubble Overflow Clipping**: On compact mobile screens, a speech bubble rendered too high can clip underneath the Dynamic Island. Constrain its vertical offset, clamp maximum width (`max-width: min(85vw, 320px)`), and set `pointer-events: none` on the bubble container so it never obstructs touches or dragging on the living mascot canvas.
- **Concurrent Command Submission Race**: Firing new commands while a previous NLP command is in flight causes overlapping speech bubble timers and conflicting emotional states. Disable or throttle the submit trigger until the active bubble finishes or clears.
- **Nested Toggle Event Bubbling**: Clicking a chevron/collapse button nested inside an expandable parent container bubbles up and fires the parent's click listener, immediately reversing the toggled state. Always call `e.stopPropagation()` on nested toggle actions.
- **Canvas DPR Blurriness**: Not multiplying canvas dimensions by `Math.min(window.devicePixelRatio, 2)` causes blurry retina rendering.
- **Procedural Accessory Clipping on Dynamic Morphs**: Mounting accessories as naive absolute overlays causes them to disconnect or distort during squircle/prism body morphs or 3D eye yaw rotations. Always bind accessory drawing directly into the character canvas transform stack using the mascot's head yaw/pitch offsets (`headYaw = Math.sin(s.yaw) * rx * 0.25; headPitch = s.pitch * ry * 0.2;`), preserve 100% SVG/Canvas vector math without emoji glyphs, and conditionally mute default body antennas (like Mochi's top light) when conflicting accessories like satellite dishes are equipped.
- **Audio Context Suspension**: Modern mobile browsers suspend Web Audio until the first user gesture. Initialize or resume `AudioContext` inside pointer/touch handlers, never automatically on page load.
- **Viewport Height Shift (Mobile URL Bar)**: Using `100vh` instead of `100dvh` causes the bottom dock to clip beneath mobile browser navigation bars.
- **Mobile Keyboard Whole-Page Lift & Dynamic Height Shrinkage**: Relying on dynamic units (`100dvh` / `100svh`) for flex-column root viewports causes mobile browsers (especially Android Chrome) to resize the layout viewport when the virtual keyboard appears. When the flex container shrinks from e.g. 844px to 544px, `justify-content: center` immediately shunts the center mascot, Dynamic Island, and backdrop upward by half the keyboard height (~150px), creating a broken, squished layout. Furthermore, relying on `:focus-within { bottom: calc(env(keyboard-inset-height) + offset); }` fails on mobile browsers because `keyboard-inset-height` evaluates to `0px` without the virtualKeyboard API, dropping the input to the screen bottom. Fix this mechanistically by: (1) adding `interactive-widget=overlays-content` to `<meta name="viewport">`; (2) locking `html, body, .app-viewport` to `--screen-height: [window.innerHeight]px` captured on non-focused resize events with `position: fixed !important; inset: 0 !important;`; (3) listening to `visualViewport` resize/virtualKeyboard geometry change to dynamically set `--keyboard-height`; (4) lifting exclusively `.command-wrapper` with `body.keyboard-open .command-wrapper { bottom: calc(var(--keyboard-height, 0px) + env(safe-area-inset-bottom, 0px) + 12px) !important; }`; and (5) enforcing `transform: none !important;` on `.zen-empty-canvas`, `.big-coucou-stage`, and `#dynamicIsland` so the entire background canvas remains 100% frozen in place.
- **Bottom Control Overlap / Off-Screen Icons**: Positioning new-chat/history controls below the prompt with absolute negative offsets can hide them under the dock or crop them off-screen. Layout prompt and compact controls in a grid or inline fixed cluster, reserve bottom padding for the dock, and mark hidden sheets `pointer-events: none; visibility: hidden` so invisible panels never intercept taps.
- **Too-Fast Chat Reveal**: Instantly swapping idle to chat makes the mascot migration feel like a glitch. Give idle→DI→chat card choreography 1–2 seconds and prioritize the character flight into the island before completing the chat expansion.
- **Sticky Tilt After Agent Switching**: Temporarily assigning a curious/tilted state during a long-press selector can leave both `state` and target tilt latched after release, so the hero remains diagonal and gaze appears broken. Close every commit/cancel path by restoring `idle`, zeroing both rendered and target tilt, releasing pointer capture, and clearing switching classes.
- **Moving-Target Drag Selection & Jittery Agent Previews**: Two pitfalls plague gesture-driven mascot carousels: (1) Translating candidate items to the center (`translateX(0)`) during preview moves the element out from under the pointer, causing hit-testing to rapidly toggle between adjacent items and trigger violent shaking ("geter-geter"). Always keep carousel slots fixed horizontally and scale items up in-place (~1.15x) while using monotonic relative-X interpolation (`relX = clientX - stripCenterX`) with fixed quadrant boundary thresholds. (2) Failing to synchronize customized agent appearances (geometry, body colors, accessories) across preview canvases causes agents to look like generic duplicates or flash default styles during drag. Always synchronize every micro-canvas with that agent's persistent look upon opening the switcher, morph the main canvas in real time with `skipSquash=true` to prevent competing keyframe animations, and restore the neutral idle state upon release.
- **Text-Pill Agent Selector Breaks the Living Metaphor**: Showing agent names in a separate chip row after long press disconnects selection from the mascot system. Reveal living micro-canvases fanned behind the hero, hide the already-active duplicate, and show a name only for the current preview candidate.
- **Shallow System Prompt Syndrome (Companion Answers Differ from Messaging Bot)**: Providing a web companion chat interface with a generic 10-line system prompt while the Telegram bot operates on rich vault memories and operational frameworks causes the companion to give disconnected, hallucinated, or generic answers. Always connect the companion's backend directly to the local Obsidian vault using bounded lexical retrieval (`retrieveCandidates`), injecting relevant notes from `KNOWLEDGE/` and `BUKU_CATATAN/` along with the core Tiga Mindset Problem Solving framework and server architecture so knowledge parity between web and messaging platforms is 100% identical.
- **Simulated Note-Taking Disconnect**: Returning a canned success message ("Ide berhasil dicatat...") without performing real filesystem I/O creates phantom notes that disappear upon inspection. Always write physical Markdown files with YAML frontmatter directly into `/home/ubuntu/otak-koding/BUKU_CATATAN/` (incrementing sequence numbers, e.g. `090-...md`), ensuring notes immediately populate the `/buku` Obsidian viewer and persist across sessions.
- **CSS Selector Specificity Washout on Inline Mascot Avatars**: Declaring a general modifier class like `.message-avatar.assistant-mumu` with low specificity (e.g. `0,2,0`) gets overridden by context-scoped ancestors like `.message-row.assistant .message-avatar` declared later in CSS, washing out the dark obsidian visor and glowing eyes with default bubble background/border styles. Always chain the full compound selector `.message-row.assistant .message-avatar.assistant-mumu` and enforce `!important` on core physical attributes (dark visor background, neon border, glowing eyes) so the mascot face maintains authentic visual fidelity in the chat stream.
- **Duplicate Variable Declaration Script Freeze**: In single-page web companions with hot-patched script tags, declaring a top-level state variable (e.g. `let isWaitingForResponse = false;`) in both the global state block and an async handler block throws `SyntaxError: Identifier '...' has already been declared`, which silently halts the script before helper functions attach to `window` and causes runtime `ReferenceError`. Always run a deterministic syntax probe (`node -e "new Function(...)`) immediately after patching complex script tags.
- **The Mascot Stiffness Pitfall (Isolated 2D Keyframes vs 3D Rig Kinematics)**: Animating a mascot character purely with canned 2D CSS floating keyframes (`@keyframes float { 50% { transform: translateY(-8px); } }`) makes the companion feel robotic, rigid, and emotionally dead ("masih kaku"). Always wrap the character in a 3D perspective rig (`perspective: 800px; transform-style: preserve-3d;`), dynamically interpolate 3D head orientation (yaw, pitch, roll) tracking pointer coordinates via spring dampening ($k \approx 0.12$), displace sunken visors with stereoscopic parallax (`translateZ(8px)` + gaze offsets), and drive interactive click reactions through Euler-Hooke numerical spring integration ($F = -kx - cv$) with coupled volume compensation ($\text{scale}_x = 1.0 + (1.0 - \text{scale}_y) \times 0.6$) for authentic squash & stretch bounce.
- **The Mobile Hero Claustrophobia Trap (Stacked Cards vs Horizontal Carousel)**: Stacking multiple suggestion or prompt cards vertically on mobile viewports (`390×844`) consumes >240px of vertical height, choking negative space, pushing primary elements off-screen, and suffocating the central mascot ("sempit banget kalau di mobile"). On mobile (`max-width: 640px`), convert stacked suggestion cards into a single-line horizontal swipeable carousel (`display: flex; overflow-x: auto; scroll-snap-type: x mandatory; -webkit-overflow-scrolling: touch; scrollbar-width: none;`). Each card spans ~200px with a 2-line clamped summary, slashing vertical height consumption from ~240px to ~68px (freeing >170px of negative space) and preserving the airy Zen Canvas feel above the fold.
- **Mobile Bottom Dock Home-Indicator Collision**: Declaring zero or minimal bottom padding on fixed or floating command docks causes input fields and action buttons to collide with or uncomfortably graze the mobile home indicator bar and gesture pill on modern devices (iPhone 12–15, Android gestural nav). Always enforce `padding-bottom: calc(20px + env(safe-area-inset-bottom, 12px))` on mobile viewport docks to guarantee comfortable thumb clearance and prevent accidental OS app-switching gestures.
- **Warm Paper vs Cool Cyber-Optic Palette Clash**: Placing a companion mascot with cold electric cyan glowing OLED visors or chrome highlights into a warm yellow/terracotta paper background creates jarring chromatic dissonance. Ground cyber-companion interfaces in an Ice Blue & Frosted Slate palette (`#EDF4F9` gradient, `#0E1B31` midnight navy, frosted crystalline cards with 14px blur) to achieve visual harmony and specular radiance.
- **Symmetric Document-Block Chat Trap in Mobile Companions**: Rendering conversational dialogue turns as wide, symmetric rectangular cards makes the companion feel like a static document editor rather than an interactive chat partner. Enforce asymmetric mobile messenger bubble styling (user right-aligned in midnight navy with subtle cyan glow, assistant left-aligned in frosted crystalline white with mini companion avatar) to preserve clear conversational rhythm, high text contrast, and thumb ergonomics.
- **Audio Tag Latency & CPU Bleed vs Decoded AudioBuffer SoundEngine**: Using `new Audio('/sounds/file.wav').play()` on every user interaction introduces an 80–250ms playback lag that ruins the snappy springiness of tactile interactions, while leaving an `AudioContext` permanently running bleeds 1–3% background CPU. Always preload and decode audio assets into memory buffers on the first user pointerdown (`decodeAudioData`), trigger playback with ephemeral `BufferSourceNode` objects connected to a master gain node for instant 0ms latency, and automatically suspend the context after 2 seconds of silence (`ctx.suspend()`) to maintain zero background CPU drain.
- **The "Lonjong" Mascot Egg Proportion Pitfall**: Setting mascot container height greater than width with an asymmetric egg-shaped border-radius and vertical harmonic breathing makes the mascot look oblong, rigid, and awkwardly stretched ("terlalu lonjong"). Enforce squircle/chubby dimensions where width >= height (e.g. 136×124px) with symmetric 48%–50% curvature and lateral breathing expansion.
- **The Character Scroll Drift Trap**: In Character-as-Container architectures, letting the outer character body or facial elements scroll along with the chat messages breaks the physical container illusion and causes the mascot's eyes to disappear off the screen. Keep the character card and face strictly pinned (`position: absolute; overflow: hidden;`) and let only `#chat-stream` scroll (`flex: 1; overflow-y: auto;`), ensuring the character's body remains completely static during scrolling ("waktu gilir ke atas atau bawah itu ngga ngikut tubuhnya").
- **Mascot-Navbar Headroom Collision (The Antenna Clipping Pitfall)**: In Character-as-Container layouts where the mascot head straddles the top border of the torso container, setting container `top` too close to the header navbar (e.g. mobile navbar `52px` vs container `top: 56px` with antenna at `top: -16px`) causes the antenna orb and ears to collide with or clip into the header title. Always enforce mathematical headroom: `container_top - navbar_height >= antenna_negative_offset + 6px` (e.g. mobile: navbar `52px`, container `top: 74px`, antenna `-16px` leaves `6px` clean breathing space; desktop: navbar `64px`, container `top: 92px`, antenna `-24px` leaves `4px` clean breathing space).
- **Sub-Pixel Micro-Jitter & GPU Style Thrashing (Settled Threshold Gate)**: Writing `style.transform` to the DOM on every `requestAnimationFrame` using continuous float values (`toFixed(4)`) forces style recalculations and GPU churn on every frame even when the mascot is resting at idle, creating perceptible micro-vibrations ("getarnya getar banget kurang mulus"). Always use critically-damped spring physics ($\zeta \approx 0.92$, tension `0.055`, damping `0.86`) paired with a settled dead-zone clamp (`Math.abs(squashScaleY - 1.0) < 0.001 && Math.abs(squashVelocity) < 0.0004`) AND a DOM write gate: cache `lastEyeTransform` and `lastBezelTransform`, skipping `element.style.transform = ...` writes completely when deltas are below `0.01px`. This drops idle CPU/GPU consumption to 0% and eliminates micro-shaking.
- **Floating Dock Bottom Message Occlusion Trap**: In chat companion layouts featuring a floating bottom prompt dock (~100–120px tall), applying standard bottom padding (e.g. `80px` or `140px`) to the scroll container causes the bottom of the last message, action buttons (Copy, Regenerate), or token metadata badges to be occluded beneath the floating dock when scrolled to bottom. Enforce generous bottom clearance on the message viewport (`padding-bottom: 210px` on mobile/desktop) paired with a dual-edge opacity mask (`mask-image: linear-gradient(to bottom, transparent 0px, black 24px, black calc(100% - 110px), transparent 100%)`) so the entire final message and its action row rest cleanly above the dock.
- **Dynamic Motion Morphi Glass Specular Tracking**: Static frosted glass can look flat or milky under low opacity. Elevate surfaces to authentic Apple visionOS / iOS 18 "motion morphi glass" by pairing deep saturation blur (`backdrop-filter: blur(36px) saturate(210%)`, `border: 1px solid rgba(255, 255, 255, 0.95)`) with an interactive specular sheen overlay (`#container::before { background: radial-gradient(850px circle at var(--sheen-x, 50%) var(--sheen-y, 0%), rgba(255, 255, 255, 0.48) 0%, transparent 65%); }`). Dynamically interpolate `--sheen-x` and `--sheen-y` on pointermove/touchmove to produce living specular refraction.
- **Inline Code Chip Line-Height Disruption**: Declaring `display: inline-block` with vertical padding on inline code snippets (`:not(pre) > code`) disrupts paragraph vertical cadence and slices through line-heights on compact mobile screens. Use `display: inline; padding: 1.5px 6px; margin: 0 2px; border-radius: 6px; box-decoration-break: clone; -webkit-box-decoration-break: clone;` with baseline alignment so inline chips wrap naturally without breaking line rhythm.
