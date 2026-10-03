---
name: agent-nash-allocation
description: Use when allocating agents via bounded Nash games.
version: 0.1.0
author: Bagas Cihuy, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [nash, congestion-games, allocation, starvation]
    related_skills: [agent-game-mechanisms, subagent-concurrency-memory-bounds]
---

# Bounded Nash Allocation

Allocate one resource choice per agent in a finite singleton congestion game. This is a research reference implementation, not a truthful auction, token-payment ledger, or production scheduler.

## When to Use
- Evaluate congestion-aware resource choices with time-decaying shared rewards.
- Require a unilateral-regret certificate instead of assuming a solver converged.
- Reserve bounded FIFO service independently of selfish resource choices.
- Do not use to claim arbitrary auction convergence, truthful bidding, or Byzantine resistance.

## Prerequisites
Python 3.11+ standard library. No installation, network, credentials, or production services required. Locate this skill's directory with `skill_view`; use its `scripts/` as working directory.

## How to Run
Through `terminal`, execute `python3 -m unittest -v test_nash_allocation` and `python3 nash_allocation.py --demo` with working directory set to this skill's `scripts/` directory. Windows may use `python`.

## Model and Bounds
At a frozen epoch t, resource reward is R_r(t)=R_r0 exp(-d_r t). Each agent i chooses one resource a_i and receives u_i=R_a(t)/n_a-c_i,a. Costs are fixed per agent/resource; all agents share each resource's reward equally.

The exact potential is Phi(a)=sum_r R_r(t) H(n_r)-sum_i c_i,a_i. Every unilateral move changes Phi by exactly that player's utility change in real arithmetic. Strict sequential best responses therefore terminate on the finite state space; simultaneous changes or time updates invalidate this proof. There are m^n states, so this is not a polynomial-time convergence guarantee.

`Game.solve` caps updates and separately computes maximum unilateral regret. `converged` means only regret <= supplied tolerance in floating-point arithmetic: an epsilon-Nash certificate, not necessarily an exact equilibrium. Do not confuse this tolerance with a stopping rule: the solver still performs every strictly improving move until stable or capped.

Memory is O(n*m) for the immutable cost matrix plus O(n+m) working state. A full sweep and certificate cost O(n*m). A coarse cap-U runtime bound is O((U+1)*n*m). No measured latency or speedup promise. Apply Amdahl only after measuring solver's fraction of end-to-end runtime.

## Procedure
1. Define resource reward units, nonnegative private costs, decay rate units, and epoch. Confirm each agent has exactly one valid choice.
2. Construct `Game(rewards, decays, costs, epoch=...)`. Inputs are copied into immutable tuples; values must be finite, nonnegative, <=1e100; at most 1024 agents/resources.
3. Call `solve(actions=None, max_updates=10000, tolerance=1e-12)`. Validate its regret, update count, actions and epoch before using allocations. Reject uncertified output when equilibrium is a hard requirement.
4. Reconstruct the game at the next epoch instead of mutating rewards inside a solve. Re-certify each new epoch; no online tracking theorem is claimed.
5. For starvation protection, create `ReserveScheduler(k, capacity)`, call `admit(job_id)` and handle `admitted`, `duplicate`, or `full`. Call consecutive `tick(t)` starting at zero; every K ticks dequeues one oldest waiting job. Other ticks return None for a caller-owned policy.
6. Treat dequeue as a dispatch proposal, not completion. The K*q waiting bound for admitted rank q assumes persistent ticks and one service quantum per dequeue. Add an acknowledged executor and failure recovery before production adoption.
7. Run deterministic tests and CLI before recording local verification. Keep sources, mathematical argument and test evidence distinct.

## Pitfalls
- Nash equilibrium does not imply truthfulness, welfare optimality or fairness.
- A decreasing priority score alone can worsen starvation; use an explicit reserve, not an unproved aging heuristic.
- FIFO reserve and game are separate policies. Reserve interventions may change the game; the equilibrium certificate covers only the solved snapshot.
- Deduplication covers waiting IDs only. Served IDs can be re-admitted; there is no durable exactly-once execution.
- Full queues reject explicitly. Guarantees exclude rejected jobs, unbounded execution times, failed workers and concurrent mutation.
- Exponential underflow produces zero reward. Floating-point certificates are not interval proofs; the hard update cap remains necessary.
- Numeric dimension limits do not imply acceptable p95 latency at maximum dimensions. Benchmark target hardware before integration.

## Verification
The scripts contain seven deterministic unittest cases covering exact-potential deviations, exhaustive small states, regret, capped nonconvergence, immutable epochs, nonfinite input rejection, underflow, FIFO waiting bounds during new arrivals, queue admission and CLI JSON. `scripts/verification.txt` preserves the initial RED/GREEN transcript; parent reruns must independently verify output.

## Sources
- Tim Roughgarden, *Potentials and Approximation (2008 Shapley Lecture)*: https://theory.stanford.edu/~tim/talks/shapley.pdf — potential arguments, harmonic sharing and congestion games.
- Rosenthal (1973), *A class of games possessing pure-strategy Nash equilibria*, DOI 10.1007/BF01737559 — bibliographic provenance; full original paper not inspected in this cycle.

The reward-maximizing specialization and FIFO bound are derived here, not attributed as a combined algorithm to either source.
