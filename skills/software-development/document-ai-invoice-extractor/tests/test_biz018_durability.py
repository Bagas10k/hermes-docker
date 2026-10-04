"""Temporary-directory fault injection; no power-cut claim."""
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import fingerprint_snapshot as snapshot
from rebilling import versioned_fingerprint


class DurabilityTests(unittest.TestCase):
    # Apriori: file fsync -> replace -> directory fsync sequence;
    # directory fsync failure raises SnapshotDurabilityError but leaves published file on disk;
    # non-directory paths (root/missing) or pre-replace faults behave cleanly without orphan files.

    def test_directory_sync_after_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'snapshot.json'
            path.write_text('old')
            events = []
            real_sync = os.fsync
            def sync(fd):
                is_dir = stat.S_ISDIR(os.fstat(fd).st_mode)
                events.append('directory' if is_dir else 'file')
                if is_dir:
                    self.assertEqual(json.loads(path.read_text()), {'schema_version': 1, 'records': []})
                else:
                    self.assertEqual(path.read_text(), 'old')
                real_sync(fd)
            with patch.object(snapshot.os, 'fsync', side_effect=sync):
                result = snapshot.save_snapshot(path, [])
            self.assertEqual(events, ['file', 'directory'])
            self.assertEqual(result, {'schema_version': 1, 'records': []})

    def test_directory_sync_failure_leaves_published_file_and_raises(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'snapshot.json'
            path.write_text('old')
            real_sync = os.fsync
            def sync(fd):
                if stat.S_ISDIR(os.fstat(fd).st_mode):
                    raise OSError('EIO on directory fsync')
                real_sync(fd)
            with patch.object(snapshot.os, 'fsync', side_effect=sync):
                with self.assertRaises(snapshot.SnapshotDurabilityError) as cm:
                    snapshot.save_snapshot(path, [])
            self.assertIn('parent directory fsync failed', str(cm.exception))
            # File is atomically replaced and readable, not rolled back
            self.assertEqual(json.loads(path.read_text()), {'schema_version': 1, 'records': []})
            self.assertEqual(list(path.parent.iterdir()), [path])

    def test_non_directory_parent_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            file_as_parent = Path(directory) / 'regular_file'
            file_as_parent.write_text('not a dir')
            target = file_as_parent / 'snapshot.json'
            with self.assertRaises(NotADirectoryError):
                snapshot.save_snapshot(target, [])

    def test_input_preservation_with_records(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'snapshot.json'
            row = dict(seller_id='S', document_id='D', line_id='L', currency='USD',
                       description='Service', quantity='1', unit_price='10', amount='10')
            records = [{'row': row, 'fingerprints': [versioned_fingerprint(row, version='v1')]}]
            res = snapshot.save_snapshot(path, records)
            self.assertEqual(len(res['records'][0]['fingerprints']), 2)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)


if __name__ == '__main__':
    unittest.main()
