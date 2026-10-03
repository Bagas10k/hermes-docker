"""Real isolated subprocess failures; no production documents."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from extract_invoice import supervise


def _make_valid_payload(status="arithmetic_consistent", has_issues=False):
    payload = {
        "status": status,
        "locale": "en_US",
        "rounding": "ROUND_HALF_UP; line products to 0.01, then sum; exact comparison",
        "authenticity_verified": False,
        "fields": {
            "invoice": {"value": "INV-1", "evidence": []},
            "currency": {"value": "USD", "evidence": []},
            "subtotal": {"value": "10.00", "evidence": []},
            "tax": {"value": "0.00", "evidence": []},
            "discount": {"value": "0.00", "evidence": []},
            "total": {"value": "10.00", "evidence": []}
        },
        "lines": [{"description": "Item", "quantity": "1", "unit_price": "10.00", "amount": "10.00", "expected_amount": "10.00", "evidence": []}],
        "issues": [{"code": "some_issue"}] if has_issues else [],
        "source": {
            "path": "test.txt", "method": "text", "pages": [], "coverage_complete": True,
            "coverage_scope": "text extraction only; visual completeness not established"
        }
    }
    return payload


class WorkerFailureTests(unittest.TestCase):
    def run_worker(self, body):
        return supervise([sys.executable, '-c', body], timeout=3)

    def test_signal_discards_partial_output(self):
        code, out, err = self.run_worker("import os,signal; print('{partial', flush=True); os.kill(os.getpid(),signal.SIGTERM)")
        self.assertEqual((code, out), (1, ''))
        self.assertIn('signal 15', err)

    def test_kill_discards_complete_looking_output(self):
        code, out, err = self.run_worker("import os,signal; print('{}', flush=True); os.kill(os.getpid(),signal.SIGKILL)")
        self.assertEqual((code, out), (1, ''))
        self.assertIn('signal 9', err)

    def test_operational_failure_discards_output(self):
        code, out, err = self.run_worker("import sys; print('{partial', flush=True); print('failure',file=sys.stderr); sys.exit(1)")
        self.assertEqual((code, out), (1, ''))
        self.assertIn('failure', err)

    def test_unknown_exit_is_operational_failure(self):
        code, out, err = self.run_worker("import sys; print('{}'); sys.exit(7)")
        self.assertEqual((code, out), (1, ''))
        self.assertIn('exit 7', err)

    def test_success_and_review_preserved_with_valid_schema(self):
        for expected in (0, 2):
            with self.subTest(expected=expected):
                st = "arithmetic_consistent" if expected == 0 else "needs_review"
                has_iss = (expected == 2)
                doc = _make_valid_payload(status=st, has_issues=has_iss)
                code, out, err = self.run_worker(
                    f"import json, sys; print(json.dumps({doc!r})); sys.exit({expected})"
                )
                self.assertEqual(code, expected)
                self.assertEqual(json.loads(out), doc)
                self.assertEqual(err, '')

    def test_invalid_json_at_exit_0_or_2_is_operational_failure(self):
        for exit_code in (0, 2):
            with self.subTest(exit_code=exit_code):
                code, out, err = self.run_worker(f"import sys; print('not a json'); sys.exit({exit_code})")
                self.assertEqual((code, out), (1, ''))
                self.assertIn('invalid schema or corrupted payload', err)

    def test_schema_mismatch_at_exit_0_or_2_is_operational_failure(self):
        # Exit 0 but status needs_review
        bad_exit0 = _make_valid_payload(status="needs_review", has_issues=True)
        code, out, err = self.run_worker(f"import json, sys; print(json.dumps({bad_exit0!r})); sys.exit(0)")
        self.assertEqual((code, out), (1, ''))
        self.assertIn('Exit code 0 requires status', err)

        # Exit 2 but status arithmetic_consistent
        bad_exit2 = _make_valid_payload(status="arithmetic_consistent", has_issues=False)
        code, out, err = self.run_worker(f"import json, sys; print(json.dumps({bad_exit2!r})); sys.exit(2)")
        self.assertEqual((code, out), (1, ''))
        self.assertIn('Exit code 2 requires status', err)

    def test_missing_mandatory_schema_field_is_operational_failure(self):
        corrupted = _make_valid_payload(status="arithmetic_consistent", has_issues=False)
        del corrupted["fields"]
        code, out, err = self.run_worker(f"import json, sys; print(json.dumps({corrupted!r})); sys.exit(0)")
        self.assertEqual((code, out), (1, ''))
        self.assertIn('Missing or invalid fields object', err)

    def test_timeout_with_partial_output_raises(self):
        with self.assertRaises(TimeoutError):
            supervise([sys.executable, '-c', "import time; print('{partial',flush=True); time.sleep(10)"], timeout=0.1)

    def test_stdout_flood_killed_and_discards_output(self):
        code, out, err = supervise(
            [sys.executable, '-c', "import sys; sys.stdout.write('A' * 200000); sys.stdout.flush()"],
            timeout=5, max_output_bytes=10000
        )
        self.assertEqual((code, out), (1, ''))
        self.assertIn('output buffer limit on stdout', err)

    def test_stderr_flood_killed_and_discards_output(self):
        code, out, err = supervise(
            [sys.executable, '-c', "import sys; sys.stderr.write('E' * 200000); sys.stderr.flush()"],
            timeout=5, max_output_bytes=10000
        )
        self.assertEqual((code, out), (1, ''))
        self.assertIn('output buffer limit on stderr', err)


if __name__ == '__main__':
    unittest.main()
