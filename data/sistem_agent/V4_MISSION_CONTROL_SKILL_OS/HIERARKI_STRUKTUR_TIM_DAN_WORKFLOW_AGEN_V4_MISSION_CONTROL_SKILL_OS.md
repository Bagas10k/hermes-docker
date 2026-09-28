# HIERARKI, STRUKTUR TIM MULTI-AGEN & WORKFLOW OPERASIONAL OTONOM — V4 MISSION CONTROL + SKILL OS
**Pencipta & Pemilik Sistem:** Bagas Saputra (Bagas Cihuy)  
**Dokumen Arsitektur Target:** `/home/ubuntu/otak-koding/SISTEM_AGENT/HIERARKI_STRUKTUR_TIM_DAN_WORKFLOW_AGEN.md`  
**Versi Revisi:** V4 — Mission Control Runtime + Skill Optimization OS  
**Status:** DOKTRIN OPERASIONAL RESMI — NON-DESTRUCTIVE EVOLUTION + LAZY CAPABILITY ROUTING  
**Tanggal Efektif:** 28 September 2026  

---

## 1. LATAR BELAKANG & DIAGNOSIS MASALAH

Sebelum perbaikan ini, ekosistem agen mengalami **friksi struktural (Structural Inefficiency)**:
1. **Pencampuran Peran (Role Smearing):** Tanggung jawab teknis web engineering, perbaikan bug, administrasi server, dan otomasi media sosial (Instagram @sputarai, @sputarball, TikTok) sering kali ditangani oleh proses tunggal tanpa isolasi konteks.
2. **Ketiadaan Siklus Belajar Berkelanjutan Terfokus (Missing Continuous Learning Loop):** Proyek otomasi media sosial (konten viral, analisis tren reels/TikTok, ML scoring) menuntut agen yang *belajar terus-menerus* terhadap pola engagement audiens dan algoritma platform. Jika dicampur dengan tugas coding frontend, agen kehilangan konsistensi observasi dan memori spesifik domain.
3. **Kebutuhan Rantai Komando yang Presisi:** Mempertegas hierarki komando mulai dari **Owner (Mas Bagas)**, **General Manager (Hermes)**, **Dispatcher Operasional (Bot 2 / @Bekbekk_bot)**, hingga **Armada Sub-Agen Spesialis Terisolasi**.

---

## 2. DIAGRAM SKEMA HIERARKI TIM LENGKAP

```text
========================================================================================
                         LEVEL 0: CHIEF ARCHITECT & OWNER
                              [ MAS BAGAS SAPUTRA ]
                   (Pemegang Hak Cipta, Veto Mutlak & Approval Akhir)
========================================================================================
                                       │
                                       ▼
========================================================================================
                     LEVEL 1: GENERAL MANAGER & ORCHESTRATOR
                            [ HERMES AGENT / @bakagent_bot ]
         (Konteks Global, Routing Strategis, Sintesis Hasil, Telegram Ruang Kerja)
========================================================================================
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
┌───────────────────────────────────────┐ ┌───────────────────────────────────────┐
│ LEVEL 2A: DISPATCHER & CONTROL TOWER │ │   LEVEL 2B: PENGAWAS KUALITAS (QC)   │
│     [ BIKAGENT BOT / @Bekbekk_bot ]   │ │         [ INVARIANT AUDITOR ]         │
│  • Pencatatan Buku & Log Obsidian     │ │  • Impeccable Anti-Slop Detector      │
│  • Mission/Task/Agent Registry         │ │  • Axe-Core WCAG AA Accessibility     │
│  • Scheduler, Progress & Dependency    │ │  • Playwright Verification Gate       │
│  • Background Jobs & Tugas Bising     │ │  • Evidence-based PASS/FAIL           │
│  • Notifikasi Grup BAgent (-100439..) │ │  • Independent from execution         │
└───────────────────────────────────────┘ └───────────────────────────────────────┘
                    │                                     │
                    └──────────────────┬──────────────────┘
                                       │
                                       ▼
========================================================================================
                      LEVEL 3: 4 DIVISI SUB-AGEN SPESIALIS TERISOLASI
========================================================================================

 ┌─────────────────────────────────┐     ┌─────────────────────────────────┐
 │ DIVISI 1: CONTENT & SOCIAL AI   │     │ DIVISI 2: WEB & UI/UX CRAFT     │
 │ (IG, TikTok, SputarBall, AI)    │     │ (Katalog, Dashboard, Landing)   │
 ├─────────────────────────────────┤     ├─────────────────────────────────┤
 │ • A1: Trend & Hook Decompiler   │     │ • B1: Design Token Architect    │
 │ • A2: Copywriter & Storyboarder │     │ • B2: Creative Frontend Builder │
 │ • A3: Media & Motion Renderer   │     │ • B3: Responsive QA Gatekeeper  │
 │ • A4: ML Scorer & Meta Sentinel │     │ • B4: Performance Optimizer     │
 └─────────────────────────────────┘     └─────────────────────────────────┘
                 │                                       │
 ┌─────────────────────────────────┐     ┌─────────────────────────────────┐
 │ DIVISI 3: INFRA, SECURITY & OPS │     │ DIVISI 4: CONTINUOUS LEARNING   │
 │ (PM2, Tunnel, Postgres, Docker) │     │ (Autopilot Engine & Vault Sync) │
 ├─────────────────────────────────┤     ├─────────────────────────────────┤
 │ • C1: PM2 & Ingress Sentinel    │     │ • D1: Trend & Skill Scout       │
 │ • C2: Supabase & DB Admin       │     │ • D2: Knowledge Distiller       │
 │ • C3: Passive Security Auditor  │     │ • D3: Memory & Context Curator  │
 │ • C4: Git & State Backup Vault  │     │ • D4: Experiment Sandbox Runner │
 └─────────────────────────────────┘     └─────────────────────────────────┘
```

---


## 2A. PENYEMPURNAAN LEVEL 2A — BIKAGENT SEBAGAI ORCHESTRATOR ASSISTANT / CONTROL TOWER

Struktur yang sudah berjalan **tidak diubah**. `HERMES AGENT / @bakagent_bot` tetap menjadi **General Manager & Strategic Orchestrator**, sedangkan `BIKAGENT BOT / @Bekbekk_bot` diperkuat menjadi **Operational Dispatcher + Orchestrator Assistant + Control Tower**.

### Pembagian otoritas yang dipertahankan

```text
MAS BAGAS
   │
   ▼
HERMES — Strategic Orchestrator
   │
   ├── BIKAGENT — Operational Control Tower
   │      ├── Agent Registry
   │      ├── Task Ledger
   │      ├── Progress Collector
   │      ├── Dependency Graph
   │      ├── Artifact Registry
   │      ├── Decision Log
   │      ├── Blocker / Escalation Manager
   │      └── Notification & Telemetry Router
   │
   └── INVARIANT AUDITOR — Independent Verification Gate
          │
          └── PASS / FAIL / RETURN FOR REVISION
```

### Prinsip tugas

**Hermes memutuskan pekerjaan apa yang perlu dilakukan.**  
**BIKAGENT mengetahui keadaan pekerjaan setiap saat.**  
**Sub-agen spesialis mengerjakan pekerjaan.**  
**Invariant Auditor membuktikan hasilnya memenuhi standar.**  
**Mas Bagas memegang veto dan approval akhir untuk tindakan kritis.**

### 2A.1 Agent Registry

BIKAGENT wajib menyimpan metadata ringkas seluruh sub-agen tanpa memasukkan seluruh konteks agen ke memori aktif Hermes.

```yaml
agent_id: B2
name: Creative Frontend & Motion Builder
division: WEB_UIUX
status: IDLE
capabilities:
  - react
  - vite
  - tailwind
  - motion
  - canvas
active_task: null
workload: 0
last_heartbeat: null
health: HEALTHY
```

Status agen:

```text
IDLE
READY
BUSY
WAITING
BLOCKED
REVIEWING
ERROR
OFFLINE
```

### 2A.2 Task Ledger

Semua tugas yang didelegasikan Hermes harus memiliki identitas dan kontrak yang konsisten.

```yaml
task_id: WEB-2026-001
project_id: HERMES-DASHBOARD
owner: HERMES
assigned_to: B2
reviewer: B3
objective: Implementasi halaman dashboard realtime
priority: HIGH
status: RUNNING
progress: 45
depends_on:
  - WEB-2026-000
artifacts: []
blockers: []
requires_owner_approval: false
```

Status tugas resmi:

```text
QUEUED
READY
ASSIGNED
RUNNING
WAITING_DEPENDENCY
BLOCKED
REVIEW_REQUIRED
VERIFYING
FAILED
COMPLETED
CANCELLED
```

**`COMPLETED` hanya boleh diberikan setelah acceptance criteria terpenuhi.**  
Jika tugas membutuhkan gate B3 / Invariant Auditor, maka `DONE` dari builder belum dianggap `COMPLETED`.

### 2A.3 Progress Collector

Setiap sub-agen wajib mengirim event progres kepada BIKAGENT pada perubahan state penting, bukan melakukan spam setiap langkah kecil.

Format minimum:

```yaml
task_id: WEB-2026-001
agent_id: B2
status: RUNNING
progress: 65
completed:
  - layout dashboard
  - event panel
current_action: integrating realtime socket events
blockers: []
need_decision: false
artifacts:
  - src/pages/Dashboard.tsx
next_action: responsive pass
confidence: HIGH
```

BIKAGENT kemudian merangkum informasi teknis tersebut menjadi laporan operasional untuk Hermes.

### 2A.4 Dependency Graph

BIKAGENT menjaga hubungan antar-task agar tugas hilir tidak berjalan menggunakan output yang belum siap.

Contoh Divisi Web:

```text
B1 DESIGN CONTRACT
       │
       ▼
B2 IMPLEMENTATION
       │
       ▼
B3 RESPONSIVE + QA GATE
       │
       ▼
B4 PERFORMANCE + DEPLOYMENT
```

Contoh lintas divisi:

```text
D1 Research
   │
   ▼
D2 Distillation
   │
   ├──────────► B1 Design Contract
   │
   └──────────► A1 Trend Intelligence
```

### 2A.5 Artifact Registry

Setiap output penting dicatat agar Hermes tidak perlu mencari ulang hasil pekerjaan.

```yaml
artifact_id: ART-WEB-014
task_id: WEB-2026-001
created_by: B2
type: source_code
path: /project/src/pages/Dashboard.tsx
version: 3
status: CURRENT
verified_by: B3
```

Jenis artefak dapat meliputi:

- source code
- `DESIGN.md`
- `theme.css`
- `tokens.json`
- hasil render
- laporan QA
- laporan keamanan
- hasil riset
- catatan Obsidian
- model/scoring report
- deployment manifest

### 2A.6 Decision Log

Keputusan arsitektural atau keputusan yang memengaruhi banyak agen tidak boleh hilang di chat.

```yaml
decision_id: DEC-031
question: Gunakan WebSocket atau polling?
decision: WebSocket
decided_by: HERMES
reason: Realtime telemetry memerlukan push event
source_task: INFRA-022
affected:
  - B2
  - B4
  - C1
status: ACTIVE
```

Sub-agen wajib membaca keputusan aktif yang relevan sebelum memulai pekerjaan.

### 2A.7 Blocker & Escalation Manager

Urutan eskalasi:

```text
SUB-AGENT
   │
   ▼
BIKAGENT
   │
   ├── Bisa diselesaikan secara operasional?
   │       └── YA → reroute / dependency fix / supporting agent
   │
   └── TIDAK
          ▼
       HERMES
          │
          ├── Bisa diputuskan dari konteks sistem?
          │       └── YA → decision + redispatch
          │
          └── TIDAK / tindakan kritis
                  ▼
               MAS BAGAS
```

Mas Bagas tidak dibanjiri detail operasional yang dapat diselesaikan oleh sistem sendiri.

### 2A.8 Communication Policy

Default komunikasi:

```text
Sub-Agent → BIKAGENT → HERMES
HERMES → BIKAGENT → Sub-Agent
```

Direct temporary collaboration antar-sub-agen hanya dibuat jika Hermes mengizinkan, misalnya:

```text
B2 ↔ B3
C1 ↔ C3
A2 ↔ A3
```

Channel kolaborasi tersebut bersifat **task-scoped**, bukan koneksi permanen.

### 2A.9 Single Source of Truth Operasional

BIKAGENT menjadi penjaga state operasional:

```text
/runtime-state/
├── agent-registry
├── task-ledger
├── dependency-graph
├── artifact-registry
├── decision-log
├── blockers
├── approvals
└── project-health
```

Obsidian tetap menjadi **knowledge source jangka panjang**, sedangkan Control Tower menyimpan **state operasional yang berubah cepat**.

Dengan pemisahan ini:
- Hermes tidak membawa seluruh detail agent ke context aktif.
- Obsidian tidak dibebani telemetry sementara.
- Sub-agen memperoleh konteks minimum yang benar-benar diperlukan.
- Token lebih hemat dan konteks lintas-domain lebih terisolasi.

---

## 3. STRUKTUR LENGKAP & TUGAS MASING-MASING SUB-AGEN

### DIVISI 1: Content & Social Media Intelligence Fleet
*Fokus Utama: Otomasi cerdas penerbitan konten Instagram (@sputarai, @sputarball) dan TikTok dengan loop belajar mandiri.*

1. **Sub-Agen A1: Trend Scout & Video Decompiler**
   * **Tugas Pokok:** Memantau feed, reels, dan TikTok untuk mengekstrak video referensi per frame (menggunakan `yt-dlp` dan `ffmpeg`).
   * **Tanggung Jawab:** Menganalisis elemen viral: jenis tipografi kinetik, formula *hook* 3 detik pertama, tempo transisi (BPM), dan tren audio.
   * **Spesialisasi Pembelajaran:** *Continuous learning* terhadap perubahan algoritma feed dan format carousel yang disukai audiens Indonesia.

2. **Sub-Agen A2: Copywriter & Narrative Storyboarder**
   * **Tugas Pokok:** Menulis draf teks, judul (headline), dan narasi slide per slide.
   * **Standar Mutu:**
     - **@sputarai:** Format wajib 4 slide terstruktur (Slide 1: Headline provokatif/cctv, Slide 2-3: Fakta/analisis berbobot, Slide 4: CTA). Gaya bahasa Indonesia alami tanpa gaya robot.
     - **@sputarball:** Berita sepak bola terkini, anti-hoax, anti-clickbait murahan (skor kualitas $\ge 8$).
   * **Pantangan:** Haram mengarang berita bohong; wajib diverifikasi silang dengan fakta transfer resmi.

3. **Sub-Agen A3: Media Synthesizer & Motion Renderer**
   * **Tugas Pokok:** Merakit aset visual akhir, grafis, thumbnail, atau klip animasi.
   * **Standar Mutu:**
     - Menggunakan foto asli aksi pemain HD anti-watermark untuk SputarBall (dilarang template lapangan hijau generik berulang).
     - Menggunakan format tipografi bersih *Swiss Editorial / Frame 023* (hairline 1px, corner pinning, zero-emoji).
     - Render video/motion via GPU Canvas atau ffmpeg.

4. **Sub-Agen A4: ML Scorer & Meta Publishing Sentinel**
   * **Tugas Pokok:** Menilai kelayakan draf menggunakan model ML scorer (`sputarai-ml-scorer :224002` dan `sputarball-ml-scorer :844553`).
   * **Aturan Gerbang Mutu:** Draf dengan skor $< 7.5$ otomatis dikembalikan ke Agen A2 untuk perbaikan narasi.
   * **Aturan Rantai Komando:** **HARAM mem-publish langsung ke Instagram/TikTok tanpa persetujuan eksplisit Mas Bagas.** Mengirimkan kartu pratinjau draf ke grup Telegram BAgent, menunggu lampu hijau Mas Bagas, baru memanggil Meta Graph API container.

---

### DIVISI 2: Web Engineering & UI/UX Craft Fleet
*Fokus Utama: Rekayasa antarmuka web, dasbor, dan landing page kelas dunia dengan standar baku Motion Bento Frame 023 (Skor 9.5).*

1. **Sub-Agen B1: Design Token & Contract Architect**
   * **Tugas Pokok (Gerbang Hulu):** Membuat dan memvalidasi berkas `DESIGN.md` sebelum koding dimulai.
   * **Alat Utama:** Linter Google CLI (`@google/design.md`). Wajib **0 errors, 0 warnings** untuk kontras WCAG AA, palet warna *Warm Paper* (`#EFECE6` / `#F3F4F6`), dan token radius bento 24px.
   * **Output:** Menghasilkan `theme.css` dan `tokens.json` sebagai sumber kebenaran tunggal (*Single Source of Truth*).

2. **Sub-Agen B2: Creative Frontend & Motion Builder**
   * **Tugas Pokok:** Mengimplementasikan kode antarmuka menggunakan React 19, Vite, Tailwind CSS, GPU Canvas 2D/WebGL, dan Web Audio procedural synth.
   * **Standar Mutu:** Transisi 60 FPS terkunci GPU, kurva pegas alami (*spring overshoot* `cubic-bezier(0.34, 1.56, 0.64, 1)`), zero-emoji policy (murni ikon SVG `lucide-react`), dan teks fungsional $\ge 12\text{px}$.

3. **Sub-Agen B3: Responsive QA & Gatekeeper Auditor**
   * **Tugas Pokok (Gerbang Hilir):** Menguji artefak web sebelum boleh dilihat pengguna.
   * **Alat Pengujian:**
     - `design_qa_scan.py` (0 findings).
     - Playwright Test Suite di 3 viewport wajib: Ponsel (390px), Tablet (768px), Desktop (1440px).
     - Axe-Core: 0 pelanggaran aksesibilitas WCAG AA/AAA.
     - Impeccable Detect: 0 anti-patterns (bebas *dark glow*, bebas *nested cards*, bebas *line-length overflow*).

4. **Sub-Agen B4: Performance & Deployment Synthesizer**
   * **Tugas Pokok:** Mengompilasi bundle produksi (`dist` $\to$ `dist-public`), mendaftarkan rute Express ke `penelitian-ai`, memperbarui whitelist `privacy-boundary.js`, dan memperbarui katalog master portofolio (`/katalog/`).

---

### DIVISI 3: Infrastructure, Security & Database Ops (SysOps)
*Fokus Utama: Keandalan 24/7, efisiensi RAM ketat, dan keamanan defensif tanpa kebocoran data.*

1. **Sub-Agen C1: PM2 & Ingress Sentinel**
   * **Tugas Pokok:** Memantau kesehatan 17 proses PM2 (termasuk Cloudflare Tunnel, Express microservices, ML scorers, dan telemetry).
   * **Kebijakan RAM:** Memastikan total konsumsi RAM server tetap stabil di bawah batas aman. Merestart proses zombie yang bocor memori secara berkala.

2. **Sub-Agen C2: Supabase & Vector Database Administrator**
   * **Tugas Pokok:** Mengelola instans PostgreSQL dan Supabase Self-Hosted (:8000), tabel memori semantik `pgvector`, dan database transaksi SQLite dengan konfigurasi WAL (*Write-Ahead Logging*) anti-kunci `busy_timeout = 5000ms`.

3. **Sub-Agen C3: Defensive Security Auditor**
   * **Tugas Pokok:** Menjalankan audit keamanan pasif non-destruktif terhadap aset internal maupun situs target yang sah (menggunakan `website-security-auditor`).
   * **Batasan Mutlak:** Dilarang melakukan serangan aktif, brute-force, eksploitasi, bypass login, atau teknik siluman terhadap pihak ketiga tanpa izin sah.

4. **Sub-Agen C4: Git & State Backup Vault**
   * **Tugas Pokok:** Menjalankan sinkronisasi pack-state Hermes (`hermes-docker`), memverifikasi file `.gitignore` agar token/kunci API tidak bocor, dan melakukan push terenkripsi ke repository privat GitHub `Bagas10k/hermes-docker.git`.

---

### DIVISI 4: Continuous Learning & Cognitive Crystallizer (Autopilot Engine)
*Fokus Utama: Riset otonom terjadwal, pembelajaran tren desain baru, dan kristalisasi ilmu ke Obsidian.*

1. **Sub-Agen D1: Trend & Skill Scout (Autopilot Runner)**
   * **Tugas Pokok:** Berjalan setiap 30 menit melalui cron job `hermes-autopilot-learner` (`e7ae53a1c7a8`).
   * **Aktivitas:** Menguji pustaka baru, mengevaluasi standar desain 2026, membedah interaksi taktil mikro, dan menguji sasis kode baru.

2. **Sub-Agen D2: Knowledge Distiller & Obsidian Scribe**
   * **Tugas Pokok:** Setiap kali sebuah solusi teknis berhasil dibuktikan atau sebuah kegagalan dievaluasi, agen ini wajib menulis catatan formal ke `/home/ubuntu/otak-koding/BUKU_CATATAN/` dan memperbarui `/home/ubuntu/otak-koding/KNOWLEDGE/INDEX.md` ke status `TESTED`.

3. **Sub-Agen D3: Memory & Context Curator (AGOTIMA Engine)**
   * **Tugas Pokok:** Menjaga kebersihan memori jangka panjang. Menghapus fakta yang sudah basi, mencegah duplikasi informasi, dan memastikan kuota karakter memori sistem tidak melebihi 2.200 karakter.

4. **Sub-Agen D4: Experiment Sandbox Runner**
   * **Tugas Pokok:** Menjalankan eksperimen *throwaway* di folder terisolasi (`/tmp/` atau sandbox lab) untuk memverifikasi hipotesis teknis sebelum diterapkan ke kode produksi.

---

## 4. WORKFLOW SISTEM: BAGAIMANA MENGELOLA & MENJALANKAN ARMADA AGEN

### 4A. ATURAN ORKESTRASI DI DALAM PROTOKOL 5 TAHAP

Protokol 5 tahap tetap dipertahankan. Penyempurnaan hanya menambahkan state management di dalamnya.

#### TAHAP 1 — Ingestion & Intent Routing

Hermes menghasilkan:

```yaml
request_id:
intent:
domain:
risk_level:
required_capabilities:
approval_required:
context_refs:
```

Hermes memilih **minimum necessary agents**. Tidak semua agen dipanggil jika dua agen sudah cukup.

#### TAHAP 2 — Dekomposisi DAG & Dispatch

Sebelum dispatch:

1. Pecah tujuan menjadi task atomik.
2. Tentukan dependency.
3. Tentukan primary agent.
4. Tentukan reviewer jika diperlukan.
5. Tentukan acceptance criteria.
6. Daftarkan semuanya ke Task Ledger BIKAGENT.
7. Baru jalankan task yang berstatus `READY`.

Task independen boleh paralel.

Task yang bergantung pada output lain wajib `WAITING_DEPENDENCY`.

#### TAHAP 3 — Continuous Learning Loop

Learning agent tidak boleh langsung mengubah doktrin produksi.

Urutannya:

```text
OBSERVE
  ↓
HYPOTHESIS
  ↓
D4 SANDBOX EXPERIMENT
  ↓
VERIFIED EVIDENCE
  ↓
D2 KNOWLEDGE DISTILLATION
  ↓
HERMES REVIEW
  ↓
ACTIVE KNOWLEDGE / CONSTRAINT
```

Pengetahuan yang belum diuji diberi status:

```text
EXPERIMENTAL
```

Pengetahuan yang telah terbukti:

```text
TESTED
```

Pengetahuan yang sudah tidak valid:

```text
DEPRECATED
```

#### TAHAP 4 — Invariant Verification Gate

Invariant Auditor hanya menghasilkan salah satu dari:

```text
PASS
FAIL
RETURN_FOR_REVISION
BLOCKED_BY_EVIDENCE
```

Tidak boleh ada status ambigu seperti “sepertinya aman” atau “cukup bagus”.

Jika gagal:

```text
Invariant Auditor
      ↓
BIKAGENT
      ↓
Task status = REVIEW_REQUIRED
      ↓
Hermes menentukan agent revisi
```

#### TAHAP 5 — Human Approval & Committed Action

Aksi irreversible / berisiko tinggi tetap memerlukan Mas Bagas.

Approval object:

```yaml
approval_id:
requested_by: HERMES
action:
reason:
affected_assets:
risk:
verification_status:
owner_decision: PENDING
```

Status:

```text
PENDING
APPROVED
REJECTED
REVOKED
```

Agen tidak boleh menginterpretasikan diamnya owner sebagai persetujuan.

---

## 4B. PROJECT HEALTH REPORT

BIKAGENT harus dapat menghasilkan ringkasan tanpa Hermes membaca log mentah seluruh agen.

```text
PROJECT: <nama>

HEALTH: GOOD / WARNING / CRITICAL
OVERALL PROGRESS: 68%

TASKS
Completed : 12
Running   : 4
Waiting   : 3
Blocked   : 1
Failed    : 0

AGENTS
Busy      : B2, C1, D2
Waiting   : B3
Idle      : A3, A4

BLOCKER TERPENTING
INFRA-022 menunggu konfigurasi tunnel.

PENDING DECISION
DEC-034 membutuhkan keputusan Hermes.

OWNER APPROVAL
Tidak ada.

NEXT CRITICAL PATH
C1 → B4 → B3 → Invariant Auditor
```

### Tiga tingkat laporan

```text
LEVEL 1
Sub-Agent → BIKAGENT
Detail teknis

LEVEL 2
BIKAGENT → Hermes
Ringkasan operasional + blocker + dependency + rekomendasi routing

LEVEL 3
Hermes → Mas Bagas
Keputusan, progress penting, risiko, dan hal yang membutuhkan approval
```

Tujuan utamanya adalah **information compression tanpa kehilangan traceability**.

---


Alur kerja operasional menerapkan **Protokol 5 Tahap Tertutup (Closed-Loop Lifecycle)**:

```text
  [ Instruksi Mas Bagas ]
             │
             ▼
  ┌────────────────────────────────────────────────────────┐
  │ TAHAP 1: INGESTION & INTENT ROUTING (Hermes GM)        │
  │ • Klasifikasi domain: Konten? Web? Infra? Riset?       │
  │ • Penetapan batas token & penentuan Single Purpose     │
  └────────────────────────────────────────────────────────┘
             │
             ▼
  ┌────────────────────────────────────────────────────────┐
  │ TAHAP 2: DEKOMPOSISI DAG & DISPATCH KE DIVISI TERPISAH │
  │ • Divisi Konten: Scout -> Copy -> Render -> ML Scorer   │
  │ • Divisi Web: Design.md -> Builder -> QA Gatekeeper    │
  │ • Isolasi Sandbox Tool & Worktree                      │
  └────────────────────────────────────────────────────────┘
             │
             ▼
  ┌────────────────────────────────────────────────────────┐
  │ TAHAP 3: CONTINUOUS LEARNING LOOP (Khusus Divisi 1 & 4)│
  │ • Evaluasi metrik engagement / skor visual             │
  │ • Identifikasi pola baru & eliminasi kegagalan         │
  │ • Kristalisasi ke Obsidian BUKU_CATATAN                │
  └────────────────────────────────────────────────────────┘
             │
             ▼
  ┌────────────────────────────────────────────────────────┐
  │ TAHAP 4: INVARIANT VERIFICATION GATE (Si Pengawas)     │
  │ • Playwright 3 layar pass?                             │
  │ • Axe WCAG AA 0 pelanggaran?                           │
  │ • Impeccable detect 0 anti-patterns?                   │
  │ • ML Scorer >= 7.5?                                    │
  └────────────────────────────────────────────────────────┘
             │
             ▼
  ┌────────────────────────────────────────────────────────┐
  │ TAHAP 5: MAS BAGAS HUMAN APPROVAL & COMMITTED ACTION   │
  │ • Lolos uji -> Kirim draf/link bersih ke Mas Bagas     │
  │ • Mas Bagas Setuju -> Publish IG / Push Git / Live     │
  │ • Mas Bagas Beri Skor < 5 -> Reset total dari nol      │
  └────────────────────────────────────────────────────────┘
```

---

## 5. DETAIL SIKLUS BELAJAR MANDIRI KONTEN (CONTINUOUS LEARNING SOCIAL MEDIA)

Mengatasi masalah spesifik Mas Bagas di mana agen otomasi IG dan TikTok sebelumnya campur aduk:

1. **Observasi Berkelanjutan (Observe):**
   Agen A1 secara terjadwal mengekstrak 10 konten teratas di ceruk AI dan sepak bola. Data yang diekstrak:
   - Durasi video & titik pergantian slide.
   - Kata pertama headline (Hook analysis).
   - Rasio warna dominan pada thumbnail.

2. **Skor Prediktif (Evaluate):**
   Sebelum draf dibuat, Agen A4 membandingkan storyboard terhadap model historis `sputarai-ml-scorer`:
   - Jika probabilitas jangkauan diprediksi rendah karena teks terlalu panjang di slide 1, draf ditolak secara internal dan diinstruksikan menulis ulang headline yang lebih tajam.

3. **Kristalisasi Pola Sukses (Learn):**
   Jika postingan yang telah terbit mendapatkan rasio likes/komentar tinggi di atas rata-rata:
   - Polanya dicatat ke memori Divisi 1 sebagai formula valid.
   - Jika performanya buruk, parameter tersebut ditandai sebagai *negative constraint* (pantangan baru).

---


## 5A. DOKTRIN PENYELESAIAN TUGAS & ISOLASI KONTEKS

### DONE ≠ VERIFIED ≠ APPROVED

Gunakan definisi:

```text
IMPLEMENTED
   ↓
VERIFIED
   ↓
COMPLETED
   ↓
APPROVED       (hanya jika approval owner diperlukan)
   ↓
COMMITTED      (publish / push / production change)
```

Builder tidak berwenang mengubah task menjadi `COMPLETED` jika task memiliki reviewer atau verification gate.

### Context Packet Minimum

Hermes/BIKAGENT hanya mengirim konteks yang dibutuhkan agent:

```yaml
task:
objective:
relevant_decisions:
required_artifacts:
constraints:
acceptance_criteria:
tool_permissions:
knowledge_refs:
```

Dilarang memberikan seluruh histori project kepada setiap agent tanpa kebutuhan.

### Retry & Failure Policy

```text
FAILED
  ↓
BIKAGENT mendiagnosis tipe kegagalan
  │
  ├── TRANSIENT → retry terbatas
  ├── DEPENDENCY → WAITING_DEPENDENCY
  ├── CAPABILITY_MISMATCH → reroute agent
  ├── REQUIREMENT_AMBIGUITY → Hermes decision
  └── CRITICAL / OWNER DECISION → Mas Bagas
```

Retry tidak boleh tanpa batas karena dapat membuat agent loop dan menghabiskan token.

---

## 6. DOKTRIN KONTROL & PANTANGAN MUTLAK HIERARKI

1. **Haram Menjalankan Tugas Konten di Thread Koding Web:**
   Agen yang sedang mengerjakan desain/dashboard dilarang merangkap memproses postingan IG/TikTok dalam satu siklus berpikir agar memori dan token tidak bocor.
2. **Doktrin Keputusan Kritis Mas Bagas:**
   - Penerbitan postingan sosial media resmi (@sputarai, @sputarball).
   - Commit & push repositori git utama.
   - Perubahan struktur basis data produksi.
   *Ketiga hal di atas wajib meminta approval Mas Bagas dan dilarang dieksekusi secara sepihak.*
3. **Penyaluran Notifikasi Otomatis:**
   Seluruh notifikasi bot, laporan telemetri, draf carousel, dan hasil audit otomatis wajib dialirkan ke **Grup Telegram BAgent (`-1004397580704`)**, sedangkan chat pribadi/ruang kerja difokuskan khusus untuk arahan strategis Mas Bagas.


---

## 7. KONSTITUSI OPERASIONAL ORKESTRATOR

1. **Mas Bagas tetap pemegang veto dan approval akhir.**
2. **Hermes adalah otak strategis dan satu pintu utama komunikasi owner.**
3. **BIKAGENT adalah Orchestrator Assistant / Control Tower, bukan pengganti Hermes.**
4. **Invariant Auditor independen dari dispatcher dan builder.**
5. **Empat divisi A/B/C/D dan seluruh spesialis yang sudah berjalan tetap dipertahankan.**
6. **Orchestrator memanggil agen minimum yang diperlukan, bukan seluruh armada.**
7. **Semua task memiliki ID, owner, dependency, acceptance criteria, dan status eksplisit.**
8. **Semua output penting masuk Artifact Registry.**
9. **Semua keputusan lintas-agent masuk Decision Log.**
10. **Sub-agent tidak boleh melakukan tindakan kritis di luar permission task.**
11. **`DONE` dari agent bukan bukti bahwa pekerjaan benar.**
12. **State operasional cepat berada di Control Tower; knowledge jangka panjang berada di Obsidian/Vault.**
13. **Progress owner diringkas; trace teknis tetap tersedia bila dibutuhkan.**
14. **Tidak ada publish, push utama, atau perubahan DB produksi tanpa aturan approval yang sudah ditetapkan.**
15. **Setiap kegagalan menghasilkan diagnosis, bukan retry membabi buta.**

### Bentuk akhir rantai komando

```text
MAS BAGAS
   │
   ▼
HERMES
Strategic Orchestrator
   │
   ├───────────────┐
   ▼               ▼
BIKAGENT        INVARIANT AUDITOR
Control Tower   Independent Quality Gate
   │
   ▼
4 DIVISI SPESIALIS
A / B / C / D
   │
   ▼
Artifact + Progress + Evidence
   │
   ▼
BIKAGENT
   │
   ▼
HERMES
   │
   ▼
MAS BAGAS
```

**Inti desain:** Hermes berpikir dan memutuskan, BIKAGENT menjaga keadaan operasional, spesialis mengeksekusi, Invariant Auditor membuktikan kualitas, dan Mas Bagas mengendalikan keputusan kritis.

---

# 8. MISSION CONTROL ENGINE — LAPISAN RUNTIME ORKESTRASI

V4 **tidak menambah bos baru dan tidak mengganti BIKAGENT**. `MISSION CONTROL ENGINE` adalah **mesin internal milik BIKAGENT/Control Tower** yang menjalankan keputusan strategis Hermes secara deterministik, terukur, dan dapat dipulihkan.

```text
MAS BAGAS
   │
   ▼
HERMES — Strategic Orchestrator / Decision Brain
   │
   ├─────────────────────────────────────────────┐
   ▼                                             ▼
BIKAGENT / CONTROL TOWER                  INVARIANT AUDITOR
   │                                      Independent QC Gate
   │
   └── MISSION CONTROL ENGINE
       ├── Mission Manager
       ├── Task Scheduler & Arbitration
       ├── Skill Manager / Capability Resolver
       │   ├── Skill Registry
       │   ├── Skill Matcher & Ranker
       │   ├── Dependency Resolver
       │   ├── Conflict Resolver
       │   ├── Skill Chain Builder
       │   └── NO_SKILL Resolver
       ├── Agent Dispatcher
       ├── Context Packet Builder
       ├── Event Router
       ├── Permission Manager
       ├── Resource Governor
       ├── Heartbeat & Lease Manager
       ├── Progress Aggregator
       ├── Workspace / Lock Manager
       ├── Checkpoint & Recovery Manager
       ├── Skill Performance Tracker
       └── Runtime Trace Manager
                    │
                    ▼
          DYNAMIC MISSION / PROJECT POD
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
        Agent     Agent     Agent
                    │
                    ▼
            Artifact + Evidence
```

## 8.1 Pemisahan tanggung jawab

### Hermes
- Memahami tujuan owner.
- Menentukan outcome.
- Memecah mission tingkat tinggi.
- Memilih strategi.
- Menentukan capability yang dibutuhkan pada tingkat strategi.
- Meminta Skill Manager menyusun skill plan bila task membutuhkan skill khusus.
- Menetapkan keputusan lintas-divisi.
- Menentukan apakah perlu eskalasi ke Mas Bagas.
- Menyintesis hasil final.

### BIKAGENT / Mission Control
- Menyimpan state runtime.
- Mendaftarkan mission dan task.
- Menjadwalkan pekerjaan.
- Menjalankan Skill Manager untuk matching, dependency, conflict, NO_SKILL, dan skill-chain resolution.
- Menyediakan metadata skill ringan dan hanya memuat isi skill terpilih saat diperlukan.
- Mengirim context packet.
- Memantau heartbeat.
- Mengelola dependency.
- Menjaga lock/workspace.
- Mengumpulkan progres.
- Mendeteksi timeout, crash, dan blocker.
- Menjalankan recovery sesuai policy.
- Mengirim ringkasan operasional ke Hermes.

### Invariant Auditor
- Tidak mengatur task.
- Tidak menjadi builder.
- Tidak menilai berdasarkan klaim agent.
- Memverifikasi artifact/evidence terhadap acceptance criteria.
- Memberikan `PASS`, `FAIL`, `RETURN_FOR_REVISION`, atau `BLOCKED_BY_EVIDENCE`.

---

# 9. MISSION REGISTRY & DYNAMIC MISSION POD

Semua pekerjaan non-trivial dibungkus sebagai **Mission**.

```yaml
mission_id: MIS-2026-0042
title: Realtime Hermes Monitoring Dashboard
requested_by: MAS_BAGAS
orchestrator: HERMES
control_tower: BIKAGENT
status: ACTIVE
priority: HIGH
objective: >
  Memperbaiki dan meningkatkan dashboard monitoring tanpa mengubah
  design language yang sudah disetujui.
constraints:
  - non_destructive
  - preserve_existing_design
  - no_production_commit_without_approval
selected_agents:
  - B2
  - B3
  - C1
  - C3
  - D2
critical_path:
  - TASK-001
  - TASK-004
  - TASK-006
owner_approval_required: true
```

## 9.1 Mission Pod bersifat sementara

Divisi A/B/C/D tetap permanen. **Mission Pod tidak mengganti divisi**; Mission Pod hanya memilih specialist yang relevan untuk sebuah tujuan.

Contoh:

```text
MISSION-042
├── B2 Frontend Builder          [PRIMARY]
├── B3 Responsive QA             [REVIEWER]
├── C1 PM2 & Ingress             [SUPPORT]
├── C3 Security                  [REVIEWER]
└── D2 Knowledge Distiller       [POST-VERIFICATION]
```

Agent yang tidak dibutuhkan tetap `IDLE` dan tidak menerima context mission.

## 9.2 Mission State

```text
DRAFT
PLANNED
ACTIVE
PAUSED
BLOCKED
VERIFYING
AWAITING_OWNER_APPROVAL
COMPLETED
FAILED
CANCELLED
ARCHIVED
```

Mission hanya boleh `COMPLETED` jika task kritis selesai dan verification gate yang diwajibkan telah lulus.

---

# 10. TASK SCHEDULER & ARBITRATION ENGINE

Mission Control wajib menentukan **kapan**, **siapa**, dan **dalam urutan apa** task dijalankan.

## 10.1 Priority class

```text
P0 = INCIDENT / RECOVERY CRITICAL
P1 = OWNER BLOCKING / PRODUCTION CRITICAL
P2 = HIGH
P3 = NORMAL
P4 = BACKGROUND / LEARNING
```

Priority tidak boleh dipakai untuk melewati permission atau approval gate.

## 10.2 Scheduling policy

Urutan evaluasi:

```text
READY?
  ↓
DEPENDENCY SATISFIED?
  ↓
AGENT CAPABILITY MATCH?
  ↓
AGENT AVAILABLE?
  ↓
PERMISSION VALID?
  ↓
RESOURCE BUDGET AVAILABLE?
  ↓
WORKSPACE SAFE?
  ↓
DISPATCH
```

## 10.3 Preemption

Agent yang sedang bekerja tidak otomatis dihentikan ketika task baru masuk.

Preemption hanya diperbolehkan bila:
- task baru P0/P1;
- pekerjaan aktif mempunyai checkpoint aman;
- tidak merusak state produksi;
- Hermes/Mission Control policy memperbolehkannya.

Task yang dipreempt:

```text
RUNNING → CHECKPOINTING → PAUSED → READY_TO_RESUME
```

## 10.4 Concurrency

Mission Control harus membatasi concurrency berdasarkan kapasitas aktual, bukan sekadar jumlah agent.

Contoh konfigurasi:

```yaml
concurrency:
  global_max_active_tasks: 6
  per_agent_max: 1
  background_max: 2
  production_mutation_max: 1
```

Nilai nyata harus disesuaikan setelah audit resource server. Jangan mengarang kapasitas.

---

# 11. HEARTBEAT, LEASE & DEAD-AGENT RECOVERY

Status `BUSY` tidak cukup. Setiap task aktif memiliki **lease**.

```yaml
runtime:
  agent_id: B2
  task_id: TASK-042
  heartbeat_at: 2026-09-28T21:00:00+07:00
  lease_expires_at: 2026-09-28T21:05:00+07:00
  checkpoint_id: CP-019
```

Jika lease kedaluwarsa:

```text
RUNNING
  ↓ no heartbeat
SUSPECTED_STALE
  ↓ verify process/session
RECOVERING
  ├── resume from checkpoint
  ├── reroute if capability available
  └── escalate if state cannot be proven safe
```

Mission Control **dilarang** menandai agent mati hanya karena satu telemetry event hilang tanpa verifikasi state runtime yang tersedia.

---

# 12. PERMISSION & AUTHORITY MATRIX

Capability dan permission adalah dua hal berbeda.

Agent dapat **mampu** melakukan sesuatu tetapi belum tentu **berwenang** melakukannya.

Permission class:

```text
READ
WRITE
EXECUTE
NETWORK
SECRET_READ
DATABASE_MUTATE
DEPLOY
PUBLISH
GIT_COMMIT
GIT_PUSH
DELETE
ADMIN
```

Contoh:

```yaml
agent_id: B2
permissions:
  source_frontend:
    - READ
    - WRITE
  shell:
    - EXECUTE
  production:
    - READ
  database_production: []
  social_publish: []
  git_main:
    - READ
```

## 12.1 Owner Approval Gate tetap berlaku

Permission runtime tidak menghapus doktrin approval Mas Bagas.

Tindakan berikut tetap melalui approval sebagaimana doktrin existing:
- publikasi akun sosial resmi;
- commit/push repository utama sesuai kebijakan yang berlaku;
- perubahan struktur database produksi;
- tindakan irreversible lain yang kemudian ditetapkan owner.

---

# 13. RESOURCE GOVERNOR & TOKEN BUDGET

Setiap task mempunyai budget agar satu agent tidak memonopoli sistem.

```yaml
budget:
  max_retries: 2
  max_tool_calls: 40
  max_context_refs: 12
  max_parallel_children: 3
  runtime_class: NORMAL
  token_policy: ADAPTIVE
```

Prinsip:
- jangan memberi seluruh vault ke agent;
- retrieve context sesuai task;
- perluasan context dilakukan hanya jika evidence kurang;
- retry harus mempunyai alasan yang berbeda dari percobaan gagal sebelumnya;
- background learning tidak boleh menghambat P0-P2.

Jika budget hampir habis tetapi task belum selesai, agent wajib mengirim:

```yaml
status: BUDGET_PRESSURE
completed:
remaining:
blocker:
recommended_next_action:
```

Bukan diam-diam menambah loop.

---

# 14. EVENT & MESSAGE PROTOCOL

Semua komunikasi runtime penting menggunakan envelope standar.

```yaml
event_id: EVT-000123
trace_id: TRC-0091
mission_id: MIS-0042
task_id: TASK-0007
correlation_id: TASK-0007
sender: B2
receiver: BIKAGENT
event_type: TASK_PROGRESS
timestamp: 2026-09-28T21:10:00+07:00
payload:
  progress: 70
  current_action: websocket integration
```

Event type minimum:

```text
MISSION_CREATED
TASK_CREATED
TASK_ASSIGNED
TASK_STARTED
TASK_PROGRESS
TASK_BLOCKED
TASK_CHECKPOINTED
TASK_FAILED
TASK_COMPLETED_BY_AGENT
VERIFICATION_REQUESTED
VERIFICATION_PASS
VERIFICATION_FAIL
DECISION_REQUIRED
OWNER_APPROVAL_REQUIRED
OWNER_APPROVED
OWNER_REJECTED
AGENT_HEARTBEAT
AGENT_STALE
ARTIFACT_CREATED
ARTIFACT_UPDATED
MISSION_COMPLETED
```

Semua event penting membawa `trace_id` agar perjalanan sebuah instruksi dapat direkonstruksi.

---

# 15. WORKSPACE OWNERSHIP, LOCKING & CONFLICT CONTROL

Untuk mencegah dua agent merusak file/state yang sama:

## 15.1 Default coding isolation

```text
MISSION
  └── isolated worktree / branch / sandbox
       ├── Agent B2 workspace
       ├── Agent C1 workspace bila perlu
       └── shared artifact melalui registry
```

## 15.2 Resource lock

```yaml
lock_id: LOCK-109
resource: src/pages/Dashboard.tsx
owner_task: TASK-042
mode: WRITE
expires_with_lease: true
```

Policy:
- banyak reader diperbolehkan;
- satu writer untuk resource yang sama;
- perubahan lintas-agent diintegrasikan melalui explicit handoff;
- conflict tidak boleh diselesaikan dengan overwrite buta.

Database migration, deployment config, dan state produksi menggunakan exclusive mutation lock.

---

# 16. CHECKPOINT, RESUME & ROLLBACK

Task panjang membuat checkpoint setelah milestone penting.

```yaml
checkpoint_id: CP-021
mission_id: MIS-0042
task_id: TASK-005
created_by: B2
state:
  completed_steps:
    - event model integrated
    - dashboard shell verified
  artifacts:
    - ART-012
  next_step: connect socket room
safe_to_resume: true
```

Checkpoint dipakai untuk:
- crash recovery;
- preemption;
- handoff agent;
- rollback eksperimen.

**Rollback point wajib dibuat sebelum perubahan produksi yang dapat dibalik.**

---

# 17. AGENT PERFORMANCE PROFILE — EVIDENCE BASED ROUTING

Mission Control boleh belajar dari kinerja agent, tetapi tidak boleh membuat reputasi berdasarkan asumsi.

Data yang dicatat:

```yaml
agent_id: B2
profile:
  task_types_completed: {}
  verification_passes: 0
  revisions_required: 0
  runtime_failures: 0
  average_handoffs: null
  common_failure_modes: []
  last_updated: null
```

Routing dapat menggunakan histori sebagai sinyal **setelah data cukup**.

Dilarang membuat skor palsu seperti `Agent B2 = 97%` tanpa dataset dan definisi metrik yang jelas.

---

# 18. OWNER COMMAND PROTOCOL

Mas Bagas tetap berinteraksi terutama dengan Hermes. Hermes/BIKAGENT harus memahami command operasional ringkas berikut jika interface mendukungnya:

```text
/status
/missions
/mission <id>
/agents
/tasks
/trace <id>
/why <task_id>
/pause <mission_id>
/resume <mission_id>
/cancel <task_id|mission_id>
/approve <approval_id>
/reject <approval_id> <reason>
```

Arti `/why`:

```text
Kenapa agent ini dipilih?
Kenapa task menunggu?
Kenapa sebuah approval diminta?
Evidence apa yang dipakai?
Dependency mana yang memblokir?
```

Hermes harus menjawab dari registry/trace, bukan mengarang alasan setelah fakta.

---

# 19. FAILURE CONTAINMENT & CIRCUIT BREAKER

Failure satu agent tidak boleh otomatis menjatuhkan mission lain.

Boundary:

```text
AGENT → TASK → MISSION → DIVISION → SYSTEM
```

Kesalahan ditahan di boundary terkecil yang aman.

Circuit breaker dipakai bila tool/service gagal berulang:

```text
CLOSED
  ↓ repeated verified failure
OPEN
  ↓ cooldown / human fix
HALF_OPEN
  ↓ controlled probe
CLOSED or OPEN
```

Mission Control tidak boleh melakukan retry tanpa batas ke API/tool yang jelas gagal.

---

# 20. POST-MISSION REVIEW & LEARNING LOOP

Setelah mission `COMPLETED`, jalankan review ringkas:

```text
MISSION OUTCOME
   ↓
WHAT WORKED?
   ↓
WHAT FAILED?
   ↓
QA / AUDITOR EVIDENCE
   ↓
OWNER FEEDBACK jika tersedia
   ↓
D2 Knowledge Distillation
   ↓
D3 Memory Deduplication / Context Curation
   ↓
Agent Performance Profile Update
```

Format lesson:

```yaml
context:
symptom:
evidence:
mechanism:
action:
result:
applicability:
status: TESTED
```

Hipotesis yang belum dibuktikan tidak boleh dinaikkan menjadi doktrin.

---

# 21. SINGLE SOURCE OF TRUTH — PEMISAHAN HOT STATE DAN LONG-TERM KNOWLEDGE

## Hot operational state — BIKAGENT / Mission Control

```text
/runtime-state/
├── missions/
├── tasks/
├── agents/
├── leases/
├── locks/
├── checkpoints/
├── traces/
├── approvals/
├── decisions/
└── artifacts/
```

## Long-term knowledge — Obsidian/Vault

```text
/home/ubuntu/otak-koding/
├── BUKU_CATATAN/
├── KNOWLEDGE/
├── SISTEM_AGENT/
└── ...
```

Aturan:
- telemetry mentah tidak otomatis menjadi knowledge;
- knowledge yang telah diverifikasi tidak perlu selalu dimuat ke runtime;
- agent mengambil referensi melalui `knowledge_refs` sesuai kebutuhan.

---

# 22. END-TO-END RUNTIME FLOW — MISSION CONTROL FOUNDATION

```text
[1] MAS BAGAS memberi instruksi
          │
          ▼
[2] HERMES memahami intent + outcome
          │
          ▼
[3] HERMES membuat / memilih MISSION
          │
          ▼
[4] MISSION CONTROL membaca capability + permission + workload
          │
          ▼
[5] Hermes/Mission Control membentuk Mission Pod minimum
          │
          ▼
[6] Task DAG + acceptance criteria + budget dibuat
          │
          ▼
[7] Context Packet minimum dikirim
          │
          ▼
[8] Specialist bekerja + heartbeat + progress events
          │
          ├──── blocker → BIKAGENT → Hermes → owner bila perlu
          │
          ▼
[9] Artifact Registry menerima output
          │
          ▼
[10] Invariant Auditor memverifikasi evidence
          │
          ├──── FAIL → revision loop terarah
          │
          └──── PASS
                  │
                  ▼
[11] Owner approval bila tindakan kritis
                  │
                  ▼
[12] Commit/publish/deploy sesuai authority
                  │
                  ▼
[13] Post-Mission Review
                  │
                  ▼
[14] D2/D3 kristalisasi knowledge
                  │
                  ▼
[15] Hermes memberi hasil ringkas kepada Mas Bagas
```

---

# 23. MIGRATION PLAN — NON-DESTRUCTIVE

Implementasi fondasi Mission Control dilakukan bertahap. **Jangan mematikan sistem existing untuk memasang V4.**

## PHASE 0 — Read-only audit

Tujuan:
- petakan service, bot, cronjob, PM2, database, vault, repo, port, dan file konfigurasi aktual;
- identifikasi state yang sudah dimiliki BIKAGENT/Hermes;
- jangan melakukan mutation.

Output:
- `CURRENT_STATE_MAP.md`
- `GAP_ANALYSIS_V4.md`
- daftar komponen yang dapat direuse.

## PHASE 1 — Registry shadow mode

Tambahkan:
- Mission Registry;
- Task Ledger;
- Agent Registry;
- Event envelope;
- trace ID.

Semua berjalan dalam **shadow/read-observe mode** tanpa mengubah routing existing.

## PHASE 2 — Progress & heartbeat

Tambahkan:
- heartbeat;
- lease;
- progress collector;
- project health report.

Routing lama masih menjadi primary.

## PHASE 3 — Controlled scheduler

Aktifkan Mission Control untuk mission baru yang dipilih sebagai canary.

Tidak langsung mengambil alih semua workflow.

## PHASE 4 — Permission, locking & recovery

Aktifkan:
- permission matrix;
- workspace ownership;
- checkpoint/resume;
- bounded retry;
- circuit breaker.

## PHASE 5 — Full orchestration

Setelah canary lolos:
- mission baru memakai Mission Control V4 secara default;
- workflow lama tetap dapat menjadi fallback selama periode stabilisasi;
- kemudian deprecated hanya setelah bukti cukup.

---

# 24. ACCEPTANCE TEST — MISSION CONTROL FOUNDATION

Mission Control belum dianggap aktif hanya karena file/config sudah dibuat.

Minimal harus terbukti:

### Test A — Routing
- instruksi web hanya membentuk pod relevan;
- agent Content tidak ikut tanpa alasan.

### Test B — Dependency
- task hilir tidak berjalan sebelum dependency selesai.

### Test C — Heartbeat
- worker yang berhenti terdeteksi tanpa membuat task ganda liar.

### Test D — Permission
- agent tanpa permission produksi ditolak ketika mencoba mutation produksi.

### Test E — QA Gate
- artifact gagal tidak dapat berubah menjadi `COMPLETED` sebelum revisi.

### Test F — Recovery
- task dapat dilanjutkan dari checkpoint yang valid.

### Test G — Trace
- `/trace <id>` dapat menjelaskan alur owner request → task → agent → artifact → verification.

### Test H — Approval
- action kritis tetap berhenti di `AWAITING_OWNER_APPROVAL` sampai Mas Bagas memberi keputusan eksplisit.

### Test I — Context Isolation
- agent hanya menerima context relevan dan tidak membawa thread domain lain secara default.

### Test J — Existing System Regression
- bot, cronjob, telemetry, PM2, vault, dan workflow existing yang sebelumnya sehat tetap sehat.

---

# 25. FINAL OPERATIONAL DOCTRINE — MISSION CONTROL FOUNDATION

```text
OWNER DECIDES THE GOAL.
HERMES DECIDES THE STRATEGY.
BIKAGENT KNOWS THE STATE.
MISSION CONTROL RUNS THE WORK.
SPECIALISTS EXECUTE.
INVARIANT AUDITOR PROVES.
OBSIDIAN REMEMBERS VERIFIED KNOWLEDGE.
OWNER RETAINS CRITICAL AUTHORITY.
```

Fondasi Mission Control **bukan penggantian struktur**. Ia adalah lapisan runtime yang membuat struktur existing dapat beroperasi sebagai organisasi multi-agent yang terkoordinasi, dapat diaudit, hemat konteks, dapat dipulihkan, dan tetap tunduk pada rantai komando yang sudah ditetapkan.

---

# 26. SKILL OPERATING SYSTEM — CAPABILITY LAYER DI DALAM MISSION CONTROL

V4 menambahkan **Skill Operating System (Skill OS)** tanpa mengubah rantai komando. Skill OS bukan agent, bukan divisi baru, dan bukan pengganti Hermes. Ia adalah **lapisan capability resolution** yang menjawab pertanyaan:

> Untuk task ini, kemampuan apa yang benar-benar diperlukan, skill mana yang paling tepat, dalam urutan apa skill dipakai, dan apakah task sebenarnya tidak membutuhkan skill khusus?

Prinsip utama:

```text
AGENT      = siapa yang mengerjakan
SKILL      = bagaimana pekerjaan dilakukan / kemampuan reusable
TOOL / MCP = alat untuk melakukan tindakan
KNOWLEDGE  = fakta, referensi, pola, dokumentasi yang dipakai
MEMORY     = pengalaman dan hasil sebelumnya
```

Kelima konsep tersebut **dilarang dicampur** di registry maupun routing.

---

# 27. POSISI SKILL MANAGER DALAM ARSITEKTUR EXISTING

Skill Manager menjadi modul internal Mission Control yang dikonsultasikan setelah Hermes memahami intent dan sebelum Agent Dispatcher mengunci executor.

```text
MAS BAGAS
   │
   ▼
HERMES
Intent + Outcome + Task Planning
   │
   ▼
BIKAGENT / MISSION CONTROL
   │
   ├── SKILL MANAGER
   │     ├── Registry
   │     ├── Match
   │     ├── Rank
   │     ├── Dependency Resolver
   │     ├── Conflict Resolver
   │     ├── Skill Chain Builder
   │     └── NO_SKILL Resolver
   │
   ├── AGENT ROUTER
   │     └── memilih executor berdasarkan capability + permission + workload
   │
   └── CONTEXT BUILDER
         └── memuat hanya skill + knowledge yang terpilih
                │
                ▼
             AGENT
                │
        ┌───────┼────────┐
        ▼       ▼        ▼
      SKILL   TOOL/MCP  KNOWLEDGE
                │
                ▼
             EXECUTION
                │
                ▼
       INVARIANT AUDITOR
                │
                ▼
   PERFORMANCE + LEARNING
```

### Batas kewenangan

- Hermes menentukan outcome dan strategi.
- Skill Manager menentukan **candidate capability plan**, bukan keputusan bisnis/owner.
- Agent Router menentukan executor berdasarkan runtime state.
- Agent menggunakan skill; skill tidak pernah menjadi executor sendiri.
- Tool/MCP hanya boleh digunakan jika permission task mengizinkan.
- Invariant Auditor menilai artifact/evidence, bukan popularitas skill.

---

# 28. SKILL REGISTRY — METADATA RINGAN, LAZY LOAD

Hermes/Mission Control **tidak boleh memuat isi semua skill ke context**.

Registry hanya menyimpan metadata ringkas:

```yaml
skill_id: frontend-implementation
version: 1.3.0
status: ACTIVE

domains:
  - frontend
  - web

capabilities:
  - react
  - html
  - css
  - responsive-layout

use_when:
  - task requires frontend implementation
  - design specification already exists

do_not_use_when:
  - task is backend-only
  - no implementation is requested

requires:
  - design_spec

optional_dependencies:
  - visual-reference-analysis

produces:
  - frontend_code

compatible_with:
  - ui-design-reasoning
  - interaction-animation
  - visual-qa

conflicts_with: []

required_tools:
  - filesystem

required_permissions:
  - READ
  - WRITE

cost_class: MEDIUM
risk_class: LOW
performance_ref: skill-performance/frontend-implementation
entrypoint_ref: skills/frontend-implementation/SKILL.md
```

### Lazy loading rule

```text
1. baca registry metadata
2. shortlist kandidat
3. resolve dependency/conflict
4. pilih skill / chain
5. BARU buka SKILL.md skill terpilih
6. ambil knowledge refs relevan
7. execute
```

Dilarang melakukan `load all skills` hanya untuk mencari kecocokan.

---

# 29. DESCRIPTION CONTRACT — AGAR ROUTING TIDAK AMBIGU

Setiap skill wajib menjelaskan:

```text
WHAT IT DOES
USE WHEN
DO NOT USE WHEN
REQUIRES
PRODUCES
TOOLS / PERMISSIONS
FAILURE / STOP CONDITIONS
```

Skill dengan deskripsi terlalu umum harus ditandai:

```text
ROUTING_AMBIGUOUS
```

Contoh yang buruk:

```yaml
description: Analyze UI design.
```

Contoh yang dapat diroute:

```yaml
description: >
  Analyze screenshots, mockups, websites, and visual references
  to extract layout, hierarchy, spacing, typography, colors,
  interaction cues, and design language.

use_when:
  - visual reference is provided
  - another skill needs a structured design specification

do_not_use_when:
  - task is backend-only
  - visual reasoning is irrelevant
```

---

# 30. SINGLE-RESPONSIBILITY SKILL & DEDUPLICATION

Hindari skill yang saling menutupi tanpa batas jelas.

Buruk:

```text
web-development
website-builder
frontend-builder
web-design
ui-web-builder
```

Lebih baik:

```text
visual-reference-analysis
        ↓
ui-design-reasoning
        ↓
frontend-implementation
        ↓
interaction-animation
        ↓
visual-qa
```

Jika dua skill overlap:

```text
DETECT OVERLAP
   ↓
COMPARE CONTRACT
   ↓
CANONICAL SKILL?
   ├── YES → alias/deprecate duplicate
   └── NO  → perjelas boundary
```

Jangan menghapus skill existing secara otomatis. Gunakan status:

```text
ACTIVE
EXPERIMENTAL
DEPRECATED
QUARANTINED
```

---

# 31. SKILL MATCHING & RANKING

Skill Manager tidak memilih skill berdasarkan nama atau popularitas.

Sinyal minimum:

```text
Intent Match
Context Match
Input Compatibility
Output Requirement Match
Dependency Readiness
Tool Availability
Permission Compatibility
Risk Compatibility
Historical Performance (jika data cukup)
Cost / Latency Class
```

### Aturan penting tentang scoring

V4 **tidak menetapkan angka/bobot palsu secara default**.

Jika sistem belum memiliki data yang cukup, gunakan ranking kualitatif:

```text
STRONG_MATCH
GOOD_MATCH
WEAK_MATCH
REJECT
```

Jika nanti scoring numerik digunakan, formula dan bobot harus:
- terdokumentasi;
- dapat diaudit;
- dikalibrasi dari data nyata;
- tidak menggunakan performance score fiktif.

Output resolver:

```yaml
skill_plan:
  mode: SKILL_CHAIN
  primary:
    - ui-design-reasoning
  supporting:
    - visual-reference-analysis
    - frontend-implementation
  reviewer:
    - visual-qa
  rejected:
    - skill_id: backend-database-admin
      reason: domain_mismatch
```

---

# 32. NO_SKILL MODE

Skill bukan kewajiban.

```text
IF base capability dapat menyelesaikan task dengan baik
AND skill tidak memberi peningkatan material
AND tidak ada workflow wajib yang mensyaratkan skill
THEN NO_SKILL
```

NO_SKILL membantu:
- mengurangi context;
- mengurangi latency;
- menghindari konflik instruksi;
- mencegah over-orchestration.

NO_SKILL tetap tunduk pada permission, verification, dan policy biasa.

---

# 33. SKILL CHAIN BUILDER

Satu task dapat menggunakan beberapa skill dengan urutan dependency yang eksplisit.

Contoh:

```text
User: build website berdasarkan screenshot

visual-reference-analysis
        ↓ produces design_evidence
ui-design-reasoning
        ↓ produces design_spec
frontend-implementation
        ↓ produces frontend_code
interaction-animation      [optional jika diperlukan]
        ↓
visual-qa
        ↓ produces verification_evidence
```

Skill chain menjadi DAG jika ada cabang paralel:

```text
                  ┌─ accessibility-analysis ─┐
reference-analysis ─ ui-design-reasoning ─ frontend-build ─ visual-qa
                  └─ content-structure ──────┘
```

Mission Control wajib mencegah skill downstream berjalan sebelum required input tersedia.

---

# 34. SKILL DEPENDENCY & CONFLICT RESOLVER

Skill metadata dapat mempunyai:

```yaml
requires:
optional_dependencies:
followed_by:
compatible_with:
conflicts_with:
```

Conflict Resolver memeriksa:
- instruksi yang saling bertentangan;
- dua skill mencoba memiliki resource yang sama;
- output contract tidak kompatibel;
- tool/permission requirement bertentangan;
- skill versi lama yang sudah deprecated.

Jika konflik tidak dapat diselesaikan deterministik:

```text
SKILL_CONFLICT
   ↓
BIKAGENT
   ↓
HERMES DECISION
```

Jangan diam-diam menjalankan dua instruksi yang bertentangan.

---

# 35. AGENT ↔ SKILL COMPATIBILITY

Agent Registry diperluas:

```yaml
agent_id: B2
capability_profile:
  domains:
    - frontend
    - motion
  supported_skills:
    - frontend-implementation
    - responsive-layout
    - interaction-animation
  preferred_skills: []
  prohibited_skills:
    - production-db-migration
```

Routing final:

```text
TASK REQUIREMENT
      ↓
SKILL PLAN
      ↓
AGENT CAPABILITY MATCH
      ↓
PERMISSION
      ↓
AVAILABILITY / WORKLOAD
      ↓
RESOURCE / LOCK
      ↓
DISPATCH
```

Skill tidak boleh dipaksakan ke agent yang tidak mempunyai capability/tool/permission yang diperlukan.

---

# 36. CONTEXT PACKET V4

Context Packet diperluas tanpa membuatnya gemuk:

```yaml
mission_id:
task_id:
objective:
inputs:
constraints:
acceptance_criteria:
permissions:

skill_plan:
  mode: SKILL_CHAIN | SINGLE_SKILL | NO_SKILL
  selected:
  versions:
  execution_order:

knowledge_refs:
tool_refs:
relevant_decisions:
expected_artifacts:
```

Isi lengkap skill hanya dimuat pada executor yang membutuhkannya. Supporting agent lain tidak otomatis menerima semua skill instructions.

---

# 37. SKILL PERFORMANCE TRACKING

Setelah execution dan verification, simpan observasi performa skill.

```yaml
execution_id: SKEXEC-00091
mission_id: MIS-0042
task_id: TASK-007
agent_id: B2
skills:
  - visual-reference-analysis@1.2.0
  - ui-design-reasoning@2.1.0
  - frontend-implementation@1.3.0
verification:
  status: PASS
user_feedback: null
corrections: []
failure_attribution: []
observed_cost:
  tool_calls: 18
  retries: 0
lesson_refs: []
```

### Larangan

Jangan menyimpulkan:

```text
skill X sukses 94%
```

kecuali denominator, definisi success, sample window, dan data mentah tersedia.

Performance profile digunakan sebagai sinyal routing hanya jika bukti cukup.

---

# 38. SKILL IMPROVEMENT PIPELINE — ANTI INSTRUCTION DRIFT

Satu koreksi owner **tidak langsung mengubah skill produksi**.

```text
EXECUTION
   ↓
FEEDBACK / FAILURE EVIDENCE
   ↓
CANDIDATE IMPROVEMENT
   ↓
D4 SANDBOX TEST
   ↓
REGRESSION / ACCEPTANCE TEST
   ↓
PASS?
 ┌───────┴────────┐
 NO              YES
 ↓                ↓
REJECT      PROMOTE NEW VERSION
                   ↓
              UPDATE REGISTRY
                   ↓
             D2/D3 DOCUMENT
```

Setiap perubahan skill harus mempunyai:
- previous version;
- proposed version;
- reason;
- evidence;
- tests;
- rollback path;
- promotion status.

---

# 39. SKILL VERSIONING & PROVENANCE

Skill production wajib mempunyai versi.

```yaml
skill_id: ui-design-reasoning
version: 2.1.0
status: ACTIVE
previous: 2.0.3
source: internal
last_verified_at:
verified_by:
change_ref:
rollback_to: 2.0.3
```

Trace mission harus dapat menjawab:

```text
Skill versi berapa yang dipakai?
Kenapa skill itu dipilih?
Knowledge apa yang diambil?
Tool apa yang dipanggil?
Agent siapa yang mengeksekusi?
Verifier apa yang meluluskan?
```

---

# 40. EVENT PROTOCOL TAMBAHAN UNTUK SKILL OS

Tambahkan event:

```text
SKILL_CANDIDATES_FOUND
SKILL_SELECTED
SKILL_REJECTED
SKILL_CHAIN_BUILT
SKILL_DEPENDENCY_BLOCKED
SKILL_CONFLICT_DETECTED
SKILL_LOADED
SKILL_EXECUTION_STARTED
SKILL_EXECUTION_COMPLETED
SKILL_EXECUTION_FAILED
NO_SKILL_SELECTED
SKILL_FEEDBACK_RECORDED
SKILL_IMPROVEMENT_PROPOSED
SKILL_VERSION_PROMOTED
SKILL_VERSION_ROLLED_BACK
```

Event wajib membawa `trace_id`, `mission_id`, dan `task_id` bila relevan.

---

# 41. SINGLE SOURCE OF TRUTH V4

Hot runtime state diperluas:

```text
/runtime-state/
├── missions/
├── tasks/
├── agents/
├── skills/
│   ├── registry/
│   ├── resolutions/
│   ├── chains/
│   └── performance/
├── leases/
├── locks/
├── checkpoints/
├── traces/
├── approvals/
├── decisions/
└── artifacts/
```

Long-term knowledge tetap di Vault/Obsidian.

Skill instructions tidak boleh diperlakukan sebagai knowledge database besar. Skill merujuk knowledge yang diperlukan melalui `knowledge_refs`.

---

# 42. END-TO-END RUNTIME FLOW V4

```text
[1] OWNER REQUEST
       ↓
[2] HERMES: INTENT + OUTCOME
       ↓
[3] MISSION / TASK PLAN
       ↓
[4] SKILL MANAGER
       ├─ metadata search
       ├─ match/rank
       ├─ NO_SKILL check
       ├─ dependency/conflict
       └─ skill chain
       ↓
[5] AGENT ROUTER
       ├─ capability
       ├─ permission
       ├─ workload
       └─ resource/lock
       ↓
[6] CONTEXT BUILDER
       ├─ selected skill instructions only
       ├─ relevant knowledge refs only
       └─ required tools only
       ↓
[7] EXECUTION + HEARTBEAT + TRACE
       ↓
[8] ARTIFACT
       ↓
[9] INVARIANT VERIFICATION
       ↓
[10] RESULT / OWNER APPROVAL IF REQUIRED
       ↓
[11] PERFORMANCE EVIDENCE
       ↓
[12] D2/D3 LEARNING
       ↓
[13] SKILL IMPROVEMENT CANDIDATE IF JUSTIFIED
```

---

# 43. MIGRATION PLAN V4 — SKILL OS DI ATAS FONDASI MISSION CONTROL

V4 mempertahankan seluruh fondasi Mission Control yang sudah dibangun. Skill OS ditambahkan bertahap tanpa menonaktifkan workflow existing.

## PHASE S0 — Skill Inventory Read-Only

Petakan seluruh skill existing:
- path;
- entrypoint;
- description;
- trigger/use_when;
- dependency;
- tool requirement;
- permission requirement;
- overlap;
- version bila ada;
- usage evidence bila ada.

Output:
- `SKILL_INVENTORY.md`
- `SKILL_GAP_ANALYSIS.md`
- `SKILL_OVERLAP_MAP.md`

## PHASE S1 — Metadata Registry Shadow Mode

Bangun registry metadata tanpa mengubah routing existing.

Uji apakah request dapat menghasilkan shortlist skill yang masuk akal.

## PHASE S2 — NO_SKILL + Dependency + Conflict Resolver

Aktifkan resolver di shadow mode dan bandingkan dengan perilaku existing.

## PHASE S3 — Skill Chain Canary

Pilih satu mission risiko rendah.

Aktifkan lazy-load skill chain untuk mission tersebut saja.

## PHASE S4 — Performance Evidence

Catat execution, verifier result, user correction, retry, dan cost yang benar-benar teramati.

## PHASE S5 — Improvement Pipeline

Aktifkan candidate → sandbox → test → promote/version/rollback.

Hanya setelah S0-S5 lulus, Skill OS menjadi default untuk mission baru.

---

# 44. ACCEPTANCE TEST V4 — SKILL OS

Selain acceptance test Mission Control Foundation, wajib ada:

### Test K — Lazy Load
Request sederhana tidak menyebabkan semua skill dibaca.

### Test L — NO_SKILL
Task yang tidak mendapat manfaat material dari skill berjalan tanpa skill khusus.

### Test M — Skill Dependency
Skill downstream tertahan sampai required output tersedia.

### Test N — Conflict
Dua skill yang memiliki instruksi/resource conflict tidak dijalankan diam-diam.

### Test O — Agent/Skill Separation
Trace menunjukkan agent sebagai executor dan skill sebagai capability, bukan sebaliknya.

### Test P — Skill Version Trace
`/trace` dapat menunjukkan skill ID + version yang dipakai.

### Test Q — Performance Evidence
Tidak ada success-rate numerik tanpa dataset yang dapat diverifikasi.

### Test R — Improvement Safety
Koreksi user membuat candidate improvement, bukan langsung memodifikasi production skill.

### Test S — Regression
Mission Control, agent routing, approval, bot, cron, telemetry, Vault, dan workflow existing tetap sehat.

---

# 45. FINAL DOCTRINE V4

```text
OWNER DEFINES THE GOAL.
HERMES UNDERSTANDS INTENT AND DECIDES STRATEGY.
SKILL MANAGER RESOLVES THE RIGHT CAPABILITY.
AGENT ROUTER CHOOSES WHO EXECUTES.
MISSION CONTROL CONTROLS STATE, TIME, AUTHORITY AND RECOVERY.
THE AGENT USES ONLY THE SKILLS IT NEEDS.
TOOLS/MCP PERFORM AUTHORIZED ACTIONS.
KNOWLEDGE PROVIDES RELEVANT FACTS.
INVARIANT AUDITOR PROVES THE RESULT.
PERFORMANCE MEMORY LEARNS FROM EVIDENCE.
OBSIDIAN RETAINS VERIFIED KNOWLEDGE.
OWNER RETAINS CRITICAL AUTHORITY.
```

V4 menjadikan pertumbuhan jumlah skill sebagai **penambahan capability**, bukan penambahan beban context. Semakin banyak skill yang tersedia, Hermes tetap ringan karena hanya metadata yang dipakai saat routing dan hanya skill terpilih yang dimuat ketika benar-benar diperlukan.

