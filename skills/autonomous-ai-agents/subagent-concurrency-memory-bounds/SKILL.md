---
name: subagent-concurrency-memory-bounds
description: Use when admitting workers under memory and queue bounds.
version: 0.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [agents, admission, cgroup-v2, memory, META-002]
    related_skills: [agent-ephemeral-worker, meta-agent-recursive-decomposition]
---

# Bounded Sub-Agent Admission

Use a locked reservation ledger before launching independent worker processes. The stdlib helper is an executable planner model, not a process launcher, cgroup enforcer, or replacement for the Hermes scheduler.

## When to Use
- Bound dynamic worker admission, backlog and shutdown accounting under a memory policy.
- Follow structural META-001 admission with resource admission.
- Do not use to certify physical RAM availability or hard isolation of in-process delegates.

## Prerequisites
Python 3.11+ standard library. No credentials or installations. Linux cgroup v2 with delegated memory controller is required only for a future runtime integration; this helper never writes kernel controls. Read [research](references/research.md) and [runtime contract](references/runtime-contract.md).

## Quick Reference
Resolve this skill directory through `skill_view`, then invoke via `terminal`:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s ~/.hermes/skills/autonomous-ai-agents/subagent-concurrency-memory-bounds/scripts -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 ~/.hermes/skills/autonomous-ai-agents/subagent-concurrency-memory-bounds/scripts/admission.py --demo
```

CLI exit 0 means successful model demonstration; exit 2 rejects configuration. No workers are spawned.

## Procedure
1. Select a byte budget B no greater than 9,000,000,000 (decimal 9.0 GB), independently from measured physical RAM. Reserve controller/queue overhead O and safety H; require O+H<B. Completion: worker capacity C=B-O-H is explicit.
2. Submit bounded IDs and positive integer reservations r. Reject impossible workers, duplicate live IDs and queue overflow without mutation. Completion: bounded backlog contains metadata only, not prompts or results.
3. Dispatch atomically under one lock: reserve before exposing a launch ticket. Require sum(r)<=C and active count below target concurrency. Completion: pending tickets and stopping workers remain charged.
4. Runtime adapter must establish containment before untrusted execution, read back controls and reconcile startup. Completion: no worker executes outside its charged cgroup. Adapter is a design contract, not implemented here.
5. Reduce concurrency target under pressure; do not reclaim running reservations or kill automatically. Completion: draining workers retain charge and new admissions wait. FIFO deliberately tolerates head-of-line blocking.
6. On shutdown stop intake, discard queued metadata, mark active tickets stopping. Signal TERM, wait a bounded grace, escalate if authorized, reap and verify descendant cgroup empty. Completion: release only with matching ticket plus independently verified exit and empty cgroup. Unknown exit means retain charge and quarantine.
7. Run model tests and CLI checks. Completion: report observed results and unresolved runtime capabilities separately using [verification](references/verification.md).

## Pitfalls
- RSS polling, semaphore counts and estimates are not hard memory bounds; cgroup limits can transiently overshoot too.
- Cancelling an asyncio task does not establish OS process death. Never release reservations in an unconditional cancellation `finally`.
- `asyncio.Queue(maxsize=0)` is unbounded; bounded queue length also needs bounded item bytes and bounded producer task count.
- Memory ledger is single-process, in-memory and trusted-caller only. Process crashes require separate fail-closed recovery and reconciliation before reopening admission.
- Pending launch and stopping tickets count as active. Do not reuse tickets; stale exit reports must not release newer workers.
- No scheduler, subprocess/cgroup adapter, actual graceful signal delivery, OOM experiment, or production changes are included.

## Verification
Run the test command and demo above, plus the rejection command documented in references. Preserve the distinction between model invariants, read-only host observations and untested kernel enforcement. References: [research](references/research.md), [runtime contract](references/runtime-contract.md), [verification](references/verification.md).
