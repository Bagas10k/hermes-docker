---
name: technology-architecture-decision-intelligence
description: Use when choosing languages, frameworks, databases, libraries, runtimes, protocols, architectures, or dependencies. Enforces Problem-First, Constraint-Aware, Reusable, and Maintainability-Driven decision intelligence without popularity bias.
---

# HERMES TECHNOLOGY & ARCHITECTURE DECISION INTELLIGENCE

## Tujuan

Dokumen ini digunakan untuk membuat Hermes mampu memilih:
- Bahasa pemrograman
- Framework
- Library
- Database
- Protocol
- Runtime
- Deployment model
- Tooling
- Arsitektur
- Dependency

berdasarkan kebutuhan proyek yang nyata.
Targetnya bukan membuat Hermes memilih teknologi yang paling populer.
Targetnya adalah membuat Hermes memilih teknologi yang paling tepat untuk konteks, constraint, skala, maintenance, dan sistem yang sudah ada.

Prinsip utama:
```text
PROBLEM FIRST
TECHNOLOGY SECOND
```

---

## 1. CORE MINDSET

Hermes tidak boleh berpikir:
```text
Ada project baru → pilih stack favorit → mulai coding
```

Gunakan alur penalaran:
```text
USER GOAL
↓
REQUIREMENT ANALYSIS
↓
CONSTRAINT ANALYSIS
↓
EXISTING SYSTEM ANALYSIS
↓
SYSTEM CHARACTERISTICS
↓
TECHNOLOGY CANDIDATES
↓
TRADE-OFF ANALYSIS
↓
COMPATIBILITY CHECK
↓
RISK / MAINTENANCE CHECK
↓
DECISION
↓
BUILD
↓
VERIFY
↓
LEARN
```

---

## 2. GOLDEN RULES

- **DO NOT CHOOSE TECHNOLOGY BY POPULARITY:** Popularitas bukan bukti kecocokan arsitektur.
- **DO NOT ADD A LIBRARY WITHOUT A PROBLEM IT SOLVES:** Setiap dependency adalah liabilitas.
- **DO NOT REWRITE A WORKING STACK WITHOUT STRONG EVIDENCE:** Sistem yang bekerja memiliki nilai integrasi dan keandalan yang teruji.
- **DO NOT OPTIMIZE BEFORE A REAL BOTTLENECK EXISTS:** Hukum Amdahl & pengukuran empiris sebelum akselerasi.
- **DO NOT CONFUSE TECHNICAL ELEGANCE WITH BUSINESS VALUE:** Utamakan deliverable nyata Mas Bagas.
- **DO NOT OVERENGINEER PERSONAL OR SMALL SYSTEMS:** Sederhana saat sederhana cukup; kompleks hanya saat kerumitan dibutuhkan.
- **PREFER THE SIMPLEST TECHNOLOGY THAT SATISFIES THE REQUIREMENT:** Minimalkan permukaan kegagalan.
- **REUSE EXISTING STACK WHEN IT IS STILL FIT FOR PURPOSE:** Manfaatkan apa yang sudah stabil.
- **EVERY NEW DEPENDENCY HAS A COST:** Biaya pembaruan, kerentanan, dan pemeliharaan jangka panjang.
- **EVERY TECHNOLOGY DECISION MUST HAVE A REASON:** Tolak dogma atau kebiasaan tanpa argumen konkret.

---

## 3. REQUIREMENT ANALYZER

Sebelum memilih teknologi, Hermes harus mengurai:
- Apa yang sedang dibuat? Siapa penggunanya?
- Berapa skala pengguna? Apakah realtime diperlukan?
- Apakah high concurrency diperlukan? Apakah latency kritis?
- Apakah data besar? Apakah sistem distributed?
- Apakah AI/ML diperlukan? Apakah offline mode diperlukan?
- Apakah browser, desktop, mobile, CLI, atau server?
- Apakah sistem harus portable?
- Apakah resource VPS terbatas (misal: pagu RAM mutlak ≤ 9.0 GB)?
- Apakah deployment harus sederhana? Apakah maintenance harus ringan?

Output YAML terstruktur:
```yaml
requirements:
  product_type: [web/cli/api/daemon/desktop]
  users: [single-user/internal-team/public]
  scale: [low/moderate/high]
  realtime: [yes/no]
  concurrency: [single-thread/io-bound/cpu-bound]
  latency: [critical/relaxed]
  data_size: [small/medium/large]
  persistence: [sqlite/postgres/file/in-memory]
  security: [high/standard]
  deployment: [pm2/docker/systemd]
  maintenance: [minimal/active]
```

---

## 4. CONSTRAINT ANALYZER

Hermes wajib mengidentifikasi kendala keras (*hard constraints*) sebelum merancang solusi:
- Existing language & framework
- Existing database & state store
- Hosting environment & batas VPS: **RAM mutlak ≤ 9.0 GB**, CPU, Disk, Jaringan
- Skema autentikasi & privasi (`[REDACTED]` credentials)
- OS & Runtime (Linux Ubuntu 22.04 LTS, Node.js v26, Python 3.11)
- License requirements & API compatibility

---

## 5. EXISTING STACK FIRST

Sebelum menambah perkakas/teknologi baru, jawab pertanyaan uji:
```text
CAN THE EXISTING STACK SOLVE THIS?
```
- Jika **YES** $\longrightarrow$ **REUSE** (Gunakan kembali stack yang ada).
- Jika **PARTIALLY** $\longrightarrow$ Evaluasi ekstensi minimal (*minimal blast radius*).
- Jika **NO** $\longrightarrow$ Baru cari kandidat teknologi baru dengan justifikasi kuat.

---

## 6. TECHNOLOGY NECESSITY TEST

Untuk setiap library/teknologi baru, wajib menjawab 9 pertanyaan:
1. Masalah apa yang diselesaikan?
2. Mengapa stack yang ada saat ini tidak bisa menyelesaikannya?
3. Kerumitan apa yang ditambahkan?
4. Berapa biaya runtime & memori (RAM footprint)?
5. Berapa beban operasional yang ditimbulkan?
6. Berapa beban pemeliharaan jangka panjang?
7. Permukaan keamanan apa yang terbuka?
8. Bisakah teknologi ini dilepas / di-rollback dengan mudah nanti (*reversibility*)?
9. Apa mitigasi jika teknologi ini tidak lagi di-maintain?

Jika Hermes tidak dapat menjawab secara tegas: **PANTANG DITAMBAHKAN**.

---

## 7. MATRIKS SELEKSI TEKNOLOGI INTI

### Bahasa Pemrograman
- **Browser UI:** JavaScript untuk tooling ringan / prototype; TypeScript untuk proyek besar dengan shared types kompleks.
- **Python:** Wajib untuk AI/ML, data processing, scientific computing, PyTorch/scikit-learn, automasi script.
- **Node.js / TypeScript:** Web backend, realtime I/O (Socket.IO/WebSocket), API middleware, RDP tool proxy, event loop.
- **Go:** Single-binary CLI, high network concurrency, minimal memory footprint, background daemon performa tinggi.
- **Rust:** Memory safety critical, CPU-heavy parser (RTK), resource-constrained micro-services, low-level engine.

### Database & Persistence
- **SQLite (WAL mode):** Pilihan utama untuk single-node VPS, personal tools, observabilitas (AOMS), embedding storage, zero-config deployment.
- **PostgreSQL:** Multi-service concurrent writes, relasi kompleks, full-text search skala enterprise, partitioned tables.
- **Redis:** In-memory caching, rate-limiting, ephemeral pub/sub queues (hanya jika measured bottleneck ada).

### Realtime Communication
- **Polling:** Cocok jika updates jarang (> 5 detik) dan kesederhanaan mutlak diperlukan.
- **SSE (Server-Sent Events):** Server $\to$ Browser satu arah, auto-reconnect, lightweight stream.
- **WebSocket / Socket.IO:** Komunikasi dua arah sub-100ms, rooms/trace isolation, event semantics terstruktur.

### Arsitektur & Deployment
- **Modular Monolith:** Pilihan utama untuk personal VPS / small team. Hindari premature microservices!
- **PM2 / systemd:** Process manager standar tanpa overhead Kubernetes untuk single VPS.

---

## 8. TEMPLAT PENGAMBILAN KEPUTUSAN TEKNOLOGI (ADR)

Setiap keputusan arsitektur penting wajib diformulasikan:

```text
TECHNOLOGY DECISION RECORD

Problem:
... (Masalah nyata apa yang dihadapi)

Requirements:
... (Skala, latensi, ketersediaan)

Constraints:
... (RAM <= 9.0GB, OS Linux, runtime existing)

Existing Stack:
... (Teknologi yang sudah terpasang)

Need New Technology:
YES / NO

Candidates:
1. ...
2. ...
3. ...

Chosen:
... (Pilihan terpilih)

Why:
... (Argumen rasional & data empiris)

Rejected Alternatives:
... (Mengapa opsi lain digugurkan)

Compatibility & Blast Radius:
... (Dampak ke sistem yang berjalan)

Operational & Maintenance Cost:
... (Overhead pemeliharaan)

Reversibility:
EASY / MODERATE / EXPENSIVE

Confidence:
HIGH / MEDIUM / LOW

Verification Plan:
... (Bagaimana keputusan ini diuji secara empiris)
```
