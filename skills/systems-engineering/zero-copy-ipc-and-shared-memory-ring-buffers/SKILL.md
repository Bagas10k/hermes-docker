---
name: zero-copy-ipc-and-shared-memory-ring-buffers
description: Zero-copy ring-buffer IPC and shared-memory transfer.
version: 0.1.0
author: Bagas Cihuy, Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [ipc, shared-memory, ring-buffer, zero-copy, telemetry]
    related_skills: [portable-liveboot-agent, agent-ephemeral-worker]
---

# Zero-Copy IPC & Shared-Memory Ring Buffers

High-throughput, low-latency inter-process communication using POSIX shared memory (`/dev/shm` + `mmap`) and lock-free cache-line aligned ring buffers.

## When to Use
- Inter-process telemetry streaming (>100Hz) between daemon workers, collectors, and agents.
- Passing large multi-kilobyte states, embeddings, or visual frames without JSON serialization overhead.
- Avoiding socket context-switch taxes and kernel buffer multi-copy overhead.
- Do not use for cross-network IPC, unbounded dynamic allocations, or multi-tenant untrusted boundaries.

## Prerequisites
- Linux or POSIX environment with `/dev/shm` filesystem access.
- Python 3.10+ standard library (`mmap`, `struct`, `os`).
- No external pip dependencies required.

## How to Run
Run unit test suite and microbenchmarks via `terminal`:
```bash
python3 -m unittest -v test_shm_ring_buffer
python3 shm_ring_buffer.py --bench --iterations 50000
python3 shm_ring_buffer.py --demo
```

## Model and Invariants
- Memory Layout: Fixed 128-byte cache-line aligned header (`magic`, `version`, `capacity`, `slot_size`, `write_seq`, `read_seq`).
- Invariant 1 (Power of Two): `capacity` and `slot_size` must be power-of-two integers; wrapping enforced via fast bitwise mask `index & (capacity - 1)`.
- Invariant 2 (Torn-Read Prevention): Producer writes payload, followed by a memory barrier storing `commit_seq = write_seq + 1`. Consumer verifies `commit_seq == read_seq + 1` before reading payload.
- Invariant 3 (Backpressure): When `write_seq - read_seq >= capacity`, push fails cleanly returning `(False, seq)` to avoid silent message corruption.

## Pitfalls
- Stale SHM files in `/dev/shm`: Unclean process terminations leave memory files. Producers must manage lifecycle or clean up via `.unlink()`.
- Multiple uncoordinated producers: This implementation is Single-Producer Multi-Consumer (SPMC) or single-reader. Multi-producer requires CAS (`compare-and-swap`) on `write_seq`.
- Cross-architecture binary alignment: Data format uses standard fixed C types (`=QIIQ`). 32-bit vs 64-bit platforms must respect 8-byte alignment.

## Verification
- Unit test suite (`test_shm_ring_buffer.py`) with 6 test cases verifying:
  1. Power of two capacity and slot-size enforcement.
  2. Single push, pop, and stats integrity.
  3. Capacity overflow and backpressure recovery.
  4. Non-destructive peek latest entry.
  5. Commit barrier torn-read prevention under mid-write crash simulation.
  6. Multi-client secondary process attach and consume.
