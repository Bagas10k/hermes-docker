---
name: multiagent-consensus-circuit-breaker
description: Use when bounding multi-agent consensus and failure loops.
version: 0.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [multi-agent, consensus, circuit-breaker, hallucination-defense, orchestration]
    related_skills: [autonomous-orchestrator, agent-hierarchical-memory]
---

# Multi-Agent Consensus, Subagent Delegation & Cascade Hallucination Circuit Breaker

Arsitektur orkestrasi multi-agen tangguh untuk mendeteksi divergensi semantik (*cascade hallucination*), menjalankan konsensus voting terbobot bukti empiris, membatasi siklus hidup subagen terisolasi, dan memutus putaran tanpa henti (*anti-doom loop circuit breaker*).

## When to Use
- Mengoordinasikan delegasi tugas ke beberapa subagen (`delegate_task`) tanpa risiko halusinasi berantai.
- Memvalidasi keputusan bercabang arsitektural menggunakan voting konsensus multi-agen (Si Pintar, Si Eksekutor, Si Pengawas).
- Memutus loop kesalahan berulang saat subagen terjebak pada kegagalan eksekusi tool yang sama.
- Memeriksa apakah klaim atau kesimpulan subagen anak berpijak pada fakta terverifikasi milik agen induk (*grounding invariant*).

Don't use for:
- Tugas sekuensial sederhana yang dapat diselesaikan oleh satu agen tunggal dalam satu kali giliran.
- Koordinasi obrolan teks sandiwara fiktif tanpa komando kerja nyata.

## Prerequisites
- Python 3.11+ standard library (`math`, `dataclasses`, `enum`, `json`, `hashlib`).
- Modul internal:
  - `scripts/multiagent_consensus_circuit_breaker.py` (BFT bounds & entropy stall breaker)
  - `scripts/consensus_breaker_engine.py` (Subagent envelope & cascade taint detector)

## How to Run
Jalankan uji validasi invariansi multi-agen dan circuit breaker:
`terminal(command="python3 -m unittest -v test_multiagent_consensus_circuit_breaker", workdir="~/.hermes/skills/autonomous-ai-agents/multiagent-consensus-circuit-breaker/scripts")`
`terminal(command="python3 ~/.hermes/skills/autonomous-ai-agents/multiagent-consensus-circuit-breaker/scripts/consensus_breaker_engine.py")`

## Quick Reference
- Inisialisasi Selubung Tugas Terisolasi: `env = DelegationEnvelope(task_id, sender, receiver, objective, constraints, max_turns=5)`
- Rekam dan Batasi Giliran: `is_allowed = env.record_turn(action_signature)`
- Evaluasi Loop Circuit Breaker: `breaker.check_loop_circuit(action_signature)`
- Hitung Konsensus Terbobot: `result = breaker.calculate_consensus(agent_opinions)`
- Deteksi Halusinasi Kaskade: `has_drift = breaker.detect_cascade_hallucination(parent_facts, child_inferences)`

## Procedure
1. **Bungkus Tugas dalam Selubung Terisolasi (Envelope)**:
   - Buat `DelegationEnvelope` yang membatasi peran, tujuan eksplisit, batasan (*read-only* / *safe*), dan kuota giliran maksimal (`max_turns`).
2. **Evaluasi Loop Sebelum Pemanggilan Tool**:
   - Uji tanda tangan aksi (*action signature*) ke `check_loop_circuit`. Jika pola aksi identik berulang melebihi ambang batas (`loop_threshold`), picu circuit breaker dan hentikan eksekusi otomatis.
3. **Karantina Halusinasi Kaskade (Taint Checking)**:
   - Bandingkan output kesimpulan subagen anak dengan kumpulan fakta awal agen induk via `detect_cascade_hallucination`. Jika rasio rujukan fakta di bawah ambang batas (misal $< 0.50$), tolak kesimpulan tersebut sebagai halusinasi kaskade.
4. **Voting Konsensus Terbobot**:
   - Jika keputusan krusial memerlukan kesepakatan multi-agen, kumpulkan opini beserta skor keyakinan dan status verifikasi empiris (`is_verified`).
   - Eksekusi `calculate_consensus`: bobot agen dengan bukti nyata dinaikkan $1.5\times$.
5. **Eskalasi ke Operator**:
   - Jika status konsensus mendeteksi kebuntuan (`DEADLOCK_OR_AMBIGUITY`) atau margin tipis ($< 0.15$), tahan tindakan otomatis dan formulasikan pertanyaan pilihan ganda terstruktur ke Mas Bagas.

## Pitfalls
- **Heuristic Is Not Proof**: Grounding ratios, confidence weighting, and `is_verified` flags are triage heuristics, not hallucination detectors or Bayesian posteriors. Verify claim-specific evidence independently; lexical overlap can preserve falsehoods and novelty can be correct. HTTP 200 and exit code zero alone do not prove task success.
- **Agreement Is Not Truth**: A unanimous set can share a false premise. For Byzantine claims, use fixed authenticated membership, explicit fault-weight bounds, quorum intersection, and durable sign-once/lock rules; never derive safety voting weights from self-reported confidence. See `byzantine-multiagent-debate` for finite audits and limitations.
- **Unbounded Delegation Recursion**: Agen anak memanggil subagen cucu tanpa batas kedalaman, menghabiskan kuota token dan memicu ledakan proses. Kunci kedalaman delegasi maksimal pada level 1.
- **Equal Weight Voting on Unverified Claims**: Menyamakan bobot klaim spekulatif dengan temuan yang teruji `exit_code == 0` memicu *groupthink* salah arah. Selalu prioritaskan bukti empiris nyata.
- **Silent Exception Swallowing in Workers**: Subagen menelan galat dan mengembalikan status sukses palsu. Wajib lakukan verifikasi berkas atau output proses secara independen.

## Verification
- Jalankan modul `scripts/consensus_breaker_engine.py`.
- Pastikan keempat invariansi lolos: Turn bound envelope, Anti-doom loop, Weighted consensus & deadlock detection, dan Cascade hallucination quarantine.
