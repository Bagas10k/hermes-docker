"""Deterministic RLIMIT_CPU exhaustion benchmark and worker recovery verification."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from extract_invoice import supervise


def _make_valid_payload():
    return {
        "status": "arithmetic_consistent",
        "locale": "en_US",
        "rounding": "ROUND_HALF_UP; line products to 0.01, then sum; exact comparison",
        "authenticity_verified": False,
        "fields": {
            "invoice": {"value": "INV-100", "evidence": []},
            "currency": {"value": "USD", "evidence": []},
            "subtotal": {"value": "50.00", "evidence": []},
            "tax": {"value": "0.00", "evidence": []},
            "discount": {"value": "0.00", "evidence": []},
            "total": {"value": "50.00", "evidence": []}
        },
        "lines": [
            {
                "description": "Diagnostic Audit",
                "quantity": "1",
                "unit_price": "50.00",
                "amount": "50.00",
                "expected_amount": "50.00",
                "evidence": []
            }
        ],
        "issues": [],
        "source": {
            "path": "audit.txt",
            "method": "text",
            "pages": [],
            "coverage_complete": True,
            "coverage_scope": "text extraction only; visual completeness not established"
        }
    }


class CPUExhaustionTests(unittest.TestCase):
    def test_rlimit_cpu_infinite_loop_killed_with_signal(self):
        """Worker spinning in an infinite loop hits RLIMIT_CPU and is terminated."""
        worker_code = """
import resource
resource.setrlimit(resource.RLIMIT_CPU, (1, 1))
while True:
    pass
"""
        code, out, err = supervise([sys.executable, '-c', worker_code], timeout=5)
        self.assertEqual(code, 1)
        self.assertEqual(out, '')
        self.assertIn('error: document worker failed (signal', err)

    def test_rlimit_cpu_with_custom_sigxcpu_handler(self):
        """Worker handling SIGXCPU can emit diagnostics before clean supervisor rejection."""
        worker_code = """
import resource, signal, sys
def handle_xcpu(signum, frame):
    print("RLIMIT_CPU soft limit reached", file=sys.stderr, flush=True)
    sys.exit(3)
signal.signal(signal.SIGXCPU, handle_xcpu)
resource.setrlimit(resource.RLIMIT_CPU, (1, 2))
while True:
    pass
"""
        code, out, err = supervise([sys.executable, '-c', worker_code], timeout=5)
        self.assertEqual(code, 1)
        self.assertEqual(out, '')
        self.assertIn('RLIMIT_CPU soft limit reached', err)
        self.assertIn('error: document worker failed (exit 3)', err)

    def test_supervisor_subsequent_worker_recovery_after_cpu_exhaustion(self):
        """Supervisor cleanly spawns healthy workers after a prior worker was killed by RLIMIT_CPU."""
        exhaustion_code = """
import resource
resource.setrlimit(resource.RLIMIT_CPU, (1, 1))
while True:
    pass
"""
        valid_payload = _make_valid_payload()
        healthy_code = f"""
import json, sys
print(json.dumps({valid_payload!r}))
sys.exit(0)
"""
        # First execution: worker hits CPU exhaustion
        c1, out1, err1 = supervise([sys.executable, '-c', exhaustion_code], timeout=5)
        self.assertEqual(c1, 1)
        self.assertEqual(out1, '')
        self.assertIn('error: document worker failed (signal', err1)

        # Second execution: subsequent healthy worker succeeds with exit 0 and valid schema
        c2, out2, err2 = supervise([sys.executable, '-c', healthy_code], timeout=5)
        self.assertEqual(c2, 0)
        self.assertEqual(json.loads(out2), valid_payload)
        self.assertEqual(err2, '')

        # Third execution: another CPU exhaustion is safely contained
        c3, out3, err3 = supervise([sys.executable, '-c', exhaustion_code], timeout=5)
        self.assertEqual(c3, 1)
        self.assertEqual(out3, '')
        self.assertIn('error: document worker failed (signal', err3)

        # Fourth execution: healthy worker executes smoothly again (no leak in supervisor)
        c4, out4, err4 = supervise([sys.executable, '-c', healthy_code], timeout=5)
        self.assertEqual(c4, 0)
        self.assertEqual(json.loads(out4), valid_payload)
        self.assertEqual(err4, '')


if __name__ == '__main__':
    unittest.main()
