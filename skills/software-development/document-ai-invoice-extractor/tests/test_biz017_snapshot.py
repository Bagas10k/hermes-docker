import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from fingerprint_snapshot import save_snapshot
from rebilling import versioned_fingerprint


class SnapshotTests(unittest.TestCase):
    # Apriori: all pre-replace faults leave previous bytes and no temp files;
    # successful reruns retain historical identities and identical bytes.
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'snapshot.json'
        row = dict(seller_id='S', document_id='D', line_id='L', currency='USD',
                   description='Service', quantity='1', unit_price='10', amount='10')
        self.records = [{'row': row, 'fingerprints': [versioned_fingerprint(row, version='v1')]}]

    def test_publish_and_history(self):
        before = copy.deepcopy(self.records)
        result = save_snapshot(self.path, self.records)
        self.assertEqual(json.loads(self.path.read_text()), result)
        self.assertEqual(result['records'][0]['fingerprints'][0], self.records[0]['fingerprints'][0])
        self.assertEqual(len(result['records'][0]['fingerprints']), 2)
        self.assertEqual(self.records, before)
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)

    def test_rerun_identical_bytes(self):
        first = save_snapshot(self.path, self.records)
        original = self.path.read_bytes()
        save_snapshot(self.path, first['records'])
        self.assertEqual(original, self.path.read_bytes())
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_invalid_preserves_target(self):
        self.path.write_bytes(b'old')
        with self.assertRaises(ValueError):
            save_snapshot(self.path, self.records + [{}])
        self.assertEqual(self.path.read_bytes(), b'old')
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_faults_preserve_target_and_cleanup(self):
        for point in ('tempfile.NamedTemporaryFile', 'os.fsync', 'os.replace'):
            with self.subTest(point=point):
                self.path.write_bytes(b'old')
                with patch('fingerprint_snapshot.' + point, side_effect=OSError('injected')):
                    with self.assertRaises(OSError):
                        save_snapshot(self.path, self.records)
                self.assertEqual(self.path.read_bytes(), b'old')
                self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_replace_observes_old_and_complete_new(self):
        import os
        original_replace = os.replace
        self.path.write_bytes(b'old')
        def inspect(source, target):
            self.assertEqual(self.path.read_bytes(), b'old')
            self.assertEqual(Path(source).parent, self.path.parent)
            self.assertEqual(len(json.loads(Path(source).read_text())['records']), 1)
            original_replace(source, target)
        with patch('fingerprint_snapshot.os.replace', side_effect=inspect):
            save_snapshot(self.path, self.records)

    def test_new_failure_leaves_no_file(self):
        with patch('fingerprint_snapshot.os.replace', side_effect=OSError('injected')):
            with self.assertRaises(OSError):
                save_snapshot(self.path, self.records)
        self.assertEqual(list(self.path.parent.iterdir()), [])

    def test_empty_batch(self):
        self.assertEqual(save_snapshot(self.path, [])['records'], [])

    def test_missing_parent(self):
        with self.assertRaises(FileNotFoundError):
            save_snapshot(self.path / 'missing' / 'file.json', self.records)
        self.assertFalse(self.path.exists())


if __name__ == '__main__':
    unittest.main()
