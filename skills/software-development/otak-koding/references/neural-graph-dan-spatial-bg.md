# Arsitektur 3D Neural Knowledge Graph: Kanvas Latar Belakang, Spasial Spasial & Sinkronisasi Real-Time

Panduan teknis dan standar baku untuk mengintegrasikan visualisasi jaringan pengetahuan 3D (Three.js & 3d-force-graph) sebagai antarmuka mandiri maupun latar belakang interaktif pada halaman web berstandar produksi.

---

## 1. Aturan Kanvas Latar Belakang (Ambient Background Doctrine)

Ketika visualisasi graf 3D difungsikan sebagai latar belakang dinamis di balik konten halaman (landing page, showcase, atau portal):

1. **Murni Bentuk Geometris Tanpa Label Teks Mengambang:**
   * Wajib menonaktifkan sprite label teks mengambang:
     ```javascript
     .nodeThreeObject(() => null)
     ```
   * *Alasan:* Menampilkan puluhan judul teks di atas bola simpul akan bertabrakan langsung dengan tipografi halaman (hero title, heading, kartu artikel), menciptakan polusi visual dan menurunkan nilai keterbacaan (readability).
   * Keterangan simpul tetap diakomodasi melalui tooltip mengambang (`.nodeLabel(...)`) yang hanya muncul saat kursor menyentuh bola simpul (*hover*), atau via kartu detail saat diklik.

2. **Tata Kelola Lapisan Pasif & Anti-Scroll Leakage (Zero Gesture Hijacking):**
   * **DOKTRIN MUTLAK:** Latar belakang 3D dilarang keras mencegat, menangkap, atau membekukan scroll native halaman web. Kanvas harus 100% pasif terhadap mouse wheel, touch drag, dan click di area kosong dokumen (*empty space*).
   * **Konfigurasi CSS Mutlak (Semua Turunan & Canvas):**
     ```css
     #bg-3d-graph,
     #bg-3d-graph *,
     #bg-3d-graph canvas,
     #bg-3d-graph .scene-container {
       pointer-events: none !important;
       touch-action: auto !important;
       user-select: none !important;
     }
     #bg-3d-graph {
       position: fixed;
       top: 0;
       left: 0;
       width: 100vw;
       height: 100vh;
       z-index: 0;
     }
     .shell {
       position: relative;
       z-index: 10;
       /* shell adalah aliran normal dokumen, tidak perlu pointer-events: none */
     }
     ```
   * **Pelepasan Kontrol Three.js (JS Initialization):**
     Nonaktifkan dan musnahkan kontrol navigasi bawaan serta amankan inline style canvas:
     ```javascript
     Graph.enableNavigationControls(false);
     const controls = Graph.controls();
     if (controls) {
         controls.enabled = false;
         if (typeof controls.dispose === 'function') controls.dispose();
     }
     const canvas = graphContainer.querySelector('canvas');
     if (canvas) {
         canvas.style.setProperty('pointer-events', 'none', 'important');
         canvas.style.setProperty('touch-action', 'auto', 'important');
     }
     ```
   * *Hasil:* Gesture roda mouse (*wheel*), usapan jari (*touch swipe* di HP), dan trackpad di area kosong mana pun (margin kiri/kanan atau sela-sela kartu) 100% menggulirkan halaman web secara instan dan bebas hambatan tanpa bocor ke kanvas 3D.

---

## 2. Kalibrasi Kontras & Sinkronisasi Tema Ganda (Light & Dark)

Graf 3D wajib beradaptasi secara instan saat sistem beralih antara Tema Terang (*Warm Paper*) dan Tema Gelap (*Cosmic Space*):

| Komponen Graf | Tema Terang (Warm Paper) | Tema Gelap (Cosmic Space) |
|---|---|---|
| Latar Belakang Tiga Dimensi | `#f8f7f3` / `#f8fafc` | `#07080b` (void black) |
| Garis Relasi Default (Idle) | `rgba(14, 165, 233, 0.45)` (azure sky) | `rgba(56, 189, 248, 0.55)` (cyan neon) |
| Garis Relasi Aktif (Highlighted) | `#0284c7` (deep cobalt, lebar 3.8px - 4.5px) | `#00f0ff` (laser cyan, lebar 3.8px - 4.5px) |
| Garis Relasi Teredam (Dimmed) | `rgba(203, 213, 225, 0.22)` (soft silver) | `rgba(51, 65, 85, 0.18)` (deep slate) |
| Permukaan Kartu UI di Atas Graf | `rgba(255, 255, 255, 0.78)` + `blur(16px)` | `rgba(15, 17, 24, 0.82)` + `blur(16px)` |

**Prosedur Update Dinamis:**
Saat event pengalih tema dipicu, mutakhirkan Three.js secara langsung tanpa me-reinstansiasi instance graf:
```javascript
Graph.backgroundColor(theme.bg);
Graph.linkColor(Graph.linkColor());
Graph.nodeColor(Graph.nodeColor());
```

---

## 3. Morfing Sudut Pandang Kamera Berdasarkan Posisi Scroll (Spatial Scroll Angle Morphing)

Agar latar belakang graf berinteraksi harmonis dengan perjalanan baca pengguna, sudut pandang kamera 3D dimorfing secara adaptif:

1. **Pemetaan Sudut Tematik per Seksi:**
   * **Hero Section:** Pandangan frontal luas (`pos: { x: 0, y: 75, z: 420 }, lookAt: { x: 0, y: 0, z: 0 }`).
   * **Showcase / Proyek:** Orbit miring dinamis (*tilted side orbit*, misal `x: 330, y: 130, z: 250`).
   * **Arsitektur / Bank Desain:** Sudut pandang atas konstelasi 2.5D (*top-down bird's-eye view*, misal `y: 450, z: 90`).
   * **Footer:** Sudut sapuan bawah (*low-angle perspective*).

2. **Deteksi Berbasis Jarak Pusat Layar (Viewport Center Distance):**
   * Hindari penentuan berdasarkan status `isIntersecting` biner murni jika terdapat kontainer besar bertingkat.
   * Gunakan kalkulasi selisih jarak absolut antara titik tengah elemen dan titik tengah layar pandang (*viewCenter* `window.innerHeight * 0.45`):
     ```javascript
     const dist = Math.abs((rect.top + rect.height * 0.5) - viewCenter);
     ```
   * Pilih seksi dengan `dist` terkecil untuk memicu `Graph.cameraPosition(targetPos, targetLookAt, 1200)`.

3. **Kontinuitas Orbit Pasca-Transisi & Engine Sinkronisasi Scroll Murni (Scroll-Slave Mode):**
   * Catat radius (`orbitRadius`) dan elevasi (`orbitHeight`) dari posisi target kamera baru.
   * *Mode Scroll-Slave (Rekomendasi Utama untuk Latar Belakang):* Hindari transisi berbasis durasi waktu statis (`setTimeout` / tween 1.2s) jika pengguna menggulir cepat. Jadikan orientasi kamera sebagai fungsi murni dari progres scroll dokumen:
     ```javascript
     const progress = window.scrollY / (document.documentElement.scrollHeight - window.innerHeight);
     // Di dalam requestAnimationFrame (60 FPS):
     smoothProgress += (progress - smoothProgress) * 0.085;
     const angle = (smoothProgress * Math.PI * 2.2) + ambientDrift;
     const radius = 430 - Math.sin(smoothProgress * Math.PI) * 50;
     const elevation = 65 + Math.sin(smoothProgress * Math.PI) * 220 - (smoothProgress * 95);
     Graph.cameraPosition(
         { x: radius * Math.sin(angle), y: elevation, z: radius * Math.cos(angle) },
         { x: 0, y: 0, z: 0 },
         0
     );
     ```
   * Pengguna merasakan sensasi terbang mengitari konstelasi pengetahuan secara natural saat membaca portofolio, dengan 100% responsivitas scroll dokumen native.

---

## 4. Pipeline Sinkronisasi Pengetahuan Real-Time (Server-Sent Events)

Penambahan catatan atau simpul baru pada direktori pengetahuan wajib terpantul ke kanvas browser secara seketika tanpa memerlukan refresh halaman:

1. **Spesifikasi Endpoint Backend Express (`/api/graph/stream`):**
   * Header wajib:
     ```javascript
     res.setHeader('Content-Type', 'text/event-stream');
     res.setHeader('Cache-Control', 'no-cache');
     res.setHeader('Connection', 'keep-alive');
     res.setHeader('X-Accel-Buffering', 'no'); // Nonaktifkan buffer Nginx untuk latensi nol
     ```
   * Heartbeat Ping: Jalankan `res.write(': ping\n\n')` tiap 20–25 detik untuk mencegah pemutusan koneksi oleh reverse proxy (Cloudflare/Nginx timeout).

2. **File Watcher Otomatis dengan Debounce:**
   * Pantau direktori catatan markdown menggunakan `fs.watch(DIR, { recursive: true })`.
   * Lindungi proses pemindaian dari lonjakan berkas beruntun menggunakan debounce timer (600ms – 800ms) sebelum memanggil `scanVault()` dan membroadcast payload `vault_updated`.

3. **Penyambungan Dinamis di Frontend:**
   * Klien mendengarkan via `new EventSource('/api/graph/stream')`.
   * Saat menerima event `vault_updated`:
     ```javascript
     Graph.graphData({ nodes: data.nodes, links: data.links });
     ```
   * Tampilkan indikator status (*real-time sync toast*) yang memudar otomatis setelah 4 detik.

---

## 5. Jebakan Operasional & Pitfall Teruji

1. **Pitfall Strict MIME Boundary pada Aset JS Statis:**
   * *Gejala:* Peramban memunculkan galat `Refused to execute script from '.../script.js' because its MIME type ('application/json') is not executable, and strict MIME type checking is enabled` dan respons berstatus `401 Unauthorized`.
   * *Penyebab:* Middleware pembatas keamanan (misal `privacy-boundary.js`) belum memasukkan berkas JS statis baru ke dalam daftar whitelist publik (`PUBLIC`), sehingga permintaan dianggap privat dan dialihkan ke respons JSON autentikasi.
   * *Aturan:* Setiap penambahan berkas script statis publik wajib didaftarkan ke array whitelist rute publik server sebelum pengujian dilakukan.

2. **Pitfall Frontmatter Mentah pada Renderer Markdown:**
   * *Penyebab:* Parser Markdown langsung menerima teks mentah berkas `.md` yang diawali blok metadata YAML (`--- ... ---`).
   * *Aturan:* Selalu bersihkan blok frontmatter sebelum dilewatkan ke parser:
     ```javascript
     const cleanMarkdown = raw.replace(/^[\s\r\n]*---[\s\S]*?---\s*/, '');
     drawerContent.innerHTML = marked.parse(cleanMarkdown);
     ```

3. **Pitfall Pembajakan Scroll Latar Belakang & Cache Stale (Empty-Space Scroll Freezing):**
   * *Gejala:* Roda mouse atau usapan jari macet saat kursor berada di ruang kosong atau sela-sela kartu, dan kanvas 3D malah ter-zoom/terputar (*bocor ke background*).
   * *Penyebab Mekanistik:* Kontrol Three.js (`TrackballControls`/`OrbitControls`) memasang listener non-pasif `wheel` dan atribut inline `touch-action: none` pada elemen canvas. Jika CSS tidak menyematkan `pointer-events: none !important` pada kontainer, semua turunan (*), dan canvas, atau kontrol Three.js tidak di-dispose, browser memprioritaskan canvas di atas document body. Selain itu, cache reverse proxy/browser dapat mempertahankan skrip lama jika versi aset tidak di-bump.
   * *Aturan:* Wajib isolasi total via CSS `#bg-canvas, #bg-canvas *, canvas { pointer-events: none !important; touch-action: auto !important; }`, panggil `controls.dispose()` di JavaScript, dan selalu sematkan cache buster (`?v=<timestamp_atau_hash>`) pada tag skrip/CSS.
