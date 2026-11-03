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
  - upnormal-morph-engine-8point
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
- Motion Standard: 60 FPS in-place morphing (FLIP or spring physics), strictly zero static blink modals. Mematuhi **Target +8 Poin Mesin Morphing**: in-place FLIP math, continuous squircle morphing, two-phase content stagger, universal vector icon morphing, liquid gooey bridge, pegas harmonik teredam (Damped Harmonic Oscillator: zeta=0.88, omega_0=18.0 rad/s, cubic-bezier(0.16, 1, 0.3, 1)), WCAG AAA reduced motion, dan 4-layer progressive glass blur.
- Creative Spacing & Fluid Clamp Doctrine: Gunakan formula matematis linier responsif tanpa jeda breakpoint kaku (`clamp(min_rem, slope*100vw + intercept, max_rem)`). Terapkan ritme editorial asimetris (Golden Ratio 1:1.618 atau Dominansi 2:1), sentuhan target interaktif minimal 44px x 44px (WCAG AAA), serta clearance dock bawah `calc(var(--dock-height) + 48px)` dan `env(safe-area-inset-bottom)`.
- Elevation: Zero fuzzy drop-shadows; separation via hairline borders (`1px solid #EDEDED`) and tonal fill shifts.
- Playful Tactile & Gamified Productivity Archetype: For daily planners, habit trackers, and personal workflow workstations, combine warm oat canvas (`#FAF8F5`) with chunky squircle geometry (`border-radius: 18px–28px`), crisp `2px solid #18181B` borders, tactile hard drop-shadows (`3px 3px 0px #18181B`), state-reactive SVG vector mascot, and zero-asset Web Audio API synthesizers for dopamine checklist feedback.
- Strictly Zero Performative Meta-Badges & Eyebrow Clutter: Never render internal design metrics, audit criteria, or architectural jargon as public badges, kicker tags, or pill strips (e.g. '100% Zero AI Slop', 'WCAG AAA (≥ 7:1)', '60 FPS In-Place Morphing', 'VOL. 02 // PORTFOLIO', 'FIG. 01'). Quality must be experienced through actual interaction, typography, and clean space—never proclaimed via decorative badge clutter.
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

5. **Implement 60 FPS Fluid Morphing (Target +8 Poin & Spring Physics):**
   Replace rigid modal popups with physical in-place expansion using FLIP geometry math and damped harmonic oscillator physics:
   - Hitung koordinat fisik awal: `first = trigger.getBoundingClientRect()`.
   - Posisikan target modal di DOM (`display: block; visibility: hidden;`), ukur `last = modal.getBoundingClientRect()`.
   - Invert: `deltaX = first.left - last.left`, `deltaY = first.top - last.top`, `scaleX = first.width / last.width`, `scaleY = first.height / last.height`.
   - Play via WAAPI atau GSAP Flip dengan kurva pegas `cubic-bezier(0.16, 1, 0.3, 1)` durasi 420ms.
   - Proteksi dua fase: cangkang luar mengembang terlebih dahulu, konten dalam di-reveal bertahap pada $t > 0.35$ agar teks tidak terdistorsi.
   ```javascript
   // Standar eksekusi Upnormal Morph Engine v2.0
   UpnormalMorphEngine.openDialog(triggerEl, surfaceEl, backdropEl, {
     duration: 420,
     easing: 'cubic-bezier(0.16, 1, 0.3, 1)'
   });
   ```

6. **Hairline Precision & Shadow Ban:**
   Enforce flat, crisp boundaries. Banish fuzzy CSS `box-shadow` in favor of surface tonal contrast and `1px solid var(--border-hairline)`.

## 7. Active Negative Space & Spatial Void Architecture (Filosofi 'Ma' 間)
Ruang kosong bukan sekadar piksel mati tanpa fungsi, melainkan unsur fungsional berenergi kinetik setara dengan konten:
1. **Gravitasi Visual & Fokus Monolitik:** Area kosong lapang di sekeliling display headline/CTA menciptakan sumur gravitasi visual tanpa garis tepi atau badge berisik.
2. **Buffer Kognitif & Kecepatan Baca:** Mematuhi Hukum Miller & Hick; ruang kosong bertindak sebagai jeda nafas kognitif pencegah kelelahan mental.
3. **Landasan Pacu Ekspansi Morphing Fisik (Morphing Expansion Runway):** Ruang kosong di sekitar elemen pemicu berfungsi sebagai buffer spasial saat kartu/modal mengembang in-place 60 FPS tanpa menabrak elemen tetangga.
4. **Zona Perlindungan Sentuh & Thumb Sanctuaries:** Ruang aman di layar ponsel untuk scroll tanpa salah memicu klik (anti fat-finger).
5. **Panggung Atmosferik Dua Lapis:** 95% kanvas akromatik terbuka memberi ruang bernafas bagi partikel halus Layer 0 (WebGPU fluid/subtle grain).
6. **Ketegangan Asimetris ('Ma' 間):** Spasi asimetris Golden Ratio (1 : 1.618) menciptakan kemewahan visual khas Awwwards/Godly.
7. **The 4-Distance Rule:** Card Internal Padding > Card-to-Card Gap > Internal Group Gap > Section Gap (dilarang bernilai sama).

## 8. Aspect Ratio Architecture & Solusi "Card Fatigue" (Dekartunisasi)
Menghilangkan penyakit "box soup" (tumpukan kotak/kardus berlebihan yang memakan ruang dan melelahkan mata):
1. **8 Rasio Visual Baku:** `1:1` (Avatar/Icon), `4:3` (Artikel ringkas/modal), `3:2` (Fotografi arsitektur), `16:9` (Video hero), `21:9` (Cinematic strip), `4:5` (Raja mobile carousel/feed), `9:16` (Story layar penuh), `1.618:1` (Golden ratio split-pane).
2. **Aturan CLS = 0:** Selalu sematkan `aspect-ratio: <w>/<h>; width: 100%; object-fit: cover;` pada wadah media agar browser mengalokasikan ruang sebelum aset gambar selesai diunduh.
3. **Kapan BOLEH Card:** Hanya untuk data heterogen mandiri (pricing tiers), elemen manipulasi drag-and-drop (Kanban), dan katalog showcase visual e-commerce.
4. **Kapan DILARANG Card:** Data transaksi berulang, tabel master, dan 4 ringkasan KPI (dilarang membuat 4 box tebal yang memakan 30% layar).
5. **5 Pola Alternatif Borderless:**
   - *Hairline Rule Separator:* Garis pembatas tipis `border-b: 1px solid rgba(255,255,255,0.06)`.
   - *Surface Tint Banding:* Zebra wash area halus tanpa border luar.
   - *Continuous Data Rows:* Baris data interaktif dengan hover wash halus ala Linear/Stripe.
   - *Typographic Proximity:* Kontras H2 tebal dan jeda vertikal 24px-32px tanpa pembungkus.
   - *In-Line Horizontal KPI Strip:* Baris datar angka metrik dengan garis pemisah hairline (`|`) yang menghemat 60% ruang vertikal.

## References
Load deep architectural references on demand using `skill_view` (`name="upnormal-ui-architecture"`, `file_path="references/<file>"`):
- `references/distinctive-font-catalog-and-pairings.md`: Katalog Tipografi Berkarakter & Pasangan Font Anti-Monoton (Thunder, Druk, PP Editorial New, Instrument Serif, PP Neue Machina, Cabinet Grotesk, Clash Display, dll).
- `references/panduan-universal-spasial-uiux.md`: Standar Rekayasa Spasial Universal oleh Bagas Cihuy: definisi padding/gap/margin, 4-level spatial ladder, 4-distance rule, eliminasi margin collapsing, CSS logical properties, fluid clamp, hit target 44px, dan 5 anti-pattern spasial.
- `references/archetypes-and-world-styles.md`: Comprehensive guide to the 6 Core World Archetypes (Swiss Editorial, Neo-Brutalism, Liquid Gooey, Console-First, Spatial Tactile, Asymmetric Bento).
- `references/motion-morphing-60fps.md`: Implementation patterns for 60 FPS in-place card expansion via GSAP Flip, spring physics, and zero-blink view transitions.
- `references/anti-ai-slop-checklist.md`: Banned visual patterns, replacement rules, and mandatory pre-flight contrast and performance gates.

## Pitfalls
- **Relying on Model Training Bias (Prior UI Habits):** Never default to the model's unassisted idea of a web UI (generic symmetrical bento boxes, purple-cyan buttons, muddy box-shadows). Always ground designs in live internet curators, explicit user direction, or official Hermes design vault tokens.
- **Accidental Generic Slop:** Never use generic purple/blue AI gradient buttons or decorative status pills that serve no purpose.
- **Displaying Internal Engineering Standards as UI Badges (Performative Meta-Slop):** Never turn internal quality metrics (WCAG AAA, 60 FPS, Zero AI Slop, Vol XX) into floating badges, eyebrow kickers, or marketing tag strips on the user's interface. It screams amateur AI-generated posturing and creates severe visual clutter. Let the typography and interaction speak for themselves silently.
- **Fabricated Squircle AI Logos:** Never generate rounded-box icons containing PC monitors, shopping carts, or stars when the user has not asked for a logo; use direct text-only typography for headers and brand titles.
- **Blurring the Text:** Never apply SVG gooey/distortion filters directly to parent containers containing text; always use the Two-Layer Silhouette pattern.
- **Contrast Compromise:** Do not sacrifice text legibility for visual flair; body text must maintain WCAG AAA compliance.
- **Native Browser Dialogs & Raw OS Controls:** Never call `window.confirm()`, `window.alert()`, or render unstyled native `<select>` and `<input type="date">`; native dialogs synchronously freeze JS threads, halt 60 FPS animations, and break design system cohesion. Always provide custom modal dialogs, searchable select popovers, and datepickers that inherit active theme tokens.
- **Native Form Validation Bubbles ("Harap isi bidang ini"):** Never allow browser-default HTML5 validation tooltips to appear; they destroy theme immersion and occlude action buttons. Always apply `novalidate` to `<form>` tags and provide custom inline error text with organic micro-shake physics or blur-glass toasts.
- **Heavy Background Media Trap:** Never embed bulky GIF files or auto-playing HTML5 video tags for minor widget atmospheres (weather, telemetry, status indicators); heavy media spikes RAM and causes layout stutter. Always use lightweight inline procedural SVG vector animations driven by CSS transform3d keyframes.
- **Symmetric Spacing & Arbitrary Pixel Gaps Trap:** Never apply uniform padding across asymmetric layouts or use arbitrary unscaled pixels (`p-[17px]`, `m-[23px]`). Always employ the 4-level spacing hierarchy, fluid responsive clamp scales, and bottom dock safe clearance (`calc(var(--dock-height) + 48px)`).
- Undersized Interactive Click Targets: Buttons or links with padding too tight (< 44px hit bounds) violate WCAG AAA touch target rules and cause severe mobile touch frustration. Ensure minimum `py-2.5 px-5` or explicit `min-h-[44px] min-w-[44px]`.
- **Border Fatigue & Cold Laboratory Vibe on Productivity Tools:** Enclosing every single label, time badge, and input into thick black boxes with all-caps typography creates an exhausting, wireframe-like atmosphere devoid of emotional reward. Daily planning tools require dopamine feedback (multi-state reactive mascots, acoustic check pops, 100% canvas confetti celebration) and soft colored pill tags rather than endless boxed grids.
- **Destructive DOM Re-renders on Sliding Navigation (Anti-Jitter / In-Place Morphing):** Never destroy container innerHTML (`container.textContent = ''`) to update active state in tabs, week strips, or segmented controls. Destroying DOM nodes wipes out CSS transition context, causing active indicator pills to snap/blink across positions rather than gliding smoothly. Keep DOM nodes persistent and glide the indicator via CSS `transform: translateX/Y` with spring physics (`cubic-bezier(0.16, 1, 0.3, 1)`).
- **SVG Transform-Origin Detachment Trap on Multi-Stage Illustrations:** When scaling or transforming sub-elements of an SVG (such as botanical growth stages, flower heads, bud scales), ALWAYS declare explicit pixel `transform-origin` matching the attachment anchor (e.g. `transform-origin: 140px 85px` at the stem apex). Omitting `transform-origin` defaults scaling to `(0, 0)` of the SVG canvas, throwing elements into the air detached from their stems. Always wrap dependent paths (e.g. leaf + vein) into a unified `<g>` so sub-elements cannot drift apart.

## Verification
Inspect compiled HTML/CSS with `terminal`:
Verify that display typography uses line-height <= 1.0, contrast ratio exceeds 7:1, drop-shadows are zero, no native confirm/alert calls exist, brand headers use direct text without fake squircle icons, and forms declare `novalidate` with custom validation styling.
