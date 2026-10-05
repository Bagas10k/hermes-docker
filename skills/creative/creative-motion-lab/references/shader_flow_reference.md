# WebGL Fragment Shader Flow Reference

Dokumentasi matematis dan implementasi referensi untuk shader prosedural berbasis GLSL ES di kanvas latar belakang ambient vibe coding.

## 1. Minimal Vertex Shader (Full-Screen Quad)

```glsl
attribute vec2 a_position;
varying vec2 v_uv;

void main() {
  v_uv = (a_position + 1.0) * 0.5;
  gl_Position = vec4(a_position, 0.0, 1.0);
}
```

Buffer quad cukup 6 koordinat (2 segitiga): `[-1, -1,  1, -1, -1,  1, -1,  1,  1, -1,  1,  1]`.

## 2. Inigo Quilez Cosine Palette Equations

Warna dihasilkan langsung di GPU tanpa lookup texture:
$$c(t) = a + b \cdot \cos(2\pi(c \cdot t + d))$$

Vektor parameter palet preset unggulan:

| Preset | a (offset) | b (amp) | c (freq) | d (phase) | Karakteristik |
|---|---|---|---|---|---|
| Aurora Borealis | `(0.1, 0.3, 0.4)` | `(0.2, 0.4, 0.5)` | `(1.0, 1.0, 1.0)` | `(0.0, 0.33, 0.67)` | Hijau emerald, cyan, ungu lembut |
| Cyber Amber Gold | `(0.5, 0.4, 0.2)` | `(0.5, 0.4, 0.2)` | `(1.0, 1.0, 1.0)` | `(0.0, 0.15, 0.30)` | Emas hangat, amber, charcoal pekat |
| Deep Obsidian Nebula | `(0.15, 0.12, 0.25)` | `(0.2, 0.15, 0.3)` | `(0.8, 0.8, 0.8)` | `(0.1, 0.2, 0.5)` | Ungu elektrik, biru malam, kontras tinggi |

## 3. High-Performance fBM Noise (No Trig Lag)

Implementasi fBM 4-oktaf hemat instruksi:

```glsl
precision highp float;
uniform vec2 u_resolution;
uniform float u_time;
uniform vec4 u_mouse;
uniform float u_energy;
varying vec2 v_uv;

float hash(vec2 p) {
  p = fract(p * vec2(123.34, 456.21));
  p += dot(p, p + 45.32);
  return fract(p.x * p.y);
}

float noise(vec2 p) {
  vec2 i = floor(p);
  vec2 f = fract(p);
  f = f * f * (3.0 - 2.0 * f); // Hermite curve
  return mix(
    mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x),
    mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x),
    f.y
  );
}

float fbm(vec2 p) {
  float v = 0.0;
  float a = 0.5;
  vec2 shift = vec2(100.0);
  mat2 rot = mat2(cos(0.5), sin(0.5), -sin(0.5), cos(0.5));
  for (int i = 0; i < 4; ++i) {
    v += a * noise(p);
    p = rot * p * 2.0 + shift;
    a *= 0.5;
  }
  return v;
}
```

## 4. Lifespan & GPU Memory Lifecycle
- Jangan re-instantiate WebGL context setiap pergantian komponen UI.
- Gunakan 1 canvas singleton di root level (`z-index: 0; pointer-events: none`).
- Pasang auto-sleep saat delta interaksi > 8 detik.
