# Exact data-only contract

The top-level object has exactly `root`, `nodes`, `dependencies`, `budget_unit`, `duration_unit`. Unknown keys are rejected, including executable command fields. The flat representation keeps hierarchy depth independent of JSON nesting.

Each node has exactly `id`, `children`, `cost`, `duration`, `acceptance`. IDs match `[A-Za-z][A-Za-z0-9_-]{0,63}` literally. `children` is a duplicate-free list of declared IDs. The root has no parent; every other node has exactly one parent; all nodes must be reachable from the root. Both root-connected and disconnected cycles reject.

`cost` and `duration` are integers in [0,10^12], never booleans. Cost is exclusive per-node reserved resource units; internal nodes include planning/aggregation overhead and must not repeat descendant costs. All costs use `budget_unit`. Internal nodes have zero duration and null acceptance because they are structural, not scheduled. Leaves have durations in `duration_unit` and acceptance objects with exactly `metric`, `op`, `threshold`, `unit`, `evidence`. Operators: `==`, `<=`, `>=`. Threshold: finite integer/float with absolute value <=10^12, never boolean. Text fields are nonblank strings of at most 256 characters. Evidence is a label, not a resolved path or executed check. This checks that a measurement is specified, not that it is useful, true, or achieved.

Each dependency record has exactly `id`, `requires`. There must be exactly one record per leaf, including isolated leaves. Requires lists contain unique, declared leaf IDs; internal-node dependencies are rejected, not silently expanded. Self-loops and multi-node cycles reject. Hierarchy edges are never inserted into this DAG.

CLI uses default limits and returns JSON with exit 0 or rejection JSON with exit 2. Trusted Python callers may pass `Limits(...)` to both `load_plan` and `validate`. Limits are caller-owned policy, never read from plan fields. Limits must be nonnegative bounded integers. No input file is modified. Ties on critical paths choose lexicographically larger IDs; topological order may otherwise follow input ordering, not a canonical ordering across permuted inputs.

See `templates/valid_plan.json`: three leaves, one join, total exclusive budget 10 tokens, ideal dependency path b→c of duration 8 seconds. These are synthetic declarations, not measured agent usage or runtime.
