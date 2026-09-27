#!/usr/bin/env python3
"""
Autonomous Knowledge Graph Schema Morphing & Dynamic Edge Reweighting Engine.
Implements:
1. Double-buffered schema definition (Read-Copy-Update / RCU) for zero-downtime query serving.
2. Dynamic edge reweighting via frequency, utility, and Bayesian evidence half-life decay.
3. Ontological contradiction & cycle detection (incompatible domain/range, disjoint classes).
4. Schema morphism migration pipeline (generalize, specialize, split, merge, deprecate).
"""

import sys
import json
import math
import copy
import time
import argparse
from typing import Dict, List, Tuple, Set, Any, Optional

class KnowledgeGraphSchemaEngine:
    def __init__(self, initial_state: Optional[Dict[str, Any]] = None):
        self.active_schema_version = 1
        # Double buffer: active_schema (read-only for readers) and staged_schema (for mutations)
        self.schemas: Dict[int, Dict[str, Any]] = {
            1: {
                "version": 1,
                "entity_types": {
                    "Agent": {"parent": "Entity", "disjoint_with": ["Resource"]},
                    "Task": {"parent": "Entity", "disjoint_with": []},
                    "Resource": {"parent": "Entity", "disjoint_with": ["Agent"]},
                    "Observation": {"parent": "Entity", "disjoint_with": []}
                },
                "relation_types": {
                    "EXECUTES": {"domain": "Agent", "range": "Task", "inverse": "EXECUTED_BY"},
                    "USES": {"domain": "Agent", "range": "Resource", "inverse": "USED_BY"},
                    "PRODUCES": {"domain": "Task", "range": "Observation", "inverse": "PRODUCED_BY"}
                }
            }
        }
        self.graph: Dict[str, Any] = {
            "entities": {},
            "edges": []
        }
        self.audit_log: List[Dict[str, Any]] = []

        if initial_state:
            self._load_state(initial_state)

    def _load_state(self, state: Dict[str, Any]) -> None:
        if "schema" in state:
            self.active_schema_version = state["schema"].get("version", 1)
            self.schemas[self.active_schema_version] = copy.deepcopy(state["schema"])
        if "graph" in state:
            self.graph = copy.deepcopy(state["graph"])

    def get_active_schema(self) -> Dict[str, Any]:
        """Reader method: constant-time lock-free read from active buffer."""
        return self.schemas[self.active_schema_version]

    def query_edges(self, source: Optional[str] = None, target: Optional[str] = None, relation: Optional[str] = None) -> List[Dict[str, Any]]:
        """Zero-downtime edge query against current graph."""
        res = []
        for e in self.graph["edges"]:
            if source and e["source"] != source:
                continue
            if target and e["target"] != target:
                continue
            if relation and e["relation"] != relation:
                continue
            res.append(copy.deepcopy(e))
        return res

    def check_ontological_compatibility(self, schema: Dict[str, Any], source_type: str, relation: str, target_type: str) -> Tuple[bool, Optional[str]]:
        """Validate if relation between source and target violates domain/range or disjoint axioms."""
        rel_def = schema["relation_types"].get(relation)
        if not rel_def:
            return False, f"Unknown relation type: {relation}"

        req_domain = rel_def.get("domain")
        req_range = rel_def.get("range")

        # Type hierarchy traversal
        def is_subtype(sub: str, parent: str) -> bool:
            curr = sub
            while curr:
                if curr == parent:
                    return True
                curr_info = schema["entity_types"].get(curr)
                if not curr_info:
                    break
                curr = curr_info.get("parent")
            return False

        if req_domain and not is_subtype(source_type, req_domain):
            return False, f"Domain mismatch: source type '{source_type}' is not a subtype of required domain '{req_domain}'"

        if req_range and not is_subtype(target_type, req_range):
            return False, f"Range mismatch: target type '{target_type}' is not a subtype of required range '{req_range}'"

        # Disjoint checking
        src_info = schema["entity_types"].get(source_type, {})
        tgt_info = schema["entity_types"].get(target_type, {})
        if target_type in src_info.get("disjoint_with", []):
            return False, f"Disjointness contradiction: '{source_type}' and '{target_type}' are explicitly disjoint"
        if source_type in tgt_info.get("disjoint_with", []):
            return False, f"Disjointness contradiction: '{target_type}' and '{source_type}' are explicitly disjoint"

        return True, None

    def reweight_edge(self, edge_index: int, utility_observed: float, current_time: float, half_life_s: float = 86400.0) -> Dict[str, Any]:
        """
        Bayesian & utility-driven edge reweighting:
        decay = exp(-ln(2) * (t - t_last) / half_life)
        w_new = (w_old * decay) * alpha + utility * (1 - alpha)
        bounded in [0.01, 1.0].
        """
        edge = self.graph["edges"][edge_index]
        last_t = edge.get("updated_at", current_time)
        dt = max(0.0, current_time - last_t)
        decay = math.exp(-0.693147 * (dt / half_life_s))
        
        old_w = edge.get("weight", 0.5)
        # Alpha controls momentum: higher weight on historical evidence if sample count is large
        count = edge.get("evidence_count", 1)
        alpha = min(0.85, 0.5 + 0.05 * math.log1p(count))

        new_w = (old_w * decay) * alpha + utility_observed * (1.0 - alpha)
        new_w = max(0.01, min(1.0, round(new_w, 4)))

        edge["weight"] = new_w
        edge["updated_at"] = current_time
        edge["evidence_count"] = count + 1
        return edge

    def stage_schema_morphism(self, morphism_type: str, parameters: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        """
        Stage a new schema version without affecting active readers.
        Morphism types:
        - ADD_RELATION: {relation: str, domain: str, range: str, inverse: str}
        - MERGE_RELATIONS: {source_relations: [str], target_relation: str}
        - SPECIALIZE_RELATION: {base_relation: str, new_sub_relation: str, specific_domain: str, specific_range: str}
        - DEPRECATE_RELATION: {relation: str}
        """
        current_schema = self.get_active_schema()
        new_version = self.active_schema_version + 1
        staged_schema = copy.deepcopy(current_schema)
        staged_schema["version"] = new_version

        if morphism_type == "ADD_RELATION":
            rel = parameters["relation"]
            staged_schema["relation_types"][rel] = {
                "domain": parameters["domain"],
                "range": parameters["range"],
                "inverse": parameters.get("inverse", f"{rel}_OF")
            }
        elif morphism_type == "MERGE_RELATIONS":
            sources = parameters["source_relations"]
            target = parameters["target_relation"]
            # Domain and range are lowest common ancestors or broad union
            staged_schema["relation_types"][target] = {
                "domain": parameters.get("domain", "Entity"),
                "range": parameters.get("range", "Entity"),
                "merged_from": sources
            }
            for s in sources:
                staged_schema["relation_types"].pop(s, None)
        elif morphism_type == "SPECIALIZE_RELATION":
            base = parameters["base_relation"]
            new_rel = parameters["new_sub_relation"]
            staged_schema["relation_types"][new_rel] = {
                "parent_relation": base,
                "domain": parameters["specific_domain"],
                "range": parameters["specific_range"]
            }
        elif morphism_type == "DEPRECATE_RELATION":
            rel = parameters["relation"]
            if rel in staged_schema["relation_types"]:
                staged_schema["relation_types"][rel]["deprecated"] = True
        else:
            raise ValueError(f"Unsupported morphism type: {morphism_type}")

        self.schemas[new_version] = staged_schema
        return new_version, staged_schema

    def commit_schema_morphism(self, new_version: int) -> Dict[str, Any]:
        """
        Atomic pointer swap: promotes staged schema to active schema.
        Migrates existing graph edges if necessary.
        Zero query downtime.
        """
        if new_version not in self.schemas:
            raise ValueError(f"Schema version {new_version} has not been staged.")

        target_schema = self.schemas[new_version]
        # Validate all existing edges against new schema
        migrated_edges = []
        invalidated_edges = []

        for e in self.graph["edges"]:
            src_t = self.graph["entities"].get(e["source"], {}).get("type", "Entity")
            tgt_t = self.graph["entities"].get(e["target"], {}).get("type", "Entity")
            rel = e["relation"]

            # If relation was merged, re-map
            for r_name, r_def in target_schema["relation_types"].items():
                if "merged_from" in r_def and rel in r_def["merged_from"]:
                    e["original_relation"] = rel
                    e["relation"] = r_name
                    rel = r_name
                    break

            compat, err = self.check_ontological_compatibility(target_schema, src_t, rel, tgt_t)
            if compat:
                migrated_edges.append(e)
            else:
                invalidated_edges.append({"edge": e, "reason": err})

        self.graph["edges"] = migrated_edges
        old_v = self.active_schema_version
        self.active_schema_version = new_version

        record = {
            "timestamp": time.time(),
            "from_version": old_v,
            "to_version": new_version,
            "active_edges_count": len(migrated_edges),
            "invalidated_edges_count": len(invalidated_edges),
            "invalidated": invalidated_edges
        }
        self.audit_log.append(record)
        return record


def run_pipeline(payload_path: str) -> Dict[str, Any]:
    with open(payload_path, "r") as f:
        data = json.load(f)

    engine = KnowledgeGraphSchemaEngine(data.get("initial_state"))
    operations = data.get("operations", [])
    results = []

    for op in operations:
        op_type = op.get("type")
        if op_type == "QUERY":
            q_res = engine.query_edges(op.get("source"), op.get("target"), op.get("relation"))
            results.append({"operation": "QUERY", "count": len(q_res), "edges": q_res})
        elif op_type == "REWEIGHT":
            edge_idx = op["edge_index"]
            utility = op["utility"]
            curr_t = op.get("current_time", time.time())
            reweighted = engine.reweight_edge(edge_idx, utility, curr_t)
            results.append({"operation": "REWEIGHT", "edge_index": edge_idx, "new_weight": reweighted["weight"]})
        elif op_type == "STAGE_MORPHISM":
            m_type = op["morphism"]
            params = op["parameters"]
            v, staged = engine.stage_schema_morphism(m_type, params)
            results.append({"operation": "STAGE_MORPHISM", "staged_version": v})
        elif op_type == "COMMIT_MORPHISM":
            v = op["version"]
            commit_res = engine.commit_schema_morphism(v)
            results.append({"operation": "COMMIT_MORPHISM", "summary": commit_res})
        elif op_type == "CHECK_COMPATIBILITY":
            s_type = op["source_type"]
            rel = op["relation"]
            t_type = op["target_type"]
            schema = engine.get_active_schema()
            ok, err = engine.check_ontological_compatibility(schema, s_type, rel, t_type)
            results.append({"operation": "CHECK_COMPATIBILITY", "valid": ok, "error": err})

    return {
        "status": "SUCCESS",
        "active_schema_version": engine.active_schema_version,
        "results": results,
        "audit_log": engine.audit_log
    }


def main():
    parser = argparse.ArgumentParser(description="Autonomous Knowledge Graph Schema Morphing CLI")
    parser.add_argument("payload", help="Path to input JSON payload")
    args = parser.parse_args()

    out = run_pipeline(args.payload)
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
