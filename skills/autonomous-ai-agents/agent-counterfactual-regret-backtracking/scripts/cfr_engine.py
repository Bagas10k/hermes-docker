#!/usr/bin/env python3
"""
Counterfactual Regret Minimization (CFR) and Invariant State Backtracking Engine
for Autonomous Multi-Agent Task Execution.

Mathematical Formulations:
1. Instantaneous Regret:
   R^t(I, a) = u(I, a, \sigma^t_{-i}) - u(I, \sigma^t)
2. Cumulative Regret & Regret-Matching:
   R^{T,+}(I, a) = \max(0, \sum_{t=1}^T R^t(I, a))
   \sigma^{T+1}(I, a) = \frac{R^{T,+}(I, a)}{\sum_{b} R^{T,+}(I, b)}  (or uniform if sum == 0)
3. Invariant State Backtracking:
   Rollback to the nearest certified invariant state snapshot S_k when \Delta(S) violates hard predicate g(S) <= 0.
"""

import sys
import json
import copy
from typing import Dict, List, Any, Optional, Tuple, Set

class InvariantViolationError(Exception):
    pass

class StateSnapshot:
    def __init__(self, step_idx: int, state_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        self.step_idx = step_idx
        self.state_data = copy.deepcopy(state_data)
        self.metadata = metadata or {}

class CFRBacktrackingEngine:
    def __init__(self, invariant_predicates: Optional[List[str]] = None):
        """
        invariant_predicates: list of hard predicate expressions or keys that must hold true.
        """
        self.invariant_predicates = invariant_predicates or []
        self.snapshots: List[StateSnapshot] = []
        self.cumulative_regrets: Dict[str, Dict[str, float]] = {}  # info_set -> {action: regret}
        self.strategy_sums: Dict[str, Dict[str, float]] = {}       # info_set -> {action: weight}
        self.trajectory_history: List[Dict[str, Any]] = []

    def save_checkpoint(self, step_idx: int, state_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> int:
        """Saves a certified invariant state snapshot."""
        # Validate state invariants before checkpointing
        valid, reason = self.verify_invariants(state_data)
        if not valid:
            raise InvariantViolationError(f"Cannot save checkpoint at step {step_idx}: {reason}")
        
        snapshot = StateSnapshot(step_idx, state_data, metadata)
        self.snapshots.append(snapshot)
        return len(self.snapshots) - 1

    def verify_invariants(self, state_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Verifies hard invariants g(S) <= 0."""
        # Built-in hard safety invariants
        if state_data.get("fatal_error", False):
            return False, "Fatal error flag detected in state"
        if state_data.get("ram_usage_mb", 0) > 9000:
            return False, "RAM quota threshold exceeded (9000MB bound)"
        if state_data.get("data_corruption", False):
            return False, "State data corruption invariant violated"
        if state_data.get("security_breach", False):
            return False, "Security privilege boundary violation"
        return True, None

    def get_strategy(self, info_set: str, actions: List[str]) -> Dict[str, float]:
        """Calculates policy via Regret-Matching."""
        if info_set not in self.cumulative_regrets:
            self.cumulative_regrets[info_set] = {a: 0.0 for a in actions}
            self.strategy_sums[info_set] = {a: 0.0 for a in actions}

        positive_regrets = {a: max(0.0, self.cumulative_regrets[info_set].get(a, 0.0)) for a in actions}
        sum_pos = sum(positive_regrets.values())

        strategy = {}
        if sum_pos > 1e-9:
            for a in actions:
                strategy[a] = positive_regrets[a] / sum_pos
        else:
            # Uniform fallback
            uniform_prob = 1.0 / len(actions) if actions else 0.0
            for a in actions:
                strategy[a] = uniform_prob

        return strategy

    def update_regret(self, info_set: str, action_taken: str, actions: List[str], 
                      factual_utility: float, counterfactual_utilities: Dict[str, float]):
        """
        Updates cumulative regret for each action based on counterfactual difference:
        R(I, a) += u(I, a) - u(I, action_taken)
        """
        if info_set not in self.cumulative_regrets:
            self.cumulative_regrets[info_set] = {a: 0.0 for a in actions}
            self.strategy_sums[info_set] = {a: 0.0 for a in actions}

        for a in actions:
            u_cf = counterfactual_utilities.get(a, factual_utility)
            regret = u_cf - factual_utility
            self.cumulative_regrets[info_set][a] = self.cumulative_regrets[info_set].get(a, 0.0) + regret

        # Track strategy accumulation
        strat = self.get_strategy(info_set, actions)
        for a in actions:
            self.strategy_sums[info_set][a] = self.strategy_sums[info_set].get(a, 0.0) + strat.get(a, 0.0)

    def trigger_backtrack(self, current_step: int, corrupted_state: Dict[str, Any]) -> Tuple[StateSnapshot, int]:
        """
        Backtracks to the latest certified safe snapshot S_k (k < current_step),
        discarding corrupted state branches.
        """
        valid, reason = self.verify_invariants(corrupted_state)
        if valid:
            raise ValueError("State does not violate invariants; backtracking unprovoked.")

        if not self.snapshots:
            raise InvariantViolationError("No checkpoint snapshots available for backtracking.")

        # Find latest snapshot strictly before current corruption
        safe_snapshot = self.snapshots[-1]
        
        # Log backtracking event
        self.trajectory_history.append({
            "event": "BACKTRACK",
            "from_step": current_step,
            "restored_snapshot_step": safe_snapshot.step_idx,
            "reason": reason
        })
        return safe_snapshot, safe_snapshot.step_idx

    def get_average_strategy(self, info_set: str) -> Dict[str, float]:
        """Returns the long-term converged average policy."""
        if info_set not in self.strategy_sums:
            return {}
        sums = self.strategy_sums[info_set]
        total = sum(sums.values())
        if total > 1e-9:
            return {a: v / total for a, v in sums.items()}
        uniform = 1.0 / len(sums) if sums else 0.0
        return {a: uniform for a in sums}

if __name__ == "__main__":
    engine = CFRBacktrackingEngine()
    print("CFR & State Backtracking Engine initialized.")
