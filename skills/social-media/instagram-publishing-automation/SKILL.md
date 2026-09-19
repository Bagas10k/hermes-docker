---
name: instagram-publishing-automation
description: Use when automating Instagram posts via Meta Graph API.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [social-media, instagram, meta-graph-api, puppeteer, carousel, automation]
---

# Instagram Publishing Automation

Gunakan skill ini saat menghubungkan sistem ke akun Instagram, menangani token Meta Graph API, atau membangun alur auto-publish yang mengubah data web (HTML) menjadi aset visual (Carousel/Post) secara otomatis.

## 1. Solusi Akses API & "Peran Developer Tidak Memadai"
Sistem Meta Developer sangat ketat saat memberikan *Access Token*. Kegagalan paling umum saat membuat App dan mengambil token adalah munculnya popup error: *"Peran Developer Tidak Memadai"*.

**Pitfalls & Syarat Mutlak (Wajib):**
- **Status Akun:** Akun Instagram target WAJIB diubah menjadi **Akun Profesional / Kreator**. Akun pribadi (Personal) akan langsung ditolak sistem Meta.
- **Tautan Facebook Page:** Akun Instagram target WAJIB ditautkan secara resmi ke sebuah Halaman Facebook (meski halamannya kosong). Meta Graph API menggunakan *Page Access Token* sebagai pintu masuk ke Instagram.
- **Persetujuan Penguji (Tester Invite):** Setelah mendaftarkan akun sebagai "Penguji" di *App Roles* Meta Developer, statusnya akan menggantung ("Menunggu Persetujuan"). Jangan mencari tombol persetujuan di desktop.
  - **Cara Menyetujui:** Masuk ke aplikasi Instagram (via smartphone) > **Pengaturan dan Privasi** > **Situs Web dan Aplikasi** (atau **Izin Situs Web**) > **Undangan Penguji** > Klik **Setujui**. (Atau langsung buka URL: `https://www.instagram.com/accounts/manage_access/` di browser web yang sedang login Instagram target).

## 2. Generate Long-Lived Access Token
Token awal yang digenerate oleh *Graph API Explorer* hanya bertahan 1-2 jam.
- **Prosedur:** Di *Graph API Explorer*, pilih target *Page Access Token*, beri izin `instagram_basic` dan `instagram_content_publish`. Klik tombol *Info (i)* pada token > *Open in Access Token Tool* > Klik *Extend Access Token* untuk mendapatkan token berumur 60 hari.

## 3. Workflow Auto-Render Carousel (HTML to IG)
Alih-alih mengedit foto, gunakan alur HTML-to-Image berbasis *headless browser*.

1. **Siapkan Sasis HTML:** Desain *template* menggunakan resolusi *Portrait IG* absolut (`width: 1080px; height: 1350px;`) untuk tiap elemen `.slide`. Gunakan CSS Grid/Flexbox dan Web Fonts.
2. **Pre-download External Images Server-Side & WAF Bot-Wall Handling:**
   Puppeteer yang me-load `http://127.0.0.1/carousel.html` akan GAGAL memuat gambar dari domain eksternal (misal `https://news.mit.edu/...`) karena CORS/mixed-content. Solusi: sebelum launch browser, download semua image field ke `ig-cache/` lokal via `fetch()` server-side, lalu ganti URL di payload menjadi `http://127.0.0.1:{PORT}/ig-cache/hero_{draftId}_{fieldId}.jpg`. Ini menjamin gambar termuat 100%.
   - **PITFALL WAF / Cloudflare Bot Wall 403 (Kanvas Hitam Kosong):** Media berita global (Politico, The Guardian, dsb) memproteksi URL gambar mereka dengan Cloudflare/Varnish yang langsung mengembalikan status `403 Forbidden` terhadap HTTP `fetch()` bawaan Node.js. Kegagalan unduh yang tertangkap `catch` diam-diam (*silent failure*) membuat slide cover dirender tanpa gambar latar (kanvas hitam pekat).
   - **FIX:** Selalu periksa `imgRes.ok` dan panjang konten. Jika endpoint media terhalang bot wall 403, gunakan domain CDN statis terbuka (seperti `static.*`), unduh via biner shell `curl`/`ffmpeg` ke cache lokal, lalu gunakan URL lokal (`http://127.0.0.1:{PORT}/ig-cache/...`) pada payload draft sebelum merender. Lakukan inspeksi visual (`vision_analyze`) pada berkas PNG slide 1 hasil render untuk memverifikasi subjek foto tampil utuh sebelum persetujuan.
   - **PITFALL Meta Crawler 401 & Cloudflare Privacy Boundary (Error Subcode 2207052):** Saat Meta Graph API mengunduh slide dari `image_url` pada `POST /{account_id}/media`, jika reverse proxy / privacy boundary (misal `privacy-boundary.js`) memblokir path dengan `401 Authentication required`, crawler Meta akan menerima JSON error alih-alih biner gambar, memicu error `OAuthException 9004 / 2207052: Only photo or video can be accepted as media type`.
   - **PITFALL Whitelist Regex Ekstensi Terlalu Sempit (Kanvas Hitam / Gambar Hilang di Render):** Jika reverse proxy / privacy boundary hanya membuka akses publik untuk ekstensi `\.png` saja, berkas media pra-unduh berformat `.webp`, `.jpg`, atau `.jpeg` akan ditolak dengan `401 Unauthorized`. Akibatnya, Puppeteer yang merender template carousel lokal memuat JSON 401 alih-alih gambar nyata, sehingga slide dirender sebagai kanvas hitam pekat atau teks polos tanpa foto.
   - **FIX:** Direktori publikasi gambar statis (seperti `/ig-cache/` dan `/sputarball/ig-cache/`) WAJIB didaftarkan ke daftar putih akses publik (`isPublic`) pada reverse proxy / gateway untuk SELURUH ekstensi visual umum (`\.(?:png|jpe?g|webp)$`), serta membuka pengecualian untuk IP loopback internal (`127.0.0.1`), memperbolehkan metode `GET` dan `HEAD` tanpa cookie sesi pribadi.
3. **Wait for Images + Fonts Before Screenshot:**
   Setelah `waitForSelector('.ig-slide-1')` dan `document.fonts.ready`, WAJIB tambahkan `Promise.all([...document.querySelectorAll('img')].map(img => img.complete ? resolve() : new Promise(onload/onerror/timeout)))`. Tanpa ini, screenshot akan menangkap placeholder kosong — file size ~89KB vs ~986KB ketika gambar benar-benar termuat.
4. **Hit & Destroy Browser (RAM Resilience):**
   Gunakan Puppeteer untuk mengambil *screenshot* selektor `.slide`. RDP Windows memori terbatas (8GB); pastikan memanggil `browser.close()` secara sinkron secepatnya setelah *buffer* gambar selesai dibuat. Dilarang membiarkan Puppeteer *standby* di memori. Tambahkan `args: ['--no-sandbox']` pada launch options.
5. **Quality Control (QC) Inspector Gate (Mandatory Pre-Publish Audit):**
   Sebelum draf diteruskan ke Meta Graph API, WAJIB melewati gerbang inspeksi otomatis oleh **QC Sub-Agent** (`qc-inspector.js`):
   - *Integritas Berkas & Geometri:* Membaca langsung biner *IHDR PNG* (byte 16-24) untuk memvalidasi resolusi tepat 1080x1350 px dan ukuran berkas (35 KB s/d 8 MB). Menggugurkan draf jika ada slide hilang atau kanvas blank.
   - *Audit Berat Berkas & Deteksi Slide Kosong:*
     - Slide 1 (Hook Cover) WAJIB memiliki ukuran berkas minimal 350–400 KB. Ukuran < 250 KB mengindikasikan foto hero gagal termuat dan kanvas hanya menampilkan teks di atas latar belakang hitam polos (*blank scrim*).
     - Slide 2 (Konteks / Warta Harian) WAJIB memiliki ukuran berkas minimal 250–300 KB. Ukuran < 200 KB mengindikasikan foto pendukung tidak ter-render.
   - *Audit Anti-Watermark & Stock Slop:* Menolak keras penggunaan gambar yang bersumber dari agensi stock foto ber-watermark (*Vecteezy*, *Freepik*, *Getty*, *Alamy*, *Shutterstock*, *iStock*, *Dreamstime*) atau thumbnail beresolusi rendah (*small_2x*, *thumbnail*, *socialshare max-600x600*).
   - *Audit Copywriting & Slop:* Memeriksa panjang headline (10–120 karakter), ketiadaan artefak markdown (`**`, `##`, ````), kicker kapital, serta integritas struktur JSON fakta di Slide 2, 3, dan 4.
   - *Audit Mutu Cropping & Framing Subjek (`qc_crop.py`):*
     - *Headroom Check:* Menolak jika dahi, kepala, atau rambut subjek terpotong garis lurus di tepi atas kanvas (`y=0`).
     - *Anchoring & Grounding Check:* Menolak jika potongan dada/badan (*bust shot*) terpotong rata melayang di tengah kanvas tanpa menempel di dasar kanvas (*floating decapitation*).
     - *Island Artifacts:* Mendeteksi dan menolak serpihan sisa background (rumput hijau, potongan pakaian orang lain) yang tertinggal via analisis komponen terhubung.
     - *Framing & Coverage Ratio:* Memastikan proporsi tinggi subjek proporsional (minimal 25% tinggi kanvas agar tidak kerdil atau luber menabrak teks).
     - *Edge Anti-Aliasing:* Memastikan batas tepi potongan memiliki gradasi alpha lembut, bukan potongan kotak piksel kasar (*pixelated/jagged*).
   - *Sinkronisasi Frekuensi Kreator & QC (Design Intent Contract):*
     - QC dilarang menginspeksi secara buta niat (*intent-blind*). Kreator menyematkan metadata `design_intent` ke dalam draf (arketipe desain, batas jumlah slide sah, aturan cropping).
     - QC membaca kontrak tersebut sebelum mengaudit: jika Kreator merancang draf 2 slide (`MATCH_RECAP_2SLIDE`), QC hanya mengaudit 2 slide dan tidak menuntut adanya slide 3 atau 4; jika Kreator merancang poster 1 slide (`MATCH_POSTER_SINGLE`), QC memverifikasi poster tunggal; jika subjek dirancang *close-up dramatis* (`ALLOW_BLEED`), QC tidak memotong nilai untuk *headroom*. Hal ini menjamin Kreator leluasa berinovasi dan QC mengawal mutu secara presisi tanpa salah paham (*zero false-positives*).
   - *Koherensi Entitas:* Memastikan entitas subjek warta (pemain/klub/tokoh/institusi) benar-benar terserap di naskah dan selaras dengan gambar.
   - *Kepatuhan Meta:* Caption <= 2200 karakter, hashtag 3–25 tag.
   - *Vonis Mutlak:* Hanya draf berstatus `QC_APPROVED` (skor >= 80, 0 cacat) yang diizinkan terbit. Jika audit gagal, penerbitan WAJIB dibatalkan seketika (*fail loudly*) dan memicu regenerasi gambar baru yang berkualitas tinggi, bukan membiarkan draf cacat lolos ke feed.

## 3A. Protokol Anti-Repetisi Gambar Mutlak (Zero-Duplicate Image Protocol)
Masalah repetisi visual (foto yang sama terbit berulang di berita berbeda) merusak reputasi media dan memicu penalti feed. Repetisi kerap terjadi akibat dua kegagalan arsitektur:

1. **PITFALL Late Locking (Penguncian Terlambat):**
   Mencatat URL foto ke tabel `used_images` HANYA setelah postingan sukses terbit ke Instagram memungkinkan cron job berikutnya (yang berjalan sebelum draf pertama terbit) menganggap foto tersebut masih kosong, lalu memakainya lagi untuk draf baru.
   - **FIX (Pre-Locking Seketika):** Kunci URL gambar seketika saat fungsi perakit draf (`createEditorialDraft` / `writer.js`) menyimpan data ke database. Pengecekan foto terpakai (`isImageUsed`) WAJIB memeriksa dua lapis: tabel `used_images` **dan** seluruh rekaman aktif di tabel `drafts`.

2. **PITFALL URL Variant & Transform Bypass:**
   Pengecekan string persis (`WHERE image_url = ?`) mudah dibobol oleh varian resize CDN atau query params berbeda dari gambar yang sama (misal: `.../SocialShare.max-600x600.webp` vs `.../SocialShare.width-1300.png`, atau `file:///path` vs `/path`).
   - **FIX (Normalisasi & Canonical Matching):** Seluruh URL gambar wajib dinormalisasi sebelum disimpan dan dicek: buang seluruh query parameter (`?width=...`), buang akhiran transformasi resize (`.max-600x600`, `.width-1300`), seragamkan prefiks path lokal (`file://`), dan lakukan pencocokan berbasis nama berkas dasar (*base filename*) di SQL (`OR image_url LIKE ?`).
6. **Graph API Publishing Flow (Staggered Upload, Edge Delay, & IPv4 Pinning):**
   - **PITFALL IPv6 Dual-Stack Blackhole (ETIMEDOUT / ENETUNREACH):** Node.js secara default mencoba menyelesaikan rute IPv6 lebih dulu (`autoSelectFamily: true`). Pada host cloud/VPS di mana rute IPv6 keluar tidak tersedia (`ENETUNREACH`), pemanggilan `axios` atau `fetch` ke Meta Graph API (`graph.instagram.com`) akan membeku 15–25 detik hingga timeout (`connect ETIMEDOUT 57.144.100.x:443`).
   - **FIX:** Kunci koneksi HTTP client ke protokol IPv4 secara eksplisit menggunakan `https.Agent({ family: 4, keepAlive: true })` (misal: `axios.defaults.httpsAgent = new https.Agent({ family: 4, keepAlive: true })`), sehingga koneksi langsung terarah ke antarmuka IPv4 tanpa hambatan.
   - **PITFALL Spam Penalti:** Mengunggah dan merakit carousel secara instan beruntun tanpa jeda akan dianggap serangan spam (DDoS) oleh mesin Instagram, memicu status *"Action Blocked"* atau *Banned*.
   - **FIX:** Jangan gunakan delay statis 3 detik — gunakan **container status polling** (`waitUntilFinished()`). Setelah upload tiap slide, poll `GET /{container_id}?fields=status_code` sampai `FINISHED` (atau `ERROR`). Ini lebih cepat DAN lebih reliable daripada tebak delay.
   - `POST /v18.0/...` (Slide 1) → poll `status_code=FINISHED`
   - `POST /v18.0/...` (Slide 2) → poll `status_code=FINISHED`
   - `POST /v18.0/...` (Carousel container) → poll `status_code=FINISHED`
   - **PITFALL Meta Subcode 2207027 (Media Belum Siap / Edge Propagation Delay):** Meskipun container carousel telah berstatus `FINISHED`, server edge Meta kerap mengalami latensi propagasi internal. Memanggil `POST /media_publish` seketika akan ditolak dengan error `OAuthException: code 9007, subcode 2207027 ("Media belum siap untuk menerbitkan, tunggu beberapa saat lagi")`.
   - **FIX:** Selalu beri jeda tenggang 3 detik setelah carousel container selesai (`FINISHED`), dan bungkus pemanggilan `POST /media_publish` dalam perulangan *retry* (hingga 5–6 percobaan dengan jeda 4 detik) khusus ketika mendeteksi `error_subcode === 2207027`.
   - `POST /v18.0/.../media_publish` (Terbitkan ke Feed).
   **Catatan:** Tetap berikan jeda minimal 1 detik antar API call sebagai courtesy rate limit, tapi jangan mengandalkan delay sebagai pengganti polling status.

## 4. Keamanan Token & Credential
- **Jangan simpan token di source code, config JSON, atau environment variable yang ter-log.** Simpan di file rahasia di luar repo (contoh: `C:/ProgramData/chronicle-secrets/ig-token`) dengan permission terbatas. Baca token dari file saat runtime.
- **Token 60 hari WAJIB dirotasi** — set reminder. Jika token pernah bocor (tercatat di chat, log, atau commit history), rotasi segera di Meta Developer Console.
- **Admin endpoint penyimpanan token:** sediakan endpoint admin yang menerima token baru, validasi format, simpan ke file rahasia, dan hanya kembalikan `{has_token: true/false}` — jangan pernah mengembalikan token itu sendiri via API.
- **Carousel slide count:** Instagram carousel menerima 2–10 slide. Validasi ini di level template creation (tolak template < 2 slide), bukan saat upload.
- **Caption snapshot immutability:** Setelah render/approve, caption yang ter-snapshot tidak boleh di-fallback ke draft yang bisa berubah. Gunakan `caption_snapshot` literal.

## 5. Publishing Safety (Human-in-the-Loop)
- **Pisahkan Approve dan Publish** — render boleh otomatis, tapi publish ke Instagram WAJIB menunggu approval eksplisit via endpoint terpisah.
- **State machine server-side:** DRAFT → RENDERED → APPROVED → PUBLISHING → PUBLISHED. Edit draft otomatis menginvalidasi approval (`invalidateForDraft()`).
  - **PITFALL Bentuk Respons & Status Check Endpoint Approve:** Endpoint persetujuan (`/api/admin/publications/:id/approve`) mengembalikan objek publikasi secara langsung (`{ id, status: 'APPROVED', ... }`), BUKAN objek `{ ok: true }`. Memeriksa `approveRes.ok` akan mengevaluasi ke `undefined` dan memicu error palsu. Selain itu, pemanggilan endpoint `/approve` pada publikasi yang sudah berstatus `APPROVED` akan ditolak dengan error *"Publication tidak dapat disetujui"*. Skrip alur WAJIB memeriksa status lokal (`checkRow.status === 'RENDERED'`) sebelum memanggil `/approve`, dan memverifikasi kesuksesan via `res.status === 'APPROVED'`.
- **Atomic publish claim & Pitfall Query Status:** Gunakan `UPDATE ... SET status='PUBLISHING' WHERE status='APPROVED'` untuk mencegah double-publish dari concurrent request.
  - **CRITICAL PITFALL:** Ketika worker mengklaim publikasi dan mengubah status menjadi `PUBLISHING`, fungsi pengunggah (`uploadToInstagram`) WAJIB menerima `status IN ('APPROVED', 'PUBLISHING')` atau langsung menerima objek publikasi yang sudah di-claim. Jika kueri SQL di dalam fungsi upload mencari `WHERE status='APPROVED'`, pemanggilan akan gagal dengan pesan *"Publication yang disetujui tidak ditemukan"*.
- **Windows PM2 Interpreter Mismatch:** Pada host Windows dengan virtualenv terpasang, menjalankan skrip Node di PM2 tanpa menentukan path interpreter eksplisit dapat menyebabkan PM2 salah mengeksekusi biner python sebagai wrapper, memicu crash `SyntaxError: Invalid or unexpected token (MZx)`. Selalu cantumkan path lengkap node pada `ecosystem.config.js` (contoh: `interpreter: 'C:/Users/Administrator/AppData/Local/hermes/node/node.exe'`).
- **Jangan pernah panggil endpoint publish atau Meta API saat testing** — uji alur penuh secara *dry-run* (Kurator -> Writer -> Visual Render -> Approve) dengan payload uji coba ber-ID unik, lalu verifikasi keberadaan berkas PNG di disk dan status `APPROVED`. Segera bersihkan data uji dari tabel database (`ig_publications` dan `drafts`) serta hapus berkas PNG sementara di cache.
- **PITFALL Nama Tabel SQLite Drafts:** Pada skema database CMS warta, tabel draft bernama `drafts`, BUKAN `ig_drafts` (berbeda dengan `ig_publications` dan `ig_metrics`). Menggunakan nama `ig_drafts` saat skrip uji coba melakukan kueri pembersihan atau inspeksi akan memicu `SqliteError: no such table: ig_drafts`.

## 6. Konten Carousel Editorial & Zero-Click Architecture
Konten carousel berita (The Chronicle Engine / The Global AI Chronicle) WAJIB bersifat mandiri, tuntas (Zero-Click Content), dan bergaya editorial premium — dilarang menggantung kalimat (...) atau memaksa audiens mengunjungi web untuk membaca lanjutannya.

- **Standar Visual:**
  - **Varian Warm Paper & Obsidian:** Warm Paper (`#F6F4EE`), Obsidian (`#111215`), aksen merah presisi (`#C5221F`), Newsreader serif masif, double hairline border sasis fisik.
  - **Varian Minimal Swiss Monochrome (Seputar AI 24/7 / @sputarai):** Kertas off-white bersih (`#FBFBFA`), tinta obsidian pekat (`#111214`), hairline sasis tipis, tipografi neo-grotesque masif (`Inter` 800/900 tight tracking -0.03em), indikator pulse dot solid tanpa pendaran warna. Memberikan kesan intelijen, objektif, dan instan. Gunakan penamaan komunikatif seperti **"SEPUTAR AI 24/7"** daripada istilah kaku "RADAR" saat mengelola akun publik seperti `@sputarai`.
- **Struktur 4 Slide Mandiri (Zero-Click):**
  - **Slide 1 (HOOK & COVER):** Headline langsung ke poin + Teks deskripsi singkat (deck) + Arahkan/Panah penunjuk geser lanjut.
    - **Fallback Visual (Hero Image) & Ekstraksi Foto Pers Asli:**
      - **Prioritas #1 (Ekstraksi og:image Sumber):** Jangan hanya mengandalkan pencarian foto stok (seperti Unsplash) yang tidak memiliki foto tokoh atau peristiwa nyata. Selalu lakukan HTTP fetch cepat ke tautan artikel sumber (`article.link`) untuk mengekstrak meta tag `<meta property="og:image">` atau `twitter:image`. Media jurnalistik (TechCrunch, The Verge, Reuters) selalu menyematkan foto pers resmi tokoh (seperti Barack Obama, Sam Altman) yang 100% sesuai konteks.
      - **Prioritas #2 (Pencarian Web Terbuka Entitas Spesifik):** Jika `og:image` kosong, cari foto pers di web terbuka menggunakan nama tokoh atau nama produk spesifik (misal `"${namedPerson} AI policy speech press"`) tanpa membatasi kueri hanya pada domain stok foto.
      - **Prioritas #3 (Vault Tematik Presisi):** Jika harus menggunakan foto vault lokal, pastikan temanya presisi (misal kategori `POLITICS_REGULATION` menampilkan gedung parlemen/sidang kebijakan formal, BUKAN ruang server atau robotika acak).
      - **PITFALL Gambar Kembar & Repetisi:** Seluruh foto yang pernah terbit WAJIB dicatat di tabel `used_images` SQLite dan dilarang keras digunakan kembali.
    - **Standar Baku Slide 1: Full-Bleed Magazine Cover (Rasio 4:5 Penuh, 1080×1350 px):**
      - **Sasis Full-Bleed Sinematik:** Foto dokumentasi pers asli memenuhi seluruh kanvas vertikal 4:5 secara utuh (`position: absolute; inset: 0; width: 1080px; height: 1350px; object-fit: cover; object-position: center 25%;`). DILARANG menggunakan bingkai boks foto terpotong kaku di tengah halaman yang memakan tempat dan memotong kepala/wajah figur.
      - **Cinematic Scrim (Dark Gradient Overlay):** Terapkan gradasi obsidian halus dari transparan di area atas (20–30%) menuju gelap pekat (`rgba(17, 18, 20, 0.88)` hingga `0.98`) di 40% area bawah. Wajah tokoh atau subjek utama di bagian atas tetap terang, hidup, dan dramatis, sementara teks di bagian bawah mendapatkan landasan kontras maksimal (WCAG AAA) yang anti-silau.
      - **Tipografi Sampul Majalah Berita Global (Time / Wired / Bloomberg):**
        - *Kicker:* Huruf kapital monospaced merah menyala (`#EF4444`) berjarak renggang, tersambung garis aksen horizontal.
        - *Headline Serif Broadsheet Masif (Ukuran 64px):* Font serif tebal putih bersih (`#FFFFFF`, 64px, line-height 1.12, letter-spacing -0.025em) dengan bayangan halus (`text-shadow: 0 4px 16px rgba(0,0,0,0.9)`). Judul wajib berskala besar dan commanding, memberikan wibawa layaknya tajuk utama halaman muka surat kabar internasional.
        - *Deck Summary:* Teks sans-serif modern berukuran 25–26px (`rgba(255, 255, 255, 0.94)`, line-height 1.52) yang nyaman dipindai kilat di layar smartphone.
        - *Pencantuman Tanggal Sumber Berita (Multi-Titik Transparan):* Tanggal publikasi dari media sumber WAJIB ditampilkan secara eksplisit pada Slide 1 di 3 titik:
          1. *Kolom Metadata Strip Bawah:* Menampilkan `TANGGAL RILIS: DD MMM YYYY • HH:MM WIB` di kolom tengah (bersanding dengan `SUMBER RESMI` dan `KLASIFIKASI`).
          2. *Subline Masthead Atas:* `PANTAUAN PERKEMBANGAN AI 24 JAM // DD MMM YYYY`.
          3. *Pill Kredit Foto Kanan Atas:* `FOTO // [SUMBER] • DD MMM YYYY` dengan efek frosted glass.
        - *Frosted Glass Metadata Strip:* Di bagian bawah sebelum footer, pasang kotak verifikasi 3 kolom (`SUMBER RESMI`, `TANGGAL RILIS`, `KLASIFIKASI`) dengan latar semi-transparan gelap (`rgba(0, 0, 0, 0.55)`, `backdrop-filter: blur(12px)`), border putih tipis, dan aksen garis vertikal merah di sisi kiri.
      - **Sasis Ganda Transparan:** Garis sasis fisik broadsheet (`.slide-frame-outer` & `.slide-frame-inner`) diubah menjadi putih semi-transparan (`rgba(255, 255, 255, 0.35)` dan `0.18`) agar identitas sasis fisik koran tetap tegas membingkai kanvas foto penuh.
  - **Slide 2 (INTI & VISUALISASI):** Visualisasi pendukung mutlak di atas (Blueprint/SVG) untuk mendukung deskripsi + Teks deskripsi inti warta.
  - **Slide 3 (LANJUTAN):** Lanjutan dari pembahasan / dampak (melanjutkan teks Slide 2).
  - **Slide 4 (CTA):** Murni penutup dan Call to Action (Ajakan Simpan/Follow).
    - **Header dan Subheader Dinamis:** Hindari label hardcoded seperti `BAGIAN 01 // 3 FAKTA KUNCI PERISTIWA` yang kaku. Hubungkan label (`chapterNum`) dan judul (`subheadVal`) secara dinamis ke role/slide index sehingga wajar saat berita berganti.
    - **Pitfall Teks "Tersangkut" (Hardcoded Fallback Value):** Jika teks di Slide 2 dan Slide 3 tidak mau berubah walau topik berganti, periksa file script algoritma AI fallback CMS (contoh: `content-cms.js`). Masalah biasanya terletak pada logic pengisian `fallbackValue()` di mana role `CONTEXT` dan `SIGNIFICANCE` diisi hardcoded string alih-alih mengekstraksi `source.summary` secara dinamis. Perbaiki *root cause* di script algoritmanya.
    - **Bahasa & Gaya Penulisan Lokal (Pasar Indonesia):** 
      - Wajib 100% Bahasa Indonesia alami, mengalir, dan berbobot jurnalisme investigatif. DILARANG menggunakan terjemahan kaku kata-per-kata atau regex replacement tempelan yang membocorkan bahasa asing.
      - **PITFALL Prompt Bahasa Lemah di Database:** Jika AI terus mengabaikan instruksi dan menghasilkan teks/JSON dalam bahasa Inggris (terutama saat menggunakan JSON Schema Strict), masalahnya ada pada aturan di *database template* CMS. Aturan `"language": "Bahasa Indonesia"` terlalu lemah. Wajib gunakan instruksi pelarangan tegas: `"DILARANG KERAS menyalin mentah-mentah teks sumber. Wajib diubah menjadi narasi cerita Bahasa Indonesia."`
      - **PITFALL Hardcoded Text Override pada Skrip CMS:** Jika model AI terbukti berhasil meracik teks Indonesia yang benar, tetapi hasil akhir yang tayang (seperti *caption*) kembali menjadi abstrak bahasa Inggris mentah, periksa skrip *publisher* (misal `daily-publisher-service.js` atau `content-cms.js`). Sering kali skrip *wrapper* memiliki baris kode *hardcoded* yang secara paksa menimpa (*override*) properti `content.caption` dengan teks aslinya. Perbaiki skrip agar mengutamakan hasil AI.
      - **Zero Fluff & To-The-Point (Dilarang Bertele-tele):** Dilarang keras menggunakan kalimat pembuka klise, dramatis, atau berbunga-bunga (seperti *"Kabar mengejutkan datang dari..."*, *"Langkah berani ini membuka mata publik..."*, *"Selama ini industri..."*). Wajib LANGSUNG ke inti: sebutkan subjek/institusi, nama spesifik sistem/model, mekanisme teknisnya, dan data/angka konkret terukur (persentase, biaya, waktu). Kalimat aktif, pendek, tegas, dan sarat informasi (Subjek - Predikat - Objek - Data).
      - **Format Tepat 2 Paragraf Padat:** DILARANG menggunakan format bullet points (`•`) pada Slide 2 dan Slide 3. Sajikan isi warta dalam format **Tepat 2 Paragraf Bercerita** yang padat data dan tuntas (masing-masing 2-3 kalimat lugas).
      - **Visualisasi Pendukung Slide Deskripsi (Slide 2 - Standar Blueprint SVG):** Wajib menyertakan elemen visual pendukung di Slide 2 (di antara kotak observasi dan narasi) untuk memecah kejenuhan teks (*visual breaker*) dan menghapus kekosongan ruang atas:
        - **PITFALL "Diagram 3 Kotak Teks Biasa":** Hanya menyajikan 3 kotak abu-abu teks polos dengan panah dinilai sebagai diagram murahan/malas yang menjatuhkan skor estetika.
        - **SOLUSI (Build Sendiri Technical Blueprint SVG):** WAJIB memprioritaskan perakitan **Infografis Skema Arsitektur Vektor SVG Murni** (kanvas 952×236px, stroke 1.5–2px, tanpa pendaran neon):
          1. *Header Blueprint:* Menampilkan nama skema teknis kapital + lencana tolok ukur/status di sisi kanan (misal: `AKURASI: 100% VALID` atau `EFISIENSI: 80X`).
          2. *Grid Blueprint Halus:* Latar belakang bertekstur grid teknis tipis (`rgba(17, 18, 20, 0.05)`).
          3. *Tiga Node Fungsional Berbobot:*
             - Node 01 (`01 // MASUKAN`): Ikon terminal/prompt, judul dataset, dan status masukan.
             - Node 02 (`02 // PROSES`): Focal point berbingkai aksen merah pekat, ikon microchip/neural, nama model pemroses, dan bilah meter telemetri operasional aktif.
             - Node 03 (`03 // KELUARAN`): Ikon shield centang verifikasi, hasil nyata capaian terobosan, dan status eksekusi. (Gunakan istilah bahasa Indonesia murni `03 // KELUARAN`, hindari kata asing seperti `OUTPUT`).
          4. *Konektor Bus Data:* Garis merah tebal dengan panah penunjuk alur linier.
          5. *Footer Metadata Telemetri:* 3 kolom data spesifikasi di bawah modul (`STATUS`, `ARSITEKTUR`, `DAMPAK`).
        - **Larangan Foto Acak Internet di Slide 2:** Jangan gunakan pencarian web foto acak untuk Slide 2 yang berisiko menampilkan foto eksekutif tak terkait dengan kepala terpotong atau salah konteks. Blueprint SVG yang di-generate langsung dari inti teknis warta menjamin 100% kohesif dan akurat.
      - **Kotak Observasi Seimbang (Observation Box):** Letakkan kotak observasi beraksen garis merah tebal di atas narasi Slide 2 dan Slide 3 (1 kalimat observasi padat, 10–12 kata). Pastikan isi teks di dalam kotak tidak mengulang kata label (hapus duplikasi prefiks `OBSERVASI:` atau `FOKUS:`).
      - **Deck Summary Slide 1:** Pastikan di bawah judul utama terdapat 1–2 kalimat ringkasan pengantar (*deck summary*) murni berbahasa Indonesia untuk menyajikan konteks seketika.
      - **Penebalan Visual (Visual Anchors):** Gunakan `<strong>...</strong>` pada maksimal 1 frasa kunci per paragraf agar pembaca yang membaca sekilas (*skimming*) langsung menangkap inti pesan tanpa merasa silau.
      - **PITFALL Garis Bawah (Underline) & Emphasis Berlebihan pada Narasi:** DILARANG KERAS menerapkan `text-decoration: underline` atau `border-bottom` pada teks narasi, serta dilarang membagi kalimat secara otomatis (misal split koma) untuk menebalkan klausul. Hal ini menyebabkan 60-70% teks tergarisbawahi dan terlihat berantakan (*visual clutter*). Teks narasi di Slide 2 dan 3 WAJIB bersih (*clean typography*).
      - **PITFALL Kanvas Top-Heavy (Kekosongan Vertikal di Bawah):** Pada kanvas vertikal 1080×1350 px, ukuran teks narasi yang terlalu kecil (<26px) dengan `flex` atas akan meninggalkan ruang kosong aneh di atas footer seolah ada gambar yang gagal dimuat. Gunakan ukuran font narasi 28px dengan `line-height: 1.65–1.7` dan distribusikan margin vertikal (`gap: 32px–36px`) agar kanvas terisi seimbang dan nyaman dibaca di smartphone.
      - **Kurasi Foto Hero Bersih & Anti-3D Cartoon:** Foto sampul WAJIB dokumentasi pers nyata atau fotografi konseptual teknologi beresolusi tinggi (lengan robot presisi di lab, wafer silikon semikonduktor, koridor server data center). DILARANG KERAS menggunakan foto render 3D kartun, meme, mainan/boneka, ilustrasi clipart, atau gambar ber-watermark komersial (filter out `plus.unsplash.com`, `premium_photo`, `shutterstock`, `gettyimages`). Hindari gambar artikel yang memuat banner teks promosi besar berbahasa Inggris atau logo vendor yang tidak relevan dengan topik.
    - **Pemenggalan Kalimat Aman:** Saat mengekstrak kalimat dari ringkasan berita, jika isi ringkasan sangat pendek (kurang dari 3 kalimat pendukung), jangan paksakan variabel kosong yang akan membuat layout *broken* atau tersangkut variabel lama. Siapkan satu klausul *fallback* redaksional elegan bergaya Indonesia yang tidak kaku.
    - **Filter Kosa Kata Asing di Judul:** Gunakan regex sederhana untuk mengganti frasa kaku bawaan mesin translasi dengan idiom lokal yang lebih natural (contoh: "How" / "Why" → "Cara", "Now everyone can" → "Kini Semua Orang Bisa", "puts on hold" → "Tunda", "due to" → "Gara-Gara").
    - **Konsistensi Identifier Role (Template vs Payload):** Pastikan role yang dikaitkan di template (`CONTEXT`, `SIGNIFICANCE`) cocok 100% dengan role yang dicek di dalam logika pemecah teks. Gunakan pencocokan majemuk jika ada varian nama role lama (`if (role === 'WHY_IT_MATTERS' || role === 'SIGNIFICANCE')`), agar format teks tetap bekerja walau sasis template pernah diubah namanya.
    - **Fallback Visual (Hero Image):** Selalu pasang *fallback* gambar latar (misal dari Unsplash) untuk Slide 1 (Hook/Cover) di logika perenderan jika artikel asli tidak memuat `image_url` (bernilai `null` atau kosong). Kanvas sampul berita tidak boleh kosong tanpa foto.
      - **PITFALL Substring Regex False Match pada Deteksi Kategori/Tema:**
        Mencari kata kunci pendek seperti `/app/i` tanpa batas kata `\b` memicu pencocokan palsu terhadap kata umum dalam ringkasan warta (misal: kata *"apply"*, *"approach"*, *"appeal"* terdeteksi sebagai aplikasi konsumen / `CONSUMER_MOBILE`). Akibatnya, warta riset sains murni (seperti Google AI / bioteknologi) salah diarahkan ke kategori ponsel/gadget. Selalu gunakan batas kata tegas (`/\bapp\b|\bapps\b/i`) dan sediakan kategori tematik sains (`SCIENCE_BIOLOGY`).
      - **PITFALL URL Gambar Mati (404 Not Found) pada Bank Kurasi Foto:**
        Menyimpan daftar URL foto statis tanpa probe verifikasi status `HTTP 200` berisiko tinggi menyebabkan gambar Slide 2 tidak muncul. Ketika Puppeteer memuat URL mati (404), rendering tetap berlanjut dan menghasilkan kotak abu-abu/putih kosong tanpa foto. Seluruh bank foto statis WAJIB diaudit berkala dan skrip pengunduh wajib memastikan status respons `200 OK` dengan tipe `image/*` sebelum menyematkannya ke payload draf.
      - **PITFALL Styling Slide 2 `object-fit: contain` vs `cover`:**
        Pada Slide 2, menggunakan `object-fit: contain` dengan latar belakang putih (`--bg-white`) dan padding menyebabkan foto kecil tampak seperti stiker mengambang yang terpotong. Gunakan `object-fit: cover` dengan posisi `center 25%` agar foto dokumentasi riset memenuhi kontainer secara padat dan elegan layaknya majalah editorial internasional (*Wired* / *Bloomberg*).
      - **PITFALL Foto Sampul Kembar/Duplikat:** Jangan gunakan pencarian statis yang selalu mengembalikan gambar yang sama (misal `findReferenceImage` yang mereturn foto ke-1 dari hasil Unsplash) untuk berita tanpa gambar asli. Hal ini membuat dua berita berbeda (seperti *paper* ArXiv) tampak seperti *postingan ganda/spam* di *feed* Instagram karena Slide 1-nya identik. **Selalu tambahkan pengacakan (random/offset) atau rotasi bank gambar** agar gambar *fallback* tidak pernah sama berturut-turut.
    - **Gaya Caption Instagram:** Buat caption lebih organik dan bergaya media berita lokal. Gunakan emoji relevan (🚨, 🔍), label sumber berita yang jelas, dan CTA yang persuasif (*"📌 Jangan lupa follow @sputarai agar tak tertinggal info AI terkini!"*), menghindari diksi kaku atau bahasa teknis (*analis industri*, *dikaji mendalam*) saat menangani fallback teks kosong.
    - **Banner Bawah Follow:** Jadikan banner hitam paling bawah sebagai zona murni follow akun (`@SPUTARAI` + maskot Inspektur Bebek + `IKUTI KABAR ➔`).
    - **Pitfall Kontras CSS Banner Bawah:** Jika latar belakang banner hitam (`#111214`), teks kicker wajib memakai putih transparan (`rgba(255, 255, 255, 0.65)`), jangan memanggil variabel warna gelap sasis yang membuat teks tenggelam (*black text on black background*).
- **Pantangan Anti-Slop Mutlak:**
  - Dilarang emoji sebagai ikon UI/UX (wajib pure inline SVG stroke 1.5–2px).
  - Dilarang teks gradasi warna-warni, badge kicker neon glow, border glow murahan, logo box melayang, dan kanvas kosong.
  - Dilarang teks terpotong menggantung dengan elipsis (...) pada narasi berita.
- **Caption & Atribusi Bersih:**
  - **Panjang Caption:** Pendek dan padat — hindari paragraf panjang yang melelahkan di layar HP. Cukup 1 judul aktif, 2–3 kalimat ringkasan inti, dan sumber asli.
  - **Pantangan Domain Internal:** DILARANG KERAS menyebut atau menyertakan domain hosting/tunnel internal (seperti `jajandigital` atau staging URL) pada caption maupun slide grafis. Selalu cantumkan langsung nama penerbit sumber resmi aslinya (`Sumber: TechCrunch AI`, `Sumber: OpenAI`, dsb).
  - **Isolasi Handle Akun:** Untuk akun publikasi khusus (seperti `@sputarai`), dilarang menyuntikkan tag/mention akun pribadi kurator (`@_bagas.spt`) ke dalam gambar atau caption publik. Jaga agar identitas tetap murni atas nama media publikasi tersebut.
  - **CTA Retensi Tegas (Wajib Simpan 24 Jam):** Pertegas instruksi di Slide 4 dan caption untuk **menyimpan postingan** sebagai arsip pemantauan 24 jam (*"📌 SIMPAN lembar ini agar tidak tertinggal perkembangan AI 24 jam"*). Metrik *save* dan *share* adalah pemicu utama distribusi algoritma Instagram 2026.
  - **Tagar:** Gunakan 4–6 tagar spesifik topik dan identitas media (`#SputarAI #KecerdasanBuatan #InovasiAI`).

## 6A. Tipe Konten 1 — Edukasi Gratis sebagai Pancingan Minat
Gunakan pola ini untuk akun edukasi yang monetisasinya berasal dari kelas, kursus, konsultasi, atau produk pengetahuan.

- **Prinsip strategis:** Konten edukasi/berita gratis bukan tujuan akhir, melainkan **mesin akuisisi dan pemantik rasa ingin tahu**. Konten membangun kesadaran masalah, kepercayaan, dan minat; produk berbayar menjual sistem belajar, urutan, pendampingan, latihan, alat, serta hasil yang lebih terarah.
- **Alur funnel:** `Masalah aktual/berita → insight gratis yang berguna → tunjukkan celah pengetahuan atau biaya salah keputusan → jembatani ke solusi terstruktur → CTA mengikuti kelas`.
- **Nilai gratis harus tetap utuh:** Jangan memakai umpan kosong, menahan fakta inti, atau membuat klaim menyesatkan. Audiens harus memperoleh satu hasil nyata dari setiap unggahan walau tidak membeli. Kelas berbayar menawarkan **kedalaman, struktur, percepatan, dan implementasi**, bukan sekadar jawaban yang sengaja disembunyikan.
- **Framing konten:** Ambil kejadian yang sedang dibicarakan audiens, jelaskan dampaknya bagi kehidupan atau keputusan mereka, lalu perlihatkan kemampuan apa yang perlu dikuasai agar mereka tidak hanya menjadi penonton berita.
- **CTA kontekstual:** Ajakan bergabung harus menjadi kelanjutan logis dari materi, bukan iklan tempelan. Contoh pola: `Kalau kamu ingin bisa menganalisis kasus seperti ini sendiri dengan kerangka yang runtut, pelajari modul/kelas [nama produk].`
- **Rasio komunikasi:** Dahulukan edukasi dan bukti kompetensi; promosi hadir setelah nilai diberikan. Jangan membuat setiap slide terasa seperti brosur penjualan.
- **Ukuran keberhasilan:** Pantau bukan hanya jangkauan, tetapi juga `save`, `share`, kunjungan profil, DM/kata kunci, klik halaman kelas, lead, dan konversi pembelian.
- **Segmentasi:** Bedakan audiens yang baru sadar masalah, mulai mempertimbangkan solusi, dan siap membeli. Hook berita cocok untuk tahap sadar; studi kasus/metode cocok untuk pertimbangan; bukti hasil, silabus, dan CTA kelas cocok untuk konversi.
- **Label internal:** Klasifikasikan pola ini sebagai **TIPE 1 — EDUCATION-LED COMMERCE**: edukasi gratis sebagai top-of-funnel, kelas sebagai produk inti.

Konsep strategi ini berasal dari observasi dan arahan Bagas Cihuy.

## 7. Monitoring & Analitik (Insights)
API yang sama dapat digunakan untuk memantau performa postingan dan metrik interaksi tanpa perlu masuk ke aplikasi.
- **Prosedur Verifikasi Status Terbit Live (Triangulasi 3 Titik):**
  Saat memeriksa apakah postingan warta sudah terbit ke Instagram:
  1. *Database Transaksi Lokal:* Kueri tabel `published_articles` dan `ig_publications` pada `data/db/chronicle.sqlite` (filter `status='PUBLISHED'`) untuk mencocokkan headline, article ID, dan IG media ID.
  2. *Meta Graph API Langsung:* Panggil `GET /{account_id}/media?fields=id,caption,permalink,timestamp` menggunakan token di `.chronicle-secrets/instagram-token` dan ID akun di `data/ig_config.json` guna memverifikasi postingan sudah live di server Instagram dan mengambil tautan `permalink` aktif.
  3. *Audit Tracker & Cron Telemetri:* Periksa `data/instant_dispatch_tracker.json` (`posts_today` rolling 24 jam) serta log eksekusi cron di `~/.hermes/cron/output/{job_id}/*.md` untuk melaporkan apakah kuota harian sedang jeda/penuh dan kapan jadwal otomatis berikutnya.
- **Prosedur Triage Cepat Saat Otomasi Tidak Mengunggah Konten Baru:**
  Ketika pengguna menanyakan ketiadaan postingan baru ("belum ada berita baru kah?"):
  1. *Hitung Kuota Rolling 24 Jam:* Baca `data/instant_dispatch_tracker.json`, hitung elemen `posts_today` yang `Date.now() - timestamp < 86400000`. Jika sudah 5, sistem tertahan oleh hard cap harian; hitung kapan entri tertua melampaui 24 jam untuk mengetahui jadwal slot terbuka kembali.
  2. *Periksa Log Scheduler Terakhir:* Baca `~/.hermes/cron/output/{job_id}/*.md` terbaru. Konfirmasi apakah output mencatat `🛑 Kuota harian terpenuhi (5/5)` atau jeda pengaman aktif (`Menunggu jeda pengaman`).
  3. *Simulasi Seleksi Gatekeeper:* Jalankan inspeksi independen tanpa menerbitkan:
     `node -e "const g=require('./scripts/editor-gatekeeper'); const fs=require('fs'); g.selectNextEditorialCandidate(JSON.parse(fs.readFileSync('./data/news_data.json')).articles).then(c=>console.log('Kandidat:', c?.article?.title, 'Skor:', c?.score));"`
     untuk memverifikasi sensor warta masih menangkap sinyal berbobot (skor >= 45) dan menampilkan kandidat teratas yang sedang menunggu antrean.
- **Tarik Daftar Postingan & Metrik Dasar:** Gunakan kueri GET ke `/{ig_account_id}/media?fields=id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,like_count,comments_count&limit=5`.
- **Thumbnail Handling:** Untuk tipe media video/reels, `media_url` mungkin tidak langsung merender gambar yang aman; gunakan fallback ke `thumbnail_url`.
- **Pitfall "Unsupported get request / Object does not exist" (ID & Token Mismatch):**
  Jika endpoint mengembalikan error *"Unsupported get request. Object with ID '...' does not exist, cannot be loaded due to missing permissions, or does not support this operation."*, penyebabnya adalah `account_id` pada konfigurasi tidak cocok dengan ID akun pemilik token akses yang terpasang, atau salah menggunakan domain host API:
  - **Identifikasi Prefix Token:** Token dengan awalan `IGAA...` atau `IG...` adalah **Instagram User Access Token** (wajib memanggil host `https://graph.instagram.com/v18.0/...`). Token ini akan ditolak dengan error `Invalid OAuth access token` jika dipanggil ke `graph.facebook.com`. Sebaliknya, token berawalan `EAAB...` adalah Meta Facebook System/Page Token.
  - **Diagnosa & Pemulihan Cepat:** Panggil `GET https://graph.instagram.com/me?fields=id,username,account_type&access_token=<TOKEN>`. Ambil nilai `id` aktual dari respons JSON (`2829...`), lalu perbarui file konfigurasi (`ig_config.json`) agar memakai `account_id` tersebut.
- **Pitfall Penghapusan Post (Delete Media):**
  Graph API Instagram (khususnya untuk User Access Token `IGAA...`) **TIDAK MENDUKUNG penghapusan media** via API (`DELETE /v18.0/{ig_media_id}`). Permintaan akan selalu ditolak dengan *"Unsupported delete request"*. Jangan membuang waktu mencoba menghapus atau menarik (undo) postingan yang salah menggunakan skrip; penghapusan WAJIB dilakukan secara manual dari aplikasi Instagram oleh pemilik akun.
- Gunakan data JSON kembalian tersebut untuk disuntikkan ke dalam Dasbor Admin (*Console-First UI*) agar pengguna bisa memantau *Like*, *Comment*, dan Tautan Publik secara *real-time* langsung dari server.

## 8. Arsitektur "CCTV Internet" Radar Pemantau 24/7
Untuk akun pemantau berkala yang beroperasi 24/7 (seperti media radar perkembangan AI global):
- **Full Spectrum Ingestion:** Jangan hanya mengandalkan 1 atau 2 feed lab besar. Gabungkan 4 spektrum:
  1. *Tier-1 Frontier Labs:* OpenAI, DeepMind, Google AI, NVIDIA, Microsoft Research, Meta AI, Stanford HAI, MIT.
  2. *Academic & Model Hubs:* ArXiv (cs.AI & cs.CL), Hugging Face Daily Papers API.
  3. *Fast Tech Wires:* Hacker News Algolia Real-time API (`query=AI&hitsPerPage=15`), TechCrunch AI, The Verge, Ars Technica.
  4. *Community Signals:* Reddit r/MachineLearning & r/LocalLLaMA.
- **Hemat Token & Zero LLM Overhead Saat Pemindaian:** Gunakan parser XML/RSS dan fetch API deterministik di latar belakang via daemon / scheduled task (`no_agent: true`). LLM hanya dipanggil saat merangkum draf yang dipilih kurator manusia, bukan saat proses crawling.
- **Deduplikasi Cerdas:** Gunakan hashing URL dan normalisasi string judul (`title.toLowerCase().replace(/[^a-z0-9]/g, '')`) untuk menyaring sindikasi berita ganda antar portal.
- **Setup Profil Instagram Akun Pemantau:**
  - *Bio:* Tulis ringkas, tanpa basa-basi, fokus pada peran pengawas 24/7 dan kurator resmi.
  - *Highlight Stories:* Pisahkan menjadi 4 pilar arsip: `RADAR 24/7` (breaking alerts), `FRONTIER` (rilis LLM/weights baru), `RISET` (paper ilmiah), dan `ARSIP` (laporan mingguan).

## 9. Model Publikasi: Terjadwal vs Event-Driven Instant Dispatcher
Ada dua pola operasional dalam mendistribusikan warta ke akun Instagram:
- **Pola Terjadwal Statis (Fixed Prime-Time Slots):**
  Menerbitkan warta pada jam-jam tetap harian (contoh: 07:30, 11:30, 14:30, 18:30, 21:30 WIB). Sangat cocok untuk ritme teratur dan menjaga konsistensi audiens.
- **Pola Event-Driven Instant Dispatcher (Asal Ada Berita Baru Langsung Post):**
  Saat prioritas beralih ke kecepatan pemantauan 24/7 di mana setiap ada warta rilis baru di dunia harus segera terbit tanpa menunggu jadwal kaku:
  1. *Interval Pengecekan Sensor:* Jalankan patroli CCTV tiap 15–20 menit (`*/20 * * * *`).
  2. *Deteksi & Deduplikasi Instan:* Bandingkan artikel terbaru dengan database `ig_publications`. Jika artikel belum pernah diterbitkan, picu alur render Puppeteer dan upload Meta API seketika. **Pastikan iterasi array membaca dari indeks ke-0 (paling baru)**; jika urutan loop salah, sistem akan menarik warta terlama dari dasar antrean yang menyebabkan audiens komplain.
  3. *Pagar Pengaman Algoritma (Anti-Spam & Burst Limiter):*
     - **Jeda Minimal Antar-Post (Cooldown):** WAJIB tetapkan jeda minimal 45–60 menit sejak postingan terakhir berhasil terbit. Jika lab merilis 3 artikel sekaligus, sistem harus mengantrekannya dengan jeda 45 menit, bukan menerbitkan serentak (mencegah penalti spam Meta).
     - **Hard Cap Harian:** Batasi maksimal **tepat 5 postingan per 24 jam** (dengan jeda minimal 45–60 menit). Melebihi 5 postingan dalam 24 jam memicu kanibalisasi jangkauan (*reach cannibalization*) dan *audience fatigue*.
     - **PITFALL Pacing Dispatcher & False "Fresh Breaking" Override (Dead Zone Lockup):** Mendefinisikan flag `isFreshBreaking` terlalu longgar (misal: usia artikel < 24 jam) menyebabkan interval jeda minimal di-bypass pada setiap run. Akibatnya, sistem menembakkan seluruh kuota harian (5/5) dalam hitungan menit di pagi hari, lalu terkunci dalam jeda *dorman* palsu (*"Kuota harian terpenuhi"*) selama belasan jam sepanjang siang hingga malam.
       - **FIX:** Batasi breaking override ketat hanya untuk artikel berusia < 2 jam DAN berskor editorial sangat tinggi (>= 85). Tetap tegakkan jeda minimum (minimal 30–45 menit untuk breaking, 90–120 menit untuk warta standar) agar jadwal posting terdistribusi merata sepanjang jam aktif (07:00–23:00 WIB).
     - **Prinsip Operasional Agen: Invariant Keberlangsungan Operasi Harian (Heartbeat Konten):** Saat agen diminta mengembangkan modul sekunder (seperti dasbor visualizer, animasi DAG, inspektor backend, atau refactoring UI), DILARANG KERAS menenggelamkan diri dalam iterasi UI hingga mengabaikan tugas pokok operasional penerbitan konten. Lakukan verifikasi kesehatan pipeline penerbitan secara berkala di sela-sela pengerjaan antarmuka.
     - **Mindset Kreator Multidimensi (Riset, Marketing, Branding):**
       - *Lensa Riset:* Cari benang merah (*The 'So What?'*), utamakan data primer terverifikasi, hindari sintesis dangkal dan klaim bombastis tanpa angka riil.
       - *Lensa Marketing (Swipe & Save Velocity):* Hook Slide 1 dipahami < 1 detik, konten mandiri tuntas (*Zero-Click Content*) yang membuat audiens merasa berhutang budi sehingga memicu tombol Simpan (Bookmark) dan Share.
       - *Lensa Branding (Wibawa Visual):* Jangan kaku pada satu dogma kaku. Tampung ragam referensi (Bento box, Data dossier, Modern broadsheet, Minimal tech) dengan tetap berpegang pada disiplin majalah fisik, palet warna terbatas, dan eliminasi total elemen AI slop (pendaran neon, badge melayang sintetis).
     - **PITFALL Dobel Upload (Filter Logika):** Jangan bergantung pada memori internal AI saat mengantre draf. Saat merancang `instant-news-dispatcher` atau skrip sejenis, urutannya MUTLAK: 1) Tarik daftar berita (terbaru di atas), 2) Query database riwayat tayang (`SELECT article_id FROM ig_publications WHERE status='PUBLISHED'`), 3) Buang berita yang sudah ada di database, 4) Ambil target [0] dari sisa list. Jangan gunakan indeks acak atau mem-bypass cache.
     - **Formula Target Pertumbuhan Followers Akun Baru:**
       - *Kombinasi 1-2 Punch:* Jadwalkan Reels harian (2 slot: 12:30 dan 19:30 WIB) sebagai mesin pembuka jangkauan (*top-of-funnel reach* ke non-followers) dipadukan dengan Carousel warta berbobot (maksimal 5 post/24 jam) sebagai mesin konversi pengunjung menjadi pengikut setia (*followers conversion*).
     - Simpan stempel waktu eksekusi pada tracker file lokal (`data/instant_dispatch_tracker.json`) untuk mempertahankan status lintas sesi reboot.
     - **Bypass Trigger Manual / Pengunggahan Uji (Force Upload):** Untuk menguji pipeline atau memicu postingan paksa saat batas kuota harian di tracker penuh atau jeda pengaman aktif, jalankan eksekusi dengan flag `--force` (`node scripts/instant-news-dispatcher.js --force`). Flag ini mem-bypass filter jeda tanpa merusak atau menghapus riwayat stempel waktu `posts_today` di file tracker, menjaga konsistensi audit log.
       - **PITFALL Menghapus Tracker Manual:** Mengosongkan tracker secara manual (`posts_today: []`) saat daemon PM2/cron aktif berisiko memicu spam bertubi-tubi karena daemon menganggap kuota kosong. Gunakan parameter `--force` pada pemanggilan manual ber-ID terisolasi alih-alih merusak berkas JSON tracker.

## 10. Sistem Notifikasi Instan Pengawas & Multi-Token Fallover
Ketika sistem beroperasi dalam mode otonom murni (auto-publish tanpa approval manusia di dashboard):
- **Notifikasi Setiap Postingan Berhasil:** Pengawas/kreator WAJIB langsung dikabari via Telegram seketika setelah postingan terbit di Instagram (`sendTelegramPostNotification`).
- **Muatan Pesan Notifikasi:**
  1. *Format Media:* Indikator warta carousel (`📰`) atau video Reels (`🎬`).
  2. *Judul & Penerbit Asli:* Menyebutkan headline aktif dan lab/sumber aslinya.
  3. *Tautan Langsung (Permalink IG):* Langsung cantumkan tautan URL Instagram aktif (`https://www.instagram.com/p/.../`) agar kreator tinggal klik untuk langsung melihat postingan yang baru tayang.
- **Sentralisasi Notifikasi ke Grup (Sterilisasi Chat Pribadi / DM):**
  - Dilarang keras meng-hardcode chat ID pribadi pengguna (`6276190957`), baik sebagai string tunggal (`DEFAULT_CHAT_ID`) maupun di dalam array ganda (`const DEFAULT_CHAT_IDS = ['6276190957', ...]`), pada skrip notifikasi atau penerbit otomatis mana pun (termasuk `publisher.js`, `telegram-notifier.js`, bot olahraga, dan warta). Notifikasi rutin yang menumpuk di chat pribadi mengotori riwayat obrolan instruksi.
  - Seluruh notifikasi penerbitan dan breaking alert otomatis MUTLAK dialirkan secara eksklusif ke grup terdedikasi (supergroup BAgent `-1004397580704`).
  - Skrip notifikasi wajib mengekstrak target chat ID secara bertingkat:
    1. Variabel lingkungan proses: `process.env.TELEGRAM_ALERT_CHAT_ID` atau `process.env.TELEGRAM_SIGNAL_CHAT_ID`.
    2. Ekstraksi langsung dari berkas `.env` (`~/.hermes/.env` atau profil terkait).
    3. Fallback baku eksklusif ke ID grup `-1004397580704`.
- **Arsitektur Multi-Token Failover:**
  - Jangan mengandalkan satu berkas environment tunggal (seperti profil pekerja) yang sewaktu-waktu dapat terbentur token kedaluwarsa (`401 Unauthorized`).
  - Skrip notifier WAJIB mengumpulkan daftar token dari seluruh profil (`~/.hermes/.env` dan `~/.hermes/profiles/*/.env`) lalu mencoba pengiriman secara berurutan hingga berhasil (`data.ok === true`).

## 11. Kontrak Otonom Penuh (Zero-Touch Autonomous Contract)
- **Pantangan Menunggu Approval Manual Saat Otonom Penuh:** Ketika pipeline atau perintah pengguna meminta pembuatan warta/konten ("seperti biasanya"), eksekusi WAJIB tuntas dari hulu ke hilir: **Deteksi Sinyal → Kurasi & Skor → Naskah AI → Render Puppeteer → Langsung Terbitkan ke Instagram → Kirim Laporan Permalink ke Telegram**.
- **Larangan Menggantung Proses & Konfirmasi Berulang:** DILARANG KERAS menghentikan alur di tahap render hanya untuk bertanya ke pengguna *"apakah ingin diterbitkan?"*. Memaksa pengguna mengetik perintah konfirmasi kedua ("langsung posting dong seperti biasanya") merusak ritme kerja otonom. Sekali pengguna memilih topik warta untuk diolah, tuntaskan otomatis hingga status terbit *live*.
- **Pitfall Kebocoran `\n\n` & Double-Escape Entitas HTML di Sasis Web:**
  - Saat payload JSON atau string literal diteruskan ke generator template HTML carousel (seperti `carousel.html`), karakter baris baru kerap tersimpan sebagai literal `\n\n`. Script parser WAJIB menormalkan baris (`(bodyVal || '').replace(/\\n/g, '\n')`) sebelum memecahnya ke tag `<p>`.
  - **Pitfall Kebocoran Karakter `\n` Literal di Caption Instagram:** Saat merakit caption via template literal atau JSON, karakter enter kerap ter-escape menjadi string literal `\n` atau `\\n`. Meta Graph API tidak mengonversi escape code ini, sehingga di aplikasi Instagram karakter `\n` tercetak mentah sebagai teks alih-alih baris baru. Solusi: seluruh pintu keluar caption (`ig-uploader.js`, `publication-workflow.js`, `content-cms.js`) WAJIB menormalkan string via `.replace(/\\r\\n/g, '\n').replace(/\\n/g, '\n').replace(/\/n/g, '\n')`.
  - Hindari pemanggilan ganda fungsi escape (`esc(captionTag)`) pada variabel yang sebelumnya sudah di-escape (`visualCaptionVal = esc(val)`), yang mengubah simbol `&` menjadi `&amp;amp;` dan tercetak secara visual sebagai `&AMP;` di kanvas render.
  - Lakukan inspeksi visual menggunakan perkakas analitik visual (`vision_analyze`) pada berkas PNG hasil render untuk memverifikasi tata letak, pemisahan paragraf, dan ketiadaan artefak teks sebelum sinyal terbit dikirim ke Instagram.

## 12. Identitas Maskot ("Brand Soul") & Anti-Slop Persona
- **Membedakan dari Ribuan Akun Bot Agregator:** Akun media otomatis sangat rentan terkesan dingin, kaku, dan membosankan jika hanya berisi teks berita formal.
- **Persona Inspektur Skeptis:** Gunakan maskot dengan karakter khas (seperti maskot *deadpan side-eye* "Inspektur Bebek") yang memposisikan akun sebagai penguji fakta independen yang dingin, skeptis terhadap klaim marketing lab AI yang berlebihan, dan berpegang pada bukti riil.
- **Penempatan Visual:** Terapkan maskot pada:
  - Foto profil resmi akun (crop melingkar dengan sasis monokrom).
  - Stempel inspeksi redaksi di Slide 4 carousel bersanding dengan tanda tangan kurator.
  - Header portal web pemantau. Kehadiran maskot ini memperkuat identitas merek (*brand recall*) dan meningkatkan *engagement/shares* tanpa merusak wibawa desain minimalis.

## 13. Ketahanan Sistem Latar Belakang & Kekebalan Sesi (`/new`)
Saat membangun automasi penerbitan jangka panjang yang dikendalikan pengguna lewat antarmuka chat (seperti Telegram):
- **Isolasi Siklus Hidup Chat vs Daemon OS:** Perintah pembersihan konteks seperti `/new` HANYA mengosongkan sesi percakapan LLM saat itu. Schedulers (`jobs.json`) dan proses PM2 beroperasi di layer sistem operasi host.
- **Kunci Konfigurasi PM2:** Jalankan `pm2 save` setelah mendaftarkan service agar seluruh proses tersimpan di `dump.pm2` dan otomatis bangkit kembali (*auto-respawn*) saat mesin server/RDP reboot.
- **Dua Faktor Penghenti Riil:**
  1. *Token Kedaluwarsa:* Token Long-Lived Meta User Access Token memiliki masa aktif ~60 hari; wajib disediakan alur pembaruan token sebelum kedaluwarsa.
  2. *Reboot Total Host:* Diatasi dengan `pm2 save` dan scheduled watchdog script deterministik (`no_agent: true`).

## 14. Viral AI Video Radar & Integrasi Pengunduh Headless
Selain warta teks resmi, sistem pemantau dapat diperluas untuk menangkap dan mengolah tren video viral di internet (TikTok / Reels / YouTube Shorts):
- **Deteksi Sumber Tren:** Pantau sub-komunitas Reddit berkategori tinggi (`r/singularity`, `r/ChatGPT` dengan filter upvote > 1.000) dan kreator penguji AI di YouTube Shorts/TikTok.
- **Pipeline Unduh Headless:** Host dilengkapi biner `yt-dlp` dan `ffmpeg`. Gunakan `yt-dlp` untuk mengunduh berkas video resolusi tertinggi tanpa perantara browser visual.
- **Mindset Kurasi Video Autentik (Anti-Voiceover AI):**
  - **Prioritas Rekaman Primer:** Cari rekaman mentah/primer asli langsung dari peneliti atau engineer (layar coding, uji lab robotika, percobaan mandiri). Jangan gunakan kompilasi warta generik atau narasi sintetis buatan yang hambar.
  - **Pertahankan Audio Asli:** 100% audio lingkungan/asli rekaman wajib dibiarkan hidup (suara mekanik, reaksi peneliti, ketikan keyboard). Suara natural memberi nyawa dan daya sebar viral jauh lebih tinggi dibanding voiceover AI.
  - **Editing Efisien:** Pemotongan klip (*trimming*) hanya dilakukan bila perlu untuk membuang momen hening (*dead air*) agar alur video padat.
- **Sasis Video Format Vertikal (9:16 Minimal Swiss via FFmpeg):**
  Untuk menghindari penalti *unoriginal content* dari algoritma Meta, jangan pernah mengunggah video mentah tanpa nilai tambah editorial. Gunakan filter grafis FFmpeg:
  - Format 1080×1920 vertikal dengan kanvas obsidian pekat (`#0E0F12`).
  - *Top Header Pill:* `SEPUTAR AI // @SPUTARAI` (font tebal putih dengan boks hitam semi-transparan `boxcolor=black@0.7:boxborderw=14`).
  - *Headline Hook:* Judul tebal 2 baris di atas frame video agar penonton langsung menangkap inti warta.
  - *Center Frame:* Klip video asli diposisikan seimbang di tengah tanpa terpotong atau terdistorsi melar (`scale=1080:-2,pad=1080:1920:0:(1920-ih)/2:color=#0E0F12`).
  - *Bottom Attribution & Follow CTA:* `Dokumentasi / Cr: @kreator_asli` dan `Follow @sputarai untuk warta 24 jam`.
- **Manajemen Ruang Penyimpanan RDP (Auto-Cleaner 3 Hari):** Berkas MP4 mentah berukuran puluhan MB dapat memenuhi harddisk server. Pasang skrip pembersih berkala (`cleanup_cache(max_age_days=3)`) yang otomatis menghapus berkas raw di folder cache yang berusia lebih dari 72 jam setelah selesai diproses.
- **Pitfall Datacenter CDN & YouTube Extraction:**
  - Koneksi langsung ke Google Video CDN sering mengalami timeout pada IP datacenter RDP jika tanpa JS runtime. Selalu sertakan flag runtime Node pada `yt-dlp` (`--js-runtimes node:"<PATH_TO_NODE_EXE>"`) atau prioritaskan link langsung / platform terbuka seperti TikTok, Reddit, dan fast edge CDN.

## 15. Hirarki Kontrol Absolut (Telegram vs RDP Server)
- **Telegram sebagai Command Center:** Pengguna mengendalikan agen 100% dari antarmuka Telegram.
- **Pembersihan Balon Progres Tool Call (`cleanup_progress`):** Saat agen menjalankan rantai *tools* (pembacaan berkas, inspeksi, perintah shell, render), antarmuka Telegram memancarkan balon status progres intermediet. Balon ini menjadi *clutter* visual yang mengotori riwayat chat jika dibiarkan setelah tugas selesai. WAJIB aktifkan `hermes config set display.platforms.telegram.cleanup_progress true` agar setiap balon status progres otomatis dihapus via `deleteMessage` segera setelah respon final berhasil dikirim.
- **RDP sebagai Server Buta (Headless-like):** RDP Windows hanyalah mesin pelaksana (backend server). Jangan pernah menyuruh pengguna untuk membuka link `127.0.0.1`, `localhost`, atau mengecek tampilan di browser RDP sendiri.
- **Pitfall Pelaporan UI/UX:** Jika merakit purwarupa dasbor, HTML, atau merender *screenshot*, agen WAJIB menggunakan perkakas tangkapan layar di server (seperti `browser_exec` atau `puppeteer`) dan langsung mengirimkan berkas/gambarnya ke antarmuka Telegram pengguna via format `MEDIA:...`.

## 16. Telemetri Terpadu Eksternal & Internal (Home, Login & Admin)
Ketika sistem memiliki banyak background jobs dan daemons yang berjalan di RDP:
- **Ketersediaan Publik Tanpa Login:** Sediakan ringkasan telemetri yang bisa diinspeksi dari luar (halaman login atau beranda publik) via modal popup transparan tanpa perlu membocorkan token/rahasia internal.
- **Data Minimum Telemetri:**
  1. *Resource Host:* RAM terpakai / total GB dan Uptime.
  2. *Status PM2:* Layanan Online vs Mati beserta penggunaan memori aktual.
  3. *Jadwal Cronjob:* Status aktif/jeda, interval ekspresi, waktu eksekusi terakhir, jadwal lari berikutnya, serta ringkasan error terakhir.
- **Efisiensi Beban Terowongan (Tunnel Pruning):** Selalu matikan background tunnel sementara (seperti Cloudflare Quick Tunnel untuk arena uji atau dev server yang tidak lagi dipakai publik) agar tidak membebani bandwidth dan memori server jangka panjang.

## 17. Pola Orkestrasi Multi-Agent Otonom (5-Agent Pipeline)
Untuk menjalankan operasional media berita terkurasi (seperti `@sputarai`) secara otonom tanpa sentuhan manual harian, rantai kerja dipecah menjadi 5 peran agent diskrit dengan batas tanggung jawab dan kontrak data yang ketat:
1. **Agent 1: Kurator (Sensor & Signal Ingestion CCTV 24/7):**
   - Memantau spektrum sensor resmi 24/7 (Tier-1 Frontier Labs, ArXiv, Hugging Face, Fast Wires) secara deterministik tanpa LLM crawling overhead.
   - Menggunakan hashing canonical link permanen (`radar-${hash}`) agar ID warta deterministik dan tidak bergeser saat ada warta baru.
2. **Agent 2: Gatekeeper (Keputusan & Kurasi Visual Kontekstual):**
   - **Anti-Duplikasi Mutlak:** Memeriksa canonical link, ID warta, dan kemiripan semantik judul/topik terhadap tabel `published_articles` di SQLite agar warta yang sama dari sumber berbeda tidak pernah terbit berulang.
   - **Scoring Mutu Editorial:** Menilai bobot berita (Tier-1 Lab +35, Riset Ilmiah +30, Freshness < 12 jam +25, penalti spam/podcast/low-effort -35). Status: `ACCEPTED` jika skor >= 45.
   - **Kurasi Visual Kontekstual:** Menyeleksi gambar tajam dan relevan dengan entitas subjek warta. Memverifikasi seluruh calon foto terhadap tabel `used_images` di SQLite sehingga foto yang sama TIDAK PERNAH terpakai berulang.
3. **Agent 3: Writer (Redaksi AI & Editorial Konten):**
   - Mengolah artikel terpilih dari Gatekeeper menjadi naskah 4 slide mandiri (Zero-Click) via 9router (`ag/gemini-3.8-flash`).
   - Menegakkan gaya bahasa 100% Bahasa Indonesia alami, format tepat 2 paragraf padat, eliminasi AI slop, dan caption pendek ber-CTA retensi.
4. **Agent 4: Visual (Headless Render & Asset Builder):**
   - Merakit visual teknis pendukung (Blueprint SVG murni di Slide 2) dan menyematkan foto hero unik terkurasi.
   - Merender aset grafis 1080x1350 via Puppeteer dengan siklus *hit-and-destroy* demi efisiensi RAM server, lalu menyimpan slide ke cache publikasi.
5. **Agent 5: Publisher (Pemberi Kuota & Eksekutor Distribusi):**
   - Mengatur ritme publikasi agar mematuhi aturan algoritma Instagram (cooldown jeda minimal 120 menit, kuota keras maksimal 5 postingan warta per 24 jam).
   - Mengeksekusi pengunggahan via Meta Graph API dengan status polling (`waitUntilFinished`), mencatat status `PUBLISHED` di database transaksi, merekam riwayat permanen ke `published_articles` & `used_images`, dan mengirim laporan permalink aktif ke Telegram.

- **PITFALL ID Bergeser & Duplikat Re-Index:** Jangan pernah menomori warta dengan indeks array sekuensial (`radar-0001`). Begitu warta baru masuk di urutan atas, seluruh penomoran bergeser dan warta lama akan diposting ulang oleh database. Wajib gunakan ID permanen berbasis hash canonical URL.
- **PITFALL Foto Berulang & Meleset Konteks (Subjek Utama Headline):** Jangan mengandalkan vault foto statis kecil (6 foto) tanpa riwayat permanen. Seluruh foto yang pernah terbit WAJIB dicatat di tabel `used_images` SQLite dan dilarang keras digunakan kembali. Pencarian foto warta harus menyertakan entitas spesifik (misal nama lab + AI computing) dan memfilter kata kunci di luar konteks (gedung/menara/mobil). **Ketika berita memuat banyak nama tokoh (debat/polemik), ekstraksi nama subjek WAJIB ditautkan langsung ke entitas yang menjadi aktor utama di Headline** (contoh: jika headline berfokus pada sikap Jensen Huang / Nvidia, dilarang meloloskan foto Sam Altman atau figur pendukung yang hanya disebut sekilas di ringkasan).
- **PITFALL Silent Fallback Teks Mentah / Template Kosong (Nilai Bobot 0):** Ketika pemanggilan LLM/redaksi AI gagal atau timeout, DILARANG KERAS membuat *silent fallback* yang menyalin ringkasan RSS bahasa Inggris mentah ke Slide 2 atau menyuntikkan teks template generik ke Slide 3. Ini meloloskan postingan cacat berbobot 0 ke akun live. Pipeline WAJIB melempar error dan membatalkan publikasi (*fail loudly*) jika naskah jurnalisme 2 paragraf padat belum berhasil ter-generate secara utuh.
- **PITFALL Timeout Inferensi Redaksi & Sinkronisasi Kredensial Latar Belakang:** Model penalaran AI yang merangkum JSON 4 slide membutuhkan waktu 25–45 detik. Gunakan batas timeout minimal 90 detik dengan 2x auto-retry. Pastikan berkas token rahasia (`~/.chronicle-secrets/router-token`) selalu tersinkronisasi dengan environment shell agar proses daemon (PM2/cron) yang berjalan tanpa variabel environment sesi tetap dapat melakukan autentikasi ke 9router tanpa terbentur 401 Unauthorized.
- **PITFALL Hardcoded Default Hero Image:** Jangan pernah menyimpan URL foto hardcoded di fungsi pembangun draf (seperti URL robot biru default). URL foto yang telah divalidasi oleh Gatekeeper WAJIB dikunci mutlak ke field `hero_image` agar tidak pernah ter-override oleh foto default lama.

### Prosedur Uji Mandiri Pipeline (Dry-Run E2E Simulation)
Saat menguji kesiapan 5 agent, jangan pernah menguji dengan akun IG live atau menghapus data riwayat tayang:
1. **Payload Uji Baru:** Buat artikel simulasi bertanda unik (`test-art-${Date.now()}`).
2. **Uji Beruntun 5 Tahap:**
   - *Kurator:* Ambil 1 feed sensor hidup untuk membuktikan parser XML/Atom aktif dan menghasilkan ID berbasis hash permanen.
   - *Gatekeeper:* Jalankan evaluasi scoring (ambang batas >= 45), pastikan anti-duplikasi judul/URL aktif, dan verifikasi foto hero tidak terdaftar di tabel `used_images`.
   - *Writer:* Kirim payload uji ke 9router (`cms.createEditorialDraft`), verifikasi kepatuhan 4 slide dan eliminasi kata terlarang ('RADAR').
   - *Visual:* Panggil endpoint render (`POST /api/admin/render/:draftId`) dan verifikasi ke-4 file fisik PNG terbit di `public/ig-cache/` dengan ukuran valid (>100 KB).
   - *Publisher:* Panggil `POST /api/admin/publications/:id/approve` dan pastikan status bertransisi menjadi `APPROVED` siap publish tanpa memanggil endpoint final publish ke Meta API.
3. **Pembersihan Bersih (Clean Teardown):** Hapus rekaman uji dari tabel `ig_publications` dan `drafts` (perhatikan nama tabel: `drafts`, bukan `ig_drafts`), serta hapus 4 file PNG sementara dari `public/ig-cache/`.

### Pemilihan Sensor Frontier & Penanganan Timeout IP Cloud
- Tidak semua RSS lab dapat diakses langsung dari IP datacenter/cloud (misal: beberapa repositori universitas seperti BAIR kerap mengalami connect timeout 10 detik).
- **Sensor Lab Frontier Terverifikasi & Cepat:**
  - `https://machinelearning.apple.com/rss.xml` (Apple ML Research)
  - `https://qwenlm.github.io/blog/index.xml` (Qwen Team Blog / Alibaba)
  - `https://aws.amazon.com/blogs/machine-learning/feed/` (AWS AI/ML Blog)
  - `https://github.blog/category/ai-and-ml/feed/` (GitHub AI & ML Blog)
  - `https://deepmind.google/blog/rss.xml` (Google DeepMind)
  - `https://huggingface.co/blog/feed.xml` (Hugging Face Blog)

## 18. Media Olahraga & Event-Driven Radar (SputarBall Architecture)
Untuk media berbasis pertandingan olahraga (seperti sepak bola internasional dan Timnas Indonesia) dengan target audiens Gen Z:
- **Pola Pemantauan Matchday & Acara Langsung:**
  - Tidak pasif menunggu artikel rilis; antisipasi jadwal laga dan respons seketika saat peluit akhir berbunyi (*Full Time / FT*, skor akhir, *comeback* sensasional, drama VAR, atau gol penentu).
  - Sensor khusus untuk peristiwa nasional (Timnas Indonesia & pemain diaspora abroad) diberikan bobot prioritas tertinggi (+50 skor).
- **Pembagian Tugas Machine Learning (ML) vs Generative AI (LLM):**
  - **Machine Learning Microservice (Python / PyTorch - Port 3086):** Menggunakan `sentence-transformers/all-MiniLM-L6-v2` untuk mengubah teks warta menjadi embeddings vektor 384-dimensi, menghitung kemiripan kosinus, konsensus lintas media, dan momentum tren Google Trends ID secara lokal di CPU tanpa biaya token API. Menghasilkan skor kelayakan warta (0-100).
  - **Generative AI (LLM via 9router):** Hanya menerima sinyal yang sudah lolos seleksi ML untuk meracik naskah kreatif gaya Gen Z, headline provokatif, dan format slide JSON.
- **Sub-Agent Content Director (Adaptasi Format & Variasi Slide):**
  - Bertindak sebagai pengarah konten yang menentukan format tayangan secara fleksibel:
    1. *Match Result - Poster Tunggal (1 Slide):* Untuk hasil pertandingan berbobot visual masif. Menampilkan skor besar (54px neon box), kicker tebal, dan foto aksi pemain penentu.
    2. *Match Result - 2 Slide Recap (`MATCH_RECAP_2SLIDE`):*
       - **Rasionalitas Strategis 2 Slide:** Diterapkan khusus untuk hasil pertandingan (*Full Time score*). Audiens sepak bola di Instagram mencari kepuasan instan: melihat skor akhir dan pencetak gol di Slide 1, lalu menggeser satu kali ke Slide 2 untuk melihat zona debat/ledek rival (*Banter Zone*) dan ajakan repost ke Instagram Story. Format ini menghasilkan *completion rate* / *swipe-through rate* di atas 90%, memicu algoritma Meta untuk melipatgandakan distribusi ke tab *Explore*.
    3. *Warta Harian / Transfer / Timnas (4 Slide Penuh):* Ulasan lengkap 4 slide (Slide 1 Hook, Slide 2 Fakta Kunci + Foto Aksi, Slide 3 Konteks/Dampak, Slide 4 CTA Simpan) dengan aturan wajib: **Slide ke-2 WAJIB memiliki foto aksi pendukung (Supporting Media Box)** di samping ringkasan fakta.
- **Suite Elemen Transparan & Cutout Pemain (`/home/ubuntu/shared-services/content-elements/`):**
  - SputarBall dapat memanfaatkan SDK `index.js` untuk mengekstrak pemain bintang menjadi PNG cutout transparan berbayang (`removeBackground`) dan menyematkan bendera negara/klub bulat (`generateFlag`) langsung ke dalam template `carousel.html`.
- **Evolusi Frekuensi & Kuota Harian SputarBall (Maksimal 20 Post/24 Jam):**
  - Kuota operasi ditingkatkan hingga maksimal **20 postingan per 24 jam** dengan jeda antrean minimum **10 menit**.
  - Dilengkapi mesin pembelajaran berkelanjutan (`learning-engine.js`) yang memetakan jam tayang relevan WIB, resonansi hook visual, dan palet warna berdasarkan skor interaksi.
  - Kewajiban Atribusi Sumber Resmi: Setiap konten wajib mencantumkan nama sumber (Guardian, Reuters, Sky Sports, AFC) pada badge Slide 1, Slide 4, dan baris khusus di caption Instagram.
  - **Standar Desain Grafis Sepak Bola Modern (Benchmark Cretivox, 433, & Bleacher Report):**
  - **PANTANGAN SERIF KLASIK & STADION KOSONG:** Menampilkan stadion kosong tanpa pemain atau menggunakan font serif koran jadul (*Newsreader*) dinilai hambar/membosankan (skor 4/10) untuk audiens olahraga modern.
  - **Benchmark Estetika Cretivox Editorial (Kultur & Visual Kelas Atas):**
    - *Full-Bleed Contextual Photography:* Foto aksi atau situasi nyata memenuhi seluruh kanvas vertikal 1080×1350 px tanpa border/kotak kaku, memanfaatkan natural vignette/gradasi gelap halus agar foto tidak tampak kusam.
    - *Tipografi Kontras 2-Tier (Plus Jakarta Sans):* Headline wajib memadukan dua karakter kontras yang berirama:
      - Baris 1: **Ultra-Bold 900** huruf kapital sebagai *hook* pembuka (`"KONDISI BANG JAY DISOROT JELANG TURNAMEN,"`).
      - Baris 2: **Light / Regular 400** dengan aksen miring (*italic neon lime*) pada kata pamungkas (`"GARUDA BAKAL PUSING?"`).
    - *Circular Inset Detail Frame (Cretivox Signature):* Di kuadran kanan atas, sematkan bingkai lingkaran berdiameter 270–310px bergaris putih bersih (5px) dan drop shadow lembut (`0 16px 40px rgba(0,0,0,0.75)`) untuk menampilkan ekspresi pemain atau aksi lapangan secara intim.
    - **Cover Minimalis & Zero Clutter (Mandat Mas Bagas):** Hapus scoreboard pill di kiri atas, hapus paragraf ringkasan/deck di bawah judul, dan hapus footer kredit/tombol geser pada Slide 1. Headline masif (64–68px, line-height 1.08, letter-spacing -0.035em) menjadi jangkar visual tunggal di atas kanvas bersih.
    - **Reposisi Identitas Brand Kicker di Atas Headline:** Tag nama akun (`● SPUTARBALL // 24/7`, font mono 15px, warna aksen kontras) diposisikan tepat **di atas headline judul utama** di dalam wrapper bawah, bukan terasing di sudut footer bawah.
    - **Letak Teks & Zona Aman Bawah (Bottom Safe Zone Clearance):**
      - Teks headline dan brand kicker DILARANG menempel di dasar kanvas ($y > 1140\text{px}$).
      - Tempatkan blok teks terangkat di level paha/bola ($y \approx 780\text{px} - 1120\text{px}$, dengan `padding-bottom: 210px–230px`).
      - Ruang kosong $210\text{px} - 230\text{px}$ di dasar kanvas berfungsi mutlak sebagai *safe zone* agar judul tidak tertutup overlay caption, sound disc, atau bilah navigasi Instagram Reels & TikTok Photos Mode.
      - Area M ($y < 750\text{px}$) tetap 100% steril dan terang untuk wajah, dada, nomor jersey, dan lambang kebanggaan.
    - *Layout 2-Tier Slide Isi:* 1/3 atas untuk headline observasi tegas (tanya/jawab) dan 1-2 baris narasi padat tanpa bullet points berantakan; 2/3 bawah untuk visual aksi sinematik.
  - **Fokus Utama: Foto Aksi Pemain Asli (Player Hero Centerpiece):** Wajib menggunakan foto aksi atau *close-up* pemain asli dengan ekspresi intens, selebrasi, atau determinasi tinggi di lapangan (Christian Pulisic, Haaland, Jay Idzes, Paes). Pertahankan pencahayaan kulit dan wajah pemain secara 100% natural — DILARANG menyuntikkan silauan/pendaran warna buatan (*ambient glow / radial color blur*) di area wajah atau leher pemain yang membuat foto tampak artifisial.
  - **Standar Resolusi Tinggi (HD) & Perburuan Foto Jernih (Anti-Buram):**
    - *Haram Thumbnail:* Jangan pernah menggunakan gambar hasil kompresi web (nama file memuat `thumb`, `_1265_711`, `quality(30)`, atau file < 90 KB) karena akan pecah dan buram saat direntangkan ke 1080×1350 px.
    - *Auto Un-crop Master Kamera:* Sistem ekstraksi gambar wajib membongkar URL crop/cache portal berita untuk menarik berkas master kamera aslinya (misal: Kompas membuang `/crops/.../1200x800/` menjadi `/data/photo/...`; Antara membuang `/cache/1200x800/`; Goal.com menaikkan `width=2400`).
    - *Browser Headless HD Hunter:* Gunakan Puppeteer dengan kueri `imagesize-large` tanpa watermark untuk memburu foto atlet beresolusi $\ge 1200\text{px}$ jika feed RSS hanya menyajikan gambar berkualitas rendah.
  - **Arsitektur SputarBall Photo Vault (Galeri Kurasi HD, Kompresi Ganda & Rekomendasi Owner):**
    - Sediakan landing page kurasi foto sepak bola (`/galeri-bola/`) dengan arsitektur penyimpanan ganda (*dual-storage*): pratinjau WebP super ringan (20–45 KB) untuk rendering web sekejap mata, dipadukan dengan tombol unduh master kamera pers asli Full HD/4K (400 KB s/d 2.5 MB).
    - *Live Tracking Status:* Menandai stok foto secara otomatis dengan badge hijau `SUDAH TAYANG` (lengkap dengan tautan langsung ke postingan IG/TikTok) vs badge amber `BELUM DIPOSTING`.
    - *Owner Recommendation Feedback Loop:* Tombol rekomendasi 1-klik (`is_recommended = 1`) di kartu pemain menghubungkan preferensi kurasi pengguna langsung ke mesin `gatekeeper.js` & `subagent-controller.js`, memberikan prioritas tertinggi pada berita terkait pemain tersebut untuk segera diproduksi menjadi materi warta berikutnya.
    - *Auto-Updating per Match Signal:* Skrip pemantau (`match-photo-watcher.js`) memindai sinyal skor laga usai (Barca, Timnas, Madrid, Milan, dll.) secara berkala dan otomatis mengunggah foto aksi bintang pertandingan terbaru ke galeri.
  - **Estetika Visual Sinematik (Kalibrasi Kontras & Saturasi):** Terapkan filter kontras (1.18) dan saturasi (1.12) pada template foto agar warna jersey klub, ekspresi pemain, dan sorotan lampu stadion keluar tajam dan dramatis (seperti foto selebrasi di bawah hujan), membedakannya dari foto datar biasa.
  - **Desain Bersih & Full-Bleed Tanpa Bingkai Tepi:** DILARANG memasang garis stroke pembatas luar (*outer frame border*) atau ornamen siku (*crosshair reticles*) di sekeliling tepian kanvas. Format media olahraga Instagram wajib 100% *full-bleed* menyentuh tepi layar.
  - **Slide 1 Minimalis & Proporsional:** Hapus kotak/tabel telemetri di bagian bawah Slide 1. Gunakan judul besar (*Bebas Neue*, 86px) dan teks deskripsi/deck berukuran padat (**20px**, line-height 1.48) agar tidak memakan kanvas. Berikan pergeseran posisi foto (`translateY(35px) scale(1.05)`) agar kepala pemain tidak terpotong atau tertutup bar skor atas.
  - **Tipografi Athletic Display Masif (Heavyweight Condensed):** Gunakan font display olahraga berenergi tinggi (*Bebas Neue*, *Anton*, ukuran 86-92px, line-height 0.94, huruf kapital penuh). Beri warna aksen menyala (*electric lime / neon green* `#00FF87` atau *fiery red* `#FF1744`) pada 1-2 kata kunci paling nendang (contoh: *"SANGAT GACOR!"*, *"COMEBACK GILA!"*).
- **Standar Redaksi "Langsung Ke Poinnya" (Benchmark: Fabrizio Romano & 433):**
  - **Zero Fluff (Tanpa Basa-Basi):** Dilarang keras memakai kalimat pembuka klise (*"Pada laga sengit tadi malam..."*, *"Sebuah pertandingan yang..."*, *"Di balik kemenangan..."*).
  - **Slide 1:** Judul langsung menembak rekor paling gila, angka skor, atau momen dramatis (maks 10–12 kata) + deck 1 kalimat tajam menusuk.
  - **Slide 2:** Poin aksi kunci 1 baris yang padat (nama pemain bintang + aksi spesifik + angka konkret).
  - **Slide 4 & Caption Instagram:** Format ala Fabrizio Romano:
    1. *Hook* huruf kapital berisi fakta gila / rekor pecah di baris pertama (misal: *"33 GOL DALAM 7 LAGA! ABSOLUTE CINEMA."*).
    2. Poin-poin fakta 1 baris padat per pemain.
    3. Pertanyaan debat interaktif penutup (*"Siapa Man of the Match menurut lu malam ini?"*).
    4. Atribusi sumber resmi berita (*"Sumber: [Nama Sumber]"*).
- **Mandat Visibilitas Subjek Utama (Anti-Tertutup Teks & Scrim):**
  - "Kalau menampilkan pemain, pemain itu harus kelihatan dan jangan sampai ketutup!"
  - **Doktrin Area M & Pembatasan Ketinggian Gradasi Hitam (Arahan Mas Bagas):**
    - Area tengah kanvas (*Area M*, dari $y = 0$ s/d $y \approx 880\text{px}$) dikhususkan untuk tubuh dan aksi subjek: kepala, wajah, dada, nomor punggung, dan lambang kebanggaan wajib 100% steril dari bayangan gradasi hitam (`background: transparent`).
    - Gradasi hitam bawah (`hero-fade-scrim`) hanya boleh aktif dari sepertiga bawah kanvas ($y \ge 65\%$ atau $y \ge 880\text{px}$) khusus sebagai alas kontras teks judul utama dan brand kicker ("cukup segitu jangan sampai tengah"). Dilarang membiarkan gradasi hitam merayap naik ke tengah kanvas hingga menggelapkan tubuh pemain.
  - **Face & Action Clearance Zone:** Pada kanvas 1080×1350 px, area vertikal `y = 140px` s/d `y = 680px` dikunci steril khusus kepala, wajah, dan aksi pemain. Wadah teks headline hanya boleh menempati area bawah (`y >= 680px`).
  - **Text Intrusion Veto:** Sistem QC mendeteksi baris piksel teks; jika teks headline merangsek naik ke `y < 620px` (menutupi dagu/wajah pemain), draf langsung **DIVETO / DITOLAK**.
  - **Anti-Drowning Check:** Kecerahan di zona wajah pemain wajib terjaga (`luminance >= 20`). Dilarang gradasi gelap (*fade scrim*) ditarik terlalu tinggi hingga mematikan ekspresi wajah pemain menjadi siluet hitam pekat (`luminance < 18` dan `std < 14`).
  - **Kalibrasi Deteksi Teks pada Jersey Putih/Terang (Anti-False-Positive QC):**
    - Atlet yang mengenakan jersey putih (misal jersey tandang Timnas Erspo, Real Madrid, Inggris) memancarkan piksel putih solid ($R>225, G>225, B>225$) yang dapat salah dideteksi sebagai huruf judul headline jika hanya mengandalkan ambang warna murni.
    - Detektor intrusi teks pada engine QC wajib mensyaratkan bahwa piksel teks didampingi oleh bayangan latar belakang gelap (scrim/shadow dengan luminansi $<65$) serta memiliki pola garis huruf horizontal tipis khas tipografi, sehingga area jersey putih pemain tidak memicu veto keliru.
- **Mandat Kesesuaian Tokoh Berita & Foto Visual (Anti-Salah Orang):**
  - "Pastikan juga orang yang ada di topik berita itu sesuai dengan pemilihan gambarnya."
  - **Verifikasi Token Nama pada Foto Sumber:** Foto bawaan feed RSS atau `og:image` HANYA digunakan jika URL/slug terbukti memuat token nama pemain/pelatih yang diberitakan. Jika URL feed hanya memuat logo klub, gambar stadion, atau pemain lawan, foto feed tersebut WAJIB ditolak.
  - **Web Hunter Prioritas Nama Pemain:** Sistem memprioritaskan perburuan foto aksi/selebrasi spesifik nama atlet: `"${entity}" celebration match action high resolution iconic -alamy -getty -shutterstock -watermark`.
  - **Doktrin Brankas Netral (Anti-Salah Orang Fallback):** Jika pencarian web gagal atau offline, sistem DILARANG KERAS mengambil foto pemain lain dari arsip lokal (misal berita Jay Idzes memunculkan Haaland). Fallback otomatis dialihkan ke atmosfer stadion megah atau lapangan netral (`stadium_epic.jpg`, `camp_nou_match.jpg`).
  - **Audit QC Cross-Player Mismatch Detector (Lapisan 1D):** Si Pengawas memindai nama tokoh berita terhadap URL/nama berkas gambar. Jika berita membahas Pemain A, namun berkas foto terdeteksi merujuk ke Pemain B, draf langsung DIVETO / DITOLAK (penalti 35 poin).
- **Siklus Pembelajaran Mandiri & Auto-Repair Draf Ditolak QC (Continuous Self-Healing):**
  - Draf yang tidak lolos QC WAJIB dianalisis akar penyebabnya dan diperbaiki jika peristiwanya masih segar (< 24 jam) sebagai sarana pembelajaran sistem.
  - **Eliminasi False-Positive Kata Slang:** Dilarang mengklasifikasikan kata slang emosional ("bantai", "pesta gol") pada warta opini/retoris non-pertandingan sebagai klaim skor palsu. Uji skor konkret hanya berlaku untuk format `MATCH_RECAP` atau klaim status `FT` eksplisit.
  - **Pengarsipan Draf Basi (Archived Stale):** Draf prediksi atau preview pertandingan yang laganya sudah selesai dan hasil resminya sudah tayang wajib dialihkan ke status `ARCHIVED_STALE`, bukan diterbitkan sebagai berita usang.
- **Ekspansi Multi-Platform: Setup Otomasi TikTok & Distribusi Serentak (Cross-Posting Instagram & TikTok):**
  - SputarBall memperluas distribusi postingan secara serentak (*dual-channel cross-posting*) ke Instagram (`@sputarball`) dan TikTok (`@sputarball` / `@gufron`) untuk format Photo Mode / Carousel 4 slide.
  - **Mandat Distribusi Serentak (Bareng):** Setiap draf warta sepak bola yang lolos QC diterbitkan berbarengan. Diorkestrasikan di `publisher.js` dan `subagent-controller.js`: suksesnya publikasi Instagram seketika memicu `publishToTikTok(draft.id)`. Jika terjadi kendala jaringan di salah satu platform, platform lainnya tetap terbit (*fault-tolerant*), tercatat di tabel SQLite masing-masing (`publications` vs `tiktok_publications`), dan laporan Telegram menyertakan tautan aktif dari kedua platform.
  - **PITFALL QR Scan Risk Engine & Solusi Export Session Cookies JSON:**
    - Scan QR code login TikTok di server VPS kerap diblokir oleh Risk Engine TikTok (*"network error"* / *loading terus saat tekan Otorisasikan*) karena disparitas IP (IP Datacenter Linux VPS vs IP residensial seluler HP).
    - **SOLUSI 100% ANDAL:** Ekspor berkas cookies JSON dari browser PC yang sudah login menggunakan ekstensi Cookie-Editor (`sessionid`, `sessionid_ss`, `sid_tt`, `ttwid`, `odin_tt`, `msToken`). Sanitasi field untuk Puppeteer (`sameSite: 'None'/'Lax'/'Strict'`, mapping `expirationDate` -> `expires`), lalu injeksikan via `page.setCookie()`. Sesi langsung terotentikasi penuh di TikTok Studio.
  - **Protokol Penambahan Audio/Lagu Latar Kontekstual (TikTok Studio Sound Engine):**
    - **Karakteristik Platform:** Meta Graph API mengunci penambahan audio pada format Carousel foto (audio hanya sah via API untuk Reels video atau edit manual di aplikasi HP). Sebaliknya, TikTok Studio mengizinkan penambahan lagu resmi/komersial langsung pada Photo Mode (Carousel foto).
    - **PANTANGAN LAGU FORMAL/KEBANGSAAN KAKU:** Dilarang keras memasang lagu kebangsaan atau orkestra formal yang kaku (seperti *Indonesia Raya* orkestra) untuk konten sepak bola di TikTok karena merusak kenyamanan audiens dan tidak sesuai kultur algoritma FYP.
    - **Kultur Audio FYP Sepak Bola (3 Kategori Utama):**
      1. *Brazilian Phonk / Montagem (Slowed / Bass Boosted):* Kueri `"montagem"` atau `"brazilian phonk"` untuk duel fisik sengit, selebrasi gol dingin, atau bursa transfer tegang.
      2. *Jedag-Jedug (JJ) & Breakbeat Indo:* Kueri `"breakbeat"` atau `"jedag jedug"` untuk aksi gacor pemain Timnas, momen kemenangan dramatis, atau warta santai audiens lokal.
      3. *Tab "Favorites" & Native "For You":* Jika pengguna mem-bookmark sound tertentu di aplikasi HP, prioritaskan dari tab Favorites; fallback menggunakan trek teratas dari tab rekomendasi "For You".
    - **PITFALL Hashtag/DraftEditor Overlay Swallowing Clicks:** Mengetik judul dan deskripsi sebelum memilih lagu menyebabkan editor DraftEditor dan dropdown autocomplete hashtag (`#`) menutupi kontainer, sehingga klik pada tombol `+ Add sound` tertelan atau gagal memicu modal.
    - **FIX Urutan Eksekusi & Siklus Submit Mutlak di Puppeteer:**
      1. Beralih ke tab Photos dan unggah berkas PNG slide (`input[type="file"][multiple]`).
      2. **Buka menu Sounds (`+ Add sound`) SEBELUM menyentuh atau memfokuskan form teks apa pun.**
      3. Ketikkan kueri sound tren (`montagem`, `phonk`, `breakbeat`, `jedag jedug`), tekan Enter, dan tunggu hasil pencarian (3–4 detik).
      4. Klik tombol `"Use"` pada trek pertama via element handle (`await useBtn.click()`), tunggu 2–3 detik hingga piringan hitam di preview ponsel berputar.
      5. Baru kemudian ketik Judul (Title) dan Deskripsi (Caption).
      6. **Tutup Overlay & Native Post Click:** Tekan Escape untuk menutup popup autocomplete hashtag, gulir seluruh kontainer ke dasar (`window.scrollTo(0, document.body.scrollHeight)`), lalu klik tombol "Post" via Puppeteer native click (`await postBtnHandle.click()`). JANGAN gunakan DOM `btn.click()` di dalam `page.evaluate()` karena React synthetic event TikTok kerap menelan bare DOM clicks tanpa mengeksekusi submission.
      7. **Siklus Lifecycle Publikasi & Verifikasi URL:**
         - Setelah tombol Post diklik, tunggu 8–10 detik. TikTok Studio tidak memunculkan modal popup, melainkan me-redirect halaman ke `/tiktokstudio/content` (Manage Posts).
         - **Status Moderasi Otomatis:** Saat pertama mendarat di Manage Posts, status post baru biasanya `⚠️ Content under review` dan privasi `🔒 Only me`. Ini adalah evaluasi AI TikTok standar (memakan waktu 60–120 detik) sebelum otomatis beralih menjadi status publik (`Everyone`).
         - **Ekstraksi Permalink Publik:** Ambil tautan publik langsung dari anchor cell postingan teratas (`a[href*="/video/"]` atau selector kelas `components_PostInfoCell_a`), yang menghasilkan URL permanen: `https://www.tiktok.com/@<username>/video/<post_id>`. Simpan post ID dan URL ini ke database SQLite `tiktok_publications`.
    - **Format Caption Khusus TikTok (Super Ringkas 100–140 Karakter - Zero Fluff):**
      - DILARANG menduplikasi caption panjang Instagram ke TikTok karena paragraf panjang akan menutupi seluruh layar ponsel di mode foto (*Photos Mode clutter*).
      - Susun caption TikTok super ringkas (maksimal 100–140 karakter):
        1. Baris 1: Headline warta / hook lugas.
        2. Baris 2: CTA singkat pancingan komentar (*"Gimana tanggapan lu?"*).
        3. Baris 3: 3–4 hashtag relevan (`#sputarball #beritabola #(klub/timnas) #fyp`).
    - **Protokol Publikasi Batch TikTok & Jeda Acak Organik (Random Delay Multi-Push):**
      - Saat menerbitkan batch postingan ke TikTok (misal 5 post berturut-turut), WAJIB menerapkan jeda acak organik (20–45 detik) antar-sesi browser headless Puppeteer. Dilarang melakukan upload beruntun tanpa jeda (*burst spam*) guna menghindari deteksi bot dan rate limit dari Risk Engine TikTok.
    - **Sistem Pembelajaran Multi-Dimensi & Rekomendasi Pintar Upload Konten (TikTok Analytics & Smart Recommender):**
      - *Mekanisme Telemetri Riil Tanpa API:* Mengambil tayangan riil, suka, komentar, dan permalink langsung dari TikTok Studio (`/tiktokstudio/content`) menggunakan Puppeteer dengan sesi cookie terinjeksi.
      - *Evaluasi 4 Pilar Kuantitatif:*
        1. **Pilar Visual (Visual Performance Index):** Membandingkan tipe foto (`MATCH_ACTION` duel dinamis lapangan, `CELEBRATION`, `PORTRAIT_REACTIONS`). Terbukti foto aksi duel dinamis mencatatkan engagement tertinggi (6.02%) dan rata-rata tayangan 89.5 views, menahan penonton di 2 detik pertama (slide 1).
        2. **Pilar Topik (Topic Resonance):** Memetakan entitas (Premier League, La Liga, Timnas Indonesia). Timnas Indonesia membukukan rasio interaksi tertinggi (11.63% peak), sementara klub Eropa memimpin akumulasi total tayangan.
        3. **Pilar Gaya Penulisan (Copywriting & Hook):** Membandingkan formula judul (`DRAMATIC_SCORELINE` dengan angka skor bantai/comeback, `EMOTIONAL_EXCLAMATION` kata seru "Waduh!"/"King Indo!", `QUESTION_CHALLENGE`, dan `DIRECT_FACTUAL`). Caption super ringkas (100–130 karakter) terbukti menghasilkan engagement 5.54% (vs 3.33% caption panjang) karena menjaga layar Photos Mode tetap bersih dari tutupan teks.
        4. **Pilar Waktu (Temporal & View Velocity):** Menghitung laju tayangan per jam ($\Delta \text{Views} / \Delta \text{Jam}$) dan memetakan 4 Jendela Jam Emas WIB:
           - *Pagi (06:45–08:30 WIB) // 1.30x:* Recap hasil laga semalam & breakfast news.
           - *Siang (11:45–13:30 WIB) // 1.40x:* Rehat makan siang to-the-point.
           - *Sore (16:30–17:45 WIB) // 1.45x:* Pulang aktivitas & preview match malam.
           - *Malam Emas (19:15–21:45 WIB) // 1.75x:* Prime time santai malam, interaksi komentar dan perdebatan paling aktif.
           - *Golden Rule Distribusi:* Unggah 15–30 menit sebelum jam puncak agar algoritma mengindeks konten tepat saat gelombang audiens masuk.
      - *Preskripsi Rekomendasi Cerdas Otomatis (`scripts/tiktok-smart-recommender.js`):* Menghitung status jam aktif saat ini, menentukan target jendela upload berikutnya (*Next Best Slot*), menyusun formula judul & topik prioritas, serta merekomendasikan aset foto resolusi tinggi yang belum tayang dari Photo Vault.
      - *Integrasi Gatekeeper & Pipeline:* Gatekeeper memberikan bonus prioritas (+10 poin saat jam prime time, +15 poin pada topik viral terbukti).
      - *Dasbor Publik Terintegrasi:* Ditampilkan pada landing page `/galeri-bola/` bertema *light mode*, 100% bebas emoji, menampilkan kartu preskripsi, 4 kartu jendela jam ramai, dan matriks pembelajaran 3 kolom.
- **Slide 2 Media Box (Foto Pendukung Wajib untuk Posting Harian):**
  - Pada kanvas Slide 2, sertakan boks foto aksi kedua (`.s2-media-box`, tinggi 330px, border semi-transparan, gradasi bawah gelap, dan lencana teks) yang memuat foto selebrasi atau aksi lapangan yang berbeda dari Slide 1.
- **Karakter Audiens Gen Z & Formula Repost-Worthy (Slide Penutup Story Trigger):**
  - Audiens Gen Z membagikan konten ke Instagram Story didorong oleh kebanggaan (*flexing* kemenangan klub/idola), debat taktik, atau sindiran antarsuporter (*banter culture*).
  - Bahasa naskah tidak boleh formal birokratis; wajib menggunakan istilah kultur sepak bola populer yang luwes dan hidup (*"Comeback Gila"*, *"Masterclass"*, *"Mode Bantai"*, *"Gacor Parah"*).
  - Di slide penutup (Slide 2 untuk format 2-slide, atau Slide 4 untuk format 4-slide), sediakan kartu ajakan bertindak yang tegas (*"BAGIKAN KE STORY LU // BANTER ZONE"*) dengan *border* kontras tinggi menyala (`rgba(0, 255, 135, 0.4)` + box shadow pendar halus) yang menyeimbangkan banner follow agar memicu retensi dan repost masif.
- **Sub-Agent Pengontrol Frekuensi Tinggi (Max Delay < 30 Menit):**
  - Mode *high-velocity event-driven* mengoperasikan sub-agent patroli tiap 15 menit melalui daemon/cron internal, memproses event langsung begitu pertandingan usai tanpa terhambat kuota harian statis.
- **PITFALL Foto Ber-Watermark Agensi Stok (Anti-Watermark Hunter Mandiri):**
  - Mengambil foto asal dari web seringkali menjaring foto stock ber-watermark agensi (seperti Getty Images, Alamy, Shutterstock, iStock). Hal ini dinilai sangat buruk (skor 1/10) dan merusak kredibilitas media.
  - **SOLUSI (Anti-Watermark & High-Res Filtering):**
    1. *Blacklist Domain:* Buang tautan yang mengandung kata kunci `alamy`, `gettyimages`, `shutterstock`, `istockphoto`, `dreamstime`, `123rf`, `watermark`.
    2. *Negative Keywords DuckDuckGo:* Suntikkan operator negatif: `"${entity}" match action high resolution -watermark -alamy -getty -shutterstock`.
    3. *Filter Kualitas Biner (HEAD Probe):* Tolak gambar berukuran < 40 KB dan resolusi lebar < 800px.
    4. *Anti-Duplikasi:* Simpan URL yang sudah terpakai di tabel `used_images` SQLite agar tidak terjadi repetisi visual.
- **Sub-Agent Quality Control (QC Inspector Gate):**
  - Sebelum publikasi dijalankan, wajib diaudit oleh sub-agent QC:
    1. Validasi geometri biner IHDR PNG: tepat 1080x1350 px pada setiap slide.
    2. Ukuran berkas wajar (35 KB s/d 8 MB per slide).
    3. Untuk format 4-slide, verifikasi keberadaan foto pendukung di Slide 2.
    4. Integritas copywriting: panjang headline (10-120 karakter), bebas artefak prompt markdown (`**`, `##`, ````), dan kepatuhan caption (maks 2200 karakter).
    5. Hanya status `QC_APPROVED` yang diizinkan memicu publikasi Meta Graph API.
- **PITFALL Same-Origin Block & 401 Redirect pada Panggilan Render Internal (Reverse Proxy / Privacy Boundary Gate):**
  - Skrip internal Node.js yang memanggil endpoint lokal `POST http://127.0.0.1:PORT/api/admin/render/...` tanpa header `Origin` akan ditolak dengan `403 Same-origin request required` jika reverse proxy menerapkan filter CSRF/Origin ketat.
  - Selain itu, ketika Puppeteer mengakses `http://127.0.0.1:PORT/carousel.html?render=1`, jika template `/carousel.html` tidak didaftarkan di daftar publik (`PUBLIC`) atau tidak mengecualikan IP loopback, middleware autentikasi (seperti `privacy-boundary.js`) akan me-redirect Puppeteer dengan status `303` ke halaman login (`/private/login`). Akibatnya, Puppeteer mengalami timeout dengan pesan galat `Error: Waiting for selector .ig-slide-1 failed`.
  - **FIX:** 
    1. Middleware reverse proxy WAJIB memeriksa apakah alamat IP pemanggil adalah loopback (`127.0.0.1` atau `::1` atau `::ffff:127.0.0.1`). Jika berasal dari loopback, izinkan akses ke `/carousel.html` dan `/api/admin/*` melintas tanpa memaksakan sesi cookie browser.
    2. Daftarkan `/carousel.html` secara eksplisit ke dalam himpunan sumber daya publik (`PUBLIC`).
    3. Di sisi skrip pemanggil internal (seperti `instant-news-dispatcher.js`), selalu sertakan header `Origin: https://<DOMAIN_RESMI>` dan `x-admin-pin` sebagai pertahanan berlapis.