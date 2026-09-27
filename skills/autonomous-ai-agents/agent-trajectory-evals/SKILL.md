---
name: agent-trajectory-evals
description: Evaluate agent trajectories, step pass rates, and pass^k.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [agent-eval, trajectory-analysis, pass-k, benchmark, monte-carlo, verifier]
    related_skills: [mathematical-problem-solving, autonomous-orchestrator, agent-test-time-compute]
---

# Agent Trajectory Evals: Framework Evaluasi & Verifikasi Otonom

Sistem evaluasi trajektori agen AI untuk mengukur performa penalaran multi-langkah (*multi-turn trajectory*), estimasi metrik probabilitas keberhasilan $Pass@k$ tanpa bias observasi, pemotongan cabang halusinasi (*trajectory pruning*), dan verifikasi deterministik hasil akhir (*outcome-based verification*).

## When to Use
- Mengukur akurasi dan reliabilitas trajektori penalaran agentik pada alur multi-langkah.
- Menghitung $Pass@1$ dan $Pass@k$ secara matematis tanpa menjalankan kombinatorik penuh.
- Melakukan diagnosis *step-level error attribution* (mendeteksi titik kegagalan pertama / first point of failure).
- Mengintegrasikan validator deterministik sebelum kompilasi atau rilis hasil kerja otonom.

## Prerequisites
- Python 3.10+ (stdlib `math`, `json`, `dataclasses`).
- Lingkungan eksekusi terisolasi untuk mereproduksi trajektori uji.

## Quick Reference
- Jalankan evaluator trajektori lokal:
  `terminal(command="python3 ~/.hermes/skills/autonomous-ai-agents/agent-trajectory-evals/scripts/eval_harness.py --trajectory <path_to_trajectory.json>")`
- Hitung estimasi Pass@k unbiased:
  `terminal(command="python3 ~/.hermes/skills/autonomous-ai-agents/agent-trajectory-evals/scripts/pass_k_calc.py -n 10 -c 7 -k 1,3,5")`

## Procedure

1. Ekstraksi Trajektori Agentik
   Ekstraksi rangkaian interaksi agent menjadi representasi state-action linier:
   $T = (s_0, a_0, o_0, s_1, a_1, o_1, \dots, s_T, a_T, o_T)$.
   Pastikan setiap node aksi mencatat durasi, nama tool, argumen JSON, dan status keluar.

2. Estimasi Unbiased Metric $Pass@k$
   Gunakan estimator tak bias Chen et al. (HumanEval) untuk menghitung probabilitas setidaknya 1 dari $k$ sampel lolos evaluasi ketika mengevaluasi $n$ sampel ($n \ge k$) dengan $c$ sampel sukses:
   $$Pass@k = \mathbb{E}\left[ 1 - rac{inom{n - c}{k}}{inom{n}{k}} ight] = 1 - rac{\prod_{i=0}^{k-1} (n - c - i)}{\prod_{i=0}^{k-1} (n - i)}$$
   Pencegahan overflow: Evaluasi perkalian rasio fraksional secara iteratif untuk menghindari penghitungan faktorial raksasa.

3. Atribusi Galat Tingkat Langkah (Step-Level Error Attribution)
   Identifikasi titik divergensi pertama ($t^* = \min \{t \mid 
eg 	ext{Valid}(s_t, a_t)\}$):
   - Type I: Kesalahan sintaksis argumen tool (Format Invariant Violation).
   - Type II: Premis halusinasi (Unbacked Grounding).
   - Type III: Dead-end action loop (Pengulangan tindakan tanpa perubahan state).

4. Verifikasi Deterministik Akhir (Outcome-Based Verification)
   Terapkan verifikator independen non-LLM (unit test, status HTTP, hash integritas) untuk memisahkan evaluasi proses dari evaluasi hasil akhir.

## Pitfalls
- Menghitung $Pass@k$ dengan formula naif $rac{c}{n}$ pada $k > 1$ memicu bias parah pada estimasi reliabilitas.
- Mengevaluasi keberhasilan hanya dari status teks agen ("Tugas selesai") tanpa verifikasi status artefak disk/eksekusi.
- Mengabaikan akumulasi latensi dan biaya token saat menaikkan ukuran sampel $k$.

## Verification
- Validasi script $Pass@k$ dengan uji batas matematis: saat $c = 0$, $Pass@k = 0$; saat $c = n$, $Pass@k = 1.0$.
- Verifikasi parsing trajektori JSON valid terhadap skema standar agent trajectory.
