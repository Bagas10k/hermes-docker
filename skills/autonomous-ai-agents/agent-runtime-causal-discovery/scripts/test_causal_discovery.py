#!/usr/bin/env python3
"""
Unit Tests for Runtime Causal Graph Discovery & Do-Calculus Bounds
"""

import unittest
from causal_discovery_engine import CausalDiscoveryEngine, StructuralEquation

class TestCausalDiscoveryEngine(unittest.TestCase):
    def setUp(self):
        self.engine = CausalDiscoveryEngine(intervention_budget=4)

    def test_dag_cycle_prevention(self):
        """Invariant: Engine must reject edges that form cycles in the DAG."""
        self.assertTrue(self.engine.add_edge("X", "Y"))
        self.assertTrue(self.engine.add_edge("Y", "Z"))
        # Adding Z -> X forms a cycle X -> Y -> Z -> X
        self.assertFalse(self.engine.add_edge("Z", "X"))
        self.assertNotIn(("Z", "X"), self.engine.edges)

    def test_observation_ingestion_and_correlation(self):
        """Verify correlation computation across synthetic observation rows."""
        # Linear mechanism: Y = 2*X + 1
        for i in range(10):
            x = float(i)
            y = 2.0 * x + 1.0
            z = 5.0 # Uncorrelated constant
            self.engine.ingest_observation({"X": x, "Y": y, "Z": z})

        corr = self.engine.compute_correlation_matrix()
        # X and Y should have perfect positive correlation ~1.0
        self.assertAlmostEqual(corr["X"]["Y"], 1.0, places=4)
        self.assertAlmostEqual(corr["Y"]["X"], 1.0, places=4)

    def test_pruning_spurious_edges(self):
        """Verify constraint-based pruning drops weak correlation edges."""
        for i in range(10):
            x = float(i)
            y = 2.0 * x
            w = 10.0 if i % 2 == 0 else 10.1 # Very weak correlation
            self.engine.ingest_observation({"X": x, "Y": y, "W": w})

        self.engine.add_edge("X", "Y")
        self.engine.add_edge("X", "W")
        self.assertEqual(len(self.engine.edges), 2)

        pruned = self.engine.prune_spurious_edges(threshold=0.3)
        self.assertIn(("X", "Y"), self.engine.edges)
        self.assertNotIn(("X", "W"), self.engine.edges)
        self.assertEqual(pruned, 1)

    def test_pearl_hard_do_calculus(self):
        """
        Pearl's Hard Do-Calculus test:
        SCM:
        X (root, base = 10)
        Y = 2*X + 5
        Z = 3*Y - 4
        do(Y = 50) must sever X->Y, yielding Y=50 and Z = 3*(50) - 4 = 146.
        """
        scm = {
            "X": StructuralEquation("X", [], {}, intercept=10.0),
            "Y": StructuralEquation("Y", ["X"], {"X": 2.0}, intercept=5.0),
            "Z": StructuralEquation("Z", ["Y"], {"Y": 3.0}, intercept=-4.0)
        }
        res = self.engine.hard_do_intervention(target="Y", value=50.0, scm_equations=scm)
        self.assertEqual(res["Y"], 50.0)
        self.assertEqual(res["Z"], 146.0)
        self.assertEqual(self.engine.interventions_used, 1)

    def test_soft_shift_intervention(self):
        """
        Soft Shift Intervention:
        Baseline shifts, parents preserved:
        Y base shifted by +10.0: Y = 2*(10) + 5 + 10 = 35. Z = 3*35 - 4 = 101.
        """
        scm = {
            "X": StructuralEquation("X", [], {}, intercept=10.0),
            "Y": StructuralEquation("Y", ["X"], {"X": 2.0}, intercept=5.0),
            "Z": StructuralEquation("Z", ["Y"], {"Y": 3.0}, intercept=-4.0)
        }
        res = self.engine.soft_shift_intervention(target="Y", shift_delta=10.0, scm_equations=scm)
        self.assertEqual(res["X"], 10.0)
        self.assertEqual(res["Y"], 35.0)
        self.assertEqual(res["Z"], 101.0)

    def test_intervention_budget_exhaustion(self):
        """Verify strict intervention budget enforcement."""
        scm = {"X": StructuralEquation("X", [], {}, intercept=1.0)}
        engine = CausalDiscoveryEngine(intervention_budget=1)
        engine.hard_do_intervention("X", 2.0, scm)
        with self.assertRaises(RuntimeError):
            engine.hard_do_intervention("X", 3.0, scm)

    def test_consistency_verification_gate(self):
        """Verify consistency gate detects false mechanism vs true mechanism."""
        # Observations: Y = 2*X + 1
        for i in range(5):
            self.engine.ingest_observation({"X": float(i), "Y": 2.0 * float(i) + 1.0})

        true_scm = {"Y": StructuralEquation("Y", ["X"], {"X": 2.0}, intercept=1.0)}
        false_scm = {"Y": StructuralEquation("Y", ["X"], {"X": 5.0}, intercept=10.0)}

        ok_true, err_true = self.engine.verify_consistency("Y", true_scm, tolerance=0.1)
        ok_false, err_false = self.engine.verify_consistency("Y", false_scm, tolerance=0.1)

        self.assertTrue(ok_true)
        self.assertAlmostEqual(err_true, 0.0)
        self.assertFalse(ok_false)
        self.assertGreater(err_false, 5.0)

    def test_net_voi_selection(self):
        """Verify Net VOI prioritization for active intervention target selection."""
        for i in range(10):
            x = float(i)
            y = 2.0 * x
            self.engine.ingest_observation({"X": x, "Y": y})
        
        voi = self.engine.calculate_experiment_voi("X", "Y")
        self.assertGreater(voi, 0.0)

if __name__ == "__main__":
    unittest.main()
