---
name: autonomous-learning-pipeline
description: Orchestrate 3-mode autonomous learning cycles in sandbox.
version: 0.1.0
author: Hermes Agent
license: MIT
related_skills:
  - subagent-lifecycle-management
  - comprehensive-agent-governance
  - autonomous-orchestrator
  - multi-agent-deliberation
metadata:
  hermes:
    tags:
      - AutonomousLearning
      - SelfDirectedLearning
      - SandboxEvaluation
      - KnowledgeGap
---

# Autonomous Learning Pipeline

Orchestrate self-directed agent learning cycles across three modalities: Error-Driven diagnosis, Knowledge-Gap scanning, and Frontier New Topic exploration. Evaluates all improvements against immutable independent supervisor assertions inside an isolated sandbox before production promotion.

## When to Use
- User asks to "jalankan pembelajaran mandiri", "/learn error", "/learn gap", "/learn new <topic>", or "/learn all".
- System experiences recurrent operational failures (3+ repeated errors in state logs).
- Auditing unproven doctrines or missing references in the Obsidian Knowledge Vault.

## Chat Telegram Shortcuts
Users trigger cycles directly from Telegram chat without terminal access:
- `/learn error` (or `!learn-error`, `belajar error`): Mode 1 Error-Driven diagnosis.
- `/learn gap` (or `!learn-gap`, `belajar gap`): Mode 2 Knowledge-Gap vault scan.
- `/learn new <topic>` (or `belajar hal baru <topic>`): Mode 3 Frontier New Topic exploration.
- `/learn all` (or `!learn-all`, `belajar semua`): Master dual run.

## Prerequisites
- Working directory: `/home/ubuntu/hermes-learning-engine`.
- Python 3.10+ runtime with `subprocess`, `argparse`, and `json` stdlib.
- Isolated sandbox root at `/home/ubuntu/hermes-learning-engine/sandbox/`.
- Knowledge Vault at `/home/ubuntu/otak-koding/KNOWLEDGE/`.

## How to Run
Invoke execution through the `terminal` tool using the unified CLI shortcut:
- Mode 1 (Error-Driven): `terminal(command="hermes-learn --error")`
- Mode 2 (Knowledge-Gap): `terminal(command="hermes-learn --gap")`
- Mode 3 (Frontier New): `terminal(command="hermes-learn --new '<topic>'")`
- Comprehensive Dual Audit: `terminal(command="hermes-learn --all")`

## Quick Reference
- Runner binary: `/home/ubuntu/.local/bin/hermes-learn`
- Engine orchestrator: `/home/ubuntu/hermes-learning-engine/run_learning_pipeline.py`
- Gap scanner: `/home/ubuntu/hermes-learning-engine/src/knowledge_gap_scanner.py`
- Sandbox logs & reports: `/home/ubuntu/hermes-learning-engine/reports/`

## Procedure

1. **Scan Deficit / Gap / New Topic:**
   - Mode 1: Parse `state.db` via `learning_analyzer.py` for failure clusters.
   - Mode 2: Run `knowledge_gap_scanner.py` against Obsidian Vault to flag `UNTESTED` doctrines or explicit `Gap:` annotations.
   - Mode 3: Web-search specifications, official RFCs, and industry reference code.

2. **Lock Curriculum & 3-Pillar Contract:**
   Write JSON schema into `curriculum/` defining:
   - Why it is important.
   - How to test it with 3-tier difficulty.
   - When it is considered successful (immutable assertion).

3. **Execute in Isolated Sandbox:**
   Run candidate patch or script inside `/tmp` or `sandbox/exp_<id>/` without modifying live production files.

4. **Independent Supervisor Gate:**
   Run immutable evaluator (`evaluators/eval_batch*.py`). If exit code is non-zero, fail immediately and roll back.

5. **Promote & Crystallize:**
   - Promote verified logic to live runtime.
   - Record formal 9-parameter report in `BUKU_CATATAN/` and index in `KNOWLEDGE/INDEX.md`.

## Pitfalls
- **Unconstrained 24/7 Looping:** Never run an unbounded continuous learning daemon; it induces catastrophic model drift and token exhaustion. Keep execution strictly manual on-demand or bounded event-driven.
- **Supervisor Tampering:** Never let the learning worker agent modify evaluation criteria or pass thresholds.
- **Silent Planning:** Never execute cycles silently; emit status updates and checklist markers within 60 seconds.

## Verification
Execute test run via `terminal`:
`hermes-learn --gap`
Verify that stdout returns `PROVEN_SUCCESS` and exit code 0 within <3 seconds.
