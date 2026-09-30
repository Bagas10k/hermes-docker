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

### 4. Integrated Command Bar & Self-Expression Loop
- **Floating Spotlight Command Input**:
  - Docked directly above the bottom companion dock for effortless one-handed thumb reach.
  - Stylized as a minimalist translucent glass bar with G2 squircle curvature, glowing amber border on focus, and tactile circular send button.
  - Accompanied by horizontal quick-action prompt chips (e.g. `Status`, `Catat Ide`, `Ping All`, `Suara`, `Pusing`) for instant common commands without typing.
- **Reactive Speech & Thought Bubble**:
  - Floats dynamically directly above the mascot's head with a soft pointing tail and spring scale-in animation (`transform: scale(0.9) translateY(4px)` to `scale(1) translateY(0)`).
  - Keeps text ultra-succinct (1 concise sentence, no robotic AI filler).
- **Three-Phase Cognitive-Expression Loop**:
  1. **Thinking Phase**: On command submit, mascot eyes gaze upward, subtle work chime sounds, and bubble displays temporary processing state (*"Sedang memproses..."*).
  2. **Execution Phase**: Asynchronous command dispatch to backend endpoint (`POST /coucou/api/command`).
  3. **Expression & Vocalization Phase**: Mascot body squashes/stretches, eye expression shifts to match context (`happy`, `proud`, `wink`, `surprised`, `dizzy`), audio chime confirms resolution, and bubble reveals the response before auto-fading after 4-6 seconds.

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

- **Speech Bubble Overflow Clipping**: On compact mobile screens, a speech bubble rendered too high can clip underneath the Dynamic Island. Constrain its vertical offset, clamp maximum width (`max-width: min(85vw, 320px)`), and set `pointer-events: none` on the bubble container so it never obstructs touches or dragging on the living mascot canvas.
- **Concurrent Command Submission Race**: Firing new commands while a previous NLP command is in flight causes overlapping speech bubble timers and conflicting emotional states. Disable or throttle the submit trigger until the active bubble finishes or clears.
- **Nested Toggle Event Bubbling**: Clicking a chevron/collapse button nested inside an expandable parent container bubbles up and fires the parent's click listener, immediately reversing the toggled state. Always call `e.stopPropagation()` on nested toggle actions.
- **Canvas DPR Blurriness**: Not multiplying canvas dimensions by `Math.min(window.devicePixelRatio, 2)` causes blurry retina rendering.
- **Audio Context Suspension**: Modern mobile browsers suspend Web Audio until the first user gesture. Initialize or resume `AudioContext` inside pointer/touch handlers, never automatically on page load.
- **Viewport Height Shift (Mobile URL Bar)**: Using `100vh` instead of `100dvh` causes the bottom dock to clip beneath mobile browser navigation bars.
