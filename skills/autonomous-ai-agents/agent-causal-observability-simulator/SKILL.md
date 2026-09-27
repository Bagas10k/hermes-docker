---
name: agent-causal-observability-simulator
description: Simulate causal latency and resource intervention bounds.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [causal-inference, observability, latency-simulation, do-calculus, amdahl-bounds]
    related_skills: [agent-runtime-causal-discovery, agent-intervention-dag-splicing, agent-counterfactual-regret-backtracking]
---

# Agent Causal Observability & Latency/Resource Intervention Simulator

Skill ini menyediakan engine observabilitas berbasis Structural Causal Model (SCM), operator do-calculus Pearl, identifikasi jalur kritis (Critical Path Method), dan simulasi batas intervensi latensi/RAM untuk agen otonom.

## When to Use
- Mengidentifikasi Amdahl Bottleneck pada alur kerja DAG multi-agen.
- Mensimulasikan dampak intervensi latensi atau alokasi RAM $do(X=x)$ sebelum melakukan perubahan pada sistem produksi.
- Memverifikasi batas invarian keras sistem ($Peak RAM \le 9.0GB$, batas SLA latensi) pada skenario counterfactual.

## Prerequisites
- Python 3.10+ (stdlib murni: typing, copy, math, unittest).
- Modul internal di `scripts/causal_simulator_engine.py`.

## Quick Reference
```python
from causal_simulator_engine import CausalObservabilitySimulator

sim = CausalObservabilitySimulator(ram_limit_mb=9000.0, max_latency_ceiling_ms=15000.0)
sim.add_node("PLANNER", base_latency_ms=1200.0, base_ram_mb=500.0, base_cost_usd=0.002)
sim.add_node("EXECUTOR", base_latency_ms=2500.0, base_ram_mb=1200.0, base_cost_usd=0.004)
sim.add_causal_edge("PLANNER", "EXECUTOR")

# Hitung jalur kritis faktual
metrics = sim.compute_critical_path()
print("Jalur Kritis:", metrics["critical_path"], "Total Latensi:", metrics["total_latency_ms"])

# Simulasikan intervensi Pearl do(EXECUTOR latency = 1000ms)
cf_metrics = sim.simulate_do_intervention({"EXECUTOR": {"latency_ms": 1000.0}})
inv = sim.evaluate_invariant_bounds(cf_metrics)
print("Invarian Lolos:", inv["passed"])
```

## Procedure
1. **Modelkan DAG Alur Kerja Agen**:
   Daftarkan node eksekusi beserta baseline latensi, RAM, dan biayanya.
2. **Hitung Jalur Kritis (Critical Path)**:
   Gunakan kalkulasi Earliest Start (ES) dan Earliest Finish (EF) untuk mengekstrak kontribusi latensi tiap node $p_i = L_i / L_{\text{total}}$.
3. **Analisis Batas Teoretis Amdahl**:
   Tentukan apakah target optimasi memiliki kontribusi signifikan ($p_i \ge 0.35$). Abaikan optimasi mikro pada node dengan $p_i < 0.15$.
4. **Jalankan Simulasi Intervensi $do(X=x)$**:
   Uji skenario alternatif (misal: penggantian model LLM ke SLM, caching prompt KV, pemangkasan konkurensi).
5. **Verifikasi Kendala Keras Invarian**:
   Pastikan Peak RAM tidak melanggar kuota 9.0 GB dan latensi memenuhi target SLA.

## Pitfalls
- Mengoptimalkan node di luar jalur kritis tidak akan mengurangi total latensi sistem (Amdahl Invariant).
- Memotong latensi satu node dapat menggeser jalur kritis ke rantai paralel lainnya secara dinamis.
- Mengabaikan batas RAM konkurensi paralel dapat memicu OOM killer di sistem produksi.

## Verification
Jalankan unit test suite deterministik:
```bash
python3 ~/.hermes/skills/autonomous-ai-agents/agent-causal-observability-simulator/scripts/test_causal_simulator_engine.py
```
Seluruh 6 uji ketergantungan DAG, deteksi siklus, kalkulasi jalur kritis, dan intervensi Pearl wajib lulus 100%.
