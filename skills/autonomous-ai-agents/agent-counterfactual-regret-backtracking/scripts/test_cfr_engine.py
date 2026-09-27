#!/usr/bin/env python3
import unittest
import copy
from cfr_engine import CFRBacktrackingEngine, InvariantViolationError, StateSnapshot

class TestCFRBacktrackingEngine(unittest.TestCase):
    def setUp(self):
        self.engine = CFRBacktrackingEngine()

    def test_checkpoint_and_invariant_verification(self):
        # Normal safe state
        state = {"step": 1, "ram_usage_mb": 1200, "db_connected": True}
        idx = self.engine.save_checkpoint(1, state)
        self.assertEqual(idx, 0)
        self.assertEqual(len(self.engine.snapshots), 1)

        # Corrupted state must raise InvariantViolationError
        bad_state = {"step": 2, "fatal_error": True}
        with self.assertRaises(InvariantViolationError):
            self.engine.save_checkpoint(2, bad_state)

    def test_backtracking_on_invariant_violation(self):
        # Step 1: safe
        self.engine.save_checkpoint(1, {"step": 1, "ram_usage_mb": 1000, "files": ["main.py"]})
        # Step 2: safe
        self.engine.save_checkpoint(2, {"step": 2, "ram_usage_mb": 1500, "files": ["main.py", "utils.py"]})

        # Step 3: fatal invariant breach occurs
        corrupted_state = {"step": 3, "ram_usage_mb": 9500, "files": ["main.py", "corrupted.bin"]} # exceeds 9000MB bound
        snapshot, restored_step = self.engine.trigger_backtrack(3, corrupted_state)
        
        self.assertEqual(restored_step, 2)
        self.assertEqual(snapshot.state_data["files"], ["main.py", "utils.py"])
        self.assertEqual(len(self.engine.trajectory_history), 1)
        self.assertEqual(self.engine.trajectory_history[0]["event"], "BACKTRACK")

    def test_cfr_regret_matching_and_strategy_convergence(self):
        info_set = "STATE_TOOL_SELECTION"
        actions = ["TOOL_A", "TOOL_B", "TOOL_C"]

        # Initial policy should be uniform
        initial_strat = self.engine.get_strategy(info_set, actions)
        self.assertAlmostEqual(initial_strat["TOOL_A"], 1.0/3.0)
        self.assertAlmostEqual(initial_strat["TOOL_B"], 1.0/3.0)
        self.assertAlmostEqual(initial_strat["TOOL_C"], 1.0/3.0)

        # Simulate round 1: agent took TOOL_A with utility 0.2, but TOOL_B would have yielded 1.0, TOOL_C yielded -0.5
        cf_utils = {"TOOL_A": 0.2, "TOOL_B": 1.0, "TOOL_C": -0.5}
        self.engine.update_regret(info_set, "TOOL_A", actions, factual_utility=0.2, counterfactual_utilities=cf_utils)

        # Regret for TOOL_B is 1.0 - 0.2 = 0.8
        # Regret for TOOL_A is 0.0
        # Regret for TOOL_C is -0.7 (clamped to 0 in regret-matching)
        new_strat = self.engine.get_strategy(info_set, actions)
        self.assertAlmostEqual(new_strat["TOOL_B"], 1.0)
        self.assertAlmostEqual(new_strat["TOOL_A"], 0.0)
        self.assertAlmostEqual(new_strat["TOOL_C"], 0.0)

    def test_average_strategy_convergence(self):
        info_set = "SUBAGENT_DISPATCH"
        actions = ["DISPATCH_PARALLEL", "SERIAL_EXECUTE"]

        # 10 rounds of updates where DISPATCH_PARALLEL dominates
        for _ in range(10):
            strat = self.engine.get_strategy(info_set, actions)
            cf_utils = {"DISPATCH_PARALLEL": 2.0, "SERIAL_EXECUTE": 0.5}
            self.engine.update_regret(info_set, "SERIAL_EXECUTE", actions, 0.5, cf_utils)

        avg_strat = self.engine.get_average_strategy(info_set)
        self.assertGreater(avg_strat["DISPATCH_PARALLEL"], 0.8)
        self.assertLess(avg_strat["SERIAL_EXECUTE"], 0.2)

if __name__ == "__main__":
    unittest.main()
