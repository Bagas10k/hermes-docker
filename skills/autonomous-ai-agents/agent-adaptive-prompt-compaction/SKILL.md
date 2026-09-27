---
name: agent-adaptive-prompt-compaction
description: Prune prompt tokens adaptively and preserve KV prefix cache.
version: 0.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [prompt-compaction, token-allocation, kv-cache, KGRAPH-003]
    related_skills: [context-compaction-curator, agent-kv-cache-slicing, agent-prompt-grammar-optimizer]
---

# Adaptive Semantic Prompt Compaction & Dynamic Token Allocation

Prune redundant prompt tokens using Shannon information entropy, dynamically allocate budgets across memory/tool/history partitions, and guarantee 100% KV-cache prefix invariance.

## When to Use

- Context window usage approaches token budget limits in long-running agent workflows.
- Reducing Time-to-First-Token (TTFT) prefill latency via Amdahl-bounded prompt pruning.
- Preserving shared system prompt prefixes to maximize RadixAttention KV-cache hit rates.
- Dynamically partitioning token budgets across tools, memory facts, and turn history.
- Do not use for deterministic code diffs, cryptographic keys, or structured JSON payloads.

## Prerequisites

Python 3.11+ standard library. Zero external dependencies required.

## Quick Reference

Execute compaction probe via CLI:
```bash
python3 scripts/prompt_compactor_engine.py
```

Run test suite:
```bash
python3 scripts/test_prompt_compactor.py
```

## Procedure

1. **Lock System Prefix (KV-Cache Anchor)**:
   - Compute $\text{SHA256}(P)$ for the system prompt.
   - Lock prefix tokens as immutable to maintain 100% KV-cache reuse.
2. **Calculate Residual Budget**:
   - Determine remaining budget: $B_{\text{rem}} = B_{\text{total}} - L(P)$.
3. **Partition Dynamic Context**:
   - Allocate dynamic budgets using Knapsack weights: Tools (40%), Memory (35%), History (25%).
4. **Shannon Entropy Pruning**:
   - Calculate line-level entropy: $H(X) = -\sum p(c) \log_2 p(c)$.
   - Penalize repetitive unigram fingerprints and prune lowest-entropy lines.
5. **Verify Invariants**:
   - Confirm $\text{SHA256}(P_{\text{final}}) \equiv \text{SHA256}(P_{\text{initial}})$.
   - Verify final prompt token count $\le B_{\text{total}}$.

## Pitfalls

- **Prefix Mutation**: Modifying even 1 byte of the system prompt invalidates the entire KV-cache tree.
- **Aggressive Tool Truncation**: Over-pruning tool schema definitions causes schema validation failures.
- **Boilerplate Accumulation**: Repeating constraint sentences across turns balloons context without informational gain.

## Verification

Execute the test suite to verify prefix lock, Shannon entropy scoring, and budget bounds:
```bash
python3 scripts/test_prompt_compactor.py
```
