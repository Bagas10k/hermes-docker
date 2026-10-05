---
name: frontend-agent-craft
description: Use when building web UI. Autonomous frontend agent craft.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [frontend, ui, ux, design-system, web, html, css, reactive, anti-slop, ponytail]
    related_skills: [ui-ux-design-vault, ui-layout-intelligence, color-intelligence, typography-ux-copy, popular-web-designs, ponytail, autonomous-engineering-craft]
---

# Frontend Agent Craft: Protokol Eksekusi UI/UX Otonom

Skill ini menetapkan standar operasional baku bagi agen AI saat merancang, membangun, memperbaiki, atau merefaktor antarmuka web (Frontend). Menggabungkan kecerdasan tata letak, warna, tipografi, bank komponen APEX, serta doktrin efisiensi *Ponytail*.

---

## 1. Aturan Besi Mas Bagas (Hard Constraints)
Setiap agen frontend wajib mematuhi batasan lingkungan nyata berikut tanpa kompromi:
1. **Haram Localhost / 127.0.0.1 di HTML Publik**: Jangan pernah menulis `http://localhost:...` atau `http://127.0.0.1:...` pada tautan, tag `<a>`, `fetch`, atau aset publik. Gunakan path relatif (`/api/...`) atau nama host produksi.
2. **Pemanfaatan 100 Aset Desain Terverifikasi**: Rujukan aset lokal berstandar tinggi berada di `/home/ubuntu/referensi-desain/` (dapat diakses via web browser di path `/desain/`). Gunakan sebagai aset referensi nyata daripada placeholder kosong.
3. **Halaman Baru Wajib Standalone**: Permintaan halaman baru (seperti halaman login, register, detail produk) wajib dibuat sebagai rute/berkas mandiri terpisah (misal `login.html`), bukan sekadar tab di sidebar dashboard.
4. **Pendaftaran Otomatis ke Katalog Portofolio**: Setiap proyek web baru atau landing page yang dibuat wajib langsung didaftarkan ke katalog portofolio Bagas (`/portofolio/` di `katalog-portofolio-web`).
5. **Standar UI Mobile Companion (Zen)**: Jika merancang tampilan pendamping mobile:
   - 100dvh (1-page non-scrollable).
   - Kanvas zen 'kosongan' minim teks dengan maskot utama besar di tengah.
   - Menu pengaturan lengkap disimpan rapi di dalam slide-up drawer G2 squircle.

---

## 2. Sintesis 5 Pilar UI/UX Intelligence

Sebelum menulis kode visual, sintesiskan 5 pilar desain berikut:
1. **Spatial Layout (`ui-layout-intelligence`)**:
   - Terapkan 4 tingkat spasial: *Page* (margin viewport/container) $\rightarrow$ *Section* (gap antar blok) $\rightarrow$ *Component* (card padding) $\rightarrow$ *Micro* (icon-label gap).
   - Gunakan ritme dasar 8px (4, 8, 12, 16, 24, 32, 48, 64px) dan CSS Gap, bukan margin acak.
2. **Color Intelligence (`color-intelligence`)**:
   - Palet fungsional, bukan dekorasi liar. Dominasi neutral slate/warm paper untuk struktur, aksen saturasi tinggi hanya untuk titik fokus interaksi.
   - Gunakan standar Warm Paper & Obsidian: kanvas porselen (`#f8fafc`), panel baca hangat (`#fdfbf7`), tipografi Obsidian pekat (`#0f172a`), dan aksen permata terukur.
3. **Typography & UX Copy (`typography-ux-copy`)**:
   - Hirarki informasi mendahului ukuran font. Gunakan `text-wrap: balance` agar tidak ada kata yatim (*orphans*).
   - Bahasa lugas, berwibawa, dan bebas basa-basi AI.
4. **Anti-Template & Anti-Slop Gate (`ui-ux-design-vault`)**:
   - **Zero Text Gradient**: Judul wajib monokrom solid tajam (putih di dark mode, hitam di light mode).
   - **Zero Decorative Badge**: Dilarang kapsul pil pemanis melayang di atas headline.
   - **0% Emoji di UI Modern**: Gunakan ikon SVG (Lucide/Heroicons) monokrom.
   - **Zero CLS**: Kunci `min-height` pada wadah teks/konten dinamis.
5. **Lazy Senior Dev Mode (`ponytail`)**:
   - Utamakan HTML/CSS native: Flexbox, Grid, CSS Variables, native `<dialog>`, `<input type="date">`.
   - Hindari dependensi JS berat jika cukup dengan 20 baris vanilla JS.

---

## 3. Pipeline Eksekusi Frontend Agent

1. **Riset & Refleks 100 Aset Desain Lokal (MCP `uiux-reference`)**:
   - Sebelum merancang antarmuka dari nol, panggil `tool_call` dengan `mcp__uiux_reference__uiux_search(query=..., category=...)` untuk mengekstrak sasis nyata dari 100 aset desain lokal di `/home/ubuntu/referensi-desain/`.
   - Gunakan `mcp__uiux_reference__uiux_get_component_recipe` untuk komponen cepat (hero-header, interactive-card, 404, empty-state).
   - Analisis relasi layout dan palet warna referensi sebelum koding.
2. **Analisis Konteks & Arketipe Permukaan**:
   - Tentukan apakah antarmuka bertipe *Console/Operate*, *Catalog/Explore*, *Monitor/Dashboard*, atau *Editorial/Learn*.
3. **Struktur Bersih**: Tulis markup semantik dengan aksesibilitas bawaan (ARIA, semantic tags).
4. **Styling Modular**: Gunakan variabel CSS terstruktur atau utility class Tailwind yang konsisten dengan token desain.
5. **Verifikasi Browser Nyata**:
   - Jalankan pemeriksaan curl HTTP 200.
   - Periksa responsivitas viewport mobile & desktop via `browser_exec`.
6. **Registrasi Portofolio**: Daftarkan tautan proyek ke `katalog-portofolio-web`.
