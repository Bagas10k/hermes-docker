# Anti-AI Slop Checklist & Quality Gates

## 1. Forbidden Patterns (Banned from Upnormal UIs)

| Forbidden Pattern | Why It Is Slop | Upnormal Replacement |
|---|---|---|
| **Generic Purple-to-Cyan Gradients** | Lazy AI hallmark; screams low-effort generated code. | 95% Achromatic stage with singular bold accent (Ember `#FA5D29` or Lime `#A6FF00`). |
| **Random Floating Glow Orbs** | Blurry decorative circles with no semantic connection to layout. | Structured interactive canvas (WebGPU fluid or mathematical mesh) on Layer 0. |
| **Decorative Kicker Badges** | Trivial pills like "✨ NEXT GEN AI PLATFORM" filling empty space. | Direct, confident headline statements with zero buzzword padding. |
| **Muddy Heavy Drop Shadows** | `box-shadow: 0 20px 40px rgba(0,0,0,0.4)` makes surfaces look dirty. | Hairline borders (`1px solid #EDEDED`) and clean surface tonal contrast. |
| **Symmetric Bento Grids** | Boring uniform 2x2 or 3x3 identical rounded rectangles. | Asymmetric editorial grid with variable column spans and proportional weights. |
| **Rigid Center-Screen Modals** | Blocks full viewport, blinks in, destroys browsing context. | In-place card morphing (GSAP Flip) or side-sliding tactile drawers. |
| **Generic Rounded-Box AI Logos** | Cheap squircle icons (PC monitor, cart, star, building) fabricated by AI. | Direct Text-Only Branding: razor-sharp typography without fake app-icon boxes unless logo assets are provided. |
| **Native Browser Dialogs (`confirm()`, `alert()`)** | Breaks UI theme, freezes JS execution thread, feels cheap/native. | Custom async confirmation modal/bottom sheet setema dengan backdrop-blur dan spring physics. |
| **Native `<select>` & `<input type="date">`** | OS default styling disrupts visual cohesion and typography. | Custom searchable select popover dan custom calendar datepicker yang mewarisi token desain web. |
| **Native Form Validation Bubbles ("Harap isi bidang ini")** | Default browser tooltip destroys theme immersion and typographic hierarchy. | Wajib gunakan `<form novalidate>` dipadu custom inline error message, input border highlight (`#FA5D29`), atau custom toast setema dengan blur glass. |

## 2. Mandatory Pre-Flight Quality Gates

Before declaring any UI task complete, the agent must verify:
- [ ] **UI Tabula Rasa Compliance:** Was this design built strictly from live web references, explicit user direction, or official Hermes Upnormal tokens — and completely free of LLM prior memory/generic AI habits?
- [ ] **Contrast Verification:** Run color contrast check. All body and headline text must meet WCAG AAA (>= 7:1) against its immediate background.
- [ ] **Typographic Dominance:** Does the hero section feature a single monolithic typographic anchor (`>= 64px`, tight line-height `<= 1.0`)?
- [ ] **Two-Layer Silhouette Integrity:** Are text elements free from blur, distortion, and filter inheritance?
- [ ] **Performance Profile:** Are heavy CSS filters (`blur()`, `drop-shadow()`) kept off animated layout elements?
- [ ] **Tactile Feel:** Do interactive controls respond with instant physical spring compression on `:active`?
- [ ] **Mobile Responsiveness:** Does extreme typography clamp gracefully (`clamp(40px, 8vw, 127px)`) without horizontal scroll overflow?
