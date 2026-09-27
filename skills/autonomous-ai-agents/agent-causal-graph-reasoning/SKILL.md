---
name: agent-causal-graph-reasoning
description: Causal graph reasoning and Bayesian intervention for agents.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [causal-inference, bayesian, do-calculus, root-cause, agent-reasoning]
    related_skills: [mathematical-problem-solving, agent-test-time-compute, multiagent-consensus-circuit-breaker]
---

# Agent Causal Graph Reasoning & Bayesian Interventions

Skill ini mengoperasionalkan penalaran graf kausal terstruktur (*Causal Directed Acyclic Graph / DAG*) dan inferensi Bayesian untuk agen otonom. Digunakan saat mendiagnosis kegagalan sistem multi-faktor, memisahkan observasi dari intervensi interaktif (*Pearl's do-calculus*), serta menghitung efisiensi diagnostik melalui *Value of Information* (VOI).

## When to Use
- Mendiagnosis bug kompleks atau anomali sistem yang melibatkan multi-faktor dependensi.
- Membedakan korelasi observasional $P(Y \mid X=x)$ dari manipulasi intervensi kausal $P(Y \mid do(X=x))$.
- Menghitung Value of Information (VOI) sebelum mengeksekusi probe diagnostik yang memakan token atau waktu I/O.
- Mengeliminasi dugaan kebetulan dan hipotesis semu melalui pengujian negatif berbasis bukti empiris.

Don't use for:
- Masalah mekanis sederhana 1-langkah tanpa ambiguitas (gunakan langsung tool terkait).
- Pengurutan murni penjadwalan DAG tanpa ketidakpastian kausal (gunakan `agent-dag-task-splicing`).

## Prerequisites
- Python 3.10+ (stdlib `json`, `math`, `copy`).
- Script engine kausal di `/home/ubuntu/otak-koding/AUTOPILOT/scripts/causal_reasoning_engine.py`.

## Quick Reference
```bash
# Inisialisasi graf kausal dan evaluasi hipotesis
python3 /home/ubuntu/otak-koding/AUTOPILOT/scripts/causal_reasoning_engine.py

# Perhitungan VOI pada probe diagnostik
python3 -c "
from causal_reasoning_engine import CausalGraphReasoningEngine
eng = CausalGraphReasoningEngine()
eng.add_hypothesis('H1', 'Token context overflow', prior=0.4)
print(eng.calculate_voi('H1', probe_cost_tokens=300, baseline_action_utility=0.5, candidate_action_utility=0.85))
"
```

## Procedure

1. **Definisikan Graf Hipotesis Awal (Prior & Nodes)**
   - Buat node untuk setiap hipotesis kandidat dengan probabilitas prior $P(H) \in (0.0, 1.0)$.
   - Hubungkan node penyebab ke node akibat via directed edge; pastikan topologi adalah DAG tanpa siklus.

2. **Hitung Value of Information (VOI) Sebelum Probe**
   - Terapkan rumus net VOI: $\text{VOI}_{\text{net}} = \mathbb{E}[\text{Utility baru}] - \text{Utility baseline} - \text{Biaya token/waktu}$.
   - Jalankan probe diagnostik HANYA jika $\text{VOI}_{\text{net}} > 0.05$ dan $0.20 \le P(H) \le 0.80$. Jika keyakinan sudah sangat tinggi atau sangat rendah, lewati probe.

3. **Kumpulkan Bukti & Perbarui Keyakinan Secara Bayesian**
   - Evaluasi likelihood bukti terhadap hipotesis: $P(E \mid H)$ dan $P(E \mid \neg H)$.
   - Perbarui probabilitas posterior:
     $$P(H \mid E) = \frac{P(E \mid H) P(H)}{P(E \mid H)P(H) + P(E \mid \neg H)P(\neg H)}$$
   - Beri bobot seimbang pada tes negatif: kegagalan observasi menggugurkan hipotesis palsu secara deterministik.

4. **Terapkan Intervensi Kausal (Pearl's do-calculus)**
   - Saat memvalidasi perbaikan sistem, bedakan observasi pasif dari tindakan intervensi aktif $do(X = x)$.
   - Lakukan *graph surgery*: putus seluruh garis ketergantungan masuk (incoming edges/parents) dari node target, lalu tetapkan nilai deterministik.
   - Amati apakah respons sistem $Y$ berubah secara nyata. Jika $Y$ tidak berubah setelah $do(X = x)$, variabel $X$ bukan akar penyebab kausal.

5. **Dokumentasikan Rantai Kausal & Keputusan**
   - Catat graf final, histori bukti, dan intervensi yang berhasil ke laporan tugas atau vault Obsidian.

## Pitfalls
- **Confounding Variable Trap**: Mengasumsikan $X$ menyebabkan $Y$ hanya karena keduanya terjadi bersamaan, padahal keduanya dipicu oleh variabel ketiga $Z$ (misal: beban trafik tinggi memicu lonjakan memori dan latensi DB secara simultan).
- **Zero-Likelihood Collapse**: Memberikan $P(E \mid H) = 0$ atau $1.0$ secara mutlak sehingga posterior membeku dan tidak dapat diperbarui lagi oleh bukti baru (selalu gunakan Laplace smoothing / bound 0.0001 - 0.9999).
- **Unbounded Diagnostic Probes**: Menjalankan puluhan probe diagnostik acak tanpa menghitung VOI, memboroskan token dan konteks LLM.

## Verification
- Validasi topologi DAG: deteksi siklus melempar exception saat edge melingkar ditambahkan.
- Bukti empiris memperbarui posterior secara konsisten dengan hukum probabilitas Bayes.
- Intervensi graf memutus incoming edge dan mengisolasi efek kausal secara terverifikasi.
