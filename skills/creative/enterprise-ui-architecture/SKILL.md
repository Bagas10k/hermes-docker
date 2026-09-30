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
- **DILARANG Menumpuk Kartu di Dalam Kartu (Anti-Nested-Card Rule):** Jangan menaruh kartu ber-border dan ber-radius di dalam kartu bento luar (`[nested-cards]`). Gunakan container transparan, button group tanpa border ganda, atau pembatas garis halus 1px.
- **DILARANG Teks Putih di Atas Tombol Oranye (WCAG Contrast Rule):** Tombol aksi oranye (`#FF5C00` atau `#EA580C`) wajib menggunakan teks arang obsidian gelap (`#0F172A` / `#111318`) yang menghasilkan rasio kontras 8.5:1. Teks putih di atas oranye hanya menghasilkan kontras ~3.55:1 dan melanggar WCAG 2 AA untuk teks normal.
- **DILARANG Baris Teks Terlalu Lebar (Strict Line Length Rule):** Batasi lebar kontainer teks narasi/penjelas maksimal 58ch–68ch (`max-width: 60ch`) agar panjang baris tidak melebihi 80 karakter (`[line-length]`).
- **DILARANG Kemiringan 3D pada Panel Teks/Kode (Anti-Blur Orthogonal Rule):** Dilarang menerapkan CSS 3D transforms (`rotateY`, `rotateX`, `perspective`) pada kontainer yang memuat teks kode monospace, diff baris, atau log telemetri; transformasi 3D miring memicu cacat anti-aliasing subpixel pada raster font browser yang menyebabkan teks terlihat kabur/buram (*rasterization blur*). Panel data/kode wajib 100% tegak lurus datar (*flat orthogonal*, `transform: translateZ(0)`), dengan elevasi dan kedalaman visual murni dibangun via layered drop-shadows, border hairline 1px, dan kontras aksen semantik.

## 2. Arsitektur Komponen Inti

### A. Tabel Data Densitas Tinggi & Ledger Finansial
- **Tabular Lining Numerals:** Nominal uang, kuota data, dan stempel waktu wajib menggunakan font monospace (`JetBrains Mono`) agar digit angka sejajar lurus secara vertikal.
- **Status Badge Semantik:** Hijau zamrud (`#10b981`) untuk selesai/settled, Amber (`#f59e0b`) untuk kliring, Merah mawar (`#f43f5e`) untuk gagal/ditolak.
- **In-Place Row Expansion (Accordion):** Baris transaksi dapat diklik untuk membuka rincian audit hash dan virtual account tanpa memuat ulang halaman (*zero-page-jump*).

### B. Interlocking Bento & Real Human Media
- **Asymmetric Corner Radius:** Terapkan variasi radius berbeda per sudut kartu (`border-radius: 36px 36px 12px 36px`) agar kartu saling mengunci (*interlocking puzzle*).
- **Asymmetric Dual-Wing Bento Hero Cockpit (65:35 Golden Ratio):**
  Untuk landing page enterprise dan simulator sistem multi-agen AI:
  - *Wing Kiri (~60-65% lebar, 1.55fr)*: Menampung judul utama berkontras tinggi (Outfit Black), manifesto sistem, selector skenario/mode eksekusi, kanvas graf fisika pegas 60 FPS (Hooke's Law: $F = -kx - cv$), dan bilah tahapan alur kerja horizontal (*stepper*).
  - *Wing Kanan (~35-40% lebar, 1fr)*: Diletakkan sejajar horizontal dengan simulator. Menampung tab pemilih agen aktif, parameter alokasi memori tertutup, serta jendela terminal emulator CLI bertema gelap (*noir*) sebagai jangkar bobot visual (*visual counterbalance*).
  - Menghindari pemotretan vertikal panjang; interaksi dengan kanvas di wing kiri langsung memperbarui telemetri dan log SQL di wing kanan secara real-time tanpa layout shift.
- **Hierarki Tipografi 4 Lapis Disiplin:**
  - *Lapis 1 (Primary Display H1)*: Bold/Black sans-serif (Outfit 900), tight tracking `-0.035em`, skala kontras tinggi.
  - *Lapis 2 (Narrative & Context)*: Teks reguler/medium dengan batas baca ergonomis (`max-width: 58ch`).
  - *Lapis 3 (Tactical Interactive)*: Label tombol, status stepper, dan tabs berbobot semi-bold dengan kontras fungsional.
  - *Lapis 4 (Machine Telemetry)*: Tipografi monospasial (JetBrains Mono) eksklusif untuk kode status (`01.`, `02.`), latensi (`p95: 18ms`), stempel waktu milidetik, dan kueri database. Memisahkan secara tegas bahasa manusia dari bahasa mesin.
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
- **Sensitivitas & Skala Persepsi Non-Linier Equalizer (Anti-Flat VU Meter Rule):**
  - Pemetaan linier mentah pada beban idle/ringan (CPU 5-10%, Disk 0) di dalam wadah sempit (<30px) menyebabkan grafik volume aktivitas hanya berfluktuasi 1-2 piksel di dasar (*terlalu ceper dan naik-turunnya tidak berasa*).
  - Wajib menerapkan kurva persepsi non-linier (`Math.pow(cpu, 0.42)` atau akar kuadrat I/O), ketinggian kontainer minimal 40–44px, modulasi gelombang multi-fase (*harmonic wave overlay*), serta *fast attack* dan *smooth gravity decay* agar detak aktivitas 100ms berdenyut elastis dan visceral di rentang 35%–85%.
- **Penghapusan Ruang Mati & Densitas Maksimal Panel Pemantau (Anti-Void Telemetry Rule):**
  - DILARANG membiarkan panel log atau tabel telemetri menyisakan 80%+ ruang hitam kosong (*longgar*) dengan placeholder pasif seperti "Menunggu tool call...".
  - Sediakan:
    1. *Pita KPI Atas*: Total panggilan, latensi rata-rata, P95, rasio sukses, dan cache hit.
    2. *Fallback Backfill Riwayat*: Jika trace aktif belum memiliki data, otomatis suntikkan 10–25 riwayat pemanggilan tool atau log event global terakhir dari database SQLite WAL.
    3. *Pita Distribusi Bawah*: Persentase distribusi tipe tool (Terminal, Patch, Read, Search) dan error rate.
    4. *Armada Proses & Kernel Watcher*: Manfaatkan margin bawah panel untuk menampilkan kesehatan microservices PM2 fleet serta statistik tasks, threads, dan FDs.
- **Kelengkapan Fitur Versi Desktop & Paritas Kemampuan (Desktop Mission Control Rule):**
  - Jangan menyembunyikan subsystem utama (seperti Autopilot Engine atau Knowledge Vault) hanya di cron latar belakang atau versi mobile; versi desktop wajib memiliki kapabilitas lebih lengkap (*rich cockpit*):
    - *Always-Visible HUD*: Widget ringkas di panel utama dengan badge status, nomor siklus, topik aktif, dan saklar cepat.
    - *Full Mission Control Deck*: Modal terdedikasi (`[F7]`) dengan split-view explorer dokumen riset lengkap (pembaca Markdown utuh dengan evaluasi Tiga Mindset).
- **Ergonomi Lebar Topbar & Pencegahan Tombol Terpotong (Anti-Clipping Topbar Rule):**
  - Pada layar standar 1440px atau 1366px, bilah atas dengan `overflow: hidden` rentan memotong tombol aksi di sisi kanan jika label teks terlalu panjang atau dropdown terlalu lebar.
  - Ringkas label tombol (`[F1: REPLAY]`, `[F2: SPECS]`, `[F6: CHAT]`, `[F7: AUTOPILOT]`, `[MOBILE]`), rapatkan gap (4px), dan batasi lebar elemen select (<140px) agar total lebar topbar aman di bawah 1200px.
- **Adaptasi Otomatis Antar-Perangkat Tanpa Setel Ulang (Zero-Friction Auto-Device Engine Rule):**
  - DILARANG memaksa pengguna melakukan penyesuaian manual (zoom out, pilih resolusi, toggle mode) saat berpindah perangkat (ponsel Android vs laptop vs desktop).
  - Terapkan deteksi adaptif dua lapis:
    1. *Deteksi & Pengalihan Cerdas*: Gateway/server dan skrip `<head>` memeriksa User-Agent serta lebar viewport (`window.innerWidth < 768px`). Jika dibuka di ponsel, otomatis alihkan instan ke `/radar/mobile` (antarmuka mobile berbasis kartu & touch-friendly). Jika di PC/Laptop, otomatis sajikan kokpit desktop penuh (`aoms.html`).
    2. *Preservasi Preferensi Eksplisit*: Jika pengguna di ponsel sengaja memilih `[DESKTOP COCKPIT]`, kunci preferensi ke `localStorage.setItem('radar_force_desktop', 'true')` dengan URL query parameter `?view=desktop` agar tidak memantul (*infinite redirect loop*), dan sediakan tombol kembali `[MOBILE]` di topbar.
    3. *Layout Elastis Vertikal-Horizontal Multi-Breakpoint*:
       - Layar laptop pendek (`max-height: 860px` seperti 1366x768 atau 1280x800): Jangan memaksakan `overflow: hidden; height: 100vh;` yang memotong panel bawah. Ubah ke `height: auto; min-height: 100vh; overflow-y: auto;` dengan batas tier minimum.
       - Layar tablet (`max-width: 1024px`): Rombak grid 3-kolom horizontal menjadi stack vertikal modular yang lapang disentuh.

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
- **Jalur Sirkuit Laser Berkelanjutan Antar-Tahapan (Animated Laser Pipeline Bus vs Static Glyphs):**
  - DILARANG menggunakan karakter panah teks mati (`↓` atau `-->`) untuk menghubungkan tahapan hierarkis proses pada diagram DAG atau alur agen.
  - Wajib menggunakan bus sirkuit SVG poligonal beranimasi dinamis yang memancarkan status proses secara fisik:
    - *Tahap Selesai (DONE)*: Garis laser hijau toska (`#10b981`) solid dan tenang dengan pendaran halus.
    - *Tahap Sedang Berjalan (ACTIVE / RUNNING)*: Garis laser cyan neon (`#00f0ff`) dengan aliran pulsa partikel energi berkecepatan tinggi (`<animateMotion>` atau running `stroke-dashoffset`) yang mengalir deras ke simpul agen aktif.
    - *Tahap Menunggu (IDLE / QUEUED)*: Garis sirkuit redup bergaris putus-putus tanpa energi.
- **Penempatan Jendela HUD Mengambang & Anti-Occlusion (Clear Quadrant Docking):**
  - Saat merender jendela live action / inspektor kode mengambang yang terhubung ke simpul aktif, DILARANG menaruh posisi jendela dengan offset horizontal sepihak langsung (`node.right + 18px`) jika terdapat simpul lain di sampingnya (misal deretan kartu sub-agen paralel). Hal ini memicu tabrakan dan menutupi kartu agen tetangga (*card occlusion*).
  - Selalu tambatkan jendela HUD pada kuadran kanvas yang lapang (misal kuadran kanan atas yang kosong), lalu hubungkan titik simpul agen aktif ke jendela HUD melalui kurva dinamis SVG Bézier (`M startX startY C cX1 startY, cX2 endY, endX endY`) dengan pendaran neon cyan dan partikel pulsa bergerak.
- **Konsolidasi Sub-Halaman Fragmented & Preservasi Mandat:**
  - Jangan membiarkan rute lama (misal `/organisasi`) berjalan sebagai antarmuka terpisah yang terpecah jika sistem telah berevolusi memiliki cockpit terpadu (`/radar`). Alihkan rute lama secara otomatis via HTTP 302 dan serap seluruh fitur hierarki, mandat organisasi, dan sensor keselamatan (kuota RAM 9.0 GB) ke dalam modal terintegrasi (misal `[F5: KABINET]`).

### H. Standar & Teknologi Proyek
- Gunakan arsitektur Vite Multi-Page (MPA) agar setiap modul halaman (`/buttons/`, `/cards/`, `/inputs/`, `/tables/`, `/navigation/`) terisolasi dan cepat dibuka.
- Pastikan ketersediaan dark mode dan light mode dengan kontras slate yang terkalibrasi.
- Selalu sertakan footer resmi: `APEX DESIGN SYSTEM • Hak Cipta & Arsitektur oleh Bagas Cihuy`.

### I. Pola Prototipe POS & Dasbor Finansial B2B Siap Pitch Klien (Client-Ready Business Systems)
- **Quick Demo Role Chips pada Dialog Autentikasi / Login:**
  Saat mempresentasikan prototipe aplikasi bisnis, kasir POS, atau dashboard manajemen langsung ke klien bisnis, DILARANG memaksa demonstrator mengetik kredensial manual atau menghafal password akun demo. Sediakan pil akses cepat 1-klik (`[Demo Kasir]`, `[Demo Kepala Toko/Admin]`) yang otomatis mengisi form login (ID pengguna, PIN, shift kerja) secara instan dan realistis agar momentum presentasi tetap lancar.
- **Konfigurasi Vite Relative Asset Base (`base: './'`) pada Sub-Rute Reverse Proxy:**
  Saat membangun aplikasi web statis yang disajikan di bawah sub-rute reverse proxy (misal `/kasir-bangunan/`), Vite WAJIB dikonfigurasi dengan `base: './'` di `vite.config.js`. Base default (`/`) menyebabkan bundler menghasilkan path aset absolut (`/assets/...`) yang langsung diarahkan ke root origin server induk, memicu galat HTTP 401/404 atau MIME type mismatch (`application/json` alih-alih CSS/JS).
- **Simulasi Struk Thermal 80mm Berstandar Operasional Asli:**
  Pada sistem kasir retail/grosir, jangan hanya mengandalkan notifikasi toast selesai transaksi. Sediakan dialog struk belanja berformat thermal 80mm monospaced (`JetBrains Mono` / `Courier`) lengkap dengan nomor faktur urut, waktu transaksi, identitas kasir, rincian item, subtotal, potongan diskon volume/kontraktor, PPN, uang diterima tunai, kembalian otomatis, barcode SVG, serta tombol aksi ganda: cetak printer thermal fisik (`window.print()`) dan bagikan struk via WhatsApp Web.
- **Kalkulator Margin Laba Otomatis pada Formulir Input Master Barang:**
  Pada form penambahan material/produk baru, selalu sertakan kalkulator margin laba kotor dinamis secara real-time: `Margin = ((Harga Jual - HPP) / Harga Jual) * 100%` dengan pewarnaan semantik (hijau tebal jika >= 15%, amber jika margin tipis < 15%, merah jika negatif/rugi) untuk memberikan feedback nilai bisnis instan kepada klien.
- **Kontras Warna Badge Status Semantik WCAG AA (>= 4.5:1) pada Latar Pastel:**
  Hindari menggunakan warna status teks menengah terang (`#10b981`, `#f59e0b`, `#ef4444`) di atas latar belakang kontainer pastel lembut (`#ecfdf5`, `#fffbeb`, `#fef2f2`); kombinasi ini hanya menghasilkan rasio kontras ~2.8:1 dan melanggar audit Axe-Core WCAG AA. Gunakan shade 700/800 yang pekat (Emerald `#047857`, Amber `#b45309`, Red `#b91c1c`) agar kontras rasio minimal 4.5:1 tercapai secara terverifikasi.
- **Aturan Aksesibilitas ARIA Role pada Kontainer Grafik SVG (`role="img"` / `role="region"`):**
  DILARANG menyematkan atribut `aria-label` langsung pada elemen `<div>` generik tanpa mendeklarasikan `role` aksesibilitas yang valid. Memberikan `aria-label` pada kontainer grafik tanpa atribut `role="img"` atau `role="region"` memicu pelanggaran `aria-prohibited-attr` pada mesin pemeriksa aksesibilitas otomatis.
- **Navigasi Bilah Sisi Kiri Vertikal (*Slidebar / Vertical Rail*) vs Topbar Tabs pada Sistem Kasir POS:**
  Pada sistem kasir POS dan ruang kendali operasional B2B, hindari tab navigasi horizontal di bilah atas (*topbar*) yang sempit dan rentan terpotong. Wajib menggunakan *Vertical Slidebar* (lebar 260–270px) tetap di sisi kiri layar dengan susunan empat kompartemen teratur:
  1. *Brand Teks Toko*: Identitas tipografi bersih tanpa logo grafis simbolis.
  2. *Status Shift*: Kartu indikator shift aktif titik hijau dan jam operasional real-time.
  3. *Navigasi Inti*: Tombol menu vertikal dengan active indicator bar, ikon garis SVG, dan pill counter jumlah item keranjang POS.
  4. *Sektor Akun & Logout*: Profil kasir bertanda avatar inisial dan tombol aksi **`Logout / Ganti Kasir`** eksplisit di footer sidebar.
  Pada layar tablet/ponsel (<1024px), sidebar otomatis bertransformasi menjadi laci geser (*slide-over drawer*) dengan tombol hamburger, tombol tutup (`X`), dan layar peredup latar (*scrim backdrop blur*).
- **Identitas Tipografi Teks Bersih Tanpa Logo Gambar Simbolik (*Pure Typography Wordmark*):**
  Saat merancang antarmuka untuk presentasi klien yang menginginkan kesederhanaan, DILARANG memaksakan ikon grafis 3D/kubus/simbol generik di header atau dialog login. Gunakan tata letak tipografi sans-serif tebal yang berwibawa (*text-only wordmark*, misal `TOKO BANGUNAN` dengan badge cabang `CABANG 01 • GUDANG PUSAT`) untuk menghadirkan kesan rapi, profesional, tidak sesak, dan bebas dari kesan template purwarupa mentah.
- **Netralitas Nama Entitas pada Prototipe & Pitch Klien (*Strict Client Neutrality & Whitelabel Rule*):**
  Saat merancang prototipe, landing page, atau sistem kasir/dasbor yang akan disodorkan langsung ke klien bisnis/pihak ketiga, DILARANG mencantumkan nama legal PT/CV perusahaan spesifik pada antarmuka (bilah header, simulasi struk belanja kasir, nomor rekening bank transfer, maupun dialog login) kecuali bila diinstruksikan secara eksplisit. Selalu gunakan nama bisnis/industri generik yang netral dan berkelas (misal `TOKO BANGUNAN`, `REKENING KASIR PUSAT`, `SUPERMARKET MATERIAL`) agar prototipe bersifat *white-label*, dapat dipresentasikan secara universal ke berbagai calon klien tanpa bias entitas lama atau kebocoran nama pihak lain.
- **Alur Logout Berpaut ke Dialog/Halaman Login untuk Demonstrasi Shift Kasir:**
  Sertakan tombol Logout yang mudah diakses di area profil kasir (dasar sidebar). Mengklik Logout wajib memicu dialog/halaman login kembali dengan notifikasi toast penjelasan status sesi berakhir, langsung siap menerima pemilihan akun demo baru (*Kasir* vs *Kepala Toko*) secara instan di hadapan klien tanpa perlu me-reload halaman browser.
- **Penyembunyian Counter Badge Bernilai Nol (Zero-Count Badge Visibility Rule):**
  DILARANG menampilkan counter badge atau pill numerik yang bernilai "0" di samping menu navigasi (misal badge `0` di menu Kasir POS). Menampilkan angka 0 menimbulkan distraksi kognitif seolah ada notifikasi atau item tertunda. Counter badge WAJIB disembunyikan (`display: none` / kondisional DOM) jika nilainya 0, dan HANYA dimunculkan secara dinamis saat nilai item > 0.
- **Eliminasi Garis Bertabrakan pada Elemen Menu Terpilih (Anti-Clashing Indicator Rule):**
  DILARANG menumpuk garis vertikal tajam 3px di tepi kiri (`::before`) di atas kontainer tombol menu yang memiliki sudut membulat (`border-radius: 8px`). Garis datar tajam yang menabrak lengkungan sudut menciptakan artefak visual yang berantakan/cacat. Gunakan penanda aktif tunggal yang bersih dan kohesif: *soft-tint background pill* (`#eff6ff`, border `#bfdbfe`, teks/ikon `#1d4ed8`) dengan bayangan halus, tanpa garis vertikal tajam terpisah di dalam radius melengkung.
- **Harmonisasi Tipografi & Mesin Jam Dinamis pada Widget Status Shift (Anti-Monospace Misalignment):**
  DILARANG menggunakan font monospace bergaya terminal/mesin tik untuk tanggal dan jam operasional di tengah panel navigasi bertipografi sans-serif modern, dan DILARANG membiarkan waktu berupa teks statis. Status shift dan waktu operasional wajib menggunakan font sans-serif proporsional (*Plus Jakarta Sans*), berindikator titik hijau dengan pendaran halus (*pulsing halo*), serta terhubung ke engine jam real-time dinamis (`setInterval`) yang memperbarui tanggal dan detik secara hidup.
- **Keselarasan Bobot & Famili Ikon Navigasi (Icon Stroke & Optical Weight Consistency):**
  DILARANG mencampurkan ikon garis tipis mentah (seperti tanda plus `+` satu garis untuk entri data) berdampingan dengan ikon bervolume atau ikon Lucide berstruktur (grid, cart, doc, cube). Seluruh ikon navigasi wajib seragam dalam satu famili (vektor inline SVG Lucide/Feather, stroke 1.8px/2px, dimensi 18–20px) dengan metafora visual yang tepat (misal ikon `file-plus-2` untuk input master data).
- **Ruang Bernapas Vertikal (*Breathing Room*) Label Seksi Sidebar:**
  DILARANG menempelkan label seksi kapital (`MENU UTAMA`) terlalu mepet dengan kartu status atau kontainer di atasnya. Berikan margin/padding yang cukup (`margin: 14–16px 14px 6px; padding: 6px 10px`) agar ritme visual dari identitas toko, kartu shift, ke menu navigasi memiliki hierarki ruang yang seimbang, lapang, dan tidak sesak.
