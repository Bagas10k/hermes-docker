---
name: shader-canvas-flow
description: "Render interactive WebGL GLSL shaders for vibe coding."
version: 1.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [webgl, glsl, fragment-shader, vibe-coding, flow-state, raymarching, ambient-canvas]
    related_skills: [dynamic-canvas-backdrop, fluid-interactive-surface, spatial-canvas-ui-physics]
---

# Shader Canvas Flow Skill

Engine WebGL fragment shader interaktif 60 FPS untuk antarmuka vibe coding, visual background canvas, dan ambient flow-state. Menghadirkan prosedural domain warping fBM, metaballs reaktif audio/kursor, raymarched volumetric fog, dan dynamic resolution throttling dengan auto-sleep 0% GPU saat idle.

## When to Use

- Membangun latar belakang vibe coding interaktif berbasis GLSL fragment shader (fBM noise, domain warping, raymarching ringan).
- Menciptakan efek visual procedural fluid-like atau aurora ambient beresolusi tinggi tanpa library raksasa (Three.js/Babylon.js).
- Mengintegrasikan reaktivitas kursor (posisi + kecepatan seret) dan keystroke cadence ke parameter seragam (`uniform`).
- Butuh performa stabil 60 FPS di laptop hemat baterai dengan proteksi context lost (`webglcontextlost`) dan auto-sleep 0% GPU.

Don't use for:
- Efek DOM sederhana yang cukup dengan CSS `radial-gradient` (gunakan `dynamic-canvas-backdrop`).
- Simulasi fluida Navier-Stokes 2D fisika nyata dengan grid adveksi kecepatan (gunakan `fluid-interactive-surface`).

## Prerequisites

- Browser modern dengan dukungan WebGL 1.0 / WebGL 2.0 (`canvas.getContext('webgl2')` atau `webgl`).
- Zero dependencies eksternal: murni single-file vanilla HTML/JS dengan embedded GLSL shader strings.
- Node.js (v18+) untuk menjalankan CLI preview atau headless test harness.

## Quick Reference

Canonical invocation & testing via `terminal`:

```bash
# Validasi sintaks shader dan test harness WebGL offline
node ~/.hermes/skills/creative/shader-canvas-flow/scripts/test_shader_harness.js

# Generate standalone HTML preview artifact
node ~/.hermes/skills/creative/shader-canvas-flow/scripts/generate_shader_artifact.js --preset=aurora --output=preview.html
```

## Architecture & Mathematical Mechanics

### 1. Model Mekanistik GLSL Uniforms & Ray Transform
Sistem memetakan input interaktif menjadi vektor seragam (*uniforms*) deterministik yang diumpankan ke fragment shader setiap frame:

$$I_{\text{out}}(x, y) = f(u\_resolution, u\_time, u\_mouse, u\_energy, u\_palette)$$

- **Domain Warping fBM (Fractional Brownian Motion):**
  $$q = \begin{pmatrix} fBM(p + 0.00 \cdot t) \\ fBM(p + 5.2 \cdot t) \end{pmatrix}, \quad r = \begin{pmatrix} fBM(p + 4.0 \cdot q + 1.7) \\ fBM(p + 4.0 \cdot q + 8.3) \end{pmatrix}$$
  $$f(p) = fBM(p + 4.0 \cdot r)$$
  Menghasilkan pusaran organik dinamis tanpa lag komputasi partikel diskrit.
- **Dynamic DPR Throttling (Hukum Amdahl GPU Fragment Fill-Rate):**
  Di layar Retina/4K, rendering fragment shader pada native DPR 2.0-3.0 menghabiskan 4x-9x fragment computations per frame. Shader Canvas Flow mengunci render buffer pada resolusi adaptif:
  $$\text{Target DPR} = \min(1.5, \text{devicePixelRatio})$$
  Jika frametime $t_{\text{frame}} > 18\text{ms}$ (drop di bawah 55 FPS), buffer resolusi diturunkan otomatis ke $0.75\times$ dengan bilinear upscaling canvas CSS.

### 2. Bayesian Confidence & Fallback Bounds
- Prior keyakinan WebGL2 vs WebGL1: $P(\text{WebGL2} \mid \text{Modern Browser}) \approx 0.98$.
- Fallback deterministik: Jika `getContext('webgl2')` gagal, sistem beralih ke `webgl` dengan ekstensi standard GLSL precision qualifiers tanpa melempar runtime exception.
- Fallback ekstrem: Jika WebGL hardware acceleration mati total (`null`), sistem fallback mulus ke kanvas 2D procedural radial glow.

### 3. System Design & Auto-Sleep Guardrail
- **Zero-Waste Auto-Sleep:** Mengukur delta pergerakan kursor dan laju ketikan. Jika tidak ada intervensi selama 6 detik dan energi internal meluruh di bawah ambang batas $\epsilon = 0.01$, loop `requestAnimationFrame` ditangguhkan otomatis (0% GPU).
- **Wake-on-Interaction:** Listener pasif (`mousemove`, `keydown`, `touchmove`, `scroll`) mengaktifkan kembali rendering secara instan tanpa latensi terasa.

## Procedure

1. **Inisialisasi WebGL Context & Shaders:**
   - Gunakan quad vertikal penuh (-1.0 s/d 1.0) dengan vertex shader 2-segitiga instan.
   - Kompilasi fragment shader dengan pengecekan `gl.getShaderParameter(shader, gl.COMPILE_STATUS)`.
2. **Koneksi Parameter Uniform Reaktif:**
   - Bind `u_resolution`, `u_time`, `u_mouse` (vec4: x, y, clickX, clickY), `u_energy` (float akumulasi ketikan), `u_warp`, dan `u_palette`.
3. **Penerapan Palet Warna Terkalibrasi (Inigo Quilez Cosine Palette):**
   - Gunakan formula harmonis:
     $$\text{color}(t) = a + b \cdot \cos(2\pi(c \cdot t + d))$$
   - Menghasilkan gradasi warna cerah, kaya, dan estetis tanpa clipping RGB kaku.
4. **Isolasi Pointer & Pencegahan Scroll Leak:**
   - Pasang `pointer-events: none` pada container canvas backdrop agar klik dan scroll teks kode di editor foreground tidak terhalang.
5. **Verifikasi Framerate & Context Restitution:**
   - Pantau frametime via rolling average 60 frame.
   - Daftarkan listener `webglcontextlost` dan `webglcontextrestored` untuk pemulihan otomatis jika OS menangguhkan GPU.

## Pitfalls

1. **Precision Qualifier Missing di GLSL ES 1.0:**
   - Fragment shader gagal kompilasi di WebGL 1.0 jika baris pertama tidak mendeklarasikan `precision highp float;` atau `precision mediump float;`.
   - *Solusi:* Selalu injeksikan header presisi adaptif sebelum source shader.
2. **GPU Memory Leak pada Hot-Reloading:**
   - Menimpa instance canvas berulang kali tanpa memanggil `gl.deleteProgram`, `gl.deleteShader`, dan `gl.deleteBuffer` menyebabkan GPU VRAM bocor hingga browser crash (Out of Memory).
   - *Solusi:* Selalu sediakan metode `destroy()` yang membebaskan seluruh buffer dan detaches event listeners.
3. **High-DPI Retina Burning:**
   - Mengalikan width/height kanvas dengan `window.devicePixelRatio = 3` di layar mobile memicu thermal throttling dan baterai boros.
   - *Solusi:* Kunci render resolution skala maksimum 1.5x.

## Verification

Verifikasi keberhasilan implementasi:
1. Skrip `test_shader_harness.js` mengeksekusi kompilasi shader offline dan kalkulasi uniform deterministik tanpa error.
2. Artefak HTML preview memuat canvas WebGL, mengalirkan domain warping 60 FPS, bereaksi terhadap kursor mouse, dan memasuki auto-sleep setelah masa idle.
3. Suite Playwright Chromium 7-viewport (320px–1440px) lolos 0 Axe violations, 0 horizontal overflow, dan 0 anti-pattern Impeccable.
