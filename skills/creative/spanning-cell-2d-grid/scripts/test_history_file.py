import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, mock_open
from byte_budget_history import ByteBudgetHistory
from history_persistence import dump_history
from history_file import save_file, load_file, restore_file, read_bounded, DurabilityUncertain


class FilePersistenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'history.json'
        self.h = ByteBudgetHistory({'A': 'awal'})
        self.h.commit('a', 'root', {'A': 'baru'}, activate=True)
        self.h.commit('b', 'root', {'B': 'cabang'}, activate=False)
        self.path.write_bytes(b'old target')

    def clean(self):
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_roundtrip_and_branches(self):
        self.assertEqual(save_file(self.h, self.path), len(dump_history(self.h)))
        self.assertEqual(dump_history(load_file(self.path)), dump_history(self.h))
        self.clean()

    def test_output_budget_preserves_old(self):
        with self.assertRaises(OverflowError):
            save_file(self.h, self.path, max_wire_bytes=1)
        self.assertEqual(self.path.read_bytes(), b'old target')
        self.clean()

    def test_file_fsync_failure_preserves_old(self):
        with patch('history_file.os.fsync', side_effect=OSError('injected')):
            with self.assertRaises(OSError):
                save_file(self.h, self.path)
        self.assertEqual(self.path.read_bytes(), b'old target')
        self.clean()

    def test_replace_failure_preserves_old(self):
        with patch('history_file.os.replace', side_effect=OSError('injected')):
            with self.assertRaises(OSError):
                save_file(self.h, self.path)
        self.assertEqual(self.path.read_bytes(), b'old target')
        self.clean()

    @unittest.skipUnless(os.name == 'posix', 'POSIX directory sync')
    def test_directory_failure_reports_committed(self):
        real = os.fsync
        calls = []
        def fail_second(fd):
            calls.append(fd)
            if len(calls) == 2:
                raise OSError('injected directory failure')
            return real(fd)
        with patch('history_file.os.fsync', side_effect=fail_second):
            with self.assertRaises(DurabilityUncertain) as error:
                save_file(self.h, self.path)
        self.assertTrue(error.exception.replaced)
        self.assertEqual(self.path.read_bytes(), dump_history(self.h))
        self.clean()

    def test_exact_read_cap(self):
        raw = dump_history(self.h)
        self.path.write_bytes(raw)
        self.assertEqual(read_bounded(self.path, max_wire_bytes=len(raw)), raw)
        with self.assertRaises(OverflowError):
            read_bounded(self.path, max_wire_bytes=len(raw)-1)

    def test_bounded_read_request(self):
        m = mock_open(read_data=b'12345')
        with patch('builtins.open', m):
            with self.assertRaises(OverflowError):
                read_bounded(self.path, max_wire_bytes=4)
        m().read.assert_called_once_with(5)

    def test_corrupt_restore_no_mutation(self):
        before = dump_history(self.h)
        with self.assertRaises(ValueError):
            restore_file(self.h, self.path)
        self.assertEqual(dump_history(self.h), before)

    def test_restore_success(self):
        save_file(self.h, self.path)
        target = ByteBudgetHistory()
        self.assertIs(restore_file(target, self.path), target)
        self.assertEqual(dump_history(target), dump_history(self.h))

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            load_file(self.path.parent / 'absent')

    def test_invalid_caps(self):
        for cap in (0, -1, True, 1.2):
            with self.subTest(cap=cap), self.assertRaises(ValueError):
                read_bounded(self.path, max_wire_bytes=cap)

    def test_nondurable_directory_option(self):
        with patch('history_file.os.fsync', wraps=os.fsync) as sync:
            save_file(self.h, self.path, sync_directory=False)
        self.assertEqual(sync.call_count, 1)
        self.assertEqual(self.path.read_bytes(), dump_history(self.h))

    def test_create_target_and_missing_parent(self):
        self.path.unlink()
        save_file(self.h, self.path)
        self.assertEqual(self.path.read_bytes(), dump_history(self.h))
        with self.assertRaises(FileNotFoundError):
            save_file(self.h, self.path.parent / 'missing' / 'history')


if __name__ == '__main__':
    unittest.main()
