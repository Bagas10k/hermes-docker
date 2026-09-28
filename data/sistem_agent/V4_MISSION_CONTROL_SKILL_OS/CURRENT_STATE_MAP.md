# CURRENT STATE MAP — AUDIT SISTEM HERMES RUNTIME
**Tanggal:** 28 September 2026  
**Status Audit:** READ-ONLY EMPIRICAL DISCOVERY  
**Scope:** Host Ubuntu Linux, PM2 Services, Hermes Gateways, Cron Jobs, Skill Repositories, Storage  

---

## 1. OBSERVED (Fakta Nyata Terverifikasi Empiris)

### A. Rantai Komando & Profile Gateway
- **Level 0 (Owner):** Mas Bagas Saputra (Bagas Cihuy). Kontrol approval mutlak via Telegram & CLI.
- **Level 1 (General Manager):** Hermes Gateway aktif (PID 2357734) menggunakan profile `default` (@bakagent_bot). Beroperasi di Telegram "ruang kerja" (-5050099384).
- **Level 2A (Operational Dispatcher):** Bikagent Gateway aktif (PID 2583538) menggunakan profile `bikagent` (@Bekbekk_bot).
- **Level 2B (Invariant Auditor):** Gerbang verifikasi pengujian:
  - Frontend: `design_qa_scan.py` (0 findings), Playwright (3 viewport), Axe-Core (0 violations), Impeccable (0 anti-patterns).
  - Social: `qc-inspector.js` SputarBall & Sputarai (ambang batas skor >= 80).
- **Level 3 (4 Divisi Spesialis):**
  - Divisi 1: Konten & Social AI (`sputarball`, `sputarball-ml-scorer`, `sputarai-ml-scorer`, `penelitian-ai`).
  - Divisi 2: Web & UI/UX Craft (`agent-forge-web`, `kinetic-motion-lab-web`, `katalog-portofolio-web`, `fleet-ops-web`).
  - Divisi 3: Infra, Security & Ops (`cf-tunnel-1/2`, Supabase :8000, PM2 17 services).
  - Divisi 4: Continuous Learning Autopilot (`hermes-autopilot-learner`, `social-content-learning-loop`).

### B. Approval Gateway & Negative Constraints (Tahap 1 & 2 Baru)
- File aturan terpusat: `/home/ubuntu/otak-koding/SISTEM_AGENT/NEGATIVE_CONSTRAINTS.json` (hard veto on auto-publish, generic pitches, clickbait, emoji).
- File antrean persetujuan: `/home/ubuntu/otak-koding/SISTEM_AGENT/APPROVAL_QUEUE.json`.
- Dispatcher CLI: `/home/ubuntu/.local/bin/approval-queue` (`list`, `approve <id>`, `reject <id>`).
- Interactive Telegram Endpoint: `https://www.jajandigital.web.id/api/approval` (HTTP 200 via Express & Cloudflare Tunnel).
- Inline Keyboard Buttons: Pesan Telegram supergroup BAgent (-1004397580704) dilengkapi tombol `[APPROVE PUBLISH]` dan `[REJECT]`.

### C. Background Jobs & Cron Runtime
- Cron scheduler Hermes aktif dengan 11 jobs terdaftar di `~/.hermes/cron/jobs.json`:
  - `token-quota-sentinel` (every 30m, active)
  - `rdp-garbage-collector` (daily 03:00, active)
  - `nightly-ui-ux-researcher` (daily 01:00, active)
  - `sputarai-instant-news-trigger` (every 20m, active, staging-only)
  - `sputarai-video-reels-publisher` (daily 12:30/19:30, active)
  - `sputarball-subagent-patrol` (every 15m, active, staging-only)
  - `sputarball-radar-cctv` (every 15m, active)
  - `sputarball-daily-cleaner` (daily 02:30, active)
  - `hermes-autopilot-learner` (every 30m, active)
  - `foundry-nightly-sprint` (daily 02:00, active)
  - `social-content-learning-loop` (every 60m, active)

### D. Skill Repository & Curator Telemetry
- Total 232 berkas `SKILL.md` terpasang di `~/.hermes/skills/` terbagi dalam 20 subdirektori.
- Curator sidecar di `~/.hermes/skills/.usage.json` melacak 164 entri penggunaan historis (top: `otak-koding` 835x, `hermes-autopilot` 571x, `mathematical-problem-solving` 515x).

---

## 2. ASSUMED (Asumsi Dokumen yang Butuh Validasi Runtime)
- KANVAS Kanban multi-agent engine diasumsikan siap mengorkestrasi sub-agent otonom antar-profile, namun belum diintegrasikan sebagai engine default pada tugas harian.
- `state.db` SQLite FTS5 diasumsikan memiliki riwayat pencarian sesi lintas platform, namun belum terikat pada W3C trace ID mission control.

---

## 3. NOT_FOUND (Fitur V4 yang Benar-Benar Belum Ada di Lingkungan)
- Belum ada `Mission Registry` terpusat yang melacak status mission lifecycle (PENDING -> SCHEDULED -> RUNNING -> VERIFIED -> COMPLETED).
- Belum ada `Task Ledger` lintas agent dengan distributed locking dan heartbeat lease per task.
- Belum ada `Skill OS Resolver` yang melakukan metadata-first matching, ranking, `NO_SKILL` check, dan conflict resolution sebelum eksekusi.
- Belum ada event envelope formal (`mission_id`, `task_id`, `event_type`, `trace_id`, `payload`).
- Belum ada sandboxed tool permission matrix di level kernel/process namespace.

---

## 4. NEEDS_VERIFICATION (Perlu Konfirmasi & Observasi Lanjutan)
- Apakah Supabase Self-Hosted (:8000) `pgvector` sudah memiliki tabel aktif untuk memori semantik V4, atau baru tabel memori default.
- Apakah Cloudflare Tunnel ingress memiliki batas latency atau timeout untuk stream WebSocket telemetry panjang.
