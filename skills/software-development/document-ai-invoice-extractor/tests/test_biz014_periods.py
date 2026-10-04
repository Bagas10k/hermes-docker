"""Synthetic local evidence; never an invoice authenticity benchmark."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import rebilling


def row(doc, start='2026-01-01', end='2026-01-31'):
    return dict(seller_id='seller', document_id=doc, line_id='1', currency='USD',
                description='Monthly hosting', quantity='1', unit_price='10', amount='10',
                service_period={'start': start, 'end': end})


class PeriodTests(unittest.TestCase):
    def test_disjoint_recurring_periods_not_candidates(self):
        result = rebilling.reconcile([row('A'), row('B', '2026-02-01', '2026-02-28')], service_periods=True)
        self.assertEqual(result['status'], 'no_candidates')
        self.assertEqual(result['candidates'], [])
        self.assertFalse(result['fraud_verified'])

    def test_invalid_periods_rejected_even_without_candidate(self):
        bad = [False, {}, [], {'start': '2026-01-01'},
               {'start': '2026-02-30', 'end': '2026-03-01'},
               {'start': '2026-02-01', 'end': '2026-01-01'},
               {'start': '20260101', 'end': '2026-01-31'},
               {'start': '2026-01-01T00:00:00', 'end': '2026-01-31'},
               {'start': '2026-01-01', 'end': '2026-01-31', 'extra': 1}]
        for period in bad:
            with self.subTest(period=period):
                item = row('A'); item['service_period'] = period
                with self.assertRaises(ValueError):
                    rebilling.reconcile([item], service_periods=True)
        with self.assertRaises(ValueError):
            rebilling.reconcile([], service_periods='yes')

    def test_relations_evidence_and_immutable_inputs(self):
        from copy import deepcopy
        cases = [('2026-01-01', '2026-01-31', 'equal', 31),
                 ('2026-01-31', '2026-02-28', 'overlap', 1),
                 ('2026-01-10', '2026-01-15', 'overlap', 6),
                 (None, None, 'unknown', None)]
        for start, end, relation, days in cases:
            a, b = row('A'), row('B', start, end)
            if start is None:
                del b['service_period']
            rows = [a, b]; before = deepcopy(rows)
            result = rebilling.reconcile(rows, service_periods=True)
            candidate = result['candidates'][0]
            self.assertEqual(candidate['period_relation'], relation)
            self.assertEqual(candidate['overlap_days'], days)
            self.assertTrue(candidate['needs_review'])
            self.assertEqual(rows, before)
            self.assertEqual(result, rebilling.reconcile(rows[::-1], service_periods=True))

    def test_leap_day_and_legacy_mode(self):
        a, b = row('A', '2024-02-29', '2024-02-29'), row('B', '2024-02-29', '2024-02-29')
        self.assertEqual(rebilling.reconcile([a,b], service_periods=True)['candidates'][0]['overlap_days'], 1)
        self.assertEqual(len(rebilling.reconcile([row('A'),row('B','2026-02-01','2026-02-28')])['candidates']), 1)


if __name__ == '__main__':
    unittest.main()
