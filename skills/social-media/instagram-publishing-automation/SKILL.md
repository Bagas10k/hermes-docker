---
name: instagram-publishing-automation
description: Use when automating Instagram posts via Meta Graph API.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
related_skills:
  - seo-expert
  - content-intelligence
  - tiktok-content-extraction
  - news-editorial-copywriting
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
2. **Pre-download External Images Server-Side:**
   Puppeteer yang me-load `http://127.0.0.1/carousel.html` akan GAGAL memuat gambar dari domain eksternal (misal `https://news.mit.edu/...`) karena CORS/mixed-content. Solusi: sebelum launch browser, download semua image field ke `ig-cache/` lokal via `fetch()` server-side, lalu ganti URL di payload menjadi `http://127.0.0.1:{PORT}/ig-cache/hero_{draftId}_{fieldId}.jpg`. Ini menjamin gambar termuat 100%.
3. **Wait for Images + Fonts Before Screenshot:**
   Setelah `waitForSelector('.ig-slide-1')` dan `document.fonts.ready`, WAJIB tambahkan `Promise.all([...document.querySelectorAll('img')].map(img => img.complete ? resolve() : new Promise(onload/onerror/timeout)))`. Tanpa ini, screenshot akan menangkap placeholder kosong — file size ~89KB vs ~986KB ketika gambar benar-benar termuat.
4. **Hit & Destroy Browser (RAM Resilience):**
   Gunakan Puppeteer untuk mengambil *screenshot* selektor `.slide`. RDP Windows memori terbatas (8GB); pastikan memanggil `browser.close()` secara sinkron secepatnya setelah *buffer* gambar selesai dibuat. Dilarang membiarkan Puppeteer *standby* di memori. Tambahkan `args: ['--no-sandbox']` pada launch options.
 5. **Graph API Publishing Flow (Staggered Upload):**
   **PITFALL:** Mengunggah dan merakit carousel secara instan beruntun tanpa jeda akan dianggap serangan spam (DDoS) oleh mesin Instagram, memicu status *"Action Blocked"* atau *Banned*.
   **FIX:** Jangan gunakan delay statis 3 detik — gunakan **container status polling** (`waitUntilFinished()`). Setelah upload tiap slide, poll `GET /{container_id}?fields=status_code` sampai `FINISHED` (atau `ERROR`). Ini lebih cepat DAN lebih reliable daripada tebak delay.
   - `POST /v18.0/...` (Slide 1) → poll `status_code=FINISHED`
   - `POST /v18.0/...` (Slide 2) → poll `status_code=FINISHED`
   - `POST /v18.0/...` (Carousel container) → poll `status_code=FINISHED`
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
- **Atomic publish claim & Pitfall Query Status:** Gunakan `UPDATE ... SET status='PUBLISHING' WHERE status='APPROVED'` untuk mencegah double-publish dari concurrent request.
  - **CRITICAL PITFALL:** Ketika worker mengklaim publikasi dan mengubah status menjadi `PUBLISHING`, fungsi pengunggah (`uploadToInstagram`) WAJIB menerima `status IN ('APPROVED', 'PUBLISHING')` atau langsung menerima objek publikasi yang sudah di-claim. Jika kueri SQL di dalam fungsi upload mencari `WHERE status='APPROVED'`, pemanggilan akan gagal dengan pesan *"Publication yang disetujui tidak ditemukan"*.
- **Windows PM2 Interpreter Mismatch:** Pada host Windows dengan virtualenv terpasang, menjalankan skrip Node di PM2 tanpa menentukan path interpreter eksplisit dapat menyebabkan PM2 salah mengeksekusi biner python sebagai wrapper, memicu crash `SyntaxError: Invalid or unexpected token (MZx)`. Selalu cantumkan path lengkap node pada `ecosystem.config.js` (contoh: `interpreter: 'C:/Users/Administrator/AppData/Local/hermes/node/node.exe'`).
- **Jangan pernah panggil endpoint publish atau Meta API saat testing** — gunakan mock/stub untuk Graph API calls di test suite.

## 6. Konten Carousel Editorial & Zero-Click Architecture
Konten carousel berita (The Chronicle Engine / The Global AI Chronicle) WAJIB bersifat mandiri, tuntas (Zero-Click Content), dan bergaya editorial premium — dilarang menggantung kalimat (...) atau memaksa audiens mengunjungi web untuk membaca lanjutannya.

- **Standar Visual:**
  - **Varian Warm Paper & Obsidian:** Warm Paper (`#F6F4EE`), Obsidian (`#111215`), aksen merah presisi (`#C5221F`), Newsreader serif masif, double hairline border sasis fisik.
  - **Varian Minimal Swiss Monochrome (Seputar AI 24/7 / @sputarai):** Kertas off-white bersih (`#FBFBFA`), tinta obsidian pekat (`#111214`), hairline sasis tipis, tipografi neo-grotesque masif (`Inter` 800/900 tight tracking -0.03em), indikator pulse dot solid tanpa pendaran warna. Memberikan kesan intelijen, objektif, dan instan. Gunakan penamaan komunikatif seperti **"SEPUTAR AI 24/7"** daripada istilah kaku "RADAR" saat mengelola akun publik seperti `@sputarai`.
- **Struktur 4 Slide Mandiri (Zero-Click):**
  - **Slide 1 (HOOK & COVER):** Headline langsung ke poin + Teks deskripsi singkat (deck) + Arahkan/Panah penunjuk geser lanjut.
    - **Fallback Visual (Hero Image):** Selalu pasang fallback gambar latar (misal dari Unsplash) untuk Slide 1 jika artikel asli tidak memuat `image_url`. **PITFALL Gambar Kembar:** Jangan gunakan keyword pencarian generik seperti "AI" atau "Technology" yang statis. Sertakan fungsi acak/hash atau gunakan judul artikel sebagai seed pencarian gambar, agar jika terdapat 2 berita tanpa foto, tidak tertarik foto Unsplash yang sama persis sehingga konten terlihat duplikat.
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
      - **Penebalan Visual (Visual Anchors):** Gunakan `<strong>...</strong>` pada 1 frasa kunci per paragraf agar pembaca yang membaca sekilas (*skimming*) langsung menangkap inti pesan tanpa merasa silau.
      - **Kurasi Foto Hero Bersih & Anti-3D Cartoon:** Foto sampul WAJIB dokumentasi pers nyata atau fotografi konseptual teknologi beresolusi tinggi (lengan robot presisi di lab, wafer silikon semikonduktor, koridor server data center). DILARANG KERAS menggunakan foto render 3D kartun, meme, mainan/boneka, ilustrasi clipart, atau gambar ber-watermark komersial (filter out `plus.unsplash.com`, `premium_photo`, `shutterstock`, `gettyimages`). Hindari gambar artikel yang memuat banner teks promosi besar berbahasa Inggris atau logo vendor yang tidak relevan dengan topik.
    - **Pemenggalan Kalimat Aman:** Saat mengekstrak kalimat dari ringkasan berita, jika isi ringkasan sangat pendek (kurang dari 3 kalimat pendukung), jangan paksakan variabel kosong yang akan membuat layout *broken* atau tersangkut variabel lama. Siapkan satu klausul *fallback* redaksional elegan bergaya Indonesia yang tidak kaku.
    - **Filter Kosa Kata Asing di Judul:** Gunakan regex sederhana untuk mengganti frasa kaku bawaan mesin translasi dengan idiom lokal yang lebih natural (contoh: "How" / "Why" → "Cara", "Now everyone can" → "Kini Semua Orang Bisa", "puts on hold" → "Tunda", "due to" → "Gara-Gara").
    - **Konsistensi Identifier Role (Template vs Payload):** Pastikan role yang dikaitkan di template (`CONTEXT`, `SIGNIFICANCE`) cocok 100% dengan role yang dicek di dalam logika pemecah teks. Gunakan pencocokan majemuk jika ada varian nama role lama (`if (role === 'WHY_IT_MATTERS' || role === 'SIGNIFICANCE')`), agar format teks tetap bekerja walau sasis template pernah diubah namanya.
    - **Fallback Visual (Hero Image):** Selalu pasang *fallback* gambar latar (misal dari Unsplash) untuk Slide 1 (Hook/Cover) di logika perenderan jika artikel asli tidak memuat `image_url` (bernilai `null` atau kosong). Kanvas sampul berita tidak boleh kosong tanpa foto.
      - **PITFALL "Foto Sampul Kembar/Duplikat":** Jangan gunakan pencarian statis yang selalu mengembalikan gambar yang sama (misal `findReferenceImage` yang mereturn foto ke-1 dari hasil Unsplash) untuk berita tanpa gambar asli. Hal ini membuat dua berita berbeda (seperti *paper* ArXiv) tampak seperti *postingan ganda/spam* di *feed* Instagram karena Slide 1-nya identik. **Selalu tambahkan pengacakan (random/offset) atau rotasi bank gambar** agar gambar *fallback* tidak pernah sama berturut-turut.
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

## 7. Monitoring & Analitik (Insights)
API yang sama dapat digunakan untuk memantau performa postingan dan metrik interaksi tanpa perlu masuk ke aplikasi.
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
     - **Mindset Kreator Multidimensi (Riset, Marketing, Branding):**
       - *Lensa Riset:* Cari benang merah (*The 'So What?'*), utamakan data primer terverifikasi, hindari sintesis dangkal dan klaim bombastis tanpa angka riil.
       - *Lensa Marketing (Swipe & Save Velocity):* Hook Slide 1 dipahami < 1 detik, konten mandiri tuntas (*Zero-Click Content*) yang membuat audiens merasa berhutang budi sehingga memicu tombol Simpan (Bookmark) dan Share.
       - *Lensa Branding (Wibawa Visual):* Jangan kaku pada satu dogma kaku. Tampung ragam referensi (Bento box, Data dossier, Modern broadsheet, Minimal tech) dengan tetap berpegang pada disiplin majalah fisik, palet warna terbatas, dan eliminasi total elemen AI slop (pendaran neon, badge melayang sintetis).
     - **PITFALL Dobel Upload (Filter Logika):** Jangan bergantung pada memori internal AI saat mengantre draf. Saat merancang `instant-news-dispatcher` atau skrip sejenis, urutannya MUTLAK: 1) Tarik daftar berita (terbaru di atas), 2) Query database riwayat tayang (`SELECT article_id FROM ig_publications WHERE status='PUBLISHED'`), 3) Buang berita yang sudah ada di database, 4) Ambil target [0] dari sisa list. Jangan gunakan indeks acak atau mem-bypass cache.
     - **Formula Target Pertumbuhan Followers Akun Baru:**
       - *Kombinasi 1-2 Punch:* Jadwalkan Reels harian (2 slot: 12:30 dan 19:30 WIB) sebagai mesin pembuka jangkauan (*top-of-funnel reach* ke non-followers) dipadukan dengan Carousel warta berbobot (maksimal 5 post/24 jam) sebagai mesin konversi pengunjung menjadi pengikut setia (*followers conversion*).
     - Simpan stempel waktu eksekusi pada tracker file lokal (`data/instant_dispatch_tracker.json`) untuk mempertahankan status lintas sesi reboot.
     - **Bypass Trigger Manual (Force Upload / "Haplot"):** Jika user meminta pengunggahan paksa ("haplot") menggunakan "Logarigma awal", namun batas kuota harian di tracker penuh, kosongkan nilai tracker (`echo '{"last_post_at": null, "posts_today": []}' > data/instant_dispatch_tracker.json`) lalu jalankan eksekusi node langsung (`node scripts/instant-news-dispatcher.js`) untuk melakukan satu siklus memindai dan posting instan. Jika menjalankan skrip lama seperti `daily-publisher-service.js`, skrip dapat *crash* jika teks AI melebihi batas (error batas karakter); lakukan *patching* kode (misal `slice(0, max_characters)`) alih-alih melempar error agar skrip *resilient* dan jalan mulus.
       - **PITFALL KRITIKAL (Background Daemon):** Jika Anda menghapus batas tracker saat proses daemon (PM2) masih hidup di *background*, daemon tersebut akan terbangun dan otomatis menembakkan rentetan postingan (spam) setelah jeda *cooldown*-nya selesai. **SELALU matikan proses PM2 terkait (`pm2 stop <nama>`)** SEBELUM melakukan tes *bypass* atau pengosongan *tracker* secara manual.

## 10. Sistem Notifikasi Instan Pengawas (Telegram Webhook Alerts)
Ketika sistem beroperasi dalam mode otonom murni (auto-publish tanpa approval manusia di dashboard):
- **Notifikasi Setiap Postingan Berhasil:** Pengawas/kreator WAJIB langsung dikabari via Telegram seketika setelah postingan terbit di Instagram (`sendTelegramPostNotification`).
- **Muatan Pesan Notifikasi:**
  1. *Format Media:* Indikator warta carousel (`📰`) atau video Reels (`🎬`).
  2. *Judul & Penerbit Asli:* Menyebutkan headline aktif dan lab/sumber aslinya.
  3. *Tautan Langsung (Permalink IG):* Langsung cantumkan tautan URL Instagram aktif (`https://www.instagram.com/p/.../`) agar kreator tinggal klik untuk langsung melihat postingan yang baru tayang.
- **Arsitektur Pengiriman:** Gunakan bot token Telegram resmi yang tersimpan di environment (`TELEGRAM_BOT_TOKEN`) melalui HTTP request mandiri (`/sendMessage`) dengan format HTML bersih.

## 11. Identitas Maskot ("Brand Soul") & Anti-Slop Persona
- **Membedakan dari Ribuan Akun Bot Agregator:** Akun media otomatis sangat rentan terkesan dingin, kaku, dan membosankan jika hanya berisi teks berita formal.
- **Persona Inspektur Skeptis:** Gunakan maskot dengan karakter khas (seperti maskot *deadpan side-eye* "Inspektur Bebek") yang memposisikan akun sebagai penguji fakta independen yang dingin, skeptis terhadap klaim marketing lab AI yang berlebihan, dan berpegang pada bukti riil.
- **Penempatan Visual:** Terapkan maskot pada:
  - Foto profil resmi akun (crop melingkar dengan sasis monokrom).
  - Stempel inspeksi redaksi di Slide 4 carousel bersanding dengan tanda tangan kurator.
  - Header portal web pemantau. Kehadiran maskot ini memperkuat identitas merek (*brand recall*) dan meningkatkan *engagement/shares* tanpa merusak wibawa desain minimalis.

## 12. Ketahanan Sistem Latar Belakang & Kekebalan Sesi (`/new`)
Saat membangun automasi penerbitan jangka panjang yang dikendalikan pengguna lewat antarmuka chat (seperti Telegram):
- **Isolasi Siklus Hidup Chat vs Daemon OS:** Perintah pembersihan konteks seperti `/new` HANYA mengosongkan sesi percakapan LLM saat itu. Schedulers (`jobs.json`) dan proses PM2 beroperasi di layer sistem operasi host.
- **Kunci Konfigurasi PM2:** Jalankan `pm2 save` setelah mendaftarkan service agar seluruh proses tersimpan di `dump.pm2` dan otomatis bangkit kembali (*auto-respawn*) saat mesin server/RDP reboot.
- **Dua Faktor Penghenti Riil:**
  1. *Token Kedaluwarsa:* Token Long-Lived Meta User Access Token memiliki masa aktif ~60 hari; wajib disediakan alur pembaruan token sebelum kedaluwarsa.
  2. *Reboot Total Host:* Diatasi dengan `pm2 save` dan scheduled watchdog script deterministik (`no_agent: true`).

## 13. Viral AI Video Radar & Integrasi Pengunduh Headless
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

## 14. Hirarki Kontrol Absolut (Telegram vs RDP Server)
- **Telegram sebagai Command Center:** Pengguna mengendalikan agen 100% dari antarmuka Telegram.
- **RDP sebagai Server Buta (Headless-like):** RDP Windows hanyalah mesin pelaksana (backend server). Jangan pernah menyuruh pengguna untuk membuka link `127.0.0.1`, `localhost`, atau mengecek tampilan di browser RDP sendiri.
- **Pitfall Pelaporan UI/UX:** Jika merakit purwarupa dasbor, HTML, atau merender *screenshot*, agen WAJIB menggunakan perkakas tangkapan layar di server (seperti `browser_exec` atau `puppeteer`) dan langsung mengirimkan berkas/gambarnya ke antarmuka Telegram pengguna via format `MEDIA:...`.

## 15. Telemetri Terpadu Eksternal & Internal (Home, Login & Admin)
Ketika sistem memiliki banyak background jobs dan daemons yang berjalan di RDP:
- **Ketersediaan Publik Tanpa Login:** Sediakan ringkasan telemetri yang bisa diinspeksi dari luar (halaman login atau beranda publik) via modal popup transparan tanpa perlu membocorkan token/rahasia internal.
- **Data Minimum Telemetri:**
  1. *Resource Host:* RAM terpakai / total GB dan Uptime.
  2. *Status PM2:* Layanan Online vs Mati beserta penggunaan memori aktual.
  3. *Jadwal Cronjob:* Status aktif/jeda, interval ekspresi, waktu eksekusi terakhir, jadwal lari berikutnya, serta ringkasan error terakhir.
- **Efisiensi Beban Terowongan (Tunnel Pruning):** Selalu matikan background tunnel sementara (seperti Cloudflare Quick Tunnel untuk arena uji atau dev server yang tidak lagi dipakai publik) agar tidak membebani bandwidth dan memori server jangka panjang.

## 16. TikTok Photo Carousel Curation & Audio Dynamics (SputarBall / Berita Bola)
Ketika mempublikasikan konten format *Photo Carousel* (Multi-Slide) ke TikTok Studio (`/tiktokstudio/upload`):
- **Pitfall Lagu Formal / Seremonial:**
  Dilarang keras memasang lagu kebangsaan resmi, mars upacara, atau musik korporat formal (misal *Indonesia Raya* atau mars resmi). Pada format TikTok, retensi audiens diuji pada 1–1.5 detik pertama. Lagu kaku membuat audiens menganggap konten membosankan dan langsung menggeser (*swipe away*), menjatuhkan skor retensi algoritma.
- **Prioritas Tab "For You" Native:**
  Modal *Add Sound* TikTok Studio sudah memiliki tab **"For You"** yang otomatis mengagregasi sound viral sesuai niche akun (misal: chant suporter sepak bola, beat viral, dan breakbeat). Biarkan query kosong sebagai *default fallback* agar sistem memilih rekomendasi teratas tab *For You*.
- **5 Kategori Audio yang Efektif untuk Carousel Sepak Bola:**
  1. *Brazilian Phonk & Funk (Montagem / Bass Berat):* Query `brazilian phonk`. Sangat ampuh untuk berita gol spektakuler, comeback dramatis, highlight striker bintang, atau performa monster pemain.
  2. *Jedag-Jedug (JJ) / Breakbeat:* Query `breakbeat`. Sangat disukai audiens TikTok lokal untuk berita kemenangan Timnas Indonesia, selebrasi viral, rivalitas derby, atau konten santai/banter.
  3. *Chill Lofi / Moody / Slowed & Reverb:* Query `chill lofi beat`. Format carousel adalah slide membaca teks; audio santai dan estetik (seperti D4vd, Arctic Monkeys slowed) membuat audiens betah membaca dari slide 1 sampai 4 tanpa kejenuhan audio (*audio fatigue*). Cocok untuk berita analisis taktik, investigasi, atau cerita cedera pemain.
  4. *UK Drill & Trap Hype:* Untuk warta bursa transfer mahal atau perkenalan rekrutan bintang baru.
  5. *Chant Suporter & Drum Tribun (Bukan Musik Upacara):* Jika bertema kedaerahan atau Timnas, gunakan ritme drum ultras tribun stadion asli daripada rekaman lagu studio formal.