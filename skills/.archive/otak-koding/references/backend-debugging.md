# Pedoman Ringkas Backend & Debugging Berbasis Bukti (Otak Koding)

1. Kontrak Sebelum Sintaks: Petakan input -> syarat -> keputusan -> mutasi -> hasil.
2. Validasi Server-Side: Jangan percaya payload client untuk otorisasi atau role.
3. Perubahan Terfokus: Perbaikan terkecil pada akar masalah; jangan acak dependensi atau arsitektur.
4. Backward Tracing: Lacak mundur dari output abnormal ke proses ke input hulu. Dilarang tambal-gejala.
5. Penanganan Error Jujur: Jangan telan error atau return success palsu.
6. PM2 & Python TUI di Windows: Jangan jalankan CLI interaktif Python yang membutuhkan TUI (seperti `prompt_toolkit`) di latar belakang menggunakan PM2 pada Windows — program akan crash dengan `NoConsoleScreenBufferError` karena tidak ada buffer layar terminal yang terikat. Jalankan proses tersebut di jendela Command Prompt yang terlihat secara persisten.
7. Node Native Addons & Glibc Mismatch (Migrasi Linux): Jika dependensi biner native C/C++ (seperti `sqlite3`, `better-sqlite3`) gagal dengan error missing `GLIBC_...`, lakukan kompilasi ulang dari source menggunakan `node-gyp rebuild` di dalam folder modul terkait. Pada npm v11+, perhatikan bahwa `allowScripts` memblokir skrip build otomatis secara default hingga disetujui via `npm install-scripts approve <pkg>`.
8. Python Virtualenv Symlink Trap: Dilarang membuat raw symlink dari `~/.local/bin/python` ke `venv/bin/python`. Python akan me-resolve path kanonikal biner asli dan kehilangan `pyvenv.cfg` sehingga modul venv tidak terbaca. Gunakan wrapper script eksekusi (`#!/bin/bash \n exec /path/to/venv/bin/python "$@"`) untuk menjaga integritas virtual environment.
9. Ekstraksi Puppeteer Headless Tanpa Unzip/Sudo: Pada sistem Linux tanpa utility `unzip` dan tanpa akses `sudo`, perintah install browser Puppeteer akan gagal mengekstrak arsip zip. Pasang paket npm `yauzl` di proyek untuk memungkinkan ekstraksi Chrome murni dari user space tanpa dependensi root.
10. Rust OpenSSL-Sys Kompilasi di User Space: Jika `cargo build` atau `cargo install` gagal mencari library OpenSSL (`Could not find directory of OpenSSL installation`) pada Linux tanpa akses root / sudo dan tanpa `pkg-config`, jangan terhenti. Tambahkan `openssl = { version = "0.10", features = ["vendored"] }` (dan bila menggunakan git2: `git2 = { version = "...", features = ["vendored-openssl"] }`) pada `Cargo.toml`. Cargo akan otomatis mengunduh `openssl-src` dan mengompilasinya dari kode sumber menggunakan `gcc` dan `perl` lokal.
11. Pemasangan MCP Server Non-Interaktif di Hermes: Hermes memblokir penulisan langsung ke `~/.hermes/config.yaml` demi alasan keamanan. Selalu gunakan CLI resmi `hermes mcp add`. Untuk mencegah pembatalan otomatis pada prompt konfirmasi interaktif di terminal latar belakang:
    - MCP Stdio: `printf "y\n" | hermes mcp add <name> --command <bin> --args <args>`
    - MCP Remote HTTP/SSE: `printf "n\ny\n" | hermes mcp add <name> --url <url>` (input pertama `n` untuk 'Does this server require authentication?', input kedua `y` untuk 'Enable all tools?').
12. External Rust Repository Toolchain Override Trap: Repositori pihak ketiga sering menyertakan `rust-toolchain.toml` dengan channel nightly yang memicu pengunduhan komponen gagal atau error biner cargo tidak ditemukan. Hapus `rust-toolchain.toml` setelah cloning atau panggil secara eksplisit `cargo +stable ...` agar build selalu menggunakan toolchain stable sistem.
13. Defensive Machine Learning Validation pada CPU Tanpa GPU: Jangan jalankan komputasi training LLM skala penuh pada server CPU murni. Validasi integritas kode secara lokal menggunakan dry-run: tes tokenisasi/dataset mapping dengan data sintetis kecil, inisialisasi arsitektur model kosong dari `AutoConfig` untuk memeriksa bentuk output logit tanpa mendownload checkpoint bobot multi-gigabyte, ukur rasio bobot LoRA via PEFT `get_nb_trainable_parameters()`, dan bungkus resep pelatihan ke berkas `.yaml` (Axolotl/LitGPT) untuk didelegasikan ke cloud GPU runner saat siap melatih.
14. Efisiensi RAM Inferensi Model Semantik (MiniLM/Sentence-Transformers di CPU):
    - Jangan pernah melemparkan ratusan kalimat dalam satu forward pass tunggal; hal ini melipatgandakan alokasi buffer aktivasi PyTorch hingga 2GB+ dan membebani RAM server.
    - Wajib lakukan batching kalimat dalam potongan kecil (`batch_size=16`), batasi panjang sequence token (`max_length=128`), dan batasi korpus pembanding pada jendela geser terbaru (misal: 50–60 entri).
    - Batasi paralelisme thread via `torch.set_num_threads(2)` dan panggil `gc.collect()` setelah kalkulasi agar penggunaan RAM tetap stabil di bawah 250MB dan CPU 0% saat idle.
15. Kalibrasi Ambang Batas Kesamaan Semantik Lintas Bahasa (Indo-Inggris):
    - Model embedding berbasis bahasa Inggris (seperti MiniLM) yang mencocokkan teks peristiwa berbahasa Indonesia terhadap korpus warta global berbahasa Inggris menghasilkan skor cosine similarity tipikal 0.50–0.70 (lebih rendah dari threshold monolingual 0.65+).
    - Terapkan ambang batas adaptif: gunakan 0.55 untuk kesamaan makna murni, dan relaksasikan ke 0.48 jika terdeteksi kesamaan entitas/kata kunci teknis kunci (brand, chipset, seri produk) guna menghindari false-negative pada topik yang sedang meledak.
16. Pipa Event-Driven Microservice ML Internal (Node.js + Python PM2):
    - Jalankan engine evaluasi ML Python sebagai microservice HTTP lokal asinkron (`aiohttp.web`) di bawah supervisi PM2 daripada memanggil skrip Python CLI berulang kali. Ini mengeliminasi latensi startup interpreter (~1.5s) dan menjaga konsumsi resource terisolasi rapi.
    - Sinkronisasi data tren dipicu secara event-driven (`POST /sync-trends`) sesaat setelah radar CCTV warta menyelesaikan patrolinya, dan kirim umpan balik (`POST /feedback`) saat artikel sukses terbit untuk memperbarui bobot adaptif di SQLite.
    - Untuk penelusuran tren pencarian nasional tanpa kunci API eksternal, gunakan feed RSS Google Trends `https://trends.google.com/trending/rss?geo=<KODE_NEGARA>` yang bersih dari CAPTCHA.
17. Express v5 Wildcard Route Syntax Trap (`app.get('*')`):
    - Pada Express v5, sintaks wildcard lama `app.get('*', ...)` melempar galat `PathError: Missing parameter name`.
    - Wajib gunakan middleware fallback standar tanpa parameter jalur: `app.use((req, res) => res.sendFile(path.join(__dirname, 'public', 'index.html')))` untuk menyajikan fallback Single Page Application (SPA).
18. Arsitektur Real-Time Crypto Data Feed (Binance Combined WebSocket + REST Bootstrap):
    - Untuk menyediakan data grafik interaktif instan tanpa memerlukan otentikasi atau API key exchange:
      1. Tarik riwayat awal via REST klines `https://api.binance.com/api/v3/klines?symbol=...&interval=...&limit=250` agar chart langsung terisi penuh saat pertama kali dibuka.
      2. Sambungkan ke WebSocket stream publik Binance `wss://stream.binance.com:9443/stream?streams=btcusdt@kline_1m/...` untuk memproses tick harga dan pembaruan candle secara real-time.
      3. Terapkan mekanisme auto-reconnect ber-exponential backoff pada event `close` atau `error` untuk menjamin operasional mandiri 24/7 di VPS.
19. Engine Simulasi Paper Trading & Invarian Jurnal Latihan:
    - Evaluasi posisi terbuka (`LONG`/`SHORT`) terhadap setiap tick harga atau batas High/Low candle terkini untuk mengeksekusi Take Profit (`TP`), Stop Loss (`SL`), atau Trailing Stop Loss secara deterministik.
    - Saat pengguna melakukan reset saldo akun demo, dilarang keras menghapus histori transaksi atau jurnal masa lalu. Reset hanya mengembalikan saldo virtual dan membatalkan posisi aktif; seluruh rekam jejak jurnal dan analitik kesalahan (*mistake distribution*) wajib dipertahankan untuk evaluasi belajar jangka panjang.
20. Agen Trading Otonom & Loop Pembelajaran Mandiri (Adaptive Bayesian Self-Learning):
    - Pada agen trading mandiri, terapkan batasan risiko non-negosiasi: batasi maksimal posisi terbuka (hindari overtrading), batasi risiko maksimal 2% dari total modal per transaksi, pastikan rasio Risk:Reward minimal 1:1.8, dan wajib patuhi keputusan `WAIT` (jika sistem menganalisa belum ada konfirmasi, dilarang memaksakan entry).
    - Saat posisi ditutup, evaluasi hasil secara adaptif: berikan reward pada bobot pemicu tren (+0.03x) saat Take Profit, dan beri penalti (-0.05x) serta perketat ambang batas keyakinan (+1.2%) saat Stop Loss terkena. Simpan bobot ini ke tabel SQLite (`ai_learning_memory`) agar kecerdasan agen terus berevolusi dan bertahan dari reboot.
    - Fitur Custom Balance wajib memperbarui saldo virtual akun demo secara fleksibel tanpa menghapus riwayat jurnal dan analitik transaksi masa lalu.
21. Subpath Reverse Proxying & Dynamic BASE_PATH pada SPA:
    - Ketika aplikasi web Single Page Application (SPA) yang dirancang pada root `/` (misal port 3070) diproxy ke subpath publik (seperti `https://domain.com/trading/`):
      1. Frontend JavaScript wajib menentukan prefix dinamis: `const BASE_PATH = window.location.pathname.startsWith('/trading') ? '/trading' : '';` untuk seluruh pemanggilan `fetch(BASE_PATH + '/api/...')` dan WebSocket `new WebSocket(protocol + '//' + host + BASE_PATH)`.
      2. Tag HTML wajib menggunakan tautan aset relatif murni (`href="style.css"`, `<script src="app.js">`), bukan path absolut dengan leading slash (`/style.css`).
      3. Pada middleware proxy Express (`http-proxy-middleware`), pasang `pathRewrite: { '^/trading': '' }`, `ws: true`, dan suntikkan header `X-Forwarded-Prefix: /trading`. Pola ini menjamin aplikasi berjalan mulus baik saat diakses langsung pada port internal maupun via domain publik.
22. Multiplexing WebSocket Upgrade pada Reverse Proxy Gateway:
    - Ketika sebuah gateway atau reverse proxy Node.js meneruskan beberapa layanan backend yang sama-sama menggunakan WebSocket (misalnya `/trading` ke `:3070`, `/telemetry` ke `:8090`, dan `/hermes` ke `:9119`):
    - JANGAN PERNAH mengikat event upgrade ke satu proxy tunggal seperti `server.on('upgrade', singleProxy.upgrade)`. Hal ini akan menelan atau menolak seluruh permintaan WebSocket ke subpath lainnya, menyebabkan koneksi browser terputus dan chart atau telemetri terlihat diam/tidak bergerak.
    - Wajib lakukan demultiplexing event `upgrade` berdasarkan awalan `req.url`:
      ```javascript
      server.on('upgrade', (req, socket, head) => {
        const url = req.url || '';
        if (url.startsWith('/trading')) tradingProxy.upgrade(req, socket, head);
        else if (url.startsWith('/telemetry')) telemetryProxy.upgrade(req, socket, head);
        else hermesProxy.upgrade(req, socket, head);
      });
      ```
23. Real-Time Candlestick Charting, 60fps Debounce & Visual AI Decision Overlay:
    - Pada aliran data pasar frekuensi tinggi (7-10 tick/detik), menggambar ulang canvas secara sinkron pada setiap tick dapat memicu stutter atau frame drop. Gunakan peredam `requestAnimationFrame` (`let pending = false; function req() { if (!pending) { pending = true; requestAnimationFrame(() => { pending = false; render(); }); } }`) agar chart beranimasi mulus pada 60 FPS tanpa jeda latensi data.
    - Untuk membangun keyakinan pengguna terhadap keputusan bot/AI, jangan biarkan proses berpikir bot tersembunyi:
      1. Gambar garis overlay aktif langsung pada canvas chart: Garis Entry (Cyan dashed), Take Profit (Emerald dashed + zona arsiran hijau transparan), dan Stop Loss (Rose dashed + zona arsiran merah transparan) serta laser price line pada candle aktif.
      2. Sediakan tab/panel inspektor keputusan yang menampilkan status radar, jarak harga ke target SL/TP dalam nominal dan persentase, alasan teknis bot masuk pasar, dan rekam jejak refleksi pembelajaran yang dipetik dari setiap trade.
      3. Terapkan standar Zero-Emoji mutlak: gantikan seluruh emoji antarmuka (seperti ⚡, 📓, 🤖, 🚀) dengan ikon vektor garis SVG presisi tinggi dan badge tipografi mono terstruktur (`[OK]`, `[WARN]`, `[ORDER]`).
24. Mode Scalping Cepat Otonom (1m - 5m Scalping & Dynamic Trailing Stop):
    - Pada preferensi trading jarak dekat / scalping (1-5 menit), hindari kerangka swing 15m/1h yang lambat.
    - Gunakan konfirmasi tren mikro di 5m, dan picu eksekusi di 1m dengan kalkulasi ATR lilin 1m ketat (Stop Loss ~0.3-0.5%, Take Profit 1.8x ATR).
    - Pasang Dynamic Trailing Stop Loss (0.75x risk distance) begitu harga bergerak searah profit (+0.2%) untuk mengunci breakeven dan mengamankan keuntungan kilat.
    - Percepat siklus scan radar AI menjadi 3 detik agar momentum mikro 1m langsung tertangkap tanpa jeda.
25. Arsitektur Responsif Mobile Penuh untuk Trading Terminal (Layar <= 900px & <= 600px):
    - Di layar mobile/tablet, ubah tata letak 3-kolom desktop menjadi bottom navigation bar 5 tab mandiri (`CHART`, `WATCHLIST`, `AI & ORDER`, `POSISI`, `JURNAL`).
    - Pasang touch drag gestures pada canvas chart (`touchstart`, `touchmove`, `touchend`) dengan `e.preventDefault()` agar pengguna mobile bisa menginspeksi candle OHLCV dan crosshair tanpa memicu scroll halaman.
    - Gunakan `ResizeObserver` agar chart otomatis menyesuaikan rasio dan DPR saat orientasi layar ponsel berganti (portrait/landscape).
    - Format header adaptif 2 baris (baris atas kontrol, pita baris bawah metrik 4-kolom saldo/PnL).
26. WebSocket Path Rewrite & perMessageDeflate RSV1 Trap pada Reverse Proxy Gateway:
    - Di `http-proxy-middleware`, penulisan `pathRewrite: { '^/trading': '' }` memiliki jebakan berbahaya: jika request masuk berupa `/trading` (tanpa trailing slash), regex akan mengubah path menjadi string kosong `""`. Express/Node HTTP backend akan merespons dengan HTTP 404 Not Found karena path kosong dianggap invalid.
    - Selalu gunakan penulisan fungsi fallback:
      `pathRewrite: (path) => path.replace(/^\/trading/, '') || '/'`
      sehingga `/trading` bersih diarahkan ke `'/'` dan `/trading/api/...` tetap mengarah ke `/api/...`.
    - Saat memproxy koneksi WebSocket melalui Node reverse proxy dan Cloudflare tunnel, aktifnya ekstensi permessage-deflate sering memicu korupsi header frame dengan galat:
      `Invalid WebSocket frame: RSV1 must be clear`
    - Solusi: Matikan kompresi pada backend WebSocketServer:
      `const wss = new WebSocketServer({ server, perMessageDeflate: false });`
      Ini memastikan frame dikirim dalam format raw JSON tanpa bit kompresi yang dapat bentrok dengan proxy multi-hop.
27. Arsitektur Data Real-Time 100ms (Binance BookTicker vs Kline & Emas XAU/USD):
    - Stream kline standar (`@kline_1m`) pada exchange hanya memancarkan data setiap 1-2 detik atau saat ada transaksi. Untuk mencapai kecepatan data ultra-realtime 100ms (10–16 pembaruan per detik):
      1. Berlangganan ke stream `bookTicker` (`btcusdt@bookTicker`, `ethusdt@bookTicker`, `solusdt@bookTicker`). Mid-market price `(bid + ask) / 2` memberikan pembaruan likuiditas instan setiap kali orderbook bergeser (< 10-50ms).
      2. Untuk instrumen komoditas/emas dunia (`XAU/USD`), gunakan token emas fisik yang terikat 1:1 (`XAUTUSDT` / `PAXGUSDT`) pada Binance Spot berdampingan dengan ticker Binance Futures `XAUUSDT TRADIFI_PERPETUAL`.
      3. Pasang throttle bucket ~80–100ms per aset di backend sebelum memancarkan event tick ke client agar tidak membanjiri buffer WebSocket.
      4. Pada frontend, terapkan mutasi DOM *in-place* menggunakan atribut target (`data-sym="${symbol}"`) untuk memperbarui angka harga dan animasi kedip hijau/merah. Dilarang merombak ulang elemen DOM (`innerHTML = ...`) pada frekuensi 100ms karena memicu layout thrashing.
28. Sistem Proteksi Anti-Revenge Trading & Psychological Circuit Breaker:
    - *Revenge Trading* (trading impulsif segera setelah mengalami kerugian untuk membalas pasar) adalah kebocoran psikologis paling fatal bagi trader.
    - Implementasikan **Automated Cool-Down Shield**: Setiap kali posisi tertutup dalam status rugi (`pnl < 0`), sistem secara otomatis mengaktifkan hitung mundur jeda tenang (misal: 180 detik / 3 menit).
    - Pada formulir order: Jika masa jeda masih aktif atau pengguna mencoba melipatgandakan ukuran modal (*Revenge Sizing / Martingale*), blokir tombol eksekusi dan munculkan banner peringatan merah anti-revenge. Hanya izinkan eksekusi jika pengguna secara sadar mencentang kotak persetujuan kontrol emosi (*"Saya sadar penuh, tenang, dan mengeksekusi murni berdasarkan sistem"*).
    - Jurnal & Evaluasi: Transaksi yang dibuka dalam masa emosional otomatis dicap dengan tag kesalahan `Revenge Trading` atau `Revenge Sizing / Tilt` di database SQLite agar AI Trading Coach dapat mengaudit rasio keberhasilan trading tenang vs trading emosional.
    - Pada Bot AI Mandiri: Terapkan jeda tenang wajib 2 menit setelah Stop Loss, naikkan ambang batas seleksi keyakinan (+1.2%), dan kunci ukuran risiko modal maksimal 1.5%.
29. Audit Kuota & Konsumsi Token AI Terpusat (9Router SQLite Telemetry):
    - Di lingkungan multi-akun dan multi-provider yang dirutekan via 9Router (`localhost:20128`), jangan menebak saldo token atau memanggil endpoint API publik yang rawan 401/404.
    - Seluruh histori transaksi, pemakaian token, dan status kesehatan akun tersimpan secara lokal dan transparan di SQLite `~/.9router/db/data.sqlite`:
      1. Tabel `usageDaily`: Menyimpan agregasi metrik harian (`requests`, `promptTokens`, `completionTokens`, `cachedTokens`, `cost`) beserta breakdown `byProvider`, `byAccount`, dan `byModel`.
      2. Tabel `providerConnections`: Menyimpan status koneksi akun aktif (Antigravity Google OAuth, Codex ChatGPT Plus/Team), masa berlaku token (`expiresAt`), `testStatus` (`active`), prioritas, dan galat (`lastError`).
      3. Tabel `combos`: Memetakan ID model kombo (`bk`, `cklow`) ke model aktual.
    - Untuk menyajikan rekapitulasi kuota, konsumsi token, dan efisiensi cache secara presisi dan instan tanpa risiko kebocoran kredensial, kueri langsung tabel `usageDaily` dan `providerConnections` di database SQLite tersebut.
31. Inisialisasi Direktori Profil Hermes & Jebakan Berkas 0-Byte (`HomeInitializationError`):
    - Saat mengelola atau memulihkan profil Hermes (`hermes -p <profile>`), direktori internal yang terdaftar di `_HERMES_HOME_SUBDIRS` (`logs/curator`, `pairing`, `hooks`, `pending_messages`, `runtime`, `skins`, `plans`) wajib berwujud direktori asli, bukan berkas reguler kosong 0-byte (yang sering tercipta akibat pemindahan arsip atau clone yang tidak sempurna).
    - Keberadaan berkas 0-byte dengan nama tersebut menyebabkan fungsi `path.mkdir(parents=True, exist_ok=True)` pada `hermes_cli/config_home.py` melempar `FileExistsError: [Errno 17] File exists` dan memblokir seluruh perintah CLI Hermes pada profil tersebut.
    - Solusi: Hapus berkas 0-byte tersebut dan buat direktori aslinya (`mkdir -p`) sebelum mengeksekusi perintah CLI atau gateway profil.
32. Resolusi Target Pasca-Login pada Aplikasi Web di Balik Subpath Reverse Proxy (`X-Forwarded-Prefix`):
    - Pada aplikasi web yang memiliki alur otentikasi formulir di balik subpath proxy (seperti `/hermes`), respons sukses login umumnya mengembalikan objek JSON `{"ok": true, "next": target}`.
    - Jika handler backend me-resolve target default ke `'/'` tanpa memperhitungkan prefix, kode JavaScript di browser (`window.location.assign(data.next || '/')`) akan mengarahkan pengguna ke root domain utama (`https://domain.com/`), bukan kembali ke dalam dasbor yang diproxy (`https://domain.com/hermes/`).
    - Solusi: Periksa header `X-Forwarded-Prefix` pada handler penyelesaian login dan sematkan prefix tersebut ke target jika target bernilai `'/'` atau belum memuat prefix:
      ```python
      target = _validate_post_login_target(next_raw) or "/"
      prefix = _prefix(request)
      if prefix and not target.startswith(prefix):
          target = f"{prefix}{target}" if target.startswith("/") else f"{prefix}/{target}"
      ```
33. Express http-proxy-middleware Path-Stripping Trap pada Mount Aset Statis:
    - Saat menggunakan `app.use('/fonts', createProxyMiddleware({ target: 'http://127.0.0.1:9119' }))` di Express, Express secara otomatis memangkas prefix mount (`/fonts`) dari `req.url` sebelum diteruskan ke proxy middleware.
    - Akibatnya, server target (seperti FastAPI/Uvicorn yang melayani aset di `/fonts/...`) menerima permintaan `/Collapse-Regular.woff2` alih-alih `/fonts/Collapse-Regular.woff2`. Ini memicu HTTP 404 atau looping redirect 302 ke `/login?next=...` jika server memproteksi root.
    - Solusi: Pasang rewrite eksplisit untuk mengembalikan prefix yang dipotong Express:
      `pathRewrite: (path) => '/fonts' + path` (atau `pathRewrite: (path, req) => req.originalUrl`).
34. Python Path.mkdir exist_ok=True Trap terhadap Berkas Reguler 0-Byte:
    - Pada pustaka standar Python, `Path.mkdir(parents=True, exist_ok=True)` hanya mentolerir keberadaan direktori yang sudah ada. Jika jalur target berwujud berkas reguler (misal berkas 0-byte pada `platforms/pairing` atau `cron/output`), Python tetap melempar `FileExistsError: [Errno 17] File exists`.
    - Hal ini kerap melumpuhkan inisialisasi daemon gateway atau cron scheduler saat boot.
    - Solusi: Lakukan verifikasi defensif `if p.exists() and p.is_file(): p.unlink()` sebelum memanggil `p.mkdir(parents=True, exist_ok=True)`.
35. Optimasi Token Konteks CLI via RTK (Rust Token Killer) Hermes Hook:
    - Eksekusi perintah bash/terminal yang bising (seperti `git diff`, `git status`, compiler build log, package manager output) dapat membanjiri context window LLM dengan ribuan token yang tidak esensial.
    - Pasang biner `rtk` ke PATH (`~/.local/bin/rtk`) dan inisialisasi adapter plugin Hermes via `rtk init -g --agent hermes --auto-patch`.
    - Plugin `rtk-rewrite` memanfaatkan hook `pre_tool_call` Hermes untuk mencegat perintah terminal dan menulis ulangnya secara transparan via `rtk rewrite <cmd>`, memangkas 60–90% token tanpa mengubah alur pemanggilan agen.
36. Sinkronisasi Kredensial Model Multi-Profile & Jebakan /v1/models vs /v1/chat/completions:
    - Saat mengkloning atau mengganti nama profil Hermes (`hermes profile rename`), variabel kredensial di `.env` profil (misalnya `HERMES_CUSTOM_LOCALHOST_20128_API_KEY`) bisa tertinggal dalam keadaan kadaluwarsa/invalid.
    - Beberapa proxy router (seperti 9Router) memperbolehkan permintaan `GET /v1/models` lolos (HTTP 200), namun menolak eksekusi `POST /v1/chat/completions` dengan `HTTP 401: Invalid API key`.
    - Solusi: Jangan mengandalkan pengecekan list model untuk validasi autentikasi; selalu uji coba langsung satu inferensi minimal ke `/v1/chat/completions` dan sinkronkan kunci API aktif dari profil default ke `.env` profil target.





