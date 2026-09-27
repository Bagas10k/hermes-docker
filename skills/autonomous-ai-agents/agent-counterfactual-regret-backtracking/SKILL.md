---
name: agent-counterfactual-regret-backtracking
description: Minimize agent regret and backtrack invariant violations.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [autonomous-agents, cfr, counterfactual-regret, state-backtracking, invariant-verification]
    related_skills: [agent-dag-task-splicing, agent-runtime-causal-discovery, agent-intervention-dag-splicing]
---

# Agent Counterfactual Regret Minimization & Invariant State Backtracking

Skill ini menyediakan kerangka kerja deterministik Counterfactual Regret Minimization (CFR) dan backtracking kondisi invarian (Invariant State Backtracking) untuk agen otonom.

## When to Use
- Mengoptimalkan alur pengambilan keputusan agen secara adaptif tanpa retraining model (regret-matching).
- Menangani pelanggaran invarian kritis sistem (RAM overflow >9.0GB, fatal error flag, pembobolan isolasi) dengan rollback ke snapshot aman terdekat $S_k$.
- Menghitung counterfactual difference utility untuk memangkas aksi sub-optimal berulang.

## Prerequisites
- Python 3.10+ (stdlib murni: copy, json, typing, unittest).
- Memori snapshot state terisolasi dalam batas memori RAM server.

## Quick Reference
```python
from cfr_engine import CFRBacktrackingEngine

engine = CFRBacktrackingEngine()
# Simpan checkpoint aman
engine.save_checkpoint(step_idx=1, state_data={"files": ["app.py"], "ram_usage_mb": 1200})

# Update penyesalan counterfactual
engine.update_regret(
    info_set="TOOL_CALL",
    action_taken="BASH_SUBPROCESS",
    actions=["BASH_SUBPROCESS", "DELEGATE_WORKER"],
    factual_utility=0.2,
    counterfactual_utilities={"BASH_SUBPROCESS": 0.2, "DELEGATE_WORKER": 1.0}
)

# Rollback otomatis saat invarian terlanggar
safe_snap, step = engine.trigger_backtrack(current_step=3, corrupted_state={"fatal_error": True})
```

## Procedure
1. Simpan State Snapshot sebelum eksekusi aksi berisiko efek-samping.
2. Evaluasi Invarian Hard Constraint $g(S) \le 0$ setelah mutasi sistem.
3. Jika invarian terlanggar, panggil `trigger_backtrack` untuk merestorasi snapshot $S_k$.
4. Perbarui matriks penyesalan kumulatif $R(I, a) \gets R(I, a) + (u(a) - u(a^*))$.
5. Konvergensikan kebijakan rata-rata (*average strategy*) via Regret-Matching.

## Pitfalls
- Membiarkan snapshot tak terbatas tanpa pruning dapat memicu kebocoran memori.
- Melakukan backtracking tanpa alasan pelanggaran invarian yang valid akan membatalkan progres sah (*premature abort*).

## Verification
Jalankan unit test suite mandiri:
`python3 scripts/test_cfr_engine.py` (4 unit test lolos 100% dalam sub-milidetik).
