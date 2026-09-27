---
name: meta-agent-recursive-decomposition
description: Use when admitting bounded recursive subgoal plans.
version: 0.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [planning, recursion, admission, offline, META-001]
    related_skills: [agent-dag-task-splicing]
---

# Bounded Recursive Subgoal Plan Admission

Validate a proposed hierarchy before execution, independently of its dependency DAG. This is an offline structural gate, not an agent runner or proof that the proposed work succeeds. JSON data is never evaluated as code; there are no model calls, tool launches, network calls, or state/vault writes in the validator.

## When to Use

- Admit a recursively decomposed goal before any execution or delegation.
- Reject runaway expansion, ambiguous ownership, unmeasurable leaves, and dependency deadlocks.
- Estimate declared resource demand and ideal dependency latency before committing a budget.
- Do not use for in-flight DAG rewrites: `agent-dag-task-splicing` handles that separate lifecycle. Do not use to certify factual accuracy, semantic goal coverage, or safe tool execution.

## Prerequisites

Python 3.11+ and its standard library only. No credentials, installs, agents, services, or privileged actions. Locate this skill's `scripts/` directory using `skill_view` or `search_files`; the commands below use its user-local default location. On another profile, resolve that profile's skill path without modifying other profiles.

## Quick Reference

Use `terminal` with these commands (substitute the discovered skill path where needed):

```text
python3 ~/.hermes/skills/autonomous-ai-agents/meta-agent-recursive-decomposition/scripts/validate_plan.py ~/.hermes/skills/autonomous-ai-agents/meta-agent-recursive-decomposition/templates/valid_plan.json
python3 -m unittest discover -s ~/.hermes/skills/autonomous-ai-agents/meta-agent-recursive-decomposition/scripts -p 'test_*.py' -v
```

Exit 0 means structurally admitted; exit 2 means rejected. The JSON result reports estimated budget and leaf dependency critical path, not observed performance. Schema and exact cost semantics: [references/schema.md](references/schema.md). Sources, mechanisms, and research limitations: [references/research.md](references/research.md).

## Procedure

1. Specify one root goal and a flat node registry, with `children` defining a tree. Use unique literal IDs; do not normalize malformed IDs. Each non-root node must have one parent and every node must be reachable. Stop expanding when a goal has a measurable atomic contract. Completion: every intended subgoal is represented exactly once.
2. Add dependency records separately, only between leaves. Each record identifies a leaf and its prerequisite leaves. Resolve references before topological sorting; graphlib can otherwise introduce an undeclared predecessor. Completion: every leaf has exactly one dependency record, including independent leaves with empty prerequisite lists.
3. Give each leaf a metric, comparison operator, finite numeric threshold, unit, and evidence label. These are declarative contracts, not commands or actual measurements. Completion: every leaf is structurally measurable; a human separately checks that these measures entail the goal.
4. Assign nonnegative integer resource units to every node's exclusive local cost. Include planning/aggregation overhead in internal-node costs, not descendant totals. Give leaves integer duration estimates in one declared time unit. Completion: no double-counted inclusive budgets and no unpriced modeled node.
5. Run the bounded validator. Policy caps are supplied by the caller, never by the plan; defaults cap bytes, nodes, depth, branching, edges, budget, and ideal critical path. Completion: exact candidate passes or is rejected with a reason. Revalidate every revision; never silently delete rejected nodes.
6. Review semantics and assumptions separately. Tree structure cannot prove mutually exclusive/collectively exhaustive coverage or faithful aggregation. Record unresolved uncertainty, resource reservations, and future runtime monitoring requirements. Completion: any subsequent execution needs separate authorization and runtime enforcement; this skill launches nothing.

## Pitfalls

- A tree edge means ownership/decomposition, not temporal precedence. Dependency edges refer only to atomic leaves; internal execution/aggregation schedules are deliberately not modeled.
- Declared budget admission is not actual token or currency enforcement. Lying estimates pass structural checks; runtimes need meters, cancellation, and reservations.
- Critical path assumes unlimited parallel resources and declared leaf durations; it excludes planning, communication, aggregation latency, retries, and contention. It is a lower bound, not a promised wall-clock duration.
- A valid metric schema is not a passed acceptance test. Evidence labels are opaque strings: no files or URLs are opened, no predicates or commands run.
- Deeper decomposition can clarify work while increasing coordination cost and fragmentation; broader trees can improve ideal parallelism while increasing memory demand and duplicate work. Prefer a Pareto tradeoff, not maximum recursion.
- Bounded input is not an OS sandbox. Use trusted local JSON files and application-level plain JSON objects only. No arbitrary Python objects or hostile filesystem devices.

## Verification

Run the offline unittest suite and valid template CLI; require both successful exit status and expected metrics. Negative cases must reject malformed structure, budgets, references, cycles, and limits. Record actual test counts/output rather than inferring success from source inspection. [references/verification.md](references/verification.md) records the scoped local evidence.

This gate establishes bounded structural admission only. Bayesian success predictions, paper benchmark results, and successful local tests are distinct evidence categories; none authorizes autonomous agents or establishes production performance.
