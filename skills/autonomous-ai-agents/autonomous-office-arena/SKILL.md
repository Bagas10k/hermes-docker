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

Pola implementasi teknis terverifikasi untuk seluruh 8 subsistem inti di atas tersedia di `references/contracts-and-subsystems.md`.

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
- **Penerbitan Halaman Kantor Mandiri (`/kantor/` atau `/office/`):** Antarmuka 100dvh layar penuh (*fullscreen*) mandiri dengan:
  - Top Floating Glass HUD (telemetri agen, ruang kerja, beban CPU/RAM, jam WIB).
  - Kanvas 2.5D isometrik yang memakai kontrak dan engine resmi yang sudah ada (mis. `map_layout.json` 11 ruang dan `arena_engine.js`) sebelum membuat model alternatif. Jika perlu menyederhanakan tampilan, turunkan dari kontrak yang sama agar tidak memutus PRD. Jadikan kelancaran animasi sebagai target terukur, bukan klaim FPS tetap. Beri label karakter ilustratif bila belum terhubung ke identitas agen runtime.
  - Left Room Quick Navigator (pilih ruangan untuk zoom/fokus kamera seketika).
  - Right Slide-Out Inspector Drawer (buka profil tugas agen atau rincian workstation saat diklik).
  - Bottom Floating Command Bar (bilah perintah meja komando founder).
  - Sintesis Suara Taktil Web Audio API murni (klik segitiga 240 $\to$ 80Hz, dentang sinus 440 $\to$ 880Hz) tanpa file audio eksternal.
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

### 9. Isolasi Proyeksi Event & Pemisahan Command vs Event
- **Idempotensi & Strict Monotonicity:** Proyektor event klien wajib memvalidasi envelope event (`event_id`, `type`, `sequence`, `payload`). Tolak event dengan ID duplikat atau `sequence \le \text{cursor}` tanpa memajukan state cursor.
- **Pemisahan Eksplisit Command vs Event:** Draft perintah meeting (seperti `CreateProject`, `AssignTask`) yang dibuat secara visual wajib ditandai secara tegas sebagai draft lokal (`status: DRAFT_NOT_SENT`, `runtime_adapter: false`). Dilarang memicu mutasi state atau mengirim POST request siluman ke server tanpa persetujuan eksplisit.
- **Karakter Visual Awal:** Seluruh agen visual wajib diinisialisasi dalam status awal `UNKNOWN` tanpa tugas (`task: null`). Dilarang membuat status kerja palsu (*invented activity*) sebelum ada event replay atau event stream nyata yang diterima.
- **Pergerakan Berbasis Delta Time (dt):** Update pergerakan agen wajib mengalikan kecepatan dengan $\Delta t$ terukur (dibatasi clamp $\le 0.05\text{s}$) agar kelancaran gerak tidak bergantung pada frame-rate monitor dan tidak melonjak saat tab berpindah visibilitas.

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
