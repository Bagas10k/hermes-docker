# Panduan Pemetaan Vibe & Anti-Template Klise (Vibe Mapping)

Panduan ini mengatur cara menerjemahkan kata kunci atmosfer visual (*vibe*) menjadi keputusan desain konkret (warna, tipografi, jarak, materialitas) tanpa terjebak dalam perangkap stereotip atau *AI-slop* generik.

---

## 1. Vibe: Premium / Luxury
- **Perangkap Klise AI (REJECT):** Kombinasi warna hitam pekat + emas berkilau, gradien emas berlebihan, teks berornamen mewah tapi sulit dibaca.
- **Eksekusi Autentik (ADOPT / TRANSFORM):**
  - **Palet:** Warna krem hangat (*warm ivory / alabaster*), charcoal lembut, atau *obsidian deep slate* dengan aksen perak satin atau tembaga redup.
  - **Tipografi:** Sans-serif netral dengan tracking huruf yang sangat terukur atau serif kontemporer dengan kontras guratan tinggi pada heading.
  - **Materialitas:** Micro-border 1px dengan opasitas sangat rendah (10-15%), tekstur matte halus, bayangan difus yang sangat jauh dan lembut (*diffuse soft drop-shadow*).
  - **Spacing:** Padding dermawan namun beraturan, memberikan ruang nafas bagi elemen penting.

---

## 2. Vibe: Futuristic / Cybernetic
- **Perangkap Klise AI (REJECT):** Selalu menggunakan latar ungu neon, teks biru menyala silau (*glow* berlebihan), kartu glassmorphism blur tebal yang membuat teks buram.
- **Eksekusi Autentik (ADOPT / TRANSFORM):**
  - **Palet:** Deep slate (#0A0C10), monochromatic carbon, dengan aksen tunggal yang tajam (misal: *amber alert* atau *cyan telemetry pulse*).
  - **Tipografi:** JetBrains Mono atau Fira Code untuk data teknis, dikombinasikan dengan sans-serif geometris tegas (Inter/Geist).
  - **Materialitas:** Grid tipis terstruktur, garis ukur 1px, indikator telemetri real-time, status badge fungsional dengan pulse halus.
  - **Interaksi:** Zero-latency transition, hover state responsif instan, feedback taktil cepat.

---

## 3. Vibe: Technical / Console / Developer Tool
- **Perangkap Klise AI (REJECT):** Latar hitam terminal dengan font hijau Matrix hacker jadul.
- **Eksekusi Autentik (ADOPT / TRANSFORM):**
  - **Palet:** Abu-abu arang netral (Zinc/Slate), border abu-abu gelap terdefinisi jelas, aksen warna semantik murni (hijau untuk OK, merah untuk fail, kuning untuk pending).
  - **Kepadatan:** *High-density compact layout*, margin/padding rapat (8-16px), border-radius tegas (4-8px).
  - **Elemen Wajib:** Tabular numbers (`font-variant-numeric: tabular-nums`), shortcut keyboard hints (`Cmd+K`, `Shift+P`), inline code badges, dan filter pencarian instan.

---

## 4. Vibe: Editorial / Thoughtful / Book
- **Perangkap Klise AI (REJECT):** Sekadar mengganti font default menjadi Times New Roman tanpa mengatur ritme teks.
- **Eksekusi Autentik (ADOPT / TRANSFORM):**
  - **Palet:** *Warm Paper & Obsidian* (#FBFBFA / #111214), tinta hitam arang pekat, pembatas garis ganda tipis (*double thin rules*).
  - **Tipografi:** Heading serif berwibawa (Newsreader, Georgia, Playfair), drop-cap proporsional pada awal paragraf utama, body text dengan line-height nyaman (1.6 - 1.8).
  - **Layout:** Grid asimetris ala majalah arsitektur, kolom tepi untuk catatan pinggir (*sidenotes/footnotes*), kutipan blok (*pull-quotes*) yang tegas.

---

## 5. Vibe: Calm / Minimal
- **Perangkap Klise AI (REJECT):** Layar kosong serba putih tanpa struktur yang membuat pengguna bingung mencari menu aksi.
- **Eksekusi Autentik (ADOPT / TRANSFORM):**
  - **Palet:** Tone abu-abu monokromatis yang berjenjang halus, kontras yang memenuhi rasio WCAG AA minimal (4.5:1).
  - **Struktur:** Hierarki berbasis ukuran font dan berat teks (*font-weight*), bukan warna-warni kotak pembungkus.
  - **Uji Subtraksi:** Hilangkan semua garis dan background kartu yang tidak esensial. Biarkan *whitespace* yang mengelompokkan data secara alami (*Law of Proximity*).

---

## 6. Vibe: Playful / Tactile
- **Perangkap Klise AI (REJECT):** Warna pelangi acak yang melelahkan mata dan kartun anak-anak.
- **Eksekusi Autentik (ADOPT / TRANSFORM):**
  - **Karakter:** Neo-brutalism terkontrol atau micro-spring physics.
  - **Materialitas:** Border tegas 2px, sudut lipatan taktil (*paper peel*), bayangan jatuh solid (*hard shadow / drop-shadow 4px*), tombol dengan sensasi penekanan fisik (*active:translate-y-1*).
