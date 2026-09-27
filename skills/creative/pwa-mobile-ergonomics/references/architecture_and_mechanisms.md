# Arsitektur PWA & Mobile Web Tactile Ergonomics

## 1. Latar Belakang & Masalah
Mobile web app sering kali menderita masalah laten yang merusak pengalaman pengguna (*vibe*):
1. **Address Bar Jump & Rubber Banding**: Saat menggulir form atau modal, bar peramban muncul-tenggelam dan memicu layout shift.
2. **Form Native yang Kaku**: Elemen `<select>` dan popup bawaan HP terasa lambat, tidak estetik, dan merusak imersi visual.
3. **Service Worker Caching Trap**: Service worker naif meng-cache seluruh request HTTP, sehingga endpoint SSE/WebSocket/API telemetri membeku (*stuck on stale data*).
4. **Emoji Inconsistency**: Render emoji berbeda di setiap vendor OS (iOS, OneUI, Xiaomi) yang menurunkan wibawa antarmuka kelas industri.

## 2. Solusi Rekayasa & Standar Desain
Arsitektur PWA Tactile Ergonomics menerapkan:
- **Pemisahan Jalur Cache (Cache Partitioning)**:
  - Cache-first untuk file statis immutable (`.js`, `.css`, SVG, fonts).
  - Network-only mutlak untuk endpoint dinamis (`/api/`, `/sse`, `/stream`, `/ws`).
- **Spring Bottom Sheet Berbasis Touch Physics**:
  - Menggunakan gesture pointer event terkalibrasi (`touchstart`, `touchmove`, `touchend`).
  - Kurva snapping: `cubic-bezier(0.32, 0.72, 0, 1)`.
  - Haptic feedback via `navigator.vibrate([10])` saat snap terjadi.
- **Viewport Safe-Area Insets**:
  - `viewport-fit=cover` dan integrasi CSS `env(safe-area-inset-top)` serta `env(safe-area-inset-bottom)` untuk perangkat berponi/island.
- **Sterilisasi Zero-Emoji**:
  - 100% menggunakan SVG monokrom bergaya Lucide/Heroicons dengan `stroke-width: 2.2-2.5`.

## 3. Hasil Validasi
Skrip audit otomatis `pwa_scaffold.py` memverifikasi 4 kriteria utama:
- Kelengkapan `manifest.json` (`display: standalone`, icons array).
- Skema isolasi Service Worker `sw.js`.
- Penanganan safe area insets pada `index.html`.
- Sanitasi ketiadaan karakter emoji Unicode di seluruh antarmuka.
