"""Explicit fork ownership policy for trusted POSIX lock files.

A child MUST detach before doing other work, and must never continue a writer
critical section. This helper does not wrap or change guarded_save.
"""
import os
import stat


class HistoryLockOwner:
    def __init__(self, lock_path):
        if os.name != 'posix':
            raise NotImplementedError('POSIX only')
        import fcntl
        self.pid = os.getpid()
        self.fd = os.open(lock_path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        try:
            if not stat.S_ISREG(os.fstat(self.fd).st_mode):
                raise ValueError('regular lock file required')
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BaseException:
            os.close(self.fd)
            self.fd = None
            raise

    def assert_owner(self):
        if os.getpid() != self.pid:
            raise RuntimeError('fork child must detach and acquire its own lock')
        if self.fd is None:
            raise RuntimeError('lock is closed')

    def detach_child(self):
        if os.getpid() == self.pid:
            raise RuntimeError('owner must use close')
        self._close_descriptor()

    def _close_descriptor(self):
        fd, self.fd = self.fd, None
        if fd is not None:
            # Do NOT LOCK_UN: fork shares the open file description with parent.
            os.close(fd)

    def close(self):
        self.assert_owner()
        self._close_descriptor()

    def __enter__(self):
        self.assert_owner()
        return self

    def __exit__(self, *exc):
        if os.getpid() != self.pid:
            self.detach_child()
        elif self.fd is not None:
            self.close()
