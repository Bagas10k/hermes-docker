import importlib.util
import unittest


class AdmissionTests(unittest.TestCase):
    def test_exit_shutdown_and_resize(self):
        from admission import Ledger
        ledger = Ledger(budget=100, overhead=10, safety=10, concurrency=2, backlog=4)
        ledger.submit('a', 30)
        ledger.submit('b', 30)
        a, b = ledger.dispatch()
        ledger.submit('c', 20)
        ledger.set_target(1)
        self.assertEqual(ledger.dispatch(), [])
        ledger.mark_stopping(a)
        self.assertFalse(ledger.release(a, reaped=True, empty=False))
        self.assertFalse(ledger.release(a, reaped=False, empty=True))
        self.assertEqual(ledger.snapshot()['reserved'], 60)
        self.assertTrue(ledger.release(a, reaped=True, empty=True))
        self.assertEqual(ledger.dispatch(), [])
        self.assertEqual(ledger.shutdown(), [b])
        self.assertEqual(ledger.snapshot()['queued'], 0)
        self.assertEqual(ledger.snapshot()['reserved'], 30)
        self.assertEqual(ledger.dispatch(), [])
        with self.assertRaises(ValueError):
            ledger.submit('d', 10)
        self.assertTrue(ledger.release(b, reaped=True, empty=True))
        with self.assertRaises(ValueError):
            ledger.release(b, reaped=True, empty=True)

    def test_input_and_backlog_bounds(self):
        from admission import Ledger, Ticket
        defaults = dict(budget=100, overhead=10, safety=10, concurrency=2, backlog=2)
        for key, value in [('budget', 9000000001), ('budget', True), ('overhead', -1), ('safety', 90), ('concurrency', 0), ('backlog', 0), ('backlog', 10001), ('concurrency', 1.5)]:
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                Ledger(**(defaults | {key: value}))
        ledger = Ledger(**defaults)
        for worker, cost in [('bad id', 1), ('x'*65, 1), ('', 1), (3, 1), ('x', True), ('x', 0), ('x', -1), ('x', 81), ('x', float('nan')), ('x', '1')]:
            before = ledger.snapshot()
            with self.subTest(worker=worker, cost=cost), self.assertRaises(ValueError):
                ledger.submit(worker, cost)
            self.assertEqual(before, ledger.snapshot())
        ledger.submit('a', 40)
        with self.assertRaises(ValueError):
            ledger.submit('a', 10)
        ledger.submit('b', 40)
        with self.assertRaises(ValueError):
            ledger.submit('c', 1)
        a, b = ledger.dispatch()
        self.assertEqual(ledger.snapshot()['reserved'], 80)
        with self.assertRaises(ValueError):
            ledger.submit('a', 1)
        for bad in [True, -1, 3, 1.0]:
            with self.assertRaises(ValueError):
                ledger.set_target(bad)
        ledger.set_target(0)
        with self.assertRaises(ValueError):
            ledger.release(Ticket(a.serial, a.worker, a.reservation), reaped=True, empty=True)
        with self.assertRaises(ValueError):
            ledger.release(a, reaped=1, empty=True)
        self.assertTrue(ledger.release(a, reaped=True, empty=True))
        ledger.submit('a', 10)
        self.assertEqual(ledger.dispatch(), [])
        ledger.set_target(2)
        newer, = ledger.dispatch()
        self.assertNotEqual(a.serial, newer.serial)
        with self.assertRaises(ValueError):
            ledger.release(a, reaped=True, empty=True)

    def test_concurrent_spike_is_bounded(self):
        from admission import Ledger
        from concurrent.futures import ThreadPoolExecutor
        ledger = Ledger(budget=100, overhead=10, safety=10, concurrency=3, backlog=10)
        def submit(i):
            try:
                ledger.submit('w'+str(i), 20)
                return True
            except ValueError:
                return False
        with ThreadPoolExecutor(max_workers=16) as pool:
            accepted = list(pool.map(submit, range(100)))
            batches = list(pool.map(lambda _: ledger.dispatch(), range(40)))
        self.assertEqual(sum(accepted), 10)
        self.assertEqual(sum(map(len, batches)), 3)
        self.assertEqual(ledger.snapshot(), {'reserved': 60, 'active': 3, 'queued': 7})

    def test_cli(self):
        import subprocess
        import sys
        import json
        from pathlib import Path
        script = str(Path(__file__).with_name('admission.py'))
        good = subprocess.run([sys.executable, '-B', script, '--demo'], capture_output=True, text=True)
        self.assertEqual(good.returncode, 0)
        self.assertTrue(good.stdout.strip(), 'CLI must produce evidence')
        result = json.loads(good.stdout)
        self.assertEqual(result['before']['reserved'], 60)
        self.assertEqual(result['after']['reserved'], 0)
        bad = subprocess.run([sys.executable, '-B', script, '--budget', '9000000001', '--demo'], capture_output=True, text=True)
        self.assertEqual(bad.returncode, 2)
        self.assertIn('error', json.loads(bad.stdout))

    def test_atomic_budget_admission(self):
        self.assertIsNotNone(importlib.util.find_spec('admission'), 'helper must exist')
        from admission import Ledger
        ledger = Ledger(budget=100, overhead=10, safety=10, concurrency=3, backlog=4)
        ledger.submit('a', 50)
        ledger.submit('b', 40)
        self.assertEqual([t.worker for t in ledger.dispatch()], ['a'])
        self.assertEqual(ledger.snapshot()['reserved'], 50)
        self.assertEqual(ledger.snapshot()['queued'], 1)


if __name__ == '__main__':
    unittest.main()
