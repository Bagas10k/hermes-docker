# Doktrin Anti-AI-Slop Endorsement, Kanvas Asli, dan Katalog Portofolio

**Arsitektur & Standar**: Bagas Cihuy (Bagas Saputra)  
**Tujuan**: Menghilangkan kebiasaan generik AI template, menjaga estetika berkelas dunia (Swiss Editorial & High-Credibility Institutional Ledger), dan memastikan akumulasi karya web terpusat.

---

## 1. Standar Anti-AI-Slop Social Proof & Endorsements (Anti-Rainbow Pills)
- **Gejala Slop yang Ditolak**:
  - Penggunaan lencana kapsul (*pill badges*) berwarna-warni pastel acak (peach, lilac, mint, sky blue) yang memuat lingkaran inisial nama generik (`SB`, `ER`, `MB`, `BS`).
  - Nama-nama pemodal ventura atau klien hanya ditulis dalam teks kapital polos biasa tanpa lambang resmi.
  - Memberi kesan murahan, kaku, dan seperti template UI kit generik Tailwind/Figma yang tidak memiliki bobot kredibilitas.
- **Standar Solusi (Swiss Editorial Endorsement Cards)**:
  - **Palet Warna Alabaster & Monokrom**: Gunakan kartu berlatar putih bersih atau warm alabaster (`#FFFFFF` / `#FAF8F4`) dengan garis tepi *hairline* 1px tipis (`#EAE3D5` atau `rgba(0,0,0,0.08)`).
  - **Logo Vektor Geometris Orisinal**: Setiap nama institusi atau modal ventura wajib dihadirkan dalam bentuk logo vektor SVG monokromatik terstruktur dengan opasitas netral teredam (`#45423C` opacity ~0.75-0.8), bukan teks sans-serif kapital mentah.
  - **Kutipan Nyata & Berbobot (*Substantive Backing Quotes*)**: Alih-alih hanya mencantumkan nama dan jabatan, sertakan tanda kutip editorial (`“`) dan pernyataan otentik (*Why they backed* / apa peran strategis mereka) yang menjelaskan mengapa platform ini penting.
  - **Hierarki Metadata Terstruktur**: Di bawah kutipan, sertakan nama dalam bobot tebal (*bold/semibold*), afiliasi/posisi terkemuka, dan lencana verifikasi netral.

---

## 2. Larangan "Floating Mock-Up Frame Trap" pada Landing Page Asli
- **Gejala Slop yang Ditolak**:
  - Membungkus seluruh halaman landing page ke dalam kontainer sempit melayang (*floating paper card*) dengan margin luar berwarna tebal (misal: ungu/lavender di sekelilingnya) saat diminta membuat website asli.
  - Halaman terlihat seperti mockup presentasi Dribbble atau screenshot media cetak, bukan website produksi fungsional yang hidup di peramban.
- **Standar Solusi (Natural Full-Width Canvas)**:
  - Seluruh kanvas browser (`body`, `html`) wajib menjadi latar belakang utama halaman secara penuh (*full-width edge-to-edge*).
  - Konten utama dikelompokkan dalam container grid terpusat yang responsif (`max-width: 1240px; margin: 0 auto; padding: 0 32px;`).
  - Header dan footer mengalir natural dari ujung ke ujung tanpa terkurung di dalam kartu mengambang artifisial.

---

## 3. Doktrin Katalog Master Portofolio Terpadu
- **Tujuan**: Memastikan setiap karya desain web dan eksperimen antarmuka yang selesai dibangun langsung ditabungkan ke dalam satu wadah portofolio resmi milik Mas Bagas (`/home/ubuntu/katalog-portofolio-web`).
- **Aturan Integrasi Setiap Karya Baru**:
  1. *Visual Preview Card*: Buat representasi vektor SVG orisinal di `src/Art.jsx` yang mencerminkan anatomi unik proyek (bukan placeholder kosong).
  2. *Metadata Komprehensif*: Cantumkan nama, tahun (2026), status live, ringkasan arsitektur, 4-5 poin keunggulan rekayasa, palet warna *swatches* hex, dan tags teknologi.
  3. *Tampilan Ganda*: Pastikan karya muncul rapi pada mode *Grid View* maupun *Ledger/Table View*.
  4. *Modal Bedah Kasus*: Modal dialog interaktif harus memuat rincian studi kasus, tantangan desain, dan tombol *Buka Live* yang mengarah langsung ke URL aktif (HTTP 200).
  5. *Integritas Uji*: Setiap penambahan proyek wajib melalui uji otomatis Playwright (viewport 390px, 768px, 1440px, 0 overflow horizontal, Zero Emoji, dan 0 pelanggaran Axe Core).
  6. *Vite Subpath Relative Base (`base: './'`)*: Selalu pastikan `vite.config.js` menyertakan `base: './'`. Jika dibiarkan default `/`, aset JS/CSS akan dimuat dari root host (`/assets/...`) alih-alih subpath (`/portofolio/assets/...`), memicu layar putih kosong (*blank screen*) dan galat MIME type stylesheet pada server reverse proxy.
  7. *Metrik Statistik Dinamis*: Indikator kuantitas proyek pada header dan *stats-strip* wajib terikat secara reaktif ke `{PROJECTS.length}`, bukan teks angka statis manual, agar total proyek selalu sinkron seketika saat karya baru didaftarkan.
  8. *Disambiguasi Kueri Pencarian E2E*: Saat menambahkan proyek baru dengan substring judul yang mirip dengan entri lama (misal: "Neraca Akuntansi Frame 023" vs "NERACA OS"), gunakan kueri penelusuran frase spesifik pada Playwright test suite agar ekspektasi jumlah kartu hasil pencarian tidak ambigu.
  9. *Penyelarasan Desain Default DESIGN.md (Motion Bento Frame 023)*:
     - Terapkan kanvas *Warm Paper / Editorial Cream* (`#EFECE6`), tipografi *Triple-Voice Pairing* (Outfit 900 untuk Display/H1, JetBrains Mono untuk metadata/timecode/status, Playfair Display italic untuk kutipan editorial), dan elemen *Viewfinder HUD Framing* (tanda siku potong sudut `┌ ┐ └ ┘`, timecode pill `TC 00:00:11:14`, dan skala penggaris terkalibrasi).
  10. *Kepatuhan Kontras Aksesibilitas WCAG AA pada Aksen Terang*:
     - Warna ber-luminansi tinggi seperti Tangerine Orange (`#FF5C00`) atau Neon Chartreuse (`#84CC16`) jika diberi teks putih (`#FFFFFF`) menghasilkan rasio kontras < 3.5:1 (gagal WCAG AA 4.5:1). Wajib menggunakan teks gelap Carbon Obsidian (`#111318`), yang menghasilkan rasio kontras 5.2:1 (lulus uji ketat WCAG AA).
  11. *Batas Waktu Pengujian Playwright E2E pada Katalog Visual*:
     - Ketika katalog memuat 20+ kartu bento dengan vektor SVG dan pengujian menangkap tangkapan layar penuh (`fullPage: true`) di 3 resolusi (390px, 768px, 1440px) beserta audit Axe-Core, tingkatkan timeout di `playwright.config.js` menjadi minimal 60 detik (`timeout: 60000`) agar tidak memicu timeout prematur pada lingkungan headless CPU-constrained.

---

## 4. Doktrin Halaman Login Mandiri: Layak Publik & Nol Istilah Developer (Zero Debug Labels)
- **Gejala Slop & Prototype Leak yang Ditolak Keras**:
  - Menyertakan teks developer/debugging seperti "no validasi", "bypass validasi", "demo mode", atau tombol pintas pengujian di antarmuka publik. Hal ini merusak kredibilitas profesional dan membuat aplikasi tampak seperti prototipe mentah.
  - Menempelkan nama pengguna bawaan (*pre-populated username*) atau kartu pratinjau identitas pengguna yang berantakan di dalam form login.
  - Memaksa tampilan login menjadi sekadar tab/menu kecil di bilah sisi dasbor alih-alih halaman mandiri terpisah.
- **Standar Solusi (Clean Centered Card & Silent Friction-Free Gateway)**:
  - **Tampilan Kartu Terpusat Elegan**: Gunakan satu kartu masuk minimalis berlatar netral dengan branding resmi, input kosong bersih disertai *placeholder* informatif, tombol intip kata sandi (SVG), dan tombol aksi utama bersih (**Masuk ke Sistem** / **Masuk Terminal**).
  - **Alur Masuk Cepat di Balik Layar (*Silent Friction-Free Gateway*)**: Jika pengujian atau demonstrasi klien memerlukan akses instan tanpa blokir formulir, jalankan alur tersebut secara senyap di background / *localStorage*, TANPA pernah membocorkan istilah "tanpa validasi" pada antarmuka pengguna.
  - **Auto-Redirect Gerbang Root (`/app/` -> `/app/login.html`)**: Ketika aplikasi memiliki halaman login mandiri, mengakses URL root wajib langsung dialihkan (HTTP 302/303) ke gerbang login, bukan menampilkan dasbor terbuka tanpa autentikasi atau memaksa pengguna mencari link login manual.

---

## 5. Arsitektur Gateway Reverse Proxy & Dual Audio Web Application
- **Whitelisting Privacy Boundary Perimeter**:
  - Pada arsitektur dengan penjaga privasi sentral (`privacy-boundary.js`), perintah `app.use('/rute', express.static(...))` di `server.js` akan tetap memblokir pengunjung publik dengan `401 Unauthorized` jika rute tersebut belum didaftarkan pada ekspresi reguler `isPublic()`. Selalu tambahkan `|| /^\/rute(?:\/.*)?$/.test(p)` pada perimeter sebelum verifikasi curl publik.
- **Dual Audio Architecture (Authentic WAV + Procedural Web Audio Synthesizer Fallback)**:
  - Untuk web interaktif yang memerlukan efek suara taktil (seperti maskot desktop, game, atau audio HUD): sediakan berkas statis WAV orisinil untuk keaslian tekstur suara, dipadukan dengan fallback seketika ke *Web Audio API procedural oscillator/synthesizer*. Hal ini menjamin efek suara tetap berbunyi seketika tanpa jeda *buffer* atau kegagalan decodifikasi audio.
- **Responsivitas Layar Sentuh & Canvas 60 FPS pada Viewport Mobile**:
  - Simulasi canvas spasial desktop (misal: MacBook screen / notch) wajib menghitung rasio skala dinamis `scale = clientWidth / baseWidth` dan memetakan *pointer events* serta *touch events* (`touchstart`, `touchmove`, `touchend`) ke koordinat kanvas virtual (`toScreen(cx, cy)`), memastikan interaksi tetap responsif tanpa distorsi pada layar smartphone (390px).

---

## 6. Doktrin Pendamping AI Layar (Notch HUD) & Keselarasan 1 Tema Terpadu (Unified Design System)
- **Gejala Slop & Toy Companion yang Ditolak Keras**:
  - Membuat pendamping/maskot AI hanya sebagai animasi visual terisolasi (*mock tour/toy simulator*) yang terputus dari ekosistem server backend asli.
  - Tidak memetakan identitas bot nyata, tidak menampilkan pemantauan layanan produksi, atau menggunakan tema warna acak yang bertabrakan dengan sistem yang telah dilatih.
- **Standar Solusi (Native Embedded Companion HUD & Unified System)**:
  - **Penanaman Fungsional Nyata (*Native Real-Time Integration*)**:
    - Sambungkan pendamping AI ke telemetri backend: sediakan endpoint REST API status (`/api/status`), SSE live stream (`/api/live-stream`), dan action gate (`/api/action`).
    - Reaksi Emosi Karakter Berbasis Beban Komputasi Nyata: Maskot secara otomatis bertransisi status (Idle saat CPU <20%, Thinking saat CPU 20-40%, Working dengan pendaran amber glow saat CPU >40% atau ada eksekusi perintah terminal aktif, serta Alert jika ada layanan PM2 yang restart/error).
    - Pemetaan Ekosistem Bot & Subagent Transparan: Tampilkan identitas nyata bot (Hermes Cognitive Engine :8080, Worker Daemon / Bot 2 Bekagent @Bekbekk_bot untuk tugas bising & Obsidian /buku, SputarAI 4-slide carousel, SputarBall radar portal :3085) serta 5 pilar Subagent Squad (Frontend, Backend, Database, Radar, Obsidian) lengkap dengan aturan batas keselamatannya.
    - Uji Interaksi Nyata: Sediakan tombol pengujian yang memicu sinyal nyata (seperti uji ping bot dan health check server) langsung ke backend.
  - **Keselarasan 1 Tema Terpadu (Bagas Unified Aesthetics 98/100)**:
    - *Kelengkungan Kontur G2 Continuous Squircle*: Terapkan radius superelips Apple (G2 continuous corner smoothing) pada seluruh modul kartu, pulau notch, tombol pill, hingga dialog popup tanpa sudut patah kaku.
    - *Palet Warna Warm Paper & Obsidian + Incandescent Solar Flare*:
      - Kanvas dasar: Deep Obsidian pekat (`#080A0E` dan `#0D1117`) dengan tekstur mikro dot-grid dan pendar foton halus.
      - Permukaan kartu: Dark Soft Slate (`#161B22` dan `#1F2937`) dipadukan dengan kaca buram (*backdrop-filter: blur(20px)*) dan garis tepi hairline halus (1px `rgba(255,255,255,0.06)`).
      - Pendar aksen primer: Incandescent Solar Flare Amber Glow (`#F59E0B`, `#FF8500`, `#FFD480`) untuk kontras hangat yang bernas.
      - Pendar aksen status terukur: Hijau zamrud (`#10B981`) untuk online/sehat, biru elektrik (`#3B9EFF`) untuk Hermes/AI, ungu (`#8B5CF6`) untuk SputarAI, dan rose (`#F43F5E`) untuk peringatan galat.
    - *Animasi Morphing Halus (*Fluid Kinematics & Spring Physics*)**:
      - Transisi Dynamic Island notch berpindah mode (*compact*, *peek*, *expanded*) menggunakan kurva pegas mulus `cubic-bezier(0.16, 1, 0.3, 1)`.
      - Kanvas 60 FPS spring physics: pelacakan tatapan mata 3D sferikal dinamis, kompresi elastis saat diklik (*squash & stretch* dengan lerp damping `sx += (1 - sx) * 0.18`), siklus kedipan organik, dan animasi pusing (*dizzy mode*) saat diketuk berturut-turut.
    - *Kepatuhan Mutlak Zero-Emoji*: 100% menggunakan vektor SVG murni (Lucide icons), bebas dari karakter emoji Unicode pada antarmuka pengguna.

---

## 7. Doktrin Zen Single-Page Zero-Scroll & Living Hero Object pada Mobile HUD
- **Gejala Slop & Layout Trap yang Ditolak Keras**:
  - Mengabaikan instruksi "page 1 ngga bisa skrol / home kosongan" dengan tetap memaksakan tata letak vertikal panjang (*multi-screen vertical scroll*) berisi tabel telemetri, daftar proses, dan teks bertele-tele di layar ponsel.
  - Membiarkan area kanvas tengah kosong melompong (*blank void*) sementara karakter maskot/pendamping hanya muncul sebagai avatar mini 48px di header, padahal pengguna meminta maskot tersebut sebagai objek utama aplikasi.
- **Standar Solusi (Zen Zero-Scroll Single-Viewport & Living Hero Object)**:
  1. *Penguncian Viewport Tunggal 100dvh (*Zero-Scroll Guarantee*)**:
     - Kunci seluruh tata letak dalam satu layar ponsel tanpa *scrollbar*: `height: 100dvh; min-height: 100dvh; max-height: 100dvh; overflow: hidden !important; position: fixed; inset: 0; touch-action: none;`.
     - Tiga zona proporsional: **Header (Dynamic Island Besar)** di atas, **Kanvas Interaktif Kosongan (Zen Space)** fleksibel di tengah (`flex: 1`), dan **Dermaga Agen (Bottom Dock)** di bawah dengan batas aman (*safe area*).
  2. *Living Hero Object di Pusat Layar*:
     - Karakter pendamping utama (misal: Big Coucou/Mochi) wajib hadir besar di pusat kanvas (`180x180 px` / skala proporsional), bukan sekadar ikon mini di header.
     - Mesin kanvas 60 FPS spring physics: mata sferikal 3D melacak sentuhan jari secara dinamis di seluruh layar, respon kompresi lentur saat diketuk (*squash & stretch*), kedipan mata organik, dan mode pusing (*dizzy*) saat diketuk beruntun.
  3. *Pola "Agent Lain Itu Coucou Juga" (Multi-Agent Avatar Dock)*:
     - Jangan menampilkan daftar teks kaku; hadirkan setiap agen otonom sebagai karakter avatar unik di dermaga bawah (*dock*):
       - Coucou Hermes (Aura Solar Amber `#F59E0B`, *Cognitive Engine*)
       - Coucou Bekagent (Aura Cyan `#38BDF8`, *Obsidian Vault Clerk*)
       - Coucou SputarAI (Aura Cosmic Violet `#A855F7`, *Media Radar*)
       - Coucou SputarBall (Aura Emerald `#10B981`, *Sports Radar*)
     - Mengetuk avatar agen pada dermaga seketika memicu mutasi pegas (*spring morphing*), lerp warna tubuh/aura, dan bunyi efek audio khas agen tersebut pada Big Coucou di tengah kanvas.
  4. *Pitfall Penanganan Event Bubbling pada Tombol Toggle Bersarang*:
     - Jika tombol ciutkan/perluas (misal: chevron `#btnToggleIsland`) berada di dalam kontainer yang juga memiliki event listener klik (`#dynamicIsland`), klik pada tombol dalam akan memicu kedua penangan secara beruntun (*bubbling*). Saat menutup, tombol dalam mengubah `isExpanded = false`, lalu event merembet ke kontainer luar yang melihat `!isExpanded` bernilai `true` dan langsung membuka kembali kontainer tersebut.
     - *Aturan Wajib*: Selalu sertakan `e.stopPropagation()` pada penangan tombol toggle bersarang agar siklus buka-tutup tidak terpicu ganda.


