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
