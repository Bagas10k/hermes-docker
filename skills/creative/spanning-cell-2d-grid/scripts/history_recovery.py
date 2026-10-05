"""POSIX cooperative save/recovery lock; trusted local directories only."""
import os
import stat
from contextlib import contextmanager
from pathlib import Path
from history_file import save_file


@contextmanager
def exclusive_history(path):
    """Nonblocking lock. Never unlink the stable lock inode. All writers must opt in."""
    if os.name != 'posix':
        raise NotImplementedError('requires POSIX flock')
    import fcntl
    path = Path(path).absolute()
    fd = os.open(path.parent / ('.' + path.name + '.lock'),
                 os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ValueError('lock must be regular')
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield path
    finally:
        os.close(fd)


def guarded_save(history, path, **kwargs):
    with exclusive_history(path) as target:
        return save_file(history, target, **kwargs)


def recover_orphans(path):
    """Discard uncommitted regular temp files; never promote or trust their contents.

    Requires every writer of this target to use guarded_save, no inherited lock
    descriptors and a stable trusted directory. Legacy save_file bypasses locking.
    """
    with exclusive_history(path) as target:
        prefix = '.' + target.name + '.'
        removed = []
        with os.scandir(target.parent) as entries:
            for entry in entries:
                middle = entry.name[len(prefix):-4]
                if (entry.name.startswith(prefix) and entry.name.endswith('.tmp')
                        and middle and entry.is_file(follow_symlinks=False)):
                    os.unlink(entry.path)
                    removed.append(entry.name)
        return sorted(removed)
