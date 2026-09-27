# Autonomous Schema Evolution & Zero-Downtime Data Migration Patterns

Status: TESTED & SYNTHESIZED
Kategori: Arsitektur Basis Data & Migrasi Otonom (SQLite & PostgreSQL)
Tanggal: 2026-09-21
Rujukan Vault: [[SYSTEM/KNOWLEDGE_ENGINE]], [[KNOWLEDGE/BACKEND/LOGIKA-BACKEND-ENGINEER]], [[references/backend-debugging]]

---

## 1. Lensa Mekanistik-Kausal (Mechanism & Bounds)

### Model Keadaan Transisi Skema (State Transition Model)
Sistem penyimpanan basis data relasional dalam ekosistem aplikasi hidup didefinisikan sebagai fungsi transisi keadaan:
$$S_{t+1} = \mathcal{M}(S_t, D_t, C_t)$$
di mana:
- $S_t$ adalah skema relasional aktif pada waktu $t$.
- $D_t$ adalah himpunan baris data tersimpan.
- $C_t$ adalah himpunan kode aplikasi/kueri yang aktif melayani *traffic*.

Pada migrasi konvensional satu tahap (*naive atomic migration*), perubahan skema memutus kompatibilitas:
$$\exists q \in C_t \implies q(S_{t+1}) = \perp \quad (\text{Error: column does not exist / lock timeout})$$

Batas matematis latensi penguncian (*Lock Contention Bound*):
Waktu tunggu transaksi konkruen saat DDL memegang *AccessExclusiveLock* ($	au_{\text{lock}}$) memicu *cascade queueing*:
$$Q_{\text{depth}} = \lambda \cdot 	au_{\text{lock}}$$
Jika kedatangan *query* $\lambda = 500\text{ req/sec}$ dan migrasi memegang tabel selama $	au_{\text{lock}} = 4\text{ detik}$ (misal untuk `ALTER TABLE ... ADD COLUMN ... DEFAULT <expression>` pada engine non-metadata atau SQLite `ALTER TABLE`), kedalaman antrean melonjak hingga 2.000 transaksi tertahan, memicu *exhaustion pool* koneksi dan downtime sistem.

### Dekomposisi Expand-and-Contract (Fase 4-Tahap)
Untuk menjamin batas keras $Q_{\text{depth}} \approx 0$ dan toleransi silang $C_{\text{old}} \land C_{\text{new}}$:
1. **Fase 1: Expand (Aditif Murni)**:
   - Menambahkan kolom baru dengan nilai nullable atau konstanta instan (PostgreSQL 11+ mendukung default instan berbasis metadata pg_attribute tanpa *table rewrite*).
   - Kode lama ($C_v1$) tetap membaca/menulis skema lama tanpa menyadari kolom baru.
2. **Fase 2: Dual-Write & Bounded Chunk Backfill**:
   - Kode aplikasi ($C_v2$) melakukan penulisan ganda (*dual-write*) ke kolom lama dan kolom baru.
   - Pekerja latar (*background backfill*) mengalirkan data historis dalam potongan terikat (*bounded primary-key chunk*):
     $$\text{SELECT id, ... FROM table WHERE id > } id_{\text{last}} \text{ ORDER BY id ASC LIMIT } B$$
     (Haram menggunakan `OFFSET` karena kompleksitas $O(N)$ pindai B-tree; wajib menggunakan *keyset pagination* $O(\log N)$ dengan $B \in [1000, 5000]$).
3. **Fase 3: Switch Reads**:
   - Pembacaan dialihkan 100% ke kolom baru ($C_v3$). Kolom lama berstatus *write-only fallback*.
4. **Fase 4: Contract (Pembersihan)**:
   - Setelah masa observasi terbukti nihil *rollback* ($t_{\text{bake}} \ge 24-48\text{ jam}$), hentikan penulisan kolom lama, lalu eksekusi DDL destruktif/drop column.

### Perbedaan Mekanistik: SQLite vs PostgreSQL
- **PostgreSQL**:
  - DDL bersifat transaksional penuh (`BEGIN ... DDL ... COMMIT`).
  - Pembuatan indeks wajib menggunakan `CREATE INDEX CONCURRENTLY` di luar blok transaksi tunggal untuk menghindari *exclusive table lock*.
  - Menambahkan *constraint* besar wajib memakai metode 2-langkah:
    `ALTER TABLE ... ADD CONSTRAINT ... NOT VALID;` lalu `ALTER TABLE ... VALIDATE CONSTRAINT ...;` (mencegah *exclusive lock* berdurasi panjang).
- **SQLite (WAL Mode & Table Replacement)**:
  - SQLite mendukung `ALTER TABLE ADD COLUMN`, tetapi tidak mendukung drop column dengan tipe mutasi kompleks tanpa pembuatan tabel bayangan (*shadow table*).
  - Mekanisme aman SQLite:
    1. Buat tabel bayangan `_new_table` dengan struktur akhir.
    2. Salin data via `INSERT INTO _new_table SELECT ... FROM old_table`.
    3. Pasang pemicu atomik (*transactional swap*): `DROP TABLE old_table; ALTER TABLE _new_table RENAME TO old_table;`.
    4. Kunci SQLite PRAGMA: Selalu jalankan `PRAGMA foreign_keys = OFF;` saat migrasi skema dan aktifkan kembali setelah verifikasi `PRAGMA foreign_key_check;`.

---

## 2. Lensa Bayesian-Eksperimental (Evidence & Belief Updating)

### Kalibrasi Keyakinan Integritas Data
- **Prior Belief ($P(H_{\text{valid}})$)**:
  Estimasi awal bahwa proses migrasi menghasilkan keselarasan data tanpa baris *orphan* atau *null discrepancy* adalah $P(H) = 0.85$.
- **Likelihood Uji Invarian & Checksum ($P(E \mid H_{\text{valid}})$ vs $P(E \mid \neg H_{\text{valid}})$)**:
  Sebelum melakukan *read switchover*, sistem otonom wajib menjalankan probe verifikasi invarian:
  1. *Row count parity*: $|D_{\text{old}}| == |D_{\text{new}}|$.
  2. *Checksum hash sampling*:
     $$\text{MD5}(\text{CAST}(col_{\text{old}} \text{ AS TEXT})) == \text{MD5}(\text{CAST}(col_{\text{new}} \text{ AS TEXT}))$$
     pada sampel acak $10\%$ data atau $100\%$ baris termutasi terakhir.
  3. Uji *Shadow Dual-Write Invariant*: Selisih waktu mutasi $\Delta t < \epsilon$.
- **Pembaruan Posterior**:
  Jika seluruh probe invarian lolos ($E_{\text{all\_pass}}$) dengan false-positive rate $P(E \mid \neg H) < 0.001$:
  $$P(H_{\text{valid}} \mid E_{\text{all\_pass}}) > 0.9998$$
  Tingkat keyakinan: **KNOWN / TESTED** (Layak di-*switch* ke *production read*).

---

## 3. Lensa Desain Sistem & Optimasi (Structure & Trade-offs)

### Pareto Trade-off: Dual-Write App vs Database Triggers
| Metrik Evaluasi | Dual-Write di Application Layer | Database Triggers (DB Layer) | Shadow Table Replication (CDC/WAL) |
| :--- | :--- | :--- | :--- |
| **Overhead Latensi Transaksi** | Tambahan 1-3ms per HTTP/DB call | Sub-milidetik (in-engine) | Zero overhead pada transaksi utama |
| **Ketergantungan Deployment** | Butuh 3-4 siklus deploy kode terpisah | Cukup 1-2 siklus deploy kode | Butuh service replikasi eksternal |
| **Kompatibilitas SQLite** | Sangat baik & terkontrol penuh | Mendukung SQLite Triggers | Rumit (butuh ekstensi kustom) |
| **Resiko State Drift** | Sedang jika koneksi terputus | Sangat rendah (atomik DB) | Rendah (eventual consistency) |
| **Rekomendasi Ekosistem** | Standar microservice multi-node | Standar SQLite internal / monolith | Standar Postgres skala jutaan baris |

### Aturan Baku Invarian Autopilot untuk Migrasi Data Otonom
1. **Zero Raw Renames**: Dilarang mengeksekusi `ALTER TABLE ... RENAME COLUMN` secara langsung pada basis data produksi yang aktif melayani lalu lintas.
2. **Deterministic Bounded Batching**: Pengisian data historis (*backfill*) wajib dibatasi ukuran batch ($1.000 - 5.000$ baris per iterasi) dengan `sleep(10ms - 50ms)` antar batch untuk mencegah saturasi IOPS disk dan lonjakan replikasi lag.
3. **Automated Rollback Barrier**:
   Jika probe invarian mendeteksi $\text{discrepancy} > 0$ saat fase migrasi, sistem membatalkan *read switchover* secara otomatis, mematikan bendera *feature flag* pembacaan baru, dan kembali membaca kolom lama tanpa interupsi bagi pengguna.
