#!/usr/bin/env python3
import unittest
import json
from self_grader_engine import TrajectorySelfGrader, InvariantType, StepStatus

class TestTrajectorySelfGrader(unittest.TestCase):
    def setUp(self):
        self.grader = TrajectorySelfGrader()

    def test_hard_invariant_exit_code_pass(self):
        inv = [{"type": InvariantType.EXIT_CODE_ZERO}]
        traj = {
            "id": "traj-001",
            "steps": [{"action": "run_test", "status": StepStatus.SUCCESS, "tokens": 150, "duration_ms": 200}],
            "final_context": {"exit_code": 0}
        }
        res = self.grader.grade_trajectory(traj, inv)
        self.assertTrue(res["all_invariants_passed"])
        self.assertEqual(res["grade"], "APPROVED")
        self.assertGreater(res["overall_score"], 80.0)

    def test_hard_invariant_exit_code_fail(self):
        inv = [{"type": InvariantType.EXIT_CODE_ZERO}]
        traj = {
            "id": "traj-fail",
            "steps": [{"action": "run_test", "status": StepStatus.FAILURE, "tokens": 150, "duration_ms": 200}],
            "final_context": {"exit_code": 1}
        }
        res = self.grader.grade_trajectory(traj, inv)
        self.assertFalse(res["all_invariants_passed"])
        self.assertEqual(res["grade"], "REJECTED")
        self.assertEqual(res["overall_score"], 0.0)

    def test_side_effect_containment_violation(self):
        inv = [{
            "type": InvariantType.NO_SIDE_EFFECT_OUTSIDE,
            "allowed_prefixes": ["/home/ubuntu/workspace/"]
        }]
        traj = {
            "id": "traj-leak",
            "steps": [{"action": "write", "status": StepStatus.SUCCESS, "tokens": 100}],
            "final_context": {
                "modified_paths": ["/home/ubuntu/workspace/app.py", "/etc/passwd"]
            }
        }
        res = self.grader.grade_trajectory(traj, inv)
        self.assertFalse(res["all_invariants_passed"])
        self.assertEqual(res["grade"], "REJECTED")
        self.assertIn("unauthorized state mutations", res["invariant_results"][0]["reason"])

    def test_numeric_metric_bound(self):
        inv = [{
            "type": InvariantType.NUMERIC_BOUND,
            "target": "latency_p95_ms",
            "min": 0,
            "max": 100
        }]
        traj_pass = {
            "id": "traj-p95-ok",
            "steps": [{"status": StepStatus.SUCCESS, "tokens": 100}],
            "final_context": {"metrics": {"latency_p95_ms": 42.5}}
        }
        traj_fail = {
            "id": "traj-p95-slow",
            "steps": [{"status": StepStatus.SUCCESS, "tokens": 100}],
            "final_context": {"metrics": {"latency_p95_ms": 142.0}}
        }
        res_pass = self.grader.grade_trajectory(traj_pass, inv)
        res_fail = self.grader.grade_trajectory(traj_fail, inv)
        self.assertTrue(res_pass["all_invariants_passed"])
        self.assertFalse(res_fail["all_invariants_passed"])

    def test_trajectory_evolution_ranking(self):
        inv = [{"type": InvariantType.EXIT_CODE_ZERO}]
        # Trajectory A: 2 steps, 0 no-op
        traj_a = {
            "id": "traj-efficient",
            "steps": [
                {"status": StepStatus.SUCCESS, "tokens": 100},
                {"status": StepStatus.SUCCESS, "tokens": 100}
            ],
            "final_context": {"exit_code": 0}
        }
        # Trajectory B: 10 steps, 4 no-op
        traj_b = {
            "id": "traj-bloated",
            "steps": [
                {"status": StepStatus.SUCCESS, "tokens": 100},
                {"status": StepStatus.NOOP, "tokens": 100},
                {"status": StepStatus.NOOP, "tokens": 100},
                {"status": StepStatus.NOOP, "tokens": 100},
                {"status": StepStatus.NOOP, "tokens": 100},
                {"status": StepStatus.SUCCESS, "tokens": 100}
            ],
            "final_context": {"exit_code": 0}
        }
        # Trajectory C: Failed invariant
        traj_c = {
            "id": "traj-broken",
            "steps": [{"status": StepStatus.SUCCESS, "tokens": 50}],
            "final_context": {"exit_code": 2}
        }

        ranked = self.grader.rank_trajectories([traj_b, traj_c, traj_a], inv)
        self.assertEqual(ranked[0]["trajectory_id"], "traj-efficient")
        self.assertEqual(ranked[1]["trajectory_id"], "traj-bloated")
        self.assertEqual(ranked[2]["trajectory_id"], "traj-broken")
        self.assertGreater(ranked[0]["overall_score"], ranked[1]["overall_score"])

if __name__ == "__main__":
    unittest.main()
