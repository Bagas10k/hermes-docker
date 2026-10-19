# Generative SVG Patterns, Gradients & Visual Generators

Skill ini adalah **panduan baku pembangkitan pola visual generatif (SVG Patterns, Grainy Noise Gradients, Page Dividers, dan Clean Shading)** untuk antarmuka web, kartu Bank Komponen, dan feed warta 60 FPS tanpa beban aset eksternal.

---

## 1. Empat Rujukan Desain Visual (Kurasi Mas Bagas)
Berdasarkan rujukan kurasi desainer `@krishnadesign.ui`:
1. **`SVGeneration` (svgeneration.com):** Pola geometri berulang SVG murni (kisi, titik, garis isometrik, blueprint).
2. **`Tabbied` (tabbied.com):** Pola seni generatif minimalis modern untuk latar kartu dan ilustrasi aksen.
3. **`Noise & Gradient` (noiseandgradient.com):** Gradien atmosferik bertekstur butiran pasir (*film grain / dithered noise*) ala Linear dan macOS.
4. **`Omatsuri` (omatsuri.app):** Toolkit frontend open-source (SVG-to-JSX, pembagi halaman wave/angled, dan generator bayangan).

---

## 2. Pola 1: Kisi Blueprint Isometrik Vektor Ringan (SVGeneration / Zero Latency)
Gunakan SVG pattern inline untuk latar belakang kartu konsol tanpa gambar PNG/JPG:

```html
<svg width="100%" height="100%" class="absolute inset-0 opacity-10 pointer-events-none">
  <defs>
    <pattern id="grid-pattern" width="24" height="24" patternUnits="userSpaceOnUse">
      <path d="M 24 0 L 0 0 0 24" fill="none" stroke="currentColor" stroke-width="1" />
      <circle cx="24" cy="24" r="1.5" fill="currentColor" />
    </pattern>
  </defs>
  <rect width="100%" height="100%" fill="url(#grid-pattern)" />
</svg>
```

---

## 3. Pola 2: Gradien Butiran Halus (Noise & Grain Gradient ala Linear)
Membuat latar belakang kartu memiliki kedalaman visual taktil (*tactile depth*) menggunakan filter SVG `feTurbulence`:

```html
<div class="relative overflow-hidden rounded-xl bg-gradient-to-br from-[#16181D] to-[#0D0E12] border border-white/10 p-6">
  <!-- Grainy Noise Overlay -->
  <svg class="absolute inset-0 w-full h-full opacity-15 pointer-events-none mix-blend-overlay">
    <filter id="noiseFilter">
      <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="3" stitchTiles="stitch" />
    </filter>
    <rect width="100%" height="100%" filter="url(#noiseFilter)" />
  </svg>
  
  <div class="relative z-10">
    <!-- Konten Kartu Bersih -->
  </div>
</div>
```

---

## 4. Pola 3: Angled & Slanted Divider (Omatsuri Style)
Pembagi seksi yang tajam dan presisi tanpa grafis berat:

```html
<div class="relative w-full h-12 overflow-hidden pointer-events-none">
  <svg viewBox="0 0 1200 120" preserveAspectRatio="none" class="relative block w-full h-full fill-[#0c0d0e]">
    <path d="M1200 0L0 0 1200 120z"></path>
  </svg>
</div>
```
