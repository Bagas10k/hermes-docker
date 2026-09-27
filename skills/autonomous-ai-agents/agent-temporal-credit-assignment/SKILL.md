---
name: agent-temporal-credit-assignment
description: Temporal credit assignment and trajectory step attribution.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [autonomous-agents, credit-assignment, trajectory-eval, counterfactual, amdhall-bottleneck, token-efficiency]
    related_skills: [agent-trajectory-evals, agent-causal-graph-reasoning, agent-continual-learning]
---

# Agent Temporal Credit Assignment Skill

Evaluates multi-step agent trajectories to assign accurate causal credit, isolate bottleneck tool calls, and eliminate token bloat loops.

## When to Use
- Attributing success or failure across long-horizon multi-step autonomous agent runs.
- Isolating which sub-agent or intermediate tool call caused a regression or unlock.
- Calculating Amdahl bottleneck latency contributions across distributed agent steps.
- Pruning negative credit actions from agent trajectory traces before handoff.

## Prerequisites
- Python 3.10+ standard library.
- Access to execution trajectories or structured action logs.

## Quick Reference
```bash
python3 ~/.hermes/skills/autonomous-ai-agents/agent-temporal-credit-assignment/scripts/credit_assignment_engine.py
```

## Procedure
1. **Collect Trajectory Trace**: Ingest sequential actions $(s_t, a_t, r_t, \text{duration\_ms})$.
2. **Compute Counterfactual Delta**: Evaluate marginal difference reward $D(a_t) = R(\tau) - R(\tau \setminus \{a_t\})$.
3. **Apply Temporal Decay**: Weight contribution by proximity to final state with decay factor $\gamma^{T-t}$.
4. **Identify Amdahl Bottlenecks**: Flag actions where latency contribution $p_t \ge 25\%$.
5. **Prune Negative Value Loops**: Extract steps with negative credit ($C(a_t) < -0.1$) to prevent error propagation.

## Pitfalls
- **Sparse Reward Fallacy**: Crediting only the terminal commit action while ignoring prerequisite discovery steps.
- **Confounding Parallel Tools**: Conflating parallel tool calls without counterfactual masking.
- **Latency Over-Optimization**: Penalizing thorough validation probes simply due to duration without weighting epistemic value.

## Verification
- Run the embedded test suite to confirm credit isolation, negative step identification, and Amdahl metrics:
```bash
python3 ~/.hermes/skills/autonomous-ai-agents/agent-temporal-credit-assignment/scripts/credit_assignment_engine.py
```
Indicates completion when self-test reports `Self-test passed: Temporal Credit Assignment invariants verified.`
