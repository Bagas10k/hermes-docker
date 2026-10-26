---
name: modern-editorial-visual-hierarchy
title: Modern Editorial Visual Hierarchy & Carousel Layout
description: "Use when designing editorial news carousels and cards."
author: Bagas Cihuy & Bikagent
version: 1.0.0
tags: [editorial, carousel, visual-hierarchy, typography, squint-test, modern-news]
---

# Modern Editorial Visual Hierarchy & Carousel Layout

Standard operating procedure for designing high-impact editorial graphics, news carousels (1080×1350, 4:5), and visual storytelling layouts for modern social audiences (The Verge, Bloomberg, Folkative style).

---

## 1. Core Principles & The Squint Test

- **The Squint Test (Uji Menyipitkan Mata):**  
  Blur your vision while looking at the design. The visual sequence MUST register in strict order:
  1. Primary Focal Point (Large Headline or Full-Bleed Subject)
  2. High-Contrast Anchor (Category pill / Kicker)
  3. Contextual Deck / Standfirst
  *If 3 or more elements compete for attention simultaneously, the hierarchy has failed and must be pruned.*

- **Dramatic Scale Jump (3×–5×):**  
  Do not use gradual stepping (e.g. 36px → 28px → 24px). Editorial authority requires an extreme contrast jump:
  - Display Headline: **48px – 64px** (Weight 900, Line-height 1.10–1.15, Tracking -0.03em to -0.04em).
  - Deck / Standfirst: **20px – 24px** (Weight 500, Line-height 1.5, neutral secondary ink).
  - Metadata / Microcopy: **12px – 14px** (Weight 700 Mono, Tracking +0.08em to +0.15em).

- **Strict Color Restraint (90/10 Rule):**  
  90% of the canvas must remain pristine neutral (Pure White `#FFFFFF`, Deep Slate `#0F172A`, Muted Border `#E2E8F0`). High-visibility accent color (e.g., Hyper Yellow `#FFE600`, Vivid Red `#DC2626`) is strictly limited to **one** focal element per card.

---

## 2. Layout Patterns

### A. Cover Slide (The Full-Bleed + Floating Card Pattern)
- Avoid placing photography inside tiny boxed windows on cover slides.
- **Background:** Full-bleed photo (1080×1350) cropped tightly on the subject's face/action to establish instant eye contact.
- **Content Container:** Floating pure-white card at the bottom third (`background: #FFFFFF`, padding 40–48px, offset shadow). This ensures 100% text readability without muddy dark gradient washes over the subject.

### B. Final Slide (The Dual-Action CTA Engine)
- Do not use generic "Like & Follow" begs. Provide a concrete logical urgency reason (e.g., *"Simpan Warta Ini Sebelum Tertimbun Linimasa 📌"*).
- **Dual Action Cards (1×2 Grid):**
  - **Primary Card (Accent Filled #FFE600):** *"Simpan Postingan"* (Bookmark icon) — directly targets Instagram's highest algorithmic distribution signal (Saves).
  - **Secondary Card (Neutral Outline #FFFFFF):** *"Bagikan ke Rekan"* (Share icon) — prompts transmission to messaging groups.
- **Footer Profile Strip:** Verified handle badge paired with a high-contrast `+ IKUTI KAMI` button.

---

## 3. Pitfalls to Avoid
- Do not place hero photography in tiny constrained boxes on cover slides; user explicitly demands full-bleed immersion with floating sterile white text cards.
- Do not bold body paragraphs; boldness is a rare visual accent, not a paragraph treatment.
- Do not use uncalibrated dark overlays that make editorial photos look murky; use clean floating cards for text isolation.
- Avoid cluttered UI borders; use single hairline dividers (`border: 1px solid #E2E8F0` or `2px solid #0F172A`) to establish structure.
- Never use personal user information or real business entities as mockup/dummy content; enforce 100% synthetic entities.
- Enforce the 7:1 WCAG 2.2 AAA contrast ratio for all text elements. Run `python3 /home/ubuntu/.hermes/scripts/ui_quality_gatekeeper.py <target>` prior to finalizing any asset.

## 4. Standar Interaksi & Motion Lifecycle (SOP Mas Bagas v2.0)
Semua tampilan kartu berita atau kartu editorial web wajib mematuhi standar gerak berikut:
- **GSAP FLIP Morphing:** Kartu yang diklik membesar secara luwes di tempatnya (450ms `power3.out`).
- **Enter Lifecycle:** Kartu muncul dengan stagger slide-up halus (280ms).
- **Anti-Berkedip Putih (SPA Seamless Transition):** Pergantian kategori atau slide berita wajib menggunakan SPA transition dinamis tanpa hard page reload browser.
- **Mobile-First Ergonomics:** Tombol aksi dan navigasi tab wajib ramah jempol smartphone tanpa teks terpotong.

## 5. References & Calibration
- Detailed binary calibration and accepted/rejected design patterns: see [references/bagas-taste-profile.md](references/bagas-taste-profile.md).
