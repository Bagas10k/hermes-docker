---
name: upnormal-ui-engine
description: "Use when building or auditing UI/UX with upnormal-ui."
version: 1.1.0
author: Bagas Cihuy & Hermes Architecture
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [upnormal-ui, design-system, anti-ai-slop, mcp, ast-linter, transmutation, bento-grid, morphing, spatial-rhythm, svg-bounds]
---

# Upnormal UI Engine & Anti-AI-Slop Architecture

Panduan baku rekayasa antarmuka profesional menggunakan ekosistem `upnormal-ui`. Mengubah doktrin desain pasif menjadi perkakas komputasi aktif (MCP & CLI) untuk membebaskan antarmuka dari belenggu template kaku model AI menuju karya seni web berjiwa bebas, berkinerja 60 FPS in-place, berkontras tinggi WCAG 2.2 AAA, dan berpenataan ruang proporsional.

## 🚨 PANTANGAN MUTLAK MAS BAGAS (Pelajaran Skor 2/10)
- **DILARANG KERAS Menampilkan Kicker Badge Mengambang & Tag Pamer Teknis:**
  Jangan pernah menampilkan floating pill tags (contoh: `INDONESIA // VOL. 02`, `FIG. 01`) atau deretan badge pamer kriteria teknis (seperti `100% Zero AI-Slop`, `WCAG AAA (≥ 7:1)`, `60 FPS In-Place Morphing`, `Privacy First`).
  *Alasan Mekanistik:* Elemen dekoratif semacam ini adalah ciri khas AI slop murahan yang membuat antarmuka terasa norak, bising, dan mengotori panggung visual. Kualitas sejati harus dirasakan langsung lewat tipografi bersih, spasi lega, dan rasa sentuh interaksi fisik—bukan dipamerkan lewat badge kata-kata.
- **DILARANG Logo Kotak Rounded Bersiluet PC/Gedung:**
  Gunakan tipografi teks langsung (*direct text-only branding*) pada logo dan header. Dilarang mengarang logo kotak squircle dengan siluet monitor, bintang, atau keranjang belanja kecuali ada aset logo resmi.
- **Formulir Wajib Memakai `novalidate`:**
  Semua tag `<form>` wajib menyertakan atribut `novalidate` untuk mencegah balon error tooltip bawaan peramban (*"Harap isi bidang ini"*) yang merusak pencelupan tema.
- **DILARANG SVG Tanpa Batas Fisik (SVG Blowup Trap):**
  Jangan pernah menyematkan elemen `<svg>` hanya berbekal class Tailwind (seperti `class="w-4 h-4"`) tanpa atribut fisik `width="..."` dan `height="..."` atau inline style. Jika CSS CDN tertunda, browser akan merender SVG selebar 100% layar (menjadi panah/ikon raksasa yang merusak halaman). Selalu sematkan `<svg width="16" height="16" style="width:16px;height:16px;" ...>`.

## 1. Aturan Penataan Jarak & Ritme Spasial (Spatial Rhythm Hierarchy)
Gunakan modul `upnormal_ui.core.spacing` (`upnormal_audit_spacing` & `upnormal_get_spacing_system`) untuk menegakkan 4 tingkatan penataan ruang:
1. **Tingkat Halaman (Page Level):** Gutter adaptif `px-4 sm:px-6 lg:px-8` dengan pembatas lebar aman `max-w-7xl mx-auto`.
2. **Tingkat Seksi (Section Level):** Pemisah vertikal antar-seksi konten makro wajib proporsional: `space-y-12 sm:space-y-16 lg:space-y-20` (48px s/d 80px). Jarak antar-seksi wajib selalu lebih besar daripada padding internal kartu komponen.
3. **Tingkat Komponen (Component Level):** Padding kartu DILARANG kaku di mobile (seperti `p-8` atau `p-10` yang memakan lebar layar 390px ponsel). Wajib responsif adaptif: `p-5 sm:p-6 lg:p-8` (20px di ponsel, 24px di tablet, 32px di desktop). Jarak antar-kartu bersaudara: `gap-4 sm:gap-6`.
4. **Tingkat Mikro (Micro Level):** Jarak teks ke ikon `gap-2` (8px), padding status badge `py-1 px-2.5`, dan jarak antar-kontrol inline `gap-3` (12px).
5. **Anti-Pattern Magic Offset:** Dilarang menambahkan `pt-6` atau offset artifisial pada elemen toggle/switch untuk meluruskan baris form. Gunakan penataan struktural `flex flex-col justify-end` atau grid alignment alami.

## 2. Arsitektur 9 Dosa AI UI Slop (Heuristik Audit & AST)
Mesin `upnormal_scan_anti_slop` dan CLI mendeteksi 9 anomali:
1. `SLOP_01_PURPLE_CYAN_GRADIENT`: Tombol gradien ungu ke cyan murahan.
2. `SLOP_02_EMOJI_AS_UI_ICON`: Emoji di dalam tombol, tautan, atau badge kontrol.
3. `SLOP_03_LOW_CONTRAST_GRAY`: Teks abu-abu redup di atas latar belakang gelap (< 7:1).
4. `SLOP_04_MUDDY_DIFFUSE_SHADOW`: Bayangan blur tebal kusam (`shadow-2xl`/`shadow-xl`).
5. `SLOP_05_RAINBOW_TEXT_GRADIENT`: Teks gradien pelangi multi-warna yang sulit dibaca.
6. `SLOP_06_RIGID_BENTO_GRID`: Bento grid 3-kolom simetris tanpa hierarki sel asimetris.
7. `SLOP_07_UNSTYLED_NATIVE_SELECT`: Kontrol `<select>` bawaan OS tanpa kustomisasi.
8. `SLOP_08_STIFF_POPUP_DIALOG`: Modal dialog kaku yang muncul melompat tanpa kontinuitas fisik.
9. `SLOP_09_ORNAMENTAL_KICKER_BADGE_CLUTTER`: Tag pill mengambang pamer teknis.

## 3. Prosedur Rekayasa Komponen Modular
Gunakan pabrik komponen `upnormal-ui` (`upnormal_ui.components`) untuk memproduksi elemen:

### A. Pabrik Tombol Modular (`components/button.py`)
Mendukung 5 varian arketipe dalam 3 ukuran (`sm`, `md`, `lg`) dan multi-framework export:
- `neo_brutal`: Hard offset shadow 4px, border 2.5px solid, fisika klik taktil.
- `swiss_editorial`: Kanvas noir/paper, garis 1px tajam, tipografi uppercase kondensasi tinggi.
- `obsidian_sleek`: Latar obsidian pekat, hairline border, aksen glow hover.
- `spatial_glass`: Progressive frosted glass, optical rim border.
- `pill_soft`: Rounded-full, spring hover membal lembut.
- Ekspor siap pakai: `framework='html'`, `'blade'` (`<x-upnormal-button>`), `'react'`, `'vue'` (Vue 3 `<script setup>`), `'svelte'` (Svelte 5 `$props()`), atau `'alpine'` (Alpine.js `x-data`).
- *Pitfall F-string Template Framework:* Saat mengembalikan sintaks Vue/Svelte/Blade di dalam f-string Python, escape kurung kurawal ganda (misal `{{{{ label }}}}` untuk menghasilkan `{{ label }}`) agar tidak bentrok dengan parser f-string Python atau terpotong menjadi ekspresi tunggal.

### B. Badge Status Fungsional (`components/badge.py`)
Menggantikan badge pamer teknis dengan status operasional nyata:
- `live`: Hijau berdenyut (`animate-ping`).
- `pending`: Amber status.
- `closed`: Abu-abu netral.
- `alert`: Merah waspada berdenyut.
- `info`: Cyan informasi.

### C. Menu Popover Aksi Taktil (`components/dropdown.py`)
Dropdown menu 3-titik (*action menu*) dengan transisi spring 60 FPS, penutup klik-luar (*outside click*), dan penutup tombol ESC.

### D. Header Navigasi Merek (`components/navbar.py`)
Navigasi sticky blur dengan *direct text-only typography* (tanpa logo kotak rounded squircle AI slop).

### E. Bento Grid Asimetris (`components/card.py`)
Susun tata letak grid dengan pembobotan asimetris rasio 2:1 (`col-span-2` untuk kartu fokus hero, `col-span-1` untuk kartu metrik sekunder) agar ritme halaman tidak monoton.

### F. In-Place Morphing Dialog 60 FPS (`components/dialog.py`)
Tombol pemicu mengembang secara fisik menjadi permukaan dialog modal utuh dengan kurva spring `cubic-bezier(0.16, 1, 0.3, 1)`. Mencegah pergeseran tata letak mendadak (*zero layout shift / CLS = 0*).

### G. Skala Warna Persepsi 11-Langkah (`core/color_scale.py`)
Hasilkan skala 50 hingga 950 dari hex aksen apa pun. Setiap langkah otomatis menghitung luminansi relatif dan menyandingkan teks hitam atau putih yang terverifikasi WCAG AAA ($\ge 7:1$).

## 4. Pitfall Teknis Parsing DOM & Runtime Eksekusi
- **Venv Eksekusi Mandatori:** Jalankan CLI dan modul `upnormal-ui` menggunakan venv Hermes yang memiliki dependensi lengkap (`mcp`, `httpx`, `beautifulsoup4`):
  ```bash
  /home/ubuntu/.hermes/hermes-agent/venv/bin/python
  ```
  Hindari binary Python default `/usr/bin/python3` atau shims tanpa venv aktif karena akan memicu `ModuleNotFoundError: No module named 'bs4'`.
- **Pitfall Atribut Kosong Falsy BeautifulSoup4:** Elemen tanpa atribut seperti `<select><option>...</option></select>` memiliki `elem.attrs = {}`. Dalam Python, `bool({}) == False`. Jika memeriksa dengan `if not getattr(elem, 'attrs', None): continue`, Python akan melewatkan elemen tersebut. Wajib gunakan pemeriksaan identitas eksplisit:
  ```python
  if getattr(elem, "attrs", None) is None:
      continue
  ```

## 5. Alur Verifikasi & Pengujian Playground
1. **Jalankan Unit Test Suite:**
   ```bash
   /home/ubuntu/.hermes/hermes-agent/venv/bin/python /home/ubuntu/upnormal-ui/tests/test_all.py
   ```
2. **Generate Interactive Playground HTML:**
   ```bash
   /home/ubuntu/.hermes/hermes-agent/venv/bin/python -m upnormal_ui.cli playground -o /home/ubuntu/penelitian-pola-pikir-ai/public/komponen/playground.html
   ```
3. **Uji Render di Peramban Nyata:**
   Buka `https://www.jajandigital.web.id/komponen/playground.html` dan ambil tangkapan layar via Chromium headless:
   ```bash
   chromium --headless --no-sandbox --disable-gpu --window-size=1280,2400 --screenshot=/tmp/playground.png "https://www.jajandigital.web.id/komponen/playground.html"
   ```
4. **Verifikasi Visual Sentuh & Spasial:**
   Pastikan tidak ada tombol bergradien ungu-cyan, tidak ada kicker badge pamer teknis, teks terbaca tajam di seluruh background, SVG memiliki dimensi terikat (`width/height`), dan jarak penataan mematuhi hierarki 4-tingkat.
