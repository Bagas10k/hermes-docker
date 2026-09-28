# HERMES ORCHESTRATOR V4 — PACKAGE README

Paket ini adalah penyempurnaan non-destructive dari V3. Struktur Hermes, BIKAGENT, Invariant Auditor, dan Divisi A/B/C/D tetap dipertahankan. V4 menambahkan Skill Operating System sebagai capability layer di dalam Mission Control.

## Isi

1. `HIERARKI_STRUKTUR_TIM_DAN_WORKFLOW_AGEN_V4_MISSION_CONTROL_SKILL_OS.md`
   - Doktrin arsitektur lengkap.
   - Mission Control + Skill OS.
   - Registry, scheduler, recovery, permission, trace, skill routing, lazy load, NO_SKILL, versioning, dan learning.

2. `PROMPT_SETUP_HERMES_ORCHESTRATOR_V4_SKILL_OS.md`
   - Prompt implementasi untuk Hermes.
   - Wajib mulai dengan audit read-only.
   - Tidak boleh rewrite sistem dari nol.
   - Memetakan runtime dan skill existing sebelum mutation.

3. `HERMES_SKILL_OPTIMIZATION_SYSTEM_SOURCE.md`
   - Salinan masukan Skill Optimization yang menjadi sumber integrasi V4.

## Cara pakai

1. Simpan doktrin V4 di area dokumentasi sistem.
2. Berikan prompt setup V4 kepada Hermes dari ruang kerja utama.
3. Biarkan Hermes menyelesaikan Phase 0 + S0 dalam read-only mode.
4. Review `CURRENT_STATE_MAP.md`, `GAP_ANALYSIS_V4.md`, `IMPLEMENTATION_PLAN_V4.md`, `SKILL_INVENTORY.md`, `SKILL_OVERLAP_MAP.md`, dan `SKILL_MIGRATION_PLAN.md`.
5. Setelah itu, migrasi berjalan shadow → canary → verified adoption.

## Prinsip inti

```text
Owner menetapkan tujuan.
Hermes menentukan strategi.
Skill Manager menentukan capability.
Agent Router menentukan executor.
Mission Control menjaga runtime.
Agent menggunakan skill terpilih secara lazy.
Tool/MCP melakukan aksi terotorisasi.
Invariant Auditor memverifikasi.
Vault menyimpan knowledge terverifikasi.
```

Jangan load semua skill sekaligus dan jangan mengubah production skill hanya karena satu koreksi.
