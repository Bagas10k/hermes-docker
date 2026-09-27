# Standar High-Density Developer HUD & Integritas Loop Kognitif Multi-Agen

Dokumen acuan untuk perancangan antarmuka observabilitas pengembang, HUD aksi realtime, dan arsitektur aliran data kognitif multi-agen.

## 1. Aturan Mutlak Visual HUD: Flat 2D Zero-Blur (Anti-3D Tilt)
- **Pantangan 3D Transform pada Monospace:** Dilarang keras menerapkan `rotateX`, `rotateY`, atau `perspective` CSS pada container jendela kode atau teks terminal. Subpixel rendering pada monitor memicu anti-aliasing blur yang merusak ketajaman karakter monospace.
- **Standar Flat Orthogonal:** Jendela HUD aksi pengembang wajib 100% tegak lurus 2D datar (*flat orthogonal*). Efek kedalaman dicapai murni melalui z-index, border kontras (1.5px), background blur semi-transparan (`backdrop-filter: blur(12px)`), dan bayangan jatuh pekat (`box-shadow: 0 18px 40px rgba(0,0,0,0.92)`).

## 2. Rasio Efisiensi & Ruang Kerja Pengembang (Dev Workstation Grade)
- **Header 1-Baris Ultra-Padat (< 25px):**
  - Menggabungkan lencana status (`● DONE`), nama agen (`Si Eksekutor › patch`), durasi latensi (`140ms`), dan tombol aksi cepat (`[COPY]`, `[EXPAND]`, `[✕]`).
  - Maksimal 15-20% tinggi jendela untuk chrome/header; 80-85% ruang wajib dialokasikan untuk konten diff/kode.
- **Smart Path Truncation:**
  - Path panjang dipotong cerdas menjadi `.../directory/filename.ext`, dilarang membiarkan path membungkus menjadi 2 baris canggung.
  - Sediakan fitur klik-untuk-salin path absolut secara instan.
- **Git-Style Gutter Diff Viewer:**
  - Penanda baris `+` dan `-` diletakkan pada kolom gutter khusus yang sejajar rapi.
  - Hindari duplikasi simbol (seperti `- -` atau `+ +`).
  - Latar belakang baris diberi highlight tipis kontras (merah gelap untuk penghapusan, hijau gelap untuk penambahan).
  - Tampilkan statistik mutasi instan: `+N -N lines`.
- **Visibilitas Guardrail & Blast Radius:**
  - Footer wajib menampilkan `SCOPE: <file>` dan `BLAST: ISOLATED` untuk kepastian developer bahwa mutasi aman dan terisolasi.

## 3. Transparansi Dual-Mode Real-Time (Planning vs Execution)
- **Zero Idle Gap:** Sistem observabilitas tidak boleh kosong tanpa aktivitas selama agen berpikir.
- **Mode Planning & Keputusan (`pre_llm_call`):**
  - Jendela otomatis menampilkan tab `🧠 PLANNING & KEPUTUSAN`.
  - Memuat Intent Discovery, Hipotesis Kausal, Deliberasi Trade-Offs, dan Rencana Topologis DAG.
- **Mode Kode & Eksekusi (`pre_tool_call`):**
  - Jendela otomatis beralih ke tab `⚡ KODE & EKSEKUSI` saat perkakas mulai dijalankan.
  - Memuat diff baris kode riil dan perintah shell.
  - Developer dapat berpindah tab secara bebas kapan saja.

## 4. Integritas Loop Kognitif Multi-Agen (Anti-Dead Pipeline)
- **Aliran Data Berkesinambungan:** Level hilir (Verifier, Critic, Learner, Memory Manager) dilarang dibiarkan mati atau permanen `SKIPPED / UNMODIFIED`.
- **Eksekusi Wajib Mengalirkan Asersi:**
  - Setiap mutasi berkas/shell otomatis menghasilkan bukti asersi integritas ke Verifier (`VERIFIED`).
  - Anomali dan linting dievaluasi mandiri oleh Critic (`PASSED`).
  - Aturan prosedural permanen diserap oleh Learner Engine (`EXTRACTED`).
  - Mutasi state persisten dicatat ke SQLite WAL dan vault Obsidian `/buku` milik Mas Bagas yang dikurasi oleh Bikagent (`COMMITTED`).
- **Jalur Sirkuit Laser:** Garis penghubung sirkuit harus menyala dan mengalirkan pulsa energi melintasi seluruh tingkat hierarki, menandakan siklus kognitif agen aktif dan tertutup sempurna.

## 5. Kejelasan Aktor & Hierarki Organisasi (Anti-Generic Labeling)
- Hindari label generik anonim ("Meta Controller", "Context Engine") jika struktur organisasi telah didefinisikan.
- Nyatakan aktor secara eksplisit:
  - **Owner & Supreme Commander:** Mas Bagas (Bagas Cihuy).
  - **General Manager:** BagAgent (Hermes Core Orchestrator).
  - **Assistant Manager:** Bikagent (@Bekbekk_bot - Kurasi Notulen, Backlog, & Vault `/buku`).
  - **Tiga Pilar:** Si Pintar (Riset & Arsitektur AST), Si Eksekutor (Shell, Patch & Mutasi), Si Pengawas (QC, Sentinel & Proof).

## 6. Anti-Ceper Activity Equalizer & Dynamic VU Meter Scaling
- **Pitfall Skala Linier pada Beban Rendah:**
  Menggunakan pemetaan linier mentah `(val / max) * 100` pada kontainer spektrum sempit (< 30px) menyebabkan visualizer/equalizer telemetri tampak "ceper", datar, dan osilasinya tidak terasa saat sistem idle (misal CPU 5–10%, Disk I/O 0, delta osilasi hanya 1–2 piksel).
- **Standar Rekayasa Dynamic VU Pulse:**
  1. *Tinggi Kontainer Ergonomis:* Minimal 40–44px untuk ruang gerak gelombang yang leluasa.
  2. *Amplifikasi Persepsi Non-Linier:* Terapkan kurva eksponensial/pangkat `Math.pow(cpu / 100, 0.42) * 80` dan akar kuadrat I/O $\sqrt{\text{IO}}$ agar saat beban rendah/santai sekalipun, bar tetap berdenyut hidup di rentang visual 35%–85%.
  3. *Asymmetric Attack/Decay (Punchy Response):* Terapkan *fast attack* (langsung melonjak saat ada proses atau paket data lewat) dan *smooth gravity decay* (turun perlahan secara organik seperti VU meter konsol audio studio).
  4. *Multi-Frequency Harmonic Wave:* Padukan osilasi multi-harmonik (`sin` dan `cos` dengan fase berbeda per bar) untuk menghindari gerakan kaku/seragam.
  5. *Gradasi Spektrum Semantik Penuh:* Gunakan gradien vertikal tajam dari Cyan di dasar, Emerald di tengah, Amber di atas, hingga Red di puncak lonjakan beban.

## 7. Ergonomi Dashboard Telemetri Versi Mobile
- **Pangkas Elemen Berat:** Pada viewport smartphone (<= 768px), singkirkan diagram graph SVG raksasa (1000px+) dan stream stdout log mentah ribuan baris yang memicu lag dan scroll fatigue.
- **Fokus 4 Kartu Inti Mobile:**
  1. *Aktivitas Agen Terkini:* Apa yang sedang dikerjakan saat ini & status 4 pilar kabinet (`[ONLINE]`).
  2. *Saklar Kontrol Manual Langsung:* Tombol saklar besar ramah jempol (*thumb-zone*) minimal tinggi 44px untuk Booster (5m), Slow (30m), Jeda/Off, dan Promosi Skill.
  3. *Kondisi Server & Vitals:* Alokasi RAM VPS terhadap batas aman 9.0 GB (*headroom safe limit*), CPU load, dan grid layanan PM2.
  4. *Musyawarah Kabinet:* Chat interaktif realtime via WebSocket dengan kolom input di dasar layar.
- **Kepatuhan Mutlak Doktrin Nol Emoji:** Seluruh antarmuka mobile wajib 100% menggunakan karakter tipografis/ASCII terkalibrasi (`[●]`, `[>>]`, `[==]`, `[||]`, `[^^]`, `[ONLINE]`), bukan emoji grafis.
