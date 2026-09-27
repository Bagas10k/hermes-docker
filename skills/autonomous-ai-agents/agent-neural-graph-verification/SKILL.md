---
name: agent-neural-graph-verification
description: Extract triplets and verify neural knowledge graphs.
version: 0.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [knowledge-graph, neural-graph, wikilinks, verification, KGRAPH-004]
    related_skills: [agent-kg-schema-morphing, agent-bayesian-belief-calibration, cross-agent-knowledge-distillation]
---

# Neural Knowledge Graph Triplet Extraction & Verification

Extract relational triplets from agent trajectories and markdown notes, audit Obsidian bidirectional wikilinks, prune spurious tautological cycles, and synthesize normalized 3D force coordinates for interactive neural graph visualization.

## When to Use

- Ingesting agent interaction trajectories into a structured relational knowledge base.
- Auditing Obsidian vault links to detect unidirectional links, broken references, or orphan nodes.
- Eliminating self-referential tautological loops and spurious cycles in knowledge graphs.
- Synthesizing degree centrality, cluster roles (hub, sink, source, bridge, orphan), and 3D coordinates.
- Do not use for raw unstructured vector embeddings or ephemeral scratchpad state.

## Prerequisites

- Python 3.10+ with standard library (`json`, `math`, `re`, `pathlib`, `dataclasses`).
- Access to markdown notes directory or Obsidian vault path (e.g. `/home/ubuntu/otak-koding/`).

## How to Run

Execute the verification engine against a document or directory of markdown notes:

```bash
python3 ~/.hermes/skills/autonomous-ai-agents/agent-neural-graph-verification/scripts/neural_graph_verifier.py
```

Run test suite:

```bash
python3 ~/.hermes/skills/autonomous-ai-agents/agent-neural-graph-verification/scripts/test_neural_graph_verifier.py
```

## Quick Reference

| Operation | Method / CLI Flag | Output / Artifact |
|---|---|---|
| Triplet Extraction | `extract_triplets_from_text(text, source_doc)` | List of `(subject, predicate, object, confidence)` |
| Wikilink Audit | `verify_bidirectional_wikilinks()` | Symmetric pair counts & unidirectional details |
| Orphan Detection | `detect_orphan_nodes()` | List of isolated nodes with `total_degree == 0` |
| Spurious Cycle Pruning | `eliminate_spurious_cycles()` | List of pruned tautological edges |
| 3D Graph Synthesis | `synthesize_3d_coordinates()` | JSON topology with `{nodes, edges, cluster, x, y, z}` |

## Procedure

1. **Extract Relational Triplets:**
   - Scan agent execution logs, markdown notes, and wikilink syntax `[[target]]`.
   - Parse directed syntax arrows (`A -> B`, `[[A]] --predicate--> [[B]]`) and semantic verb phrases.
   - Attach confidence scores ($c \ge 0.85$) and provenance metadata.

2. **Verify Bidirectional Obsidian Wikilinks:**
   - Construct adjacency list $A[u]$ and reverse adjacency $A^T[v]$.
   - Validate symmetry: identify forward links lacking backward reciprocity.
   - Flag broken references where the target does not resolve to an existing note.

3. **Detect Orphan Nodes & Disjoint Components:**
   - Compute in-degree $d_{	ext{in}}(v)$ and out-degree $d_{	ext{out}}(v)$ for all $v \in V$.
   - Isolate nodes where $d_{	ext{total}}(v) = 0$; allocate them to outer peripheral shells.

4. **Eliminate Spurious Cycles:**
   - Execute cycle detection on mutual edges sharing tautological predicates (e.g., `relates_to`).
   - Retain primary semantic direction and prune redundant reverse edges to maintain acyclic hierarchies where appropriate.

5. **Synthesize 3D Neural Topology:**
   - Distribute nodes using Fibonacci spherical mapping combined with degree-centrality gravity.
   - High-centrality hub nodes are positioned near coordinate origin ($r \le 100$), leaf nodes at intermediate radii, and orphans at outer shells ($r \ge 350$).
   - Export topological JSON payload ready for WebGL/Three.js or D3.js force rendering.

## Pitfalls

- **False Positive Verb Parsing:** Naive regex matching on common words can misidentify conversational prose as formal predicates. Limit verb phrase extraction to strict technical predicates (`implements`, `depends_on`, `calls`, `modifies`).
- **Wikilink Heading/Alias Stripping:** Obsidian links may contain anchor tags or pipe aliases (e.g. `[[Note#Heading|Alias]]`). Failure to clean anchors before matching causes target node key collisions.
- **Spherical Cluster Collapse:** When all nodes have identical degree, linear spherical projection can overlap. The engine applies the golden angle $\phi = \pi(3 - \sqrt{5})$ to guarantee uniform spatial dispersion.

## Verification

Run the deterministic test suite:

```bash
python3 ~/.hermes/skills/autonomous-ai-agents/agent-neural-graph-verification/scripts/test_neural_graph_verifier.py
```

Verification is successful when all 5 unit tests pass, verifying triplet extraction, link symmetry, orphan identification, cycle elimination, and 3D coordinate bounds.
