---
name: multiagent-formal-verification
description: Use when verifying multi-agent protocol safety.
version: 0.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [agents, mpst, verification, protocols]
    related_skills: [agent-trajectory-evals, multiagent-consensus-circuit-breaker]
---

# Multi-Agent Formal Verification

Specify communication before connecting agents. Separate MPST theorem assumptions, bounded model exploration, and runtime trace evidence; none proves that an LLM's statements are true.

## When to Use
- Verify dispatcher/worker/reviewer handoffs, branching, cancellation, and message order.
- Investigate circular waits or orphan messages across asynchronous workers.
- Do not use as a substitute for authorization, factual verification, or arbitrary-code sandboxing.

## Prerequisites
- Python 3.10+ for the dependency-free finite FIFO explorer in `scripts/check_protocol.py`.
- Explicit roles, per-role state transitions, finite queue bound, and terminal states.
- For theorem-level MPST claims, select an actual calculus/toolchain and verify its assumptions; the helper is NOT an MPST compiler or proof assistant.
- Read `references/evidence.md` before asserting deadlock-freedom.

## Quick Reference
Use `terminal` from this skill directory:
- `python3 scripts/check_protocol.py model.json --bound 2 --max-states 100000`
- `python3 scripts/test_protocol.py`
The checker returns JSON; exit 0 means no stuck state within the complete finite exploration, 1 means a counterexample, 2 means incomplete exploration or invalid input.

## Procedure
1. Define roles and global choices. For `A -> B: label(T)`, project send to A, receive to B, and continuation to other roles. A role outside a branch must have mergeable continuations, or receive a discriminating branch notification. Completion: every role knows enough to make its next choice.
2. Declare transport assumptions: FIFO per ordered role pair, queue capacity/backpressure, reliable participants, crash detection, retry/replay policy, and fairness. Completion: no hidden assumption about remote availability.
3. Compile/check projections using the selected MPST toolchain for production. Pin tool version, retain commands and compiler results. Completion: exact theorem/property and unsupported constructs recorded. Never label handwritten FSM validation as successful MPST compilation.
4. Export a finite abstraction to the helper. Role format: `initial`, `final` list, `edges` list with `[source, send|recv, peer, label, target]`. Completion: terminal states have no edges and all peer roles exist.
5. Write predictions before running: valid handshake terminates; receive/receive circular wait gets a shortest counterexample; abandoned queue gets stuck; bounded-capacity send cycle gets stuck. Run different bounds without calling bounded results unbounded proofs. Completion: fixtures pass and all inspected state counts are retained.
6. At runtime enforce session ID, authenticated sender, protocol version, state transition, payload schema, and monotone sequence/idempotency keys before side effects. Commit durable transition and outbox atomically. Completion: invalid/replayed messages rejected without mutating state; actual integration tests required.
7. Model cancel/error/crash as protocol outcomes, not silent participant disappearance. Distinguish timeout suspicion from proven crash. Completion: failure traces reach documented terminal/compensation outcomes.
8. Report safety, termination, and liveness separately. Measure baseline and instrumented p50/p95/p99 on representative traces before claiming speedup. Completion: evidence scope and deployment approval stated.

## Pitfalls
- MPST communication safety is not semantic truth, privilege confinement, or prompt-injection immunity.
- Projection plus JSON schemas alone does not establish subject reduction, progress, or liveness.
- The finite explorer checks reachable stuck states, not fairness, livelock, arbitrary recursion, crash semantics, or unbounded queues.
- Queue bounds can introduce artificial backpressure deadlocks; do not discard the counterexample if the production queue is also bounded.
- Empty queues plus all roles terminal is success. A terminated receiver with unread messages is NOT success.
- Tool-enforced transport order must match the model; a global total-order log can falsely reject legitimate independent sends.
- Old notes claiming absolute deadlock-freedom, universal speedups, or numerical Bayesian posteriors without measured evidence are not prerequisites or proof.

## Verification
Run all helper fixtures; ensure valid and adversarial cases produce expected statuses. Keep counterexample steps, bounds, explored-state counts, sources, and missing production tests. A local test pass licenses only the finite explorer result, not a distributed deployment claim.
