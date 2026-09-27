---
name: agent-speculative-execution
description: Speculative tool execution with two-phase verification.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [speculative-execution, two-phase-commit, latency-reduction, rollback-barrier, tool-sandboxing]
    related_skills: [agent-ephemeral-sandboxing, agent-test-time-compute, multiagent-consensus-circuit-breaker]
---

# Agent Speculative Tool Execution & Pre-Commit Verification

Skill operasional untuk menjalankan eksekusi spekulatif (*speculative tool execution*) pada alur kerja agen otonom: memangkas latensi putaran LLM melalui prediksi paralel (*speculative branching*), isolasi efek samping via *copy-on-write scratchpad*, verifikasi dua fase (*two-phase commit*), dan proteksi pembatalan tanpa kebocoran (*zero-leak rollback barrier*).

## When to Use

- Mengurangi latensi kumulatif agen saat memproses rantai tool yang memiliki ketergantungan baca-tulis parsial.
- Melakukan pra-eksekusi (*pre-fetching*) pada operasi read-only atau analisis kode saat LLM masih dalam proses streaming token.
- Menguji mutasi berkas atau eksekusi sistem berbahaya dalam sandbox bayangan sebelum dikomit ke lingkungan kerja utama.
- Mencegah inkonsistensi status sistem saat LLM membatalkan rencana atau menghasilkan respon divergen di tengah jalan.

### Don't use for:

- Operasi eksternal ireversibel (seperti memublikasikan post media sosial, transfer dana, menghapus basis data produksi tanpa replika, atau mengirimkan email).
- Perintah interaktif yang memerlukan masukan manusia secara langsung (*human-in-the-loop prompt*).

## Prerequisites

- Python 3.10+ dengan modul standar (`json`, `os`, `sys`, `pathlib`, `shutil`, `hashlib`, `time`).
- Engine verifikator spekulatif lokal: `python3 ~/.hermes/skills/autonomous-ai-agents/agent-speculative-execution/scripts/speculative_engine.py`.

## Quick Reference

```bash
# Menjalankan evaluasi spekulasi terhadap rencana eksekusi tool
python3 ~/.hermes/skills/autonomous-ai-agents/agent-speculative-execution/scripts/speculative_engine.py --eval-plan plan.json

# Memeriksa batas Amdahl speedup berdasarkan fraksi paralel
python3 ~/.hermes/skills/autonomous-ai-agents/agent-speculative-execution/scripts/speculative_engine.py --amdahl --p 0.70 --speedup 3.5

# Menjalankan dry-run terisolasi dengan verifikasi two-phase commit
python3 ~/.hermes/skills/autonomous-ai-agents/agent-speculative-execution/scripts/speculative_engine.py --sandbox-run --action "patch" --target "/path/file"
```

## Procedure

### 1. Klasifikasi Tingkat Efek Samping (Side-Effect Tiering)
- Petakan setiap tool yang akan dipanggil ke dalam 3 tier keselamatan:
  - **Tier 0 (Pure Read / Epistemic):** `read_file`, `search_files`, `web_search`. Dapat dieksekusi secara instan dan bebas spekulasi paralel.
  - **Tier 1 (Idempotent Local Mutation):** `write_file`, `patch` pada file kerja lokal. Wajib diarahkan ke direktori bayangan *copy-on-write* (CoW scratchpad).
  - **Tier 2 (Irreversible External Action):** `git push`, API eksternal, penghapusan permanen. Haram dispekulasikan; wajib menunggu konfirmasi final atau token non-spekulatif.
- Kriteria penyelesaian: Seluruh pemanggilan tool memiliki label tier eksplisit.

### 2. Formulasi Batas Kecepatan Amdahl (Theoretical Bound Check)
- Evaluasi percepatan sistem teoritis dengan Hukum Amdahl:
  $$S_{\text{latency}} = \frac{1}{(1 - p) + \frac{p}{s}}$$
  di mana $p$ adalah fraksi tool yang dapat dispekulasikan paralel dan $s$ adalah faktor percepatan eksekusi konkuren.
- Hitung risiko pembatalan spekulatif: Jika probabilitas keberhasilan spekulasi $P(\text{accept}) < 0.60$, hentikan spekulasi untuk menghemat beban CPU/RAM.
- Kriteria penyelesaian: Estimasi VOI (*Value of Information*) dan efisiensi waktu bernilai positif.

### 3. Isolasi Percabangan Spekulatif (Shadow Workspace Branching)
- Buat ruang kerja bayangan sementara di memori atau direktori ephemeral (`/tmp/hermes_spec_<uuid>`).
- Duplikasi hanya berkas target (*sparse copy-on-write*), jangan menyalin seluruh repositori untuk menghemat I/O disk.
- Jalankan aksi spekulatif di dalam scratchpad dan catat hash perubahan (*pre-commit delta receipt*).
- Kriteria penyelesaian: Aksi berhasil dieksekusi dalam isolasi tanpa mencemari workspace produksi.

### 4. Verifikasi Dua Fase (Two-Phase Commit Barrier)
- **Fase 1 (Prepare / Validate):** Periksa apakah output final LLM cocok dengan asumsi spekulatif ($P(\text{match}) = 1.0$) dan uji sintaks/integritas artefak di scratchpad.
- **Fase 2 (Commit or Abort):**
  - Jika **MATCH & VALID**: Lakukan perpindahan atomik (*atomic rename / fast-forward copy*) dari scratchpad ke workspace kerja utama.
  - Jika **MISMATCH / ERROR**: Picu *Abort*, hapus scratchpad tanpa jejak, dan kembalikan state awal ke agen (*zero-leak rollback*).
- Kriteria penyelesaian: Mutasi terjadi secara atomik atau dibatalkan 100% tanpa residu.

## Pitfalls

1. **Speculative Leakage on External Sinks:** Menjalankan perintah jaringan atau webhook publik di dalam cabang spekulatif yang berujung pada pengiriman duplikat atau spam saat rantai spekulasi dibatalkan.
2. **CoW Scratchpad Bloat:** Menyalin direktori `node_modules` atau data biner besar ke dalam scratchpad spekulatif yang menghabiskan memori dan membalikkan keuntungan kecepatan menjadi kelambatan I/O disk.
3. **Dirty Read Concurrency:** Sub-agent membaca file yang sedang dimodifikasi secara spekulatif oleh worker lain sebelum fase commit selesai, menghasilkan status *phantom read*.

## Verification

Jalankan rangkaian tes mandiri engine spekulasi:

```bash
python3 ~/.hermes/skills/autonomous-ai-agents/agent-speculative-execution/scripts/speculative_engine.py --test-all
```

Verifikasi wajib membuktikan:
1. Amdahl latency gain terhitung presisi.
2. Tier-0 dieksekusi langsung, Tier-1 diisolasi ke scratchpad, dan Tier-2 dicegat barrier.
3. Rollback pada kondisi galat terbukti membuang scratchpad tanpa merusak file acuan.
4. Two-phase commit terbukti mentransfer hasil mutasi secara atomik saat divalidasi.
