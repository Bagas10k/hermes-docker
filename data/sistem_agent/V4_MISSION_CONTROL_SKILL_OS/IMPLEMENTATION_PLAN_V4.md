# IMPLEMENTATION PLAN — HERMES ORCHESTRATOR V4 & SKILL OS
**Tanggal:** 28 September 2026  
**Prinsip Utama:** Non-destructive, additive, zero downtime, shadow-first.  
**Dasar Implementasi:** Temuan aktual dari `CURRENT_STATE_MAP.md` dan `GAP_ANALYSIS_V4.md`.

---

## Rute Eksekusi 5 Fase

### PHASE 1 — Registry & Shadow Mode (Fondasi Data Tanpa Mengubah Eksekusi)
- **Scope:**
  - Inisialisasi basis data SQLite terpusat: `/home/ubuntu/otak-koding/SISTEM_AGENT/V4_MISSION_CONTROL_SKILL_OS/mission_control.sqlite`.
  - Membuat skema tabel inti: `missions`, `tasks`, `agent_registry`, `event_logs`, `artifacts`.
  - Membangun `Skill OS Metadata Registry` (`skills_registry.json`) dari 232 skill yang ada.
- **Service/File yang Disentuh:**
  - Hanya file baru di direktori `V4_MISSION_CONTROL_SKILL_OS/`.
  - Layanan produksi (PM2, cron, gateway) sama sekali tidak diubah.
- **Risk:** Sangat rendah (Read-only indexing).
- **Rollback:** Cukup hapus folder database jika ada kegagalan skema.
- **Acceptance Test:** SQLite schema validation passes, 232 skills terindeks tanpa error parsing.

### PHASE 2 — Progress, Heartbeat & Event Envelope (Observabilitas Lintas Divisi)
- **Scope:**
  - Menstandarkan Event Envelope (`trace_id`, `mission_id`, `task_id`, `event_type`, `payload`).
  - Mengintegrasikan logger telemetri ringan ke runner Divisi 1 dan Divisi 2 untuk mencatat progres ke SQLite.
  - Memasang heartbeat lease checker (mendeteksi task zombie yang hang > 15 menit).
- **Service/File yang Disentuh:**
  - Helper module: `otak-koding/SISTEM_AGENT/V4_MISSION_CONTROL_SKILL_OS/lib/telemetry-hook.js`.
- **Risk:** Rendah (Hook asynchronous non-blocking; jika database sibuk, task utama tetap jalan).
- **Rollback:** Matikan flag `V4_TELEMETRY_ENABLED=false`.
- **Acceptance Test:** 1 task background tercatat di `event_logs` dengan trace ID valid.

### PHASE 3 — Controlled Scheduler Canary (Uji Coba 1 Alur Tugas Terisolasi)
- **Scope:**
  - Memilih 1 misi percontohan (misalnya: kurasi berita atau pengujian build lab kecil) untuk dijadwalkan lewat Mission Control DAG Engine.
  - Menguji `Skill Chain Builder` (misal: `design-md` -> `impeccable` -> `playwright`).
- **Service/File yang Disentuh:**
  - Script canary mandiri: `scripts/canary-mission-runner.js`.
- **Risk:** Sedang (Uji coba terbatas, tidak menyentuh database transaksi produksi).
- **Rollback:** Hentikan proses canary.
- **Acceptance Test:** Misi canary selesai 100% dengan status `VERIFIED` dan artefak tersimpan di registry.

### PHASE 4 — Permission, Lock & Recovery (Penegakan Invarian & Keamanan)
- **Scope:**
  - Mengikat `NEGATIVE_CONSTRAINTS.json` langsung ke Mission Control Gatekeeper sebelum task di-dispatch.
  - Menerapkan workspace lock berbasis file/cgroup untuk mencegah tabrakan resource RAM antar sub-agen.
  - Memasang checkpoint recovery otomatis jika terjadi restart server tak terduga.
- **Service/File yang Disentuh:**
  - `otak-koding/SISTEM_AGENT/V4_MISSION_CONTROL_SKILL_OS/lib/guardrail-enforcer.js`.
- **Risk:** Sedang (Memastikan gatekeeper tidak memblokir operasi yang sah).
- **Rollback:** Disable gatekeeper hook, kembali ke manual approval queue.
- **Acceptance Test:** Percobaan aksi terlarang (misal auto-publish tanpa izin) berhasil ditolak 100% oleh guardrail.

### PHASE 5 — Full Orchestration & Default V4
- **Scope:**
  - Mengintegrasikan Mission Control dan Skill OS ke alur kerja harian Hermes GM dan Bikagent Dispatcher.
  - Hermes secara otomatis menerapkan routing: `Intent` -> `Skill Matching` -> `Agent Dispatch` -> `Audit Gate` -> `Owner Approval`.
- **Service/File yang Disentuh:**
  - Memperbarui dokumentasi operasional dan memory jangka panjang.
- **Risk:** Rendah (Karena seluruh komponen telah melewati verifikasi Fase 1-4).
- **Rollback:** Kembali ke mode V3 manual.
- **Acceptance Test:** Misi end-to-end dari instruksi Mas Bagas berhasil dijalankan dengan pemikiran minimum, token hemat, dan verifikasi tuntas.
