"""Synthetic, deterministic versioned identity contract tests."""
import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from rebilling import fingerprint, versioned_fingerprint


def row(**updates):
    r = dict(seller_id='seller', currency='USD', document_id='A', line_id='1',
             description='Hosting', quantity='1', unit_price='10', amount='10',
             service_period={'start': '2026-01-01', 'end': '2026-01-31'})
    r.update(updates)
    return r


class VersionedFingerprintTests(unittest.TestCase):
    def test_legacy_golden_serialization(self):
        expected = hashlib.sha256(b'["seller","USD","1","10","10","hosting"]').hexdigest()
        self.assertEqual(fingerprint(row()), expected)
        self.assertEqual(versioned_fingerprint(row(), version='v1')['digest'], expected)

    def test_distinct_periods(self):
        a = row()
        b = row(service_period={'start':'2026-02-01','end':'2026-02-28'})
        self.assertEqual(fingerprint(a), fingerprint(b))
        self.assertNotEqual(versioned_fingerprint(a)['digest'], versioned_fingerprint(b)['digest'])

    def test_canonical_identity_and_no_mutation(self):
        a = row()
        before = copy.deepcopy(a)
        b = row(document_id='B', line_id='2', description=' HOSTING ', quantity='1.0000', amount='10.00')
        self.assertEqual(versioned_fingerprint(a), versioned_fingerprint(b))
        self.assertEqual(a, before)

    def test_unknown_is_explicit_and_not_eligible(self):
        a = row(service_period=None)
        b = row(); b.pop('service_period')
        result = versioned_fingerprint(a)
        self.assertEqual(result, versioned_fingerprint(b))
        self.assertEqual(result['period_state'], 'unknown')
        self.assertFalse(result['period_identity_complete'])
        self.assertTrue(result['needs_review'])
        self.assertNotEqual(result['digest'], versioned_fingerprint(row())['digest'])

    def test_invalid_periods_fail_closed(self):
        for period in [{}, {'start':'2026-01-01'}, {'start':'2026-02-30','end':'2026-03-01'},
                       {'start':'2026-02-02','end':'2026-02-01'}, [], False]:
            with self.subTest(period=period), self.assertRaises(ValueError):
                versioned_fingerprint(row(service_period=period))

    def test_versions_and_scope(self):
        for version in ['v0', 1, None, True, []]:
            with self.subTest(version=version), self.assertRaises(ValueError):
                versioned_fingerprint(row(), version=version)
        a = versioned_fingerprint(row())
        self.assertEqual(a['version'], 'v2')
        self.assertNotEqual(a['digest'], versioned_fingerprint(row(seller_id='other'))['digest'])
        self.assertNotEqual(a['digest'], versioned_fingerprint(row(), version='v1')['digest'])
        self.assertTrue(a['needs_review'])

    def test_legacy_ignores_invalid_period_as_before(self):
        a = row(service_period='legacy-unparsed')
        self.assertEqual(versioned_fingerprint(a, version='v1')['digest'], fingerprint(a))
        self.assertEqual(versioned_fingerprint(a, version='v1')['period_state'], 'ignored')

    def test_overlap_is_not_equal_identity(self):
        a = row()
        b = row(service_period={'start':'2026-01-15','end':'2026-01-31'})
        self.assertNotEqual(versioned_fingerprint(a)['digest'], versioned_fingerprint(b)['digest'])


if __name__ == '__main__':
    unittest.main()
