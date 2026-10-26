---
name: liquid-gooey
description: "Use when designing liquid, gooey, jelly morphing, and rubber-trail UI components without blurring text."
version: 1.0.0
author: Jakub Antalik & Hermes
license: MIT
platforms: [linux, macos, windows]
related_skills:
  - upnormal-ui-architecture
  - ui-ux-design-vault
  - motion-ui-lifecycle-and-morphing
  - creative-visual-mindset
metadata:
  hermes:
    tags: [gooey, liquid-ui, jelly-morph, svg-filter, two-layer-silhouette, motion, spring-physics]
---

# Liquid Gooey & Two-Layer Silhouette Architecture

Skill ini adalah **panduan baku implementasi efek cairan (Gooey / Liquid / Jelly Morphing)** pada antarmuka modern tanpa merusak ketajaman tipografi dan ikon, mengacu pada arsitektur pustaka `liquid-gooey` karya Jakub Antalík (@jakubantalik).

---

## 1. Masalah Utama Efek Gooey Konvensional (Mengapa Ditinggalkan?)
Metode lama menggunakan CSS filter `filter: blur() contrast()` langsung pada pembungkus HTML. Pendekatan ini memiliki cacat fatal:
1. **Teks & Gambar Rusak:** Font menjadi buram/kabur (*fuzzy*), gambar foto terdistorsi dan kehilangan detail.
2. **Bayangan Hilang:** Operasi kontras alfa tinggi memangkas dan menghancurkan seluruh efek `box-shadow`.
3. **Safari / WebKit Bug:** WebKit sering mengalami artefak visual pecah saat CSS `url(#filter)` diaplikasikan ke elemen HTML DOM.
4. **Terbatas pada Dekorasi:** Akhirnya efek cairan hanya dipakai untuk bulatan-bulatan hiasan yang tidak fungsional.

---

## 2. Arsitektur Dua Lapis (Two-Layer Silhouette Architecture)

Untuk menghasilkan cairan elastis yang mempertahankan ketajaman 100% pada elemen UI:

```
┌────────────────────────────────────────────────────────┐
│  LAYER 2: CONTENT LAYER (Real HTML DOM)                │
│  - Teks, ikon SVG, foto, tombol, input, ARIA          │
│  - 100% Crisp / Tajam Pixel, Tanpa Filter Blur        │
│  - Hit-target & event listener tetap normal            │
└──────────────────────────┬─────────────────────────────┘
                           │ (Posisi tersinkronisasi)
┌──────────────────────────▼─────────────────────────────┐
│  LAYER 1: SILHOUETTE LAYER (SVG Canvas / Background)   │
│  - Membawa bentuk blob / tetesan cairan               │
│  - Membawa filter SVG <feGaussianBlur> + <feColorMatrix>│
│  - Membawa bayangan gabungan (Merged Drop Shadow)      │
│  - Merata di Safari, Chrome, Firefox                  │
└────────────────────────────────────────────────────────┘
```

---

## 3. Empat Pola Efek Utama (The Four Liquid Effects)

### A. Morph (Peleburan Tetesan Cairan)
Ketika dua elemen saling mendekat, massa cairan saling menjangkau dan melebur secara elastis seperti jelly.
- **Penggunaan:** Menu aksi mengembang (*expanding fab*), avatar grup bertumpuk, panel transisi.
- **Rasio Bridging:** Pelekatan terjadi saat nilai blur $\ge$ jarak celah antar elemen.

### B. Move (Jejak Karet Cair / Rubber Trail)
Ketika elemen digeser (*dragged* atau digeser via slider), cairan di belakangnya tertinggal membentuk ekor tetesan elastis (*droplet tail*) yang kemudian memantul menyatu kembali.

### C. Melt (Peleburan Dua Gambar)
Dua visual yang saling bersentuhan meleburkan tepiannya dengan distorsi gelombang turbulensi (*turbulence displacement*), menghasilkan efek marmer cair.

### D. Bend (Lenturan Inersia Kecepatan)
Badan komponen melengkung secara aerodinamis mengikuti kecepatan geser jempol pengguna (*velocity arc*), lalu kembali tegak saat berhenti.

---

## 4. Implementasi SVG Filter Standar Bersih (Zero-Dependency)

```html
<svg width="0" height="0" class="absolute pointer-events-none" aria-hidden="true">
  <defs>
    <!-- Filter Gooey Tajam dengan Rekonstruksi Alfa -->
    <filter id="liquid-gooey-filter" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="8" result="blur" />
      <feColorMatrix in="blur" mode="matrix" 
        values="1 0 0 0 0  
                0 1 0 0 0  
                0 0 1 0 0  
                0 0 0 19 -9" result="goo" />
      <feComposite in="SourceGraphic" in2="goo" operator="atop" />
    </filter>
  </defs>
</svg>
```

---

## 5. Standar Rekayasa Mas Bagas (SOP UI v2.0)
1. **Zero Text Degradation:** Teks tombol dan label WAJIB berada di Content Layer (Layer 2) agar keterbacaan tetap 100% tajam.
2. **Fisika Pegas Alami:** Durasi pemisahan tetesan wajib menggunakan `cubic-bezier(0.34, 1.56, 0.64, 1)` untuk hentakan membal (*overshoot*).
3. **Mobile Touch Safe:** Jarak sentuh tombol minimal 44px dengan target hit yang tidak bergeser dari posisi visual akhir.
