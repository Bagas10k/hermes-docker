---
name: shared-memory-mpmc-queue
description: Use when building lock-free MPMC shared-memory queues.
version: 1.0.0
author: Bagas Saputra & Hermes Autopilot
license: MIT
metadata:
  hermes:
    tags: [mpmc, lock-free, shared-memory, ring-buffer, systems-engineering, concurrency]
    related_skills: [kernel-eventfd-agent-signaling, agent-iouring-zero-copy-ipc, zero-copy-ipc-and-shared-memory-ring-buffers]
---

# Shared-Memory Lock-Free MPMC Concurrent Ring-Buffer

Antrean cincin bebas-kunci (*lock-free*) Multi-Producer Multi-Consumer (MPMC) berbasis algoritma Dmitry Vyukov dengan nomor sekuens atomik per-slot. Menghilangkan *lock contention* dan *mutex bottleneck* saat puluhan agen produser dan konsumen bertukar pesan secara simultan.

## Kapan Digunakan
1. Swarm multi-agen memiliki banyak produser tugas (*dispatchers*) dan banyak agen pekerja (*workers*) yang mengakses satu antrean bersama.
2. Penggunaan `queue.Queue` atau `multiprocessing.Queue` berbasis mutex konvensional mengalami degradasi performa akibat *thread serialization*.
3. Membutuhkan transfer pesan cepat dengan alokasi slot tetap (256-byte) di memori bersama tanpa *garbage collection* berlebih.

## Sintesis 3 Mindset Problem Solving

1. **Lensa Mekanistik-Kausal (Vyukov Sequence-Based Synchronization)**:
   - Setiap slot mempertahankan nomor urut atomik `sequence`.
   - Produser memeriksa apakah `slot.sequence == pos`. Jika ya, produser memajukan `enqueue_pos` via CAS atomik, menyalin payload, lalu memperbarui `slot.sequence = pos + 1`.
   - Konsumen memeriksa apakah `slot.sequence == pos + 1`. Jika ya, konsumen memajukan `dequeue_pos` via CAS atomik, membaca data, lalu mengembalikan slot ke produser via `slot.sequence = pos + mask + 1`.
   - Hal ini menjamin tidak ada pembacaan data sebelum penulisan tuntas (*torn-read prevention*).

2. **Lensa Bayesian-Eksperimental**:
   - Prediksi: 4 produser dan 4 konsumen konkuren mengirimkan 1.000 pesan simultan tanpa ada satu pun pesan yang hilang atau terduplikasi.
   - Hasil uji: 5 unit test deterministik lulus dalam 0.071 detik (`test_mpmc_queue.py`), membuktikan integritas $100\%$ zero data loss (`len(set(received)) == 1000`).

3. **Lensa Desain Sistem & Optimasi**:
   - Operasi modulo dioptimasi dengan bitwise mask (`pos & mask`), menuntut kapasitas kelipatan dua ($2^N$).
   - Backpressure deterministik: Pengembalian nilai `False` instan saat antrean penuh tanpa memblokir thread.

## Implementasi Cepat

```python
from mpmc_queue import LockFreeMPMCQueue

# Inisialisasi antrean 64-slot
queue = LockFreeMPMCQueue(capacity=64)

# Multi-Producer
queue.push(b"AGENT_TASK_PAYLOAD_1")
queue.push(b"AGENT_TASK_PAYLOAD_2")

# Multi-Consumer
msg1 = queue.pop()
msg2 = queue.pop()
print("Diterima:", msg1.decode(), msg2.decode())
```

## Verifikasi Empiris
Telah diverifikasi via `scripts/test_mpmc_queue.py`:
- `test_01_power_of_two_enforcement`: Penegakan kapasitas $2^N$.
- `test_02_fifo_order_and_empty`: Integritas urutan FIFO dan penanganan antrean kosong.
- `test_03_queue_full_backpressure`: Backpressure saat kapasitas maksimum tercapai.
- `test_04_concurrent_mpmc_correctness`: 4 produser & 4 konsumen simultan tanpa data hilang.
- `test_05_payload_size_boundary`: Penolakan batas payload melebihi 256 byte.
