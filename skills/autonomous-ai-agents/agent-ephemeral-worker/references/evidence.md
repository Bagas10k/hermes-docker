# Ephemeral Worker Architecture & Isolation Bounds

## 1. Mekanisme & Batasan Sistem
Model eksekusi sub-agent terisolasi:
$$T_{total} = T_{spawn} + T_{exec} + T_{dispose}$$
Dalam arsitektur konvensional (full VM / container launch), $T_{spawn} \approx 500\text{ms} - 3000\text{ms}$. Dengan micro-sandbox CoW / unshare tempfs lokal, $T_{spawn} < 15\text{ms}$.
Hukum Amdahl membatasi throughput paralel sub-agent jika overhead siklus hidup worker ($T_{spawn} + T_{dispose}$) melebihi durasi task $T_{exec}$.

## 2. Lensa Bayesian & Bukti Empiris
- Prior: Isolasi container Docker lengkap diasumsikan perlu untuk setiap tugas sub-agent kecil.
- Bukti Empiris: Untuk eksekusi script murni komputasi / read-only analysis / formatting, overhead Docker memboroskan RAM (~80-150MB per container) dan waktu cold-start.
- Update Keyakinan: Terapkan isolasi bertingkat: Ephemeral scratchpad sandboxing sub-detik untuk lightweight sub-agents, dan eskalasi ke microVM hanya untuk untrusted execution berisiko tinggi.

## 3. Desain Sistem & Invarian Kebocoran Nol (Zero-Leak)
- Sandboxed base directory dengan per-worker UUID.
- Path traversal prevention via relative-to check.
- Quota limiter berbasis memory & disk byte counter.
- Atomic cleanup via unconditional tree disposal pada exit.
