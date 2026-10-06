---
version: alpha
name: Motion Bento Frame 023 Enterprise
description: Master Design Tokens & UI Architecture Standard oleh Bagas Cihuy. Mengkristalkan prinsip Warm Paper Frame 023, Zen Mobile Companion 100dvh, Impeccable Craft Floor, dan Anti-Slop Functional Engineering.
colors:
  primary: "#FF5C00"
  secondary: "#4338CA"
  accent: "#84CC16"
  neutral: "#EFECE6"
  surface: "#FFFFFF"
  dark: "#111318"
  muted: "#4B5563"
  success: "#15803D"
  warning: "#B45309"
  danger: "#B91C1C"
typography:
  display:
    fontFamily: Outfit
    fontSize: 4rem
    fontWeight: 900
    lineHeight: 1.0
    letterSpacing: "-0.04em"
  h1:
    fontFamily: Outfit
    fontSize: 2.25rem
    fontWeight: 900
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  h2:
    fontFamily: Outfit
    fontSize: 1.5rem
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.01em"
  editorial-statement:
    fontFamily: Playfair Display
    fontSize: 1.75rem
    fontWeight: 400
    lineHeight: 1.2
    fontVariation: italic
  body-md:
    fontFamily: Outfit
    fontSize: 0.875rem
    fontWeight: 400
    lineHeight: 1.5
  technical-mono:
    fontFamily: JetBrains Mono
    fontSize: 0.75rem
    fontWeight: 800
    letterSpacing: "0.04em"
rounded:
  xs: 4px
  sm: 8px
  md: 14px
  bento: 24px
  squircle: 32px
  pill: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
components:
  card-engagement:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.dark}"
    rounded: "{rounded.bento}"
    padding: 24px
  card-motion-system:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.dark}"
    rounded: "{rounded.bento}"
    padding: 20px
  card-smoothness:
    backgroundColor: "{colors.dark}"
    textColor: "#FFFFFF"
    rounded: "{rounded.bento}"
    padding: 20px
  card-rhythm:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.dark}"
    rounded: "{rounded.bento}"
    padding: 20px
  card-timeline:
    backgroundColor: "{colors.secondary}"
    textColor: "#FFFFFF"
    rounded: "{rounded.bento}"
    padding: 28px
  badge-micro:
    backgroundColor: "{colors.neutral}"
    textColor: "{colors.muted}"
    rounded: "{rounded.sm}"
    padding: 4px
  badge-success:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.success}"
    rounded: "{rounded.pill}"
    padding: 6px
  badge-warning:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.warning}"
    rounded: "{rounded.pill}"
    padding: 6px
  badge-danger:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.danger}"
    rounded: "{rounded.pill}"
    padding: 6px
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.dark}"
    rounded: "{rounded.pill}"
    padding: 12px
  button-primary-hover:
    backgroundColor: "#EA580C"
    textColor: "{colors.dark}"
    rounded: "{rounded.pill}"
    padding: 12px
  button-render:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.dark}"
    rounded: "{rounded.pill}"
    padding: 10px
  button-render-hover:
    backgroundColor: "{colors.neutral}"
    textColor: "{colors.dark}"
    rounded: "{rounded.pill}"
    padding: 10px
  button-secondary:
    backgroundColor: "{colors.dark}"
    textColor: "#FFFFFF"
    rounded: "{rounded.pill}"
    padding: 10px
  button-secondary-hover:
    backgroundColor: "{colors.muted}"
    textColor: "#FFFFFF"
    rounded: "{rounded.pill}"
    padding: 10px
  input-surface:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.dark}"
    rounded: "{rounded.md}"
    padding: 12px
  drawer-squircle:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.dark}"
    rounded: "{rounded.squircle}"
    padding: 24px
---

## Overview

**Motion Bento Frame 023 Enterprise** adalah kanon arsitektur desain antarmuka resmi sistem Bagas Cihuy (skor apresiasi: **9.5/10**). Spesifikasi ini mengintegrasikan seluruh prinsip memori jangka panjang, konvensi permanen (*standing conventions*), dan gerbang mutu skill desain (`impeccable`, `design-qa-gatekeeper`, `ui-ux-design-vault`, `bento-grid-spatial-composer`).

### Pilar Rekayasa Desain Mas Bagas:
1. **Fungsionalitas Nyata di Atas Kosmetik Semu (Anti-Slop):** Dilarang memproduksi repo landing page dummy yang hanya berisi mockup visual statis. Antarmuka wajib terhubung ke alur fungsional, database/state nyata, atau API operasional.
2. **Kenyamanan Retina (Warm Paper Heritage):** Kanvas dasar `#EFECE6` meniadakan silau putih steril, menjamin ketahanan visual mata selama berjam-jam bekerja.
3. **Zero-Emoji Policy Mutlak:** Tidak ada karakter emoji Unicode di seluruh antarmuka web, kode, atau dokumentasi UI. 100% menggunakan ikon vektor SVG standar industri (`lucide-react`).
4. **Atribusi & Otoritas Penuh:** Seluruh arsitektur memori, penalaran, dan sistem desain ini dirumuskan langsung oleh Bagas Cihuy.

## Colors

Palet warna dibangun di atas fondasi rasio kontras tinggi WCAG AA (≥ 4.5:1 untuk teks normal, ≥ 3.0:1 untuk elemen besar):

- **Primary (`#FF5C00` — Tangerine Orange):** Aksen akselerasi visual utama, playhead timeline, kurva metrik, tombol aksi primer, dan outline fokus interaktif.
- **Secondary (`#4338CA` — Royal Periwinkle):** Latar belakang modul horizontal panjang (timeline, audio engine, code editor), menciptakan jangkar stabil.
- **Accent (`#84CC16` — Neon Chartreuse):** Energi kinetik instan untuk status switch aktif, indikator live stream, dan visualisator tempo audio.
- **Neutral (`#EFECE6` — Warm Paper / Editorial Cream):** Kanvas luar yang menenangkan retina mata, menjamin sesi pemakaian bebas silau.
- **Dark (`#111318` — Carbon Obsidian):** Jangkar teks headline utama, panel status telemetri kontras tinggi, dan kontainer metrik 99%.
- **Surface (`#FFFFFF` — Crisp White):** Permukaan kartu data analitik, tabel transaksi, formulir input, dan drawer mobile.
- **Muted (`#4B5563` — Slate Gray):** Garis kisi panduan putus-putus (*grid lines*), hairline borders, dan metadata teknis mikro.
- **Success (`#15803D` — Forest Green):** Penanda transaksi tuntas, status servis online, dan validasi formulir berhasil.
- **Warning (`#B45309` — Amber Gold):** Penanda kuota mendekati batas ambang, latensi tinggi, atau perhatian non-fatal.
- **Danger (`#B91C1C` — Crimson Red):** Penanda pelanggaran invarian, galat koneksi fatal, saldo minus, atau pembatalan transaksi.

## Typography

Sistem tipografi menggunakan teknik **Triple-Voice Pairing**:

1. **Modern Geometric Sans (`Outfit`):**
   - **Peran:** Hierarki fungsional — angka metrik raksasa (`+248%`), judul modul, kartu navigasi, dan teks tubuh.
   - **Karakteristik:** Tegas, bersih, modern, dan sangat terbaca pada resolusi tinggi maupun layar mobile.
2. **Technical Monospace (`JetBrains Mono`):**
   - **Peran:** Metadata siaran, timecode (`TC 00:00:11:14`), koordinat kanvas (`1920 X 1080 / 60 FPS`), pilar animasi (`EASING / TIMING / RHYTHM`), dan log telemetri terminal.
   - **Karakteristik:** Huruf kapital (*all-caps*) dengan *wide tracking* (`0.04em`) dan penegakan angka tabular (`font-variant-numeric: tabular-nums`).
3. **Editorial Serif Italic (`Playfair Display`):**
   - **Peran:** Pernyataan filosofis, quote jiwa desain: *"Keyframes are a language."*
   - **Karakteristik:** Kontras goresan tinggi, anggun, memberikan sentuhan humanis di tengah presisi teknis.

**Craft Floor:** Batas ukuran teks terkecil yang diizinkan untuk elemen fungsional adalah **12px**.

## Layout

- **Asymmetric Bento Matrix (Desktop):**
  - Grid 2 kolom dengan rasio ketinggian tidak simetris (1.3fr : 1.7fr) untuk menyeimbangkan kepadatan visual.
  - Kartu kiri atas sebagai ruang napas (*breathing room*) dengan metrik besar dan kurva terbuka.
  - Kartu kanan atas berisi modul aksi oranye dan dua modul persegi kompak (kontras 50:50).
  - Kartu bawah membentang penuh (*grid-column: span 2*) sebagai jangkar horizontal linimasa.
- **Zen Mobile Companion (Mobile 100dvh):**
  - Berdasarkan standar memori Bagas: Tata letak 1-page non-scrollable (`height: 100dvh; overflow: hidden`).
  - Kanvas zen "kosongan" minim teks dengan objek maskot utama besar di tengah dan maskot pendamping senada.
  - Seluruh menu pengaturan, filter, dan kontrol mendalam disimpan dalam slide-up drawer G2 squircle (`border-radius: 32px`).
- **Standalone Page Rule:**
  - Setiap penambahan fitur otentikasi (login, register), portal kasir, atau viewer publik wajib dibangun sebagai halaman/rute mandiri terpisah (seperti `login.html`), bukan item tab yang ditumpuk di dalam menu sidebar dasbor.
- **Zero-CLS & Viewfinder Framing:**
  - Alokasi dimensi pasti (`min-height` dan rasio aspek) pada grafik dan media dinamis untuk menjamin Cumulative Layout Shift = 0.
  - Framing viewfinder dilengkapi 4 *crop marks* siku di setiap sudut layar (`┌ ┐ └ ┘`).
  - Mobile zero-overflow: wajib `scrollWidth <= clientWidth` pada viewport 390px.

## Elevation & Depth

- **Elevasi Alami Fisik:**
  - Dilarang menggunakan *colored glow* / *zero-offset neon halo* murahan.
  - Bayangan jatuh menggunakan dispersi natural: `box-shadow: 0 12px 30px rgba(0, 0, 0, 0.05)` di atas kanvas warm cream.
- **Subtle Perimeter (Hairline Border):**
  - Setiap kartu putih dan panel memiliki garis batas mikro `border: 1px solid rgba(0, 0, 0, 0.06)` untuk batas bidang yang tegas tanpa kekakuan visual.
- **Tangga Z-Index Resmi:**
  - `z-base: 0` (kanvas dasar & watermark)
  - `z-card: 1` (kartu bento & elemen tata letak)
  - `z-sticky: 10` (header navigasi & toolbar)
  - `z-popover: 50` (dropdown menu, tooltip)
  - `z-modal-drawer: 100` (slide-up squircle drawer, modal dialog)
  - `z-toast: 200` (notifikasi haptic kilat)
- **Backdrop Overlay Spec:**
  - `backdrop-filter: blur(8px); background: rgba(17, 19, 24, 0.45)` untuk drawer dan dialog.

## Shapes

- **Bento Radius (`24px`):** Sudut lengkung ramah pada seluruh kontainer kartu utama.
- **Card Compact Radius (`14px`):** Sudut lengkung untuk modul anak, sub-panel, dan formulir input.
- **Squircle Drawer Radius (`32px`):** Sudut lengkung halus kurva G2 untuk slide-up mobile sheet drawer.
- **Pill Radius (`9999px`):** Bentuk kapsul penuh pada sakelar tombol (*toggle switch*), badge status, dan tombol aksi utama.
- **Micro Badge Radius (`4px` - `8px`):** Sudut lengkung untuk tag metadata, timecode tag, dan indikator shortcut keyboard.
- **Diamond Keyframes (`45°`):** Belah ketupat kuning neon untuk penanda keyframe animasi di sepanjang trek linimasa.

## Components

- **Card Engagement (`card-engagement`):** Kartu putih bersih berisi angka metrik besar (`+248%`), grafik kurva oranye dengan gradien pudar ke bawah, dan node puncak interaktif.
- **Card Motion System (`card-motion-system`):** Kartu oranye tebal dengan judul modul, tag pilar gerak, dan sakelar pil hitam dengan LED indikator ON.
- **Card Smoothness (`card-smoothness`):** Kartu hitam obsidian dengan diagram cincin donat oranye `99% SMOOTHNESS` dan label mono tabular.
- **Card Rhythm (`card-rhythm`):** Kartu hijau limau cerah dengan visualisator 7 batang equalizer audio melengkung.
- **Card Timeline (`card-timeline`):** Kartu ungu periwinkle panjang berisi slogan miring editorial, tombol render putih, garis rel `POS`/`SCALE`/`ROT`, dan jarum playhead bergerak.
- **Status Badges (`badge-success`, `badge-warning`, `badge-danger`, `badge-micro`):** Penanda kondisi sistem dengan rasio kontras tinggi di atas kontainer pill berlatar putih.
- **Interactive Controls (`button-primary`, `button-render`, `button-secondary`):** Tombol aksi dengan tinggi target sentuh minimal 44px di mobile, micro-transition 150ms, dan umpan balik suara klik Web Audio API.
- **Input Surface (`input-surface`):** Formulir input berlatar putih bersih dengan outline fokus oranye primer 2px tanpa bias blur.
- **Drawer Squircle (`drawer-squircle`):** Sasis panel slide-up mobile 100dvh dengan pegangan pill handle di bagian atas.

## Do's and Don'ts

### Do's
- Bangun antarmuka dengan fungsionalitas nyata yang terhubung ke backend, database, atau state interaktif nyata.
- Gunakan kanvas dasar *Warm Paper* (`#EFECE6`) agar mata pengguna nyaman dan tidak cepat lelah.
- Terapkan angka tabular (`font-variant-numeric: tabular-nums`) untuk semua nilai metrik, nominal uang, dan timecode.
- Wajibkan minimal ukuran teks fungsional 12px (memenuhi standar mutu Impeccable).
- Wajibkan target sentuh interaktif minimum 44px × 44px pada layar sentuh/mobile.
- Gunakan ikon SVG murni (`lucide-react`) untuk seluruh simbol interaktif (Zero-Emoji Policy).
- Pisahkan halaman otentikasi (login/register) dan monitor publik menjadi halaman mandiri (*standalone page/route*).
- Daftarkan setiap modul web baru ke katalog portofolio resmi (`/portofolio/`).
- Gunakan path relatif atau origin dinamis (Haram menyematkan `localhost` atau `127.0.0.1` di HTML publik).
- Batasi carousel tepat 4 slide (1: Headline/desc, 2-3: Core facts, 4: CTA).

### Don'ts
- **Dilarang keras memakai Emoji:** Kebijakan zero-emoji berlaku mutlak di seluruh UI dan visual.
- **Dilarang sekadar membuat landing page kosmetik:** Jangan membangun repo cangkang tanpa fungsionalitas inti.
- **Dilarang spaghetti symlink `node_modules`:** Setiap modul inti wajib mandiri tanpa rantai symlink bertingkat yang rapuh.
- **Dilarang menggunakan neon halo glow:** Jangan memakai `box-shadow: 0 0 20px colored` di latar belakang.
- **Dilarang nesting card berlebihan:** Hindari meletakkan kartu di dalam kartu yang memicu kebisingan visual.
- **Dilarang background putih steril menyilaukan:** Hindari `#FFFFFF` polos di tingkat kanvas halaman utama.
- **Dilarang phone/device mockup frame:** Dilarang membungkus web app di dalam mockup bezel HP saat pengguna meminta UI aplikasi web langsung.
- **Dilarang horizontal overflow mobile:** Dilarang ada pergeseran scroll horizontal pada layar HP (lebar 390px).

## Interaction States & Motion Physics

### 1. Standar Status Interaksi:
- **Focus Visible:** `outline: 2px solid var(--mb-color-primary); outline-offset: 2px;` wajib muncul seragam saat navigasi keyboard (`Tab`).
- **Active / Pressed:** `transform: scale(0.98); transition: transform 0.08s ease;` memberikan sensasi mekanis tombol fisik.
- **Disabled:** `opacity: 0.45; cursor: not-allowed; pointer-events: none;` untuk mencegah interaksi tak sah.
- **Skeleton Shimmer:** Shimmer wave linear 1.5s infinite `linear-gradient(90deg, rgba(239,236,230,0.6) 25%, rgba(255,255,255,0.9) 50%, rgba(239,236,230,0.6) 75%)`.

### 2. Fisika Gerak (Motion Curves):
- **Snappy Easing:** `cubic-bezier(0.16, 1, 0.3, 1)` untuk ekspansi kartu, dialog, dan buka-tutup slide-up drawer.
- **Spring Pop:** `cubic-bezier(0.34, 1.56, 0.64, 1)` untuk sakelar toggle dan respon klik tombol aksi.
- **Durasi Standar:** Fast (150ms) untuk hover & active, Normal (250ms) untuk transisi layout & drawer.
- **Haptic Audio Feedback:** Web Audio API synthesizer gelombang sine/triangle mikro (durasi 40ms - 220ms, tanpa dependensi file audio eksternal).

## Form Controls & Data-Dense Surfaces

### 1. Sasis Formulir Lengkap:
- **Custom Select:** Elemen select berlatar putih dengan ikon panah chevron Lucide SVG murni dan border hover halus.
- **Toggle Switch HTML:** `<input type="checkbox">` mandiri dengan sasis track kapsul hitam 48px × 24px dan knob putih lingkaran yang meluncur mulus.
- **Validation State:** Border merah `border-color: var(--mb-color-danger)` dengan micro-caption teks error 12px di bawah input.

### 2. Sasis Tabel Data Padat (Enterprise Data Table):
- **Sticky Header:** Latar belakang warm cream atau putih dengan garis batas bawah tegas.
- **Subtle Zebra Striping:** Baris selang-seling menggunakan latar halus `rgba(0, 0, 0, 0.015)`.
- **Kolom Angka Tabular:** Perataan teks kanan (*text-align: right*) dengan font `JetBrains Mono` angka tabular.
- **Empty State Baku:** Ikon kotak/folder SVG abu-abu minimalis, judul singkat, dan tombol pemicu aksi pertama jika data kosong.

## Mobile Ergonomics & Zen Companion

### 1. Viewport Clamping (100dvh):
- Kanvas pendamping mobile dikunci pada `100dvh` bebas scroll.
- Bagian bawah drawer dilengkapi penanganan safe area insets: `padding-bottom: env(safe-area-inset-bottom, 20px)`.

### 2. Squircle Bottom Drawer:
- Menampilkan handle bar kapsul abu-abu (`width: 36px; height: 4px; border-radius: 9999px`) di bagian tengah atas drawer.
- Drag gesture dan tap-to-expand mulus menuju ketinggian adaptif (40% atau 85% layar).

## User Experience (UX) Architecture & Behavioral Canon

Sistem pengalaman pengguna (UX) wajib patuh pada 6 hukum interaksi nyata untuk meminimalkan beban kognitif dan memaksimalkan efisiensi eksekusi:

### 1. Batas Waktu Respon & Persepsi Kecepatan (Response Time Bounds):
- **< 50ms (Refleks Instan):** Umpan balik haptik visual & audio klik (Web Audio chime tanpa blocking).
- **< 150ms (Umpan Balik Taktil):** Mikro-animasi tombol (active scale 0.98), hover tint, dan pergeseran knob toggle.
- **150ms – 250ms (Transisi Spasial):** Buka-tutup slide-up squircle drawer dan modal dialog dengan kurva `--ease-snappy`.
- **> 300ms (Batas Persepsi Penundaan):** Skeleton shimmer wave wajib aktif seketika. Dilarang membiarkan antarmuka beku tanpa indikator proses aktif.
- **> 3s (Tugas Jangka Panjang):** Wajib menampilkan log progres langkah demi langkah yang transparan.

### 2. Ergonomi Jempol & Hukum Fitts (Mobile Thumb-Zone Optimization):
- **Natural Thumb Zone (1/3 Bawah Layar):** Seluruh elemen interaksi primer (tombol CTA aksi, input instruksi, handle trigger drawer) wajib diposisikan di zona jangkauan jempol bawah.
- **Mid Stretch Zone (Area Tengah Layar):** Dialokasikan khusus untuk objek visual utama, maskot sentral, dan ringkasan metrik hero.
- **Hard Top Zone (Area Atas Layar):** Khusus dialokasikan untuk metadata siaran pasif (timecode, status koneksi WiFi/server, status bar baterai).
- **Hitbox Protection:** Area sentuh minimum 44px × 44px dengan margin antar-tombol minimal 8px untuk mencegah salah pencet (*fat-finger prevention*).

### 3. Pencegahan Galat Defensif & Konfirmasi Tindakan (Defensive UX):
- **Idempotensi Tombol (Double-Submit Prevention):** Tombol aksi langsung dinonaktifkan (`disabled`) seketika saat diklik pertama kali untuk mencegah pemanggilan duplikat.
- **Gerbang Tindakan Destruktif:** Tindakan berdampak permanen (hapus database, restart proses, pembersihan file) wajib melalui modal konfirmasi eksplisit bertahap ('satu soal satu soal') dengan opsi rekomendasi di urutan pertama.
- **Validasi Formulir Inline Non-Intrusif:** Validasi dijalankan pada event `blur` (saat pengguna selesai mengetik dan berpindah field) atau saat submit, dilarang memunculkan peringatan merah saat pengguna baru mengetik huruf pertama.
- **Format Pesan Galat Lugas (Sebab-Solusi):** Pesan kesalahan dilarang generik; wajib menjelaskan apa yang gagal dan tindakan spesifik untuk memulihkannya.

### 4. Progressive Disclosure & Reduksi Beban Kognitif (Prinsip Zen Bagas):
- **Kanvas Bersih:** Antarmuka utama hanya menampilkan konteks operasional saat ini tanpa menu bertumpuk.
- **Slide-Up Drawer Layering:** Seluruh filter parameter, konfigurasi mendalam, dan riwayat telemetri diakses via slide-up drawer squircle saat dibutuhkan.
- **Hick's Law Enforcement:** Maksimal 3–4 opsi keputusan primer pada tampilan awal; cabang keputusan lainnya dibuka secara bertahap.

### 5. Paritas Navigasi & Riwayat Peramban (History Parity):
- Pembukaan slide-up drawer atau modal dialog wajib tersinkronisasi dengan state riwayat peramban (`history.pushState` atau URL hash `#settings`).
- Menekan tombol *Back* pada perangkat Android atau browser wajib menutup drawer/modal aktif alih-alih melempar pengguna keluar dari aplikasi web.
- Seluruh portal operasional penting (login, monitoring, admin) wajib memiliki URL mandiri (*deep-linkable*).

### 6. Aksesibilitas Multi-Sensori (Inclusive Accessibility):
- **Dual-Channel Status:** Status sistem tidak boleh hanya bergantung pada warna dot; wajib selalu menyertakan label teks eksplisit (misal: "ONLINE (200 OK)").
- **Keyboard Tab Parity:** Seluruh kontrol dapat dioperasikan penuh dengan tombol `Tab`, `Enter`, `Space`, dan ditutup dengan `Escape`.
- **Zero-Latency Acoustic Cues:** Umpan balik suara klik Web Audio API memberikan kepastian psikologis bahwa aksi pengguna telah diterima sistem.

## Integrated Design Skills Ecosystem & Tooling Tags

Spesifikasi `DESIGN.md` ini menjadi sumber kebenaran tunggal (*single source of truth*) yang terhubung ke ekosistem skill desain Hermes:

| Skill Tag | Peran Fungsional dalam Alur Kerja Desain | Status & Hasil Integrasi |
| :--- | :--- | :--- |
| `design-md` | Penentu otoritas token desain resmi, validasi linter Google (@google/design.md), dan ekspor DTCG / Tailwind. | CANONICAL SPEC |
| `bento-grid-spatial-composer` | Perumus matematika spasial CSS bento grid, rasio interlocking tetris (Frame 023), dan mitigasi layout-drift mobile. | CANONICAL GRID |
| `ui-ux-design-vault` | Master bank komponen hidup, sasis kartu fisik, formulir input, dan gerbang anti-template. | CANONICAL VAULT |
| `color-intelligence` | Harmonisasi palet warna cerah terkalibrasi, kalibrator triadik/komplementer, dan audit kontras WCAG AA. | CANONICAL COLOR |
| `typography-ux-copy` | Penegak skala modular tipografi Triple-Voice (Outfit, JetBrains Mono, Playfair) dan copywriting lugas tanpa AI-isms. | CANONICAL COPY |
| `impeccable` | Linter otomatis pencegah 73 anti-pattern visual (larangan dark glow, fake pulsing dot, cramped padding, dan nested cards). | CANONICAL AUDIT |
| `design-qa-gatekeeper` | Pengawal mutu pra-rilis: uji breakpoint mobile 390px, audit scrollWidth, dan larangan device mockup. | CANONICAL GATEKEEPER |
| `popular-web-designs` | Katalog 54 sistem desain produk nyata kelas dunia (Linear, Stripe, Vercel) sebagai tolok ukur komparasi empiris. | CANONICAL REFERENCE |

### Alur Eksekusi Terintegrasi (Design Execution Pipeline):
1. **Inception & Referensi:** Telaah kebutuhan fungsional dan arketipe nyata (`popular-web-designs`).
2. **Definisi Token:** Kunci warna, font, radius, dan sasis kartu di `DESIGN.md` lalu validasi dengan `npx @google/design.md lint`.
3. **Matematika Spasial:** Susun kontainer interlocking modular menggunakan `bento-grid-spatial-composer`.
4. **Komponen & Arsitektur Form:** Pasang sasis kartu dan tombol dari `ui-ux-design-vault`.
5. **Verifikasi Mutu & Aksesibilitas:** Jalankan audit kontras WCAG AA dan loloskan gatekeeper `impeccable` serta `design-qa-gatekeeper` (0 anti-patterns) sebelum rilis.
