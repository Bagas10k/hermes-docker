---
name: design-vault
description: Use when authoring UI/UX components or design systems.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design, ui-ux, components, design-system, anti-template, buttons, cards, typography, forms]
---

# Design Vault: Sistem Bank Komponen & Anti-Template UI/UX

Gunakan skill ini saat merancang antarmuka web, membuat landing page, menyusun sistem desain, atau memilih varian komponen (tombol, kartu, form input, tipografi, badge, header, footer). Skill ini mengkodifikasi bank komponen hidup yang tersimpan di `C:\Users\Administrator\Desktop\latihan ai\design-system-vault\` dan aturan pencegahan desain template AI.

## 1. Aturan Anti-Template AI & Anti-Slop (Absolute Quality Gates)

Kebiasaan gagal generatif AI yang paling sering terjadi adalah menyusun landing page seragam: **headline tengah melayang + badge pemanis di atas + teks bergradasi pelangi + 3-4 kartu fitur identik dengan ikon bulat di atas**. Pola ini membuat desain langsung dinilai "terlalu template", jelek, dan kehilangan kredibilitas.

Aturan pencegahan mutlak:
1. **Zero Text Gradient**: Judul dan heading wajib berwarna solid monokrom murni (putih di dark mode, hitam di light mode). Dilarang keras menerapkan teks bergradasi pelangi/neon cyan-purple yang merupakan penanda khas template AI generik.
2. **Zero Decorative Badge Kickers**: Dilarang meletakkan kapsul pil pemanis dekoratif mengambang di atas headline utama (misal: "● PRODUCTION-GRADE..."). Mulai langsung dari headline inti atau value proposition lugas.
3. **Wordmark-Only Branding**: Hindari logo box generik (seperti ikon huruf dalam kotak gradasi). Gunakan tipografi murni (*pure typographical wordmark*) dengan tracking presisi.
4. **Anti-Slop Directory & Dashboard Taxonomy**:
   - Jangan pernah mencampuradukkan sistem operasional/bisnis aktif terpisah ke dalam daftar kartu proyek generik.
   - Bedakan dengan tegas antara **Publikasi/Produksi (Live)** dan **Internal/Lab (Uji Coba)**.
   - Hindari layout bento bertumpuk warna-warni semu (pastel pills, icon boxes warna-warni acak). Gunakan chassis linier berdensitas tinggi (Linear/Obsidian style), micro-dot status 6px monokrom/status murni, dan garis 1px bergradien nol.
5. **Pilih Arketipe Permukaan Sebelum Menata Token**:
   - **Operate / Console-First**: Untuk sistem kerja, sekolah, enterprise, B2B, atau alat manajemen. Jangan gunakan hero promosi; gunakan instrumen kerja langsung (tabel mutasi live, log kehadiran, status server).
   - **Explore / Catalog**: Untuk produk makanan, retail, e-commerce. Komposisi didominasi galeri visual berbobot, radar profil rasa, dan laci keranjang geser.
   - **Monitor**: Untuk analitik, finansial, dan observabilitas. Kepadatan glanceable metrik angka besar (*stadium typography*) dan scrubber interaktif.
   - **Decide / Learn**: Hanya gunakan hero headline besar jika tujuannya murni edukasi/konversi satu ide per bagian.
5. **Karakter Sesuai Domain**:
   - Sistem formal/institusi/sekolah membutuhkan otoritas: palet formal navy/slate, tabel ledger rapat, font humanist tajam, zero fluff marketing.
   - Produk consumer/kriya membutuhkan kehangatan bahan: warna perkamen, tipografi serif italic humanist, foto asli.
   - Produk digital/modern: palet akromatik dengan aksen tunggal disiplin (gaya Linear/Mercury/Revolut).
6. **Arsitektur Multi-Page (MPA) untuk Publikasi Referensi**: Proyek referensi komponen kelas publikasi wajib dipisah ke halaman mandiri per kategori menggunakan bundler modern (Vite) dengan Home Bento Hub interaktif.

---

## 2. Bank Referensi Komponen Hidup (`APEX Design System` / `design-system-vault`)

Sebelum merancang antarmuka dari nol, manfaatkan koleksi komponen teruji yang sudah terverifikasi di bank desain:

### A. Bank Gaya Tombol (50 Varian Lengkap)
Koleksi lengkap 50 varian tombol hidup di `design-system-vault/index.html` terbagi dalam 4 kelompok:
1. **Minimalist, Software & Engineering (1–12)**: Linear Ghost, Liquid Frosted Glass, Neo-Brutalist Pop, Cyber Neon Terminal, Fintech Chunk Pill (Revolut), 3D Tactile Push Bubble, Shimmer Gradient, Expanding Underline, Beacon Pulse Live, Segmented Control Tabs, Elevated Circle FAB, Split Dual Action.
2. **Modern Product & Next-Gen SaaS (13–25)**: Vercel Stark Mono, Stripe Violet Glow, Neumorphic Soft Extrude, Border Beam Pulse, Retro Mac System 7, Glitch RGB Split, Raycast Spotlight Pill, Hairline Monochrome, Rainbow Prism Border, Arc Browser Capsule, Chip with Pill Counter, Destructive Confirm Alert, Spring Tactile Hover.
3. **Tactile, Hardware & Retro Mechanical (26–38)**: Cherry MX Keycap, Sunset Gradient Glass, Artisan Rotated Sticker, Blinking Unix Cursor, Brushed Metal Chrome, Studio 48V Switch, Embedded Loading Spinner, Success Confirmed Check, Micro Copy Clipboard, Podcast Scrubber Pill, 8-Bit Retro Arcade, CAD Blueprint Dotted, Matte Terracotta Roast.
4. **Creative, Micro-Interactions & Experimental (39–50)**: Arrow Slide Extension, Slide Track Verify, Aurora Northern Lights, Figma Component Node, Notion Minimal Row, GitHub Social Repo, Liquid Organic Blob, Industrial Caution Hazard, Equalizer Sound Pill, Shortcut Keyboard Tag, Synthwave Dual Neon, 3D Isometric Postage.

### B. Evaluasi Sasis Fisik Kartu & Arsitektur Lanjut (20+ Sasis Teruji)
Kartu dinilai dari **bentuk fisik kanvas/sasis kontainernya** dan **keselarasan isi 100% (Form-Meets-Function)**:
- **Sasis Fisik Kontainer Beragam**: Hairline Flat 1px, 3-Layer Diffused Float, Deep Frosted Glass, Concave Sunken Inset Well, Gradient Rim, Neo-Brutalist 2.5px Hard Block, Dashed CAD Blueprint, Sliced Top Rail, Chamfered 45° Polygon, Neumorphic Dual Convex, Squircle 28px, Left Rail Status, Deck Layer Stepped, Brushed Metal, Desktop OS Window, Dot Matrix Grid, In-place Expandable Drawer, Industrial Hazard Strip, 3D Drop Depth 8px.
- **Keselarasan Isi Nyata**: Sasis kontainer harus memuat data fungsional nyata (spec sheet cluster, balance portofolio Rp 2.84M, sensor cuaca, audio VU meter), bukan placeholder semu.
- **Studi Stroke vs Shadow Murni**: Evaluasi garis tepi vs bayangan wajib menggunakan konten dalaman identik dan polos agar penilaian murni pada perlakuan batas dan elevasi.
- **Card-Based Mobile Table Handling (Console Pattern)**: Mengubah tabel `<table class="...table...">` standar menjadi tumpukan kartu pada layar sempit (mobile) dengan mengatur `table, thead, tbody, th, td, tr { display: block; }`, menyembunyikan `thead` (via absolute positioning `-9999px`), dan menyuntikkan label statis pada `td:before { content: "Header Name"; position: absolute; left: 10px; }`.
- **Transparent Image Fallback (Anti-Broken UI)**: Mencegah kerangka tata letak rusak (broken image icon) akibat HTTP 403 atau 404 dari server pihak ketiga dengan menanamkan fallback langsung pada elemen: `<img src="..." onerror="this.style.display='none'">` atau `onerror="this.parentElement.style.display='none'"`.
- **Live Preview iFrame Editor (Mini-Canva Pattern)**: 
  - Saat merancang dasbor editor komponen statis yang perlu dipotret oleh Puppeteer, jangan merender ulang DOM di parent window.
  - Pisahkan kanvas target ke `iframe`. Gunakan form input dengan `onkeyup` di parent window, lalu tembak DOM iframe secara dinamis tanpa *refresh* menggunakan: `iframe.contentWindow.postMessage({ type: 'UPDATE', payload: data }, '*')`.
  - Tangkap pesannya di dalam iframe via `window.addEventListener('message', ...)` untuk memperbarui teks/ukurannya (*real-time slider tweak*).
- **4 Perilaku Interaksi Lanjut**:
  1. *Spatial Proximity Ray*: Pendaran volumetrik membaca kursor mouse radius 320px (`radial-gradient`).
  2. *Physical Deck Stacking*: Ilusi tumpukan kartu fisik 3D yang dapat diklik untuk rotasi antrean tiket.
  3. *In-place Expandable Drawer*: Kartu mengembang di tempat (*zero-page-jump*) untuk inspeksi error log.
  4. *Rugged Tactical Chamfer*: Sudut potong 45° dengan strip pelat proteksi perimeter luar.
- **Interlocking Asymmetric Bento & Node Flow (Pola Pinterest Zylo)**:
  - Sudut asimetris organik per kartu (`36px 36px 8px 36px`, `36px 36px 36px 8px`) yang saling mengunci (*interlocking puzzle*).
  - Alur fitur interaktif disajikan sebagai diagram pipa node (`[Pill]` -> `(+)` -> `[Pill]`) dengan tombol konektor lingkaran berotasi 90°.

### C. Bank Form & Kontrol Input (30 Presets Teruji)
Koleksi 30 arsitektur kontrol masukan data presisi yang terkalibrasi di `apex-ui/inputs/`:
1. **Linear Monochrome Clean**: Input akromatik bersudut 6px tajam dengan border slate yang berubah menjadi putih solid saat fokus aktif.
2. **Floating Kinetic Label**: Label teks melayang ke atas via pure CSS transition saat input difokuskan.
3. **Financial Currency Ledger**: Format input nominal finansial dengan prefix `IDR` hijau zamrud dan angka tabular `JetBrains Mono`.
4. **OTP 6-Digit PIN Cells**: Kotak verifikasi 6-segmen terpisah dengan tanda hubung pemisah di tengah.
5. **Unix Shell CLI Prompt**: Wadah baris perintah konsol berlatar hitam pekat dengan host prompt hijau fosfor (`root@host:~$`).
6. **Discrete Stepped Slider**: Slider sumber daya server bertingkat dengan aksen cyan dan persentase kuota live.
7. **Tactile Toggle Switch**: Sakelar fisik iOS/macOS dengan knop bulat halus dan transisi hijau mulus.
8. **Segmented Radio Switcher**: Bilah kontrol kapsul multi-opsi untuk beralih mode runtime (Dev, Staging, Prod).
9. **Password Eye Reveal**: Kolom sandi terproteksi dengan tombol glyph mata instan.
10. **Autocomplete Chip Box**: Wadah tokenisasi tag dinamis yang dapat dihapus per unit.
11. **Neumorphic Inset Well**: Bidang masukan ambles (*sunken*) dengan bayangan inset ganda lempung lembut.
12. **Neo-Brutalist Hard Block**: Garis batas hitam 2.5px dengan bayangan solid miring 4px tanpa blur.
13. **CAD Technical Dashed**: Border putus-putus biru sian cetak biru untuk koordinat vektor teknis.
14. **Tactical 45° Angular**: Sudut terpotong 45 derajat menggunakan `clip-path` poligon avionik militer.
15. **Command Search Bar**: Bilah pencarian cepat dengan shortcut keyboard `⌘K`.
16. **Hex Color Picker Swatch**: Pemilih warna terpadu antara swatch cakram native dan teks heksadesimal.
17. **Dual Calendar Range**: Pasangan kalender rentang waktu log audit awal dan akhir.
18. **File Drag Dropzone**: Area unggah berkas drag & drop bergaris putus-putus interaktif.
19. **Tactile Checkbox Row**: Kotak centang fungsional dengan label regulasi dan sub-keterangan kepatuhan.
20. **Clean Inline Select**: Menu dropdown dengan panah chevron kustom tanpa kotak browser default.
21. **Frosted Glass Translucent**: Permukaan kaca buram berlatar blur 14px dengan highlight cincin atas.
22. **Validation Error State**: Indikator kesalahan format masukan berbingkai merah mawar dengan badge peringatan spesifik.
23. **Validation Success State**: Indikator sukses validasi masukan berbingkai hijau zamrud dengan centang verifikasi.
24. **Monospace Code Textarea**: Kolom masukan teks multi-baris monospace untuk konfigurasi reverse proxy atau JSON.
25. **Number Stepper Controller**: Kontrol penambah dan pengurang angka diskret dengan tombol plus-minus menyatu di sasis.
26. **Interactive Star Score**: Pemilih rating kepuasan dengan glyph bintang emas dan angka desimal.
27. **Dual Balance Audio Fader**: Fader audio stereo kiri-kanan dengan detent titik tengah (*center 0*).
28. **Left Rail Status Accent**: Kolom masukan bergaris tebal 4px merah solid di bibir kiri sasis.
29. **Radio Selection Tiles**: Ubin kartu radio bertingkat yang dapat diklik langsung untuk memilih paket hardware SSD.
30. **Dot Matrix Spatial HUD**: Bidang masukan spatial berhias bintik matriks radar 12px x 12px dengan teks fosfor cyan.

### D. Bank Badges & Status Pills (8 Varian)
- Status emerald pulse (*Online 99.9%*), blue dot (*Syncing*), amber (*Pending*), rose (*Timeout*), purple (*AI Synthesized*), monospace hash (*Build*), promo pop, dan hotkey tag (`⌘K`).

### E. Pasangan Tipografi Terkalibrasi
- **Precision Software**: *Inter Variable* (`cv01`, `ss03`) + *Space Grotesk*.
- **Luxury Editorial**: *Newsreader* (Serif) + *Plus Jakarta Sans*.
- **Neo-Pop Impact**: *Syne 800* + *Space Grotesk*.
- **Telemetri Finansial**: *JetBrains Mono* dengan format digit `tabular-nums`.

---

## 3. Alur Kerja Perancangan Cepat
1. **Analisis Persona & Kredibilitas**: Siapa penggunanya (usia, konteks bisnis)? Hindari visual remaja untuk sistem korporasi; hindari visual kaku untuk produk pop.
2. **Pilih 1 Set Token dari Vault**: Tentukan 1 gaya tombol, 1 gaya kartu, 1 varian kontrol form/input, dan 1 pasangan font dari katalog di atas.
3. **Bangun Prototipe Self-Contained**: Simpan dalam format HTML5 + CSS Variables murni yang siap disalin kodenya.
4. **Wajib Verifikasi Visual Browser Nyata**: Sebelum mengonfirmasi tugas selesai, buka halaman di browser nyata dan evaluasi tangkapan layar via vision tool. Periksa secara kritis:
   - Apakah ada tabrakan teks (*text collision / overlap*) pada kartu bertingkat atau judul dan badge.
   - Apakah ada teks terpotong (*text truncation / overflow*) pada kolom pencarian dan input.
   - Apakah elemen bento membentang proporsional dan tidak terlempar keluar dari kontainer induk.
   - Perbaiki semua cacat visual secara tuntas sebelum menyerahkan laporan kepada pengguna.
