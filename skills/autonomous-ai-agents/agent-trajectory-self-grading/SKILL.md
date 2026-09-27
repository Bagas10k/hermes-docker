---
name: agent-trajectory-self-grading
description: Self-grade agent trajectories with hard invariants.
version: 0.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [trajectory-evals, self-grading, hard-invariants, pareto-ranking, self-evolution]
    related_skills: [agent-trajectory-evals, agent-reflexion-memory-pruning, agent-continual-learning]
---

# Agent Trajectory Self-Grading

Evaluate and rank multi-step agent trajectories using deterministic state diffs, exit codes, and hard invariant checks. This eliminates reliance on hallucinatory LLM judges and guides trajectory evolution toward Pareto-optimal routes.

## When to Use
- Evaluating completed multi-step agent trajectories before committing state changes.
- Selecting the most efficient trajectory among speculative execution candidates.
- Detecting token bloat loops, redundant no-op steps, or unauthorized filesystem mutations.
- Don't use for subjective creative writing scoring or unconstrained free-form chat.

## Prerequisites
- Python 3.10+ standard library.
- Declared hard invariant constraints (`invariants.json`) and trajectory metadata (`trajectory.json`).
- Access to deterministic test oracles (exit codes, checksums, numeric metric thresholds).

## Quick Reference
Use `terminal` with the skill directory as working directory:
- `python scripts/test_self_grader.py` runs deterministic unit tests.
- `python scripts/self_grader_engine.py trajectory.json invariants.json` grades a trajectory and outputs a structured JSON report.
- Read [architecture](references/architecture.md) for mathematical formulation and Pareto ranking.

## Procedure
1. **Define hard invariant constraints.** Specify acceptance criteria ($g_i(x) \le 0$) such as `exit_code_zero`, `file_sha256`, `numeric_bound`, and `no_side_effect_outside`.
2. **Capture trajectory trace.** Record every execution step: tool call, execution status (`success`, `failure`, `noop`), duration in ms, and token footprint.
3. **Execute deterministic audit.** Run `self_grader_engine.py` against the trajectory context. Complete when all hard invariants are evaluated without relying on LLM-as-a-judge.
4. **Enforce fail-closed gate.** If any hard invariant fails, immediately reject the trajectory ($Score = 0.0$, Status = `REJECTED`).
5. **Calculate trajectory efficiency.** For passing trajectories, compute the redundancy ratio ($N_{\text{noop}} / N_{\text{total}}$) and token cost discount.
6. **Evolve policy route.** Compare candidate trajectories using `rank_trajectories` and retain the shortest Pareto-optimal path for crystallization into procedural memory.

## Pitfalls
- A verbal assertion of success by the agent is not evidence; only state diffs and oracles count.
- Never average a safety invariant failure with high efficiency; safety constraints are non-negotiable hard boundaries.
- Beware of no-op loops where the agent calls redundant read/search tools without progressing task state.
- Invariant validation must run locally in sub-millisecond execution, avoiding expensive external API roundtrips.

## Verification
- Run `python -m unittest discover -s scripts` to verify all invariant checks, violation rejections, and Pareto trajectory rankings pass 100%.
