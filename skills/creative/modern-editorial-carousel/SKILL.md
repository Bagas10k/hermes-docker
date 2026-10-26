---
name: modern-editorial-carousel
description: "Use when designing modern bright editorial carousel slides."
version: 1.0.0
author: Bagas Cihuy & Bikagent
license: MIT
platforms: [linux, macos, windows]
related_skills:
  - seo-expert
  - content-intelligence
  - instagram-publishing-automation
  - tiktok-content-extraction
metadata:
  hermes:
    tags: [carousel, editorial, instagram, visual-hierarchy, modern-news, folkative-style, cta-conversion]
---

# Modern Editorial Carousel & High-Contrast Visual System

Skill ini memandu perancangan visual konten media sosial carousel (Instagram 4:5 / 1080×1350) dan antarmuka editorial agar berstandar internasional, bersih, terang, dan memiliki akurasi 90–100% terhadap selera Mas Bagas.

## When to Use
- Merancang atau merender slide carousel berita/edukasi (@sputarai, @sputarball, dsb).
- Menata hierarki tipografi judul, deck ringkasan, dan kartu penutup (CTA).
- Mengaudit kontras palet warna dan struktur slide agar bebas dari AI-slop.

---

## 1. Format Baku Anatomi Slide (ACC Mas Bagas 2026)

### A. Slide 1 / Cover (The Hook)
- **Foto 100% Full-Bleed:** Foto tokoh/peristiwa/aksi memenuhi seluruh kanvas secara dramatis dan hidup. Dilarang keras foto kecil terjepit kotak kliping koran.
- **Floating White Card (Kotak Putih Mengambang):**
  - Diletakkan mengambang di bagian bawah dengan margin kiri, kanan, dan bawah (48px).
  - Latar belakang putih bersih (`#FFFFFF`) dengan bayangan solid dan garis batas tegas (`#0F172A`).
  - Menjamin keterbacaan (*readability*) 100% tanpa bayangan gradien hitam kotor di atas foto.
- **Hierarki Tipografi:**
  - Kicker tag: Monospace kapital merah/kuning padat (`• KATEGORI TOPIK 2026`).
  - Headline utama: *Plus Jakarta Sans Bold 900* (46–64px, line-height 1.15, tracking rapat `-0.03em` hingga `-0.04em`).
  - Deck ringkasan: Sans-serif netral (20–24px, line-height lapang 1.5).

### B. Slide 4 / Penutup (The CTA Conversion Engine)
- **Trigger Urgensi Logis:** Berikan alasan spesifik bernilai simpan (contoh: *"Simpan Warta Ini Sebelum Tertimbun Linimasa 📌"*), bukan sekadar ajakan klise *"Jangan lupa like"*.
- **Dual Action Tactile Cards:**
  - **Kartu Primer (Kuning Terang #FFE600):** Aksi **"Simpan Postingan"** (Aksi paling berharga untuk sinyal algoritma Explore).
  - **Kartu Sekunder (Putih Bersih #FFFFFF):** Aksi **"Bagikan ke Rekan"** (Memicu share ke grup Telegram/WhatsApp).
- **Bar Profil & Tombol Ikuti:** Bar identitas akun di footer berdampingan dengan tombol kontras hitam pekat `+ IKUTI KAMI`.

---

## 2. Sistem Palet Warna & Rasio Kontras Tinggi (WCAG 2.2 AAA / min 7:1)

- **Kanvas Terang:** Latar putih murni (`#FFFFFF`) dipadu tinta teks hitam pekat titanium (`#0F172A`), rasio kontras 19:1 (Ultra Jernih).
- **Teks Pendukung:** Abu-abu baja gelap (`#475569`), rasio kontras 7.2:1 (Lolos AAA).
- **Aksen Pemicu Fokus:** Kuning Kenari (`#FFE600`) atau Merah Crimson (`#DC2626`).
- **Diharamkan Mutlak:**
  - Teks abu-abu muda di atas putih (kontras loyo / mata cepat lelah).
  - Teks abu-abu gelap di atas hitam pekat.
  - Teks warna neon terang tanpa garis batas kontras.

---

## 3. Protokol Evaluasi: Uji Menyipitkan Mata (The Squint Test)
Sebelum slide disetujui untuk rilis:
1. Sipitkan mata hingga layar terlihat buram (*blur*).
2. Urutan tertangkap mata wajib:
   - **Level 1:** Headline Besar atau Foto Hero.
   - **Level 2:** Kotak Kategori Berwarna Terang.
   - **Level 3:** Teks Ringkasan.
3. Jika ada elemen dekoratif yang berebut perhatian secara acak, desain wajib disederhanakan.

---

## 4. Standar Interaksi & Motion Lifecycle (SOP Mas Bagas v2.0)
   Semua template carousel interaktif wajib menerapkan:
   - **GSAP FLIP Morphing:** Kartu atau slide CTA bermetamorfosis membesar secara luwes di tempatnya (450ms `power3.out`).
   - **Enter Lifecycle:** Stagger slide-up (280ms) saat render.
   - **Anti-Berkedip Putih (SPA Seamless Transition):** Pergantian slide interaktif di web preview wajib tanpa reload browser kasar.
   - **Mobile Thumb Zone:** Tombol swipe dan CTA mudah dijangkau di layar HP.
