#!/usr/bin/env python3
"""
Trajectory Self-Grading Engine & State Diff Verifier
Deterministic evaluator enforcing hard invariant gates, diff audits,
and Pareto trajectory efficiency ranking without LLM judge hallucination.
"""

import sys
import json
import hashlib
from typing import Dict, List, Any, Tuple, Optional

class InvariantType:
    FILE_EXISTS = "file_exists"
    FILE_SHA256 = "file_sha256"
    REGEX_MATCH = "regex_match"
    JSON_SCHEMA_VALID = "json_schema_valid"
    NUMERIC_BOUND = "numeric_bound"
    EXIT_CODE_ZERO = "exit_code_zero"
    NO_SIDE_EFFECT_OUTSIDE = "no_side_effect_outside"

class StepStatus:
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"
    NOOP = "noop"

class TrajectorySelfGrader:
    def __init__(self, workspace_root: str = "/"):
        self.workspace_root = workspace_root

    def verify_invariant(self, invariant: Dict[str, Any], context: Dict[str, Any]) -> Tuple[bool, str]:
        inv_type = invariant.get("type")
        target = invariant.get("target")
        expected = invariant.get("expected")

        if inv_type == InvariantType.EXIT_CODE_ZERO:
            actual = context.get("exit_code", -1)
            passed = (actual == 0)
            return passed, f"exit_code expected 0, got {actual}"

        elif inv_type == InvariantType.NUMERIC_BOUND:
            metric_val = context.get("metrics", {}).get(target)
            if metric_val is None:
                return False, f"metric {target} not found in context"
            min_val = invariant.get("min", float("-inf"))
            max_val = invariant.get("max", float("inf"))
            passed = min_val <= metric_val <= max_val
            return passed, f"metric {target}={metric_val} outside [{min_val}, {max_val}]"

        elif inv_type == InvariantType.NO_SIDE_EFFECT_OUTSIDE:
            modified_paths = context.get("modified_paths", [])
            allowed_prefixes = invariant.get("allowed_prefixes", [])
            violations = []
            for path in modified_paths:
                if not any(path.startswith(prefix) for prefix in allowed_prefixes):
                    violations.append(path)
            passed = len(violations) == 0
            return passed, f"unauthorized state mutations detected: {violations}" if not passed else "no side-effect outside allowed paths"

        elif inv_type == InvariantType.FILE_SHA256:
            actual_hash = context.get("file_hashes", {}).get(target)
            passed = (actual_hash == expected)
            return passed, f"file {target} sha256 expected {expected}, got {actual_hash}"

        return False, f"unknown invariant type: {inv_type}"

    def grade_trajectory(self, trajectory: Dict[str, Any], invariants: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Grades trajectory based on:
        1. Hard Invariant Pass Rate (g_i(x) <= 0) - If ANY fails, trajectory is INVALID.
        2. Execution Efficiency (Step count, tokens, latency).
        3. No-op / Redundant Step Ratio.
        """
        steps = trajectory.get("steps", [])
        context = trajectory.get("final_context", {})

        # 1. Evaluate Hard Invariants
        invariant_results = []
        all_passed = True
        for inv in invariants:
            passed, reason = self.verify_invariant(inv, context)
            invariant_results.append({
                "invariant": inv,
                "passed": passed,
                "reason": reason
            })
            if not passed:
                all_passed = False

        # 2. Step and Redundancy Metrics
        total_steps = len(steps)
        noop_steps = 0
        failed_steps = 0
        total_tokens = sum(s.get("tokens", 0) for s in steps)
        total_duration_ms = sum(s.get("duration_ms", 0) for s in steps)

        for step in steps:
            status = step.get("status")
            if status == StepStatus.NOOP:
                noop_steps += 1
            elif status == StepStatus.FAILURE:
                failed_steps += 1

        redundancy_rate = (noop_steps / total_steps) if total_steps > 0 else 0.0

        # 3. Efficiency Score: J(x) = (Invariant Score) * (1 - 0.5 * redundancy) / (1 + log(tokens/1000 + 1))
        # Note: If any invariant fails, overall grade is 0.0 (Hard gate constraint).
        if not all_passed:
            overall_score = 0.0
            grade = "REJECTED"
        else:
            efficiency_multiplier = (1.0 - 0.4 * redundancy_rate)
            overall_score = round(100.0 * efficiency_multiplier * (1.0 / (1.0 + (total_steps / 20.0))), 2)
            grade = "APPROVED" if overall_score >= 70.0 else "SUBOPTIMAL"

        return {
            "trajectory_id": trajectory.get("id", "unknown"),
            "grade": grade,
            "overall_score": overall_score,
            "all_invariants_passed": all_passed,
            "total_steps": total_steps,
            "noop_steps": noop_steps,
            "failed_steps": failed_steps,
            "redundancy_rate": round(redundancy_rate, 4),
            "total_tokens": total_tokens,
            "total_duration_ms": total_duration_ms,
            "invariant_results": invariant_results
        }

    def rank_trajectories(self, trajectories: List[Dict[str, Any]], invariants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ranks multiple candidate trajectories to evolve the policy toward Pareto optimal route.
        Valid trajectories sorted by score descending, then step count ascending.
        """
        graded = [self.grade_trajectory(t, invariants) for t in trajectories]
        # Sort key: all_invariants_passed (bool desc), overall_score desc, total_steps asc
        graded.sort(key=lambda x: (x["all_invariants_passed"], x["overall_score"], -x["total_steps"]), reverse=True)
        return graded

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: self_grader_engine.py <trajectory.json> [invariants.json]")
        sys.exit(1)

    with open(sys.argv[1], "r") as f:
        traj_data = json.load(f)

    inv_data = []
    if len(sys.argv) >= 3:
        with open(sys.argv[2], "r") as f:
            inv_data = json.load(f)

    grader = TrajectorySelfGrader()
    report = grader.grade_trajectory(traj_data, inv_data)
    print(json.dumps(report, indent=2))
