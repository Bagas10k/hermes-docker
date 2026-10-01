# Hermes Digital Company Arena — Subsystem Implementation Patterns

Panduan arsitektur dan pola implementasi teknis untuk 8 subsistem inti Hermes Digital Company Arena yang telah terverifikasi melalui 30 unit tests deterministik.

---

## 1. Meeting Engine & DAG Task Release (Phase 5)

Command Table adalah antarmuka primer Founder untuk inisiasi proyek dan perubahan scope. Alur kerja tidak boleh melemparkan prompt bebas ke agen acak tanpa kontrak tertulis.

### Pola Implementasi:
1. **Kickoff Meeting:** Founder memanggil meeting (`create_meeting`) dengan topik, tipe rapat, dan daftar peserta agen (`attendees: ["hermes", "architect", "bekagent", ...]`).
2. **Project Brief & Decision Card:** Rapat merumuskan draf brief yang memuat cabang kerja paralel (*initial parallel tracks*). Sistem secara otomatis menghasilkan *Decision Card* bertatus `PENDING_APPROVAL` yang memerinci konsekuensi arsitektural.
3. **Persetujuan Instan & Splicing DAG:** Saat Founder menyetujui kartu keputusan (`approve_decision_and_release_dag`), mesin secara deterministik menyuntikkan setiap cabang tugas ke dalam `WorkGraphScheduler`, menandai rapat `RESOLVED`, dan merilis agen ke workstation masing-masing.

---

## 2. Work Graph DAG Scheduler & Cycle Detection (Phase 4)

Penjadwalan tugas harus berbasis grafik asiklik terarah (DAG) untuk memaksimalkan fraksi kerja paralel independen sesuai Hukum Amdahl.

### Pola Implementasi:
1. **Topological Sort & Kahn's Algorithm:** Lakukan validasi siklus (`detect_cycle`) sebelum menjadwalkan batch tugas berikutnya. Jika terdapat circular dependency ($A \to B \to A$), hentikan penjadwalan seketika dengan `RuntimeError`.
2. **Dynamic Ready Queue:** Tugas berstatus `READY` hanya jika seluruh simpul prasyarat (`dependencies`) telah berada di dalam himpunan `completed_tasks`.
3. **Exclusive Agent Leases:** Satu agen hanya dapat disewa oleh satu tugas aktif (`lease_agent`). Kunci sewa dilepaskan secara otomatis saat tugas selesai (`complete_task`).
4. **Concurrency Budget:** Batasi jumlah tugas berjalan simultan (`max_concurrency`) agar tidak melebihi kuota memori server atau rate limit provider LLM.

---

## 3. Content-Addressed Artifact Bus & Lineage (Phase 6)

Kolaborasi antar-agen tidak mengandalkan obrolan teks mentah, melainkan pertukaran dokumen resmi bertanda tangan hash.

### Pola Implementasi:
1. **Integritas SHA-256:** Setiap dokumen dihitung hash SHA-256 dari kontennya (`sha256:<hex>`). Jika dokumen dengan hash identik dimasukkan kembali, sistem menandainya sebagai duplikat dan menolak pembuatan versi redundant.
2. **Silsilah Versi (Lineage Graph):** Perubahan semantik mayor menghasilkan nomor versi baru (misal `v1.0` $\to$ `v2.0`) dengan atribut `parents: ["art_v1"]`. Dokumen induk otomatis ditandai `SUPERSEDED`.
3. **Structured Handoff:** Transfer kepemilikan dokumen (`execute_handoff`) memvalidasi pemegang saat ini (`current_holder == from_agent`), memindahkan ke `to_agent`, dan mencatat riwayat ke log audit serah terima.
4. **Archive Agent Retention:** Dokumen yang telah selesai digunakan diarsipkan secara permanen (`archive_artifact`) dengan metadata tanggal dan identitas agen pengarsip.

---

## 4. Scoped Obsidian Brain Vault Adapter (Phase 7)

Integrasi pengetahuan dengan Obsidian Vault (`/home/ubuntu/otak-koding/`) harus selektif dan higienis.

### Pola Implementasi:
1. **Format Standar Frontmatter:** Setiap catatan yang dibuat oleh agen wajib memiliki metadata YAML valid (title, date, author, category, tags).
2. **Value of Information (VOI) Scoped Retrieval:** Dilarang melakukan dump seluruh vault ke prompt agen. Jalankan pencarian bertingkat:
   - Pencocokan token judul berbobot tinggi ($\times 5$).
   - Kepadatan kata kunci pada cuplikan awal tubuh catatan ($\times 1$).
   - Pembatasan kategori direktori (misal `01_ARCH`, `04_ENGINEERING`).
   - Kembalikan hanya top-$k$ catatan paling relevan beserta cuplikan singkat.

---

## 5. Hermes Bridge & Delta Stream (Phase 8)

Menjembatani event runtime nyata dari hook Hermes CLI/Daemon (`pre_tool_call`, `post_tool_call`, `on_session_finalize`) ke Event Bus visual Arena.

### Pola Implementasi:
1. **Sequence Monotonicity & Gap Detection:** Setiap event yang masuk harus memiliki sequence nomor yang tegas menaik. Jika terdeteksi lompatan sequence ($seq > expected$), catat gap ke buffer rekonsiliasi.
2. **Delta Reconciliation:** Klien visual yang baru tersambung kembali dapat meminta delta perubahan (`get_delta_since(last_client_seq)`) untuk memutar ulang event yang terlewat tanpa reload total halaman.

---

## 6. Parallel Workspaces & Resource Mutex (Phase 9)

Mencegah tabrakan file antar-agen yang mengedit kode secara bersamaan.

### Pola Implementasi:
1. **Isolated Workspace Scratchpads:** Setiap tugas pengkodean dialokasikan sub-direktori kerja independen (`/tmp/arena_workspaces/<task_id>_<agent_id>/`) untuk isolasi mutasi file lokal.
2. **Fine-Grained Resource Locks:** Sumber daya yang benar-benar tunggal (misal: urutan migrasi database schema atau alokasi port daemon) dilindungi oleh mutex eksklusif (`acquire_lock` / `release_lock`).

---

## 7. Tool Factory & Benchmark Gate (Phase 10)

Otomasi sintesis alat untuk pola kerja berulang yang memicu inefisiensi.

### Pola Implementasi:
1. **Friction Tracker:** Catat setiap kali agen mengalami kendala atau menjalankan prosedur manual berulang. Jika ambang batas terlampaui ($\ge 3$ kali), buat proposal pembuatan tool otomatis (`propose_tool`).
2. **Empirical Sandbox Benchmark:** Uji kandidat tool dalam sandbox. Tool hanya boleh didaftarkan ke registri aktif jika rasio percepatan memenuhi batas minimal Amdahl ($\ge 1.1\times$ speedup).
3. **Instant Rollback:** Sediakan fungsi pemulihan instan (`rollback_tool`) untuk mencabut tool jika ditemukan regresi performa.

---

## 8. Observation Center & Bottleneck Diagnostician (Phase 11)

Mendiagnosis kemacetan alur kerja sistem tanpa memaksa manusia membaca log teks mentah.

### Pola Implementasi:
1. **Span Correlation:** Rekam setiap eksekusi sub-task dalam bentuk span terstruktur yang terikat pada `trace_id`.
2. **Dependency Stall Explainer:** Ketika sebuah proyek berhenti berkembang, sistem membandingkan daftar tugas belum selesai dengan prasyarat yang belum terpenuhi. Sistem secara otomatis merangkum daftar tugas yang terhambat beserta nama tugas hulu yang ditunggu, menyajikan status `DEPENDENCY_WAITING` yang jelas di antarmuka pengguna.

---

## 9. Full-Office Backup & Disaster Recovery Rehearsal (Phase 12)

Menjamin ketahanan sistem terhadap kehilangan data atau migrasi server.

### Pola Implementasi:
1. **Unified Backup Manifest:** Himpun seluruh target kritis (konfigurasi, profil agen, skills, catatan Obsidian, database proyek, state tracker) ke dalam satu arsip terkompresi `tar.gz`.
2. **Checksum Integrity Manifest:** Sertakan berkas JSON manifest yang memuat hash SHA-256 dari setiap berkas komponen dan hash total arsip.
3. **Dry-Run Restore Rehearsal:** Setiap proses pencadangan wajib diverifikasi melalui simulasi pemulihan di direktori sandbox sementara (`tempfile.mkdtemp`), memverifikasi kecocokan hash dan kelengkapan berkas sebelum menyatakan snapshot valid.
