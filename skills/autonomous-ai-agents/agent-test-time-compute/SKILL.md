---
name: agent-test-time-compute
description: Agent test-time compute, search-over-action, and MCTS.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [test-time-compute, mcts, search-over-action, verification, prm, fallback]
    related_skills: [mathematical-problem-solving, autonomous-orchestrator]
---

# Agent Test-Time Compute & Search-Over-Action Verification

Skill operasional untuk mengorkestrasi komputasi waktu-uji (*test-time compute*), pencarian ruang aksi (*Search-over-Action*), pemeringkatan langkah via Process Reward Model (PRM), dan penghalang verifikasi mutasi sebelum mengeksekusi tool berisiko tinggi.

## When to Use

- Tugas agen otonom memerlukan rangkaian tindakan kritis (misal: migrasi database, patch refaktor multi-berkas, konfigurasi infrastruktur).
- Menghindari jebakan eksekusi serakah (*greedy execution trap*) di mana kegagalan langkah awal memicu loop halusinasi tak berujung.
- Membutuhkan eksplorasi paralel dari beberapa kandidat rencana aksi (Monte Carlo Tree Search / Beam Search over tool calls) dengan penilaian Process Reward Model (PRM).
- Memerlukan mekanisme verifikasi hipotesis bertahap dan *reflexive self-correction* ketika eksekusi probe awal mengembalikan hasil negatif.

### Don't use for:
- Perintah baca sederhana yang tidak memiliki efek samping mutatif (gunakan pemanggilan tool langsung).
- Alur kerja sekuensial deterministik yang sudah terbukti andal tanpa percabangan (misal: eksekusi script build terisolasi).

## Prerequisites

- Python 3.10+ dengan pustaka standar (`json`, `math`, `typing`, `dataclasses`).
- Akses terminal atau Hermes tool execution (`execute_code`, `read_file`, `write_file`, `terminal`).

## How to Run

Jalankan harness verifikasi dan simulasi pencarian aksi:

```bash
python3 ~/.hermes/skills/autonomous-ai-agents/agent-test-time-compute/scripts/test_time_search_engine.py --mode dry-run
```

Atau gunakan modul Python secara terprogram di dalam sub-agent:

```python
from test_time_search_engine import ActionNode, SearchOverActionEngine, ValueAssessment
```

## Quick Reference

- **MCTS UCT Formula**: $\text{UCT}(s, a) = Q(s, a) + c_{\text{puct}} \cdot P(s, a) \cdot \frac{\sqrt{\sum N(s, b)}}{1 + N(s, a)}$
- **Process Reward Threshold**: $\tau_{\text{prm}} \ge 0.75$ untuk cabang aksi aman, $\tau_{\text{prm}} < 0.40$ langsung dipangkas (*pruned*).
- **Amdahl Latency Bound**: Batasi kedalaman pencarian $d \le 4$ dan cabang $b \le 3$ untuk menjaga tail latency $p95 \le 2.5\text{s}$.
- **Side-Effect Barrier**: Dilarang mengeksekusi operasi stateful/mutatif pada fase simulasi; seluruh simulasi wajib memakai copy-on-write workspace atau mock probe.

## Procedure

1. **Dekomposisi Ruang Masalah & Penetapan Invarian**:
   Definisikan kendala keras $g_i(x) \le 0$ dan fungsi tujuan $J(x)$. Petakan state awal $s_0$ dan daftar tindakan potensial $A = \{a_1, a_2, \dots, a_k\}$.
   *Kriteria Selesai*: Daftar invarian keamanan dan kondisi keberhasilan terdefinisi secara eksplisit.

2. **Pembentukan Kandidat Trajectory (Search-over-Action)**:
   Bangun pohon pencarian aksi hingga kedalaman $d$. Evaluasi prior probability $P(s, a)$ dari LLM planner.
   *Kriteria Selesai*: Minimal 2 kandidat jalur tindakan terbentuk dalam pohon pencarian.

3. **Skoring Langkah Melalui Process Reward Model (PRM)**:
   Uji setiap simpul menggunakan probe verifikasi non-destruktif atau evaluasi deterministik. Hitung skor langkah $r_t \in [0, 1]$.
   *Kriteria Selesai*: Setiap simpul memiliki skor PRM terkalibrasi dan label keabsahan.

4. **Pemilihan Jalur Optimal (Selection & Backpropagation)**:
   Pilih simpul dengan metrik UCT tertinggi. Lakukan backpropagation nilai ekspektasi reward $Q$ ke simpul induk.
   *Kriteria Selesai*: Terpilih satu trajectory tindakan terbaik dengan skor kumulatif tertinggi.

5. **Eksekusi Terkendali & Reflexive Self-Correction**:
   Eksekusi aksi terpilih secara nyata. Jika hasil observasi tidak sesuai prediksi apriori ($P(E \mid H) \approx 0$), aktifkan pemicu rollback seketika dan pilih cabang terbaik kedua (*fallback branch*) tanpa mengulang dari awal.
   *Kriteria Selesai*: Seluruh aksi mutatif berhasil dieksekusi dan diverifikasi secara empiris.

## Pitfalls

- **Simulation Leakage**: Menjalankan perintah mutatif (seperti `rm`, `git commit`, mutasi database) saat mengevaluasi cabang simulasi. Wajib batasi simulasi hanya pada evaluasi kode/AST kering atau isolasi direktori sementara.
- **Over-Search / Token Budget Exhaustion**: Mengembangkan pohon pencarian terlalu lebar ($b > 5$) atau terlalu dalam ($d > 5$), menghabiskan kuota token dan memicu timeout. Terapkan pemangkasan dini (*early pruning*) saat skor PRM $< 0.4$.
- **Outcome Bias vs Step Verification**: Hanya menilai hasil akhir tanpa memvalidasi keabsahan langkah perantara, meloloskan kesalahan logika tersembunyi yang kebetulan menghasilkan output parsial benar.

## Verification

Buktikan keandalan engine test-time compute dengan menjalankan test suite terpadu:

```bash
python3 ~/.hermes/skills/autonomous-ai-agents/agent-test-time-compute/scripts/test_time_search_engine.py --verify-invariants
```

Verifikasi wajib membuktikan:
1. Pemangkasan cabang berbahaya secara deterministik sebelum eksekusi mutatif.
2. Skor UCT memprioritaskan jalur dengan probabilitas verifikasi tertinggi.
3. Transisi fallback otomatis saat simpul primer sengaja disimulasikan gagal.