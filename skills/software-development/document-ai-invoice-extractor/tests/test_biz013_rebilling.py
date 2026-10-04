import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from rebilling import fingerprint, reconcile


def row(**changes):
    value = dict(seller_id='vendor-1', currency='USD', document_id='A', line_id='1',
                 description='Monthly hosting service', quantity='1', unit_price='20', amount='20')
    value.update(changes)
    return value


class RebillingTests(unittest.TestCase):
    def test_exact_cross_document(self):
        result = reconcile([row(), row(document_id='B')])
        self.assertEqual(result['candidates'][0]['kind'], 'exact')
        self.assertFalse(result['fraud_verified'])
        self.assertEqual(result['status'], 'needs_review')

    def test_canonical_hash(self):
        self.assertEqual(fingerprint(row()), fingerprint(row(document_id='B', amount='20.00', description=' MONTHLY  HOSTING SERVICE ')))
        self.assertNotEqual(fingerprint(row()), fingerprint(row(seller_id='vendor-2')))

    def test_fuzzy_and_order(self):
        values = [row(), row(document_id='B', description='Monthly hosting servlce')]
        self.assertEqual(reconcile(values), reconcile(values[::-1]))
        self.assertEqual(reconcile(values)['candidates'][0]['kind'], 'fuzzy')

    def test_scope_and_numeric_controls(self):
        for change in ({'seller_id':'vendor-2'}, {'currency':'IDR'}, {'quantity':'2'},
                       {'amount':'21'}, {'unit_price':'21'}, {'description':'Office stationery'}):
            with self.subTest(change=change):
                self.assertEqual(reconcile([row(), row(document_id='B', **change)])['candidates'], [])

    def test_same_document_not_rebilling(self):
        self.assertEqual(reconcile([row(), row(line_id='2')])['candidates'], [])

    def test_duplicate_reference_rejected(self):
        with self.assertRaises(ValueError):
            reconcile([row(), row()])

    def test_bad_numeric_and_fields(self):
        for bad in ('NaN', 'Infinity', '1e2', '-1', 1.0, '', '1,000', '1.00001'):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                reconcile([row(amount=bad)])
        for bad in (row(quantity='0'), row(description=' '), row(currency='EUR'), {}, None):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                reconcile([bad])

    def test_limits(self):
        for bad in (0.79, 1.1, float('nan'), True, '0.9'):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                reconcile([], threshold=bad)
        with self.assertRaises(ValueError):
            reconcile([row()] * 501)
        with self.assertRaises(ValueError):
            reconcile([], max_lines=501)
        with self.assertRaises(ValueError):
            reconcile([row(description='a' * 257)])

    def test_no_transitive_dedup_or_deletion(self):
        values = [row(document_id=x) for x in ('C', 'A', 'B')]
        original = [dict(x) for x in values]
        self.assertEqual(len(reconcile(values)['candidates']), 3)
        self.assertEqual(values, original)

    def test_empty_and_strict_threshold(self):
        self.assertEqual(reconcile([])['status'], 'no_candidates')
        self.assertEqual(reconcile([row(), row(document_id='B', description='Monthly hosting servlce')], threshold=1)['candidates'], [])


if __name__ == '__main__':
    unittest.main()
