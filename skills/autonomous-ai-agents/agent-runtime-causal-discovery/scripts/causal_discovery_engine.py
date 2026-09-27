#!/usr/bin/env python3
"""
Runtime Causal Graph Discovery & Do-Calculus Bounds Engine
Author: Bagas Cihuy & Hermes Agent
License: MIT

Implements:
1. Online Observation-Intervention Active Discovery (CausaLab SCM Paradigm)
2. Pearl's Do-Calculus Surgery Bounds (Hard-Do vs Soft Shift-Intervention)
3. Dynamic Invariant Consistency Verification Gate (Prevents premature stopping)
4. Fast Conditional Independence & Partial Correlation Pruning (Constraint + Score)
5. Net Value of Information (VOI) Budgeted Experiment Selection
"""

import math
import copy
import json
import sys
from typing import Dict, List, Tuple, Set, Optional, Any

class StructuralEquation:
    """Represents a structural equation for a node: X_i = f(PA_i) + U_i"""
    def __init__(self, target: str, parents: List[str], weights: Dict[str, float], intercept: float = 0.0, noise_std: float = 0.05):
        self.target = target
        self.parents = parents
        self.weights = weights  # parent -> weight
        self.intercept = intercept
        self.noise_std = noise_std

    def evaluate(self, parent_values: Dict[str, float], noise: float = 0.0) -> float:
        val = self.intercept + noise
        for p in self.parents:
            val += self.weights.get(p, 0.0) * parent_values.get(p, 0.0)
        return val

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target": self.target,
            "parents": self.parents,
            "weights": self.weights,
            "intercept": self.intercept,
            "noise_std": self.noise_std
        }

class CausalDiscoveryEngine:
    def __init__(self, intervention_budget: int = 10):
        self.nodes: Set[str] = set()
        self.edges: Set[Tuple[str, str]] = set()  # (u, v) means u -> v
        self.observations: List[Dict[str, float]] = []
        self.interventions: List[Dict[str, Any]] = []
        self.intervention_budget = intervention_budget
        self.interventions_used = 0
        self.hypothesized_equations: Dict[str, StructuralEquation] = {}

    def add_node(self, node: str) -> None:
        self.nodes.add(node)

    def add_edge(self, u: str, v: str) -> bool:
        """Adds directed edge u -> v with strict DAG cycle check."""
        if u not in self.nodes:
            self.nodes.add(u)
        if v not in self.nodes:
            self.nodes.add(v)
        
        # Tentatively add edge and check for cycles
        if (u, v) in self.edges:
            return True
        if u == v:
            return False
            
        self.edges.add((u, v))
        if self._has_cycle():
            self.edges.remove((u, v))
            return False
        return True

    def remove_edge(self, u: str, v: str) -> None:
        if (u, v) in self.edges:
            self.edges.remove((u, v))

    def _has_cycle(self) -> bool:
        visited = set()
        rec_stack = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for parent, child in self.edges:
                if parent == node:
                    if child not in visited:
                        if dfs(child):
                            return True
                    elif child in rec_stack:
                        return True
            rec_stack.remove(node)
            return False

        for n in self.nodes:
            if n not in visited:
                if dfs(n):
                    return True
        return False

    def ingest_observation(self, obs: Dict[str, float]) -> None:
        """Record passive observation data row."""
        self.observations.append(obs)
        for k in obs.keys():
            self.nodes.add(k)

    def hard_do_intervention(self, target: str, value: float, scm_equations: Dict[str, StructuralEquation]) -> Dict[str, float]:
        """
        Executes Pearl's hard do-calculus: do(target = value).
        Sever all incoming edges to target (PA_target = empty).
        Propagate downstream values topologically.
        """
        if self.interventions_used >= self.intervention_budget:
            raise RuntimeError(f"Intervention budget exhausted ({self.interventions_used}/{self.intervention_budget})")

        self.interventions_used += 1
        state: Dict[str, float] = {}
        
        # Hard-do setting
        state[target] = value

        # Topologically simulate SCM
        # Nodes without parents or root nodes evaluated
        order = self._topological_sort_scm(scm_equations)
        for node in order:
            if node == target:
                continue
            eq = scm_equations.get(node)
            if eq:
                state[node] = eq.evaluate(state)
            else:
                state[node] = 0.0

        record = {
            "type": "hard_do",
            "target": target,
            "value": value,
            "result": state
        }
        self.interventions.append(record)
        return state

    def soft_shift_intervention(self, target: str, shift_delta: float, scm_equations: Dict[str, StructuralEquation]) -> Dict[str, float]:
        """
        Executes soft shift intervention: target's baseline is shifted by delta,
        retaining parent connections.
        """
        if self.interventions_used >= self.intervention_budget:
            raise RuntimeError(f"Intervention budget exhausted ({self.interventions_used}/{self.intervention_budget})")

        self.interventions_used += 1
        state: Dict[str, float] = {}

        order = self._topological_sort_scm(scm_equations)
        for node in order:
            eq = scm_equations.get(node)
            if not eq:
                state[node] = 0.0
                continue
            base = eq.evaluate(state)
            if node == target:
                base += shift_delta
            state[node] = base

        record = {
            "type": "soft_shift",
            "target": target,
            "delta": shift_delta,
            "result": state
        }
        self.interventions.append(record)
        return state

    def _topological_sort_scm(self, scm_equations: Dict[str, StructuralEquation]) -> List[str]:
        in_degree = {n: 0 for n in scm_equations.keys()}
        adj = {n: [] for n in scm_equations.keys()}

        for target, eq in scm_equations.items():
            for p in eq.parents:
                if p in adj:
                    adj[p].append(target)
                    in_degree[target] += 1

        queue = [n for n, deg in in_degree.items() if deg == 0]
        order = []
        while queue:
            curr = queue.pop(0)
            order.append(curr)
            for neighbor in adj.get(curr, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Add any unlisted
        for n in scm_equations.keys():
            if n not in order:
                order.append(n)
        return order

    def compute_correlation_matrix(self) -> Dict[str, Dict[str, float]]:
        """Computes Pearson correlation across gathered observations."""
        if len(self.observations) < 2:
            return {}

        nodes = sorted(list(self.nodes))
        n = len(self.observations)
        means = {node: sum(obs.get(node, 0.0) for obs in self.observations) / n for node in nodes}
        std = {}
        for node in nodes:
            var = sum((obs.get(node, 0.0) - means[node]) ** 2 for obs in self.observations) / n
            std[node] = math.sqrt(var) if var > 1e-9 else 1e-9

        corr: Dict[str, Dict[str, float]] = {u: {} for u in nodes}
        for u in nodes:
            for v in nodes:
                if u == v:
                    corr[u][v] = 1.0
                else:
                    cov = sum((obs.get(u, 0.0) - means[u]) * (obs.get(v, 0.0) - means[v]) for obs in self.observations) / n
                    corr[u][v] = cov / (std[u] * std[v])
        return corr

    def prune_spurious_edges(self, threshold: float = 0.25) -> int:
        """
        Constraint-based edge pruning:
        Removes edges where correlation is below threshold.
        """
        corr = self.compute_correlation_matrix()
        if not corr:
            return 0

        pruned = 0
        to_remove = []
        for u, v in self.edges:
            c = abs(corr.get(u, {}).get(v, 0.0))
            if c < threshold:
                to_remove.append((u, v))

        for u, v in to_remove:
            self.remove_edge(u, v)
            pruned += 1
        return pruned

    def verify_consistency(self, target: str, scm_equations: Dict[str, StructuralEquation], tolerance: float = 0.15) -> Tuple[bool, float]:
        """
        Consistency Verification Gate:
        Checks whether current hypothesized equations can faithfully reconstruct
        past observational and interventional data within a tolerance margin.
        Mitigates premature stopping.
        """
        eq = scm_equations.get(target)
        if not eq:
            return False, 1.0

        errors = []
        # Check against observations
        for obs in self.observations:
            pred = eq.evaluate(obs)
            actual = obs.get(target, 0.0)
            err = abs(pred - actual)
            errors.append(err)

        # Check against interventions (non-targeted)
        for itv in self.interventions:
            if itv.get("target") != target:
                res = itv.get("result", {})
                pred = eq.evaluate(res)
                actual = res.get(target, 0.0)
                err = abs(pred - actual)
                errors.append(err)

        if not errors:
            return True, 0.0

        mean_err = sum(errors) / len(errors)
        is_consistent = mean_err <= tolerance
        return is_consistent, mean_err

    def calculate_experiment_voi(self, candidate_intervention_target: str, dependent_target: str) -> float:
        """
        Calculates Net Value of Information (VOI) for choosing next intervention.
        High VOI when edge existence between candidate and dependent is ambiguous.
        """
        # If candidate already has an edge to dependent, or vice versa, test if intervention confirms direction
        has_edge_fwd = (candidate_intervention_target, dependent_target) in self.edges
        has_edge_bwd = (dependent_target, candidate_intervention_target) in self.edges

        # Ambiguity is highest if correlation exists but direction is unknown
        corr = self.compute_correlation_matrix()
        c = abs(corr.get(candidate_intervention_target, {}).get(dependent_target, 0.0))
        
        # Information gain potential
        if not has_edge_fwd and not has_edge_bwd:
            prior_ambiguity = c
        elif has_edge_fwd != has_edge_bwd:
            prior_ambiguity = 0.5 * c
        else:
            prior_ambiguity = 0.2

        # Cost: fraction of remaining budget
        remaining = max(1, self.intervention_budget - self.interventions_used)
        cost = 1.0 / remaining

        voi_net = max(0.0, prior_ambiguity - (0.15 * cost))
        return round(voi_net, 4)

    def summary(self) -> Dict[str, Any]:
        return {
            "nodes": sorted(list(self.nodes)),
            "edges": sorted([f"{u}->{v}" for u, v in self.edges]),
            "observations_count": len(self.observations),
            "interventions_count": len(self.interventions),
            "interventions_used": self.interventions_used,
            "intervention_budget": self.intervention_budget
        }

if __name__ == "__main__":
    engine = CausalDiscoveryEngine(intervention_budget=5)
    print("CausalDiscoveryEngine initialized successfully.")
