---
name: agent-async-rpc-protocol
description: Use when designing cancellable sub-agent RPC.
version: 0.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [agents, rpc, cancellation, flatbuffers, backpressure]
    related_skills: [multiagent-formal-verification, agent-dag-task-splicing]
---

# Asynchronous Sub-Agent RPC

Separate transport, serialization, buffer ownership, and execution semantics. Prefer a mature RPC runtime; zero-copy decoding is not an end-to-end zero-copy transport or a security boundary.

## When to Use
- Design streaming dispatcher/worker RPC, cascade cancellation, or bounded local data exchange.
- Diagnose orphan work, expired requests, or copies dominating measured latency.
- Do not replace MCP/A2A interoperability protocols with a private binary protocol without an explicit adapter contract.

## Prerequisites
- Python 3.11+, isolated venv with `grpcio` and `flatbuffers` for the runnable probe.
- Approved sandbox only; the probe binds an ephemeral loopback port, never a public listener.
- Define authenticated peers, maximum payload, queue bytes, concurrency, deadline, and side-effect policy before deployment.
- Read [evidence and architecture](references/evidence.md).

## Quick Reference
Use `terminal` from this skill directory:
- `python3 -m venv /tmp/agent-rpc-venv` (on Windows choose a user temp path).
- `/tmp/agent-rpc-venv/bin/pip install grpcio flatbuffers` (Windows: `Scripts/python.exe -m pip`).
- `/tmp/agent-rpc-venv/bin/python scripts/probe_rpc.py`.
The helper prints assertions, package versions and loopback latency samples. It is an integration probe, not a production agent service.

## Procedure
1. Specify versioned envelope: session_id, request_id, parent_id, attempt, method, sequence, remaining_budget, idempotency_key, payload reference. Authenticate sender independently of these fields. Completion: malformed, unauthorized and replayed requests have documented outcomes before side effects.
2. Model latency as queue + encode + transport + work + decode. Calculate Amdahl bound using measured serialization fraction before adopting zero-copy. Completion: p50/p95/p99 and sample size retained, no vendor benchmark substituted for agent measurements.
3. Choose transport: gRPC for mature deadlines/streaming; Cap'n Proto for capability/promise-pipelining workloads; FlatBuffers for typed in-place payload access, not an RPC runtime by itself. Completion: compatibility and encryption requirements explicitly covered.
4. Propagate remaining time, not a remote monotonic timestamp. Derive local deadline on receipt and subtract local queue/processing elapsed time before child dispatch. Reserve cleanup time. Completion: expired work never starts and child deadlines never exceed parent remaining budget.
5. Track each outgoing call/task under its parent. On cancellation cancel children, await cleanup, and re-raise CancelledError. Never assume cancelling an await stops a thread/process or external mutation. Completion: actual nested cancellation and deadline tests observe cleanup events, not only client errors.
6. Bound both message bytes and active calls before spawning work; use transport flow control plus application admission. Keep cancellation/control traffic out of a saturated data queue. Completion: slow-consumer and oversize tests demonstrate bounded memory in the target deployment.
7. For shared-memory payloads define owner, segment generation, offset, length, lease, immutable publication, ACK, and reclaim sequence. Use supported IPC synchronization, not Python/GIL assumptions about atomic interprocess writes. Completion: stale-generation and concurrent-reclaim tests precede adoption; copying remains the safe fallback across untrusted writers.
8. Separate CANCEL_REQUESTED, CANCELLED, SUCCEEDED, FAILED, and UNKNOWN_OUTCOME. Cancellation can race a commit; reconcile by idempotency key before retry. Completion: crash/replay tests establish effect semantics rather than claiming exactly-once from RPC delivery.
9. Run helper twice, record versions and all limitations. Completion: server-stream sequence, direct cancellation, nested-child cleanup, deadline, bounded queue, and FlatBuffers view tests pass. Production auth/replay/shared-memory concurrency still require separate testing.

## Pitfalls
- FlatBuffers benchmark page describes an old Windows 7 C++ fixture; its large ratios do not predict Python agent performance.
- Zero-copy field access can still allocate strings, copy builder output, use kernel copies, and traverse TLS buffers.
- Cap'n Proto pipelining removes eligible network waits, not computation, client-side branches, or arbitrary scalar dependencies.
- gRPC Python spawned work needs explicit lifecycle handling; no deadline is installed by default.
- A bounded queue does not bound RAM if unlimited producers, message sizes, or tasks are admitted.
- Suppressing CancelledError can break TaskGroup/timeout semantics. CPU-bound handlers need process isolation and explicit termination policy.
- Shared writable buffers can change after verification (TOCTOU); an offset bounds check is not sufficient trust isolation.

## Verification
Run `scripts/probe_rpc.py` with the isolated interpreter. Verify each named assertion and read actual output, not a fabricated expected transcript. The local probe uses raw-byte gRPC handlers and a FlatBuffers byte-vector fixture; it does not test generated production schemas, TLS, authorization, durable deduplication, shared-memory rings, Cap'n Proto transport, or WAN tail latency. Retain these as unverified acceptance gates, not successful claims.
