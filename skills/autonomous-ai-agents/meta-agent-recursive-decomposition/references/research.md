# Research basis and explicit limits

## Primary sources consulted

1. Python Software Foundation, Python 3.11 `graphlib` documentation: https://docs.python.org/3.11/library/graphlib.html . Retrieved through web extraction. `TopologicalSorter` consumes a mapping from nodes to **predecessors**, not successors. A complete topological ordering exists iff the graph is acyclic; `static_order()` is suitable for offline ordering. This implementation resolves every predecessor against the declared leaf registry before invoking graphlib and rejects `CycleError` rather than accepting a partial order.
2. Salaheddin Alzu’bi et al., **ROMA: Recursive Open Meta-Agent Framework for Long-Horizon Multi-Agent Systems**, arXiv:2602.01848v2, 14 February 2026. Primary full-text source: https://arxiv.org/html/2602.01848v2 . Sections 1 and 2.1 describe Atomizer, Planner, Executor, Aggregator; top-down dependency-aware decomposition; bottom-up aggregation; local executor contexts; dependency-aware parallelism. The paper links the authors' implementation at https://github.com/sentient-agi/ROMA (link recorded, repository not installed or executed). Paper benchmark improvements are author-reported system-level results, not evidence for this validator.

Search route note: the agent-reach Exa CLI route failed because `mcporter` was absent. Built-in web search located the paper and web extraction read the primary source. No dependency installation or live agent experiment was performed.

## What transfers, and what does not

ROMA motivates separating recursive task ownership from lateral precedence and explicit leaf contracts. This skill implements an intentionally narrower **pre-execution admission gate**, not ROMA's controller, prompt optimizer, agent executors, aggregation, or safety sandbox. Unlike ROMA's dynamic planning, the input here must already contain the complete bounded hierarchy. Semantic MECE (mutually exclusive, collectively exhaustive) coverage cannot be proven by graph validation.

The existing `agent-dag-task-splicing` skill changes dependencies during execution, preserves completed work, and handles failure cones. This skill admits a static decomposition tree and a separately supplied leaf dependency DAG before any execution. No splicing, scheduling, worker creation, retry loop, or task status mutation occurs. A changed plan must be resubmitted as a fresh snapshot.

Do not confuse task recursion with latent-state recursive multi-agent computation. A search also surfaced RecursiveMAS, arXiv:2604.25917, whose abstract concerns latent collaboration loops; that is not the hierarchy-admission mechanism implemented here and its performance claims are not used.

## Mechanistic bounds

Let N be nodes, E leaf dependency edges, B maximum branching, and D maximum depth (root depth zero). For B > 1 the complete-tree envelope is (B^(D+1)-1)/(B-1); for B=1 it is D+1; for B=0 only a root is possible. Enforce the explicit N cap independently, since a depth cap alone does not control breadth. Iterative traversal avoids recursive Python calls for hierarchy validation. The JSON loader caps input bytes before parsing, rejects duplicate JSON keys and nonfinite constants, and translates parser recursion failure into rejection.

Default policy: 262144 input bytes, 128 nodes, depth 8, branching 8, 512 dependency edges, 100000 declared budget units, 10000 declared critical-path time units. Internal node costs are exclusive planning/aggregation overhead. Total budget is the sum of all node costs once. The library accepts a trusted caller's Limits object; the plan cannot raise its own caps. Reject booleans as numeric values and cap individual integers to prevent extreme numeric payloads.

After reference resolution and tree validation, topological processing computes EF(v)=duration(v)+max(EF(p)) over prerequisites, with the empty maximum zero. The largest EF is the weighted leaf dependency critical path. Time and auxiliary graph storage are O(N+E) after bounded JSON parsing, assuming bounded identifiers and arithmetic. Input byte limits apply to the file loader; direct Python callers must provide already-decoded ordinary JSON data, not arbitrary objects. Reading hostile devices or blocking pipes is outside this local-file contract.

## Amdahl and work/span bounds

For parallelizable fraction p and W workers, the overhead-free Amdahl speedup ceiling is 1/((1-p)+p/W). An illustrative p=0.8 and W=4 yields 2.5, calculated with Python; this is not measured speedup. For total leaf work T and dependency span C, execution time is at least max(T/W, C) under the declared cost model. Planner/aggregation overhead, communication, retries, and worker contention increase actual time. Record p95 from real traces before making production latency claims.

## Prediction versus tests

A claim such as 'decomposition improves success probability' is a hypothesis, not a passed test. Under a deliberately simplified Bernoulli model with a Beta(alpha,beta) prior, measured task successes s and failures f yield Beta(alpha+s,beta+f); report the prior, sampling scheme, and uncertainty, and do not invent observations. Correlated subtasks and changing task distributions violate the simple independence/stationarity assumptions. A structural unit-test pass is not a task success sample and must never update that posterior. This delivery computes no Bayesian posterior and has no live task outcomes.

A future separately authorized evaluation could preregister a comparison against flat planning on matched held-out tasks, hold model/tool budgets fixed, score external leaf and root acceptance, record cost and wall-clock latency, and examine calibration as well as success. Those are proposed tests, not tests conducted here.

## Optimization tradeoffs

Increasing depth can make contracts more specific but amplifies planner/aggregator overhead, information loss, and error propagation. Increasing breadth offers ideal parallelism at the cost of peak memory, coordination, duplicate work, and API contention. Aggregation compresses context but may discard critical evidence. Minimizing the ideal critical path can increase total cost. Optimize a constrained Pareto frontier (success, spend, latency, peak concurrency), not recursion depth itself. This validator enforces declared caps and reports a lower-bound leaf latency only; it does not claim optimal schedules or estimate root semantic success.
