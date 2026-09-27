---
name: dynamic-temperature-decay-critic-guardrail
description: Use when bounding cognitive loops with decay and critic.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cognitive-reasoning, temperature-decay, critic-guardrail, circuit-breaker, anti-thrashing]
---

# Dynamic Temperature Decay & Dual-Phase Critic Guardrail

Pola rekayasa kognitif untuk membatasi alur penalaran ReAct pada agen otonom agar tidak terjebak thrashing loop atau halusinasi acak, serta memvalidasi aksi dan respons akhir secara deterministik.

## 1. Rumus Dynamic Temperature Decay
Gunakan penurunan eksponensial suhu LLM berdasarkan langkah eksekusi:
$$T_{\text{step}} = \max\left(T_{\text{min}},\, T_{\text{base}} \times \gamma^{\text{step}}\right)$$
- $T_{\text{base}} = 0.70$ (fleksibel di awal eksplorasi)
- $\gamma = 0.85$ (laju pembekuan / crystallization rate)
- $T_{\text{min}} = 0.10$ (deterministik mutlak di langkah konklusi)

## 2. Dual-Phase Critic Guardrail
1. **Pre-Execution Action Audit**:
   - Cegah input parameter kosong pada pemanggilan tool fungsional.
   - Deteksi pola instruksi destruktif (`rm -rf`, `mkfs`, dropping DB).
   - Evaluasi skor kelayakan (0-100), tolak aksi jika terdapat temuan `CRITICAL`.
2. **Post-Execution Output Audit**:
   - Tolak output kosong atau di bawah panjang batas minimum.
   - Filter kebocoran pola kredensial sensitif (`sk-`, `ghp_`, `bearer`, `token=`).

## 3. Circuit Breaker Invariant
- Hentikan loop bila:
  - Jumlah langkah melebihi `max_steps`.
  - Durasi eksekusi melebihi `timeout_seconds`.
  - Konsumsi token melebihi `token_budget`.
  - Fingerprint hash snippet output terdeteksi identik 3 kali berturut-turut (*thrashing*).
