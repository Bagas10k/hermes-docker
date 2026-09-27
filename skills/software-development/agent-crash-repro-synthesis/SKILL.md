---
name: agent-crash-repro-synthesis
description: Deterministic crash reproduction and minimal repro synthesis.
version: 0.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [debugging, crash-reproduction, delta-debugging, synthesis, SELFHEAL-001]
    related_skills: [systematic-debugging, test-driven-development, mathematical-problem-solving]
---

# Deterministic Crash Reproduction Loops & Minimal Repro Synthesis

Extract structured crash signatures from execution failures, execute delta-debugging (ddmin) input minimization, eliminate non-deterministic flakiness, and synthesize self-contained standalone reproducer scripts.

## When to Use

- Isolating and synthesizing deterministic reproducers from production exceptions or test failures.
- Minimizing large inputs, JSON payloads, or stack traces down to a 1-minimal trigger subset.
- Verifying whether a bug is deterministic ($P(\text{crash}) = 1.0$) or intermittent/flaky.
- Guarding against false-positive reproducers that mutate the original crash fingerprint.
- Do not use for cosmetic visual inspection or unreproducible external network outages.

## Prerequisites

- Python 3.10+ standard library (`sys`, `os`, `re`, `subprocess`, `dataclasses`, `tempfile`).
- Target script or command capable of returning non-zero exit codes upon failure.

## How to Run

Execute the crash reproducer synthesis engine:

```bash
python3 ~/.hermes/skills/software-development/agent-crash-repro-synthesis/scripts/agent_crash_repro_synthesis.py
```

Run test suite:

```bash
python3 ~/.hermes/skills/software-development/agent-crash-repro-synthesis/scripts/test_agent_crash_repro_synthesis.py
```

## Quick Reference

| Operation | Method / CLI | Artifact / Invariant |
|---|---|---|
| Traceback Extraction | `parse_python_traceback(tb)` | Structured `CrashSignature` & fingerprint |
| Delta Minimization | `ddmin_minimize(items, oracle)` | 1-minimal subset of crash-inducing tokens |
| Repro Synthesis | `synthesize_minimal_repro(...)` | Reduction ratio metric & minimal payload |
| Standalone Script | `generate_repro_script(...)` | Executable `.py` returning 0 on exact crash |

## Procedure

1. **Extract Structured Crash Signature:**
   - Parse traceback text to capture exception type, root message, culprit file, and line number.
   - Formulate deterministic fingerprint: `ExceptionType@filename:line`.

2. **Execute Delta-Debugging Minimization (ddmin):**
   - Partition input lines or parameters into subsets and complements.
   - Run oracle evaluator against candidate subsets.
   - Narrow down inputs until removing any single element ceases to trigger the failure (1-minimality).

3. **Verify Fingerprint Preservation:**
   - Assert that the minimal candidate triggers the exact same fingerprint.
   - Reject candidates that trigger secondary errors (e.g. `IndexError` or `KeyError` due to truncated inputs).

4. **Verify Determinism & Reject Flakiness:**
   - Execute the candidate reproducer across $K \ge 5$ iterations.
   - Confirm $P(\text{crash} \mid c) = 1.0$. If variance is observed, quarantine as flaky.

5. **Synthesize Self-Contained Reproducer:**
   - Generate standalone Python script containing isolated repro logic.
   - Exit code 0 indicates deterministic crash reproduction; exit code 1 indicates crash disappeared.

## Pitfalls

- **Fingerprint Drift:** Minimization can easily produce an invalid syntax or malformed payload that triggers an unrelated crash. The oracle must strictly check `fingerprint_match == True`.
- **Flaky Environmental Dependencies:** Crashes dependent on wall-clock time, randomized hash seeds, or live network endpoints can yield $P(\text{crash}) < 1.0$. Always isolate external state with fixed mocks.
- **Cascading Secondary Failures:** Truncating multi-line code can cause syntax errors before reaching the bug. AST-aware tokenization or line-level validity guards must precede oracle execution.

## Verification

Run the deterministic test suite:

```bash
python3 ~/.hermes/skills/software-development/agent-crash-repro-synthesis/scripts/test_agent_crash_repro_synthesis.py
```

Verification is successful when all 5 unit tests pass, validating traceback extraction, ddmin minimization, reduction ratios $\ge 99\%$, generated script execution, and flakiness rejection.
