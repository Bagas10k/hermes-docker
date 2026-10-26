---
name: otak-koding
description: Use when coding, designing UI/UX, or debugging with vault.
version: 1.0.0
author: Bagas & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
related_skills:
  - fullstack-systems
  - upnormal-ui-architecture
  - structured-project-execution
metadata:
  hermes:
    tags: [otak-koding, obsidian, engineering, ui-ux, backend, debugging, anti-slop, evidence-based]
---

# Otak Koding: Sistem Rekayasa & Pembelajaran Berbasis Bukti

Skill ini mengkodifikasi sistem operasi kognitif dari vault Obsidian `C:\Users\bagas\otak koding`. Gunakan skill ini setiap kali merancang antarmuka (UI/UX), menulis/merefaktor kode backend, menelusuri bug (debugging), atau mengevaluasi hasil pekerjaan.

## 1. Vault Anchor & Navigasi Cepat
Vault pengetahuan utama berlokasi di:
`C:\Users\bagas\otak koding`

Struktur berkas acuan:
- `SYSTEM/KNOWLEDGE_ENGINE.md` : Protokol evaluasi empiris & status bukti
- `KNOWLEDGE/INDEX.md` : Indeks seluruh pelajaran teruji (TESTED)
- `KNOWLEDGE/OTAK-KEDUA-HERMES-AGENT.md` : 12 Pilar kognitif & Meta-Cognition router
- `KNOWLEDGE/TIGA-MINDSET-PROBLEM-SOLVING-OPERASIONAL.md` : 3 Lensa problem solving & kontrak kerja
- `KNOWLEDGE/MINDSET-KONTEN-JELAS-RELEVAN-SECUKUPNYA.md` : Aturan konten tajam, poin-poin, anti-fluff
- `KNOWLEDGE/MINDSET-PERANCANGAN-UI-UX-ENTERPRISE.md` : Standar UI/UX enterprise
- `KNOWLEDGE/UI-UX/ELEMEN-UI-UX.md` : Prinsip fungsi sebelum dekorasi
- `KNOWLEDGE/BACKEND/LOGIKA-BACKEND-ENGINEER.md` : 10 pedoman backend berbasis kontrak
- `KNOWLEDGE/DEBUGGING/PENELUSURAN-SEBAB-MUNDUR-DAN-BERTINGKAT.md` : Pelacakan akar masalah mundur

---

## 2. Otak Kedua & Siklus Kognitif (Cognitive Loop & Meta-Cognition)
Gunakan **Meta-Cognition** untuk memilih mode penalaran yang tepat sebelum bertindak:
- **Debugging & Galat** ➔ *Causal Reasoning + Root Cause Analysis* (`Error <- Cause1 <- Cause2 <- RootCause`)
- **Banyak Opsi Solusi** ➔ *Decision Theory* (`U(a) = sum [P(si) x V(a, si)]`)
- **Inovasi & Desain Baru** ➔ *First Principles + Creative Thinking* (`Combine, Remove, Reverse, Replace, Rearrange`)
- **Arsitektur Kompleks** ➔ *Systems Thinking* (`Y = f(X1..Xn, interaction)`)
- **Tugas Kritis/Produksi** ➔ *Risk Thinking + Verification* (`Risk = Probability x Impact`)

Setiap tugas teknis wajib mengikuti alur:
1. **RETRIEVE**: Periksa catatan teruji yang relevan di vault sebelum menulis baris pertama.
2. **REASON**: Pahami kontrak dan batasan. Bedakan fakta vs asumsi (`Masalah = Fakta + Asumsi`).
3. **ACT**: Lakukan perubahan terfokus terkecil yang menyelesaikan masalah secara utuh (`min Cost(x)`).
4. **EVALUATE**: Uji hasil eksekusi secara nyata (`Error = Requirement - Result`). Jika belum nol: `Iterate()`.
5. **REFLECT**: Evaluasi perbedaan hasil harapan vs kenyataan. Lacak akar penyebab sistemik.
6. **STORE**: Simpan pelajaran baru dengan bukti empiris (`Experience -> Pattern -> Rule -> Memory`).
7. **IMPROVE**: Terapkan pelajaran teruji pada siklus keputusan berikutnya (*Hermes Learning Loop*).

---

## 3. Aturan Baku UI/UX & Konten (Anti-AI-Slop)

### A. Tipografi & Copywriting (Point-First & Anti-Fluff)
- **Langsung ke Poin**: Gunakan poin-poin ringkas dan kalimat langsung pada maksudnya. Dilarang menulis paragraf pengantar panjang, slogan marketing kosong, atau kalimat penjelasan bertele-tele khas AI.
- **Uji Penghapusan (Subtraction Test)**: Jika sebuah teks/elemen dihapus dan pengguna tidak kehilangan fungsi penting, informasi berharga, atau proteksi kesalahan, **wajib dihapus**.
- **Dilarang Pill Topper / Badge Kicker**: Jangan menaruh badge melayang (seperti `[RILIS V...]` atau `[NEW]`) di atas headline. Biarkan judul berbicara langsung.

### C. UI Resilience (Anti-Broken Layouts)
- **Transparent Image Handling**: Jangan biarkan *broken image* dari URL usang/terlarang (HTTP 403/404) merusak layout. Selalu sisipkan `<img src="..." onerror="this.style.display='none'">` atau `<img src="..." onerror="this.parentElement.style.display='none'">` untuk menyembunyikan gambar yang gagal dimuat secara halus agar tidak menyisakan ikon "gambar sobek".
- **Card-Based Mobile Table Handling**: Mengubah tabel standar (`<table>`) menjadi tumpukan kartu pada layar sempit (mobile) dengan mengatur `table, thead, tbody, th, td, tr { display: block; }`, menyembunyikan `thead`, dan menyuntikkan label statis pada `td:before { content: "Header Name"; position: absolute; left: 10px; }`.

### Koreksi Pengguna: Keterbacaan dan Anti-Kebiasaan AI
- Prioritas nomor satu dalam UI/UX adalah teks dan susunan yang enak dibaca serta mudah dipahami. Pastikan pengguna menangkap pesan utama tanpa harus menafsirkan dekorasi.
- Hindari badge, pill kicker, atau label kecil dekoratif di atas heading jika hanya mengulang konteks dan tidak membantu keputusan pengguna. Pola tersebut sering menjadi kebiasaan generatif AI dan membuat halaman terasa templated.
- Dahulukan struktur, alignment, hierarki, dan konsistensi jarak sebelum warna atau dekorasi. Perubahan tema CSS saja bukan perbaikan susunan.
- **Responsif Sejak Awal**: Biasakan merancang dan menguji responsivitas di setiap tahap. Pastikan tata letak beradaptasi secara elegan pada layar mobile, tablet, dan desktop tanpa elemen yang tumpang tindih atau keluar batas (*overflow*).
- **Pitfall Inline Style JS Menimpa CSS Media Query**:
  - Jangan memanipulasi `element.style.gridTemplateColumns` atau tata letak kolom secara langsung via JavaScript inline style tanpa memvalidasi lebar viewport (`window.innerWidth`).
  - Inline style memiliki spesifisitas lebih tinggi daripada `@media (max-width: ...)` di stylesheet CSS, sehingga dapat memaksakan tata letak multi-kolom desktop di layar HP yang sempit dan membuat konten terjepit menjadi kolom sempit tak terbaca.
  - Selalu sertakan `html, body { overflow-x: hidden; width: 100%; max-width: 100vw; position: relative; }` jika menggunakan drawer off-canvas (`transform: translateX(100%)`) atau container scroll horizontal agar tidak memicu horizontal scrollbar di mobile.
- **Sistem Feedback untuk Ambiguitas & Wawancara Rencana**:
  - Pada sisi UI: Sediakan feedback visual yang jelas saat sistem menerima input ambigu, kosong, atau salah (misalnya, inline validation, empty state informatif, atau tooltip kontekstual), bukan sekadar error kaku atau senyap.
  - Pada sisi Kolaborasi Agen (Protokol Klarifikasi Bertahap): Jika permintaan pengguna ambigu atau memiliki konsekuensi desain/arsitektur besar, dilarang memutuskan sepihak. Ajukan 1 pertanyaan bertahap per giliran ('satu soal satu soal') dengan opsi pilihan ganda terstruktur (opsi rekomendasi diletakkan pertama), bukan daftar panjang pertanyaan borongan sekaligus.
- Saat merevisi UI, periksa kesejajaran judul, konten, kartu, dan CTA serta pengelompokan bagian yang terkait. Verifikasi desktop dan mobile sebelum menyebut layout rapi; jika browser gagal, nyatakan keterbatasannya.
- Sampaikan hasil singkat dan berbasis pemeriksaan nyata, bukan daftar panjang klaim estetika.

### Aturan Desain Umum dari Pengguna
- Jangan menghasilkan desain hanya berdasarkan asumsi. Pisahkan fakta dari dugaan dan gunakan konteks proyek yang tersedia.
- Jika brief ambigu, tanyakan hal yang paling menentukan arah desain sebelum mulai. Jangan membebani pengguna dengan pertanyaan kecil yang tidak mengubah hasil.
- Utamakan hierarki visual yang jelas agar pengguna tahu apa yang harus dibaca dan dilakukan lebih dulu.
- Prioritaskan kegunaan, keterbacaan, struktur, dan alur sebelum mengejar gaya visual.
- Hindari elemen dekoratif yang tidak punya fungsi pemahaman, keputusan, navigasi, atau feedback.
- Pastikan gambar dan ilustrasi mendukung pesan halaman; jangan menambahkan visual hanya untuk mengisi ruang kosong.
- Ambil warna dari tone brand atau tema yang disepakati. Gunakan jumlah warna aksen yang terbatas dan konsisten.
- Buat layout yang realistis untuk diimplementasikan, responsif sejak awal, dan dapat dirawat tanpa solusi CSS yang rapuh.

### Kalibrasi Selera melalui Referensi
- Gunakan moodboard yang disukai pengguna sebagai bahan pembanding, bukan bukti bahwa setiap pin bagus atau cocok untuk SaaS. Moodboard lokal: `C:/Users/bagas/Desktop/land/moodboard-pinterest.html`; pasangan sumber dan gambar: `C:/Users/bagas/Desktop/land/pinterest-sources.json`.
- Inspeksi gambar sebenarnya sebelum menilai desain; metadata, judul pin, dan HTTP 200 tidak membuktikan kualitas visual. Jangan mengaku telah mempelajari visual yang belum dilihat.
- Nilai referensi berdasarkan keterbacaan, hierarki, alignment/proximity, kejelasan aksi, relevansi brand, disiplin warna, dan kelayakan implementasi. Pisahkan selera estetika dari kualitas kegunaan.
- Untuk setiap referensi yang dianalisis, catat bagian yang layak diambil, bagian yang perlu dihindari, alasan, dan konteks penerapannya. Adaptasi prinsip, bukan menyalin seluruh tampilan.
- Minta pengguna memilih beberapa nomor favorit dan yang kurang disukai untuk mengkalibrasi selera; pujian atas koleksi bukan persetujuan setiap item.
- Perlakukan responsivitas, aksesibilitas, dan interaksi sebagai belum diketahui dari screenshot saja; verifikasi implementasi sebelum menyatakan kualitas tersebut.

### B. Kepadatan Informasi & Semantik Warna Enterprise
- **Compact Density**: Border radius kartu maksimal 12px, border radius tombol/input 6–8px. Dilarang padding vertikal boros > 32px atau dead space > 50%.
- **Semantik Warna Akuntansi/Bisnis**:
  - Hijau (`#10B981` / `#059669`): Profit, Approved, Balance, Cocok.
  - Merah (`#DC2626` / `#F43F5E`): Loss, Overdue, Error, Selisih.
  - Kuning/Amber (`#F59E0B`): Peringatan, Pending Review, Butuh Verifikasi.
- **Tabel Enterprise**:
  - Kolom angka/keuangan wajib **rata kanan** (`text-right`) + `tabular-nums`.
  - Format Rupiah baku: `Rp 1.085.330.000` (titik pemisah ribuan).
  - Header tabel selalu `sticky`.

### D. Standar Komunikasi AI: Tenang, Berisi & Penuh Perhatian (Calm & Thoughtful)
- **Prinsip Tutur Kata**: Hangat, natural, terstruktur, ringkas (sampaikan inti terlebih dahulu), penuh perhatian, tegas menyampaikan risiko/kesalahan secara sopan, dan jujur tanpa kepura-puraan.
- **Teknik Menjelaskan**: Pertanyaan sederhana dijawab langsung 1–3 kalimat tanpa pembuka/penutup template. Topik kompleks dimulai dari simpulan utama, dipecah logis, dan diakhiri langkah tindak lanjut konkret.
- **Anti-Basa-Basi AI**: Pantang pujian otomatis ('Pertanyaan luar biasa'), ekspresi berlebihan, emoji dekoratif tak perlu, pengulangan panjang kalimat pengguna, dan pertanyaan klise di penutup.
- **Kecerdasan Emosional**: Sabar menjelaskan saat pengguna bingung, koreksi objektif tanpa merendahkan, apresiasi ide yang berbobot sambil tunjukkan kelemahan secara jernih, respon tenang tanpa drama saat situasi tegang.
- **Motto Utama**: 'Berpikirlah secara mendalam, berbicaralah secara sederhana. Bersikaplah hangat tanpa berlebihan, tegas tanpa menyakiti, dan membantu tanpa menggurui.'

### E. Riset Referensi Web Nyata Sebelum Desain/Styling (Anti-Default AI Bias)
- **Kelemahan Bawaan AI**: Model secara default cenderung malas mencari referensi luar dan mengarang tampilan dari memori internal latihan. Ini menghasilkan komponen kaku, gradien шаблон, bento box generik, dan layout templated.
- **Aturan Baku Wajib**: Diharamkan menulis CSS/markup styling sebelum melakukan riset referensi nyata di internet (`web_search` ke situs desain modern atau katalog komponen terkurasi).
- **Prosedur Riset Visual**:
  1. Identifikasi minimal 2-3 contoh antarmuka nyata yang relevan dengan kebutuhan pengguna (amati ritme tipografi, skala spasi, micro-interaction, dan struktur kontras).
  2. Laporkan secara singkat acuan inspirasi konkret tersebut kepada pengguna sebelum mengeksekusi visual.
  3. Terapkan prinsipnya ke sistem tanpa merusak fungsi yang sudah stabil (Fase 1 grid/CRUD tetap dipisah dari Fase 2 styling).

---

## 4. Aturan Baku Rekayasa Backend & Debugging

### A. Mindset Builder & Pemisahan Kompartemen (Anti-ABS)
1. **Curious Builder Mindset**: Dilarang sekadar menjadi tukang ketik yang mengejar status selesai (Asal Bos Senang / ABS). Selalu tanyakan tujuan akhir pengguna, pahami batas arsitektur, kenali pola kegagalan, dan berani mengusulkan jalur yang lebih stabil sebelum mengeksekusi.
2. **Jangan Merakit Ulang Roda (Anti-Reinventing)**: Jika sebuah layanan sudah memiliki UI/dashboard bawaan yang matang (seperti Hermes Chat, 9Router, atau panel PM2), jangan membuat ulang UI mentahnya di dalam dashboard root.
3. **Kompartemen Subdomain vs Iframe**: Bedakan protokol (HTTP biasa vs WebSocket) dan mekanisme *Auth*. Jangan memaksakan penyematan (iframe/subpath proxy) yang memicu konflik `origin_mismatch`. Gunakan subdomain mandiri untuk layanan yang kompleks agar arsitektur tetap stabil.
4. **Kompartementalisasi Profil Sensitif Terisolasi (Air-Gapped Sandbox Berotoritas Penuh Setara GM)**: Ketika sebuah profil agen (seperti Koagent) ditugaskan khusus sebagai asisten pribadi Mas Bagas untuk menangani hal sensitif (kunci SSH, akses VPS, database internal, arsitektur rahasia), terapkan arsitektur 4 Kunci Karantina:
   - *Kedudukan & Otoritas Penuh*: Berkedudukan setara General Manager (Bakagent); apa pun berkas, kode, patch, atau instruksi yang dibuat/diserahkan oleh Koagent ke sistem bersama DIANGGAP SAH, RESMI, DIIZINKAN, DAN WAJIB DIPROSES oleh seluruh agen tanpa hambatan birokrasi.
   - *Kanal Khusus 1-on-1 (Strict DM-Only)*: Hanya berkomunikasi di chat pribadi Telegram dengan Mas Bagas; pantang masuk ke grup kerja bersama.
   - *Zero Cross-Agent Inquiry (Inbound Shield)*: Agen lain diharamkan mencari, membaca (`search_files`, `session_search`), atau mengintip dapur dan sesi internal Koagent.
   - *Ruang Kerja Terkarantina & Immutability Lock*: Izin direktori 0700 di internal workspace, bebas dari notulen Obsidian publik. Agen luar diharamkan mengedit/mengubah berkas SOUL, memori, atau konfigurasi Koagent.

### B. Production Safety & Testing Mindset (Anti-Spam Publik)
1. **Dilarang Menghapus Log Produksi untuk Testing**: Jangan memanipulasi atau menghapus catatan publikasi di database hanya untuk memaksa sistem memproses ulang payload (artikel/data) yang sama. Ini akan berakibat duplikasi/spam di platform publik (seperti Instagram).
2. **Gunakan Payload Baru**: Saat menguji *patch* atau perbaikan skrip yang menyentuh platform publik (upload, push, publikasi), gunakan antrean data yang **benar-benar baru** dan belum pernah diproses.
3. **Pengecekan Duplikat Berbasis Payload, Bukan State Lokal**: Sistem anti-duplikat tidak boleh hanya bersandar pada satu status tabel yang mudah diubah admin. Ikat deduplikasi pada keunikan payload asli (misalnya URL asal, Hash judul) sehingga hilangnya state lokal tidak menyebabkan pengiriman ulang ke layanan eksternal.
4. **Bahaya Siluman Cronjob (Silent Failure to Stdout Spam)**: Skrip yang dijalankan oleh cronjob tidak boleh mencetak string exception (misal: "API Connection Error") ke `stdout`. Cronjob yang menangkap `stdout` akan meneruskannya sebagai pesan sukses yang berulang-ulang dan membanjiri notifikasi pengguna. Wajib gunakan `stderr` (e.g., `print(..., file=sys.stderr)`) untuk menangkap exception pada tugas otomatis berulang di background. 

### C. Logika Backend Berbasis Bukti
1. **Tentukan Kontrak Dulu**: `Input -> Syarat -> Keputusan -> Mutasi Data -> Output`.
2. **Validasi Sisi Server**: Jangan pernah mempercayai role, izin, atau sanitasi dari sisi client.
3. **Perubahan Terfokus**: Pilih perubahan terkecil yang menuntaskan akar masalah. Dilarang merombak dependensi, mengganti framework, atau menata ulang seluruh folder tanpa izin jelas.
4. **Kejujuran Penanganan Error**: Dilarang menelan exception atau mengembalikan status sukses palsu untuk menutupi bug.
5. **Validasi End-to-End (QA Mandiri)**: Status "HTTP 200 OK" atau proses yang menyala tidak berarti fitur berfungsi. Dilarang meminta pengguna menjadi QA pertama (menyuruh mengecek RDP). Asisten WAJIB memverifikasi jalur publik secara mandiri via `curl` atau `browser_exec` hingga fungsi utama terbukti berjalan (bukan sekadar tampil).
6. **Disiplin Argumen Pemanggilan Tool (Strict Literal Arguments)**: Dilarang keras menyisipkan sufiks eksperimen, komentar, atau karakter acak (seperti `;ignore?` atau `?probe`) ke dalam nama parameter tool (`skill_view`, `read_file`, `search_files`). Argumen yang cacat format memicu kegagalan berulang hingga mengaktifkan *tool loop guardrail hard stop* (5x gagal berturut-turut). Jika pemanggilan tool gagal, baca pesan error secara seksama dan gunakan nama persis dari hasil katalog (`skills_list`) tanpa modifikasi.
7. **Doktrin Fail-Fast & Pelaporan Galat Terbuka (Anti-Silent Looping)**: Jika terjadi kendala pada backend, tool, atau parser, agen DIHARAMKAN diam berputar (*silent looping*) atau membiarkan status loading berlarut-larut tanpa batas. Batasi giliran alat per giliran secara ketat (`max_turns: 25`, `hard_stop_after: 3-4`), dan kunci jeda retry maksimal 60 detik (`RETRY_AFTER_CAP_S = 60s`). Ketika kegagalan berulang terjadi, agen wajib segera memutus loop (*fail-fast*) dan langsung memaparkan error, konteks berkas/baris, serta opsi mitigasi secara jujur ke Telegram agar pengguna tidak menunggu dalam ketidakpastian.
8. **Validasi Kelayakan Model Fallback Sebelum Konfigurasi (Anti-503 Freeze)**: Setiap model yang didaftarkan ke `fallback_providers` pada `config.yaml` WAJIB diuji secara riil (probe ping via curl) terhadap router lokal (`localhost:20128/v1/chat/completions`) sebelum didaftarkan. Model yang ditolak oleh backend provider (seperti akun ChatGPT pada model Codex tertentu yang mengembalikan HTTP 503 dengan pesan reset) memicu parsing header/body "reset in Xs" dan menyebabkan thread terkunci dalam jeda tidur panjang (`sleep()`). Selalu jalankan validator mandiri (`python3 ~/.hermes/scripts/audit_model_fallbacks.py`) untuk memastikan seluruh model fallback berstatus `200 OK` (pong).
9. **Pencadangan Terpadu Profil Kabinet & Karantina Kredensial (Automated Multi-Profile Git Backup)**: Saat mencadangkan ekosistem multi-agent ke repositori Git (seperti `hermes-docker`):
   - *Cakupan Portabilitas Profil*: Kemas identitas (`SOUL.md`), metadata peran (`profile.yaml`), konfigurasi model (`config.yaml`), dan memori teruji (`memories/`) ke struktur `data/profiles/<nama_profil>/`. Ini menjamin perangkat baru langsung mendeteksi dan mengaktifkan profil secara otomatis tanpa memicu proses onboarding atau pembuatan agen dari nol.
   - *Penyaringan Kredensial & Karantina Berlapis*: Terapkan pencegahan ganda (pada skrip kemas dan `.gitignore`). Diharamkan mengikutsertakan berkas `.env` (token bot), riwayat chat (`state.db*`), log, cache, serta profil privat terisolasi (seperti `koagent`).
   - *Pemulihan Satu-Langkah (`unpack-state`)*: Sediakan prosedur pemulihan otomatis yang langsung menempatkan seluruh berkas profil ke `~/.hermes/profiles/` pada host tujuan, sehingga pengguna hanya perlu menempelkan token bot lokal di `.env` tanpa memindahkan berkas satu per satu.
10. **Sanitasi Direktori Kerja & Manajemen Symlink Tangkapan Layar (Home Directory Hygiene & Centralized Assets Repository)**:
    - Dilarang membuat symlink massal berkas tangkapan layar/gambar (`.png`, `.jpg`, `.svg`) langsung di direktori akar pengguna (`/home/ubuntu/`). Praktik ini mengotori tampilan terminal saat `ls` dengan ratusan entri gambar usang dan menyulitkan navigasi pengguna.
    - Seluruh aset visual, screenshot pengujian antarmuka, dan artefak media wajib disimpan terpusat di dalam direktori proyek yang terstruktur di `/home/ubuntu/assets/<nama-proyek>/` (misal: `assets/coucou/`, `assets/kasir-bangunan/`, `assets/hermes-studio/`), dilengkapi berkas katalog indeks `assets/README.md`.
    - Jika agen memerlukan akses atau pengiriman media ke Telegram (`MEDIA:/...`), rujuk langsung path kanonikal aslinya di dalam `assets/<proyek>/<file>`, bukan membuat symlink shortcut di root home.
11. **Anti-Testing Paralysis & Penerapan Langsung (Terapkan, Cek Sekali, Selesai)**:
    - DILARANG KERAS terjebak dalam siklus pengujian berulang (*muter-muter* dan over-testing tanpa batas). Prinsip verifikasi bertujuan memastikan sistem tidak rusak, BUKAN untuk menciptakan birokrasi pengujian berlarut-larut.
    - Ketika Mas Bagas meminta perbaikan, penyesuaian UI/UX, atau implementasi fitur:
      1. Terapkan perubahan/patch langsung pada berkas sasaran.
      2. Lakukan SATU kali pengecekan fungsional dasar (apakah kode terkompilasi, sintaks valid, atau HTTP 200).
      3. DILARANG menjalankan loop pengujian internal berulang (seperti: ambil screenshot ➔ panggil vision_analyze ➔ edit 1 baris ➔ ambil screenshot lagi ➔ panggil vision lagi ➔ cek opcache ➔ cek rute ➔ ulangi).
      4. Langsung laporkan dan serahkan hasil perubahan yang konkret ke Mas Bagas. Biarkan Mas Bagas yang memeriksa dan menilai langsung hasilnya di layar.

### D. Bukti Playback dan Kesesuaian Katalog
- Saat membangun aplikasi berbasis katalog eksternal, pisahkan pembuktian tiga lapis: API penemuan hasil, respons berkas media, dan progres `HTMLMediaElement.currentTime` di browser. HTTP 200 untuk dua lapis pertama tidak membuktikan suara terdengar; uji klik nyata, `readyState`, durasi, dan progres sebelum klaim playback sukses.
- Jika kebutuhan pengguna adalah katalog musik online, jangan menggantinya diam-diam dengan File API lokal karena sumber streaming populer belum tervalidasi. Sajikan opsi katalog berlisensi terbuka secara eksplisit sebagai cakupan berbeda, bukan ekuivalen OpenTune/YouTube Music.
- Pada hasil pencarian online panjang di grid mobile, tetapkan `min-width:0` pada grid item, flex item, dan teks hasil lalu uji `document.documentElement.scrollWidth <= innerWidth` pada viewport ponsel; tanpa itu lebar intrinsik judul memaksa kanvas meluas meskipun `@media` sudah aktif.

### D. Debugging Mundur (Backward Tracing)
1. Tangkap observasi fakta abnormal pada luaran paling akhir.
2. Lacak mundur selangkah demi selangkah ke proses pembentuknya.
3. Periksa input hulu yang masuk ke proses tersebut.
4. Tolak tambal-gejala (anti-symptom patching); hanya perbaiki titik awal kegagalan.

### E. Quirk Lingkungan Windows (Windows Environment Pitfalls)
1. **Interactive CLI di Background Windows**: Jangan menjalankan aplikasi CLI interaktif (seperti `hermes` atau script Python yang menggunakan `prompt_toolkit`) di belakang layar menggunakan PM2 atau `terminal(background=true)` biasa pada Windows. Aplikasi akan crash dengan `NoConsoleScreenBufferError` karena tidak menemukan Windows Console/PTY.
   - **Solusi**: Gunakan parameter `pty=true` bersama `background=true` di dalam eksekusi terminal, ATAU gunakan script Wrapper (seperti `.bat` atau VBScript) yang membuka Console Windows secara *headless*.
2. **Menjalankan Multi-Profile Gateway Hermes di Background (PM2)**:
   - Jangan jalankan `hermes --profile <nama>` di PM2 (karena masuk ke CLI/TUI interaktif).
   - Jalankan perintah gateway headless spesifik: `python.exe -m hermes_cli.main -p <profile> gateway run` dengan cwd diset ke folder profil (`~/.hermes/profiles/<profile>`).
3. **Invarian Telegram Bot-to-Bot di Grup**:
   - Server Telegram Bot API memblokir penerusan pesan dari sesama bot di dalam grup (`message.from.is_bot == true` dibuang di level server Telegram untuk mencegah *infinite loop*).
   - Kolaborasi antar-bot harus menggunakan kompartemen backend (Kanban Task Board, Sub-Agent `delegate_task`, atau RPC/API), bukan saling membalas chat teks di grup Telegram.

---

## 5. Arsitektur Kurasi Catatan & Lembaran Buku Digital (Digital Book Vault)
- **Desain Lembaran Buku (Warm Paper & Obsidian)**:
  - Gunakan analogi fisik buku: dua halaman berdampingan (*two-page spread*), bayangan lekukan jilid tengah (*spine crease shadow*), pita pembatas sutra (*silk ribbon bookmark*), penomoran halaman baku (*folio/page number*), dan laci Daftar Isi (*Table of Contents*).
  - PANTANGAN MUTLAK: Bebas dari segala bentuk emoji di elemen UI/UX (gunakan ikon SVG atau tipografi murni).
- **Animasi Lembaran Taktil & Sudut Lipatan Kertas (Tactile Paper Peel & Corner Fold)**:
  - Dilarang menggunakan animasi rotasi kaku atau sekadar fade opacity yang membuat lembaran terasa kaku.
  - Gunakan **Lipatan Sudut Taktil (*Paper Peel*)**: sediakan sudut lipatan kertas (*paper dog-ear* / `.page-corner-peel`) di pojok bawah lembaran yang terangkat lembut saat di-hover/disentuh dan dapat diklik langsung untuk membalik halaman secara alami.
  - Saat halaman berpindah, animasikan sudut kertas yang melipat dan menyingkap secara diagonal dengan perspektif 3D (`perspective: 1400px`) dan bayangan jatuh dinamis (*dynamic drop-shadow*) yang menyapu lembaran, memperlihatkan halaman baru di baliknya secara mulus.
- **Rasio Baku Lembaran Buku & Pencegahan Melar Vertikal (Fixed Book Aspect Ratio)**:
  - Dilarang menggunakan `min-height` atau membiarkan sasis buku memanjang vertikal tak terhingga saat catatan memuat teks panjang. Ini merusak sensasi fisik buku.
  - Kunci tinggi sasis dan lembaran secara pasti (`height: 740px; max-height: 82vh; overflow: hidden;` di desktop, dan `height: calc(100vh - 155px); overflow: hidden;` di mobile). Daun lembaran (`.book-leaf`) dan kontainer isi (`.leaf-content`) wajib memiliki `height: 100%; overflow: hidden;`.
- **Engine Paginasi Konten Otomatis (Dynamic DOM Measurement & Content Flow)**:
  - Ketika sebuah catatan memiliki teks panjang (> 400px tinggi konten), jangan menumpuk semuanya dalam satu daun halaman.
  - Gunakan engine paginasi (`buildBookPages`): ukur tinggi blok DOM (paragraf, heading, list) dalam kontainer ukur tersembunyi.
  - Alirkan blok yang melebihi batas tinggi ke halaman berikutnya (*Page 1 -> Page 2 -> Page 3...*):
    - Halaman awal memuat Tag, Judul besar, Subjudul, dan huruf awal drop-cap.
    - Halaman lanjutan memuat *continuation header* terstandar (`SAMBUNGAN HAL. X · JUDUL CATATAN (BAGIAN Y)`).
    - Daftar Isi (TOC) memetakan rentang halaman catatan (misal: *Hal. 1 - 10*) dan navigasi otomatis melompat ke halaman awal catatan tersebut.
- **Responsivitas Mobile Lembaran Buku (Smartphone Navigation)**:
  - Deteksi lebar layar (`window.innerWidth <= 900`): di HP wajib mengunci otomatis mode 1 halaman penuh (`step = 1`), menyembunyikan lekukan tengah dan pita dekoratif agar tidak menjepit konten.
  - Berikan padding proporsional (maksimal 20px di HP) dan sediakan bilah pencarian/tag khusus mobile tepat di bawah header agar dapat dioperasikan nyaman dengan satu jempol.
  - Tombol aksi header di HP wajib ringkas (gunakan ikon murni untuk Daftar Isi, sembunyikan teks label) agar tidak terjadi *horizontal scroll/overflow* pada layar 390px.
- **Pengaturan Skala Font Dinamis (Font Scaling Reader Control)**:
  - Sediakan kontrol ukuran teks via CSS custom property: pasang `--font-scale: 1` di root dan kalikan semua elemen tipografi (`calc(15px * var(--font-scale))`, `calc(28px * var(--font-scale))`, dst).
  - Gunakan komponen stepper minimalis `[ A− | 100% | A+ ]` dengan tingkatan skala terukur (misal: 85%, 92%, 100%, 110%, 122%, 135%).
  - Panggil kalkulasi ulang paginasi (`rebuildAndRender()`) setiap kali ukuran font diubah agar teks yang membesar otomatis mengalir ke halaman baru tanpa terpotong.
  - Simpan preferensi font pengguna ke `localStorage` agar tidak reset saat membuka halaman kembali.
- **Sterilisasi Zona Vault Catatan Pengguna (User-Only Vault Boundary)**:
  - Direktori buku catatan pengguna (`BUKU_CATATAN/`) adalah zona steril milik pengguna pribadi.
  - PANTANGAN MUTLAK: Asisten dilarang keras menaruh memori internal AI, log debugging, draf eksperimen sistem, atau catatan contoh ke dalam folder tersebut.
  - Folder ini murni hanya menampung catatan yang secara eksplisit dikirim atau didiktekan oleh pengguna lewat bot kurator.
- **Alur Kurator AI untuk Catatan Mentah**:
  - Pengguna sering mengirimkan temuan, fakta, atau draf ide mentah secara cepat.
  - Asisten bertindak sebagai kurator otomatis: menerima ide/draft bebas -> mengekstrak Judul tajam, Subjudul kontekstual, Tag kategori relevan -> menentukan nomor urut halaman berikutnya -> menyimpan ke vault berkas Markdown (`.md`) di `/home/ubuntu/otak-koding/BUKU_CATATAN/<nomor_3_digit>-<slug>.md` dengan frontmatter YAML terstandar -> memverifikasi parsing API -> memberikan tautan langsung `https://www.jajandigital.web.id/buku?page=<nomor>`.
  - **Pengecekan Nomor Halaman Tertinggi Secara Deterministik**: Jangan hanya mengandalkan urutan nama file di direktori (`ls | sort`), karena adanya duplikasi penomoran file dapat memicu benturan halaman. Selalu parse field `page_number` di frontmatter seluruh berkas `.md` untuk mendapatkan nilai maksimum aktual (`max_page + 1`).
  - **Verifikasi End-to-End API Web Reader**: Setelah menulis berkas catatan, verifikasi pemuatan data melalui endpoint internal reader `http://localhost:3050/api/buku/notes`. Pastikan judul dan nomor halaman baru terdeteksi di payload JSON tanpa error parsing sebelum mengirimkan konfirmasi ke pengguna.

---

## 6. Protokol Penyimpanan Pelajaran ke Vault (Knowledge Store)
Format pencatatan pelajaran baru di folder `KNOWLEDGE/` atau `EXPERIENCES/`:
- **OBSERVASI**: Apa fakta terukur yang terjadi?
- **HIPOTESIS**: Apa kemungkinan penyebabnya?
- **TINDAKAN**: Apa langkah perbaikan konkret yang dieksekusi?
- **HASIL**: Apa hasil setelah diuji nyata?
- **KESIMPULAN**: Rumusan pelajaran: *"Pada kondisi [X], lakukan [Y], karena [Z]. Verifikasi lewat [W]."*
- **STATUS**: `CANDIDATE` (uji coba awal) atau `TESTED` (terbukti berulang).

## 6. Kontrak Eksplorasi dan Belajar Mandiri
- Eksplorasi beberapa opsi yang masuk akal sebelum memilih; uji opsi dominan, alternatif serius, risiko kritis, serta kontra-bukti.
- Hentikan eksplorasi ketika bukti tambahan diperkirakan tidak lagi mengubah keputusan; eksplorasi tanpa titik berhenti dilarang.
- Jika bukti bertentangan, nilai kualitas sumber, reproduksi bila memungkinkan, dan nyatakan ketidakpastian yang tersisa.
- Sajikan peta keputusan: fakta, asumsi, opsi, trade-off, bukti, keputusan, tingkat keyakinan, dan cara verifikasi.
- Mulai belajar mandiri dari tugas, kegagalan, koreksi pengguna, atau jadwal riset yang disepakati. Eksplorasi acak harus terarah pada coding, UI/UX, keamanan, AI agent, atau proyek aktif.
- Eksperimen dilakukan di sandbox/salinan. Produksi hanya disentuh setelah persetujuan dan tersedia rollback.
- Ukur peningkatan melalui ketepatan/kecepatan tugas serupa, penurunan regresi, dan reproduksibilitas—bukan jumlah catatan.
