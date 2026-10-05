import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from history_lock_owner import HistoryLockOwner

# Predictions: inherited descriptors retain flock after owner exit; detach
# releases the last reference, but cannot release a still-live owner's lock.
SCENARIO = r'''
import ctypes, os, sys
from history_lock_owner import HistoryLockOwner
libc = ctypes.CDLL(None, use_errno=True)
assert libc.prctl(36, 1, 0, 0, 0) == 0  # isolated Linux child subreaper
path, mode = sys.argv[1:]
ready_r, ready_w = os.pipe()
cmd_r, cmd_w = os.pipe()
ack_r, ack_w = os.pipe()
owner_cmd_r, owner_cmd_w = os.pipe()
pid = os.fork()
if pid == 0:
    lock = HistoryLockOwner(path)
    child = os.fork()
    if child == 0:
        try:
            try:
                lock.assert_owner()
                os._exit(11)
            except RuntimeError:
                pass
            os.write(ready_w, b'R')
            assert os.read(cmd_r, 1) == b'D'
            lock.detach_child()
            lock.detach_child()  # idempotent child cleanup
            os.write(ack_w, b'A')
            assert os.read(cmd_r, 1) == b'X'
            os._exit(0)
        except BaseException:
            os._exit(12)
    if mode == 'death':
        os._exit(0)
    assert os.read(owner_cmd_r, 1) == b'X'
    lock.close()
    _, status = os.waitpid(child, 0)
    os._exit(os.waitstatus_to_exitcode(status))
assert os.read(ready_r, 1) == b'R'
if mode == 'death':
    assert os.waitpid(pid, 0)[1] == 0

def blocked():
    try:
        candidate = HistoryLockOwner(path)
    except BlockingIOError:
        return True
    candidate.close()
    return False

assert blocked()
os.write(cmd_w, b'D')
assert os.read(ack_r, 1) == b'A'
assert blocked() == (mode == 'live')
os.write(cmd_w, b'X')
if mode == 'live':
    os.write(owner_cmd_w, b'X')
    assert os.waitpid(pid, 0)[1] == 0
else:
    assert os.waitpid(-1, 0)[1] == 0
with HistoryLockOwner(path) as final:
    final.assert_owner()
print('verified:' + mode)
'''


@unittest.skipUnless(sys.platform == 'linux', 'real fork scenarios use Linux subreaper')
class ForkOwnershipTests(unittest.TestCase):
    def scenario(self, mode):
        with tempfile.TemporaryDirectory() as d:
            p = subprocess.run([sys.executable, '-c', SCENARIO, d + '/stable.lock', mode],
                               cwd=Path(__file__).parent, capture_output=True,
                               text=True, timeout=10)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn('verified:' + mode, p.stdout)

    def test_parent_death_retains_lock_until_child_detaches(self):
        self.scenario('death')

    def test_child_detach_does_not_unlock_live_parent(self):
        self.scenario('live')

    def test_owner_rejects_detach_and_closed_use(self):
        with tempfile.TemporaryDirectory() as d:
            lock = HistoryLockOwner(d + '/lock')
            with self.assertRaises(RuntimeError):
                lock.detach_child()
            self.assertFalse(os.get_inheritable(lock.fd))
            lock.close()
            with self.assertRaises(RuntimeError):
                lock.assert_owner()

    def test_exception_releases_lock(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                with HistoryLockOwner(d + '/lock'):
                    raise ValueError('injected')
            with HistoryLockOwner(d + '/lock') as lock:
                lock.assert_owner()

    def test_contention_and_stable_inode(self):
        with tempfile.TemporaryDirectory() as d:
            path = d + '/lock'
            with HistoryLockOwner(path):
                inode = os.stat(path).st_ino
                with self.assertRaises(BlockingIOError):
                    HistoryLockOwner(path)
            with HistoryLockOwner(path):
                self.assertEqual(os.stat(path).st_ino, inode)


if __name__ == '__main__':
    unittest.main()
