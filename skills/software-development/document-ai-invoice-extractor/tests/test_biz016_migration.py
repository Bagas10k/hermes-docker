"""Synthetic local records; no production persistence."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import rebilling


def record():
    row = dict(seller_id='seller', document_id='doc', line_id='1', currency='USD',
               description='Service', quantity='1', unit_price='10', amount='10')
    return {'row': row, 'fingerprints': [rebilling.versioned_fingerprint(row, version='v1')]}


class MigrationTests(unittest.TestCase):
    def test_invalid_envelopes_fail_closed(self):
        import fingerprint_migration as migration
        mutations = [('digest', '0' * 64), ('version', 'v9'), ('algorithm', 'md5'),
                     ('needs_review', False), ('needs_review', 1),
                     ('period_identity_complete', 0), ('period_state', 'known')]
        for field, value in mutations:
            item = record()
            item['fingerprints'][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                migration.migrate_records([item])
        for history in [[], [record()['fingerprints'][0]] * 2, 'bad']:
            item = record()
            item['fingerprints'] = history
            with self.subTest(history=history), self.assertRaises(ValueError):
                migration.migrate_records([item])

    def test_bounds_schema_and_atomic_failure(self):
        import fingerprint_migration as migration
        for value in [None, {}, [record()] * 501, [record(), record()],
                      [{'row': {}}], [dict(record(), extra='unsupported')]]:
            with self.subTest(value_type=type(value)), self.assertRaises(ValueError):
                migration.migrate_records(value)
        source = [record(), record()]
        source[1]['row']['document_id'] = 'other'
        source[1]['row']['service_period'] = {'start': 'bad', 'end': 'bad'}
        before = copy.deepcopy(source)
        with self.assertRaises(ValueError):
            migration.migrate_records(source)
        self.assertEqual(source, before)

    def test_known_period_and_existing_v2_validation(self):
        import fingerprint_migration as migration
        item = record()
        item['row']['service_period'] = {'start': '2026-01-01', 'end': '2026-01-31'}
        result = migration.migrate_records([item])
        self.assertTrue(result[0]['fingerprints'][1]['period_identity_complete'])
        result[0]['row']['service_period']['end'] = '2026-02-01'
        with self.assertRaises(ValueError):
            migration.migrate_records(result)
        item['fingerprints'][0]['extra'] = 'unsupported'
        with self.assertRaises(ValueError):
            migration.migrate_records([item])

    def test_empty_and_full_batch(self):
        import fingerprint_migration as migration
        self.assertEqual(migration.migrate_records([]), [])
        records = [record() for _ in range(500)]
        for i, item in enumerate(records):
            item['row']['document_id'] = str(i)
        self.assertEqual(len(migration.migrate_records(records)), 500)

    def test_unbounded_metadata_rejected(self):
        import fingerprint_migration as migration
        item = record()
        item['row']['raw_document'] = 'x' * 10000
        with self.assertRaises(ValueError):
            migration.migrate_records([item])

    def test_preserve_history_and_idempotence(self):
        import fingerprint_migration as migration
        source = [record()]
        original = copy.deepcopy(source)
        result = migration.migrate_records(source)
        self.assertEqual(source, original)
        self.assertEqual(result[0]['fingerprints'][0], source[0]['fingerprints'][0])
        self.assertEqual(result[0]['fingerprints'][1], rebilling.versioned_fingerprint(source[0]['row']))
        self.assertEqual(migration.migrate_records(result), result)
        result[0]['row']['description'] = 'changed'
        self.assertEqual(source, original)
