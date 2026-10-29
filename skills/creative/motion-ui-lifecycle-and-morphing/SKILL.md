---
name: motion-ui-lifecycle-and-morphing
description: "Use when creating UI motion, card morphing, and animations."
version: 1.0.0
author: Bikagent & Bagas Cihuy
license: MIT
platforms: [linux, macos, windows]
related_skills:
  - upnormal-ui-architecture
  - ui-ux-design-vault
  - creative-visual-mindset
  - progressive-blur
metadata:
  hermes:
    tags: [ui, ux, motion, morphing, gsap, flip, lifecycle, progressive-blur, 60fps]
---

# Motion UI Lifecycle, Morphing & Tactile Feedback

Standar baku rekayasa gerakan antarmuka pengguna (UI/UX Motion) untuk memastikan seluruh transisi komponen terasa hidup, berbobot fisik nyata, dan bebas dari kebiasaan modal pop-up kaku.

## 1. Hukum Wajib Morphing (In-Place Continuity)
- **Zero Abrupt Modals:** Dilarang menggunakan dialog pop-up modal yang tiba-tiba menutupi layar secara kaku tanpa kontinuitas objek.
- **GSAP FLIP Engine:** Komponen kartu ringkasan atau tombol yang disentuh wajib bermetamorfosis (*morph*) membesar di tempatnya (*in-place expansion*) menjadi panel kerja detail.
- **Teknik FLIP (*First, Last, Invert, Play*):**
  1. Rekam koordinat awal elemen (`Flip.getState([card, body])`).
  2. Ubah state DOM (toggle kelas atau tambahkan slot detail).
  3. Mainkan animasi transisi:
     ```javascript
     Flip.from(state, {
       duration: 0.55,
       ease: "power3.out", // Spring inersia alami
       fade: true,
       nested: true        // Teks dan child ikut bermutasi tanpa glitch
     });
     ```

## 2. Motion Lifecycle Trinity (Enter — Loop — Exit)
Setiap elemen dinamis wajib dirancang dengan tiga fase siklus hidup terukur:
1. **Enter Reveal (280ms):**
   - Kurva `ease-out` mendarat anggun (`cubic-bezier(0.16, 1, 0.3, 1)` atau `power3.out`).
   - Transformasi vertikal pendek (`translateY: 16px ➔ 0`) dengan `opacity: 0 ➔ 1`.
2. **Looping Ambient (2.2s):**
   - Gelombang sinus berdenyut tenang (`cubic-bezier(0.45, 0, 0.55, 1)` atau `sine.inOut`) bolak-balik yoyo (`scale: 1 ➔ 1.02`).
   - Menandakan status telemetri/sistem sedang aktif dan bernafas secara real-time.
3. **Exit Dismissal (180ms):**
   - Wajib ~30% lebih cepat daripada animasi masuk.
   - Kurva `ease-in` berakselerasi cepat keluar (`cubic-bezier(0.7, 0, 0.84, 0)` atau `power2.in`), `scale: 1 ➔ 0.92`, `opacity: 1 ➔ 0`.

## 3. Progressive Blur & Frosted Glass (Blender Optics Tier)
Hindari penerapan satu lapis `backdrop-filter: blur(16px)` datar yang terlihat seperti mika plastik murahan.
- **4-Layer Masked Ramp:** Gunakan tumpukan 4 layer blur bertingkat (`2px ➔ 6px ➔ 14px ➔ 26px`) yang masing-masing dibatasi oleh gradien masker (`mask-image: linear-gradient(to top, black 0%, transparent 100%)`).
- **Efisiensi:** Animasikan kemunculan kaca buram HANYA lewat properti `opacity` (bukan menganimasikan angka piksel blur) agar GPU browser tidak melakukan rasterisasi ulang setiap frame.
- **Aksessibilitas:** Berikan `pointer-events: none` dan `aria-hidden="true"` pada kontainer overlay blur.

## 4. Rasio Kontras Tinggi (WCAG 2.2 AAA Min 7:1)
- Latar belakang putih (`#FFFFFF`) wajib menggunakan teks hitam titanium (`#0F172A`) dengan kontras 19:1.
- Dilarang keras teks abu-abu redup di atas putih atau teks gelap di atas hitam pekat.
- Aksen terang (Kuning `#FFE600`, Merah `#DC2626`, Hijau `#10B981`) hanya boleh menyentuh 1 elemen pemicu fokus.

## 5. Performa Hardware & Pencegahan Redraw Artifacts (Anti-White Flash)
- Animasi HANYA boleh menyentuh properti GPU: `transform` (`scale`, `translate3d`) dan `opacity`.
- Dilarang keras menganimasikan `width`, `height`, `padding`, `margin`, atau `top/left` mentah karena memicu *layout reflow/jank*.
- **Pencegahan Berkedip Putih (Anti-White Flash / FOUC pada Dark Mode)**:
  - Jangan gunakan navigasi anchor murni (`<a href="?param=...">`) untuk tombol filter timeline atau tab interaktif pada tema gelap, karena browser me-reload dokumen dan mengekspos kanvas putih bawaan OS sepersekian detik.
  - Wajib gunakan `<button type="button">` dengan transisi **SPA Seamless Swap**: redupkan kontainer lama via GSAP (`opacity: 0.25, duration: 0.14s`), fetch HTML di background, tukar elemen DOM target via `DOMParser`, sinkronkan URL via `history.pushState`, lalu animasikan elemen baru kembali dengan siklus Enter (280ms `power3.out`).
  - Selalu kunci level root dokumen dengan `<meta name="color-scheme" content="dark">` dan CSS `html, body { background-color: #HEX_DARK !important; color-scheme: dark; }` agar kanvas putih sistem operasi tidak pernah bocor.
- **Reverse Proxy Query String Preservation**: Saat mengarahkan antarmuka melalui reverse proxy (seperti `createProxyMiddleware`), pastikan fungsi rewrite meneruskan query string URL secara penuh (`req.url.slice(req.url.indexOf('?'))`). Menghapus query string menyebabkan filter state tampak tidak responsif (*stale/frozen*).

## 6. Strict Responsive Viewport Isolation (Anti-Duplicate DOM & Mobile Ergonomics)
- **Pencegahan Elemen Dobel**: Saat mengonversi tabel desktop lebar menjadi Card View khusus mobile, jangan biarkan media query longgar merender kedua kontainer sekaligus.
  - Terapkan isolasi biner absolut:
    ```css
    .desktop-only { display: block !important; }
    .mobile-only { display: none !important; }
    @media (max-width: 768px) {
      .desktop-only { display: none !important; }
      .mobile-only { display: flex !important; }
    }
    ```
- **Mobile Card View Pattern untuk Data Tabel**: Tabel multidimensi yang melebihi lebar layar HP wajib diubah menjadi Card View vertikal mandiri. Setiap kartu memuat: Header (Judul + Skor kontras), Metadata Monospace (ID + Kategori), Full-width Progress Bar, dan Footer (Bukti log + Status Badge terbingkai).
- **SVG Axis & Radar Chart Bounds**: Saat merender grafik SVG melingkar/radar di layar sentuh, perlebar bantalan tepi teks (`r_max = ukuran / 2 - 80`) agar label sumbu di tepi kiri/kanan tidak terpotong tepi layar atau kontainer (*clipping prevention*).

## 7. Integrasi Routing & Validasi Biner Mandiri
- **Fast Router Lookup:** Sebelum memulai pengerjaan animasi, jalankan `python3 /home/ubuntu/.hermes/scripts/motion_router.py "<intent>"` untuk menarik pasangan tool yang tepat (GSAP, Progressive Blur, Earshot) dan mengeliminasi 85% token redundan.
- **Audit Gerbang Biner:** Sebelum melaporkan selesai atau menyerahkan kode, jalankan verifikasi biner:
  `python3 /home/ubuntu/.hermes/scripts/ui_quality_gatekeeper.py <path_berkas_atau_folder>`
  Dilarang mengklaim fitur selesai jika validator biner belum mengembalikan status PASS (Exit 0).
- **Dekoding Granularitas Mas Bagas:** Periksa instruksi pengguna via `python3 /home/ubuntu/.hermes/scripts/granularity_calibrator.py "<pesan>"`.
  - Jika Level 1 (perintah singkat): eksekusi instan tanpa banyak tanya wacana.
  - Jika Level 3 (teguran/nilai 0/batasan mutlak): isolasi akar masalah, akui kesalahan tanpa membela diri, dan pasang pagar biner detik itu juga.

## 7.1. Pitfall Runtime: Pan/Zoom Canvas Interaktif & Pointer Capture
- **try/catch pada `setPointerCapture`:** Saat membuat kanvas spasial interaktif dengan Pointer Events (`pointerdown`, `pointermove`, `pointerup`), panggil `element.setPointerCapture(e.pointerId)` selalu di dalam blok `try/catch`. Event sintetis atau pointer yang terlepas sebelum event diproses akan melempar `NotFoundError: Failed to execute 'setPointerCapture'` dan menghentikan seluruh eksekusi handler drag jika tidak ditangkap.
- **Dual-Loop Render Fallback (rAF + Timeout):** Browser otomatis menunda callback `requestAnimationFrame` saat tab berada di background (`document.hidden = true`) atau saat uji headless CDP dijalankan tanpa jendela aktif. Saat membuat scheduler render kanvas berbasis rAF (`swarmScheduleRender`), pasang timer cadangan pendek (100–120ms). Jika rAF tidak kunjung dieksekusi, timer cadangan akan memicu render langsung ke DOM sehingga state koordinat tidak tertahan (*frozen*).
- **DOM Insertion via textContent over innerHTML:** Saat merender node kartu dari payload eksternal atau database (seperti goal/branch tugas agen), bangun elemen menggunakan `document.createElement` dan tetapkan teks via `.textContent` bukan template literal `.innerHTML`. Ini menutup celah XSS dan mencegah karakter khusus merusak pohon DOM kanvas.

## 8. Two-Layer Silhouette Liquid Gooey Architecture (Jakub Antalík)
Untuk menerapkan efek cairan (*liquid / gooey / jelly morphing*) tanpa merusak ketajaman font dan bayangan:
- **Masalah Klasik Filter Gooey:** Mengaplikasikan `filter: blur() contrast()` langsung pada elemen HTML merusak teks menjadi buram/kabur (*fuzzy/soft*), menelan bayangan `box-shadow`, dan memicu bug render di Safari/WebKit.
- **Arsitektur Dua Lapis Bersih:**
  1. **Layer 1 (Silhouette Layer di Belakang):** Kontainer SVG/div terisolasi yang membawa siluet cairan (*droplets/blobs*), filter `<feGaussianBlur>` + `<feColorMatrix>`, dan bayangan fisik gabungan (*merged shadow*).
  2. **Layer 2 (Content Layer di Atas):** Elemen DOM nyata (teks, ikon SVG murni, tombol, hit target) dengan latar belakang transparan. 100% *pixel-crisp* tanpa terkena efek blur filter.
- **Empat Pola Gerak Cairan:**
  - *Morph:* Dua massa cairan mendekat, membentuk jembatan leher (*necking bridge*), dan melebur menjadi satu sasis kapsul elastis.
  - *Move:* Elemen yang digeser meninggalkan ekor cairan karet (*droplet tail*) yang membal kembali.
  - *Melt:* Dua gambar bersentuhan meleburkan tepiannya via displacement gelombang turbulensi (*two-liquid marbling*).
  - *Bend:* Badan kartu melengkung dinamis mengikuti kecepatan inersia pergerakan (*velocity arc*).

## 9. Jebakan Kritis State Awal Antarmuka (Initial View Visibility Trap)
- Saat mengelola transisi tampilan SPA dengan CSS:
  ```css
  .view-section {
    display: none;
    opacity: 0;
    transform: translateY(12px);
  }
  .view-section.active {
    display: block;
    opacity: 1 !important;
    transform: translateY(0) !important;
  }
  ```
- **Jebakan Fatal:** Menyatakan `display: block;` saja tanpa menyatakan ulang `opacity: 1` dan `transform: translateY(0)` akan menyebabkan halaman awal ter-render transparan/kosong melompong (`opacity: 0`) hingga event pergantian view dipicu secara manual. Pastikan state aktif selalu mengesampingkan nilai opasitas awal.

## 10. Tiga Pola Morphing Kasta Atas 60 FPS (Çağatay Han Kurt Paradigm)
Berdasarkan kurasi reel Threads Mas Bagas, tiga pola morphing berikut wajib dikuasai untuk antarmuka upnormal:
1. **Contextual Action Toolbar Morph (OMUZ Pattern):**
   Tombol aksi utama meregang dan membelah secara elastis di tempat (*in-place expansion*) menjadi kartu popover pilihan terkontekstual menggunakan GSAP spring `back.out(1.8)`. Teks dan ikon anak muncul bertahap (*staggered fade-in*) tanpa dialog modal terpisah.
2. **Row-to-Card Accordion Morph (KEOM DeFi Pattern):**
   Baris tabel datar bermetamorfosis menjadi modul kartu transaksi lengkap dengan input saldo dan sakelar agunan (*collateral*). Baris-baris tetangga di bawahnya terdorong ke bawah secara fluida (`ease: "power3.inOut"`) via GSAP Flip tanpa loncatan layout mendadak (*zero layout shift*).
3. **3D Tilt Parallax & Perspective Card Expansion (Gigcep Pattern):**
   Kartu modular merespons koordinat kursor mouse dengan kemiringan 3D halus (`transform: perspective(1000px) rotateX(...) rotateY(...) scale3d(1.02, 1.02, 1.02)`), dengan kartu utama (*featured card*) berdenyut tenang di lapisan Z terdepan.
4. **Sintesis Audio Taktil Tanpa Aset Eksternal (Web Audio API Click):**
   Setiap interaksi morphing diiringi efek klik mikro taktil menggunakan generator frekuensi audio browser:
   ```javascript
   function playTactileClick(freq = 600, duration = 0.04) {
     const ctx = new (window.AudioContext || window.webkitAudioContext)();
     const osc = ctx.createOscillator(), gain = ctx.createGain();
     osc.type = 'sine';
     osc.frequency.setValueAtTime(freq, ctx.currentTime);
     osc.frequency.exponentialRampToValueAtTime(120, ctx.currentTime + duration);
     gain.gain.setValueAtTime(0.12, ctx.currentTime);
     gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
     osc.connect(gain); gain.connect(ctx.destination);
     osc.start(); osc.stop(ctx.currentTime + duration);
   }
   ```

