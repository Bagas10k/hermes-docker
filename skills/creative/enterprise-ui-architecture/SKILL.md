---
name: enterprise-ui-architecture
description: "Use when building contemporary enterprise UI systems."
version: 1.0.0
author: Bagas Cihuy & Hermes
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ui, ux, design-system, data-tables, bento-grid, navigation, vite-mpa, anti-ai-slop, clean-code]
---

# Enterprise UI Architecture & Component Systems

Standar baku rekayasa antarmuka enterprise kelas dunia (Linear, Mercury, Raycast style). Dibangun dengan arsitektur Zero-Runtime-Bloat (Vite MPA, Pure CSS Tokens, Vanilla ESM) di bawah kepemilikan arsitektural **Bagas Cihuy**.

## 1. Standar Mutlak Anti-AI-Slop (Strict Blocker Constraints)
Sebelum mengirimkan hasil rancangan ke pengguna, jalankan inspeksi mandiri via browser headless. Tolak output sendiri jika melanggar poin berikut:
- **DILARANG Menggunakan Emoji untuk Ikon UI:** Wajib menggunakan vektor garis inline SVG presisi (stroke 1.5px/2px, Feather/Lucide style). Emoji berwarna merusak kesan profesionalitas software enterprise.
- **DILARANG Gradasi Teks:** Seluruh judul dan body text wajib solid monokrom murni (putih murni di tema gelap, hitam pekat di tema terang).
- **DILARANG Badge Kicker Dekoratif:** Dilarang meletakkan pil teks kecil pemanis mengambang di atas headline hero.
- **DILARANG Kotak Logo Generik:** Gunakan pure typography wordmark minimalis.
- **DILARANG Bento Simetris Kaku:** Hindari grid kotak 2x2 atau 3x3 seragam yang membosankan. Gunakan bentang kolom asimetris (*interlocking fluid corners*).
- **DILARANG Teks Menabrak Foto/Elemen Lain:** Pisahkan kontainer teks dan visual secara vertikal atau beri padding batas aman tegas.

## 2. Arsitektur Komponen Inti

### A. Tabel Data Densitas Tinggi & Ledger Finansial
- **Tabular Lining Numerals:** Nominal uang, kuota data, dan stempel waktu wajib menggunakan font monospace (`JetBrains Mono`) agar digit angka sejajar lurus secara vertikal.
- **Status Badge Semantik:** Hijau zamrud (`#10b981`) untuk selesai/settled, Amber (`#f59e0b`) untuk kliring, Merah mawar (`#f43f5e`) untuk gagal/ditolak.
- **In-Place Row Expansion (Accordion):** Baris transaksi dapat diklik untuk membuka rincian audit hash dan virtual account tanpa memuat ulang halaman (*zero-page-jump*).

### B. Interlocking Bento & Real Human Media
- **Asymmetric Corner Radius:** Terapkan variasi radius berbeda per sudut kartu (`border-radius: 36px 36px 12px 36px`) agar kartu saling mengunci (*interlocking puzzle*).
- **Real Photography:** Tampilkan foto manusia/kreator nyata beresolusi tinggi dengan pembungkus frame kontras, bukan ilustrasi vektor generik.
- **Connected Pipeline Node Diagram:** Sajikan alur fitur menggunakan node berpenghubung panah kurva SVG nyata (`Auto-Boosting` ➔ `Analitik`), bukan sekadar bullet list teks.

### C. Navigasi Fisik & Kontrol Papan Ketik
- **Linear Left-Rail Collapsible Sidebar:** Transisi 260px (label penuh) ke 64px (ikon rail murni) via shortcut keyboard `[` atau toggle.
- **Raycast Modal Command Palette (`⌘K`):** Jendela pencarian perintah melayang di tengah berlatar blur kaca (`backdrop-filter: blur(12px)`) dengan navigasi panah keyboard.
- **macOS Floating Magnification Dock:** Kapsul melayang di dasar layar dengan pembesaran magnetik dinamis (`scale 1.35x`) dan titik pendar status aktif cyan.
- **Segmented Breadcrumbs & Action Docks:** Jejak hierarki bertingkat dan deretan aksi cepat atas (*topbar actions*) wajib disatukan ke dalam sasis fisik kapsul segmented dengan pembatas garis halus 1px, bukan tombol-tombol individual yang tercecer dan membuat header berantakan.
- **Tipografi Enak Dibaca & Presisi:**
  - Wajib menyertakan link CDN Google Fonts resmi (`Plus Jakarta Sans` / `Inter` dan `JetBrains Mono`) di `<head>` agar tidak bergantung pada fallback font lokal yang berbeda di tiap OS.
  - Terapkan `-webkit-font-smoothing: antialiased`, `-moz-osx-font-smoothing: grayscale`, dan `text-rendering: optimizeLegibility`.
  - Pasang tight tracking: `letter-spacing: -0.011em` (body), `-0.025em` (headings), serta `-0.02em` + `tabular-nums` pada angka monospace.
- **Prinsip Visual-Only Refactoring pada Sistem Berjalan:**
  - Saat diminta mempercantik atau merapikan UI pada sistem/layanan yang sedang aktif berjalan, isolasi perubahan 100% pada lapisan visual (CSS & markup presentasi). Dilarang merombak routing backend, controller, skrip socket, scheduler, atau file runtime data agar fungsionalitas sistem tidak terganggu.
- **Pola Autentikasi & Reset Kredensial via Messaging Gateway:**
  - Untuk alur lupa password / OTP admin pada aplikasi headless/dashboard, sambungkan ke gateway bot WhatsApp/Telegram yang sudah terpasang.
  - Sediakan fallback nomor super admin terkonfigurasi di `config.json` dan tampilkan masked phone number (`6282****4003`) di UI untuk transparansi verifikasi.
- **Kecepatan Tindakan & Anti-Overcautious:**
  - Saat pengguna memberikan instruksi tindakan langsung (refactor, pull, edit aset, update token), prioritaskan eksekusi cepat terarah tanpa ragu atau over-cautious berlebihan yang memperlambat momentum kerja. Verifikasi cukup dilakukan secara ringkas berbasis fakta hasil luaran.

### D. Topologi SaaS Admin Dashboard Modern & "Koper Kerja Digital"
- **Filosofi Sekat Koper:** Jangan anggap UI sebagai "halaman web panjang". Rancang dasbor sebagai kompartemen tertutup yang terpisah (*Bento Grid* modular). Satu sekat untuk AI, satu sekat untuk transaksi, satu sekat untuk server. 
- **Pencegahan Halation Galeri Visual & Tokenisasi Tema Ganda (Dark Slate vs Warm Paper)**:
  - Pada galeri pameran referensi desain, DILARANG menempelkan kartu kertas putih/krem murni (`#FAF7EE`) langsung di atas kanvas gelap pekat; hal ini memicu silau tajam (*halation*), efek kotak catur yang memecah konsentrasi mata, dan merusak keselarasan tema Obsidian.
  - Sasis kartu wajib beradaptasi secara dinamis terhadap mode tema:
    - *Mode Gelap (Warm Obsidian)*: Latar kanvas `#14120E`, sasis kartu menggunakan lempengan arang arsitektural hangat (`#1C1915`) dengan garis tepi hairline (`#2D2822`) dan teks putih gading (`#FAF6EF`).
    - *Mode Terang (Warm Paper)*: Latar kanvas kertas hangat (`#FAF6EF`), sasis kartu menjadi cetak putih gading bersih (`#FFFFFF`) dengan teks tinta arang pekat (`#14120E`).
  - Sediakan sakelar tema (`☀️ / 🌙`) yang tersinkronisasi lintas halaman via `localStorage.theme`.
  - Pemuatan galeri masal (100+ aset) wajib menyediakan mode tampilan ganda: *Grid Taktil* (muat bertahap per 12 kartu dengan animasi *staggered reveal* saat di-scroll) dan *Slide Lembaran (Carousel)* dengan navigasi keyboard (`←`/`→`) serta pita thumbnail interaktif di bagian bawah.
- **Pola Portal Utama & Direktori Workspace Multi-Tier**:
  - Halaman indeks portal utama (`/`) wajib memisahkan katalog modul secara tegas menjadi dua tingkatan hierarkis (*two-tier bento*):
    1. *Tier 1: Perkakas Rekayasa & Sistem (Engineering Workspace)*: Modul kerja internal berdensitas tinggi (*Knowledge Graph, Memory Engine, Desain Library, Telemetri Kernel*).
    2. *Tier 2: Publikasi & Layanan Terbuka (Public Ecosystem & Gateway)*: Modul konten dan akses terbuka (*Warta AI, Buku Catatan, Model Gateway, Riset Teoretis*).
  - Setiap kartu bento wajib memiliki: status mikro badge semantik (`badge-live`), judul langsung tanpa kicker dekoratif, deskripsi padat 2 baris, panel ringkasan teknis bergaris halus 1px (`mono`), dan tombol aksi cepat (*Quick Launch Action*) berpenunjuk panah SVG presisi.
  - Sediakan Command Palette (Omnibar `⌘K`) di header utama yang mengindeks seluruh modul dan rute secara instan dengan navigasi panah keyboard dan shortcut slash `/`.
- **Adaptive Liquid Interface (Tab-Bar Mobile):** Layout Desktop = Dual-sidebar (global + contextual). Layout Mobile = Harus "mencair" menjadi aplikasi dengan Bottom Tab-Bar. Sidebar dibuang, tabel transaksi dipadatkan menjadi *Card View*.
- **Telemetri Pikiran (Skeletal Loading & Status):** Jangan ciptakan "Ilusi Tombol Rusak". Jika AI sedang bekerja (misal via Gateway), pasang *Skeletal Loading* dan teks status progresif ("Membaca sumber... -> Merender slide...") via WebSockets/SSE agar pengguna tidak melakukan double-klik (*spam trigger*).
- **Dual-Sidebar Navigation:** Pisahkan navigasi menjadi dua pilar. Pilar kiri mentok (64px) khusus ikon global (*Home, Analytics, Users, Settings*). Pilar sebelahnya (240px) khusus konteks lokal (*Contextual Menu*) yang berubah sesuai ikon global yang dipilih.
- **Top Bar Omnibar:** Gunakan bilah pencarian universal (*Command Palette / ⌘K*) di atas *header* untuk akses cepat ke ID pesanan atau halaman, tanpa navigasi hierarkis panjang.
- **Metrics Grid Minimalis:** Tampilkan angka analitik (Pendapatan, Tiket Aktif, Kuota Token) di dalam sasis garis Obsidian 1px. DILARANG menggunakan gradasi warna/kotak neon. Gunakan indikator panah naik/turun tipis berwarna hijau zamrud/merah mawar.
- **Drawer Context (Laci Kanan):** Saat admin mengklik baris DataGrid (misal untuk melihat bukti transfer atau detail *chat*), rincian WAJIB meluncur (*slide-out*) sebagai *Drawer* dari sisi kanan layar, BUKAN memindahkan admin ke halaman URL baru (menjaga konteks tabel tetap terlihat).

### E. Infrastruktur Jaringan, Koper Kerja Digital & Akses Cerdas
- **Domain Permanen vs Latihan:** Aplikasi permanen wajib dirutekan via domain stabil (Cloudflare Zero Trust). Tunnel acak (trycloudflare) hanya diaktifkan murni untuk testing/latihan di sandbox sementara, lalu matikan untuk menghemat resource.
- **Topologi Koper Kerja Digital (Super Dashboard):** Rancang dashboard tersentralisasi (Koper Kerja) yang berisi perkakas sistem: Hermes Chat Terminal (port 20128), PM2 Server Manager, Remote File/Code Editor, dan SputarAI/Radar Engine.
  - **Eksklusi Bisnis Front-Facing:** Jangan mencampurkan dashboard bisnis publik (seperti Dasbor Jajan Digital) ke dalam koper ini. Biarkan beroperasi mandiri (standalone) agar traffic pelanggan tidak mengganggu server koper.
  - **Modularitas Extensible (Plug & Play):** Pastikan koper dapat ditambahkan kompartemen (ruang) baru secara dinamis oleh pengguna kapan saja tanpa hardcode yang kaku.
- **Autentikasi Magic Link (Telegram Pager):** Gantikan password konvensional dengan push notifikasi Telegram. Web/Sistem mengirim permintaan ke bot, admin menyetujui lewat klik di Telegram ("Seseorang mencoba masuk dari IP X").
- **Notifikasi Omnichannel:** Tugas asinkron/lama yang dieksekusi di web harus tetap mengirimkan laporan output akhirnya via push notifikasi ke Telegram (layar web mungkin sudah ditinggalkan/dikunci).

### F. Dasbor Telemetri Frekuensi Tinggi & Cyber Cockpit HUD (Pola Fun & Interaktif Bebas Slop)
- **Kompartemen Tab Anti-Clutter:** Saat menyajikan metrik sistem, proses OS, dan status skuad bot/pekerja, hindari menumpuk 10+ kartu secara vertikal. Sediakan segmented tab navigation (`[ Hardware 100ms ]`, `[ Hermes Agent & Bots ]`, `[ PM2 & Proses ]`) agar viewport tetap terkontrol dan lapang.
- **Tachometer Sirkular SVG (Speedometer Dials):** Hindari progress bar flat yang monoton untuk metrik real-time. Gunakan SVG Circular Dial (`stroke-dasharray` & `stroke-dashoffset` dinamis) bergaya speedometer kokpit dengan peralihan warna semantik halus (Cyan ➔ Amber ➔ Rose saat beban tinggi).
- **Maskot Reaktif (Vector SVG HUD):** Hadirkan nuansa menyenangkan (*fun*) melalui maskot resmi berformat vektor SVG (tanpa emoji murahan) yang terhubung ke pembacaan hardware:
  - Maskot menampilkan balon status dinamis (*state-driven commentary*) sesuai ambang CPU/RAM (misal: "adem ayem" saat < 20%, "produktif" saat 20-65%, "TURBO OVERCLOCK" saat > 65%).
  - Tambahkan interaksi mikro: klik pada avatar maskot memicu animasi pantul (*bounce*) dan audio chiptune.
- **Audio Sintesis Nol-Dependensi (Web Audio API):**
  - Dilarang mengunduh berkas audio eksternal (`.mp3`/`.wav`) yang rentan gagal muat, membebani bandwidth, atau memicu latensi.
  - Bangun synthesizer audio mikro menggunakan `window.AudioContext` oscillator native browser (`sine`/`square`/`triangle`) dengan envelope pendek (60-120ms) untuk klik tombol, perubahan tab, dan alert. Sediakan tombol mute (`🔊 / 🔈`) persisten di header.
- **Preset Tema Tri-Mode:** Sediakan tombol beralih tema instan antara *Cyber Arcade* (Dark Neon), *Neo Cockpit* (High-Octane Warm Amber), dan *Warm Obsidian* (Klasik Editorial).

### G. Visual Agent Workflow & Parallel Execution Graphs (Pola Estafet Sektoral)
- **Anti-Linear-Sprawl Doctrine (Bukan Deretan Horizontal Puluhan Kotak):**
  - DILARANG merender alur kerja multi-agent sebagai deretan 30–50 kartu horizontal berurutan yang memanjang berkilo-kilometer (membuat mata lelah dan merusak gambaran hierarki organisasi).
  - Terapkan **Papan Orkestrasi Paralel Sektoral (Hierarchical Parallel Handoff Board)**:
    - *Level Manajemen Atas*: Direktur (GM) & Wakil Direktur (Asisten) memantau keseluruhan siklus dan dekomposisi perintah.
    - *Level Pilar Lapangan*: Tiga pilar utama (Pusat Riset, Komandan Lapangan, Auditor Mutu) berjajar berdampingan secara paralel dalam 3 kolom yang seimbang.
    - *Level Pekerja (Sub-Agents)*: Sub-agents teknis terkelompok rapi di bawah komandan pilar masing-masing secara vertikal.
- **Prinsip Estafet Saling Lempar (Execution Handoff Flow):**
  - Pasang pita alur estafet (*Handoff Ribbon*) di atas kanvas: Mas Bagas (Owner) ➔ Direksi ➔ Si Pintar (Riset) ➔ Si Eksekutor (Lapangan) ➔ Si Pengawas (QC) ➔ Respon Selesai.
  - Pendaran neon dinamis (`n8nNodePulse`) hanya menyorot pilar dan sub-agent yang sedang aktif memegang tongkat eksekusi detik ini, sementara tahapan selesai terkunci hijau emerald.
- **Viewport-Bounded Ergonomics & Pan-Anchor:**
  - Seluruh graf orkestrasi wajib muat nyaman dalam satu bidang pandang layar standar (~1200x650px) tanpa keharusan scroll horizontal panjang.
  - Perhitungan auto-fit kanvas DILARANG memusatkan bounding box yang menghasilkan `translateX` negatif ekstrem (yang mendorong node awal keluar layar). Selalu kunci titik jangkar awal (`dagPanX = 50px`, `dagScale = 0.85`) agar simpul awal selalu tampak di layar saat halaman dimuat.
- **Resiliensi Reverse Proxy & API Prefixing:**
  - Pada aplikasi dasbor yang diproxy di bawah sub-rute (misal `/organisasi`), panggilan `fetch()` di frontend wajib menghormati `apiBase` dinamis (`/api/organisasi/...` vs `/api/...`).
  - Reverse proxy gateway wajib membuka whitelist rute publik untuk seluruh namespace API internal yang dipanggil visualizer (`/api/graph`, `/api/organisasi/graph`) agar tidak terblokir dengan HTTP 401 Unauthorized.

### H. Standar & Teknologi Proyek
- Gunakan arsitektur Vite Multi-Page (MPA) agar setiap modul halaman (`/buttons/`, `/cards/`, `/inputs/`, `/tables/`, `/navigation/`) terisolasi dan cepat dibuka.
- Pastikan ketersediaan dark mode dan light mode dengan kontras slate yang terkalibrasi.
- Selalu sertakan footer resmi: `APEX DESIGN SYSTEM • Hak Cipta & Arsitektur oleh Bagas Cihuy`.
