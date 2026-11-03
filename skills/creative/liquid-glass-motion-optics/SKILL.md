---
name: liquid-glass-motion-optics
description: "Use when creating, animating, or reviewing liquid glass refraction, chromatic dispersion (prism fringe), Snell's law WebGL shaders, or 60 FPS motion morphing for UI and web video."
version: 1.0.0
author: "Bagas Cihuy & Hermes Agent"
license: MIT
metadata:
  hermes:
    tags: [liquid-glass, refraction, optics, chromatic-aberration, shaders, webgl2, svg-displacement, remotion, 60fps, video-motion]
    related_skills: [motion-ui-lifecycle-and-morphing, universal-icon-morphing, upnormal-ui-architecture, hallmark, canvas-spatial-grounding]
---

# Liquid Glass Motion Optics & Physical Refraction

Production standard for creating Apple VisionOS-grade **liquid glass surfaces, optical refractions, chromatic prism dispersion, and 60 FPS motion morphing** in web applications and automated video renderers (Remotion / Puppeteer).

---

## 1. Physical Principles: Optical Refraction vs Blur

Traditional "glassmorphism" using simple `backdrop-filter: blur(20px)` is considered **AI Slop** because real glass does not merely blur—**real glass bends light ray paths (refraction)** at its curvature and **splits light into colors (chromatic dispersion)**:

1. **Hukum Pembiasan Snellius (Snell's Law):**
   $$n_1 \sin\theta_1 = n_2 \sin\theta_2$$
   Di mana $n_1 \approx 1.0$ (udara) dan $n_2 \approx 1.45 - 1.52$ (kaca optik). Bagian tepi kaca melengkung (bevel) membelokkan berkas cahaya di belakangnya ke arah dalam (magnification bulge).
2. **Dispersi Kromatik (Chromatic Aberration / Prism Fringe):**
   Indeks bias bergantung pada panjang gelombang ($n_{red} < n_{green} < n_{blue}$). Di tepian lengkungan, kanal merah mengalami pembiasan lebih rendah daripada kanal biru, menghasilkan pendar pelangi tipis yang realistis.
3. **Pantulan Fresnel (Schlick's Approximation):**
   Sudut pandang tegak lurus meneruskan cahaya (transparan), sedangkan sudut tepi yang miring memantulkan cahaya lebih kuat (*specular edge reflection*).

---

## 2. Arsitektur Dua Jalur: WebGL vs SVG Filter

| Jalur | Teknologi | Kapan Digunakan? |
|---|---|---|
| **Jalur SVG Filter (`feDisplacementMap`)** | SVG Filter + CSS `backdrop-filter: url(#id)` | **Default untuk UI & Teks Live:** Elemen HTML tetap hidup, teks tetap bisa diseleksi/diklik, ringan, dan 100% kompatibel di Chromium video renderer. |
| **Jalur Shader WebGL2 (GLSL ES 3.00)** | WebGL Canvas + Texture FBO | **Default untuk Full Video Canvas / Background Shader:** Memerlukan Snell's Law fisika murni, simulasi IOR nyata, dan caustics cair dinamis. |

---

## 3. Aturan Sakral Animasi Morphing 60 FPS (Anti-Lag)

Saat kartu atau tombol kaca membesar, mengecil, atau membuka modal:
1. **DILARANG me-raster ulang peta perpindahan (*displacement map*) pada setiap frame!**
   Membuat ulang data URI SVG di setiap frame render (16.6ms) akan memicu garbage collection dan frame drop (*stutter*).
2. **Wajib Animasikan Atribut Skala Filter Saja:**
   Ubah atribut `scale` pada elemen `<feDisplacementMap>` secara dinamis via JavaScript/CSS transform atau GSAP:
   ```javascript
   // Ringan, dieksekusi langsung oleh GPU compositor
   dispMapElement.setAttribute('scale', currentScale);
   ```
3. **Regenerasi Map Hanya Saat Selesai (*On Settle*):**
   Peta perpindahan baru hanya dihitung ulang satu kali saat animasi transisi dimensi telah berhenti total (*settled*).

---

## 4. Pemanfaatan dalam Pipeline Video (Remotion / Puppeteer)

Di server VPS kita, rendering video untuk **SputarBall**, **SputarAI**, dan **Studio Gerak** dijalankan melalui headless Chromium:
- Headless Chromium mendukung `backdrop-filter: url(#id)` dengan akselerasi GPU penuh.
- Teks berita, logo klub, atau angka metrik AI yang bergeser di bawah panel kaca otomatis terbias dengan pendar prisma pelangi 60 FPS tanpa perlu render berat di Adobe After Effects atau Blender.

---

## 5. Integrasi MCP Server (`liquid-glass`)

Agen dapat memanggil kakas MCP `liquid-glass` secara langsung:
1. `liquid_glass_svg_filter(scale, chroma, border, map_blur, width, height, filter_id)`:
   Menghasilkan markup filter SVG 3-layer chromatic aberration dan CSS `backdrop-filter`.
2. `liquid_glass_component_template(component, title, body, width, height, theme)`:
   Menghasilkan komponen kartu/modal kaca siap pakai.
3. `liquid_glass_webgl_shader(ior, chromatic_spread, bevel_depth)`:
   Menghasilkan kode fragment shader GLSL ES 3.00 untuk kanvas WebGL2.
4. `liquid_glass_remotion_motion_snippet(fps, duration_frames)`:
   Menghasilkan komponen React Remotion untuk video pipeline.

---

## 6. Resep Kode Cepat (Quick Recipe)

### Resep 1: Kartu Kaca Refraktif 1-File (HTML/CSS)
```html
<div class="glass-card">
  <h2>Breaking News</h2>
  <p>Refractive edge bending with real chromatic dispersion.</p>
</div>

<style>
  .glass-card {
    width: 380px;
    height: 220px;
    border-radius: 24px;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.3);
    backdrop-filter: url(#liquid-lens) blur(0.5px);
    -webkit-backdrop-filter: url(#liquid-lens) blur(0.5px);
    box-shadow: 0 20px 50px rgba(0,0,0,0.3), inset 0 1px 1px rgba(255,255,255,0.4);
  }
</style>
```
