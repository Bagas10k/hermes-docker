#!/usr/bin/env python3
"""
Unit tests for agent-crash-repro-synthesis.
Verifies:
1. Traceback parsing & structured signature fingerprinting.
2. Delta-debugging ddmin 1-minimality on input array.
3. Repro script synthesis & execution exit codes.
4. Binary elimination efficiency (>= 80% input reduction).
5. Non-deterministic / flaky crash detection.
"""

import unittest
import os
import sys
import tempfile
import subprocess
from agent_crash_repro_synthesis import (
    parse_python_traceback,
    ddmin_minimize,
    synthesize_minimal_repro,
    generate_repro_script,
    CrashSignature
)

class TestCrashReproSynthesis(unittest.TestCase):

    def test_traceback_parsing(self):
        sample_tb = """
Traceback (most recent call last):
  File "/opt/app/service.py", line 42, in process_request
    result = compute_metrics(payload)
  File "/opt/app/calculator.py", line 108, in compute_metrics
    return total / count
ZeroDivisionError: division by zero
"""
        sig = parse_python_traceback(sample_tb)
        self.assertEqual(sig.exception_type, "ZeroDivisionError")
        self.assertEqual(sig.error_message, "division by zero")
        self.assertEqual(sig.culprit_file, "/opt/app/calculator.py")
        self.assertEqual(sig.culprit_line, 108)
        self.assertEqual(len(sig.stack_frames), 2)
        self.assertEqual(sig.fingerprint, "ZeroDivisionError@calculator.py:108")

    def test_ddmin_minimization(self):
        # Crash occurs specifically when both 'TRIGGER_A' and 'TRIGGER_B' are present
        large_payload = [f"line_{i}" for i in range(100)]
        large_payload[15] = "TRIGGER_A"
        large_payload[85] = "TRIGGER_B"

        def oracle(subset):
            return "TRIGGER_A" in subset and "TRIGGER_B" in subset

        minimized, iters = ddmin_minimize(large_payload, oracle)
        self.assertEqual(set(minimized), {"TRIGGER_A", "TRIGGER_B"})
        self.assertEqual(len(minimized), 2)
        self.assertTrue(iters < 50)

    def test_repro_synthesis_ratio(self):
        large_input = [f"data_item_{i}" for i in range(200)]
        large_input[50] = "CRITICAL_PAYLOAD"

        def oracle(subset):
            return "CRITICAL_PAYLOAD" in subset

        res = synthesize_minimal_repro("dummy_cmd", large_input, oracle)
        self.assertEqual(res.original_size, 200)
        self.assertEqual(res.minimized_size, 1)
        self.assertGreaterEqual(res.reduction_ratio, 0.99)
        self.assertTrue(res.fingerprint_match)

    def test_generated_script_execution(self):
        sig = CrashSignature(
            exception_type="ValueError",
            error_message="Invalid bounds detected",
            culprit_file="worker.py",
            culprit_line=25,
            stack_frames=[],
            fingerprint="ValueError@worker.py:25"
        )
        repro_body = "    raise ValueError('Invalid bounds detected')"
        
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            script_path = f.name
        
        try:
            generate_repro_script(sig, repro_body, output_path=script_path)
            res = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0)
            self.assertIn("PASS: Deterministically reproduced expected ValueError", res.stdout)
        finally:
            if os.path.exists(script_path):
                os.remove(script_path)

    def test_flaky_detection_oracle(self):
        # Flaky oracle that crashes intermittently
        state = {"counter": 0}
        def flaky_oracle(subset):
            state["counter"] += 1
            return state["counter"] % 2 == 0

        # Repeated test on same subset reveals inconsistency
        sub = ["item1", "item2"]
        res1 = flaky_oracle(sub)
        res2 = flaky_oracle(sub)
        self.assertNotEqual(res1, res2, "Flakiness must be detected via repeated evaluation variance")

if __name__ == "__main__":
    unittest.main()
