---
name: agent-ephemeral-worker
description: Use when spawning isolated ephemeral workers.
version: 0.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [agents, worker, sandbox, ephemeral, isolation]
    related_skills: [agent-async-rpc-protocol, agent-ephemeral-sandboxing]
---

# Ephemeral Sub-Agent Worker Sandboxing

Isolate ephemeral sub-agent execution with bounded memory, path containment, and zero-leak resource reclamation.

## When to Use
- Spawn lightweight sub-agents requiring scratchpad disk access without persistent contamination.
- Enforce strict byte quotas, execution timeouts, and path traversal barriers on worker tasks.
- Clean up worker state deterministically after task completion or failure.

## Prerequisites
- Python 3.11+ standard library.
- Read [evidence and architecture](references/evidence.md).

## Quick Reference
Execute test probe via `terminal`:
- `python3 scripts/probe_worker.py`

## Procedure
1. Initialize worker with dedicated temporary workspace and memory limit.
2. Intercept and validate file access to guarantee relative-path containment.
3. Track allocated bytes against the per-worker memory/scratchpad quota.
4. Execute worker task with bounded timeout.
5. Guarantee unconditional rmtree disposal on exit or error.

## Pitfalls
- Relying solely on chroot/namespaces when unprivileged users cannot invoke them.
- Silent leakage of temporary directories when tasks fail with unhandled exceptions.
- Assuming memory limits in user space prevent OS-level out-of-memory without quotas.

## Verification
Run `scripts/probe_worker.py` and verify all 3 test cases pass with zero residual artifacts on disk.
