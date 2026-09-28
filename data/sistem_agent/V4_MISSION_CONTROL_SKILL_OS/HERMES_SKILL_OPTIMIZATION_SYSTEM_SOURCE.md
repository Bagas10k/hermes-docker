# HERMES SKILL OPTIMIZATION SYSTEM

## Tujuan
Membuat Hermes mampu menggunakan banyak skill secara optimal tanpa harus diperintah satu per satu.

Prinsip utama:

> Hermes tidak perlu menghafal semua skill. Hermes harus mampu mencari, memilih, menyusun, menjalankan, dan mengevaluasi skill yang paling tepat sesuai konteks tugas.

---

## 1. Arsitektur Utama

```text
USER
  ↓
MAIN ORCHESTRATOR
  ↓
INTENT ANALYZER
  ↓
SKILL MANAGER
  ├─ Skill Registry
  ├─ Skill Matching
  ├─ Skill Ranking
  ├─ Dependency Resolver
  ├─ Conflict Resolver
  └─ Skill Chain Builder
  ↓
AGENT ROUTER
  ↓
AGENT / EXECUTOR
  ↓
TOOLS / MCP
  ↓
VERIFIER
  ↓
RESULT
  ↓
PERFORMANCE MEMORY
```

---

## 2. Peran Tiap Komponen

### Orchestrator
Menjadi pintu utama dari user ke seluruh sistem.

Tugas:
- memahami permintaan
- membagi tugas
- memilih agent
- meminta Skill Manager menentukan kemampuan yang diperlukan
- mengumpulkan hasil
- memantau progres

### Skill Manager
Mengatur seluruh skill Hermes.

Tugas:
- mencari skill relevan
- memberi ranking
- menentukan primary dan supporting skill
- membangun skill chain
- mengecek dependency
- mendeteksi konflik antar-skill
- memilih NO_SKILL jika skill tidak diperlukan

---

## 3. Skill Registry

Setiap skill harus memiliki metadata yang ringkas.

Contoh:

```yaml
id: frontend-implementation

domain:
  - frontend
  - web

capabilities:
  - react
  - html
  - css
  - responsive-layout

requires:
  - design_spec

produces:
  - frontend_code

compatible_with:
  - visual-reference-analysis
  - ui-design-reasoning
  - visual-qa

priority: normal
cost: medium
```

Hermes cukup membaca metadata ini saat melakukan routing.

Isi lengkap skill baru dibuka jika skill terpilih.

---

## 4. Description Skill Harus Jelas

Jangan:

```yaml
description: Analyze UI design.
```

Gunakan:

```yaml
description: >
  Analyze screenshots, mockups, websites, and visual references
  to extract layout, hierarchy, spacing, typography, colors,
  interaction cues, and overall design language.

  Use when:
  - user provides visual references
  - user asks to imitate a visual style
  - another skill needs design information

  Do not use when:
  - task is backend-only
  - visual reasoning is not required
```

Description adalah bagian penting dari sistem routing skill.

---

## 5. Skill Harus Punya Tanggung Jawab Spesifik

Hindari banyak skill yang fungsinya hampir sama.

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

Setiap skill memiliki satu tanggung jawab utama.

---

## 6. Skill Scoring

Hermes tidak langsung memilih skill.

Setiap kandidat diberi skor.

Contoh:

```text
Skill: ui-design-reasoning

Intent Match       0.95
Context Match      0.90
Input Match        0.90
Dependency Match   0.85
Performance Score  0.90

Final Score        0.90
```

Lalu tentukan:

```text
PRIMARY SKILL
ui-design-reasoning

SUPPORTING SKILL
frontend-debugging
```

---

## 7. NO_SKILL Mode

Hermes tidak wajib menggunakan skill.

Rule:

```text
IF base_model_can_handle_task
AND skill_does_not_materially_improve_result
THEN
    NO_SKILL
```

Tujuan:
- menghemat token
- mengurangi latency
- menghindari konflik instruksi
- membuat sistem lebih ringan

---

## 8. Skill Chain

Satu tugas bisa membutuhkan beberapa skill.

Contoh user:

> Build website berdasarkan screenshot ini dan pertahankan vibe desainnya.

Hermes membentuk:

```text
visual-reference-analysis
        ↓
ui-design-reasoning
        ↓
frontend-implementation
        ↓
visual-qa
```

User tidak perlu memerintahkan tiap tahap secara manual.

---

## 9. Dependency Skill

Contoh:

```yaml
requires:
  - visual-reference-analysis

optional:
  - design-trend-research

followed_by:
  - visual-qa
```

Skill Manager otomatis menyusun urutan eksekusi.

---

## 10. Bedakan Agent, Skill, Tool, Knowledge, dan Memory

```text
AGENT
= siapa yang mengerjakan

SKILL
= kemampuan yang digunakan

TOOL / MCP
= alat untuk melakukan tindakan

KNOWLEDGE
= informasi dan referensi yang digunakan

MEMORY
= pengalaman dan hasil sebelumnya
```

Contoh:

```text
Frontend Agent
│
├── Skills
│   ├─ frontend-implementation
│   ├─ responsive-layout
│   └─ interaction-animation
│
├── Tools
│   ├─ browser
│   ├─ terminal
│   └─ filesystem
│
└── Knowledge
    └─ frontend vault
```

---

## 11. Skill ≠ Knowledge

Skill:

```text
Bagaimana melakukan sesuatu.
```

Knowledge:

```text
Apa yang perlu diketahui.
```

Contoh:

```text
Skill:
ui-design-reasoning

Vault:
├── typography
├── spacing
├── color-theory
├── dashboard-patterns
├── mobile-ui
└── design-trends
```

Skill hanya mengambil knowledge yang relevan saat dibutuhkan.

---

## 12. Skill Performance Tracking

Setelah eksekusi, simpan performanya.

Contoh:

```yaml
task: build-dashboard-from-reference

skills:
  - visual-reference-analysis
  - ui-design-reasoning
  - frontend-implementation

outcome: success

user_correction:
  - padding terlalu besar

failure_attribution:
  - ui-design-reasoning

lesson:
  - avoid overly generous spacing on dense dashboard layouts
```

Dashboard performa:

```text
visual-reference-analysis
success: 94%
usage: 181
corrections: 9

ui-design-reasoning
success: 79%
usage: 143
corrections: 31

frontend-implementation
success: 91%
usage: 220
corrections: 14
```

Skill yang sering gagal menjadi prioritas tuning.

---

## 13. Skill Improvement Pipeline

Jangan langsung mengubah skill setelah satu koreksi user.

Gunakan:

```text
Execution
   ↓
Feedback
   ↓
Candidate Improvement
   ↓
Evaluation
   ↓
Testing
   ↓
PASS?
├─ YES → Promote
└─ NO  → Reject
```

Ini mencegah instruction drift.

---

## 14. Arsitektur Akhir Hermes

```text
                         USER
                           │
                           ▼
                  MAIN ORCHESTRATOR
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
     Intent Engine     Context Engine    Memory Engine
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                    TASK PLANNER
                           │
                           ▼
                    SKILL MANAGER
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
    Skill Registry    Skill Ranking    Skill Composer
                           │
                           ▼
                    AGENT ROUTER
                           │
       ┌───────────┬───────┼───────┬───────────┐
       ▼           ▼       ▼       ▼           ▼
    Agent 1     Agent 2  Agent 3   ...      Agent 10
                           │
                           ▼
                      TOOLS / MCP
                           │
                           ▼
                       EXECUTION
                           │
                           ▼
                       VERIFIER
                           │
                           ▼
                        RESULT
                           │
                           ▼
              PERFORMANCE / LEARNING ENGINE
                           │
                           ▼
                     OBSIDIAN VAULT
```

---

## 15. Prinsip Final

1. Jangan load semua skill sekaligus.
2. Metadata skill selalu ringan.
3. Isi skill hanya dibaca ketika dibutuhkan.
4. Satu skill = satu tanggung jawab jelas.
5. Izinkan multi-skill chain.
6. Izinkan NO_SKILL.
7. Skill Manager memilih skill, bukan user.
8. Agent menggunakan skill; skill bukan agent.
9. Knowledge dipisahkan dari skill.
10. Semua skill memiliki performance history.
11. Skill yang gagal dituning berdasarkan bukti.
12. Perubahan skill harus diuji sebelum dipromosikan.

---

## Target Akhir

Hermes harus mampu menerima instruksi seperti:

```text
"Buat dashboard berdasarkan referensi ini,
gunakan sistem yang sudah ada,
jangan ubah struktur utama,
dan pastikan hasil akhirnya konsisten."
```

Tanpa user perlu mengatakan:

```text
gunakan skill A
gunakan skill B
ambil knowledge C
gunakan agent D
gunakan MCP E
review pakai skill F
```

Hermes sendiri yang menentukan:

```text
Intent
→ Context
→ Plan
→ Agent
→ Skill Chain
→ Knowledge
→ Tools
→ Execution
→ Verification
→ Learning
```

Dengan begitu, semakin banyak skill yang dimiliki Hermes,
semakin luas kemampuan sistem tanpa membuat orchestrator semakin berat.
