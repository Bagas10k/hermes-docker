---
name: autonomous-learning-supervisor
description: "Use when evaluating self-directed learning experiments."
version: 1.0.0
author: Bagas Cihuy & Hermes
license: MIT
metadata:
  hermes:
    tags: [learning-supervisor, benchmark, governance, fixed-oracle, baseline-vs-challenger, zero-regression]
---

# Autonomous Learning Supervisor & Capability Benchmark

Rigorous evaluation harness for autonomous learning cycles. Governs the boundary between the learning worker and the independent evaluation gate to prevent self-confirmation bias, hallucinated progress, and silent capability regressions.

## When to Use
- Running self-directed learning pipelines or curriculum batches (`/home/ubuntu/hermes-learning-engine/`).
- Validating whether a candidate patch or workflow improvement produces real measurable gains over historical baselines.
- Gating capability promotions into production configurations.

## Architecture: The 5-Domain Evaluation Matrix
Evaluates progress across five core operational competencies:
1. **Problem Solving:** Root-cause detection, input sanitation, and fail-fast resilience without error-swallowing.
2. **Decision Making:** Multi-criteria prioritization based on Net Value of Information (VOI), systemic impact, and reversibility.
3. **System Architecture:** Clean boundary separation, subpath ingress isolation, and container orchestration.
4. **Adaptive Reasoning:** Bayesian belief updating from empirical evidence without dogmatic assumptions.
5. **Autonomous Execution:** End-to-end task completion verified by deterministic exit codes (0) with zero human intervention.

## Governance Rules (Baseline vs Challenger Gate)
A candidate learning run (`challenger`) is approved for production promotion ONLY when it satisfies all three conditions:
1. **Minimum Performance Gain (+5%):** Absolute score increase must exceed +0.5 points (>= +5.0% relative gain) over the baseline. Marginal or zero-gain experiments are marked `REJECTED_KEEP_BASELINE`.
2. **Zero Regression:** No single domain score may drop below its historical baseline level.
3. **Independent Evaluation (Fixed Oracle):** The evaluation script (`evaluators/supervisor_evaluator.py`) must be executed by an isolated process whose assertions cannot be modified by the learning worker.

## Standard 9-Parameter Reporting Schema
Every completed learning cycle must generate an immutable report record:
```text
OBJECTIVE  : Specific deficit targeted
BASELINE   : Pre-training score and failure frequency
EXPERIMENT : Sandbox action performed
EVIDENCE   : Verified command output, exit codes, and timestamps
EVALUATION : Quantitative before-vs-after delta
REGRESSION : Verification status across legacy test suites
DECISION   : PROMOTED_TO_PRODUCTION | REJECTED_KEEP_BASELINE
NEXT ACTION: Next step or operational crystallization
```

## Operational Safety
- Keep learning pipelines in **Manual On-Demand** mode: execute only when explicitly triggered by the user.
- Maintain a persistent ledger in `reports/capability_evolution_ledger.jsonl` to track long-term capability trajectory.
