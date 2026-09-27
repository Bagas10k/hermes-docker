---
name: agent-runtime-causal-discovery
description: Runtime causal graph discovery and do-calculus bounds.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [causal-inference, do-calculus, dag-discovery, scm, agent-reasoning]
    related_skills: [agent-causal-graph-reasoning, agent-dag-task-splicing, mathematical-problem-solving]
---

# Agent Runtime Causal Graph Discovery & Do-Calculus Bounds

Skill ini mengoperasionalkan penemuan graf kausal waktu-nyata (*Runtime Causal Graph Discovery*) dan batasan manipulasi intervensi Pearl (*Do-Calculus Bounds*) pada loop eksekusi agen otonom. Dirancang untuk memecahkan ilusi korelasi vs kausalitas, mengisolasi akar penyebab dalam rantai eksekusi tugas, dan memilih intervensi aktif beranggaran optimal (*Value of Information*).

## When to Use
- Mendiagnosis ketergantungan antar-tugas atau anomali sistem di mana korelasi observasional $P(Y \mid X)$ mengaburkan hubungan kausal nyata $P(Y \mid do(X))$.
- Menentukan intervensi pengujian optimal di bawah anggaran kuota eksekusi/token terbatas.
- Menguji hipotesis mekanisme sistem melalui pemutusan garis masuk (*graph surgery / parent severance*).
- Menjalankan verifikasi konsistensi invarian (*Consistency Verification Gate*) sebelum menghentikan proses diagnostik agar terhindar dari *premature stopping*.

Don't use for:
- Penjadwalan murni task DAG tanpa ketidakpastian kausal (gunakan `agent-dag-task-splicing`).
- Kalibrasi probabilitas generik tanpa manipulasi graf (gunakan `agent-bayesian-belief-calibration`).

## Prerequisites
- Python 3.10+ (stdlib `math`, `json`, `copy`, `typing`).
- Engine penemu kausal: `~/.hermes/skills/autonomous-ai-agents/agent-runtime-causal-discovery/scripts/causal_discovery_engine.py`.

## Quick Reference
```bash
# Jalankan unit test engine kausal
python3 ~/.hermes/skills/autonomous-ai-agents/agent-runtime-causal-discovery/scripts/test_causal_discovery.py

# Inisialisasi engine dan uji do-calculus CLI
python3 -c "
import sys; sys.path.insert(0, '/home/ubuntu/.hermes/skills/autonomous-ai-agents/agent-runtime-causal-discovery/scripts')
from causal_discovery_engine import CausalDiscoveryEngine, StructuralEquation
eng = CausalDiscoveryEngine(intervention_budget=5)
eng.add_edge('A', 'B')
print(eng.summary())
"
```

## Procedure

1. **Inisialisasi Ruang Variabel & Observasi Pasif**
   - Daftarkan variabel sistem dan masukkan metrik observasi pasif baris demi baris via `ingest_observation(data_row)`.
   - Hitung matriks korelasi otomatis untuk memetakan keterkaitan awal antar-komponen.

2. **Pemangkasan Tepi Palsu (Constraint-Based Pruning)**
   - Pangkas garis ketergantungan yang memiliki koefisien korelasi di bawah ambang batas ($\tau_{\text{corr}} < 0.25$) menggunakan `prune_spurious_edges()`.
   - Pastikan setiap penambahan tepi mematuhi invarian DAG murni (nol siklus rekursif).

3. **Kalkulasi Net Value of Information (VOI)**
   - Sebelum mengeksekusi intervensi yang memakan kuota komputasi atau kuota intervensi, evaluasi skor VOI kandidat via `calculate_experiment_voi(candidate, target)`.
   - Prioritaskan intervensi pada node yang memiliki ambiguitas arah kausal tertinggi dengan biaya kuota terkecil.

4. **Eksekusi Intervensi Kausal (Pearl's Do-Calculus Surgery)**
   - Jalankan `hard_do_intervention(target, value, scm)` untuk memutus seluruh dependensi masuk (*incoming parents*) dan memvalidasi respons turunan hilir secara terisolasi.
   - Gunakan `soft_shift_intervention(target, delta, scm)` jika sistem mensyaratkan pergeseran parameter dasar tanpa mematikan pipa hulu.

5. **Gerbang Verifikasi Konsistensi (Consistency Verification Gate)**
   - Sebelum menyimpulkan mekanisme kausal akhir, jalankan `verify_consistency(target, scm, tolerance)`.
   - Tolak penyelesaian prematur (*premature stopping*) jika formulasi persamaan struktural gagal merekonstruksi data riwayat observasi dan intervensi sebelumnya.

## Pitfalls
- **Premature Commitment & Early Stopping**: Menghentikan eksplorasi saat menemukan satu korelasi kuat tanpa memvalidasi konsistensi model terhadap data intervensi lampau.
- **Cycle Injection Trap**: Memaksa penambahan tepi kausal dua arah ($A \to B$ dan $B \to A$) yang melanggar invarian DAG asiklis.
- **Budget Burn Without VOI**: Menjalankan eksperimen intervensi secara acak tanpa menghitung nilai informasi bersih, menghabiskan kuota sebelum arah kausal utama terungkap.

## Verification
- Unit test suite `test_causal_discovery.py` wajib lolos 100% tanpa galat.
- Invarian pemutusan siklus DAG teruji melempar penolakan deterministik.
- Hasil hard-do memvalidasi isolasi variabel target dari pengaruh hulu.