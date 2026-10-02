---
name: autonomous-office-arena
description: "Use when building multi-agent office operating environments."
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [arena, multi-agent, operating-environment, work-graph, dag, artifact-bus, continuous-execution]
    related_skills: [autonomous-orchestrator, hermes-autopilot, agent-speculative-execution]
---

# Autonomous Office Arena Operating Environment

Skill panduan untuk merancang, membangun, dan mengoperasikan lingkungan kantor digital otonom multi-agent (*Digital Company Arena*). Mengintegrasikan penjadwalan DAG non-linear, kolaborasi berbasis bus artefak, pelacakan progres publik *zero-downtime*, dan eksekusi berkelanjutan (*continuous uncapped execution*) tanpa merusak stabilitas runtime server.

## When to Use

- Membangun antarmuka komando multi-agent berskala besar yang mengadopsi metafora ruang kantor virtual (Meeting Room, Strategy, Research, Engineering, QA, Tool Factory, Vault, Archive, Observation, Backup).
- Menjalankan eksekusi tugas proyek jangka panjang yang berjalan secara otonom (*continuous execution*) melintasi banyak fase tanpa pengawasan manual langsung.
- Menyediakan dasbor pelacak progres publik real-time (*live progress tracker*) yang menampilkan roadmap, fase aktif, dan matriks checklist (selesai vs belum).
- Mengorkestrasi agen-agen spesialis menggunakan bus artefak terindeks (*content-addressed artifact bus*) dan penjadwal ketergantungan DAG paralel.

### Don't use for:

- Skrip tugas tunggal jangka pendek tanpa koordinasi multi-agent.
- Modifikasi liar pada runtime orkestrator inti (*core runtime*) tanpa izin eksplisit pengguna.
- Pembuatan antarmuka statis atau game visual murni yang tidak terhubung dengan state komputasi nyata.

## Core Mental Model: One Building = One Hermes

Kantor digital adalah batasan (*boundary*) utama dari satu instalasi Hermes yang utuh:
- **Meeting Room:** Meja komando utama Founder untuk memulai proyek (*Project Brief*), persetujuan risiko tinggi, dan pengalihan ruang lingkup.
- **Chief Orchestrator:** Mesin penjadwal DAG yang melepaskan tugas independen secara serempak ke lantai departemen.
- **Artifact Bus:** Jalur pertukaran dokumen resmi antar-agen (spesifikasi, arsitektur, skema DB, kontrak API, laporan pengujian).
- **Obsidian Brain & Archive Agent:** Otak penyimpanan memori jangka panjang terstruktur di `/otak-koding/` dengan pembersihan siklus hidup dokumen secara teratur.
- **Tool Factory:** Bengkel konversi friksi kerja berulang menjadi tools, skills, atau skrip otomatis terverifikasi.
- **Observation Center & Backup Room:** Pemantauan telemetri latensi/token serta snapshot pencadangan 1-klik untuk pemulihan bencana (*Disaster Recovery*).

Pola implementasi teknis terverifikasi untuk seluruh 8 subsistem inti di atas tersedia di `references/contracts-and-subsystems.md`. Panduan arsitektur frontend Game HUD, proyeksi minimap, sintesis audio Web Audio API, dan dock manajemen samping tersedia di `references/game-hud-and-tactile-ui.md`. Panduan de-stacking balon status multi-agent, 2D relaxation solver, dan arsitektur top-layer HUD tersedia di `references/canvas-spatial-hud-and-collision.md`.

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

## Pitfalls

1. **Server-Killing Restarts During Active Requests:**
   - *Mekanisme:* Agen otonom mencoba menambahkan rute statis dengan mengedit file server utama dan menjalankan `pm2 restart`. Ini seketika mematikan soket HTTP/SSE yang sedang melayani request pengguna, memicu galat `RemoteDisconnected` / *"Galat koneksi ke server pendamping"*.
   - *Solusi:* Gunakan rute dinamis wildcard (`/p/:project`) yang sudah aktif sebelumnya.

2. **Recursive Root Filesystem Scans:**
   - *Mekanisme:* Membiarkan instruksi agen menjalankan pencarian rekursif (`grep -rn` atau `find`) di direktori induk `/home/ubuntu/` yang sarat dengan folder `node_modules` dan lingkungan virtual Python.
   - *Solusi:* Tegaskan dalam direktif eksekusi untuk melarang grep rekursif dan wajib menulis berkas langsung ke path target pada giliran awal.

3. **Serializing Computation for Visual Metaphors:**
   - *Mekanisme:* Menunda atau menahan eksekusi logika komputasi hanya demi menunggu animasi langkah karakter sprite selesai berjalan di kanvas visual.
   - *Solusi:* Pisahkan *domain state* dari *visual state*. Agen di backend harus terus bekerja dengan kecepatan penuh; animasi visual di frontend hanya mencerminkan event stream secara asinkron.

4. **Unbounded Sub-Agent Delegation in Interactive Latency Loops:**
   - *Mekanisme:* Memanggil `delegate_task` di dalam handler perintah interaktif, memicu rantai penalaran latar belakang yang melebihi batas waktu gateway peramban/Cloudflare (30-45 detik).
   - *Solusi:* Batasi eksekusi interaktif pada giliran deterministik dengan tool native bawaan dan tetapkan batas waktu proses anak secara proporsional.

5. **Phantom Completion Assertions:**
   - *Mekanisme:* Menandai tugas "selesai" berdasarkan balasan teks model semata tanpa mengecek apakah berkas fisik benar-benar ada di disk atau server merespon dengan benar.
   - *Solusi:* Lakukan verifikasi file fisik (`ls -la`), pembacaan hash/konten, dan verifikasi curl HTTP sebelum mengumumkan penyelesaian tugas.

6. **A* Path Reconstruction Node Skipping:**
   - *Mekanisme:* Saat merekonstruksi jalur dari `came_from`, melewatkan penambahan node terdekat sebelum memajukan pointer `curr = came_from[curr]`. Ini menciptakan lompatan jarak koordinat ($> 1.5$) yang merusak animasi dan memicu diskontinuitas langkah.
   - *Solusi:* Selalu masukkan `path.append(curr)` sebelum memperbarui `curr = came_from[curr]` dan akhiri dengan `path.reverse()`.

7. **Sequence Monotonicity Violation in Event Streams:**
   - *Mekanisme:* Menerima event dengan `sequence` yang tidak menaik secara tegas ($\le$ `last_sequence`), menyebabkan race condition dan kondisi state yang tidak konsisten saat replay.
   - *Solusi:* Terapkan gerbang validasi keras `if seq <= last_sequence: raise ValueError` pada State Engine sebelum mengaplikasikan mutasi domain model.

8. **Conflating Status Dashboard with Dedicated Virtual Office Environment:**
   - *Mekanisme:* Saat diminta membangun kantor/arena virtual dengan dasbor pelacak, mengubur kanvas kantor hanya sebagai tab sekunder di dalam halaman pelacak administratif. Pengguna mengharapkan gedung kantor visual mandiri layar penuh (*"mana page kantor nya"*).
   - *Solusi:* Bangun dan terbitkan keduanya sebagai rute mandiri terpisah: dasbor pelacak di `/arena-tracker/` dan gedung kantor interaktif 100dvh di `/kantor/` (lengkap dengan HUD, room deck, dan inspector drawer).

8b. **Invisible Background Work During Monitored Runs:**
   - *Mekanisme:* Menjalankan subagent atau tmux worker tanpa menghubungkannya ke radar/progress page membuat pengguna melihat tidak ada gerakan walau file berubah.
   - *Solusi:* Sebelum menyatakan kerja otonom berjalan, pilih satu permukaan bukti yang dapat dipantau pengguna (`/arena-tracker/`, `/kantor/`, atau berkas progres yang disajikan publik) dan update permukaan itu setiap milestone. Jika radar belum terintegrasi, katakan belum terintegrasi dan tampilkan bukti di permukaan lain; jangan menyiratkan radar akan bergerak.

9. **Conversational Pausing During Uncapped Autonomous Mandates:**
   - *Mekanisme:* Memotong alur kerja untuk menanyakan izin atau klarifikasi minor di chat padahal pengguna telah menginstruksikan mandat otonom penuh lepas tangan (*"ngga usah jeda jeda terus aja bekerja, saya monitoring di web"*).
   - *Solusi:* Terus melangkah maju melintasi tahapan roadmap secara otonom dalam batch berkelanjutan, gunakan unit test dan assertions untuk memvalidasi gerbang, dan perbarui data live tracker web sebagai media pengawasan pengguna.

10. **Mocked Client-Only Controls Instead of Real Backend Execution:**
   - *Mekanisme:* Mengimplementasikan bilah perintah atau kontrol interaktif di halaman kantor hanya sebagai mutasi string lokal di JavaScript klien tanpa mengirim request ke server dan tanpa mengeksekusi proses nyata. Pengguna memprioritaskan berjalannya sistem operasional nyata di atas simulasi kosmetik.
   - *Solusi:* Selalu hubungkan bilah perintah dan kontrol visual 100% ke backend nyata (`/api/command`, `/api/live-stream`), tampilkan jendela output melayang (*floating output card*) yang merender stdout/stderr terminal dan tautan aktif, serta salurkan telemetri CPU/RAM server via Server-Sent Events.

11. **Replacing User-Provided Diorama Assets with Abstract Wireframes:**
   - *Mekanisme:* Ketika pengguna melampirkan aset gambar otentik (misalnya peta diorama game *Cat Tech HQ*), menggantinya dengan kisi geometris abstrak yang kaku merusak estetika dan visi produk yang diinginkan.
   - *Solusi:* Jadikan aset gambar resolusi tinggi tersebut sebagai panggung utama kanvas visual (*living game diorama*), lalu petakan poligon ruangan, karakter agen, dan balon status mengambang tepat di atas koordinat karya seni tersebut.

12. **Replay-Dependent DOM Query Failures in QA Automation:**
   - *Mekanisme:* Skrip QA browser yang mencoba mengklik elemen dinamis (seperti `.artifact-card`) pada langkah replay awal sebelum event penciptaan artefak (`ARTIFACT_CREATED`) terproyeksikan akan mengalami error `null` atau `false` assertion.
   - *Solusi:* Majukan kursor replay secara deterministik (`while(projection.cursor < N) stepReplay()`) hingga event yang memunculkan elemen tersebut selesai diproses sebelum menguji interaksi elemen anak.

13. **Mock Harness Context Pollution on Zero-Emoji Assertion:**
   - *Mekanisme:* CLI browser automation tertentu (seperti `browser-use`) menyisipkan emoji penanda sesi internal ke dalam judul tab browser (`🐴`). Evaluasi zero-emoji yang memeriksa judul tab melalui harness dapat menghasilkan false-positive kegagalan uji.
   - *Solusi:* Evaluasi kepatuhan zero-emoji langsung pada level DOM Chromium terisolasi (`document.querySelector('title').textContent` dan `document.body.innerText`) via CDP mentah atau Playwright tanpa prefix wrapper harness.

14. **Barren Ocean & Micro-Asset Syndrome in Scaled Grids:**
   - *Mekanisme:* Menggambar perabot berdimensi kecil di dalam grid ruangan besar ($14 \times 12$ atau $28 \times 14$) tanpa karpet pembagi zona atau kluster kolaboratif membuat kanvas tampak seperti pulau terisolasi di lautan kosong yang tandus, merusak estetika diorama miniatur 3D.
   - *Solusi:* Skalakan aset perabot secara volumetrik, tambahkan karpet zona (runner carpets), hubungkan workstation dengan tech island sentral atau lounge istirahat, dan manfaatkan perimeter dinding untuk papan presentasi, rak server, dan tanaman tropis.

15. **Z-Indexing Inset Glitch on Composite Isometric Furniture:**
   - *Mekanisme:* Menghitung posisi kursi depan menggunakan offset relatif yang jatuh di dalam poligon permukaan meja, menyebabkan kursi tampak melayang atau tenggelam di dalam kaca/kayu meja.
   - *Solusi:* Terapkan 3-phase depth rendering: gambar kursi belakang terlebih dahulu $\rightarrow$ gambar meja (yang secara alami menutupi bagian bawah kursi belakang) $\rightarrow$ gambar kursi depan dengan koordinat $Y$ strictly di luar tepi beveled bawah meja.

16. **Avatar and Speech Bubble Text Collision in Crowded Canvases:**
   - *Mekanisme:* Merender label nama agen tepat di atas kepala atau di bawah gelembung status tanpa kalkulasi tinggi dinamis menyebabkan teks nama dan pesan status bertumpuk dan tidak terbaca.
   - *Solusi:* Pisahkan sumbu vertikalnya: letakkan badge nama berlatar kontras tinggi di bawah kaki agen ($iy + 13.5\text{px}$) dan apungkan gelembung status di atas kepala ($bodyY - 32\text{px}$) dengan ekor pointer menghadap ke bawah.

17. **Barren Void in Large Isometric Rooms ($14 \times 14$ or larger):**
   - *Mekanisme:* Menaruh satu set perabot tunggal di pusat ruangan besar membuat 65-75% lantai menjadi ruang kosong tandus yang membuat pengguna merasa visualnya kurang terisi dan belum siap pakai.
   - *Solusi:* Pecah ruangan menjadi 2-3 sub-zona fungsional (misal: area duduk utama, bar kopi barista, dan meja kerja komunal) yang mengisi seluruh kuadran secara seimbang.

18. **Floating Decal Illusion from Missing Contact Shadows:**
   - *Mekanisme:* Menggambar perabot atau sprite diorama tanpa bayangan oklusi ambient membuat objek tampak seperti stiker 2D mengambang di atas garis grid kanvas.
   - *Solusi:* Gambar bayangan jatuh lembut berarsir (`rgba(0,0,0,0.45)`) di bawah alas setiap perabot, pot tanaman, dan kaki avatar sebelum merender badan objek.

19. **Stale Asset Caching in CDP Visual QA:**
   - *Mekanisme:* Chromium headless menyimpan cache skrip canvas engine secara agresif di memori. Pengujian tangkapan layar otomatis tanpa cache-busting akan memotret kode lama, menghasilkan feedback palsu bahwa perubahan visual belum terjadi.
   - *Solusi:* Selalu perbarui parameter versi URL di HTML (`?v=...`) dan panggil `Network.setCacheDisabled` dengan nilai `true` pada sesi CDP sebelum mengambil tangkapan layar verifikasi.

20. **Monolithic Document Page Flow vs Fullscreen Game HUD:**
   - *Mekanisme:* Membungkus kanvas kantor 2.5D di dalam container dokumen biasa dengan kartu berukuran terbatas (misal 580px) dan menumpuk panel manajemen di bawahnya secara vertikal. Ini memaksa pengguna melakukan scroll dokumen yang canggung dan merusak ilusi game diorama miniatur.
   - *Solusi:* Buat wrapper 100dvh dengan canvas `position: absolute; inset: 0;`, apungkan HUD bar di atas dan bawah, dan simpan seluruh panel manajemen di dalam sliding dock samping (`#game-dock`) yang dapat dibuka-tutup.

21. **Minimap Canvas Element Unbound to Engine Loop:**
   - *Mekanisme:* Membuat elemen `<canvas id="minimap-canvas">` di HTML tetapi tidak mengaitkannya ke instance engine (`arenaEngine.minimapCanvas = ...`). Metode `renderMinimap` tidak pernah dipanggil dan minimap tetap kosong/hitam saat loop render berjalan.
   - *Solusi:* Bind elemen minimap ke engine saat inisialisasi (`arenaEngine.minimapCanvas = $('#minimap-canvas')`), lalu render denah miniatur, highlight ruangan, dan blip agen di setiap frame loop animasi.

22. **Unconstrained Sidebar Container Breaking Mobile Compactness Invariants:**
   - *Mekanisme:* Tes QA seluler memeriksa kekompakan navigasi via `document.querySelector('.side').getBoundingClientRect().height < 180`. Jika kelas `.side` disematkan pada seluruh container dock samping yang memiliki `height: calc(100vh - 108px)`, assertion akan gagal di viewport seluler (`navHeight > 180`).
   - *Solusi:* Berikan kelas `.side` pada strip navigasi tab dock yang kompak (`height: 44px !important; position: static !important;`), bukan pada pembungkus panel geser secara keseluruhan, sehingga selalu memenuhi ambang batas < 180px di seluruh ukuran viewport.

23. **Disconnected Allowed Command Whitelist in Form Select Options:**
   - *Mekanisme:* Mengubah label opsi pada dropdown perintah (`<select id="meeting-kind">`) menjadi nilai string bebas (seperti `SPRINT_KICKOFF`) yang tidak terdaftar dalam whitelist `allowed` pada parser draf lokal (`createMeetingDraft`). Ini menyebabkan parser melempar error dan mencetak teks pesan error ke dalam blok `#meeting-draft`, yang kemudian gagal di-parse sebagai JSON (`SyntaxError: Unexpected token ... is not valid JSON`).
   - *Solusi:* Pastikan atribut `value` pada setiap `<option>` selalu identik dengan array whitelist perintah (`CreateProject`, `AssignTask`, `RequestMeeting`, dll.), dan gunakan deskripsi pengguna hanya sebagai inner text tampilan.

24. **GPU Fill-Rate Throttling from Stacked Backdrop-Filter Blurs in Game HUDs:**
   - *Mekanisme:* Menggunakan radius blur tinggi (`backdrop-filter: blur(16px/20px)`) pada beberapa layer HUD melayang secara simultan di atas kanvas animasi 60 FPS memaksa GPU memproses separable Gaussian blurs berulang-ulang, menyebabkan thermal throttling dan frame drop pada perangkat mobile/laptop.
   - *Solusi:* Kurangi blur ke level ringan (`6px/8px`) dengan latar belakang kaca gelap solid (`rgba(9, 13, 22, 0.94)`), matikan blur sepenuhnya di layar seluler (`backdrop-filter: none; background: rgba(8, 12, 19, 0.98)`), serta isolasi layer dengan `contain: paint layout;` dan `transform: translateZ(0); will-change: transform;`.

25. **Garbage Collection Stutter from Dynamic String Concatenation in Canvas RAF Loops:**
   - *Mekanisme:* Melakukan perakitan string warna dinamis (`ctx.fillStyle = m.color + alpha + ')'`) untuk puluhan partikel di setiap frame animasi menghasilkan ribuan alokasi string sementara per detik, memicu stutter periodik akibat jeda Garbage Collection V8.
   - *Solusi:* Gunakan konstanta `baseColor` tetap dan kendalikan transparansi partikel melalui `ctx.globalAlpha = alpha` dalam isolasi `ctx.save() ... ctx.restore()` untuk mencapai zero memory allocation per frame.

26. **Fixed-Height Header Wrap & Flexbox Overcrowding:**
   - *Mekanisme:* Menumpuk lebih dari 8 kontrol terpisah secara horizontal di bilah atas HUD tetap (`height: 52px`) memerlukan ruang lebar $> 1600\text{px}$. Pada monitor laptop 1366x768 atau 1440x900, elemen flexbox meluap atau terbungkus (*wrap*) ke bawah, menimpa kanvas dan memblokir interaksi klik pengguna.
   - *Solusi:* Terapkan arsitektur 3 zona dengan batas total lebar $\le 1040\text{px}$: Zona Kiri identitas kantor ($\le 300\text{px}$), Zona Tengah pulau status terpadu CPU/RAM/SSE/Ticker/Jam ($\le 280\text{px}$), dan Zona Kanan kontrol terpadu dengan pill tombol terkelompok (`SFX | AMB`) ($\le 450\text{px}$).

27. **Multi-Line Wrapping & Dangling Bullets in Compact Floating Docks:**
   - *Mekanisme:* Memaksakan beberapa status string panjang dan disclaimer statis ke dalam flex row kecil menyebabkan teks terlipat compang-camping menjadi 3 baris dengan tanda pemisah peluru (*bullet*) yang menggantung canggung, menciptakan kesan antarmuka rapuh dan berantakan.
   - *Solusi:* Kunci teks status dengan `white-space: nowrap; overflow: hidden;` dalam 1 baris horizontal tunggal yang tegas: hitungan progres tebal di kiri dan event aktif ber-ellipsis di kanan. Pindahkan disclaimer statis panjang ke dalam panel audit di sidebar.

28. **Mechanical String Slicing vs Standard Tactical Codes:**
   - *Mekanisme:* Memotong string nama ruangan/entitas secara mekanis dengan `slice(0, 6)` untuk menyesuaikan ukuran radar menghasilkan fragmen kasar seperti `Meetin`, `Strate`, `Resear`, `Observ` yang merusak estetika profesional.
   - *Solusi:* Gunakan tabel pemetaan akronim taktis 3-huruf resmi (`MTG`, `STR`, `RES`, `TOL`, `OBS`, `ENG`, `ARC`, `LNG`, `QAL`, `VAU`, `BKP`) dengan font monospaced tebal berkontras tinggi.

29. **Awkward Void Gaps from Mismatched Side Dock Height:**
   - *Mekanisme:* Mengubah bilah bawah dari balok penuh menjadi pulau komando melayang tanpa menyesuaikan properti `bottom` pada dock samping (tetap `bottom: 56px`) meninggalkan celah hitam kosong tak beraturan di sudut kanan bawah.
   - *Solusi:* Selaraskan dock samping agar membentang penuh hingga dasar layar (`bottom: 0 !important;`) sehingga membentuk pilar vertikal yang kokoh dan menyatu alami dengan kanvas.

30. **Agent Stacking & Sprite Collision in Multi-Unit Room Routing:**
   - *Mekanisme:* Mengarahkan banyak agen ke ruangan yang sama dengan menetapkan koordinat target ke titik tengah zona ruangan (`room.zone.x + width/2`, `y + height/2`) menyebabkan seluruh agen bertumpuk pada satu titik koordinat yang sama persis ($P(\text{Collision}) = 1.0$). Sprite, label nama, dan gelembung status saling menutupi dan tidak terbaca.
   - *Solusi:* Tetapkan titik kursi dan workstation mandiri (`seats: [{ id, roomId, label, gx, gy, facing, occupant }]`) di setiap ruangan. Alokasikan kursi kosong secara unik (`assignSeatForAgent`); jika kapasitas ruangan penuh, hitung offset berdiri di sekitarnya. Saat tiba, posisikan agen dalam pose duduk menghadap meja/workstation dengan koordinat unik.

31. **Direct-Tile Stacking during Social Interaction / Conversation:**
   - *Mekanisme:* Menyuruh agen berinteraksi atau berbincang dengan mengarahkannya tepat ke koordinat agen lain membuat keduanya saling bertabrakan dan menutupi sprite satu sama lain di petak yang sama.
   - *Solusi:* Terapkan pathfinding berjarak sosial aman (`talkToAgent`). Cari petak tetangga yang valid dan kosong di sekitar agen target (jarak sopan 1.0 - 1.2 petak grid). Saat tiba, hadapkan kedua agen satu sama lain dan picu pertukaran balon dialog multi-alur dengan aura kedekatan tanpa tabrakan.

32. **Passive-Only Quick Inspector Causing Poor Command Usability (UX Degradation):**
   - *Mekanisme:* Menjadikan kartu inspektor agen di kanvas hanya sebagai penampil metadata pasif ("Fokus Kamera", "Buka Detail") memaksa pengguna membuka dock samping yang padat dan mencari dropdown tersembunyi untuk memberi perintah.
   - *Solusi:* Transformasikan Quick Inspector menjadi Dek Perintah Taktis Langsung saat karakter dipilih di kanvas: sertakan pemilih pindah kursi ruangan, pemilih ajak bicara rekan, tombol aksi cepat 1-klik (`Rapat`, `Coding`, `QA`, `Lounge`), serta lingkaran retikel target berdenyut pada kanvas yang menunjukkan ke mana agen berjalan.

33. **Direct Canvas Action Omission in RTS Interfaces (Excessive Menu Friction):**
   - *Mekanisme:* Mewajibkan pengguna selalu membuka drawer atau dropdown menu untuk setiap perintah pergerakan atau percakapan agen menciptakan friksi interaksi yang tinggi.
   - *Solusi:* Terapkan standar interaksi game RTS langsung di atas kanvas: seleksi Agen A lalu klik Agen B langsung memicu `talkToAgent` (menghitung jarak sopan 1.2 grid dan memunculkan dialog); seleksi Agen A lalu klik kursi kosong langsung memicu `moveAgentToSpecificSeat` lengkap dengan cursor hover highlight. Sediakan pula tombol orkestrasi global 1-klik (`Rapat Pleno` dan `Kembali ke Divisi`).

34. **Empty Obstacles Set Causing Wall-Phasing Pathfinding:**
   - *Mekanisme:* Menginisialisasi `GridPathfinder` dengan set rintangan kosong (`new Set()`) menyebabkan rute A* menembus dinding pembatas 2.5D antar-ruangan secara garis lurus alih-alih keluar lewat pintu resmi (`room.door`) dan lorong koridor.
   - *Solusi:* Ekstrak koordinat dinding perimeter ruangan ke dalam `obstacles` pada pathfinder dan kecualikan lubang pintu (`room.door`) sebagai simpul yang dapat dilalui (*walkable*).

35. **Post-Replay Freeze & Wax-Museum Syndrome in Static Simulations:**
   - *Mekanisme:* Menghentikan pemrosesan saat replay event fixture terakhir selesai tanpa siklus aksi latar belakang membuat simulasi kantor mendadak mati dan membeku seperti museum patung lilin.
   - *Solusi:* Pasang mesin siklus kehidupan mandiri (*Autonomous Ambient Life Loop*) yang secara berkala memicu aktivitas wajar (menyeduh kopi di lounge, reviu papan tulis, rotasi giliran bicara rapat) saat replay dalam kondisi idle.

36. **Undeclared Global Helper Invocation with Optional Chaining (`ReferenceError`):**
   - *Mekanisme:* Memanggil fungsi utilitas yang belum dideklarasikan menggunakan optional chaining (seperti `showToast?.(...)` tanpa awalan `window.` atau deklarasi lokal `function showToast`) melempar `ReferenceError: showToast is not defined` di JavaScript runtime V8/Chromium. Ini seketika mematikan eksekusi skrip event handler sebelum mutasi DOM selanjutnya tercapai.
   - *Solusi:* Deklarasikan helper secara eksplisit pada lingkup modul (`function showToast(...)`) atau gunakan pengecekan aman `window.showToast?.(...)` / `typeof showToast === 'function'` sebelum pemanggilan.

37. **Non-Interactive World Fixtures & Static Scenery:**
   - *Mekanisme:* Menggambar perabot dunia penting (seperti mesin espresso, papan tulis arsitektur, rak server) hanya sebagai elemen visual kanvas pasif tanpa hitbox interaktif (`fixtures: [{ gx, gy, action }]`) membuat simulasi kantor terasa kaku dan mengabaikan interaksi eksplorasi pengguna.
   - *Solusi:* Daftarkan objek dunia penting dengan radius deteksi hover cincin holografik cyan dan aksi kontekstual (misal: klik mesin kopi mengarahkan agen rehat ke Lounge; klik papan tulis membuka tab Work Graph DAG).

38. **Single-Shot Dialogue Silence in Group Meetings:**
   - *Mekanisme:* Memicu rapat dengan menampilkan gelembung status satu kali lalu membersihkannya setelah timeout membuat seluruh agen di meja rapat terdiam kaku selamanya tanpa dinamika diskusi lanjutan.
   - *Solusi:* Implementasikan generator giliran bicara bertahap (*Turn-Taking Meeting Dialogue*) dengan agenda multi-babak terorkestrasi (pembukaan -> laporan arsitektur -> status backend -> validasi frontend -> hasil QA -> kesimpulan sprint -> pembubaran tertib ke meja kerja).

39. **Wall Collision without Visual Doorway Openings:**
   - *Mekanisme:* Algoritma A* sudah dipagari rintangan dinding dan keluar lewat koordinat pintu (`door: {x,y}`), tetapi perenderan visual dinding di kanvas (`renderRoomPartitions`) tetap menggambar garis dinding padat tanpa celah/ambang pintu. Pengguna melihat karakter tampak melangkah menembus garis dinding karena tidak ada visual kusen pintu (*doorway opening*) atau keset lantai (*door mat*) di titik koordinat pintu.
   - *Solusi:* Putuskan garis render dinding isometrik pada koordinat pintu atau gambar ambang pintu berpendar/keset lantai di titik `room.door` untuk menegaskan adanya jalan masuk fisik.

40. **Multi-Touch Jitter from Missing Pinch-to-Zoom Gesture Detection:**
   - *Mekanisme:* Penanganan event kanvas hanya melacak pointer tunggal (`isDragging = true` pada setiap pointerdown). Pada perangkat ponsel/tablet, gestur cubit (*pinch*) dua jari memicu dua event `pointermove` yang saling berebut variabel `dragStartX/dragStartY`, menyebabkan kanvas bergetar liar (*jitter*) alih-alih memperbesar atau memperkecil skala diorama secara proporsional.
   - *Solusi:* Simpan peta pointer aktif (`activePointers: Map<id, {x, y}>`). Jika `activePointers.size === 2`, hitung jarak Euclidean antar dua jari (`Math.hypot(p1.x - p2.x, p1.y - p2.y)`) dan ubah rasio skala kanvas secara mulus tanpa menggeser origin pan.

41. **Stale State Reference in Transient Canvas Popovers:**
   - *Mekanisme:* Mengikat teks status inspektor popover (`#qi-state`) hanya satu kali saat karakter diklik (`showAgentInspector`). Ketika agen menyelesaikan perjalanan dan berganti status (misal dari `WALKING` menjadi `WORKING` di kursi), teks popover tidak tersinkronisasi dan tetap menampilkan status kadaluarsa.
   - *Solusi:* Pasang sinkronisasi status real-time atau trigger listener pada event kedatangan agen (`onAgentStateChange` / `agent.onArrival`) untuk memperbarui DOM elemen inspektor aktif secara deterministik.

42. **Unbounded Timeout Accumulation in Turn-Taking Group Sequences:**
   - *Mekanisme:* Menjadwalkan rantai dialog multi-babak dengan `setTimeout` tanpa menyimpan array referensi ID timer-nya. Jika pengguna membatalkan rapat atau mengalihkan agen sebelum urutan selesai, timeout yang tertunda tetap dieksekusi di latar belakang dan memicu aksi sepihak (seperti memulangkan agen) di tengah aktivitas lain.
   - *Solusi:* Simpan seluruh timer aktif dalam array (`activeTimers = []`), dan sediakan metode pembatalan eksplisit (`clearAllTimers()`) yang dipanggil sebelum memulai urutan baru atau saat aksi kontradiktif (seperti *Kembali ke Divisi*) dipicu.

43. **Missing Empty-State Feedback on Live Roster Filter Search:**
   - *Mekanisme:* Memfilter kartu daftar elemen DOM murni dengan menyetel `style.display = 'none'` saat kueri pencarian tidak cocok, menyebabkan kontainer menjadi ruang kosong tanpa teks informasi apa pun.
   - *Solusi:* Pantau jumlah elemen yang terlihat setelah pemfilteran (`visibleCount = ...`); jika nol, tampilkan elemen placeholder *empty state* yang ramah (misal: `[Tidak ada divisi atau agen yang cocok]`).

44. **Depth Sorting Inversion between Agents and Composite Tables:**
   - *Mekanisme:* Merender seluruh perabot diorama di awal lalu merender seluruh karakter sprite sesudahnya membuat karakter yang duduk di sisi utara meja rapat (koordinat $Y$ lebih kecil dari meja) tampak mengambang di atas permukaan meja.
   - *Solusi:* Pisahkan siklus rendering karakter menggunakan ambang batas kedalaman isometrik ($depth = gx + gy$): gambar Rear Agents ($depth \le \text{threshold}$) sebelum perabot, lalu gambar perabot meja, dan akhiri dengan gambar Fore Agents ($depth > \text{threshold}$) setelah perabot agar karakter terselip rapi dan alami di bawah meja.

45. **Read-Only Replay Progress Bars without Scrubbing Controls:**
   - *Mekanisme:* Membuat bilah progres replay hanya sebagai display pengisian persentase pasif memaksa pengguna mengeklik tombol step berulang kali puluhan kali untuk mencapai event tertentu.
   - *Solusi:* Tambahkan event listener pointer/klik pada track progress bar (`jumpToReplayEvent(targetIdx)`), hitung rasio klik terhadap lebar track, dan lakukan reset serta fast-forward deterministik ke event yang dipilih seketika.

46. **Silent Replay Freeze in Exhibition / Kiosk Displays:**
   - *Mekanisme:* Menghentikan pemutaran replay saat mencapai event terakhir tanpa opsi pengulangan mandiri membuat tampilan dasbor kantor membeku di layar monitor publik.
   - *Solusi:* Sediakan toggle kendali putar ulang otomatis (*Auto-Loop Replay*); saat event terakhir tercapai, jadwalkan jeda countdown 3 detik lalu bersihkan dan putar kembali secara otomatis dari awal.

47. **Ghosting Sprite Penetration between Walking Agents:**
   - *Mekanisme:* Menjalankan pathfinding A* strictly per node tanpa deteksi jarak dinamis terhadap agen lain yang sedang berjalan berpapasan menyebabkan kedua sprite menembus tubuh satu sama lain saat berpapasan di lorong.
   - *Solusi:* Hitung vektor perpendikular lateral saat dua agen berpapasan ($dist < 1.1\text{ petak}$), terapkan offset sinusoidal menyamping sopan pada render sprite tanpa mengubah koordinat simpul rute dasar.

48. **Console Autoplay Policy Rejections in Autonomous Background Loops:**
   - *Mekanisme:* Memanggil generator audio (`AudioContext.resume()` atau instansiasi node) dari loop aktivitas latar belakang (*ambient life*) sebelum ada interaksi pengguna di halaman memicu penolakan dan warning merah di konsol browser.
   - *Solusi:* Bungkus pemanggilan audio dengan guard interaksi awal (`hasUserGesture: false`); pasang listener pada event `pointerdown`/`keydown`/`touchstart` pertama untuk membuka kunci audio secara aman.

50. **Unconstrained Camera Drag Bounds (Camera Void Loss):**
   - *Mekanisme:* Penanganan seret kamera pada `pointermove` tanpa batas clamping koordinat membuat kanvas diorama kantor dapat terlempar hilang sepenuhnya ke ruang hampa kosong (*infinite void space*).
   - *Solusi:* Batasi nilai `originX` dan `originY` dengan `Math.max(-maxPan, Math.min(maxPan, ...))` dan sediakan metode pemulihan cepat `recenterCamera()` (serta shortcut tombol `R`) untuk memusatkan kembali kamera seketika.

51. **Missing Walking Path Trajectory in RTS Movement:**
   - *Mekanisme:* Karakter melangkah menyusuri simpul A* tanpa visualisasi garis jejak lantai membuat rute pergerakan terkesan tidak dapat diprediksi dan membingungkan pengguna.
   - *Solusi:* Render garis putus-putus beranimasi (`setLineDash([4, 5])`) dan titik-titik waypoint bercahaya di lantai sepanjang sisa jalur `a.path` menuju kursi tujuan.

52. **Missing 1-Click High-Resolution Canvas PNG Export:**
   - *Mekanisme:* Antarmuka simulasi hanya menyediakan ekspor teks manifest JSON, tanpa fasilitas pengunduhan foto citra kanvas bersih untuk dokumentasi atau presentasi.
   - *Solusi:* Sediakan fungsi `canvas.toDataURL('image/png')` yang dapat dipicu 1-klik via tombol Top Bar (`Foto HD`) atau pintasan tombol `P`.

53. **Mouse-Only Roster Search Navigation Friction:**
   - *Mekanisme:* Mencari agen atau ruangan mengharuskan pengguna membuka panel samping dan mengklik input secara manual, memperlambat alur komando taktis.
   - *Solusi:* Sediakan shortcut keyboard global tombol `/` yang secara otomatis membuka dock samping dan memfokuskan kursor ke input pencarian roster.

54. **Flat Darkness in Midnight/Dark Ambient Themes:**
   - *Mekanisme:* Tema malam yang hanya menggelapkan background kanvas tanpa menyalakan lampu interior membuat bangunan terlihat suram dan dingin seperti ruangan mati.
   - *Solusi:* Render gradien radial lampu downlight hangat (`rgba(254, 240, 138, 0.22)`) di pusat setiap ruangan saat tema malam aktif untuk menciptakan estetika miniatur arsitektur yang hidup.

55. **Passive Scenery Doorway Thresholds:**
   - *Mekanisme:* Ambang pintu 3D hanya berfungsi sebagai dekorasi pasif tanpa deteksi hover/klik.
   - *Solusi:* Daftarkan koordinat `room.door` ke deteksi hover pointer; tampilkan pendaran halo portal neon, label portal taktis, dan fokuskan kamera ke ruangan saat pintu diklik.

56. **Static Status Badges in Real-Time DAG Work Graph:**
   - *Mekanisme:* Simpul tugas DAG hanya menampilkan warna statis per status, menyulitkan identifikasi seketika tugas mana yang sedang aktif diproses saat event stream berjalan.
   - *Solusi:* Terapkan kelas `.active-processing` dengan animasi CSS denyut cincin radar (`@keyframes dagPulse`) pada simpul tugas berstatus `ASSIGNED` atau `IN_PROGRESS`.

57. **Desynchronized Live Stream Status Tag (Zero Fake Claims Violation):**
   - *Mekanisme:* Menyetel badge status stream secara statis ke "LIVE SSE" berwarna hijau di Top Bar sementara koneksi telemetri sebenarnya terputus atau kedaluwarsa ($> 15\text{s}$) melanggar prinsip Zero Fake Claims dan menyesatkan pengguna.
   - *Solusi:* Sinkronisasikan badge status stream secara real-time dengan status EventSource (`onopen` -> LIVE SSE hijau, `onerror` / freshness timeout -> OFFLINE / KEDALUWARSA merah).

58. **Unanchored Multi-Touch Pinch-to-Zoom (Missing Midpoint Focal Anchor):**
   - *Mekanisme:* Menghitung rasio jarak dua sentuhan tanpa memperhitungkan titik tengah (*midpoint*) kedua jari menyebabkan kanvas membesar mengarah ke poros layar acak alih-alih area yang sedang dijepit pengguna.
   - *Solusi:* Hitung titik tengah `midX = (p1.x + p2.x)/2` dan `midY = (p1.y + p2.y)/2`, lalu sesuaikan `originX` dan `originY` berdasarkan koordinat spasial midpoint sebelum dan sesudah zoom.

59. **Microscopic Speech Bubbles on Zoom-Out:**
   - *Mekanisme:* Merender gelembung dialog dengan ukuran font tetap di kanvas yang di-zoom out ($\le 0.5$) membuat teks menyusut hingga menjadi buram dan tak terbaca ($\le 4\text{px}$).
   - *Solusi:* Terapkan skala terbalik (*scale-invariant scaling*) pada gelembung status: kalikan ukuran font dan dimensi padding gelembung dengan $\max(1, 0.85 / \text{scale})$ agar teks tetap tajam dan terbaca jelas pada level zoom apapun.

60. **Lost Character View in Large Buildings (Missing Camera Follow Mode):**
   - *Mekanisme:* Karakter yang melangkah melintasi gedung besar akan keluar dari bidang pandang kamera (*off-screen*) jika posisi kamera diam terpaku di titik asal.
   - *Solusi:* Sediakan mode kamera pengikut otomatis (*Camera Follow / Lock-On*) dengan interpolasi halus menuju koordinat agen aktif, dan nonaktifkan secara otomatis saat pengguna melakukan drag manual.

61. **Accidental Replay Reset Data Loss:**
   - *Mekanisme:* Menekan tombol reset atau pintasan panah kiri secara tidak sengaja memulihkan kursor event ke awal dan menghapus state proyeksi agen tanpa opsi pemulihan.
   - *Solusi:* Simpan `previousReplayIndex` sebelum reset, berikan toast notifikasi undo, dan sediakan pintasan tombol `Z` untuk melompat kembali ke event sebelum di-reset.

62. **Dark Unlit Workstations on Seated Working Agents:**
   - *Mekanisme:* Karakter yang berstatus `WORKING` di workstation tampak pasif seperti melamun jika monitor di depannya tetap gelap tanpa pendaran cahaya.
   - *Solusi:* Render kerucut pendaran cahaya monitor (*monitor screen light cone*) dengan animasi flicker lembut di atas meja kerja saat agen berada dalam status `WORKING`.

63. **Static Management Tabs without Dynamic Unread Badges:**
   - *Mekanisme:* Tab navigasi samping tidak menampilkan indikator jumlah artefak atau tugas baru yang tercipta dari event stream, memaksa pengguna mengecek tab secara manual.
   - *Solusi:* Sematkan elemen pill badge dinamis (`.dock-tab-badge`) pada tab navigasi samping yang terbarui secara otomatis saat entitas baru diproyeksikan.

64. **Click-Only Replay Scrubber (Missing Drag-to-Scrub):**
   - *Mekanisme:* Hanya menangani event `click` pada bilah progres replay tanpa melacak seretan pointer (`pointerdown`, `pointermove`, `pointerup` + `setPointerCapture`), membuat scrubbing kursor kaku dan tidak responsif terhadap geseran cepat.
   - *Solusi:* Implementasikan event Pointer API lengkap pada bilah progres (`setPointerCapture`) agar pengguna dapat menekan dan menggeser kursor scrub secara mulus layaknya video player modern.

65. **Unidentified Selected Agent in Spatial Radar:**
   - *Mekanisme:* Menggambar titik blip seluruh agen dengan ukuran dan gaya yang sama di minimap radar tanpa membedakan agen yang sedang dipilih pengguna, membingungkan navigasi taktis di denah gedung besar.
   - *Solusi:* Tambahkan cincin denyut beranimasi (*pulsing beacon ring*) dan titik putih kontras tinggi pada blip agen yang sedang aktif dipilih di radar minimap.

66. **Awkward Orphan Box on Minimized Radar:**
   - *Mekanisme:* Menyembunyikan kanvas radar saat diminimize (`display = 'none'`) tanpa menyesuaikan kontainer pembungkusnya, meninggalkan kotak kosong melayang yang canggung di sudut layar.
   - *Solusi:* Sematkan kelas `.collapsed` pada kontainer yang merampingkan padding dan ukuran pembungkus menjadi tombol lencana minimalis padat dengan ikon `+`.

67. **Visually Disconnected Inter-Agent Conversations:**
   - *Mekanisme:* Menampilkan balon percakapan pada dua agen yang sedang berdialog tanpa visual penghubung di lantai diorama, membuat keduanya terlihat seperti dua entitas terisolasi yang kebetulan memunculkan teks bersamaan.
   - *Solusi:* Render kurva gelombang resonansi akustik bergaris putus-putus berdenyut (*harmonic resonance curve*) dan riak elips lantai di antara kedua karakter yang sedang berbicara.

68. **Static Atmosphere vs Real-World Office Circadian Hours:**
   - *Mekanisme:* Menyajikan pilihan tema pencahayaan kanvas murni manual tanpa sinkronisasi jam kerja lokal, mengabaikan realitas operasional kantor.
   - *Solusi:* Sediakan mode `Atmosfer: Otomatis (WIB)` yang mendeteksi jam Jakarta secara real-time dan secara dinamis beralih antara tema Studio (siang), Sunset (senja), dan Midnight (malam).

69. **Missing Diorama Floating Room Banners:**
   - *Mekanisme:* Memfokuskan kamera ke suatu ruangan tanpa label 3D di kanvas diorama memaksa pengguna bolak-balik memeriksa teks sidebar untuk memastikan identitas ruangan.
   - *Solusi:* Apungkan spanduk holografis kaca 3D dengan label akronim divisi dan panah penunjuk berlian di atas pusat ruangan yang sedang difokuskan pengguna.

70. **Fullscreenchange State Desynchronization:**
   - *Mekanisme:* Hanya memperbarui teks tombol layar penuh di dalam event click tombol tanpa mendengarkan event native `fullscreenchange`. Saat pengguna keluar dari mode layar penuh menggunakan tombol fisik `ESC`, teks tombol tetap tertahan di 'Keluar Penuh'.
   - *Solusi:* Pasang listener `document.addEventListener('fullscreenchange', ...)` dan sinkronkan teks tombol serta status visual secara reaktif terhadap boolean `!!document.fullscreenElement`.

71. **Canvas Fixture Tab Selector Misalignment:**
   - *Mekanisme:* Menghubungkan klik objek kanvas ke selector CSS tab yang salah (misal `[data-tab="tab-work-graph"]` padahal elemen DOM menggunakan `data-tab="work-graph"`) membuat interaksi klik perabot diorama mati tanpa memicu pembukaan panel target.
   - *Solusi:* Selaraskan selector data-attribute dan buka dock samping (`#game-dock.classList.add('open')`) secara bersamaan saat fixture kanvas diklik.

72. **Uniform Audio Feedback Monotony across Critical Actions:**
   - *Mekanisme:* Memanggil synthesizer audio yang sama persis (`SoundFX.playChime()`) untuk seluruh aksi (dari kickoff sprint hingga hotpatch berbahaya) menghilangkan diferensiasi akustik taktis.
   - *Solusi:* Rancang profil frekuensi dan envelope khusus per jenis aksi: 4-note ascending fanfare untuk Kickoff, dual saw warning untuk Hotpatch, crystal pip ganda untuk QA, dan sub-bass write tone untuk Database backup.

73. **DPI-Adjusted Pointer Coordinate Mapping on Scaled Minimap/Overlay Canvases:**
   - *Mekanisme:* Menghitung koordinat klik langsung dari `(e.clientX - rect.left)` pada kanvas yang di-scale via CSS tanpa normalisasi rasio buffer canvas terhadap bounding rect (`canvas.width / rect.width`) menyebabkan koordinat klik melenceng pada layar HiDPI / retina atau kanvas dengan lebar responsif.
   - *Solusi:* Selalu normalisasi koordinat pointer dengan perbandingan dimensi buffer terhadap CSS client rect: `clickX = (e.clientX - rect.left) * (canvas.width / rect.width)` sebelum memetakan ke kisi ruang 2.5D.

74. **User Preference State Volatility across Browser Reloads:**
   - *Mekanisme:* Menginisialisasi seluruh slider volume, status audio SFX/Ambient, pilihan tema cahaya sirkadian, dan mode putar ulang kiosk ke nilai default statis di setiap pemuatan halaman membuat preferensi pengguna hilang saat refresh.
   - *Solusi:* Simpan konfigurasi pengguna ke `localStorage` (`kantor_vol`, `kantor_sfx`, `kantor_theme`, `kantor_speed`) dan muat kembali secara deterministik saat event `DOMContentLoaded` sebelum merender antarmuka.

75. **Monolithic Movement Velocity across Disparate Operational Priorities:**
   - *Mekanisme:* Menyetel kecepatan jalan konstan seragam (`speed = 6.0`) untuk seluruh agen membuat panggilan rapat darurat pleno (*Kickoff*) dan tugas krisis (*Hotpatch*) terlihat lambat dan santai seperti agen berjalan rehat menyeduh kopi.
   - *Solusi:* Terapkan kecepatan adaptif berbasis prioritas misi: percepat ke `speed = 9.0` saat panggilan Rapat Pleno, `speed = 8.0` saat intervensi krisis, dan `speed = 4.5` saat rehat santai, lalu pulihkan ke `baseSpeed = 6.0` saat tiba di kursi kerja.

76. **Invisible Character Boundary Clamping in Long-Form Directives:**
   - *Mekanisme:* Membatasi panjang teks `decision` secara ketat di backend/parser (maksimal 2000 karakter) tanpa indikator jumlah karakter langsung di formulir antarmuka menyebabkan pengguna tidak menyadari kuota tersisa dan berisiko mengalami error validasi saat teks terpotong.
   - *Solusi:* Sediakan widget penghitung karakter reaktif di bawah textarea dengan transisi warna peringatan (kuning saat $>1600$, merah saat $>2000$) sebelum formulir dipratinjau.

77. **Transient Session Command Overwrite (Missing In-Memory Draft Undo/History):**
   - *Mekanisme:* Menimpa output pratinjau draf perintah secara instan setiap kali tombol generate ditekan menghilangkan catatan draf sebelumnya dalam sesi kerja yang sama.
   - *Solusi:* Catat hingga 5 draf perintah terakhir dalam array memori sesi (`sessionCommandHistory`), tampilkan dalam chip/kartu riwayat dengan badge perintah dan timestamp, serta sediakan tombol "Muat Kembali" untuk mengisi ulang form secara otomatis.

78. **Missing Dynamic ETA and Path Distance at Waypoint Terminus:**
   - *Mekanisme:* Garis trajektori waypoint di kanvas hanya menampilkan jalur titik tanpa metrik jarak atau sisa waktu tempuh.
   - *Solusi:* Sematkan kapsul taktis melayang di simpul akhir jalur agen aktif dengan metrik sisa petak dan estimasi waktu tempuh detik (`[ETA: ${steps} petak · ${eta}s]`).

79. **Static Technology Racks in Living Factory/Datacenter Dioramas:**
   - *Mekanisme:* Menggambar unit komputasi dan pendingin server diorama sebagai kotak abu-abu statis dengan kisi ventilasi diam mengurangi kesan fasilitas industri teknologi aktif.
   - *Solusi:* Gambar rotor kipas pendingin mekanis dengan 3 bilah berputar dinamis (`rot = clockTime * 18`) di atas atap rak server cluster cold storage dan lab riset.

80. **Unsegmented Long Catalogs in Management Tabs (Missing Category Filter Pills):**
   - *Mekanisme:* Menampilkan katalog alat atau entitas dalam daftar linear panjang tanpa tombol pill filter kategori memaksa pengguna menggulir terus-menerus.
   - *Solusi:* Tambahkan baris tombol pill kategori (*Semua*, *Code*, *Data*, *Network*) dengan penyaringan DOM instan dan audio feedback klik.

81. **Unskewed Drop Shadows Breaking Isometric Sun Vector:**
   - *Mekanisme:* Menggambar bayangan kontak tanah tepat di pusat lingkaran avatar (`y + 0`) membuat kedalaman spasial 2.5D terasa mendatar.
   - *Solusi:* Geser proyeksi elips bayangan sedikit ke arah tenggara (`x + 2.5, y + 3`) selaras dengan sudut datang sinar matahari barat laut diorama isometrik.

82. **Static Minimap Canvas vs Tactical Live Radar Sweep:**
   - *Mekanisme:* Kanvas radar minimap hanya menampilkan denah kamar kotak pasif tanpa gelombang pemindai berputar layaknya instrumen radar taktis militer.
   - *Solusi:* Gambarkan jarum sapuan radar berputar (`(clockTime * 1.8) % 2PI`) dengan pendaran fosfor `rgba(56, 189, 248, 0.16)` dan lingkaran konsentris.

83. **Manual Selection Friction on Generated Command Drafts:**
   - *Mekanisme:* Mengharuskan pengguna menyeleksi dan menekan Ctrl+C manual pada teks JSON draf perintah di terminal/drawer meningkatkan risiko kesalahan blok dan friksi operasional.
   - *Solusi:* Sematkan tombol 1-klik 'Salin JSON' di atas textarea draf dengan integrasi Clipboard API, audio chime, dan toast notifikasi.

84. **Disconnected Home Station Context for Mobile Agents:**
   - *Mekanisme:* Saat agen bergerak mendekati rekan untuk berbicara di ruangan lain, hubungan visual ke meja kerja asalnya terputus.
   - *Solusi:* Gambarkan garis putus-putus tether emas animasi dari kaki agen ke kursi asalnya lengkap dengan lencana `[KURSI ASAL]` di atas kursi.

85. **Static Text Pops vs AI Typewriter Terminal Caret:**
   - *Mekanisme:* Memunculkan seluruh kalimat sekaligus pada balon ucapan agen terasa seperti papan statis.
   - *Solusi:* Sematkan kursor terminal berkedip `_` (`clockTime % 2 === 0 ? ' _' : ''`) pada teks balon ucapan kanvas untuk mensimulasikan transmisi pesan AI yang hidup.

86. **Simplex Polling & SSE Bottleneck vs Full-Duplex Agent Sockets (DAP v1):**
   - *Mekanisme:* Mengandalkan Server-Sent Events (SSE) atau polling periodik (2-3.5s) untuk telemetri agen membatasi komunikasi menjadi setengah-dupleks (satu arah hilir). Operator tidak dapat mengirim instruksi pengarah (*in-flight steering*) atau membatalkan proses yang terjebak loop tanpa memutus paksa koneksi ($P(\text{Intervensi} \mid \text{Running}) = 0$).
   - *Solusi:* Bangun saluran soket persisten dua arah (WebSocket Duplex Agent Protocol). Pisahkan antrean kontrol berprioritas tinggi (`INTERRUPT_ABORT`, `STEER_IN_FLIGHT` via `AbortController`) yang memotong antrean data reguler (`THOUGHT_DELTA`, `TOOL_RESULT`), mewujudkan interupsi sub-50ms tanpa buffer bloat.

87. **Async Loop Race Condition on Aborted Task Completion:**
   - *Mekanisme:* Menjalankan siklus penalaran asinkron bertahap (seperti `setTimeout` loop per token delta) dengan `AbortController` tanpa memeriksa kecocokan identitas instance tugas (`this.activeTasks.get(agent_id) !== task`). Ketika tugas lama dibatalkan di tengah eksekusi perkakas atau digantikan oleh tugas baru, callback asinkron dari tugas lama yang masih tersisa di event loop tetap menembakkan mutasi status `IDLE · GOAL_SATISFIED`, menimpa status pembatalan `INTERRUPTED` atau mengacaukan tugas baru.
   - *Solusi:* Pasang *instance guard* ketat di setiap langkah asinkron: `if (abortCtrl.signal.aborted || this.activeTasks.get(agent_id) !== task) return;` sebelum menembakkan mutasi status penyelesaian atau hasil eksekusi perkakas.

88. **Heartbeat RTT Measurement Timing Bias in Test Assertions:**
   - *Mekanisme:* Mengukur RTT jaringan dengan menghitung selisih waktu `Date.now() - client_time` setelah fungsi pengujian melakukan `sleep(N)` alih-alih mencatatnya seketika saat event `onmessage` penerima frame `PONG` terpanggil. Ini menggelembungkan hasil ukur RTT dengan durasi jeda sleep lokal, memicu kegagalan assertion batas latensi (false-positive).
   - *Solusi:* Catat timestamp kedatangan RTT seketika di dalam callback penanganan event `PONG` (`rtt = Date.now() - parsed.payload.client_time`), terpisah dari siklus tunggu atau evaluasi pengujian.

89. **Universal Fallback for Restricted Public WebSocket Upgrades:**
   - *Mekanisme:* Ketika antarmuka web diakses melalui reverse-proxy publik atau firewall yang membatasi upgrade soket mentah (`101 Switching Protocols`), menghentikan sistem duplex sepenuhnya memutus kemampuan interupsi operator.
   - *Solusi:* Sediakan klien duplex polimorfik yang otomatis mendeteksi kegagalan jabat tangan WebSocket dan beralih ke mesin pekerja duplex terisolasi di memori (*in-memory duplex worker*) dengan semantik `AbortController` dan `THOUGHT_DELTA` bertahap yang identik.

90. **Reconnection Stream Loss & Monotonic Sequence Gap:**
   - *Mekanisme:* Saat klien peramban memulihkan koneksi WebSocket setelah putus sementara atau tab diminimize, langsung mendengarkan aliran event baru melewatkan frame mutasi status dan token kesimpulan yang dipancarkan server selama masa terputus.
   - *Solusi:* Server gateway wajib menyimpan ring buffer terbatas (misal 64 frame terakhir). Saat rekoneksi berhasil, klien mengirim `RESYNC_STREAM` berisi `last_seq` tertinggi yang pernah diterima, dan server memutar ulang frame yang terlewat sebelum menyambung ke live stream.

91. **Auditory Fatigue from Monolithic Streaming Tone:**
   - *Mekanisme:* Memutar suara ketukan nada yang sama persis untuk setiap token yang mengalir (20-30 token/detik) menciptakan kelelahan pendengaran (*auditory fatigue*) dan rasa bising bagi operator.
   - *Solusi:* Sintesiskan micro-click berdurasi mikro (18ms) dengan frekuensi acak halus antara 1100-1300 Hz dan kurva eksponensial lembut; gunakan profil nada disonan ganda sawtooth turun (220/233Hz -> 80Hz) khusus saat sinyal interupsi darurat dipicu.

92. **Spatial Disconnection in Streaming Reasoners:**
   - *Mekanisme:* Agen mengalirkan pemikiran di terminal teks tanpa indikator visual pada kanvas diorama membuat operator kehilangan konteks fisik agen mana dan di ruangan mana proses tersebut sedang berjalan.
   - *Solusi:* Gambarkan riak cincin radio spasial berdenyut bergaris putus-putus (`setLineDash([3, 4])`) di atas lantai koordinat agen saat `isDuplexStreaming` bernilai benar.

93. **Input Selection Friction for In-Flight Steering:**
   - *Mekanisme:* Mengharuskan operator mencari dan mengeklik agen di kanvas terlebih dahulu sebelum dapat mengetikkan instruksi pengalihan arah (*in-flight steering*) memperlambat intervensi kritis saat agen mulai mengalami halusinasi atau drift.
   - *Solusi:* Dukung pengalamatan langsung via sintaksis `@agent` (misal `@backend <arahan>`) pada kolom input; lakukan parsing otomatis regex `^@([a-zA-Z0-9_]+)`, petakan alias, ganti seleksi inspektor aktif, dan kirimkan arahan dalam satu langkah cepat.

94. **Multi-Agent Streaming Blindspot & Concurrency Starvation in Single-Inspector Terminals:**
   - *Mekanisme:* Menampilkan aliran penalaran duplex hanya untuk agen yang sedang dipilih secara aktif di Quick Inspector menyebabkan operator kehilangan jejak saat beberapa agen spesialis mengeksekusi tugas secara bersamaan di latar belakang.
   - *Solusi:* Sediakan tab/pill pemilih konkurensi multi-agen di atas terminal duplex dengan indikator status denyut streaming aktif (`.streaming`); klik pada pill langsung mengalihkan inspektor dan memuat transkrip agen terkait secara instan tanpa memutus jalannya tugas agen lain.

95. **Unstructured Uniformity in Token Streaming (Semantic Keyword Blindness):**
   - *Mekanisme:* Merender aliran token penalaran AI sebagai teks mentah polos berseragam menyulitkan operator membaca cepat keputusan kritis di tengah ratusan baris log.
   - *Solusi:* Terapkan penyorotan sintaks semantik berbasis regex otomatis pada token: warnai hijau untuk kata kunci verifikasi/sukses (`PASS`, `INVARIANT`, `OPTIMAL`, `BERHASIL`), merah untuk kegagalan/intervensi (`ERROR`, `ABORT`, `INTERUPSI`, `FAIL`), cyan untuk primitif teknologi (`DATABASE`, `SQL`, `WAL`, `SOCKET`), dan kuning untuk arahan operator (`[PENGALIHAN]`, `[Lampiran]`).

96. **Volatile In-Memory Reasoning Transcripts (Session Loss on Reload):**
   - *Mekanisme:* Menyimpan log penalaran dan riwayat arahan duplex hanya dalam memori klien JavaScript membuat seluruh draf penalaran hilang seketika saat peramban dimuat ulang atau tertutup tak sengaja.
   - *Solusi:* Simpan riwayat transkrip per agen secara terikat ke `localStorage` (dibatasi buffer 10KB terakhir per agen dengan debounce tulis 500ms), dan pulihkan secara otomatis saat agen dipilih kembali di antarmuka.

97. **Context Injection Friction for Structured Artifact Directives:**
   - *Mekanisme:* Mengharuskan operator menyalin dan menempelkan manual kutipan dokumen spesifikasi (PRD, skema event, laporan audit) ke kolom arahan in-flight meningkatkan waktu reaksi dan risiko salah ketik.
   - *Solusi:* Sediakan dropdown pemilih artefak langsung di atas kolom arahan duplex yang secara otomatis menyematkan kutipan kontekstual ringkas (`[Lampiran: <Nama Dokumen> (...)]`) ke dalam input teks arahan saat dipilih.

98. **Double-Click Queue Flooding & Unthrottled Directive Bursting:**
   - *Mekanisme:* Ketiadaan mekanisme debounce atau visual cooldown pada tombol 'Arahkan' dan 'Interupsi' memungkinkan operator yang panik atau tidak sabar mengeklik tombol berkali-kali dalam hitungan milidetik, membanjiri antrean pesan server dengan duplikasi sinyal interupsi.
   - *Solusi:* Terapkan cooldown 300ms pada tombol aksi duplex (`btn.classList.add('cooldown')` dengan `pointer-events: none`) dan pulihkan kembali secara asinkron setelah jendela waktu proteksi berakhir.

99. **Lossy Text Summaries for Automated Third-Party Forensics:**
   - *Mekanisme:* Hanya menyediakan ekspor log transkrip dalam format naratif Markdown (`.md`) menghilangkan metadata teknis tingkat frame (nomor urut monotonik `seq`, kanal `control` vs `data`, timestamp presisi UNIX epoch, dan payload mentah) yang dibutuhkan oleh mesin evaluasi atau auditor otomatis.
   - *Solusi:* Sediakan tombol ekspor berkas JSON DAP v1 terstruktur (`dap-frames-<agent>-<timestamp>.json`) yang menyimpan rekam jejak utuh seluruh frame yang dipertukarkan selama sesi duplex.

100. **Foreground Background Race on Stream Clearing:**
   - *Mekanisme:* Mengosongkan transkrip agen di DOM tanpa membatalkan tugas streaming asinkron aktif terlebih dahulu memungkinkan token-token yang masih berjalan di latar belakang langsung menimpa ulang transkrip yang baru saja dibersihkan.
   - *Solusi:* Selalu panggil `interruptTask` sebelum memanggil `clearTranscript` dan memperbarui tampilan terminal.

101. **Unbounded Rate Limit Burst Loop in Duplex Client:**
   - *Mekanisme:* Klien duplex yang mengirimkan perintah arahan atau frame heartbeat tanpa perlindungan token bucket di server gateway dapat membanjiri event loop Node.js saat klien terjebak dalam loop kesalahan.
   - *Solusi:* Pasang algoritma Token Bucket (kapasitas 50 frame, refill 25 frame/detik) dengan penolakan instan `RATE_LIMIT_EXCEEDED` dan sinyal audio glitch khusus.

102. **Camera Reset Disorientation across Navigation Reloads:**
   - *Mekanisme:* Mengabaikan persistensi transformasi kamera (`scale`, `originX`, `originY`) memaksa pengguna memposisikan ulang kanvas diorama setiap kali halaman di-refresh.
   - *Solusi:* Simpan transformasi kamera dengan debounce ke `localStorage['kantor_camera_transform']` dan pulihkan secara deterministik saat engine diinisialisasi.

103. **Accidental Multi-Unit Disruption from Single-Click Mass Operations:**
   - *Mekanisme:* Memicu tombol aksi global berdampak luas (seperti memanggil seluruh agen ke ruang rapat atau mengembalikan semua agen ke divisi) hanya dengan satu kali klik tanpa konfirmasi. Klik tidak sengaja seketika merusak rute A* dan menghentikan investigasi spasial agen aktif.
   - *Solusi:* Terapkan pola Two-Phase Commit UI: klik pertama mengubah tombol menjadi status konfirmasi merah/amber berdenyut (`Yakin Rapat Pleno? (Klik Lagi)`) berdurasi 3 detik; mutasi spasial hanya dijalankan jika tombol diklik untuk kedua kalinya dalam jendela waktu tersebut.

104. **Invisible Quota Depletion in Token Bucket Rate Limiting:**
   - *Mekanisme:* Server gateway menerapkan pembatasan laju token bucket secara ketat tetapi klien tidak memiliki visibilitas sisa kuota, sehingga operator tiba-tiba terbentur penolakan `RATE_LIMIT_EXCEEDED` saat mengirimkan arahan berturut-turut.
   - *Solusi:* Modelkan token bucket klien lokal tersinkronisasi dan tampilkan bilah kuota taktis (`42/50 msg`) di Quick Inspector dengan transisi warna peringatan dinamis sebelum penolakan server terjadi.

105. **Loss of Agent Focal Detail in Full-Canvas Screenshots:**
   - *Mekanisme:* Mengambil tangkapan layar seluruh kanvas diorama ($1440 \times 900$) untuk melaporkan bug atau aktivitas spesifik satu agen menghasilkan gambar luas dengan sprite agen yang teramat kecil dan memerlukan pemotongan manual di aplikasi pihak ketiga.
   - *Solusi:* Sediakan fitur ROI Crop Snapshot menggunakan kanvas off-screen $260 \times 260$ yang memproyeksikan koordinat layar agen terpilih secara terpusat dengan bingkai sudut taktis dan metadata terstruktur.

106. **Stale Dialogue Confusion from Timestampless Speech Bubbles:**
   - *Mekanisme:* Balon ucapan agen di kanvas 2.5D tanpa stempel waktu dan tanpa pemudaran durasi membuat pesan lama tampak seolah baru diucapkan, membingungkan kronologi percakapan multi-agen.
   - *Solusi:* Bubuhkan stempel waktu monotonik `[HH:MM:SS]` di awal teks balon ucapan dan terapkan pemudaran transparansi linier ($\alpha = \max(0, 1 - (t - 12)/3)$) setelah 12 detik.

107. **Keyboard Hotkey Collision between Active Panels and Global Navigation:**
   - *Mekanisme:* Mendaftarkan hotkey angka global (1, 2, 5 untuk kecepatan replay) tanpa memeriksa state keterbukaan panel dock samping membuat penekanan angka saat bernavigasi tab memicu aksi kanvas yang tidak diinginkan.
   - *Solusi:* Kontekstualisasikan perutean keyboard: jika dock samping dalam status `.open`, prioritaskan angka 1-6 untuk berpindah tab dock samping, dan kembalikan ke fungsi kanvas hanya saat dock tertutup.

108. **Silent Socket Disconnections Misinterpreted as Agent Thought Loops:**
   - *Mekanisme:* Saat koneksi soket terputus di balik reverse-proxy, widget status hanya diam menampilkan RTT terakhir, membuat operator keliru meyakini agen sedang berpikir hening padahal komunikasi telah terhenti.
   - *Solusi:* Pancarkan event rekoneksi terstruktur dengan status exponential backoff (`reconnecting`) dan ubah visual Top Bar menjadi banner amber berdenyut (`DUPLEX: RECONNECTING (1/5)`).

109. **Multi-Agent Speech Bubble Stacking & Prop Occlusion in Dense Clusters:**
   - *Mekanisme:* Menampilkan balon ucapan/status agen berdimensi lebar (akibat timestamp detik dan teks tugas panjang) pada elevasi statis (`bodyY - 32px`) membuat balon saling bertumpuk dan menutupi perabot diorama di belakang agen. Selain itu, merender balon pada pass kedalaman agen menyebabkan meja konferensi atau partisi ruangan digambar di atas balon agen belakang.
   - *Solusi:* Pisahkan perenderan balon ke pass terpisah di lapisan teratas (*global top-layer overlay*) setelah seluruh geometri dunia selesai. Terapkan elevasi `headY = bodyY - 56px`, batasi teks hingga 18–20 karakter tanpa timestamp detik overhead, hilangkan balon kosong pada agen idle, dan gunakan 4-pass 2D relaxation solver untuk memisahkan balon yang berhimpitan secara vertikal (*altitude tiering*) dan horizontal dengan ekor penunjuk elastis.

110. **Linear Latency Averaging Masking Tail Jitter Anomalies (Missing Z-Score Guard):**
   - *Mekanisme:* Menghitung latensi bolak-balik (RTT) dan jitter hanya menggunakan rata-rata linier bergerak sederhana gagal mendeteksi lonjakan variasi transmisi mikro sebelum soket terputus. Pada koneksi seluler atau jaringan fluktuatif, lonjakan latensi mendadak tetap dibiarkan menyemburkan token burst hingga soket putus seketika (*socket drop*).
   - *Solusi:* Pertahankan sliding window 30 sampel RTT, hitung Z-Score statistik ($Z = \frac{\text{RTT} - \mu}{\sigma}$), dan aktifkan perisai peringatan dini serta penahanan burst token saat $Z \ge 2.5\sigma$ dan $\text{RTT} \ge 20\text{ms}$.

111. **Missing Spatial Pre-Incident History on Aborts (Unbuffered Time-Travel):**
   - *Mekanisme:* Saat terjadi anomali sistemik, kegagalan invarian, atau pembatalan paksa (*operator abort*), operator hanya disajikan koordinat akhir agen tanpa kemampuan menelusuri runtutan manuver spasial sesaat sebelum insiden terjadi.
   - *Solusi:* Simpan ring buffer 300 frame (5 detik @ 60 FPS) koordinat spasial seluruh agen di memori klien (~150KB, zero GC) dan sediakan kontrol scrubber taktil untuk memutar balik waktu secara instan frame-demi-frame.

112. **Ignoring User Scope Pruning Directives on Pre-Execution Lists:**
   - *Mekanisme:* Setelah menyajikan daftar rencana kerja yang diminta pengguna, mengabaikan instruksi pemangkasan pengguna (misal *"2 itu ngga perlu"*) dan tetap mencoba mengimplementasikannya membuang token dan memicu penolakan pengguna.
   - *Solusi:* Identifikasi dan kecualikan item yang dipangkas secara tegas, fokuskan implementasi hanya pada subset item yang disetujui, dan selesaikan semuanya dalam satu siklus eksekusi terverifikasi.

113. **Single-Point Room Center Routing Causing Destination Endpoint Stacking:**
   - *Mekanisme:* Mengarahkan agen ke ruangan dengan menyetel koordinat tujuan ke titik tengah ruangan secara statis (`roomCenter(roomId)`) menyebabkan seluruh agen yang ditugaskan ke ruangan tersebut bertumpuk pada satu titik koordinat yang sama persis (misal di atas meja radar Research Lab atau meja rapat Meeting Room), membuat avatar dan lingkaran retikel target saling menimpa.
   - *Solusi:* Arahkan selalu melalui alokasi kursi/meja individual (`arenaEngine.sendAgentToRoom`) yang memetakan agen ke stasiun kerja/kursi unik berjarak aman.

114. **Unlabeled Fixture Replay Mistaken for Live Agent Computation (Zero Dummy Violation):**
   - *Mekanisme:* Memutar rekaman fixture event simulasi tanpa label arsip yang jelas membuat pengguna mengira balon ucapan agen adalah status aktivitas instan server saat ini, lalu memicu kekecewaan saat menyadari bahwa status tersebut hanyalah teks rekaman statis (*"saya harap ngga ada yang dumy yang diisiini"*).
   - *Solusi:* Hubungkan status agen ke data telemetri riil server (`/kantor/api/status`) pada mode live, dan beri label penanda `[REPLAY]` eksplisit pada setiap event historis saat mode putar ulang dijalankan.








