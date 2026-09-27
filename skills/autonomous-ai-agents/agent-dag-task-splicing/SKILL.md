---
name: agent-dag-task-splicing
description: DAG task splicing and dynamic topological replanning.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [dag, task-splicing, topological-sort, replanning, amdahl-concurrency, workflow-orchestration]
    related_skills: [multiagent-consensus-circuit-breaker, agent-speculative-execution, agent-trajectory-evals]
---

# Agent DAG Task Splicing & Dynamic Topological Replanning

Skill operasional untuk mengelola eksekusi alur kerja Directed Acyclic Graph (DAG) pada agen otonom: topological sorting deterministik, penyisipan node dinamis (*in-flight task splicing*), pelacakan kerucut kausal (*causal cone dependency tracking*), isolasi cabang gagal (*failure pruning*), dan optimasi konkurensi berbasis batas Amdahl.

## When to Use

- Mengorkestrasi tugas multi-langkah atau pendelegasian sub-agen paralel yang memiliki dependensi data terarah.
- Menyisipkan langkah validasi, pra-pemeriksaan AST, atau sanitasi keamanan secara dinamis sebelum alat berbahaya dijalankan (*in-flight splicing*).
- Menghitung jalur kritis (*critical path*) dan mengoptimasi konkurensi eksekusi independen secara serentak.
- Mengisolasi kegagalan satu sub-tugas agar tidak melumpuhkan seluruh rencana (*causal cone failure pruning*).

### Don't use for:

- Percakapan santai satu putaran tanpa dependensi tugas bertahap.
- Alur kerja yang membutuhkan siklus loop tak terbatas (*infinite polling loops* tanpa kondisi terminasi asiklik).

## Prerequisites

- Python 3.10+ dengan modul standar (`json`, `collections`, `argparse`, `typing`).
- Engine DAG terpasang di: `~/.hermes/skills/autonomous-ai-agents/agent-dag-task-splicing/scripts/dag_replanning_engine.py`.

## Quick Reference

```bash
# Menjalankan demonstrasi lengkap alur DAG dan kalkulasi Amdahl
python3 ~/.hermes/skills/autonomous-ai-agents/agent-dag-task-splicing/scripts/dag_replanning_engine.py --demo

# Mengevaluasi metrik latensi jalur kritis dan percepatan teoritis
python3 ~/.hermes/skills/autonomous-ai-agents/agent-dag-task-splicing/scripts/dag_replanning_engine.py --metrics

# Menghitung layer eksekusi paralel (Sugiyama layering)
python3 ~/.hermes/skills/autonomous-ai-agents/agent-dag-task-splicing/scripts/dag_replanning_engine.py --layers

# Menyimulasikan pemangkasan kerucut kausal saat node mengalami kegagalan
python3 ~/.hermes/skills/autonomous-ai-agents/agent-dag-task-splicing/scripts/dag_replanning_engine.py --prune-failed worker_test
```

## Procedure

### 1. Pemodelan Graf Dependensi Kausal (DAG Invariant Modeling)
- Modelkan rencana kerja agen sebagai himpunan node $V$ dan sisi berarah $E$.
- Pastikan invariansi asiklik terpenuhi ($\text{CycleCheck}(G) = \text{False}$). Dilarang membiarkan dependensi sirkular yang memicu deadlock.
- Kriteria penyelesaian: Seluruh tugas terdaftar dengan durasi estimasi dan edge dependensi hulu-hilir yang valid.

### 2. Penjadwalan Konkurensi & Sugiyama Layering
- Hitung derajat masuk ($\text{in-degree}$) untuk setiap node.
- Kelompokkan node dengan $\text{in-degree} = 0$ ke dalam satu layer eksekusi serentak.
- Hitung durasi jalur kritis ($T_{\text{critical}}$) dan bandingkan dengan total serial ($T_{\text{serial}}$) untuk mengidentifikasi bottleneck utama.
- Kriteria penyelesaian: Node independen terdistribusi ke dalam layer paralel tanpa tabrakan identitas.

### 3. Dynamic Task Splicing (Penyisipan Node In-Flight)
- Saat eksekusi mendeteksi kebutuhan langkah pencegahan baru (misal: sanitasi sebelum `patch`):
  1. Buat node baru $v_{\text{new}}$ dengan status `pending`.
  2. Alihkan seluruh relasi pendahulu dari $v_{\text{target}}$ ke $v_{\text{new}}$.
  3. Hubungkan $v_{\text{new}} \to v_{\text{target}}$.
  4. Lakukan validasi ulang topological sort untuk memastikan tidak ada siklus baru.
- Kriteria penyelesaian: Node berhasil disisipkan dan urutan eksekusi terbarui secara mulus tanpa mengulang tugas yang sudah selesai.

### 4. Isolasi Causal Cone & Pruning Cabang Gagal
- Jika salah satu node mengalami kegagalan fatal:
  1. Tandai node tersebut dengan status `failed`.
  2. Telusuri seluruh turunan langsung dan tidak langsung melalui penelusuran BFS ($\text{Cone}^{+}(v_{\text{fail}})$).
  3. Ubah status seluruh dependent downstream menjadi `skipped`.
  4. Lanjutkan eksekusi pada cabang independen lain yang tidak terdampak.
- Kriteria penyelesaian: Cabang gagal terisolasi, menghemat konsumsi token, dan tugas yang valid tetap selesai.

## Pitfalls

1. **Deadlock akibat Siklus Tersembunyi:** Menambahkan dependensi balikan dari hasil output hilir ke perencana hulu tanpa titik terminasi. Selalu jalankan `_would_create_cycle` sebelum mengizinkan penambahan edge.
2. **ID Collision pada Panggilan Paralel:** Menamai node hanya dengan ID pesan saat memanggil batch tools sekaligus. Wajib gunakan format unik `node_tool_${message_id}_${call_id}`.
3. **Negative Pan Canvas Shift:** Menghitung titik fokus kanvas secara naif yang melempar graf ke area koordinat negatif. Kunci anchor awal dengan padding kiri tetap (`panX = 50px, panY = 40px`).
4. **Premature Abort:** Membatalkan seluruh alur kerja saat satu worker sampingan gagal, padahal tugas independen lainnya masih dapat menghasilkan nilai solusi. Gunakan causal cone pruning.

## Verification

Jalankan skrip verifikasi otomatis untuk memastikan seluruh invariansi graf, splicing, dan Amdahl speedup bekerja 100%:

```bash
python3 ~/.hermes/skills/autonomous-ai-agents/agent-dag-task-splicing/scripts/dag_replanning_engine.py --demo
```

Output wajib mengonfirmasi:
- Topological sort sukses tanpa siklus.
- Sugiyama layers terpisah secara simetris.
- Dynamic task splicing berhasil menyisipkan node perantara.
- Causal cone pruning berhasil mengisolasi kegagalan downstream tanpa mematikan cabang independen.
