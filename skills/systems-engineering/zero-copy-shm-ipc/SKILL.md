---
name: zero-copy-shm-ipc
description: Zero-copy lock-free ring-buffer & eventfd IPC for Linux.
version: 1.0.0
author: Bagas Saputra & Hermes Autopilot
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [eventfd, shared-memory, lock-free, mpmc, zero-copy, ipc, io-uring]
    related_skills: [ephemeral-worker-engine, portable-liveboot-agent]
---

# Zero-Copy Shared-Memory & EventFd IPC Engine

Engine terpadu IPC Linux performa tinggi (sub-mikrodetik) untuk komunikasi antar-agen otonom. Mengonsolidasikan arsitektur antrean cincin (*ring buffer*) memori bersama, algoritma MPMC Vyukov bebas-kunci, pensinyalan kernel `eventfd` (0% CPU idle), dan batching `io_uring` SQ/CQ.

## Kapan Digunakan
- Pertukaran data atau streaming telemetri (>100Hz) antar proses/pekerja agen lokal di `/dev/shm`.
- Mencegah *busy-polling* CPU 100% pada antrean kosong via pensinyalan `eventfd` (*kernel wait-queue*).
- Swarm banyak produser dan banyak konsumen (MPMC) dengan alokasi slot tetap (256-byte) bebas alokasi dinamis.
- Batching pesan biner atau RPC melalui mekanisme cincin `io_uring` (SQ/CQ) untuk mengeliminasi overhead *syscall*.
- PANTANGAN: Jangan gunakan untuk transfer data lintas jaringan (gunakan soket TCP/gRPC).

## Arsitektur & Pilihan Mekanisme

### 1. Hybrid EventFd + Lock-Free SHM Queue (Rekomendasi Utama Multi-Worker)
Menggabungkan kecepatan cincin Vyukov atomic CAS dengan efisiensi tidur kernel `eventfd`:
- Konsumen mengecek antrean non-blocking; jika kosong, masuk ke `eventfd.wait(timeout)` yang memindahkan thread ke *kernel wait queue* (0% CPU).
- Saat produser memasukkan data (`push`), `eventfd.notify(1)` langsung membangunkan konsumen secara deterministik.
- Menghindari 100% core spin dan mencegah *torn-read* via sekuens per-slot.

```python
from hybrid_eventfd_shm_ipc import HybridEventFdShmQueue

q = HybridEventFdShmQueue(capacity=64)
q.push(b"telemetry_chunk", notify=True)
item = q.pop(timeout_sec=1.0)
q.close()
```

### 2. Lock-Free MPMC Ring-Buffer (Vyukov Sequence Array)
Untuk antrean tugas simultan banyak-produser banyak-konsumen tanpa *lock contention*:
- Kapasitas wajib kelipatan dua ($2^N$), wrapping menggunakan bitwise masking `pos & (capacity - 1)`.
- Sinkronisasi berbasis sekuens atomik per-slot menjamin isolasi mutasi data dan transmisi FIFO teratur.

```python
from mpmc_queue import LockFreeMPMCQueue

queue = LockFreeMPMCQueue(capacity=64)
queue.push(b"TASK_PAYLOAD")
msg = queue.pop()
```

### 3. POSIX Shared-Memory Direct Mmap Buffer
- Header 128-byte selaras cache-line (`magic`, `version`, `capacity`, `write_seq`, `read_seq`).
- Barrier memori memastikan verifikasi `commit_seq` sebelum membaca muatan data (*torn-read prevention*).

### 4. Linux io_uring SQ/CQ Socket Ring Buffer
- Batching $N$ operasi kirim/terima ke dalam Submission Queue Entries (SQE) dieksekusi dalam 1 kali pemicu `submit_and_wait()` ($O(1)$ syscall).
- Mengurangi *context-switch tax* drastis pada frekuensi RPC tinggi (>10.000 pesan/detik).

## Invarian Matematis
- **Batas Daya Dua**: Kapasitas $C = 2^k$ untuk seluruh antrean cincin guna menjamin wrapping bitwise $O(1)$ (`pos & (C - 1)`).
- **Backpressure Terkelola**: Saat cincin penuh, operasi `push` mengembalikan `False` tanpa merusak sekuens buffer.
- **Konsumsi CPU Idle**: 0% pemanfaatan CPU saat antrean kosong berkat `eventfd` wait queue.
