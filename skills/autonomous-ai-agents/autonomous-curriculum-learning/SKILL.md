---
name: autonomous-curriculum-learning
description: "Use when designing self-improvement experiments on deficits."
version: 1.1.0
author: Bagas Cihuy & Hermes
license: MIT
related_skills:
  - subagent-lifecycle-management
  - comprehensive-agent-governance
  - autonomous-orchestrator
  - multi-agent-deliberation
metadata:
  hermes:
    tags: [self-improving, curriculum-learning, autonomous-eval, fixed-evaluator, rigor, sandbox-experiments]
---

# Autonomous Curriculum Learning

Pemberantasan ilusi keahlian semu (*vanity skills*). Agen tidak mengejar kuantitas skill, melainkan bertindak sebagai perancang eksperimen peningkatan diri berbasis defisit empiris nyata.

## When to Use
- Mengidentifikasi pola kegagalan berulang (*repeated failures*) dari riwayat tugas.
- Mengidentifikasi celah doktrin yang belum teruji (*untested doctrines*) atau catatan gap di Obsidian Knowledge Vault (`/otak-koding/KNOWLEDGE/` & `BUKU_CATATAN/`).
- Merancang simulasi latihan bertingkat (3 tiers) di sandbox tertutup.
- Membuktikan peningkatan performa nyata di hadapan penguji independen (*fixed evaluator*) sebelum memperbarui skill.
- Menolak klaim perkembangan yang tidak memiliki bukti biner (Exit Code 0).

## Dua Mode Pembelajaran Mandiri (Dual-Mode Architecture)

### 🔴 Mode 1: Error-Driven Learning (Diagnosis Riwayat Kegagalan)
- **Fungsi:** Mengambil data riwayat error empiris di `state.db` (misal: deadlock subpath, parsing error, loop tool).
- **Shortcut CLI:** `hermes-learn --error` (atau `hermes-learn -e`).
- **Tujuan:** Menyembuhkan kelemahan operasional nyata yang pernah dialami pengguna.

### 📚 Mode 2: Knowledge-Gap-Driven Learning (Pindai & Lengkapi Celah Vault)
- **Fungsi:** Memindai 164+ bab di Obsidian Knowledge Vault via `src/knowledge_gap_scanner.py` untuk menemukan doktrin berstatus `UNTESTED` atau anotasi celah (`Gap:`, `Belum diuji:`, `TODO:`).
- **Shortcut CLI:** `hermes-learn --gap` (atau `hermes-learn -g`).
- **Tujuan:** Menutup celah arsitektur secara proaktif di sandbox sebelum meledak menjadi error di produksi.

### ⚡ Mode Dual:
- **Shortcut CLI:** `hermes-learn --all` (atau `hermes-learn -a`) untuk menjalankan audit error disusul penutupan celah vault secara berurutan.

## Arsitektur Enam Pilar (Hermes Autonomous Learning Engine)
Direktori kerja modul: `/home/ubuntu/hermes-learning-engine/`
1. **Pembaca Riwayat (Learning Analyzer):** Memindai `state.db` dan log server untuk mendeteksi pola gagal berulang (loop tool, error OS, deadlock subpath, rollback). Berkas: `src/learning_analyzer.py`.
2. **Direktur Riset (Research Director):** Menentukan prioritas penelitian strategis jangka panjang berdasarkan Net Value of Information (VOI), dampak sistemik, dan frekuensi. Berkas: `src/research_director.py`.
3. **Perancang Kurikulum (Curriculum Planner):** Merumuskan kontrak latihan bertingkat (Beginner, Intermediate, Advanced) dengan 3 pilar wajib. Berkas: `src/curriculum_planner.py`.
4. **Pelaksana Eksperimen Sandbox (Experiment Runner):** Menjalankan latihan di lingkungan terisolasi (`sandbox/`). Berkas: `src/experiment_runner.py`.
5. **Penguji Independen Kaku (Learning Supervisor / Fixed Evaluator):** Menilai kelulusan dengan kriteria tetap (*immutable assertions*), terpisah dari izin worker. Berkas: `evaluators/supervisor_evaluator.py`.
6. **Pengoptimal Pengetahuan (Knowledge Optimizer):** Menguji regresi lama dan mempromosikan hasil latihan ke sistem hanya jika terbukti lulus biner (Exit Code 0). Berkas: `src/knowledge_optimizer.py`.

## Tiga Pilar Wajib Kontrak Kurikulum (The Trinity of Rigor)
Dilarang membuat modul latihan atau skill baru tanpa menulis kontrak resmi di `curriculum/<DEFICIT_NAME>.json`:

1. **Mengapa Latihan Ini Penting (Diagnostic Why):**
   - Wajib mencantumkan data frekuensi insiden riil dari riwayat (misal: "12 insiden subpath CSRF deadlock").
   - Rumuskan hipotesis kausal kegagalan teknis, bukan sekadar ketertarikan pada topik baru.
2. **Gimana Cara Nguji Keberhasilannya (Fixed Sandbox Harness):**
   - Tetapkan perintah penguji otomatis yang dijalankan oleh Supervisor independen.
   - Kriteria kelulusan tidak boleh ditentukan oleh agen yang sedang diuji (*Anti-Self-Report*).
3. **Kapan Dianggap Berhasil (Quantitative Pass Threshold):**
   - Bandingkan baseline performa lama vs performa baru.
   - Wajib: Seluruh skenario latihan lulus biner (`Exit Code 0`) + Uji regresi lama 100% aman (*Zero Regression*).
   - **Aturan Pembuktian:** Jika metrik performa baru tidak melampaui baseline lama, agen **DILARANG MENGKLAIM BERKEMBANG** dan eksperimen berstatus `REJECTED`.

## Kebijakan Operasional Jadwal: Manual On-Demand (Zero Background Mutation)
- Mode pembelajaran mandiri **100% PURE ON-DEMAND**: hanya berjalan saat diperintahkan Mas Bagas di chat.
- **TIDAK ADA cronjob otomatis 24 jam**: menjaga RAM/CPU tetap dingin dan mencegah mutasi kode liar tanpa izin.
- Setiap siklus berjalan dalam batas ketat (*bounded one-shot*), maksimal 3 iterasi, dan langsung kembali ke status IDLE setelah menyajikan laporan 9 parameter.
- Eksekusi master pipeline terpadu via: `python3 /home/ubuntu/hermes-learning-engine/run_learning_pipeline.py`.

## Batasan Eksekusi (Guardrails):
- Jalankan dalam siklus terbatas (*one-shot bounded execution*), bukan background loop 24 jam penuh.
- Batasi kuota percobaan maksimal 3 iterasi per eksperimen.
- Pisahkan wewenang mutlak: Hermes Worker yang belajar dilarang keras mengubah kode evaluator/penguji independen.
- Eksekusi master pipeline terpadu via: `python3 /home/ubuntu/hermes-learning-engine/run_learning_pipeline.py`.
