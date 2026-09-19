---
name: genjutsu
description: "Creative coding: motion, micro-interactions, and design systems."
version: 3.1.0
author: AThevon, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [genjutsu, creative-coding, motion, animations, design-systems, anti-slop, ui-ux]
    related_skills: [claude-design, design-vault, ui-ux-design-vault]
---

# Genjutsu — The Art of Illusion in Creative Coding

Creative coding for interfaces: transforms any functional interface into something exceptional through motion design, micro-interactions, and coherent visual design systems. Zero AI slop.

Covers Web (React, Vue, Svelte, CSS, Three.js, Canvas), Android (Jetpack Compose), and Apple (SwiftUI).

---

## 1. Dua Pipeline Utama

### A. `/genjutsu:cast` — The Illusionist
Gunakan saat menyempurnakan atau menganimasikan UI yang sudah ada:
- *"Tambahkan animasi scroll pada landing page"*
- *"Buat dropdown dan modal ini terasa taktil dan snappy"*
- *"Poles efek hover kartu ini dengan spring physics"*
- Rujuk panduan lengkap di: `skills/creative/genjutsu/cast/SKILL.md`

### B. `/genjutsu:paint` — The Master Painter
Gunakan saat merancang alam semesta visual atau design system lengkap dari nol:
- *"Rancang landing page SaaS ini dari nol"*
- *"Buat design system lengkap dengan token warna, tipografi, dan motion"*
- *"Bangun antarmuka dashboard mobile/desktop baru"*
- Rujuk panduan lengkap di: `skills/creative/genjutsu/paint/SKILL.md`

---

## 2. Peta Sub-Skills (`_jutsu/`)

Genjutsu dilengkapi modul spesialis internal di direktori `skills/creative/genjutsu/_jutsu/`:

- **Fondasi & Prinsip:**
  - `motion-principles`: Timing, easing cubic-bezier, reduced-motion, aturan do-not.
  - `mobile-principles`: Touch targets (min 44px), no-hover doctrine, thumb zones, gestures.
  - `desktop-principles`: Pointer precision, hover states, keyboard shortcuts, multi-window.
  - `ui-ux-pro-max`: Database kecerdasan desain (gaya visual, palet warna, pasangan font, stacks).
  - `design-audit`: Checklist audit motion gap, accessibility contrast, bundle size, dan fps hitches.

- **Web Stacks:**
  - `gsap`: Timeline, ScrollTrigger, pinning, svg motion.
  - `framer-motion`: Motion values, layout transitions, AnimatePresence, spring gestures.
  - `css-native`: Scroll-driven animations, View Transitions API, `@starting-style`.
  - `threejs-r3f`: React Three Fiber, WebGL shaders, 3D particles.
  - `canvas-generative`: Flow fields, noise, fractals, particles.

- **Mobile Native Stacks:**
  - `compose-motion` & `compose-graphics`: Jetpack Compose springs, SharedTransitionLayout, AGSL shaders.
  - `swiftui-motion` & `swiftui-graphics`: SwiftUI withAnimation, matchedGeometryEffect, Metal shaders.

---

## 3. Aturan Besi (Iron Rules)

1. **Validasi Interaction Thesis Sebelum Koding:** Rumuskan apa efek visual yang ingin dicapai, komponen mana yang bergerak, dan apa tujuannya sebelum menulis baris kode pertama.
2. **Satu Pertanyaan Bertahap:** Ajukan satu pertanyaan penentu arah dalam satu waktu. Jangan memborong pertanyaan.
3. **Tolak AI-Slop:** Dilarang menggunakan gradien pelangi klise, glassmorphism buram berlebihan, atau animasi lambat yang membuang waktu pengguna.
4. **Prioritas Performa (60 FPS):** Hindari layout shift (CLS). Animasikan hanya properti `transform` dan `opacity`.
5. **Hormati Pustaka Yang Sudah Ada:** Jika proyek sudah menggunakan Tailwind atau Framer Motion, gunakan pustaka tersebut tanpa memaksakan dependensi baru yang tidak perlu.
