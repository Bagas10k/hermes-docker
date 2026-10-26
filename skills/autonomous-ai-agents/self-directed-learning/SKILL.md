---
name: autonomous-curriculum-learning
description: "Use when designing self-improvement experiments on deficits."
version: 1.2.0
author: Bagas Cihuy & Hermes
license: MIT
related_skills:
  - subagent-lifecycle-management
  - comprehensive-agent-governance
  - autonomous-orchestrator
  - multi-agent-deliberation
metadata:
  hermes:
    tags: [self-improving, curriculum-learning, autonomous-eval, fixed-evaluator, rigor, sandbox-experiments, baseline-vs-challenger]
---

# Autonomous Curriculum Learning

Pemberantasan ilusi keahlian semu (*vanity skills*). Agen tidak mengejar kuantitas skill, melainkan bertindak sebagai perancang eksperimen peningkatan diri berbasis defisit empiris nyata.

## When to Use
- Mengidentifikasi pola kegagalan berulang (*repeated failures*) dari riwayat tugas (`state.db`).
- Menjalankan siklus 6 tahap pembelajaran mandiri terisolasi di `/home/ubuntu/hermes-learning-engine/`.
- Membandingkan performa penantang (*challenger*) terhadap patokan lama (*baseline*) dengan syarat kenaikan minimal +5%.
- Membuktikan peningkatan kemampuan nyata di hadapan penguji independen (*fixed evaluator*) sebelum memperbarui sistem.
- Menolak klaim perkembangan yang tidak memiliki bukti biner (`Exit Code 0`) atau yang menyebabkan regresi pada kemampuan lama.

## Dual-Mode Learning: Error-Driven vs Knowledge-Gap-Driven
Sistem pembelajaran mandiri mendukung dua mode penemuan kurikulum:
1. **Mode 1: Error-Driven Learning (Diagnosis Riwayat Kegagalan)**
   - Pemicu: Pola kegagalan berulang di `state.db` (misal 3+ deadlock, loop tool, crash).
   - Tujuan: Menemukan akar penyebab dan menyembuhkan bug dengan mitigasi teruji.
2. **Mode 2: Knowledge-Gap-Driven Learning (Pindai & Lengkapi Celah Vault)**
   - Pemicu: Pemindaian Obsidian Vault via `src/knowledge_gap_scanner.py`.
   - Sasaran: Doktrin di `KNOWLEDGE/INDEX.md` yang berstatus `UNTESTED`, catatan celah eksplisit (`Gap:`, `Belum diuji`, `TODO`), dan konsep gantung.
   - Tujuan: Membangun harness pengujian biner di sandbox sebelum celah tersebut meledak menjadi error di produksi.

## Antarmuka Pemicu Cepat (Shortcut Triggers)
Dua jalur pemicu cepat telah distandarisasi untuk kenyamanan Mas Bagas:
- **Jalur Chat Telegram (Direct In-Chat Shortcut):**
  - Mode 1: `/learn error` (atau `!learn-error`, `belajar error`)
  - Mode 2: `/learn gap` (atau `!learn-gap`, `belajar gap`)
  - Mode Dual: `/learn all` (atau `!learn-all`, `belajar semua`)
- **Jalur Terminal Linux:**
  - Binary executable: `/home/ubuntu/.local/bin/hermes-learn`
  - Sintaks: `hermes-learn --error` (-e), `hermes-learn --gap` (-g), atau `hermes-learn --all` (-a).

## Arsitektur Enam Pilar (Hermes Autonomous Learning Engine)
Direktori kerja modul: `/home/ubuntu/hermes-learning-engine/`
1. **Pembaca Riwayat (Learning Analyzer):** Memindai `state.db` dan log server untuk mendeteksi pola gagal berulang (loop tool, error OS, deadlock subpath, rollback). Berkas: `src/learning_analyzer.py`.
2. **Direktur Riset (Research Director):** Menentukan prioritas penelitian strategis jangka panjang berdasarkan Net Value of Information (VOI), dampak sistemik, dan frekuensi insiden. Berkas: `src/research_director.py`.
3. **Perancang Kurikulum (Curriculum Planner):** Merumuskan kontrak latihan bertingkat (Beginner, Intermediate, Advanced) dengan 3 pilar wajib. Berkas: `src/curriculum_planner.py`.
4. **Pelaksana Eksperimen Sandbox (Experiment Runner):** Menjalankan latihan di lingkungan terisolasi (`sandbox/`). Berkas: `src/experiment_runner.py`.
5. **Penguji Independen Kaku (Learning Supervisor / Fixed Evaluator):** Menilai kelulusan dengan kriteria tetap (*immutable assertions*), terpisah mutlak dari wewenang agen pembelajar. Berkas: `evaluators/supervisor_evaluator.py`.
6. **Pengoptimal Pengetahuan (Knowledge Optimizer):** Memverifikasi *zero regression* dan mengkristalisasi aturan baru ke sistem hanya jika terbukti lulus biner (Exit Code 0). Berkas: `src/knowledge_optimizer.py`.

## Tiga Pilar Wajib Kontrak Kurikulum (The Trinity of Rigor)
Dilarang membuat modul latihan atau skill baru tanpa menulis kontrak resmi di `curriculum/<DEFICIT_NAME>.json`:

1. **Mengapa Latihan Ini Penting (Diagnostic Why):**
   - Wajib mencantumkan data frekuensi insiden riil dari riwayat (misal: "12 insiden subpath CSRF deadlock" atau "3 insiden blocked workdir").
   - Rumuskan hipotesis kausal kegagalan teknis, bukan sekadar ketertarikan pada topik baru.
2. **Gimana Cara Nguji Keberhasilannya (Fixed Sandbox Harness):**
   - Tetapkan perintah penguji otomatis yang dijalankan oleh Supervisor independen.
   - Kriteria kelulusan tidak boleh ditentukan oleh agen yang sedang diuji (*Anti-Self-Report*).
3. **Kapan Dianggap Berhasil (Quantitative Pass Threshold):**
   - Bandingkan baseline performa lama vs performa baru.
   - Wajib: Seluruh skenario latihan lulus biner (`Exit Code 0`) + Uji regresi lama 100% aman (*Zero Regression*).
   - **Aturan Pembuktian:** Jika metrik performa baru tidak melampaui baseline lama minimal +5%, agen **DILARANG MENGKLAIM BERKEMBANG** dan eksperimen berstatus `REJECTED`.

## Kebijakan Operasional Jadwal: Manual On-Demand (Zero Background Mutation)
- Mode pembelajaran mandiri **100% PURE ON-DEMAND**: hanya berjalan saat diperintahkan Mas Bagas di chat.
- **TIDAK ADA cronjob otomatis 24 jam**: menjaga RAM/CPU tetap dingin dan mencegah mutasi kode liar tanpa izin.
- Setiap siklus berjalan dalam batas ketat (*bounded one-shot*), maksimal 3 iterasi, dan langsung kembali ke status IDLE setelah menyajikan laporan 9 parameter.
- Eksekusi master pipeline terpadu via: `python3 /home/ubuntu/hermes-learning-engine/run_learning_pipeline.py`.

## Standar Format Laporan Siklus Pembelajaran (Wajib 9 Parameter)
Setiap kali menyelesaikan satu siklus pembelajaran, agen WAJIB menyajikan laporan terstruktur:
1. **OBJECTIVE:** Apa yang ingin ditingkatkan?
2. **BASELINE:** Bagaimana kemampuan sebelumnya?
3. **EXPERIMENT:** Apa yang dilakukan di sandbox?
4. **EVIDENCE:** Apa bukti fisiknya (Exit Code 0, hash, latency)?
5. **EVALUATION:** Apakah terjadi peningkatan yang terukur?
6. **REGRESSION:** Apakah kemampuan lama terdampak? (Wajib Zero Regression).
7. **DECISION:** Diterima (`PROMOTED_TO_PRODUCTION`), Ditolak (`REJECTED`), atau Butuh Uji Tambahan.
8. **NEXT ACTION:** Apa langkah berikutnya?

## Batasan Eksekusi & Guardrails Keras:
- Jalankan dalam siklus terbatas (*one-shot bounded execution*), bukan background loop 24 jam penuh.
- Batasi kuota percobaan maksimal 3 iterasi per eksperimen.
- Pisahkan wewenang mutlak: Hermes Worker yang belajar dilarang keras mengubah kode evaluator/penguji independen.
- Menolak klaim perkembangan diri jika delta kenaikan skor < 5% atau jika ditemukan 1 pun regresi pada kemampuan lama.
