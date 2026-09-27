# META-002: evidence and reasoning

Research retrieved 2026-09-24 through agent-reach's web/Jina route. Official pages were read, not merely search snippets. This is a new resource-admission layer; META-001 validates plan structure and agent-ephemeral-worker addresses scratchpad lifecycle. Neither replaces OS memory containment.

## Primary sources and claim map

1. Linux cgroup v2: https://docs.kernel.org/admin-guide/cgroup-v2.html — sections Memory Interface Files, Core Interface Files, Delegation, No Internal Process Constraint. `memory.max` is the memory controller's hard limit, with documented temporary overshoot; unreclaimable usage can invoke in-cgroup OOM. `memory.high` throttles/reclaims and is not a hard bound. `memory.swap.max` controls swap separately. `memory.oom.group=1` treats a workload as an OOM group, except tasks protected by oom_score_adj=-1000. `cgroup.kill` kills descendants with SIGKILL, handling concurrent forks/migrations; it is not graceful shutdown. `cgroup.events` populated=0 reports no live processes in the subtree, not zero cached memory charge.
2. Python 3.11 queues: https://docs.python.org/3.11/library/asyncio-queue.html — positive maxsize bounds queued item count; zero/negative means unbounded. Awaited put blocks when full. Queues are not thread-safe. This helper instead uses a threading RLock and immediate rejection; it does not claim to implement asyncio.Queue.
3. Python 3.11 subprocesses: https://docs.python.org/3.11/library/asyncio-subprocess.html — wait establishes direct-child termination; pipes can deadlock wait, communicate drains pipes but buffers output in memory. Use bounded streaming/discard or quota-limited files in a real adapter. The StreamReader limit is not a total output cap.
4. Python 3.11 tasks: https://docs.python.org/3.11/library/asyncio-task.html — CancelledError is a BaseException; propagate after cleanup. wait_for cancels its awaitable and can exceed the nominal timeout while cancellation finishes. Shield prevents propagation into a task, not process death or indefinite parent survival.

These are rolling kernel docs versus pinned Python 3.11 docs. Kernel features, writable delegation and effective ancestor constraints must be probed on the actual deployment, not inferred from documentation presence.

## Mindset 1 — mechanistic/causal

Policy B <= 9,000,000,000 bytes; O=controller+bounded-queue+output+metadata envelope, H=safety margin, C=B-O-H. Admit iff count(A)<target and sum(r_i for i in A)+r_new<=C. Active A includes RESERVED (not launched), RUNNING and STOPPING. Reserve before spawn; release only after verified exit and empty descendant cgroup. A cancellation event is a request, not causal evidence of process death. A lock covers both count and budget checks plus mutation; separate semaphore and memory checks would admit races.

For homogeneous r, total feasible concurrency W=min(W_config, floor(C/r), W_cpu, W_external). CPU/external bounds are adapter policy, not automatically detected by this helper. Additional admission uses min(max(0,target-|A|), floor((C-sum(r_i))/r)). Mixed sizes use FIFO exact reservation checks; do not divide free bytes by mean RSS. Target reductions drain without retroactively falsifying existing reservations; existing count may temporarily exceed target but never configured maximum.

Example computed with Python: B=9e9, O=1.5e9, H=0.5e9, r=1e9 => 7 possible worker envelopes before CPU/external constraints. These are hypothetical declared bytes, not a recommendation for this host. Effective deployment budget must be no higher than policy, provisioned envelope and effective ancestor cgroup capacity, with co-tenants accounted for. Observed current scope limit was 4,294,967,296 bytes, so 9 GB is not deployable there.

## Mindset 2 — Bayesian/experimental

Known: official semantics above; local model tests reject malformed values, bound reservation/count/backlog and hold stopping reservations. Known: read-only host inspection found cgroup v2 and a finite current-scope limit. Likely: preserving reservations until exit avoids overcommit during cancellation spikes; a bounded queue reduces planner metadata growth. Uncertain: throughput, workload-specific r, O/H sizing, tail latency, swap behavior under pressure, delegation usability and real descendant cleanup.

Do not treat deterministic tests as posterior samples of LLM task success or OOM-free runtime. Future authorized experiment: fixed task corpus, same model/budget, compare fixed versus pressure-adaptive targets, record admitted/rejected, service time, p95 latency, memory.events, memory.current/peak, queue dwell and cleanup latency. Pre-register failure: any outside-cgroup execution, premature release, unbounded producer accumulation or unmatched live cgroup. No such experiment was run.

## Mindset 3 — optimization/system design

Amdahl illustration S(W)=1/((1-p)+p/W), p=0.8: Python computation returned W=1:1.0, W=2:1.6666666666666665, W=4:2.5, W=8:3.333333333333333. This is a theoretical upper bound for the assumed parallel fraction, not a benchmark. More workers trade memory/coordination for diminishing speedup; CPU saturation, I/O quotas and model-provider limits may dominate.

Queue count Q plus maximum metadata bytes L bounds retained payload approximately O(Q*L), not Python allocator overhead or total RSS. Here IDs are ASCII <=64 characters, integers bounded, backlog<=10000, configured concurrency<=1024, active/history dictionaries discard released tickets. Ticket serial is monotonic and grows logarithmically with lifetime admissions; this is not a strict fixed-byte allocator. Queue scans and reservation sums cost O(Q+W) per relevant operation, bounded by configured caps. No task-per-waiting-submit is created. Immediate backpressure is intentional; callers must not compensate with an unbounded retry list.

FIFO head-of-line blocking preserves admission order but may underutilize capacity. Size-aware bypass can improve packing while starving large jobs; add aging only with separate tests. Hysteresis is adapter policy: reduce target promptly on pressure, increase conservatively after sustained headroom; never substitute observed low RSS for reservation release.
