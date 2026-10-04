import itertools
import unittest
from revision_gate import RevisionGate, MAX_REVISION


class RevisionTests(unittest.TestCase):
    def test_all_arrival_orders(self):
        for order in itertools.permutations(range(1, 5)):
            gate = RevisionGate()
            for _ in range(4): gate.begin()
            commits = []
            for r in order: gate.apply(r, r, commits.append)
            self.assertEqual(commits, [4])

    def test_old_rejected_before_latest_arrives(self):
        gate = RevisionGate(); gate.begin(); gate.begin()
        self.assertFalse(gate.apply(1, None, lambda _: self.fail()))
        self.assertEqual(gate.applied, 0)

    def test_duplicate_future_unissued(self):
        gate = RevisionGate()
        self.assertFalse(gate.apply(1, None, lambda _: self.fail()))
        gate.begin()
        self.assertTrue(gate.apply(1, None, lambda _: None))
        for r in (1, 2):
            self.assertFalse(gate.apply(r, None, lambda _: self.fail()))

    def test_validation(self):
        gate = RevisionGate(); gate.begin()
        for r in (True, False, 0, -1, 1.0, '1', None, MAX_REVISION + 1):
            with self.assertRaises(ValueError): gate.apply(r, None, lambda _: self.fail())

    def test_failure_retry(self):
        gate = RevisionGate(); r = gate.begin()
        def fail(_): raise RuntimeError('build failed')
        with self.assertRaises(RuntimeError): gate.apply(r, None, fail)
        self.assertEqual(gate.applied, 0)
        self.assertTrue(gate.apply(r, None, lambda _: None))

    def test_exhaustion(self):
        gate = RevisionGate(); gate.issued = MAX_REVISION
        with self.assertRaises(OverflowError): gate.begin()
        self.assertEqual(gate.issued, MAX_REVISION)


if __name__ == '__main__': unittest.main()
