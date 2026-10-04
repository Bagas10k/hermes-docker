"""Single-writer local snapshots; directory durability, not power-cut proof."""
import json
import os
from pathlib import Path
import tempfile
from fingerprint_migration import migrate_records


class SnapshotDurabilityError(RuntimeError):
    """Publication succeeded via os.replace, but parent directory fsync failed.

    Target path contains valid complete data, but persistence across power
    loss is not assured by the local filesystem.
    """


def save_snapshot(path, records):
    """Validate/migrate before I/O; publish a complete JSON file by rename.

    Parent must already exist and be trusted. No concurrent writers or hostile
    path mutations are supported. Flushes and fsyncs temporary file data,
    atomically replaces target path, then opens and fsyncs the parent directory.
    If directory fsync fails after replace, raises SnapshotDurabilityError.
    Existing files are replaced with owner-only permissions. Failure before
    replace preserves the old target and unlinks temporary files.
    """
    target = Path(path)
    migrated = migrate_records(records)
    payload = (json.dumps({'schema_version': 1, 'records': migrated},
                          ensure_ascii=True, sort_keys=True, separators=(',', ':'),
                          allow_nan=False) + '\n').encode('utf-8')
    temp = None
    try:
        with tempfile.NamedTemporaryFile(mode='wb', prefix='.snapshot-',
                                         dir=target.parent, delete=False) as stream:
            temp = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, target)
        temp = None
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)

    # Sync directory entry to persist link mutation
    dir_fd = os.open(str(target.parent), os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
    try:
        os.fsync(dir_fd)
    except OSError as err:
        raise SnapshotDurabilityError(
            f"Snapshot published to '{target}', but parent directory fsync failed: {err}"
        ) from err
    finally:
        os.close(dir_fd)

    return {'schema_version': 1, 'records': migrated}
