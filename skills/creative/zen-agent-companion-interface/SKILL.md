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
- **Viewport Lock**:
  ```css
  html, body {
    width: 100vw;
    height: 100dvh;
    overflow: hidden !important;
    position: fixed;
    inset: 0;
    touch-action: none;
  }
  ```
- No document scrollbar, no bouncing overscroll, no multi-page stacking.
- Three balanced vertical tiers:
  1. **Top**: Dynamic Island / Header capsule (live status, identity, expand chevron).
  2. **Center**: Spacious Zen Canvas ("home kosongan") housing the living central mascot (size ~180x180px, 60 FPS spring physics, continuous eye tracking following touches).
  3. **Bottom**: Floating Agent Dock housing companion buddies and primary haptic triggers.

### 2. Multi-Agent Ecosystem Parity ("Agent Lain Itu Maskot Juga")
- Every bot or subagent in the ecosystem is represented as a first-class mascot buddy, not a raw textual list.
- Tapping any agent in the bottom dock smoothly morphs:
  - Central mascot theme color, blush intensity, and characteristic eye traits.
  - Dynamic Island identity badge, subtitle, and port status.
  - Background radial ambient halo glow.
  - Audio chime signature (e.g. `greet`, `work`, `blip`, `pop`).

### 3. G2 Squircle Bottom Sheet for Settings ("Menu Pengaturan")
- Keep the home canvas radically simple and free of data tables.
- House all rich controls in an off-canvas slide-up drawer:
  - Character geometry morphing (`mochi` squircle, `galet` pill, `lueur` orb).
  - Eye gaze sensitivity & squash intensity sliders with live numeric feedback.
  - Master volume slider & WAV sound test pads.
  - Instant emote sandbox (happy, wink, proud, surprised, love blush, dizzy).
  - Real backend diagnostic triggers (Ping all bots, PM2 health check).
- Slide-up transition uses G2 squircle corners (`border-radius: 36px 36px 0 0`) and backdrop blur:
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
  - Accompanied by horizontal quick-action prompt chips (e.g. `Status`, `Catat Ide`, `Ping All`, `Suara`, `Pusing`) for instant common commands without typing. Clicking chips auto-populates the input and recalculates height via `adjustInputHeight()`.
- **Adaptive Spatial Layout Choreography**:
  - **Idle State**: The living mascot stands proud and centered in the spacious zen canvas (`transform: translate(0, 0) scale(1)`).
  - **Thinking / Processing State**:
    - The mascot enters the thinking phase on EVERY query: tilts eyes upward in deep focus with a pulsing amber aura.
    - Enforce a **Guaranteed Minimum Thinking Duration** (at least 1200ms) even if the LLM responds faster, preventing jarring visual flickers and letting progressive stages render palpably.
    - A dedicated **Progressive Thinking Card** (`.thinking-card`) smoothly slides up right above the input bar with live stage feedback:
      * Stage 1: `Menerima pesan & menganalisis instruksi...`
      * Stage 2: `Memanggil kognisi AI & telemetri sistem...`
      * Stage 3: `Merumuskan jawaban komprehensif...`
  - **Responded / Chat State**:
    - The canvas switches to flex-column stacking (`.zen-empty-canvas.has-chat { justify-content: flex-start; }`).
    - The mascot smoothly morphs into an elegant companion at the top of the canvas (`width: 80px; height: 80px; transform: scale(0.48); margin-top: -24px; margin-bottom: -16px; z-index: 30;`), sitting cleanly above the chat card without overlapping a single character of text.
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
  - Supports comprehensive multi-turn dialogue with rich formatting: clean paragraphs, numbered and bulleted lists, bold emphasis, and dark monospaced code blocks (`<pre><code>`).
  - **Integrated Action Controls** in the card header:
    - **Copy Button**: Copies full response text to clipboard in 1 tap with momentary visual feedback.
    - **Speech (TTS) Button**: Triggers browser Web Speech Synthesis (`SpeechSynthesisUtterance`) to voice the response.
    - **Reset Button**: Clears the conversation thread and resets the mascot to center stage.
    - **Minimize / Close Button**: Smoothly collapses the chat card and glides the living mascot back to the center of the zen canvas.

### 5. Multimodal Action Cards, File Attachment & Dynamic Island Live Status
- **Dynamic Island Live Mascot Status & Action Bubbles**:
  - Replace static agent labels in the Dynamic Island with **Real-Time Mascot Cognitive Activity**:
    * **Siaga**: `Coucou Siaga • Menanti instruksi...` (pulsing emerald beacon dot).
    * **Berpikir**: `Coucou Berpikir • Menganalisis pola kausal...` (pulsing amber beacon dot).
    * **Merespons**: `Coucou Merespons • Mengetik jawaban...` (active amber beacon dot).
    * **Menerima Berkas**: `Coucou Menerima Berkas • [nama berkas]` (pulsing cyan beacon dot).
  - Embed tactile **Menu Gelembung (*Action Bubble Pills*)** directly inside the Dynamic Island:
    * `+ Baru`: Starts a new clean session, archives the current thread to `localStorage`, collapses the chat card, and springs the mascot back to the center of the zen canvas.
    * `Riwayat`: Opens the slide-up chat history drawer.
- **Typewriter Streaming Reveal Animation ("Animasi Ketikan Mengalir")**:
  - Rather than dumping the entire Markdown response in a single frame (which creates an abrupt, jarring height leap), stream words and tokens sequentially (~18–22ms intervals) with a blinking amber cursor (`▌`).
  - The chat card smoothly expands in height ("molor ke atas") as sentences flow in, and `body.scrollTop = body.scrollHeight` continuously follows the bottom baseline.
  - Rich accessories (link cards, file download cards, and interactive inquiry chips) animate in with a staggered fade-in *only after* typing stream completes.
- **Slide-up Chat History Drawer & Session Persistence**:
  - House past conversations in `localStorage` under `coucou_chat_sessions` as structured session objects (`{ id, title, preview, time, messages }`).
  - Render a slide-up G2 squircle sheet (`.history-sheet`) featuring total session counts, formatted timestamps, message quantities, title/preview snippets, individual delete buttons, and a global "Hapus Semua Riwayat" button.
  - Tapping any session instantly reloads the entire multi-turn thread into the chat card and expands it smoothly into view.
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
- **High Intellectual Curiosity Persona**: The companion AI acts proactively with high intellectual curiosity—exploring root causes, proposing creative hypotheses, and providing 2–3 thought-provoking follow-up questions.
- **Link Cards**: Structured preview cards with Lucide external-link SVG icons, title, and direct URL.
- **File Attachment Cards**: Emerald-tinted file cards (`.chat-file-card`) displaying filename, description, and size. Clicking the download button dynamically synthesizes a `Blob` (`URL.createObjectURL`) for instant, reliable local file download.
- **Interactive Follow-up Question Chips**: Clickable prompt pills (`.followup-chip`) rendered beneath the bot message. Clicking any chip immediately inputs the question into the command bar and fires the thinking cycle, maintaining continuous effortless dialogue.
- **Reactive Speech & Thought Bubble**:
  - Floats dynamically directly above the mascot's head during casual interactions with a soft pointing tail and spring scale-in animation.
  - Multi-line formatting (`white-space: normal; width: max-content; min-width: 140px; max-width: min(85vw, 320px); word-break: break-word; line-height: 1.4;`). Never apply `white-space: nowrap` or `text-overflow: ellipsis`.
  - Proactive greeting on load (500ms) and playful reactions upon tapping the mascot directly.

## Procedure

1. **Establish Fixed Viewport & Ambient Canvas**:
   - Set `100dvh` flex column, prevent browser default pull-to-refresh and rubberbanding.
   - Lay down an ambient radial mesh gradient reflecting the active agent's energy color.
2. **Mount Dual 60 FPS Canvas Objects**:
   - Render the micro-mascot inside the Dynamic Island and the hero living mascot in the central zen canvas.
   - Calculate 3D spherical eye gaze projection:
     $$\text{dx} = \frac{x_{\text{pointer}} - x_{\text{center}}}{w_{\text{window}}}, \quad \text{dy} = \frac{y_{\text{pointer}} - y_{\text{center}}}{h_{\text{window}}}$$
   - Apply spring physics damping for squash & stretch on touch/tap.
3. **Mount Multi-Agent Dock Switcher**:
   - Render tactile squircle buttons for each agent.
   - Bind click/tap events to trigger concurrent canvas morphing, audio chime, and toast notification.
4. **Implement Nested Settings Drawer**:
   - Hook settings open button to add `.open` class to drawer and backdrop overlay.
   - Allow dismissal via close button (`✕`), backdrop click, drag handle, or Escape key.
5. **Mount Spotlight Command Bar & Reactive Speech Bubble**:
   - Anchor the command bar form directly above the bottom agent dock with quick prompt chips (`Status`, `Catat Ide`, `Ping All`, `Suara`, `Pusing`).
   - Mount an absolute-positioned speech bubble container above the mascot canvas.
   - Wire submit event to trigger optimistic "thinking" state (upward eye tilt, work chime), call the backend command endpoint asynchronously, and render the vocalized reply with emotional animation.
6. **Verify Zero-Emoji & Accessibility**:
   - 100% SVG vector icons for every glyph.
   - Minimum 44px touch targets on mobile viewports.

## Pitfalls

- **Instant Chunk Ingestion Visual Shock (Omitted Streaming Reveal)**: Injecting large Markdown responses in a single DOM update causes the viewport to instantly jump from 0 to full height with no visual continuity. Stream the response tokens word-by-word with an animated cursor (`▌`) and smooth scroll tracking, deferring rich card accessories (links, files, inquiry chips) until the stream finishes.
- **Lost Chat Sockets Without Local Session Persistence**: In single-page zero-scroll apps, refreshing or starting a new query without persisting past conversations permanently destroys conversational context. Save serialized session arrays (`id`, `title`, `preview`, `time`, `messages`) to `localStorage` under `coucou_chat_sessions`, loadable anytime via a slide-up G2 squircle history drawer with per-session deletion.
- **Detached File Picker UX Disconnect**: Providing file upload capability without tactile visual feedback or mascot acknowledgment makes the user uncertain whether the file was accepted. Always mount a floating preview pill above the input, update the Dynamic Island live status to `Menerima Berkas`, and trigger a physical mascot reaction (downward eye tracking, surprised squash bounce, and contextual greeting) upon file selection.
- **Single-Line Prompt Input Horizontal Overflow & Dead Wrapping**: Using a standard `<input type="text">` for user prompts causes longer sentences or multi-clause instructions to scroll horizontally out of view, hiding what the user typed and preventing multi-line drafting. Always use an auto-resizing `<textarea rows="1">` housed in an elastic flex container (`align-items: flex-end; min-height: 44px; max-height: 110px;`), dynamically recalculating `style.height = Math.min(Math.max(scrollHeight, 20), 110) + 'px'` on the `input` event, dispatching submit on `Enter` without `Shift`, and resetting height to `auto` on send.
- **Absolute Floating Mascot Overlapping Message Body**: Translating a floating companion with static absolute offsets (`translate(...)`) over an expanding chat card inevitably collides with or occludes lines of response text on long replies. Always switch the parent canvas container to flex-column stacking (`.has-chat { justify-content: flex-start; }`), shrink the mascot smoothly to a dedicated top companion slot (`width: 80px; height: 80px; transform: scale(0.48); margin-top: -24px; margin-bottom: -16px;`), and make the chat card relative (`position: relative; flex: 1; max-height: calc(100dvh - 265px);`) so text collision is structurally impossible.
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
- **Audio Context Suspension**: Modern mobile browsers suspend Web Audio until the first user gesture. Initialize or resume `AudioContext` inside pointer/touch handlers, never automatically on page load.
- **Viewport Height Shift (Mobile URL Bar)**: Using `100vh` instead of `100dvh` causes the bottom dock to clip beneath mobile browser navigation bars.
