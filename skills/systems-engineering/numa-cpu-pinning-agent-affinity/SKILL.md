---
name: numa-cpu-pinning-agent-affinity
description: NUMA-aware CPU pinning and memory affinity for agents.
version: 1.0.0
author: Bagas Cihuy, Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [numa, cpu-pinning, taskset, affinity, systems-engineering, performance]
    related_skills: [systems-engineering:zero-copy-ipc-and-shared-memory-ring-buffers, systems-engineering:hybrid-eventfd-shm-ipc]
---

# NUMA-Aware CPU Pinning & Memory Affinity for Parallel Agent Workers

Sistem isolasi core CPU, affinitas memori NUMA, dan alokasi sumber daya deterministik untuk memotong tail-latency p99 inferensi paralel antar-agen.

## When to Use
- Mengisolasi proses worker agent agar tidak berpindah core CPU secara acak (mencegah context switching dan cache invalidation).
- Menjalankan inferensi SLM paralel pada mesin multi-socket/multi-core tanpa inter-socket memory penalty.
- Mengalokasikan memory affinity lokal ke NUMA node yang sama dengan core pemrosesan.

## Prerequisites
- Linux OS dengan akses sysfs (`/sys/devices/system/cpu` dan `/sys/devices/system/node`).
- Python 3.8+ dengan modul standar (`os.sched_setaffinity`).
- Opsional: paket `numactl` untuk kontrol memori berbasis kernel `set_mempolicy`.

## How to Run
Jalankan engine pinning via terminal:
```bash
python3 /home/ubuntu/.hermes/skills/systems-engineering/numa-cpu-pinning-agent-affinity/scripts/numa_pinning_engine.py --status
```

## Quick Reference
- Deteksi Topologi: `NUMAWatcher.detect_topology()`
- Alokasi Worker: `engine.allocate_worker(worker_id, pid, num_cores, preferred_node)`
- Pelepasan Worker: `engine.release_worker(worker_id)`
- Penalti Antar-Node: `engine.calculate_cross_node_penalty(cpu_id, target_node_id)`

## Verification
Jalankan pengujian unit deterministik:
```bash
python3 /home/ubuntu/.hermes/skills/systems-engineering/numa-cpu-pinning-agent-affinity/tests/test_numa_pinning.py
```
Seluruh 6 unit tests wajib lulus 100%.
