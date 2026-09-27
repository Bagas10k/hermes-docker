---
name: vibe-coding-accelerator
description: Accelerate vibe coding with live artifacts and rapid flow.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [vibe-coding, flow-state, rapid-prototyping, live-preview, generative-ui]
    related_skills: [claude-design, sketch, spike]
---

# Vibe Coding Accelerator

Vibe coding is the flow-state paradigm where ideas translate into living, interactive software at conversational speed. The agent acts as an intuitive engineering copilot that absorbs vibes, sketches, and natural language intent, then materializes zero-friction interactive artifacts with instant feedback loops.

## When to Use

- User wants to rapidly build an idea without getting bogged down in boilerplate, package configs, or setup friction.
- User describes a software concept through mood, aesthetic, metaphors, or rough user flow ("bikin aplikasi catatan tapi gayanya neo-brutalist tactile").
- Fast prototyping: creating standalone interactive HTML/JS prototypes, visual components, or live playgrounds.
- Iterative visual refinement: sculpting UI feel, motion curves, typography, and micro-interactions conversationally.
- Don't use for: deep low-level kernel driver development, formal mathematical theorem proving, or complex database migration rollback dry-runs.

## Prerequisites

- Modern browser environment or headless browser verification via `browser_exec`.
- Standard web standards: HTML5, CSS3, modern JavaScript (ES Modules, Canvas, Web Audio API).
- Zero mandatory build tools: prefer zero-install CDN libraries (Tailwind CDN, Lucide Icons, Alpine.js, Chart.js, Three.js) for instantaneous turnaround.

## Quick Reference

- **Zero-Build Sandbox Shell**: Standalone HTML file with Tailwind CDN, standard fonts, and Lucide icons.
- **Instant Visual Test**: `browser_exec` -> `goto_url("file://...")` -> `capture_screenshot()`.
- **Sensory Audio Feedback**: Web Audio API procedural synthesis for clicks, notifications, and tone cues without external audio assets.
- **Speculative Mocking**: In-memory reactive state stores with simulated asynchronous delays (`setTimeout`) and fake data generators.

## Core Pillars of High-Vibe Coding

1. **Zero-Setup Velocity**: Ship runnable, self-contained artifacts immediately. Eliminate 15-minute `npm create`, bundler configurations, and dependency resolution steps during ideation.
2. **Sensory Tactualism**: Code must feel good to touch and interact with. Include micro-animations, active press states, sound synthesis, and mobile viewport ergonomics.
3. **Conversational Sculpting**: Treat code as clay. When the user asks for adjustments ("buat lebih cerah", "tambah animasi pegas"), perform surgical adjustments using `patch` rather than discarding the working prototype.
4. **Zero-Emoji Discipline**: Preserve professional aesthetics. Use clean typography, crisp geometric badges (`[LIVE]`, `[RUN]`, `[•]`), hairline borders, and calibrated chromatic palettes instead of distracting emoji clutter.

## Procedure (The Vibe Coding Loop)

### 1. Intent & Vibe Distillation
Capture the core energy and purpose in 3 foundational vectors:
- **Aesthetic Vibe**: Color palette mood (e.g., Warm Paper & Obsidian, Neo-Brutalist High-Contrast, Swiss Editorial, Vibrant Sunset Glow).
- **Interaction Rhythm**: Snappy (spring physics, instant responses) vs Zen (smooth fades, ambient transitions).
- **Functional Core**: The single interactive mechanic that makes the prototype exciting right now.

### 2. Scaffold Self-Contained Artifact
Construct a single-file executable prototype using modern zero-build patterns:
```html
<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Vibe Prototype</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
  <style>
    /* Tactile micro-interactions and smooth spring transitions */
    .tactile-btn:active { transform: scale(0.97); }
    .glass-card { background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(8px); }
  </style>
</head>
<body class="bg-slate-50 text-slate-900 min-h-screen">
  <!-- Interactive reactive container -->
</body>
</html>
```

### 3. Add Web Audio Procedural Sonification (Flow Cues)
Audio is optional and off by default; silent prototypes remain valid. For operational integration use `ambient-sonification-flow` with explicit gesture unlock, mute, bounded voices, hidden-tab suspension and cleanup. The minimal sketch below is illustrative only; do not ship it without those lifecycle controls. No concentration or dopamine benefit is established by this example.
```javascript
const AudioVibe = {
  ctx: null,
  init() { if (!this.ctx) this.ctx = new (window.AudioContext || window.webkitAudioContext)(); },
  playClick() {
    this.init();
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.frequency.setValueAtTime(600, this.ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(150, this.ctx.currentTime + 0.05);
    gain.gain.setValueAtTime(0.15, this.ctx.currentTime);
    gain.gain.linearRampToValueAtTime(0.01, this.ctx.currentTime + 0.05);
    osc.connect(gain); gain.connect(this.ctx.destination);
    osc.start(); osc.stop(this.ctx.currentTime + 0.05);
  },
  playSuccess() {
    this.init();
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(440, this.ctx.currentTime);
    osc.frequency.setValueAtTime(880, this.ctx.currentTime + 0.08);
    gain.gain.setValueAtTime(0.12, this.ctx.currentTime);
    gain.gain.linearRampToValueAtTime(0.01, this.ctx.currentTime + 0.25);
    osc.connect(gain); gain.connect(this.ctx.destination);
    osc.start(); osc.stop(this.ctx.currentTime + 0.25);
  }
};
```

### 4. Live Verification & Visual Feedback
- Launch or render the file directly.
- Use `browser_exec` with device emulation (e.g. 390x844 mobile portrait) to inspect layout balance, touch ergonomics, and visual hierarchy.
- Deliver real-time status and actionable links to the user.

## Pitfalls

1. **Over-Engineering on Turn One**: Do not scaffold complex build pipelines, TypeScript configs, and multi-folder structures when the user is exploring an idea. Start monolithic, extract modularly later.
2. **Native Mobile Modal Bleed**: Never rely on raw HTML `<select>` or native dialogs in mobile prototypes; always build tactile sliding bottom sheets or inline pill pickers.
3. **Emoji Slop**: Never inject generic emoji icons in buttons or navigation. Use crisp geometric badges, SVG icons, or monospaced text indicators (`[PLAY]`, `[x]`, `[+]`).
4. **Missing Feedback**: Always expose visible progress and result states. Sound must be opt-in and redundant with visible feedback; silence is not a defect and dopamine effects must not be asserted without evidence.

## Verification Checklist

- [ ] Artifact is self-contained and opens without build errors or failed imports.
- [ ] Responsive on both mobile portrait (390px) and desktop viewports.
- [ ] Micro-interactions respond instantly with active states and visual feedback.
- [ ] Zero emoji in markup, scripts, and typography.
- [ ] Working functionality verified through browser rendering or direct terminal inspection.
