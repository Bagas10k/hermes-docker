import unittest
from causal_simulator_engine import CausalObservabilitySimulator


class TestCausalObservabilitySimulator(unittest.TestCase):
    def setUp(self):
        # Setup pipeline agen otonom standar:
        # Trigger -> Planner -> (Researcher || Executor) -> Evaluator -> Responder
        self.sim = CausalObservabilitySimulator(ram_limit_mb=9000.0, max_latency_ceiling_ms=15000.0)
        self.sim.add_node("TRIGGER", base_latency_ms=50.0, base_ram_mb=100.0, base_cost_usd=0.0)
        self.sim.add_node("PLANNER", base_latency_ms=1200.0, base_ram_mb=500.0, base_cost_usd=0.002)
        self.sim.add_node("RESEARCHER", base_latency_ms=3000.0, base_ram_mb=800.0, base_cost_usd=0.005)
        self.sim.add_node("EXECUTOR", base_latency_ms=2500.0, base_ram_mb=1200.0, base_cost_usd=0.004)
        self.sim.add_node("EVALUATOR", base_latency_ms=800.0, base_ram_mb=400.0, base_cost_usd=0.001)
        self.sim.add_node("RESPONDER", base_latency_ms=200.0, base_ram_mb=150.0, base_cost_usd=0.0005)

        self.sim.add_causal_edge("TRIGGER", "PLANNER")
        self.sim.add_causal_edge("PLANNER", "RESEARCHER")
        self.sim.add_causal_edge("PLANNER", "EXECUTOR")
        self.sim.add_causal_edge("RESEARCHER", "EVALUATOR")
        self.sim.add_causal_edge("EXECUTOR", "EVALUATOR")
        self.sim.add_causal_edge("EVALUATOR", "RESPONDER")

    def test_topological_sort_and_dag_invariance(self):
        order = self.sim.topological_sort()
        self.assertEqual(order[0], "TRIGGER")
        self.assertEqual(order[-1], "RESPONDER")
        self.assertLess(order.index("PLANNER"), order.index("RESEARCHER"))
        self.assertLess(order.index("PLANNER"), order.index("EXECUTOR"))

    def test_cycle_rejection(self):
        with self.assertRaises(ValueError):
            self.sim.add_causal_edge("RESPONDER", "TRIGGER")

    def test_critical_path_computation(self):
        res = self.sim.compute_critical_path()
        # Jalur kritis: TRIGGER (50) + PLANNER (1200) + max(RESEARCHER 3000, EXECUTOR 2500) + EVALUATOR (800) + RESPONDER (200)
        # = 50 + 1200 + 3000 + 800 + 200 = 5250 ms
        self.assertEqual(res["total_latency_ms"], 5250.0)
        self.assertEqual(res["critical_path"], ["TRIGGER", "PLANNER", "RESEARCHER", "EVALUATOR", "RESPONDER"])
        self.assertEqual(res["peak_ram_mb"], 3150.0)

    def test_do_intervention_pearl_surgery(self):
        # Intervensi do(RESEARCHER latency = 1000ms via cache hit)
        cf_res = self.sim.simulate_do_intervention({
            "RESEARCHER": {"latency_ms": 1000.0}
        })
        # Sekarang EXECUTOR (2500ms) menjadi jalur kritis baru!
        # Total latency = 50 + 1200 + 2500 + 800 + 200 = 4750 ms
        self.assertEqual(cf_res["total_latency_ms"], 4750.0)
        self.assertEqual(cf_res["critical_path"], ["TRIGGER", "PLANNER", "EXECUTOR", "EVALUATOR", "RESPONDER"])

    def test_invariant_bounds_and_ram_headroom(self):
        base_res = self.sim.compute_critical_path()
        inv_base = self.sim.evaluate_invariant_bounds(base_res)
        self.assertTrue(inv_base["passed"])
        self.assertFalse(inv_base["ram_breached"])
        self.assertFalse(inv_base["latency_breached"])

        # Intervensi yang memicu breach RAM (misal model local 8000MB)
        cf_breach = self.sim.simulate_do_intervention({
            "EXECUTOR": {"ram_mb": 7500.0}
        })
        inv_breach = self.sim.evaluate_invariant_bounds(cf_breach)
        self.assertFalse(inv_breach["passed"])
        self.assertTrue(inv_breach["ram_breached"])

    def test_amdahl_speedup_calculation(self):
        # Amdahl speedup jika RESEARCHER dipercepat 10x
        speedup = self.sim.compute_amdahl_theoretical_speedup("RESEARCHER", 10.0)
        # p = 3000 / 5250 = ~0.5714
        # S = 1 / ((1 - 0.5714) + 0.5714/10) = 1 / (0.4286 + 0.05714) = 1 / 0.48574 = ~2.0587
        self.assertGreater(speedup, 1.8)
        self.assertLess(speedup, 2.3)


if __name__ == "__main__":
    unittest.main()
