# Progressive Blur & Frosted Glass (Linear / Apple / Blender Tier)

Skill ini adalah **panduan baku arsitektur efek Progressive Blur (Blur Bertingkat / Depth of Field) dan Frosted Glass Fisik** untuk web antarmuka dan mobile viewport 60 FPS sesuai standar studio Pixelpoint dan Linear.

---

## 1. Konsep Utama: Mengapa Blur Biasa Terlihat Murahan?
- **Blur Biasa (`backdrop-filter: blur(12px)`):** Memotong layar secara seragam dan mendadak seperti kaca buram datar murahan.
- **Progressive Blur (Blur Bertingkat Fisik):** Semakin mendekati tepi layar atau semakin jauh objek, efek blur meningkat secara bertahap (*gradient of blur*), meniru fenomena optik kamera fisik dan render material Blender / Glassmorphism kasta atas.

---

## 2. Implementasi CSS Native Murni (4-Layer Masked Ramp)

Untuk performa 60 FPS tanpa membebani GPU rendering rasterization:

```html
<!-- Progressive Frosted Glass Header / Dock -->
<div class="relative w-full h-32 overflow-hidden pointer-events-none select-none">
  <!-- Layer 1: Base Subtle Blur -->
  <div class="absolute inset-0 backdrop-blur-[2px] [mask-image:linear-gradient(to_bottom,black_0%,transparent_100%)]"></div>
  
  <!-- Layer 2: Mid Blur -->
  <div class="absolute inset-0 backdrop-blur-[6px] [mask-image:linear-gradient(to_bottom,black_25%,transparent_85%)]"></div>
  
  <!-- Layer 3: Heavy Optical Blur -->
  <div class="absolute inset-0 backdrop-blur-[14px] [mask-image:linear-gradient(to_bottom,black_50%,transparent_75%)]"></div>
  
  <!-- Layer 4: Deep Edge Frost -->
  <div class="absolute inset-0 backdrop-blur-[28px] [mask-image:linear-gradient(to_bottom,black_75%,transparent_60%)]"></div>

  <!-- Surface Tint (White or Dark Obsidian Tint) -->
  <div class="absolute inset-0 bg-[#141517]/40 [mask-image:linear-gradient(to_bottom,black_60%,transparent_100%)]"></div>
</div>
```

---

## 3. Aturan Efisiensi & Kinerja (60 FPS Safe)
1. **Dilarang Menganimasikan Properti `filter` / `backdrop-filter`:**  
   Menganimasikan nilai blur pixel-by-pixel memaksa browser melakukan rasterisasi ulang setiap frame dan menjatuhkan FPS ke bawah 30.
2. **Animasi Hanya Melalui Opacity:**  
   Jika ingin efek blur muncul atau memudar (fade on scroll), **animasikan properti `opacity` (0 ➔ 1)** pada kontainer progressive blur.
3. **Posisikan di Atas Konten (Composite Layer):**  
   Wajib diberi `pointer-events: none` dan `aria-hidden="true"` agar tidak memblokir interaksi klik tombol di bawahnya.

---

## 4. Standar Interaksi & Motion Lifecycle (SOP Mas Bagas v2.0)
Komponen kartu berlatar progressive frosted glass WAJIB mengadopsi standar gerak:
- **GSAP FLIP Morphing:** Saat kartu diklik, layer frosted glass bermetamorfosis membesar in-place (450ms `power3.out`).
- **Enter Lifecycle:** Lapisan blur muncul dengan fade-in halus (280ms) untuk mencegah drop FPS GPU.
- **Anti-Berkedip Putih (SPA Transition):** Efek kaca blur diuji di atas kanvas gelap terkunci agar tidak pernah memantulkan cahaya putih bocor saat filter/tab berganti.
- **Mobile Touch Optimization:** Masking CSS gradient dioptimalkan hardware-accelerated (`will-change: transform`) untuk layar HP.
