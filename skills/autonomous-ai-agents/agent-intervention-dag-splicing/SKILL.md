---
name: agent-intervention-dag-splicing
description: "Live intervention task splicing and dynamic DAG reschedule."
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [autonomous-agents, dag, causal-inference, task-splicing, dynamic-rescheduling, amdahl]
    related_skills: [agent-runtime-causal-discovery, agent-dag-task-splicing, mathematical-problem-solving]
---

# Agent Intervention DAG Splicing

Engine penyambungan tugas intervensi langsung (live task splicing), pembatalan kerucut kausal hilir (causal cone invalidation), dan penjadwalan ulang topologis dinamis untuk alur kerja agen otonom.

## When to Use
- Mengubah atau menyisipkan tugas baru pada alur kerja DAG agen yang sedang berjalan di tengah eksekusi.
- Menginvalasi tugas hilir secara kausal ketika kontrak/skema data tugas hulu dimutasi atau diperbaiki.
- Menjadwalkan ulang urutan eksekusi tugas sisa tanpa mengulang tugas yang sudah sukses (preserve completed work).
- Mencegah siklus dependensi (cycle rejection & atomic rollback) saat melakukan intervensi alur kerja.

Don't use for:
- Perencanaan awal statis sebelum runtime dimulai (gunakan `agent-dag-task-splicing` atau `meta-agent-recursive-decomposition`).
- Eksekusi satu tugas tunggal tanpa grafik dependensi.

## Prerequisites
- Python 3.10+
- Modul internal: `scripts/dag_splicing_engine.py`

## Quick Reference
```bash
# Jalankan pengujian unit invarian engine
python3 ~/.hermes/skills/autonomous-ai-agents/agent-intervention-dag-splicing/scripts/test_dag_splicing.py
```

## How to Run via Hermes Tools
```python
from dag_splicing_engine import InterventionDAGSplicer, TaskNode, TaskState

splicer = InterventionDAGSplicer(dag_id="workflow-1")
splicer.add_task(TaskNode("A", "Fetch", "fetch", 50.0))
splicer.add_task(TaskNode("B", "Process", "process", 100.0), dependencies=["A"])

# Splice tugas intervensi V di antara A dan B secara atomik
verify_node = TaskNode("V", "Validate", "validate", 20.0)
splicer.splice_intervention_nodes(
    intervention_nodes=[verify_node],
    splice_edges=[("A", "V"), ("V", "B")],
    remove_edges=[("A", "B")],
    reason="Inject data validation gate"
)

# Ambil urutan eksekusi yang dijadwalkan ulang
order = splicer.reschedule_topological_order()
```

## Procedure
1. **Modelkan Status Awal Alur Kerja**: Inisialisasi `InterventionDAGSplicer` dan daftarkan seluruh tugas beserta dependensinya.
2. **Identifikasi Titik Intervensi**: Tentukan simpul target yang mengalami perubahan kontrak atau memerlukan langkah penyelamatan.
3. **Penyambungan Tugas Atomik (Atomic Splicing)**: Panggil `splice_intervention_nodes()` dengan simpul baru, edge tambahan, dan edge usang yang dihapus.
4. **Verifikasi Bebas Siklus**: Pastikan engine tidak melempar `DAGCycleError`. Jika terjadi siklus, engine otomatis melakukan rollback topologi secara atomik.
5. **Invalasi Kerucut Kausal**: Seluruh tugas hilir yang terjangkau secara kausal otomatis ditransisikan ke status `INVALIDATED` untuk eksekusi ulang.
6. **Eksekusi Penjadwalan Ulang Topologis**: Dapatkan urutan kerja baru via `reschedule_topological_order()`.

## Pitfalls
- **Untracked Downstream Mutation**: Mengubah output tugas hulu tanpa menginvalasi simpul hilir menyebabkan inkonsistensi data. Engine secara otomatis menghitung transitive closure causal cone untuk membatalkan hasil usang.
- **Circular Dependency Trap**: Menyambungkan tugas verifikasi yang secara tidak sengaja merujuk kembali ke tugas hilir. Engine menolak siklus dengan Kahn's algorithm sebelum mutasi dikomit.
- **Premature Re-execution**: Mengulang tugas independen yang sudah sukses memboroskan batas Amdahl. Penjadwal dinamis mengabaikan simpul `COMPLETED` yang tidak terinvalasi.

## Verification
- Jalankan suite pengujian unit: `scripts/test_dag_splicing.py` (7/7 tests passed).
- Pastikan invariansi rollback siklus terbukti: topologi kembali utuh saat deteksi siklus terpicu.
