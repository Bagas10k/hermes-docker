---
name: agent-visual-trajectory-correction
description: Use when verifying visual action trajectories safely.
version: 0.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [vision, trajectory, verification, offline]
    related_skills: [agent-multimodal-hybrid-grounding]
---

# Visual Trajectory Correction — VISION-004

A bounded offline decision gate for temporal verification after a possibly dispatched action. Extends VISION-003 geometry admission with action correlation, semantic readback, reconciliation and terminal-state discipline. It never clicks, sleeps, fetches, or claims task completion from image differences.

## When to Use

- Decide whether to observe, reconcile, or propose a bounded retry after GUI input.
- Test stale observations, ambiguous outcomes and delayed responses before integration.
- Do not use as an autonomous payment, publish, delete, credential or native input driver.

## Prerequisites

- Python 3.10+ standard library; no network, packages, credentials or model required.
- Trusted serialized adapter supplies one monotonic clock, unique logical action identity, attempt number, context epoch, target and semantic predicate identity.
- Read [technical research](references/technical-research.md) for evidence trust and dispatch boundaries. Load `agent-multimodal-hybrid-grounding` for geometry; do not recalculate its transforms here.

## Quick Reference

Use `terminal` with the resolved skill scripts directory as `workdir`:

```text
python3 -B -m unittest discover -s . -p 'test_*.py' -v
```

- [scripts/trajectory.py](scripts/trajectory.py): `Tracker(...).step(observation, now=...)` returns a decision string.
- [scripts/test_trajectory.py](scripts/test_trajectory.py): executable synthetic examples and adversarial tests.
- Decisions: `OBSERVE`, `RECONCILE`, `RETRY`, `SUCCESS`, `STOP`, `STOP_RECONCILE`.
- `RETRY` is a consumed attempt reservation, NOT input dispatch permission. Obtain fresh VISION-003 admission and authorization separately before any dispatch.

## Procedure

1. Before dispatch, bind the authorized intent to a unique action, context epoch, target and predicate; define authoritative semantic readback and a global deadline. Finish with explicit idempotency, not a guessed property of a button.
2. Create one tracker at the dispatch boundary, conservatively treating the first attempt as possibly sent. Preserve this tracker; do not reset budgets or identity after timeouts. Completion: one in-flight action and bounded policy.
3. Collect read-only evidence for the exact attempt. Page text, animation, visual change, transport ACK and unrelated success toast are not authoritative business state. Completion: typed observation or missing evidence.
4. Call `step` under serialization. Discard stale, future, pre-dispatch, duplicate, out-of-order and wrong-context evidence. Unknown outcomes request reconciliation, never blind replay. Completion: decision recorded with original action/attempt identity.
5. Reconcile by querying the authoritative receipt/resource/audit state, never by clicking the action again. A non-idempotent action never auto-retries in this implementation, even with reported no-effect. Completion: confirmed predicate or terminal handoff.
6. For `RETRY`, re-authorize and re-ground; reservation already advanced the attempt counter and observation floor. Dispatch at most once for that reservation. Any delay or dispatch uncertainty requires readback; do not reuse stale geometry. Completion: adapter ledger records the reserved attempt, including not-sent/unknown.
7. Terminal outcomes are absorbing. `STOP_RECONCILE` means unresolved effect, not failure or cancellation of the remote operation. Stop scheduling this tracker and hand off a bounded record for manual/read-only reconciliation. Completion: no terminal replay or budget reset.

## Pitfalls

- A semantic false condition does not prove no effect; only an authoritative `absent` result may propose an idempotent retry.
- Context includes application/tab/document or navigation epoch plus tenant/workflow scope. Unexpected navigation forces reconciliation; expected navigation needs a predeclared adapter correlation mapping, not accepting any new page.
- Fresh evidence is not authenticated evidence. This helper cannot prevent a malicious adapter from forging a boolean or correlation token.
- No wall-clock mixing, page-provided policy, generic numeric confidence, unbounded screenshots/history, or repeat-until-success loops.
- The portable stdlib helper is tested on Linux only; listed platforms express code portability, not verified desktop integration.

## Verification

Require unittest exit zero and inspect semantic, ambiguity, freshness, budget and terminal tests. Status is **TESTED_OFFLINE_ONLY**. Fixtures are synthetic and do not measure browser latency, detector accuracy, RSS or production safety. Live integration still requires dispatch journaling, crash recovery, authenticated readback, race tests and sandbox fault injection. No scheduler state changes belong to this skill.
