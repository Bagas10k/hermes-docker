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
- **Floating Spotlight Command Input**:
  - Enclose the input inside a `<form id="cmdForm" action="javascript:void(0);">` so that pressing the virtual software keyboard's "Go", "Search", or "Enter" button on iOS/Android reliably fires the `submit` event.
  - Explicitly override global touch/selection rules on the text field with `user-select: text !important; -webkit-user-select: text !important; touch-action: manipulation;` to prevent mobile WebKit/Safari from blocking keyboard focus and cursor selection.
  - Docked directly above the bottom companion dock for effortless one-handed thumb reach.
  - Accompanied by horizontal quick-action prompt chips (e.g. `Status`, `Catat Ide`, `Ping All`, `Suara`, `Pusing`) for instant common commands without typing.
- **Adaptive Spatial Layout Choreography**:
  - **Idle State**: The living mascot stands proud and centered in the spacious zen canvas (`transform: translate(0, 0) scale(1)`).
  - **Thinking / Processing State**:
    - The mascot tilts eyes upward in deep focus with a pulsing amber aura.
    - A dedicated **Progressive Thinking Card** (`.thinking-card`) smoothly slides up right above the input bar with live stage feedback:
      * Stage 1: `Menerima pesan & menganalisis instruksi...`
      * Stage 2: `Memanggil kognisi AI & telemetri sistem...`
      * Stage 3: `Merumuskan jawaban komprehensif...`
    - Animated pulsing dots and progress track bar provide immediate tactile reassurance while awaiting model synthesis.
  - **Responded / Chat State**:
    - The mascot smoothly glides to the side or top-right corner (`transform: translate(100px, -140px) scale(0.45); z-index: 35 !important;`) using spring physics easing (`cubic-bezier(0.16, 1, 0.3, 1)`), remaining 100% visible, winking, and attentive.
    - The **Chat Response Card** (`.chat-response-card`) smoothly expands upwards ("molor ke atas") into the central viewport:
      ```css
      .chat-response-card {
        max-height: 0;
        opacity: 0;
        transform: translateX(-50%) translateY(30px);
        transition: max-height 0.5s cubic-bezier(0.16, 1, 0.3, 1),
                    opacity 0.35s ease,
                    transform 0.45s cubic-bezier(0.16, 1, 0.3, 1);
      }
      .chat-response-card.expanded {
        opacity: 1;
        transform: translateX(-50%) translateY(0);
        max-height: calc(100dvh - 250px);
      }
      ```
- **In-Browser Telegram Alternative (Full Markdown Threading)**:
  - Supports comprehensive multi-turn dialogue with rich formatting: clean paragraphs, numbered and bulleted lists, bold emphasis, and dark monospaced code blocks (`<pre><code>`).
  - **Integrated Action Controls** in the card header:
    - **Copy Button**: Copies full response text to clipboard in 1 tap with momentary visual feedback.
    - **Speech (TTS) Button**: Triggers browser Web Speech Synthesis (`SpeechSynthesisUtterance`) to voice the response.
    - **Reset Button**: Clears the conversation thread.
    - **Minimize / Close Button**: Smoothly collapses the chat card and glides the living mascot back to the center of the zen canvas.
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

- **Mascot Obscuration by Expanding Chat Card (`z-index` Layering Conflict)**: When an expanding chat card grows upwards (`z-index: 20`), leaving the companion stage with default stacking context (`z-index: 10`) causes the card to visually swallow or occlude the mascot. Always elevate the companion stage's stacking context to `z-index: 35 !important;` and constrain the chat card's maximum height (`max-height: calc(100dvh - 250px)`) so the mascot floats completely unobstructed in its shifted corner.
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
