# Two-Phase Engineering Protocol: Structure & Function First, Vibe Second

A disciplined separation-of-concerns protocol designed to eliminate cognitive overload, preventing agents from premature visual styling while the core data and business logic remain unbuilt or unstable.

## 1. The Core Failure Mode: Premature Polishing
When building applications from scratch, agents frequently attempt full visual design concurrently with backend engineering:
- The agent tweaks CSS gradients, blur filters, and micro-animations while database migrations are incomplete and CRUD routes throw unhandled exceptions.
- Result: An interface that appears flashy at a glance, but buttons trigger broken handlers, forms lose state, and API endpoints fail in production.

---

## 2. Phase 1 — Structural Grid & Functional Engine (Barebones First)

In Phase 1, the agent dedicates 100% of its reasoning budget to system stability and spatial organization:
1. **Container & Grid Scaffolding:**
   - Establish clean CSS Grid and Flexbox layouts (Sidebar, Header, Main Work Area, DataGrid).
   - Ensure responsive container boundaries without horizontal overflow.
   - Keep visuals completely barebones: neutral grayscale, minimal borders, zero decorative glow or complex animations.
2. **Data & Backend Integrity:**
   - Database schemas, table relationships, foreign key constraints, and seeders.
   - Backend API routes, request validation, authentication middleware, and error handling.
   - Core CRUD interactions: Create, Read, Update, Delete with deterministic state management.
3. **Phase 1 Acceptance Criterion:**
   - The application runs end-to-end. Data successfully persists to the database, renders in the table, and responds to user input without errors.

---

## 3. Checkpoint — Vibe & Theme Confirmation with User

Once Phase 1 is empirically proven, the agent **pauses execution** and asks the user directly before styling:
```text
Sistem dan tatanan grid dasar sudah berjalan stabil dan terverifikasi runtime.
Untuk tahap pematangan visual, Mas Bagas ingin tema dan 'vibe' rasanya seperti apa?
1. Elegan & Luxury Minimalist (Monokrom kontras tinggi, hairline border, grotesk tajam)
2. Industrial Console HUD (Densitas data tinggi, aksen amber/electric, monospace)
3. Swiss Editorial Modern (Warm paper, tipografi raksasa asimetris, aksen berani)
4. Playful / Fun Neo-Brutalist (Karakter ceria, tombol tactile, palet pop)
5. Pilihan kustom lain dari Mas Bagas?
```

---

## 4. Phase 2 — Aesthetic Craftsmanship & Upnormal Styling

Upon user vibe confirmation:
1. **Live Reference Discovery:** Query current global exemplars matching the selected vibe (`site:godly.website` or `site:awwwards.com`).
2. **Apply Hermes Taste Filter:**
   - Panggung 95% akromatik dengan 5% aksen tunggal berani.
   - Kontras teks WCAG AAA (>= 7:1).
   - Tipografi raksasa monolitik (Direct text branding, zero fake AI logo boxes).
   - In-place fluid morphing 60 FPS (zero static blink modals).
   - Kontrol kustom anti-native (modal konfirmasi CRUD kustom, custom select, custom datepicker).
3. **Preserve Functional Invariants:**
   - Styling must never mutate working data contracts, element IDs, or API request payloads established in Phase 1.
