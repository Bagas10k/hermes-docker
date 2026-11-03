## Procedure

### 1. Inisialisasi Kontrak & Struktur Direktori (Phase 0 Freeze)
- Cari dan baca dokumen kelas produk terlebih dahulu sebelum mengubah UI: `PRD.md`, `ARCHITECTURE.md`, `ANIMATION_SYSTEM.md`, `map_layout.json`, dan engine arena yang sudah ada. Gunakan pencarian file terbatas pada root proyek terkait, vault/blueprint, dan core arena; jangan menulis ulang dari nol sebelum membuktikan kontrak asli tidak tersedia.
- Ekstrak dan audit dokumen spesifikasi, taksonomi event, dan batasan invariant arsitektur.
- Audit definisi ruangan dan pemetaan agen yang benar-benar tersedia sebelum menetapkan jumlah di HUD; turunkan hitungan dari data, bukan dari target desain. Pisahkan ruangan, karakter ilustratif, agen runtime, dan proses layanan.
- Utamakan kantor mini yang bagian dan fungsinya terbaca daripada gedung besar tertutup panel. Gunakan penjelasan ruangan berbahasa Indonesia, fokus/zoom yang mudah, serta navigasi sentuh; pengguna memprioritaskan kualitas permanen dan perkembangan yang terlihat dibanding pengerjaan cepat.
- Saat memakai referensi video, bedakan frame yang berhasil diperiksa dari gerakan/interaksi yang belum teramati; gambar sampul tidak membuktikan perilaku video penuh.
- Untuk versi permanen, pertahankan proyek dan rute stabil, siapkan cadangan sebelum perubahan, pisahkan modul visual/data/interaksi, dan dokumentasikan pengujian serta rollback. Jangan menganggap penyimpanan file saja membuktikan layanan tahan restart.
- Siapkan direktori kerja mandiri yang terpisah dari repositori induk sistem:
  ```bash
  mkdir -p /home/ubuntu/<arena-project>/dist-public
  ```

### 2. Pemasangan Dynamic Project Router (Zero-Downtime Serving)
- **Aturan Mutlak:** Dilarang membiarkan agen otonom mengedit `server.js` atau merestart PM2 di tengah pemrosesan tugas aktif.
- Pasang router dinamis berbasis wildcard di server web Express:
  ```javascript
  app.use('/p/:project', (req, res, next) => {
    const proj = (req.params.project || '').replace(/[^a-zA-Z0-9_-]/g, '');
    const target = `/home/ubuntu/${proj}/dist-public`;
    if (fs.existsSync(target)) return express.static(target)(req, res, next);
    next();
  });
  ```
- Daftarkan pola `/p/:project` ke dalam allowlist `privacy-boundary.js` agar proyek yang baru dibangun langsung aktif dan dapat diakses publik dengan tautan yang bisa diklik tanpa reboot server.

### 3. Pemisahan Dua Antarmuka: Dasbor Pelacak vs Halaman Kantor Mandiri
- **Pemisahan Tanggung Jawab (*Separation of Surfaces*):** Pengguna membedakan antara *dasbor pelacak* (roadmap, log, checklist matriks) dan *halaman gedung kantor fisik nyata*. Jangan pernah mengubur kantor visual hanya sebagai tab sekunder di dalam dasbor pelacak.
- **Penerbitan Dasbor Pelacak (`/arena-tracker/`):** Menyajikan status eksekusi real-time, persentase fase, matriks 38 checklist selesai vs belum, dan log stream via auto-polling `state.json` (setiap 3,5 detik).
- **Penerbitan Halaman Kantor Mandiri (`/kantor/` atau `/office/`):** Antarmuka 100dvh layar penuh (*fullscreen game HUD*) mandiri dengan:
  - Arsitektur Game Viewport 100dvh (`position: fixed; inset: 0; width: 100vw; height: 100vh; overflow: hidden;`) di mana kanvas 2.5D diorama membentang penuh edge-to-edge tanpa terjebak di dalam dokumen scroll.
  - Top Floating Glass HUD Bar: Tiga zona terpisah (Zona Kiri identitas kantor <=300px, Zona Tengah pulau status terpadu CPU/RAM/SSE/Ticker/Clock <=280px, Zona Kanan kontrol terpadu <=450px) dengan total lebar <=1040px untuk menjamin bebas flex-wrapping pada laptop standar.
  - Bottom Floating Command Island: Pulau perintah melayang terpusat (`left: 50%; transform: translateX(-50%); max-width: 820px; border-radius: 14px; bottom: 16px;`) dengan tipografi single-line tegas (`white-space: nowrap; gap: 12px;`) memisahkan hitungan progres dan event aktif tanpa teks compang-camping atau dangling bullets.
  - Tactical Radar Minimap (Bottom-Left): Mini-canvas interaktif dengan kode taktis 3-huruf resmi (`MTG`, `STR`, `RES`, `TOL`, `OBS`, `ENG`, `ARC`, `LNG`, `QAL`, `VAU`, `BKP`) menggantikan pemotongan string kasar, highlight ruangan aktif, serta koordinat blip agen berpindah live. Klik pada minimap memicu auto-pan kamera langsung ke ruangan tujuan.
  - Quick Inspector Card Melayang: Popover card di sudut atas kanvas saat ruangan atau agen diklik langsung di kanvas, menyajikan peran, kapasitas, dan tombol pintas tanpa harus membuka dock penuh.
  - Sliding Game Side Dock (Right Dock): Seluruh instrumen manajemen (Ruang & Agen, Work Graph DAG, Alur Artefak, Knowledge Vault, Tool Factory, Telemetri Host, Meja Komando, Backup & Disaster Recovery, Ledger Event) dipadatkan ke dalam satu dock samping geser (lebar ~380px, membentang penuh dari `top: 52px` hingga `bottom: 0` tanpa meninggalkan celah kosong) dengan tab navigasi instan dan animasi buka-tutup mulus (`transform: translateX(...)`).
  - Roster 10 Agen & Live A* Agent Dispatching: Tab Ruang & Agen menyajikan direktori 10 agen spesialis dengan kontrol kirim ke ruangan (`sendAgentToRoom`). Agen menghitung rute A*, melangkah dinamis, mengubah balon status konteks, dan menggerakkan titik blip minimap real-time.
  - Sintesis Suara Taktil & Ambient Drone Web Audio API (Zero-Asset Audio): SFX taktil (klik tombol, chord chime 3-nada saat pilih ruangan/agen, tick replay) serta generative binaural ambient drone (55Hz/110.5Hz dengan lowpass resonant filter) dengan toggle terpisah `SFX: ON/OFF` dan `Ambient: ON/OFF`.
  - Preset Atmosfer Pencahayaan Dinamis: Dropdown di bilah atas HUD untuk mengubah tema pencahayaan visual (Studio Cyber, Sunset Warm, Midnight Neon, Clean Studio).
  - Pintasan Keyboard Game & Cheatsheet Modal: Hotkeys ergonomis (Space untuk play/pause, Panah Kanan/D untuk step maju, Panah Kiri/A untuk reset, 1/2/5 untuk kecepatan, M untuk minimap, E untuk dock samping, F untuk layar penuh, S untuk audio SFX, dan Esc untuk menutup popup/drawer) dilengkapi modal panduan `[Pintasan]`.
  - Kanvas 2.5D isometrik yang memakai kontrak dan engine resmi yang sudah ada (mis. `map_layout.json` 11 ruang dan `arena_engine.js`) sebelum membuat model alternatif. Jika perlu menyederhanakan tampilan, turunkan dari kontrak yang sama agar tidak memutus PRD. Jadikan kelancaran animasi sebagai target terukur, bukan klaim FPS tetap. Beri label karakter ilustratif bila belum terhubung ke identitas agen runtime.
- Daftarkan kedua halaman secara terpisah ke katalog portofolio utama (`katalog-portofolio-web`).

### 4. Doktrin Eksekusi Otonom Berkelanjutan (*Zero-Interruption Autonomous Run*)
- Ketika pengguna memberikan mandat kerja otonom penuh (*"ngga usah jeda jeda terus aja bekerja, saya monitoring di web aja"*):
  - Hentikan jeda percakapan turn-by-turn dan hindari meminta konfirmasi berulang untuk hal-hal teknis non-destruktif.
  - Maju terus melintasi fase-fase roadmap secara beruntun (*continuous batch*), jalankan unit test otomatis untuk memvalidasi setiap gerbang (*gate*), dan perbarui `state.json` di latar belakang.
  - Biarkan pengguna memantau progres secara mandiri melalui dasbor web pelacak.
- Jika pengguna memberi batas waktu panjang (mis. sampai jam tertentu), jangan bergantung pada `delegate_task` saja karena hasilnya kembali ke chat dan mudah putus konteks. Tulis brief otonom ringkas di root proyek, jalankan proses Hermes mandiri di `tmux`/job tahan lama dari root proyek, dan minta proses itu memperbarui berkas progres proyek serta halaman/status publik yang sudah disepakati. Simpan nama session, target waktu, dan aturan non-destruktif di brief agar pekerjaan bisa dilanjutkan setelah model/token berganti.
- **Pencegahan Shell Command Injection pada Prompt Panjang tmux:** Saat mem-pass isi markdown panjang atau instruksi multiline ke proses mandiri (`hermes chat -q ...`) di dalam `tmux new-session`, **dilarang menyisipkan string mentah langsung ke argumen shell**. Karakter backtick, quotes, atau path di dalam markdown akan di-parse oleh shell sebagai perintah executable (mis. `bash: /path/to/file: Is a directory` atau `Permission denied`), membuat proses crash seketika di latar belakang. Gunakan runner script terpisah (misal `/tmp/start-runner.sh`) yang membaca berkas brief secara aman lalu mengeksekusi launcher.
- **Konsistensi Spesifikasi Produk (PRD Grounding First):** Sebelum memodifikasi atau membuat ulang antarmuka kantor/arena, periksa terlebih dahulu seluruh berkas spesifikasi di blueprint dan core repository (`PRD.md`, `ARCHITECTURE.md`, `contracts/map_layout.json`, `event.schema.json`). Jangan pernah mereduksi atau mengarang jumlah ruangan/entitas secara sepihak (misal mengubah kontrak 11 ruang menjadi 9 ruang) tanpa dasar dokumen resmi.
- **Proyeksi Event Lifecycle Lengkap (Full Lifecycle Stream):** Simulasi atau replay event harus mencerminkan siklus hidup proyek nyata yang terverifikasi skema JSON: Kickoff (`MEETING_REQUESTED`), Keputusan Arsitektur (`DECISION_APPROVED`), Penugasan Paralel (`TASK_ASSIGNED`), Handoff Dokumen (`ARTIFACT_HANDOFF_COMPLETED`), Penanganan Isu (`TASK_FAILED` & `TASK_RESUMED`), hingga Penyelesaian (`PROJECT_COMPLETED`).
- Untuk mandat tanpa banyak komunikasi, bentuk jawaban chat harus pendek: sebut tindakan yang sudah dilakukan dan handle pemantauan. Hindari paparan panjang tentang penyebab kecuali diminta; pengguna menilai dari artefak berjalan.
- **Siklus Audit Mandiri Pasca-Eksekusi (Immediate Flaw Hunting):** Setiap kali satu batch eksekusi dan verifikasi otomatis tuntas, jangan berhenti pasif menunggu pengguna bertanya. Langsung lakukan audit sistemik menyeluruh untuk mengidentifikasi kekurangan berikutnya (spasial, interaksi, ergonomi ponsel, audio, dan kontinuitas state) dan sajikan temuannya secara proaktif.
- Bila ada ambiguitas yang benar-benar mengubah arah implementasi, ajukan satu pertanyaan dengan opsi pilihan ganda singkat dan rekomendasi pertama. Jika pilihan teknis aman dan reversibel, putuskan sendiri dan lanjutkan.

### 5. Penjadwalan Kerja Paralel (Parallel-First DAG Scheduler)
- Susun tugas sebagai grafik terarah asiklik (DAG), bukan antrean linear sekuensial.
- Jalankan riset UI, desain API, dan skema database secara paralel pada cabang waktu yang sama untuk memaksimalkan batas kecepatan Amdahl:
  $$S_{\text{latency}} = \frac{1}{(1 - p) + \frac{p}{s}}$$
- Gabungkan kembali seluruh cabang pada simpul integrasi (*integration milestone*) sebelum masuk ke tahap pengujian QA.

### 6. Verifikasi Gerbang Kualitas (Definition of Done)
- Setiap fase memiliki gerbang kelulusan tegas: `Implement → Run → Test → Inspect → Fix → Accept`.
- Haram menandai fase atau checklist sebagai `DONE` tanpa bukti empiris nyata:
  - **Fitur Visual:** Uji via browser headless (`browser_exec`), periksa box model/DOM, dan ambil tangkapan layar verifikasi (`capture_screenshot`).
  - **Fitur Runtime:** Periksa status HTTP 200 via `curl`, kode keluar terminal (exit code 0), dan assert payload JSON.
- Perbarui status di `state.json` hanya setelah bukti verifikasi terekam.
- Simpan riwayat perubahan yang dapat dibuka dari kantor, dengan pembedaan direncanakan, sedang dikerjakan, diterapkan, dan terverifikasi. Sertakan artefak atau hasil uji per perubahan; jangan tampilkan persentase selesai tanpa kriteria yang dapat dihitung.
- Saat pengguna menanyakan apakah eksekusi benar-benar berjalan, jawab dengan status worker terkini dan bukti perubahan yang sudah diperiksa, bukan daftar niat. Bedakan agen sedang berjalan, file sudah berubah, versi sudah disajikan, dan fitur sudah lolos uji; waktu modifikasi file saja tidak membuktikan fitur selesai. Jika pengguna frustrasi, hentikan penjelasan panjang dan lakukan koreksi langsung; hanya tanya jika keputusan teknis benar-benar bercabang, dengan opsi pilihan ganda singkat dan rekomendasi pertama.
- Validasi kesegaran aktivitas terpisah dari koneksi SSE: gunakan timestamp event dan tampilkan umur data, status belum diketahui, kedaluwarsa, atau terputus. Paket telemetri baru dapat membawa aktivitas lama; koneksi hidup dan jumlah layanan PM2 tidak membuktikan semua karakter sedang bekerja. Jangan isi keadaan awal dengan CPU atau tugas rekaan.

### 7. Peningkatan Kemampuan Terkendali (Tool Factory Gate)
- Klasifikasikan evolusi mandiri sistem ke dalam 3 tier keselamatan:
  - **Green (Low-Risk):** Pembaruan template, catatan Obsidian, rules deskriptif $\rightarrow$ Otomatis setelah unit test lulus.
  - **Yellow (Medium-Risk):** Pembuatan skill baru, skrip otomatisasi, plugin $\rightarrow$ Wajib melalui uji sandbox dan benchmark latensi.
  - **Red (Critical):** Perubahan orkestrator inti, gerbang keamanan auth, atau penghapusan permanen $\rightarrow$ Wajib meminta persetujuan eksplisit Mas Bagas.

### 8. Kanvas 2.5D Isometric & Navigasi A*
- Transformasi koordinat isometrik:
  $$x_{\text{iso}} = (x_{\text{grid}} - y_{\text{grid}}) \cdot \frac{W_{\text{tile}}}{2}, \quad y_{\text{iso}} = (x_{\text{grid}} + y_{\text{grid}}) \cdot \frac{H_{\text{tile}}}{2}$$
- Urutkan kedalaman render (*depth sorting*) agen berdasarkan $(x_{\text{grid}} + y_{\text{grid}})$ menggunakan Painter's algorithm agar objek depan menutupi latar belakang secara alami.
- Balon status karakter dibatasi maksimal 2–4 kata (*public work status*), dilarang menampilkan *chain-of-thought* atau *hidden reasoning*.
- **Integrasi Pointer API & Anti-Drag Misclick:** Gunakan Pointer Events (`pointerdown`, `pointermove`, `pointerup`, `setPointerCapture`) dengan ambang gerak (misal $\Delta > 4\text{px}$). Jangan memicu event klik/seleksi ruangan saat pointer dilepas bila pengguna berniat menggeser (*pan/drag*) kanvas.
- **Keterbacaan Label Ruangan di Kanvas:** Beri kontras pelindung (badge latar belakang semi-transparan dengan border tipis) pada nama ruangan di kanvas agar tetap terbaca jelas tanpa tertelan warna lantai atau tekstur diorama.
- **Elevasi Dinding 2.5D & Kejelasan Bagian Ruang:** Buat dinding belakang dengan elevasi ketinggian isometrik nyata ($H \approx 18\text{px}$) dan arsiran pencahayaan arsitektural untuk menegaskan pemisahan spasial 11 ruang daripada poligon datar di lantai. Berikan pola ubin grid isometrik subtil pada lantai dan celah lorong pintu masuk (`room.door`) agar batas ruang terbaca jelas dan proporsional.
- **Perabot Khas per Ruang & Densitas Spasial (Anti-Barren Space & Multi-Zoning):** Pasang perabot spesifik yang proporsional terhadap luas grid. Untuk ruangan besar ($14\times12$, $14\times14$, atau $28\times14$), dilarang menempatkan hanya satu perabot tunggal di tengah ruangan yang memicu sindrom "lautan kosong tandus" (65-75% void). Wajib membagi ruangan besar menjadi 2 hingga 3 sub-zona fungsional yang kohesif:
  - *Lounge & Breakroom:* 1) Zona perapian/hearth dengan panel akustik ber-downlight di dinding belakang; 2) Zona duduk santai dengan karpet luas, sofa modular bentuk L, meja kopi dengan cangkir mengepul, dan lampu lantai lengkung; 3) Zona barista espresso bar dengan kursi tinggi; 4) Zona meja kerja tasting komunal dengan laptop terbuka.
  - *QA Lab:* 1) Zona bangku uji osiloskop ganda dengan gelombang sinus animasi dan lampu kerja LED; 2) Zona device farm multi-perangkat dengan ponsel/tablet berlayar menyala; 3) Zona infrastruktur dengan server rack dan contamination sticky-mat di pintu masuk.
  - *Observation Center:* Meja kokpit operator melengkung, video wall CCTV 6-layar pada rangka baja vertikal dengan gelombang telemetri, dan menara server enterprise ganda dengan kabel jaringan snaking.
  - *Knowledge Vault:* Rak buku mahoni 3 tingkat berarsitektur 3D tebal dengan jajaran buku miring beraksen emas, meja studi perpustakaan kayu ek dengan lampu banker hijau zamrud, buku terbuka, dan karpet permata berumbai.
- **Ambient Occlusion & Contact Shadows (Grounding Rule):** Setiap objek furnitur isometrik, pot tanaman, dan avatar wajib memiliki bayangan kontak jatuh (`ctx.fillStyle = 'rgba(0,0,0,0.45)'` atau gradien elips lembut) tepat di bawah alasnya. Ketiadaan bayangan membuat aset terlihat seperti stiker datar 2D yang melayang di atas lantai grid.
- **Depth-Sorting Multi-Lapisan pada Perabot Majemuk:** Untuk set perabot komposit (seperti meja konferensi dan kursi), wajib menerapkan 3-fase render kedalaman: 1) Render kursi belakang terlebih dahulu $\rightarrow$ 2) Render badan dan permukaan meja (menutupi kaki kursi belakang secara alami) $\rightarrow$ 3) Render kursi depan dengan koordinat $Y$ di luar lis tepi beveled bawah meja. Ini mencegah bug z-indexing kursi yang tampak tenggelam di atas meja.
- **Pemisahan Spasial Avatar, Layar, dan Tipografi (Zero-Collision Geometry):**
  - Letakkan layar presentasi, papan tulis, atau papan metrik CI/CD menempel tinggi di dinding belakang atau digeser lateral menjauhi posisi berdiri avatar agar tidak terhalang gelembung status.
  - Pisahkan sumbu vertikal tipografi: tempatkan badge nama agen berlatar kontras di bawah kaki ($iy + 13.5\text{px}$), dan apungkan gelembung status di atas kepala ($bodyY - 32\text{px}$ hingga $bodyY - 48\text{px}$) dengan ekor pointer menghadap ke bawah. Ini mengeliminasi 100% tumpang tindih teks.
- **Kordinat Proposional Relatif Zona (`room.zone`):** Hitung penempatan perabot relatif terhadap `room.zone.x`, `room.zone.y`, `room.zone.width`, dan `room.zone.height`, bukan koordinat grid absolut acak, untuk mencegah perabot keluar dari batas ruangan atau menembus koridor.
- **Fungsionalisasi Interaktif Penuh (Bukan Sekadar Kartu Statis):**
  - *Inspektor Artefak*: Klik kartu artefak wajib membuka modal spesifikasi utuh yang menyajikan isi kontrak nyata (OpenAPI, SQL DDL, markdown), status lifecycle, produsen/konsumen, dan verifikasi checksum SHA-256 dengan tombol salin.
  - *Work Graph Terhubung ke Kanvas*: Node DAG dapat difilter (Semua, Selesai, Aktif), menampilkan dependensi serta deliverable saat diklik, dan menyediakan tombol untuk memfokuskan kamera kanvas langsung ke ruang kerja agen pelaksana.
  - *Knowledge Vault & Tool Factory Terintegrasi*: Panel terhubung ke kurasi catatan nyata di Obsidian (`BUKU_CATATAN/`) dengan pencarian teks langsung dan katalog tools terverifikasi dengan rasio percepatan (*speedup*) dan boundary keamanan.
  - *Snapshot Manifest 1-Klik*: Fitur backup menghasilkan manifest JSON terstruktur yang memuat snapshot komprehensif seluruh 11 ruang, 10 agen, work graph, dan artefak yang dapat diunduh.
- **Visual Ambang Pintu & Pintu Terbuka (Doorway Openings):** Pada dinding pembatas 2.5D, lubangi garis dinding pada koordinat `room.door` atau gambar keset lantai/ambang pintu berpendar agar pengguna melihat secara visual mengapa agen melangkah melalui titik tersebut tanpa ilusi menembus dinding padat.
- **Pelacakan Multi-Touch (Pinch-to-Zoom) pada Kanvas Mobile:** Gunakan `Map<pointerId, {x, y}>` untuk mendeteksi gestur 2 jari pada perangkat mobile; ubah skala `targetScale` berdasarkan jarak Euclidean kedua sentuhan tanpa memicu getaran pan.
- **Depth-Sorting Terpadu Antara Karakter dan Meja Majemuk:** Pisahkan proses rendering karakter menggunakan threshold kedalaman isometrik ($depth = gx + gy$): gambar Rear Agents ($depth \le 16$) sebelum furnitur, gambar meja dan perabot diorama, lalu gambar Fore Agents ($depth > 16$) sesudah perabot agar karakter di sisi utara meja terselip secara fisik dan alami di bawah meja.
- **Timeline Scrubber Interaktif pada Replay Stream:** Jadikan progress bar replay sebagai seekbar yang dapat diklik atau diseret (`jumpToReplayEvent(targetIdx)`) untuk melompat seketika ke event tertentu tanpa harus menekan tombol step berulang kali.
- **Manuver Menghindar Dinamis Antar-Agen (Lateral Dodging):** Saat dua agen bergerak berpapasan dalam jarak dekat ($< 1.1\text{ petak}$), hitung vektor perpendikular terhadap arah gerak dan terapkan simpangan sinusoidal halus pada sprite visual agar kedua agen tidak saling menembus tubuh (*ghosting clip*).
- **User Gesture Guard pada Sintesis Audio Latar Belakang:** Lindungi pemanggilan AudioContext (SFX/ambient drone) dari loop latar belakang dengan flag `hasUserGesture` yang baru aktif setelah pengguna pertama kali menyentuh atau menekan tombol di halaman, mencegah warning merah kebijakan autoplay konsol.

### 9. Isolasi Proyeksi Event & Pemisahan Command vs Event
- **Idempotensi & Strict Monotonicity:** Proyektor event klien wajib memvalidasi envelope event (`event_id`, `type`, `sequence`, `payload`). Tolak event dengan ID duplikat atau `sequence \le \text{cursor}` tanpa memajukan state cursor.
- **Pemisahan Eksplisit Command vs Event:** Draft perintah meeting (seperti `CreateProject`, `AssignTask`) yang dibuat secara visual wajib ditandai secara tegas sebagai draft lokal (`status: DRAFT_NOT_SENT`, `runtime_adapter: false`). Dilarang memicu mutasi state atau mengirim POST request siluman ke server tanpa persetujuan eksplisit.
- **Karakter Visual Awal:** Seluruh agen visual wajib diinisialisasi dalam status awal `UNKNOWN` tanpa tugas (`task: null`). Dilarang membuat status kerja palsu (*invented activity*) sebelum ada event replay atau event stream nyata yang diterima.
- **Pergerakan Berbasis Delta Time (dt):** Update pergerakan agen wajib mengalikan kecepatan dengan $\Delta t$ terukur (dibatasi clamp $\le 0.05\text{s}$) agar kelancaran gerak tidak bergantung pada frame-rate monitor dan tidak melonjak saat tab berpindah visibilitas.

### 10. Implementasi Protokol Saluran Full-Duplex Realtime (DAP v1)
- **Pemisahan Jalur Prioritas Kendali (Out-of-Band Priority Lane):** Pisahkan kanal kontrol prioritas instan (`INTERRUPT_ABORT`, `STEER_IN_FLIGHT`) dari aliran data reguler (`THOUGHT_DELTA`, `TOOL_INVOCATION`, `STATE_MUTATION`). Pesan interupsi wajib memotong antrean data dan langsung memicu pemutusan `AbortController`.
- **Instance Guarding pada Loop Token Asinkron:** Bungkus eksekusi token streaming bertahap dengan `AbortController` terisolasi dan validasi kepemilikan instance (`this.activeTasks.get(agent_id) === task`) sebelum memutasi status akhir agar tugas yang dibatalkan tidak menimpa state.
- **Pengukuran RTT Empiris Realtime & Throughput Token:** Kirim heartbeat PING/PONG teratur dan hitung latensi bolak-balik seketika saat event `onmessage` penerima frame `PONG` tiba. Hitung running rate token per detik (`tok/s`) dan tampilkan metrik langsung pada pulau status HUD.
- **Transmisi Polimorfik dengan Fallback Mandiri & Resync Buffer:** Sediakan klien peramban polimorfik yang otomatis mendeteksi ketersediaan WebSocket RFC 6455 dan beralih ke mesin pekerja duplex terisolasi di memori (*in-memory duplex worker*) jika berada di balik reverse-proxy publik. Pertahankan ring buffer 64 frame terakhir di server untuk rekonsiliasi paket hilang saat reconnect.
- **Ergonomi Aliran & Penyorotan Semantik:** Sediakan tab pemilih konkurensi multi-agen di atas terminal duplex, penyorotan sintaks otomatis pada kata kunci verifikasi/galat/teknis, cooldown 300ms untuk mencegah banjir sinyal interupsi ganda, serta persistensi transkrip lokal per agen di `localStorage`.
- **Ekspor Forensik DAP v1 & Penautan Dokumen Artefak:** Sediakan dropdown penautan konteks spesifikasi dokumen langsung ke prompt arahan serta ekspor rekaman seluruh frame terstruktur (seq, channel, timestamp) dalam format JSON valid di samping log Markdown.
- **Kunci Pintasan Intervensi Cepat (Duplex Action Hotkeys):** Daftarkan hotkey global `Ctrl+Shift+X` (atau `Cmd+Shift+X`) untuk interupsi abort darurat seketika tanpa jeda navigasi mouse, `Ctrl+Enter` untuk pengiriman arahan langsung dari input teks, dan `Escape` untuk membatalkan fokus/menutup popup.
- **Server-Side Token Bucket Rate Limiting:** Pasang algoritma pembatas laju *Token Bucket* (misal burst 50 frame, isi ulang 25 frame/detik) pada gateway WebSocket duplex server (`duplex_runtime.js`) untuk memitigasi loop galat tak terhingga dari klien dan melindungi event loop Node.js sebelum memproses frame hulu.
- **Telemetri Variasi Latensi Jaringan (RTT Jitter Moving Average):** Hitung moving average jitter paket bolak-balik bersama latensi RTT murni (`jitter = 0.7 * jitter + 0.3 * |rtt - lastRtt|`) untuk mendeteksi instabilitas transmisi mikro sebelum memicu resync stream.
- **Mode Tampilan Ringkas (Compact Floating HUD):** Sediakan mode `.compact-hud` pada kartu Quick Inspector (terminal mini 80px) untuk menjaga keterlihatan kanvas diorama 100dvh pada layar ponsel ringkas (320px–390px).
- **Siklus Pembersihan Transkrip & Pembatalan Tugas Aktif:** Pembersihan transkrip agen wajib memanggil `interruptTask` terlebih dahulu sebelum mengosongkan state DOM/localStorage agar sisa token penalaran di latar belakang tidak menimpa ulang tampilan yang baru dibersihkan.
- **Pill Aliran Eksekusi Perkakas (Tool Invocation Stream):** Suntikkan penanda semantik terstruktur (`[PERKAKAS: nama_tool(args)]` dan `[HASIL PERKAKAS (ms): ...]`) langsung ke dalam aliran transkrip duplex dengan badge penyorot warna tersendiri (`.kw-tool`) agar eksekusi alat terlihat jelas di sela-sela pemikiran agen.
- **Pembeda Visual Aura Interupsi Spasial (Tactile Interrupted Aura):** Render cincin peringatan merah bergaris putus-putus berdenyut di lantai kanvas diorama saat status agen berubah menjadi `INTERRUPTED` untuk memberikan kepastian visual seketika bahwa proses telah dibatalkan secara paksa.
- **Penyaringan Kanal & Konten Transkrip (Channel & Content Filtering):** Sediakan filter instan (`Semua`, `Penalaran`, `Perkakas`, `Arahan`) dan pengukur akumulasi token total per sesi tanpa merusak integritas frame DAP v1.
- **Persistensi Transformasi Kamera Diorama:** Simpan parameter transformasi kanvas (`targetScale`, `originX`, `originY`) dengan debounce ke `localStorage['kantor_camera_transform']` dan pulihkan secara deterministik saat kanvas diinisialisasi.
- **HUD Banner Status Rekoneksi & Exponential Backoff:** Pancarkan event `reconnecting` dengan counter percobaan dan delay kalkulasi exponential backoff ($t = \min(8000, 1000 \times 1.5^{\text{attempt}})$), ubah warna indikator Top Bar ke amber berdenyut (`.hud-reconnecting`) agar operator terhindar dari ilusi bahwa agen sedang berpikir hening.
- **Pengukur Kuota Batas Laju Transmisi (Rate Limit Quota Gauge):** Lacak sisa token bucket klien secara lokal tersinkronisasi dan tampilkan bilah kuota taktis (`42/50 msg`) di Quick Inspector dengan transisi warna bahaya sebelum error `RATE_LIMIT_EXCEEDED` terpicu.
- **Tangkapan Layar ROI Terfokus Wilayah Agen (Agent ROI Crop):** Sediakan pembuatan kanvas off-screen terisolasi ($260 \times 260$) yang memproyeksikan koordinat isometrik agen terpilih ke resolusi tajam dengan bingkai taktis dan watermarking untuk dokumentasi insiden tanpa beban cropping eksternal.
- **Stempel Waktu Monotonik & Fade Decay pada Balon Ucapan:** Sisipkan penanda waktu `[HH:MM:SS]` pada balon ucapan agen dan terapkan pemudaran transparansi linier ($\alpha = \max(0, 1 - (t - 12)/3)$) setelah 12 detik agar percakapan lama tidak menyesatkan kronologi.
- **Konfirmasi Dua Tahap (Two-Phase Commit) pada Aksi Massal:** Lindungi tombol komando berdampak luas (seperti *Rapat Pleno Semua Agen*) dengan dua tahap: klik pertama mengaktifkan status konfirmasi bertenggat waktu 3 detik (`Yakin Rapat Pleno? (Klik Lagi)`), dan hanya klik kedua yang menjalankan mutasi spasial.
- **Pintasan Keyboard Kontekstual Berbasis State UI:** Alihkan pemetaan hotkey angka 1-6 ke tab samping secara otomatis saat dock terbuka (`.open`), dan pulihkan ke kontrol kecepatan kanvas saat dock tertutup tanpa menimpa fokus input.
- **Mode Kontras Tinggi Terminal (High-Contrast Mode):** Sediakan toggle layar terminal hitam murni (`#000000`) dengan border tegas dan penajaman kontras teks untuk kenyamanan operasional di lingkungan silau tinggi (WCAG AAA).
- **Off-Thread Web Worker Threading (Jank-Free 60 FPS Compute):** Pindahkan kalkulasi komputasi berat (pencarian rute kisi A*, formatting sintaks token, normalisasi matriks) ke file `arena_worker.js` mandiri via Web Worker asinkron (`postMessage` / `onmessage`) dengan batas waktu fallback sinkron 40ms. Ini mengunci Main Thread UI tetap pada 60 FPS bebas jank saat merender kanvas diorama bersamaan dengan banjir frame token duplex.
- **Dead-Reckoning Spline & Kinematika Spasial (Hermite Cubic Smoothing):** Pisahkan posisi komputasi kisi agen (`gridX`, `gridY`) dari posisi perenderan visual (`renderGridX`, `renderGridY`). Gunakan peluruhan kurva kubik Hermite atau faktor dead-reckoning eksponensial halus ($\Delta x = (x_{\text{target}} - x_{\text{render}}) \cdot \min(1.0, 18 \Delta t)$) agar visual agen tidak tersentak atau teleportasi saat terjadi lonjakan kedatangan paket jaringan dari soket duplex.
- **Side-by-Side Semantic JSON Specification Diff Viewer:** Sediakan penampil perbandingan visual dua kolom di Meja Komando yang mengevaluasi secara struktural perbedaan spesifikasi dasar (*baseline*) dengan usulan perubahan (*proposed*). Warnai penambahan kunci dengan hijau (`+`), modifikasi nilai dengan kuning (`~`), dan penghapusan dengan merah (`-`) untuk memvalidasi intervensi arsitektural sebelum dieksekusi.
- **Agent Inter-Mesh Topology Matrix (P2P Wire Mesh):** Lacak komunikasi inter-agen langsung (DAP v1) dalam bentuk matriks dua dimensi $N \times N$ pada tab Work Graph. Rekam jumlah paket (*packet counts*) dan volume bita (*bytes transferred*) antar-pasangan agen dengan pewarnaan heatmap intensitas untuk mendeteksi kemacetan koordinasi P2P.
- **Dual-Mode Communication Syntax (Machine Wire vs Human Operator):** Sintaks mikro terkompresi 5-baris (`[AKSI]`, `[BERKAS]`, `[UJI]`, `[STATUS]`, `[LANJUT]`) dialokasikan **khusus untuk protokol komunikasi kawat internal antar-agen (Inter-Agent Wire RPC / DAP v1)** guna menekan konsumsi token hingga 85% pada koordinasi latar belakang. Dilarang menggunakan format kaku ini saat berbicara dengan operator manusia; komunikasi dengan operator wajib diterjemahkan kembali ke dalam bahasa alami yang bersih, hangat, dan berstruktur manusiawi.
- **GLiDE Thinking Decision Engine (TDE, Uncertainty Gating & Safety Interlock):** Terapkan gerbang keyakinan model keputusan sebelum mengeksekusi tindakan atau perkakas:
  1. Hitung tingkat keyakinan (*confidence score*, $0.0 - 1.0$) dan distribusi probabilitas kandidat perkakas teratas.
  2. Jika keyakinan $\ge 85\%$, gunakan mode cepat **`FAST_PASS`** (eksekusi sub-25ms tanpa membuang token penalaran).
  3. Jika kondisi ambigu atau tugas berisiko dengan keyakinan $< 85\%$, picu otomatis mode **`DEEP_REASONING`** (*test-time compute*) untuk menimbang dampak sebelum bertindak.
  4. Pasang **Safety Interlock**: jika tindakan tergolong berisiko tinggi (*abort*, *hotpatch*, *drop/reset*) dan skor keyakinan $< 70\%$, kunci eksekusi secara otomatis dan wajibkan konfirmasi otorisasi eksplisit dari operator.
- **Persistent Simulation State & Offline Time Catch-Up (Anti-Fake Continuity):** Simulasi kantor virtual atau alur kerja multi-agen wajib mempertahankan state secara berkelanjutan melintasi refresh browser atau penutupan tab.
  1. Simpan kursor event, state domain, dan koordinat agen ke storage persisten (`localStorage` / server state) secara periodik dan pada event `pagehide`/`beforeunload`.
  2. Saat halaman dibuka atau di-refresh, hitung delta waktu offline: $\Delta t = \text{Date.now()} - \text{timestamp}_{\text{terakhir}}$, lalu tentukan $\Delta \text{events} = \lfloor \Delta t / \text{durasi\_event} \rfloor$.
  3. Majukan (*fast-forward*) simulasi sebanyak $\Delta \text{events}$ tanpa mereset ke awal, sehingga agen terlihat terus bekerja di latar belakang secara otentik.
  4. Tangkap event `visibilitychange`: saat tab kembali aktif setelah diminimalkan, sinkronkan event yang terlewat seketika.
- **Canvas Raycasting, Clean Selection Transitions & Viewport Containment:**
  1. Seleksi entitas karakter dilarang mengunci raycasting denah ruangan.
  2. Klik pada karakter lain wajib langsung beralih seleksi (`selectedAgent = newAgent`), bukan mengunci ke aksi percakapan.
  3. Klik pada ruangan denah wajib membersihkan seleksi agen (`selectedAgent = null`) dan beralih menampilkan inspeksi ruangan.
  4. Klik pada lantai kosong di luar ruangan wajib melakukan deseleksi total (`selectedAgent = null; selectedRoom = null`).
  5. Tombol tutup pada floating inspector card wajib membersihkan referensi seleksi di mesin kanvas (`engine.selectedAgent = null`), bukan hanya menyembunyikan elemen HTML via CSS.
  6. Batasi tinggi kartu inspeksi melayang (`max-height: 52vh; overflow-y: auto;` pada mobile dan `max-height: calc(100vh - 140px)` pada desktop) agar tidak menutupi seluruh layar kanvas dan memblokir pointer event ke denah.
- **Adaptive Jitter Anomaly Guard (Sliding-Window Z-Score Detection):**
  - Menerapkan jendela geser 30 sampel RTT pada klien soket duplex (`duplex_client.js`).
  - Menghitung mean $\mu$ dan standar deviasi $\sigma$.
  - Menghitung $Z = \frac{\text{RTT} - \mu}{\sigma}$. Jika $Z \ge 2.5\sigma$ dan $\text{RTT} \ge 20\text{ms}$, picu event `jitter_anomaly`, sematkan kelas peringatan `.jitter-spike` pada `#hud-duplex`, dan tahan *burst* pengiriman paket token ke dalam leaky bucket pelindung hingga koneksi kembali normal ($Z \le 1.2$).
- **Spatial Micro-Rewind Ring Buffer (5-Second Time Travel Scrubber):**
  - Alokasikan circular ring buffer 300 frame (5 detik @ 60 FPS) di memori kanvas `arena_engine.js` (~150KB footprint, zero GC overhead).
  - Simpan snapshot koordinat agen (`gridX`, `gridY`, `renderGridX`, `renderGridY`, `bubble`, `state`) di setiap frame animasi.
  - Sediakan kontrol putar balik `Rewind 5d` (`#btn-rewind-5s`) dan floating scrubber dock (`#rewind-scrubber-bar`) dengan slider interaktif untuk menggeser waktu mundur frame-demi-frame dengan overlay visual holographic HUD `REWIND: -X.Xs`, serta tombol kembali ke waktu nyata (`exitMicroRewind`).
- **Direct Live Event Push via DAP v1 WebSocket:**
  - Dengarkan event `ARENA_EVENT` pada saluran WebSocket client (`duplex_client.js`) dan proyeksikan mutasi agen, status tugas, dan gelembung ucapan live stream langsung ke kanvas diorama Cat Tech HQ tanpa ketergantungan pada polling terputus-putus.
- **Alokasi Endpoint Kursi Mandiri vs Room Center (Zero-Endpoint Stacking Rule):**
  - Saat merekam atau memproyeksikan pergerakan agen ke suatu ruangan (pada event `TASK_ASSIGNED`, `AGENT_STATE_CHANGED`, atau perintah rapat), dilarang mengarahkan agen ke titik tengah ruangan secara statis (`roomCenter(roomId)`). Titik tengah ruangan adalah koordinat $(x,y)$ tunggal (biasanya tepat di atas meja radar atau meja rapat tengah). Mengirim banyak agen ke koordinat tunggal tersebut membuat avatar, lingkaran target (*destination reticle*), dan bayangan kontak mereka saling menindih di satu titik.
  - Wajib menggunakan sistem alokasi kursi/meja dinamis (`assignSeatForAgent()`) sehingga setiap agen memiliki titik tujuan (*destination endpoint*) unik yang terpisah, berjarak aman minimal 2–4 petak grid, dan bebas benturan.
- **Kebijakan Nol Data Rekayasa / Zero Dummy Data Policy:**
  - Antarmuka kantor otonom dilarang keras menampilkan data dummy atau status kerja rekaan yang terputus dari komputasi nyata.
  - Balon status dan telemetri agen pada mode live wajib terhubung ke endpoint status proses riil server (`/kantor/api/status`), mencerminkan status service PM2 aktual, cron jobs, performa host, dan catatan Obsidian Vault.
  - Jika memutar riwayat rekaman (seperti fixture 32-event `arena_events.ndjson`), wajib memberi label arsip `[REPLAY]` secara tegas dan transparan di HUD dan status bubble, sehingga operator dapat membedakan secara instan antara aktivitas langsung mesin (*live VPS telemetry*) dan penelusuran rekaman historis.
- **Interactive Scope Pruning & Plan Presentation Gate:**
  - Saat pengguna menginstruksikan untuk mengirimkan daftar rencana pengerjaan terlebih dahulu sebelum eksekusi (*"kirim list pengerjaannya dulu ke saya"*), sajikan daftar terstruktur dengan opsi konfirmasi dan rekomendasi pertama.
  - Ketika pengguna memangkas salah satu item (*"2 itu ngga perlu"*), patuhi pemangkasan tersebut secara mutlak, kecualikan dari rencana, dan langsung eksekusi seluruh item yang telah disetujui dalam satu siklus implementasi dan verifikasi terpadu.
