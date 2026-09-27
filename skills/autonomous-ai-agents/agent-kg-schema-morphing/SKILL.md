---
name: agent-kg-schema-morphing
description: Evolve knowledge graph schemas and reweight edges.
version: 0.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [knowledge-graph, schema-morphing, reweighting, KGRAPH-001]
    related_skills: [cross-agent-knowledge-distillation, agent-causal-graph-reasoning, agent-hierarchical-memory]
---

# Autonomous Knowledge Graph Schema Morphing & Dynamic Edge Reweighting

Evolve relational knowledge schemas dynamically without query downtime and reweight edge confidence based on empirical evidence and temporal decay. This skill implements a double-buffered (RCU-style) schema migration pipeline, Bayesian utility reweighting, and ontological constraint checking to prevent contradictory assertions in agentic knowledge graphs.

## When to Use

- Adapt an agent's relational knowledge schema when encountering new domain concepts.
- Perform zero-downtime schema migrations (relation specialization, merging, or deprecation).
- Dynamically decay stale graph connections and amplify actively verified edge weights.
- Prevent contradictory triples by enforcing domain, range, and disjointness axioms.
- Do not use for unstructured raw vector embeddings or ephemeral scratchpad state.

## Prerequisites

Python 3.11+ standard library. No external pip dependencies or database credentials required. Detailed formal foundations in [research](references/research.md).

## Quick Reference

Run the schema morphing and reweighting engine on a JSON payload:
```bash
python3 scripts/schema_morphing_engine.py templates/sample_morphing_payload.json
```

Execute unit tests:
```bash
python3 -m unittest scripts/test_schema_morphing.py
```

## Procedure

1. **Schema Inspection & Querying**:
   - Query entities and relations against the lock-free active buffer (`get_active_schema()`).
   - Validate that readers always see consistent, immutable snapshots during ongoing modifications.
2. **Ontological Compatibility Checking**:
   - Before admitting a new edge, check if `(source_type, relation, target_type)` satisfies declared domain and range constraints.
   - Enforce disjointness axioms; reject contradictory relationships with fail-closed errors.
3. **Dynamic Edge Reweighting**:
   - Update edge confidence weights via Bayesian utility and half-life decay:
     $$w_{new} = (w_{old} \cdot e^{-\lambda \Delta t}) \cdot \alpha + U(e) \cdot (1 - \alpha)$$
   - Bound confidence scores strictly within $[0.01, 1.0]$.
4. **Staging Schema Morphisms**:
   - Stage a proposed schema mutation (`ADD_RELATION`, `MERGE_RELATIONS`, `SPECIALIZE_RELATION`, `DEPRECATE_RELATION`) into version $N+1$.
   - The active version $N$ remains untouched for concurrent query operations.
5. **Atomic Commit & Graph Migration**:
   - Validate existing edges against the staged schema version.
   - Atomically swap the active schema version pointer to $N+1$.
   - Re-map or invalidate non-conforming historical edges, recording mutations in the audit log.

## Pitfalls

- **Synchronous Locking Bottleneck**: Never place global write locks on the knowledge graph during ontology restructuring; use double-buffering (RCU) to maintain $O(1)$ query availability.
- **Premature Edge Deletion**: Avoid hard-deleting edges when utility drops; allow them to decay toward lower bounds so historical provenance is preserved for counterfactual reasoning.
- **Cyclic Schema Inheritance**: Ensure entity type inheritance remains an acyclic directed tree to avoid infinite recursion during subtype resolution.

## Verification

Run the test suite to verify zero-downtime morphism staging, edge reweighting, and ontological vetoes:
```bash
python3 -m unittest scripts/test_schema_morphing.py
```
All tests must report `OK` with zero warnings.
