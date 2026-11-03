---
name: living-editorial-diorama
description: Use when building living scenic dioramas or 3D tickets.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Diorama, KineticMotion, RetroEditorial, HalftoneShading, TactileSkeuomorphism, WebAudio, 60fps]
    related_skills: [animated-vector-icons, upnormal-ui-architecture, generative-visual-patterns, creative-motion-lab]
---

# Living Editorial Diorama & Tactile Skeuomorphism

Architectural standard and mathematical formulas for crafting living, breathing web hero scenes ("Living Kinetic Diorama") paired with retro-editorial typography, risograph halftone shading, and tactile 3D interactive skeuomorphic components.

## When to Use

- "buatkan living hero / scenic diorama animasi (kereta melintas, balon udara, lanskap pegunungan)"
- "rancang desain retro-modern editorial travel (ala Slowline, Awwwards Site of the Day)"
- "buatkan tiket boarding pass / kartu fisik digital dengan efek kemiringan 3D interaktif kursor (cursor tilt)"
- "terapkan arsiran halftone risograph stipple dot pada SVG murni tanpa gambar raster"
- "integrasikan soundscape atmosferik Web Audio sintetis murni tanpa file MP3 eksternal"

## Core Design Architecture

A **Living Editorial Diorama** combines three sensory layers:
1. **Editorial Typography Hierarchy:** High-contrast display serif (`Instrument Serif`, `Playfair Display`) with an italic emotional clause (`"Take the long way, through the mountains"`), framed by monospaced metadata (`ROUTE 7`, `DEPART 14:20`) and clean sans-serif controls.
2. **Continuous Kinetic Environment:** An SVG multi-layer landscape that loops continuously without human input (moving vehicle, particle exhaust, atmospheric buoyancy, flock paths, real-time synchronized clock).
3. **Tactile Skeuomorphic Micro-Interaction:** A physical digital artifact (boarding pass, passport, compass) hovering with 3D perspective physics, reacting dynamically to mouse pointer coordinates.

---

## 1. 2.5D Tactile Cursor Tilt & Specular Glare Formula

The skeuomorphic card floats above the viewport with a `preserve-3d` context. Tilt angles are calculated relative to card center and clamped to prevent unnatural distortion:

```javascript
// Calculate normalized offset from card center (-1.0 to +1.0)
const rect = card.getBoundingClientRect();
const deltaX = (e.clientX - rect.left - rect.width / 2) / (rect.width / 2);
const deltaY = (e.clientY - rect.top - rect.height / 2) / (rect.height / 2);

const maxTiltDeg = 14;
const rotateY = deltaX * maxTiltDeg;
const rotateX = -deltaY * maxTiltDeg;

card.style.transform = `perspective(1000px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) scale3d(1.02, 1.02, 1.02)`;

// Dynamic Specular Glare (light source follows pointer)
const glareX = ((e.clientX - rect.left) / rect.width) * 100;
const glareY = ((e.clientY - rect.top) / rect.height) * 100;
glareEl.style.background = `radial-gradient(circle at ${glareX.toFixed(1)}% ${glareY.toFixed(1)}%, rgba(255, 255, 255, 0.4), transparent 60%)`;
```

### Physical Skeuomorphic Details
- **Perforated Edge Notches:** Use circular cutout notches at the fold/tear line (`width: 18px; border-radius: 50%; background: var(--bg-canvas)`).
- **Parametric Barcode:** SVG `<rect>` elements with randomized alternating widths (`1px`, `2px`, `3px`, `4px`) and dashed separator lines.
- **Verification Stamp:** Monospace angled badge (`transform: rotate(-12deg); border: 2px solid var(--terracotta)`).

---

## 2. Risograph Halftone Stipple Shading (Pure SVG)

Avoid raster textures or heavy PNG overlays. Define reusable SVG `<pattern>` tiles for ink-printed halftone dot shading:

```xml
<defs>
  <!-- Primary Halftone Stipple Pattern -->
  <pattern id="halftone-dots" x="0" y="0" width="8" height="8" patternUnits="userSpaceOnUse">
    <circle cx="2" cy="2" r="1.2" fill="#2A5442" opacity="0.45"/>
    <circle cx="6" cy="6" r="0.9" fill="#2A5442" opacity="0.35"/>
  </pattern>
  
  <!-- Deep Shadow Stipple Pattern -->
  <pattern id="halftone-shadow" x="0" y="0" width="6" height="6" patternUnits="userSpaceOnUse">
    <circle cx="3" cy="3" r="1.4" fill="#183D2D" opacity="0.6"/>
  </pattern>
</defs>

<!-- Applied directly as fill over mountain polygons or viaduct arches -->
<polygon points="280,110 440,280 280,280" fill="url(#halftone-dots)"/>
```

---

## 3. Kinetic Diorama Motion Loops

### A. Vehicle Traverse & Particle Smoke Kinematics
- **Vehicle Movement:** Constant linear translation across the bridge span (`animation: train-traverse 14s linear infinite`).
- **Smoke Puff Emission:** Multiple staggered circles emerging from smokestack with expanding scale and decaying opacity:
  ```css
  @keyframes steam-puff {
    0% { transform: translate(0, 0) scale(0.6); opacity: 0.85; }
    100% { transform: translate(-35px, -45px) scale(2.2); opacity: 0; }
  }
  ```

### B. Atmospheric Buoyancy (Hot Air Balloon Bobbing)
- Alternating gentle vertical displacement combined with subtle pendular roll ($+1.5^\circ \to -1.0^\circ$):
  ```css
  @keyframes balloon-float {
    0% { transform: translateY(0px) rotate(-1deg); }
    100% { transform: translateY(-24px) rotate(1.5deg); }
  }
  ```

### C. Live Real-Time Synchronized Clockwork
- Station analog clock hands and digital timetable must bind to real system `Date()` seconds and minutes, creating visceral continuity between user reality and the virtual scene:
  ```javascript
  const now = new Date();
  const minuteAngle = (now.getMinutes() + now.getSeconds() / 60) * 6;
  const hourAngle = ((now.getHours() % 12) + now.getMinutes() / 60) * 30;
  minuteHand.setAttribute('transform', `rotate(${minuteAngle} 44 12)`);
  hourHand.setAttribute('transform', `rotate(${hourAngle} 44 12)`);
  ```

---

## 4. Zero-Asset Synthetic Web Audio Soundscape

Synthesize living soundscapes directly in JavaScript without fetching large MP3 files:
1. **Mountain Breeze Drone:** Buffer filled with white noise passed through a `lowpass` BiquadFilter (cutoff 320 Hz) at low gain (0.04).
2. **Rhythmic Rail Click-Clack:** Periodic dual-pulse oscillator (`triangle`/`sine`) frequency-ramped down ($85\text{ Hz} \to 35\text{ Hz}$) with fast exponential decay (80ms).
3. **Station Mechanical Stamp:** Mid-frequency punch ($140\text{ Hz} \to 40\text{ Hz}$) triggered on ticket clicks.

---

## Pitfalls & Quality Gates

- **Mobile Viewport Tilt Overflow:** Disable 3D pointer tilt on touchscreens (`window.matchMedia('(pointer: coarse)')`) to avoid janky scroll interference; fallback to static elevation or soft tap-state scale.
- **Pattern Zoom Distortion:** Always set `patternUnits="userSpaceOnUse"` on halftone patterns so dots do not stretch when the parent SVG viewBox resizes.
- **Audio Context Auto-Play Block:** Never start the Web Audio synthesizer automatically on page load. Always gate behind an explicit user gesture (`click` on sound toggle or play button).
- **Excessive Layer Compositing:** Limit active animated SVG groups to $\le 6$ concurrent layers to prevent GPU battery drain on mobile devices.
