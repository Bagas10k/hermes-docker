---
name: agent-bayesian-belief-calibration
description: Calibrate agent beliefs and quantify epistemic uncertainty.
version: 0.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bayesian, belief-calibration, uncertainty, KGRAPH-002]
    related_skills: [agent-causal-graph-reasoning, agent-kg-schema-morphing, cross-agent-knowledge-distillation]
---

# Bayesian Belief Calibration & Epistemic Uncertainty Quantification

Calibrate probability distributions over knowledge graph assertions, distinguish epistemic ignorance from aleatoric variance, and decay unverified assertions exponentially across agent sessions.

## When to Use

- Updating factual claims in knowledge graphs based on incoming tool observations.
- Quantifying epistemic uncertainty to prevent LLM hallucination and overconfidence.
- Deciding whether to run expensive verification probes via Net Value of Information (VOI).
- Decaying stale beliefs toward uninformative priors over time when unverified.
- Do not use for deterministic file integrity checks or cryptographic signatures.

## Prerequisites

Python 3.11+ standard library. Zero external dependencies required.

## Quick Reference

Calibrate beliefs using the CLI:
```bash
python3 scripts/belief_calibration_engine.py
```

Run unit tests:
```bash
python3 scripts/test_belief_calibration.py
```

## Procedure

1. **Register Assertion**:
   - Initialize proposition with uninformative prior $(\alpha=1.0, \beta=1.0)$ or domain prior.
   - Set claim half-life $t_{1/2}$ for cross-session decay.
2. **Ingest Empirical Observation**:
   - Apply temporal decay: excess evidence decays via $2^{-\Delta t / t_{1/2}}$.
   - Update pseudo-counts: $\alpha \leftarrow \alpha + w$ (supporting) or $\beta \leftarrow \beta + w$ (contradicting).
3. **Quantify Uncertainty**:
   - Epistemic uncertainty: $U_{\text{epistemic}} = \frac{1}{\alpha + \beta - (\alpha_0 + \beta_0) + 1} \in [0, 1]$.
   - Aleatoric uncertainty: $U_{\text{aleatoric}} = 4 \cdot \mathbb{E}[p] \cdot (1 - \mathbb{E}[p]) \in [0, 1]$.
4. **Evaluate Value of Information (VOI)**:
   - Calculate $\text{VOI}_{\text{net}} = U_{\text{epistemic}} \cdot \text{Power} - \text{Cost}$.
   - Only execute probe if $\text{VOI}_{\text{net}} > 0$.

## Pitfalls

- **Overconfidence from Zero Prior Variance**: Never set $\alpha=0$ or $\beta=0$; maintain proper prior regularization.
- **Premature Probe Triggering**: Probing facts with high aleatoric variance but low epistemic uncertainty wastes resources without resolving ambiguity.
- **Stale Belief Poisoning**: Always check timestamps before using cached assertions in high-stakes actions.

## Verification

Run the test suite to verify belief convergence, decay math, and VOI gating:
```bash
python3 scripts/test_belief_calibration.py
```
