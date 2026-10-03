---
name: edge-slm-microsandbox
description: Use when isolating edge SLM tools under memory quotas. Ephemeral micro-sandbox via POSIX rlimit.
version: 1.0.0
author: Bagas Saputra & Hermes Autopilot
license: MIT
metadata:
  hermes:
    tags: [edge-slm, sandboxing, rlimit, memory-bounds, low-latency, cgroups]
    related_skills: [edge-slm-tool-calling, agent-speculative-execution, agent-test-time-compute]
---

# Edge SLM Micro-Sandbox: Ephemeral Resource Quotas on Edge Devices

Isolasi eksekusi alat (*tool calling*) pada perangkat edge / CPU berspesifikasi rendah tanpa overhead Docker container (>500ms startup). Menggunakan POSIX `resource.setrlimit` dan grup proses terisolasi untuk membatasi alokasi RAM, waktu CPU, batas waktu *wall-clock*, dan deskriptor berkas.

## Kapan Digunakan
1. Menjalankan skrip atau alat tidak terpercaya yang dipanggil oleh model SLM lokal (llama.cpp, Ollama, vLLM).
2. Mencegah kebocoran memori (*OOM crash*) pada server/VPS berspesifikasi hemat RAM (<1GB).
3. Menghentikan secara deterministik *infinite loop* atau proses menggantung tanpa merusak *main agent loop*.

## Arsitektur Batas Matematis (Berdasarkan 3 Mindset)
1. **Mekanistik-Kausal (Bounds & Resource Modeling)**:
   - `RLIMIT_AS`: Batas *virtual address space*. Mencegah alokasi heap di luar kuota (misal: 64MB - 128MB).
   - `RLIMIT_CPU`: Batas detik CPU riil sebelum kernel mengirim `SIGXCPU`.
   - `RLIMIT_NOFILE`: Batas jumlah file descriptor terbuka (mencegah *descriptor exhaustion*).
   - `os.setpgrp()`: Mengisolasi subproses ke dalam process group terpisah, memungkinkan `os.killpg()` membersihkan seluruh pohon subproses seketika.
2. **Bayesian-Eksperimental**:
   - Prediksi kegagalan: Alokasi yang melebihi kuota kuantitatif wajib memicu kegagalan deterministik (`MemoryError` / `SIGSEGV`), bukan menelan alokasi sistem.
   - Pengecekan status *two-phase*: Verifikasi kode keluar dan penanda *killed_by* sebelum hasil diterima.
3. **Desain Sistem & Optimasi**:
   - Latensi *cold start* < 10ms (jauh lebih cepat dibanding microVM/Docker yang memakan 200ms - 2s).
   - *Zero-regression buffer*: Output dipotong pada `max_output_bytes` (misal: 64KB) agar memori proses induk aman.

## Implementasi Kode Praktis

```python
from micro_sandbox import run_in_microsandbox, EphemeralResourceQuota

quota = EphemeralResourceQuota(
    max_memory_bytes=64 * 1024 * 1024,   # 64 MB
    max_cpu_seconds=2,                    # 2 detik CPU
    max_wall_time_seconds=3.0,            # 3 detik Wall time
    max_output_bytes=32 * 1024            # 32 KB
)

result = run_in_microsandbox(
    cmd=["python3", "candidate_script.py"],
    quota=quota
)

if not result.is_success:
    print(f"Tool execution rejected by sandbox: {result.killed_by}")
else:
    print("Output:", result.stdout)
```

## Verifikasi Empiris
Telah diverifikasi dengan 5 uji deterministik di `scripts/test_micro_sandbox.py`:
- `test_01_normal_execution`: Berhasil dengan exit 0.
- `test_02_memory_limit_breach`: Memblokir alokasi 120MB pada limit 32MB (`memory_limit`).
- `test_03_wall_clock_timeout`: Menghentikan proses menggantung tepat waktu (<2.5s).
- `test_04_output_truncation_cap`: Menahan lonjakan buffer output di 512 byte.
- `test_05_startup_latency_benchmark`: Latensi startup <15ms.
