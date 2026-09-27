---
name: agent-prompt-grammar-optimizer
description: Use when optimizing agent prompts and output grammars.
version: 0.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [prompt-optimization, gepa, dspy, grammar, evaluation]
    related_skills: [agent-continual-learning, agent-trajectory-evals]
---

# Bounded Prompt and Grammar Optimization

Optimize task instructions and demonstrations without changing model weights or permission boundaries. Use DSPy/GEPA for proposals; use independent, deterministic evaluators for admission. This is a research-backed workflow, not evidence of a deployed or universally superior optimizer.

## When to Use
- Repeated agent tasks have labeled outcomes and a measurable failure mode.
- Compare instruction evolution, few-shot selection, or structured decoding under a fixed budget.
- Do not use to rewrite system policy, credentials, tool permissions, or safety invariants.

## Prerequisites
- Python 3.10+ for the offline admission helper; no network or third-party dependency required.
- For live optimization, install and pin `dspy` and its compatible `gepa` dependency in a dedicated virtual environment. Inspect installed signatures before copying examples.
- Authorized model endpoint and budget are required for live rollouts; never infer authorization from available credentials.
- Separate train, selection-validation, and untouched final-test partitions, grouped by task/source to prevent near-duplicate leakage.

## Quick Reference
Use `terminal(command="python <skill-dir>/scripts/promotion_gate.py --self-test")` for deterministic positive/negative admission tests.
Use `terminal(command="python <skill-dir>/scripts/promotion_gate.py report.json")` to inspect a measured report. Nonzero exit means rejected or invalid input. This helper does not generate prompts or measure model behavior.
Read [architecture and sources](references/architecture.md) before a live run.

## Procedure
1. Freeze the contract: version evaluator, dataset membership, immutable prefix, tool schema, model revision, and grammar acceptance rules. Exit: baseline manifest and rollback artifact exist.
2. Predict the intervention: change instructions OR demos OR grammar representation, not all simultaneously. Define smallest meaningful improvement and cost limits before observing results. Exit: signed-off experiment specification, including stop budget.
3. Choose the optimizer: MIPROv2 for joint instruction/demo search; GEPA for trajectory-informed reflection and complementary candidate search. Preserve the supplied term GEP but do not silently treat it as an established synonym for GEPA. Exit: exact algorithm and source identified.
4. Evaluate baseline on selection-validation. Keep train traces available for proposals; redact secrets and treat traces as untrusted data. Exit: per-example scores, invariant failures, token counts, elapsed time, and RSS recorded.
5. Run bounded proposals with official DSPy APIs. GEPA accepts scalar plus textual feedback; specify `max_metric_calls` rather than relying on an ambiguous preset. Bound concurrency, reflection tokens, wall time, and retries separately. Exit: every candidate has provenance and complete cost accounting.
6. Preserve the immutable system prefix and append candidate task instructions after it. Hash the actual serialized stable request prefix, including tools/schema where applicable. A grammar/schema edit can invalidate caching even if prompt prose is unchanged. Exit: prefix mismatch rejects automatic promotion; no claim of cache hits without provider telemetry.
7. Validate grammar syntax with the actual decoder/compiler, then positive/negative corpus cases, semantic validators, and refusal/truncation handling. Do not claim language equivalence from a finite corpus. Exit: unchanged authorization and application contract; candidate never changes evaluator acceptance rules.
8. Select on validation, freeze one finalist, then run final test once against the baseline under matched settings. Quantify uncertainty with paired task-level resampling or discordant-outcome tests; repeated tuning on this set invalidates its holdout status. Exit: lower confidence bound exceeds the predeclared margin, with no invariant or protected-slice regression.
9. Pass measured report to admission helper, then seek deployment authorization separately. Helper approval is necessary but not sufficient: human review, live backend grammar test, canary, and rollback remain required. Exit: versioned candidate retained; no automatic production write.

## Pitfalls
- GEPA means Genetic-Pareto; a generic GEP expansion is not a verified algorithm specification.
- Validation is part of optimization, not a pristine test set. Omitting GEPA `valset` permits train reuse and overfitting.
- Pareto complementarity across examples is not automatically a deployment Pareto frontier for cost and latency.
- Syntax-constrained output can still be false, malicious, or semantically invalid.
- Reflection-generated explanations are proposals, not proof of causality.
- Lower average latency can hide worse p95; include warm/cold-cache strata and timeouts.
- Stable prefix hashes detect drift, but do not prove cache residency or unchanged safety behavior.
- Missing metrics, nonfinite numbers, test overlap, and exhausted budgets fail closed.

## Verification
- Run the helper self-test; preserve actual output with the experiment record.
- Verify real grammar compilation and decoding separately; offline fixtures cannot establish backend compatibility.
- Report live-model results only after actual authorized calls. Distinguish measured gate correctness, paper-reported results, and untested production improvement.
- Do not mark a roadmap cycle complete until skill, reference, helper tests, vault note, and state references exist.
