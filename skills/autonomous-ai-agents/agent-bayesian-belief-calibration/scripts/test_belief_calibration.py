#!/usr/bin/env python3
import unittest
import time
from belief_calibration_engine import BayesianBeliefEngine

class TestBayesianBeliefEngine(unittest.TestCase):
    def setUp(self):
        self.engine = BayesianBeliefEngine(prior_alpha=1.0, prior_beta=1.0, default_half_life=100.0)

    def test_uninformative_prior(self):
        res = self.engine.register_claim("fact-1", "Database port is 5432")
        self.assertEqual(res["expected_probability"], 0.5)
        self.assertEqual(res["epistemic_uncertainty"], 1.0)
        self.assertEqual(res["status"], "UNCERTAIN_INSUFFICIENT_EVIDENCE")

    def test_positive_evidence_accumulation(self):
        self.engine.register_claim("fact-2", "API returns 200 OK")
        # Add 10 positive observations
        res = self.engine.update_evidence("fact-2", evidence_type="supporting", weight=10.0)
        self.assertGreater(res["expected_probability"], 0.90)
        self.assertLess(res["epistemic_uncertainty"], 0.15)
        self.assertEqual(res["status"], "VERIFIED_HIGH_CONFIDENCE")

    def test_contradictory_evidence_decay(self):
        self.engine.register_claim("fact-3", "Cache hit ratio > 80%")
        # 10 negative observations
        res = self.engine.update_evidence("fact-3", evidence_type="contradicting", weight=10.0)
        self.assertLess(res["expected_probability"], 0.10)
        self.assertEqual(res["status"], "REFUTED_HIGH_CONFIDENCE")

    def test_temporal_decay(self):
        t0 = 1000.0
        self.engine.register_claim("fact-4", "Service alive", timestamp=t0)
        self.engine.update_evidence("fact-4", evidence_type="supporting", weight=10.0, current_time=t0)
        
        # After 1 half-life (100 seconds later)
        res_half = self.engine.get_belief("fact-4", current_time=t0 + 100.0)
        # Excess was 10.0, decayed by 50% -> excess is 5.0 -> alpha = 1.0 + 5.0 = 6.0, beta = 1.0
        self.assertAlmostEqual(res_half["alpha"], 6.0, places=2)
        self.assertAlmostEqual(res_half["beta"], 1.0, places=2)
        
        # After many half-lives (e.g. 1000s) -> decays back to uninformative prior (1.0, 1.0)
        res_decayed = self.engine.get_belief("fact-4", current_time=t0 + 1000.0)
        self.assertAlmostEqual(res_decayed["alpha"], 1.0, places=1)
        self.assertAlmostEqual(res_decayed["beta"], 1.0, places=1)
        self.assertEqual(res_decayed["status"], "UNCERTAIN_INSUFFICIENT_EVIDENCE")

    def test_value_of_information(self):
        self.engine.register_claim("fact-5", "Subsystem latency < 50ms")
        voi_high = self.engine.compute_value_of_information("fact-5", probe_cost=0.1)
        self.assertTrue(voi_high["should_probe"])
        self.assertEqual(voi_high["recommendation"], "EXECUTE_PROBE")
        
        # Now verify fact-5 with high evidence
        self.engine.update_evidence("fact-5", evidence_type="supporting", weight=20.0)
        voi_low = self.engine.compute_value_of_information("fact-5", probe_cost=0.1)
        self.assertFalse(voi_low["should_probe"])
        self.assertEqual(voi_low["recommendation"], "SKIP_PROBE_INSUFFICIENT_VOI")

if __name__ == "__main__":
    unittest.main()
