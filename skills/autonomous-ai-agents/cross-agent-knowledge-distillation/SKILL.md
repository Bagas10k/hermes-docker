---
name: cross-agent-knowledge-distillation
description: Absorb ephemeral sub-agent facts into durable memory.
version: 0.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [distillation, memory, meta-agent, offline, META-004]
    related_skills: [meta-agent-recursive-decomposition, subagent-concurrency-memory-bounds, multitier-safety-guardrails]
---

# Cross-Agent Knowledge Distillation & Ephemeral State Absorption

Absorb distilled atomic facts from ephemeral sub-agent trajectories into durable memory vaults. This is an offline deterministic distillation engine, not a live message bus. It prevents context bloat, scrubs raw credentials and terminal noise, resolves state mutations, and quarantines stable invariant collisions.

## When to Use

- Absorb insights and discovered environment facts from finished ephemeral sub-agents.
- Deduplicate knowledge across multiple worker executions with Bayesian corroboration.
- Prevent credential leaks, base64 data URIs, and ANSI escape sequences from reaching long-term storage.
- Quarantine conflicting assertions on stable architectural constants.
- Do not use for raw terminal streaming or live agent inter-process communication.

## Prerequisites

Python 3.11+ standard library. No external pip packages or network credentials required. Read [research](references/research.md).

## Quick Reference

Validate and distill a sub-agent payload against existing durable facts:
```bash
python3 scripts/cross_agent_distiller.py templates/sample_distillation_payload.json
```

Pass existing store to test updates and conflict detection:
```bash
python3 scripts/cross_agent_distiller.py payload.json --existing store.json
```

Run test suite:
```bash
python3 scripts/test_cross_agent_distiller.py
```

## Procedure

1. **Extract Atomic Candidates**: Require sub-agents to emit structured tuples (`subject`, `predicate`, `value`, `target_scope`, `confidence`, `relation_mode`) rather than raw conversation logs.
2. **Noise & Secret Scrubbing**: Run `sanitize_text` to strip ANSI escape codes, terminal progress bars, base64 data blocks, and redact API tokens/passwords.
3. **Identity Hashing**: Compute deterministic SHA-256 hash on `subject::predicate::target_scope` to identify unique atomic facts.
4. **Bayesian Corroboration**: If an existing identical fact is corroborated by an independent agent, update confidence via $P(H|E) = 1 - (1 - P_{\text{prior}}) \cdot (1 - P_{\text{new}} \cdot 0.5)$.
5. **State Evolution vs Quarantine**:
   - `relation_mode = 'mutable'`: supersede old value, archive prior state to `history[]` if $c_{\text{new}} \ge c_{\text{old}}$.
   - `relation_mode = 'stable'`: quarantine conflicting assertions into `quarantined_conflicts` without overwriting the verified invariant.

## Pitfalls

- **Silent Overwrites**: Overwriting stable constants (e.g. partition type or security boundary) without human review leads to corrupted knowledge graphs.
- **Log Dumping**: Storing unparsed sub-agent stdout wastes context budget and pollutes neural graph search.
- **False Corroboration**: Over-counting confidence when multiple sub-agents share identical biased inputs. The discount factor (0.5) bounds correlated consensus.

## Verification

Run the test suite verifying schema rejection, noise scrubbing, atomic deduplication, Bayesian confidence fusion, and invariant quarantine:
```bash
python3 scripts/test_cross_agent_distiller.py
```
Check exit code is 0 and all tests pass.
