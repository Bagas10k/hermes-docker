# Motion Graphic Genres and Terminology Reference

Use this reference when identifying, classifying, or decomposing motion graphics styles, visual reels, and generative animation techniques from video references or client requests.

---

## 1. Primary Taxonomy & Terminology

### Kinetic Typography (Experimental / Brutalist)
- **Characteristics**: Fast-paced typographic cuts, stretching, scaling, elastic text distortion, word-level rhythm synchronization with audio beats, high-contrast monochrome or primary palettes.
- **Visual Markers**: Technical metadata overlays, monospace timecodes (`TC 00:00:02:15`), frame counter readouts (`1920x1080 / 60 FPS`), chapter/segment tagging (`01 / KINETIC TYPE`), viewfinder crop marks at four corners (`┌ ┐ └ ┘`), and calibrated ruler tick-mark tracks along edges.
- **Canvas Materiality Pitfall**: Never assume generic black/dark mode for technical showreels. High-end motion reels frequently use **Warm Paper & Editorial Cream** (`#EFECE6` or `#F3F4F6`), paired with saturated neo-digital contrast (Safety Orange `#FF5C00`, Royal Periwinkle `#4338CA`, Neon Chartreuse `#A3E635`, Carbon Black `#111318`).
- **Standard Use Cases**: Studio showreels, tech keynote teasers, brand manifestos, launch videos.

### Shader & Creative Coding Motion (WebGL / GLSL)
- **Characteristics**: Real-time or programmatically rendered visual effects executing on fragment and vertex shaders rather than pre-rendered keyframe compositions.
- **Core Techniques**:
  - **SDF Raymarching & Volumetric Depth**: Procedural calculation of signed distance fields for raymarched 3D solids, organic fluid metaballs, glass refraction, and chromatic dispersion.
  - **Particle & Point Cloud Dispersion**: Millions of GPU particles forming, dispersing, and morphing into typographic forms or brand marks.
  - **Domain Distortion & Optical Warp**: Non-linear domain warping via Simplex or Perlin noise creating liquid lens distortion, chromatic fringing, and turbulent motion.
  - **ASCII & Terminal Rasterization**: Quantizing luminance buffers into character matrices (ASCII glyphs, block elements, matrix scanlines).

### Neo-Brutalist & Cyberpunk HUD Aesthetics
- **Characteristics**: Raw UI components, exposed layout grid lines, monospaced tabular data, warning accents (safety amber, electric blue, acid green), glitch artifacts, and scanline overlays.
- **Standard Tooling**: Three.js, React Three Fiber, GLSL Shaders, Remotion, Canvas 2D / WebGPU, TouchDesigner, After Effects (with displacement map and optics plugins).

---

## 2. Technique Decomposition Checklist

When the user shares a motion design video or asks "animasi/motion ini namanya apa":
1. **Analyze Subject Matter**: Typography-centric (Kinetic Typography) vs Object-centric (3D Product Render) vs Data-centric (Dashboard/HUD Animation).
2. **Inspect Transitions**: Hard cuts on audio transient peaks, spring-physics scale pops, or continuous camera moves across volumetric space.
3. **Examine Materiality**: Flat 2D vector vs glass/refractive dispersion vs raymarched SDF volume vs particle point cloud.
4. **Identify Overlay Framing**: Technical broadcast borders, timecode bars, aspect ratio indicators, and segment indices indicative of editorial showreels.

---

## 3. Video Reference Decompilation Pipeline

When the user provides a video reference link (Instagram Reels, TikTok, YouTube Shorts):
1. **Download Local Source**: Ingest the video via `yt-dlp`:
   ```bash
   yt-dlp -o "/tmp/motion_ref.%(ext)s" "<URL>"
   ```
2. **Scene-Cut Extraction**: Never rely solely on the video poster or thumbnail. Extract distinct scene cuts via `ffmpeg`:
   ```bash
   ffmpeg -i /tmp/motion_ref.mp4 -vf "select=gt(scene\,0.3)" -vsync vfr /tmp/scene_%02d.png
   ```
3. **Multi-Scene Vision Audit**: Inspect keyframes across diverse chapters with `vision_analyze` to extract:
   - Base canvas color (e.g. warm cream `#EFECE6` vs dark midnight `#0D0E1C`).
   - Saturated accent pairings (Safety Orange `#FF5C00`, Royal Periwinkle `#4338CA`, Chartreuse `#A3E635`).
   - Typographic pairing (compressed heavy display vs monospace technical readouts vs editorial serif italic).
   - Dynamic motion models (elastic stretch, damped spring harmonic snapping, fluid caustics).

---

## 4. Multi-Chapter "1 Style per View" Architecture

When tasked with turning a multi-technique motion showreel into an interactive web artifact:
- **Avoid Single-Page Congestion**: Do not cram 6 distinct visual paradigms onto a single scrolling canvas.
- **Dedicated Chapter Switching**: Build a 100vh Motion Theater where each chapter owns its viewport:
  - Topbar HUD with project metadata (`CLAUDE / MOTION REEL 2026`, `TC 00:00:...`, `60 FPS`).
  - Chapter navigation strip (`01 / KINETIC TYPE`, `02 / HAZARD RHYTHM`, `03 / PARTICLES`, `04 / DEPTH`, `05 / INTERFACE`, `06 / LIQUID`).
  - Isolated stage rendering 100% native web standards (GPU Canvas 2D/WebGL or CSS Transform Matrix, never video/GIF fallbacks).
  - Interactive playback controls: Speed slider (0.2x to 2.5x), play/pause toggle, and mathematical specification dialog.
  - Audio-tactile feedback: Web Audio API procedural synthesis (blip, warp, cyber sweep) on chapter switch.

---

## 5. High-Density Motion Bento Pattern (Frame 023 Signature)

The signature UI/dashboard chapter from high-end motion showreels employs an asymmetrical 5-cell bento layout:
- **Cell 1 (Left Anchor - Giant White Metric)**: Clean white card, monospace micro-header (`ENGAGEMENT`), massive bold metric (`+248%`), upward acceleration curve with soft area fill and peak node point.
- **Cell 2 (Right Top - Saturated System Header)**: Safety orange card, bold title (`Motion system`), monospace pillar badges (`EASING / TIMING / RHYTHM`), and active pill toggle switch with neon lime dot.
- **Cell 3 (Right Middle Left - Dark Status Ring)**: Carbon black card (`#111318`), animated circular donut ring (`99% SMOOTHNESS`).
- **Cell 4 (Right Middle Right - Energy Equalizer)**: Neon chartreuse card (`#A3E635`), 7-bar rounded audio equalizer visualizer (`RHYTHM 120 BPM`).
- **Cell 5 (Bottom Span - Keyframe Timeline Editor)**: Royal periwinkle card (`#4338CA`), editorial italic serif slogan (*"Keyframes are a language."*), parameter track lanes (`POS`, `SCALE`, `ROT`), diamond keyframes, moving orange playhead needle, and tactile `RENDER` CTA.

---

## 6. Impeccable Craft Floor & Anti-Slop Gates for Motion Graphics

- **No Zero-Offset Colored Glows**: Eliminate `box-shadow: 0 0 ... var(--color)`. Replace with crisp 1px hairline borders (`border: 1px solid ...`) or directional elevation shadows.
- **No Undersized UI Text**: All technical micro-labels, HUD timecodes, and chip texts must stay at or above `12px` to prevent high-DPI legibility failures.
- **Intentional Canvas Palette**: When using warm paper/cream backgrounds, calibrate contrast against `#EFECE6` or `#F3F4F6` so that muted text passes WCAG AA (>= 4.5:1 ratio).
- **Zero-Emoji Rule**: Exclusively use precision SVG icons (`lucide-react`). Unicode emojis in technical/motion UI are strictly prohibited.
- **Non-Monotonous Subtitle Dynamics**: Avoid uniform bounce/glow animations on every token. Keep connective words quiet, and apply a single purposeful variation (subtle scale pop, hairline underline sweep, accent tint, or vertical position shift) strictly to verified emphatic words or numbers. Constrain to 2 lines max within mobile safe areas without obscuring speaker faces.
- **SVG-First Concrete Subject Vectors**: Represent abstract concepts (signals, databases, metrics, workflows) using clean procedural or stroked SVGs rather than random unverified raster images or generic wireframe cards.
