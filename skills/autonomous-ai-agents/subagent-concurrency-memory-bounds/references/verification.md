# Local verification — 2026-09-24

Status TESTED only for the admission model; runtime adapter remains CANDIDATE/unimplemented.

## Commands through terminal

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s /home/ubuntu/.hermes/skills/autonomous-ai-agents/subagent-concurrency-memory-bounds/scripts -p 'test_*.py' -v
python3 -B /home/ubuntu/.hermes/skills/autonomous-ai-agents/subagent-concurrency-memory-bounds/scripts/admission.py --demo
python3 -B /home/ubuntu/.hermes/skills/autonomous-ai-agents/subagent-concurrency-memory-bounds/scripts/admission.py --demo --budget 9000000001
```

Observed: 5 unittest methods passed, including parameterized malformed inputs, budget boundary, concurrent spike, shutdown, target draining, stale/forged tickets and CLI behavior. First implementation was preceded by a failing helper-presence/admission test; lifecycle, validation/backpressure and CLI slices each ran red before their implementations. The lifecycle red was missing-method AttributeError, explicitly not a behavioral failure. Final suite reported `Ran 5 tests in 0.288s`, `OK`. ThreadPoolExecutor spike submitted 100 requests into backlog 10 then ran 40 dispatch calls; assertions verified exactly 10 accepted, 3 active, 7 queued, 60 declared bytes reserved. This is synthetic metadata, not measured worker memory.

Demo returned model_only=true, exit_evidence=synthetic; before={reserved:60,active:2,queued:0}; after={reserved:0,active:0,queued:0}; successful CLI is also asserted by subprocess test. Above-policy CLI returned JSON error `integer outside policy range`, exit 2 (expected). A combined shell invocation ends with 2 because its last command intentionally rejects.

## Read-only capability observation

/proc/self/cgroup used unified 0:: hierarchy. cgroup2 root listed memory controller; its root memory.max was absent (normal root-interface distinction, not lack of memory control). Resolved current scope exposed controllers `memory pids`, empty subtree_control, memory.max=4294967296, memory.high=max, memory.swap.max=max, populated=1. os.access(current_scope,W_OK) was True while cgroup root was False. Ancestor memory.max entries above the current scope reported max. These observations are ephemeral and do not establish writable valid worker delegation. Root listing alone was insufficient, so inspection followed the current path.

/proc/meminfo reported MemTotal=16372148 kB; this is not the 9.0GB policy cap, nor the 4GiB current-scope allowance. No deployment budget was inferred from MemAvailable. No writes to /sys, live OOM, worker processes, service, scheduler, state.json, cron or other profile were performed.

## Retrieval and limitations

Official kernel/Python pages retrieved successfully via Jina. Optional `agent-reach check-update` failed with command-not-found exit 127; no installation was attempted and retrieval was unaffected. No load/performance benchmark, durable recovery, adversarial caller isolation, fork/migration, swap, actual grace/kill cleanup or kernel enforcement test ran. Future runtime code requires a new authorization and separate acceptance suite.
