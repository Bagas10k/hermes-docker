import unittest
from dataclasses import replace
import trajectory as t

class TrajectoryTests(unittest.TestCase):
    def gate(self, **kw):
        return t.Tracker('a', 'ctx', 'target', 'saved', start=0, **kw)

    def obs(self, **kw):
        return replace(t.Observation('a', 'ctx', 'target', 'saved', 1, 1, 1, 'complete', True, True), **kw)

    def test_semantic_success(self):
        self.assertEqual(self.gate().step(self.obs(), now=1), 'SUCCESS')

    def test_same_capture_cannot_be_relabelled(self):
        g = self.gate()
        self.assertEqual(g.step(self.obs(outcome='pending', semantic=None), now=1), 'OBSERVE')
        self.assertEqual(g.step(self.obs(seq=2), now=1.1), 'RECONCILE')

    def test_unknown_nonidempotent_never_repeats(self):
        g = self.gate(max_checks=4)
        for n in range(1, 5):
            self.assertEqual(g.step(self.obs(seq=n, captured=n, outcome='unknown', semantic=None), now=n), 'RECONCILE')
        self.assertEqual(g.step(now=5), 'STOP_RECONCILE')
        self.assertEqual(g.attempt, 1)

    def test_unknown_idempotent_also_reconciles(self):
        self.assertEqual(self.gate(idempotent=True).step(now=1), 'RECONCILE')

    def test_visual_delta_not_success(self):
        for delta in (True, False):
            self.assertEqual(self.gate().step(self.obs(outcome='unknown', semantic=None, visual_changed=delta), now=1), 'RECONCILE')

    def test_untrusted_semantics_not_success(self):
        self.assertEqual(self.gate().step(self.obs(authoritative=False), now=1), 'RECONCILE')

    def test_contradictory_evidence(self):
        for outcome, semantic in [('complete', False), ('absent', True), ('pending', True)]:
            self.assertEqual(self.gate().step(self.obs(outcome=outcome, semantic=semantic), now=1), 'RECONCILE')

    def test_all_correlation_fields(self):
        for field in ('action', 'context', 'target', 'predicate', 'attempt'):
            with self.subTest(field=field):
                self.assertEqual(self.gate().step(self.obs(**{field: 2 if field == 'attempt' else 'other'}), now=1), 'RECONCILE')

    def test_stale_future_predispatch(self):
        for capture, now in [(0, 1), (2, 1), (1, 4)]:
            self.assertEqual(self.gate().step(self.obs(captured=capture), now=now), 'RECONCILE')

    def test_sequence_replay_and_capture_regression(self):
        for seq, captured in [(1, 2), (0, 2), (2, 0.5)]:
            g = self.gate()
            g.step(self.obs(outcome='pending', semantic=None), now=1)
            self.assertEqual(g.step(self.obs(seq=seq, captured=captured), now=2), 'RECONCILE')

    def test_bounded_retry_and_old_attempt(self):
        g = self.gate(idempotent=True)
        absent = self.obs(outcome='absent', semantic=False)
        self.assertEqual(g.step(absent, now=1), 'RETRY')
        self.assertEqual(g.attempt, 2)
        self.assertEqual(g.step(self.obs(seq=2, captured=2), now=2), 'RECONCILE')
        self.assertEqual(g.step(replace(absent, attempt=2, seq=3, captured=3), now=3), 'STOP')

    def test_retry_requires_after_reservation(self):
        g = self.gate(idempotent=True)
        g.step(self.obs(outcome='absent', semantic=False), now=1)
        self.assertEqual(g.step(self.obs(attempt=2, seq=2), now=1), 'RECONCILE')
        self.assertEqual(g.step(self.obs(attempt=2, seq=3, captured=2), now=2), 'SUCCESS')

    def test_nonidempotent_absent_stops(self):
        self.assertEqual(self.gate().step(self.obs(outcome='absent', semantic=False), now=1), 'STOP')

    def test_deadline_is_global_and_inclusive(self):
        g = self.gate(timeout=2, idempotent=True)
        g.step(self.obs(outcome='absent', semantic=False), now=1)
        self.assertEqual(g.step(self.obs(attempt=2, captured=2), now=2), 'STOP_RECONCILE')

    def test_terminal_absorbing(self):
        for end in ('SUCCESS', 'STOP', 'STOP_RECONCILE'):
            g = self.gate()
            o = self.obs() if end == 'SUCCESS' else self.obs(outcome='absent', semantic=False)
            result = g.step(now=30) if end == 'STOP_RECONCILE' else g.step(o, now=1)
            self.assertEqual(result, end)
            self.assertEqual(g.step(object(), now=float('nan')), end)
            self.assertEqual(g.step(self.obs(captured=2), now=2), end)

    def test_bad_numeric_clock(self):
        for value in (float('nan'), float('inf'), -1, True, '1'):
            self.assertEqual(self.gate().step(now=value), 'STOP_RECONCILE')
        g = self.gate()
        g.step(now=2)
        self.assertEqual(g.step(now=1), 'STOP_RECONCILE')

    def test_invalid_observation_schema(self):
        for kw in ({'seq': True}, {'seq': 2**64}, {'captured': float('nan')}, {'semantic': 1}, {'authoritative': 'yes'}, {'visual_changed': 1}, {'outcome': 'SUCCESS'}, {'action': 'x'*129}, {'attempt': False}):
            with self.subTest(kw=kw):
                self.assertEqual(self.gate().step(self.obs(**kw), now=1), 'STOP_RECONCILE')
        self.assertEqual(self.gate().step({}, now=1), 'STOP_RECONCILE')

    def test_invalid_policy(self):
        for kw in ({'max_attempts': 9}, {'max_checks': 0}, {'max_checks': True}, {'max_checks': 1025}, {'timeout': float('inf')}, {'timeout': 0}, {'max_age': -1}, {'idempotent': 1}):
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                self.gate(**kw)
        with self.assertRaises(ValueError):
            t.Tracker('', 'c', 't', 'p', start=0)

    def test_check_cap_no_retry_on_last_check(self):
        self.assertEqual(self.gate(idempotent=True, max_checks=1).step(self.obs(outcome='absent', semantic=False), now=1), 'STOP')

    def test_flood_has_constant_retained_state(self):
        g = self.gate(max_checks=4)
        for _ in range(10000):
            g.step(self.obs(context='wrong'), now=1)
        self.assertEqual(g.checks, 4)
        self.assertFalse(hasattr(g, '__dict__'))
        self.assertEqual(g.terminal, 'STOP_RECONCILE')

if __name__ == '__main__':
    unittest.main()
