---
name: upnormal-ui-architecture
description: Design radical, artistic, high-contrast upnormal web UIs.
version: 0.1.0
author: Hermes Agent
license: MIT
related_skills:
  - ui-ux-design-vault
  - motion-ui-lifecycle-and-morphing
  - procedural-vector-graphics
  - graphic-design-elements
  - seo-expert
  - creative-visual-mindset
metadata:
  hermes:
    tags:
      - UpnormalDesign
      - CreativeUI
      - SwissEditorial
      - NeoBrutalism
      - TwoLayerSilhouette
---

# Upnormal UI Architecture

Architect and implement artistic, unconventional, high-contrast "upnormal" web interfaces. Enforces a strict departure from generic AI templates through editorial typographic dominance, 60 FPS in-place fluid morphing, achromatic stage contrast with singular punch accents, and two-layer silhouette rendering.

## When to Use
- User asks for "desain upnormal", "tampilan artistik", "anti-mainstream UI", or "Awwwards / Godly level web".
- When no specific template is mandated and the default must be breathtaking.
- Designing landing pages, portfolios, or luxury dashboards requiring memorable creative identity.

For implementation sequence, preservation of existing behavior, and real-browser verification, also follow `ui-ux-execution-standard`. Upnormal art direction remains project-specific; do not copy the Kasir Bangunan green calendar palette into unrelated products.

## Prerequisites
- Standard web environment: HTML5, CSS3 (Modern Grid, Flexbox, CSS Variables, SVG filters).
- Modern animation engine: GSAP (with Flip plugin) or native CSS transitions with cubic-bezier spring curves.
- Two-layer DOM layout separation (`z-index: 0` for canvas/filter layer, `z-index: 10` for sharp typography).

## How to Run
Invoke component scaffolding and visual verification through the `terminal` tool or inspect rendering using `browser_navigate`.

## Quick Reference
- The 3 Identical Invariants (Wajib Identik & Dipertahankan):
  1. *Physical Blur Glass:* Multi-layered backdrop-filter: blur(12px-24px), semi-transparent hairline border (1px solid rgba(255,255,255,0.08) / rgba(0,0,0,0.08)), two-layer silhouette (text stays 100% sharp on Layer 10).
  2. *Motion Graphics Easing In-Out:* Natural organic acceleration curves (cubic-bezier(0.16, 1, 0.3, 1) or power3.inOut / spring physics). Strictly zero linear robotic motion.
  3. *Fluid In-Place Morphing:* Seamless 60 FPS in-place component morphing (GSAP FLIP / shared layout) from card to expanded view. Strictly zero static blink modal popups.
- In-Place Looping Vector Animations: Embed lightweight (<10KB) procedural SVG vector loops on Layer 0 for living widgets (weather atmosphere, telemetry sine wave, live status). Runs at 60 FPS via GPU transform3d without video files or heavy GIFs.
- Palette: 95% Achromatic (Ink `#111111` / `#222222`, Canvas `#F8F8F8`, Border `#EDEDED`) + 5% Singular Accent (Ember `#FA5D29` / Electric Blue `#49B3FC`).
- Display Typography: `Inter Tight`, `Syne`, or `Cinzel` at `112px-127px`, weight 300-600, line-height `0.93`, tracking `-0.02em`.
- Typographic Emphasis & Punctuation: Actively use deliberate text accents — keyword coloring with singular accent (`var(--accent-punch)`), generous underlined offsets (`text-underline-offset: 4px–6px`, `text-decoration-thickness: 1px–2px`), and monospace/italic sub-phrasing to guide user gaze effortlessly.
- Contrast Floor: WCAG AAA minimal 7:1 against background.
- Motion Standard: 60 FPS in-place morphing (FLIP or spring physics), strictly zero static blink modals.
- Elevation: Zero fuzzy drop-shadows; separation via hairline borders (`1px solid #EDEDED`) and tonal fill shifts.
- Control & Modal Governance: Strictly zero native browser dialogs (confirm/alert), raw OS inputs (<select>, <input type="date">), or browser-default validation bubbles ("Harap isi bidang ini"). All CRUD confirmations, dropdowns, datepickers, and form errors must use custom, theme-cohesive templates (always use `<form novalidate>`).
- Branding Mandate: Direct text-only typography by default. Strictly zero fabricated rounded-box squircle AI logos (e.g. monitor, cart, star) unless official logo assets are provided.

## Procedure

0. **Two-Phase Engineering Protocol (Structure & Function First, Vibe & Styling Second):**
   When building an application or interface from scratch, NEVER attempt full visual polishing at the beginning. Prevent cognitive overload by dividing the build into two distinct phases:
   - **Phase 1 (Barebones Grid & Functional Engine):** Build a clean, structural wireframe layout (CSS Grid / Flexbox containers) and ensure 100% of core system functionality works smoothly (database, CRUD, API endpoints, error handling). Keep aesthetics simple and bare.
   - **Checkpoint (Vibe & Theme Confirmation):** Once the functional system is running and visually clear, pause and ask Mas Bagas directly what aesthetic "vibe" is desired (e.g. Elegant Minimalist, Modern Swiss Editorial, Industrial Console HUD, Fun Playful Neo-Brutalist).
   - **Phase 2 (Aesthetic Craftsmanship & Upnormal Styling):** Search live global references matching the selected vibe, pass candidates through the Hermes Taste Filter, and apply high-contrast upnormal styling without breaking the verified functional engine.

1. **Execute Live Internet Query & Curation via Hermes Taste Filter:**
   Purge 100% of internal model UI memory and LLM training priors. Never guess or hallucinate an interface layout. Follow the master workflow:
   - **Step 1 — Search Live Global References:** Use `web_search` to pull current global references: `"site:godly.website" <topic>`, `"site:awwwards.com" site of the day <topic>`, or GitHub/CodePen vanguard creative code.
   - **Step 2 — Curate through Hermes Skill Taste:** Never copy blindly. Pass every candidate through the Hermes taste filter stored in skills and memory: (1) Achromatic 95% stage + 5% singular punch, (2) WCAG AAA >= 7:1 contrast floor, (3) 60 FPS in-place morphing without static modals, (4) Direct text branding without fake AI logo boxes, and (5) Custom anti-native form controls (modal konfirmasi CRUD, custom select, custom datepicker).
   - **Step 3 — Transparent Citation:** Briefly state the specific inspiration reference (e.g. typography hierarchy, spacing scale, micro-interaction pattern) to the user before writing CSS/markup, proving that styling is grounded in real web design rather than generic model priors.

2. **Establish Achromatic Stage & Punctuation:**
   Define CSS custom properties:
   ```css
   :root {
     --bg-canvas: #f8f8f8;
     --surface-card: #ffffff;
     --border-hairline: #ededed;
     --text-ink: #111111;
     --text-muted: #7a7a7a;
     --accent-punch: #fa5d29; /* Singular focal point */
   }
   ```

3. **Mount Two-Layer Silhouette Architecture:**
   Isolate interactive backdrop from content:
   - Layer 0 (`z-index: 0`, `pointer-events: none`): WebGPU fluid canvas, SVG gooey filter, or organic mesh.
   - Layer 10 (`z-index: 10`): Razor-sharp typography and interactive click targets without filter distortion.

4. **Deploy Extreme Typographic Scale & Direct Text Branding:**
   Establish the hero anchor and header branding using pure typography without fake app-icon boxes:
   ```css
   .hero-display {
     font-family: 'Inter Tight', sans-serif;
     font-size: clamp(64px, 10vw, 127px);
     font-weight: 600;
     line-height: 0.93;
     letter-spacing: -0.02em;
     color: var(--text-ink);
   }
   ```

5. **Implement 60 FPS Fluid Morphing:**
   Replace rigid modal popups with in-place card expansion using GSAP Flip:
   ```javascript
   const state = Flip.getState(card);
   card.classList.toggle('is-expanded');
   Flip.from(state, { duration: 0.6, ease: 'power3.inOut' });
   ```

6. **Hairline Precision & Shadow Ban:**
   Enforce flat, crisp boundaries. Banish fuzzy CSS `box-shadow` in favor of surface tonal contrast and `1px solid var(--border-hairline)`.

## References
Load deep architectural references on demand using `skill_view` (`name="upnormal-ui-architecture"`, `file_path="references/<file>"`):
- `references/archetypes-and-world-styles.md`: Comprehensive guide to the 6 Core World Archetypes (Swiss Editorial, Neo-Brutalism, Liquid Gooey, Console-First, Spatial Tactile, Asymmetric Bento).
- `references/motion-morphing-60fps.md`: Implementation patterns for 60 FPS in-place card expansion via GSAP Flip, spring physics, and zero-blink view transitions.
- `references/anti-ai-slop-checklist.md`: Banned visual patterns, replacement rules, and mandatory pre-flight contrast and performance gates.

## Pitfalls
- **Relying on Model Training Bias (Prior UI Habits):** Never default to the model's unassisted idea of a web UI (generic symmetrical bento boxes, purple-cyan buttons, muddy box-shadows). Always ground designs in live internet curators, explicit user direction, or official Hermes design vault tokens.
- **Accidental Generic Slop:** Never use generic purple/blue AI gradient buttons or decorative status pills that serve no purpose.
- **Fabricated Squircle AI Logos:** Never generate rounded-box icons containing PC monitors, shopping carts, or stars when the user has not asked for a logo; use direct text-only typography for headers and brand titles.
- **Blurring the Text:** Never apply SVG gooey/distortion filters directly to parent containers containing text; always use the Two-Layer Silhouette pattern.
- **Contrast Compromise:** Do not sacrifice text legibility for visual flair; body text must maintain WCAG AAA compliance.
- **Native Browser Dialogs & Raw OS Controls:** Never call `window.confirm()`, `window.alert()`, or render unstyled native `<select>` and `<input type="date">`; native dialogs synchronously freeze JS threads, halt 60 FPS animations, and break design system cohesion. Always provide custom modal dialogs, searchable select popovers, and datepickers that inherit active theme tokens.
- **Native Form Validation Bubbles ("Harap isi bidang ini"):** Never allow browser-default HTML5 validation tooltips to appear; they destroy theme immersion and occlude action buttons. Always apply `novalidate` to `<form>` tags and provide custom inline error text with organic micro-shake physics or blur-glass toasts.
- **Heavy Background Media Trap:** Never embed bulky GIF files or auto-playing HTML5 video tags for minor widget atmospheres (weather, telemetry, status indicators); heavy media spikes RAM and causes layout stutter. Always use lightweight inline procedural SVG vector animations driven by CSS transform3d keyframes.

## Verification
Inspect compiled HTML/CSS with `terminal`:
Verify that display typography uses line-height <= 1.0, contrast ratio exceeds 7:1, drop-shadows are zero, no native confirm/alert calls exist, brand headers use direct text without fake squircle icons, and forms declare `novalidate` with custom validation styling.
