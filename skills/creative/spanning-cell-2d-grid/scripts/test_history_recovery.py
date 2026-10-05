import os
import select
import signal
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from byte_budget_history import ByteBudgetHistory
from history_file import save_file, load_file
from history_persistence import dump_history
from history_recovery import guarded_save, recover_orphans, exclusive_history


@unittest.skipUnless(os.name == 'posix', 'POSIX kill and flock')
class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'history.json'
        save_file(ByteBudgetHistory({'A': 'old'}), self.path)
        self.old = self.path.read_bytes()
        self.new = dump_history(ByteBudgetHistory({'A': 'new'}))

    def worker(self, boundary):
        p = subprocess.Popen([sys.executable, str(Path(__file__).with_name('history_kill_worker.py')),
                              str(self.path), boundary], stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        def cleanup():
            if p.poll() is None:
                p.kill()
            p.communicate(timeout=5)
        self.addCleanup(cleanup)
        ready, _, _ = select.select([p.stdout], [], [], 5)
        self.assertTrue(ready, 'worker handshake timeout')
        self.assertEqual(p.stdout.readline(), b'READY\n')
        return p

    def boundary(self, name, replaced):
        p = self.worker(name)
        with self.assertRaises(BlockingIOError):
            recover_orphans(self.path)
        p.kill()
        p.wait(timeout=5)
        self.assertEqual(p.returncode, -signal.SIGKILL)
        expected = self.new if replaced else self.old
        self.assertEqual(self.path.read_bytes(), expected)
        self.assertEqual(dump_history(load_file(self.path)), expected)
        removed = recover_orphans(self.path)
        self.assertEqual(len(removed), 0 if replaced else 1)
        self.assertEqual(recover_orphans(self.path), [])
        self.assertEqual(self.path.read_bytes(), expected)
        guarded_save(ByteBudgetHistory({'A': 'new'}), self.path)
        self.assertEqual(self.path.read_bytes(), self.new)

    def test_kill_before_sync(self):
        self.boundary('before_sync', False)

    def test_kill_before_replace(self):
        self.boundary('before_replace', False)

    def test_kill_after_replace(self):
        self.boundary('after_replace', True)

    def test_active_writer_temp_not_deleted(self):
        p = self.worker('before_replace')
        before = sorted(x.name for x in self.path.parent.iterdir())
        with self.assertRaises(BlockingIOError):
            recover_orphans(self.path)
        self.assertEqual(before, sorted(x.name for x in self.path.parent.iterdir()))
        p.stdin.write(b'continue\n')
        p.stdin.flush()
        p.wait(timeout=5)
        self.assertEqual(p.returncode, 0)
        self.assertEqual(self.path.read_bytes(), self.new)

    def test_second_writer_rejected(self):
        self.worker('before_replace')
        with self.assertRaises(BlockingIOError):
            guarded_save(ByteBudgetHistory(), self.path)
        self.assertEqual(self.path.read_bytes(), self.old)

    def test_scoped_cleanup_preserves_symlinks_directories_and_other_targets(self):
        root = self.path.parent
        candidate = root / '.history.json.abcd.tmp'
        candidate.write_bytes(b'incomplete')
        other = root / '.other.json.abcd.tmp'
        other.write_bytes(b'other')
        link = root / '.history.json.link.tmp'
        link.symlink_to(self.path)
        directory = root / '.history.json.dir.tmp'
        directory.mkdir()
        self.assertEqual(recover_orphans(self.path), [candidate.name])
        self.assertTrue(other.exists())
        self.assertTrue(link.is_symlink())
        self.assertTrue(directory.is_dir())
        self.assertEqual(self.path.read_bytes(), self.old)

    def test_lock_inode_stable(self):
        lock = self.path.parent / '.history.json.lock'
        with exclusive_history(self.path):
            inode = lock.stat().st_ino
        recover_orphans(self.path)
        self.assertEqual(lock.stat().st_ino, inode)

    def test_lock_symlink_rejected(self):
        lock = self.path.parent / '.history.json.lock'
        lock.symlink_to(self.path)
        with self.assertRaises(OSError):
            recover_orphans(self.path)
        self.assertEqual(self.path.read_bytes(), self.old)


if __name__ == '__main__':
    unittest.main()
