---
name: zen-agent-companion-interface
description: Use when building zero-scroll zen mobile companion surfaces.
version: 0.2.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [zen-ui, mobile-companion, zero-scroll, dynamic-island, mascot-kinematics, haptic, audio-synthesis]
---

# Zen Agent Companion Interface

Zero-scroll zen mobile companion surfaces, tactile living agent containers, and volumetric mascot kinematics.

## Supporting References
- `references/unabridged-zen-companion.md`: Full unabridged reference and complete mathematical formulas.
- `references/mascot-volumetric-kinematics.md`: Superellipse $n=2.7$ geometry, 4-layer volumetric lighting, 3D spherical gaze projection, and spring kinematics.
- `references/dynamic-island-and-living-containers.md`: Dynamic island ("Rumah si Agent"), living squircle folders, and Purrweb Character-as-Container architecture.
- `references/companion-pitfalls-catalog.md`: Exhaustive 26KB catalog of mobile viewport traps, scroll drift, and mascot jitter traps.

---

## Core Invariants & Architecture

### 1. The 1-Page Zero-Scroll Invariant
- **Viewport Lock**: Set `html, body { height: 100%; overflow: hidden; position: fixed; width: 100%; }`.
- **Zero Scroll on Mobile**: Enforce `<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, interactive-widget=resizes-content">`.
- Prevent virtual keyboard popups from pushing header/mascot offscreen or causing rubber-band scroll bounce.

### 2. Multi-Agent Ecosystem Parity ("Agent Lain Itu Maskot Juga")
- Every subagent (Pintar, Eksekutor, Pengawas, Kuli) has its own living mascot avatar, color theme, and status state.
- Synchronize status across agents: `IDLE` (gentle breathing), `THINKING` (gaze tracks upward, shimmer), `WORKING` (active tool typing), `SUCCESS` (playful bounce).

### 3. Dynamic Island Capsule & User Dock
- **Dynamic Island ("Rumah si Agent")**: Floating pill at top center (`margin: 12px auto; border-radius: 9999px; backdrop-filter: blur(20px);`). Shows active agent name, status beacon, and quick session switcher.
- **Floating Command Bar**: Bottom prompt capsule with Apple G2 squircle curve (`border-radius: 26px`), auto-expanding upward textarea (up to 140px ceiling), and zero emojis (clean SVG line icons).

### 4. Volumetric Mascot Craft (The Mumu Doctrine)
*(Detailed math and shaders in `references/mascot-volumetric-kinematics.md`)*
- **Anti-Lonjong Proportions**: Maintain squircle aspect ratio ($w:h pprox 1:0.92$ to $1:1$). Never stretch avatars vertically.
- **Critically Damped Spring Kinematics**: Use $k pprox 0.065, c pprox 0.84$. Never apply CSS `transition: transform` on rAF-animated elements.
- **3D Spherical Gaze Projection**: Calculate pupil and specular highlight offsets based on normalized pointer vector $(dx, dy)$ clamped to iris radius.

### 5. Atmospheric Crystalline Palette & Sound Synthesis
- **Canvas Atmosphere**: Crystalline Ice Blue & Frosted Slate (`#F0F4F8` light / `#0B0F17` dark). Two-layer silhouette architecture (95% achromatic, 5% radiant cyan/emerald accent).
- **Zero-Asset Multisensory Feedback**: Synthesize audio clicks and haptic pulses via Web Audio API (`AudioContext` oscillators: 800Hz-1200Hz micro-beeps) unlocked on first user gesture.
- **Asymmetric Mobile Messenger Bubbles**: Right-aligned user bubbles (`align-self: flex-end; max-width: 82%`) and cardless unboxed assistant text directly on canvas.

---

## Critical Pitfalls (Summary)
*(Full 26KB catalog in `references/companion-pitfalls-catalog.md`)*

1. **Mobile Keyboard Viewport Bleed**: Omitting `interactive-widget=resizes-content` causes inputs to submerge under software keyboards.
2. **Simultaneous CSS vs JS Animation Conflict**: Applying CSS transitions to JS spring solvers causes violent 60 FPS jitter (*getar hebat*).
3. **Flat 2D Card Masquerading as Mascot**: Drawing a plain flat SVG box instead of a 4-layer volumetric gradient superellipse.
4. **Unbounded AudioContext Leak**: Instantiating a new `AudioContext` on every sound effect. Reuse a single shared singleton.
5. **Horizontal Breadcrumb Breakout**: Breadcrumb labels forcing horizontal scrollbars on mobile. Enforce `overflow-wrap: anywhere; min-width: 0;`.

---

## Verification Checklist

- [ ] Zero document scroll on mobile (`window.scrollY === 0` during typing).
- [ ] Mascot kinematics run smoothly at 60 FPS without layout thrashing.
- [ ] Web Audio API unlocks cleanly on first tap on iOS Safari and Chromium.
- [ ] G2 squircle curves render smoothly with continuous curvature.
- [ ] All 3 references linked and verified via `skill_view`.
