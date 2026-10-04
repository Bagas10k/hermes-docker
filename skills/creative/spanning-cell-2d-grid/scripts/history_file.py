"""Local trusted-directory persistence; no multiwriter or power-loss guarantee."""
import os
import tempfile
from pathlib import Path
from history_persistence import dump_history, load_history, restore_history, _limit


class DurabilityUncertain(OSError):
    """Replacement is visible, but parent-directory synchronization failed."""
    replaced = True


def save_file(history, path, *, max_wire_bytes=1048576, sync_directory=True):
    """Sync temporary file, replace atomically, optionally sync parent (POSIX).

    Caller owns the directory and serializes writers. Replaces inode/permissions.
    Failures before replace preserve the old target; failures after replace do not
    roll it back. Process termination can leave an orphan temporary file.
    """
    if type(sync_directory) is not bool:
        raise ValueError('sync_directory must be bool')
    if sync_directory and os.name != 'posix':
        raise NotImplementedError('directory sync requires POSIX')
    raw = dump_history(history, max_wire_bytes=max_wire_bytes)
    path = Path(path).absolute()
    directory_fd = None
    temporary = None
    try:
        if sync_directory:
            directory_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        fd, temporary = tempfile.mkstemp(prefix='.' + path.name + '.', suffix='.tmp', dir=path.parent)
        with os.fdopen(fd, 'wb') as stream:
            written = stream.write(raw)
            if written != len(raw):
                raise OSError('short write')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        temporary = None
        if directory_fd is not None:
            try:
                os.fsync(directory_fd)
            except OSError as exc:
                raise DurabilityUncertain('replaced; directory fsync failed') from exc
    finally:
        if directory_fd is not None:
            os.close(directory_fd)
        if temporary is not None:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass
    return len(raw)


def read_bounded(path, *, max_wire_bytes=1048576):
    """Read at most cap+1 bytes before decode; trusted regular-file paths only."""
    _limit(max_wire_bytes)
    with open(path, 'rb') as stream:
        raw = stream.read(max_wire_bytes + 1)
    if len(raw) > max_wire_bytes:
        raise OverflowError('wire byte budget')
    return raw


def load_file(path, *, max_wire_bytes=1048576, **limits):
    return load_history(read_bounded(path, max_wire_bytes=max_wire_bytes),
                        max_wire_bytes=max_wire_bytes, **limits)


def restore_file(target, path, *, max_wire_bytes=1048576):
    return restore_history(target, read_bounded(path, max_wire_bytes=max_wire_bytes),
                           max_wire_bytes=max_wire_bytes)
