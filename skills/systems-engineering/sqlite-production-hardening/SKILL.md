---
name: sqlite-production-hardening
description: Hardening SQLite WAL, concurrency, and online zero-downtime backup.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [sqlite, wal, concurrency, database, backup, recovery, reliability]
    related_skills: [database-design-migrations, autonomous-engineering-craft]
---

# SQLite Production Hardening & High-Concurrency Recovery

Enterprise production hardening, connection pooling guidelines, WAL concurrency tuning, and zero-downtime live backups for embedded SQLite databases.

## When to Use

- Configuring embedded SQLite for multi-process or high-concurrency Node.js/Python microservices.
- Resolving `SQLITE_BUSY`, `SQLITE_BUSY_SNAPSHOT`, or database lock errors under concurrent read/write loads.
- Implementing zero-downtime live online database backups without blocking writers or corrupting WAL files.
- Enforcing schema integrity, transactional foreign keys, and preventing silent cascade data loss (`REPLACE` vs `UPSERT`).
- Do NOT use for: Distributed multi-node clustered databases (use PostgreSQL/Supabase with Cockroach or Citus).

## Prerequisites

- Python 3.8+ (`sqlite3` standard library with `sqlite3_backup` support) or Node.js (`better-sqlite3`).
- Host filesystem supporting POSIX advisory locking or Windows share modes.
- Shared memory (`-shm`) and Write-Ahead Log (`-wal`) permissions matching base database file.

## Quick Reference

```bash
# Recommended production pragma bootstrap
python3 -c "
import sqlite3
conn = sqlite3.connect('app.db', timeout=5.0)
conn.execute('PRAGMA journal_mode = WAL;')
conn.execute('PRAGMA synchronous = NORMAL;')
conn.execute('PRAGMA busy_timeout = 5000;')
conn.execute('PRAGMA foreign_keys = ON;')
conn.execute('PRAGMA temp_store = MEMORY;')
conn.execute('PRAGMA mmap_size = 268435456;') # 256MB
conn.commit()
"

# Online live backup execution without lock contention
python3 ~/.hermes/skills/systems-engineering/sqlite-production-hardening/scripts/sqlite_backup.py backup --src app.db --dst backup.db
```

## Production Pragma Rules

1. `PRAGMA journal_mode = WAL;`
   - Persistent database property. Allows concurrent multiple readers alongside one writer without mutual blocking.
2. `PRAGMA synchronous = NORMAL;`
   - In WAL mode, `NORMAL` guarantees database integrity across process crashes and system power losses while eliminating fsync stalls on every single write commit.
3. `PRAGMA busy_timeout = 5000;`
   - Connection-scoped. Must be executed on EVERY new connection. Ensures SQLite internally waits and retries up to 5000ms before returning `SQLITE_BUSY`.
4. `PRAGMA foreign_keys = ON;`
   - Connection-scoped. Disabled by default in SQLite. Must be enabled immediately upon connection establishment before executing queries.
5. `PRAGMA temp_store = MEMORY;`
   - Keeps intermediate temporary tables and indices in RAM, reducing disk I/O load.
6. `PRAGMA mmap_size = 268435456;` (256 MB)
   - Enables memory-mapped I/O for read queries, bypassing user-space buffer copy overhead.

## Procedure

### 1. Connection Initialization Contract

Every SQLite database wrapper must apply the baseline configuration hook prior to handling queries:

```python
import sqlite3

def create_hardened_connection(db_path: str, timeout: float = 5.0) -> sqlite3.Connection:
    conn = sqlite3.connect(
        db_path,
        timeout=timeout,
        isolation_level=None # Explicit transaction control
    )
    # Essential PRAGMAs
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA busy_timeout = 5000;")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA temp_store = MEMORY;")
    conn.execute("PRAGMA mmap_size = 268435456;")
    return conn
```

### 2. Handling Immediate Transactions to Prevent `BUSY_SNAPSHOT`

When performing read-then-write workflows, a deferred transaction (`BEGIN DEFERRED`) starts as a shared lock. If two connections attempt to upgrade to a write lock concurrently, SQLite aborts the second with `SQLITE_BUSY_SNAPSHOT`.

- **Rule**: Start write transactions with `BEGIN IMMEDIATE` or `BEGIN EXCLUSIVE` to acquire write reservations immediately.

```python
def execute_write_transaction(conn: sqlite3.Connection, fn):
    retries = 3
    backoff = 0.05
    for attempt in range(retries):
        try:
            conn.execute("BEGIN IMMEDIATE;")
            result = fn(conn)
            conn.execute("COMMIT;")
            return result
        except sqlite3.OperationalError as e:
            conn.execute("ROLLBACK;")
            if "busy" in str(e).lower() and attempt < retries - 1:
                import time, random
                time.sleep(backoff + random.uniform(0.01, 0.05))
                backoff *= 2
                continue
            raise
```

### 3. Avoiding Cascade Deletion with `INSERT OR REPLACE`

- **Pitfall**: `INSERT OR REPLACE INTO table ...` executes a `DELETE` followed by `INSERT`. This triggers foreign key `ON DELETE CASCADE` actions and changes rowids.
- **Rule**: Always use modern `INSERT INTO ... ON CONFLICT(col) DO UPDATE SET ...` (UPSERT).

```sql
-- DANGEROUS:
INSERT OR REPLACE INTO users (id, name, score) VALUES (1, 'Alice', 100);

-- SAFE (UPSERT):
INSERT INTO users (id, name, score) VALUES (1, 'Alice', 100)
ON CONFLICT(id) DO UPDATE SET score = excluded.score;
```

### 4. Zero-Downtime Live Online Backup

Never copy the `.db` file using `cp` while processes are writing in WAL mode; the resulting copy will miss uncheckpointed `-wal` transactions or be corrupted.

- Use the SQLite Online Backup API (`sqlite3_backup`):

```python
def backup_live_db(src_conn: sqlite3.Connection, target_file: str, pages_per_step: int = 250):
    dest_conn = sqlite3.connect(target_file)
    src_conn.backup(dest_conn, pages=pages_per_step, sleep=0.005)
    dest_conn.close()
```

## Pitfalls

1. **Copying `.db` without `-wal` and `-shm`**:
   - In WAL mode, latest committed writes reside in `-wal`. Direct OS copies (`cp db.sqlite backup.sqlite`) produce stale or corrupted states. Always use `sqlite3_backup` API or execute `PRAGMA wal_checkpoint(TRUNCATE)` before freezing files.
2. **Network Filesystem Locking (NFS / SMB / CIFS)**:
   - SQLite WAL mode relies on shared memory (`-shm`) backed by POSIX shared memory or memory-mapped files. Network filesystems frequently break POSIX locking semantics, leading to database corruption. Keep SQLite databases on local NVMe/SSD storage.
3. **`PRAGMA foreign_keys` Inside Transactions**:
   - Running `PRAGMA foreign_keys = ON;` inside an active transaction is a no-op. It must be executed before opening transactions.
4. **Multiple Writers in Separate Threads**:
   - SQLite serializes all writes across connections. For optimal throughput in high-concurrency systems, dedicate a single writer queue or background worker, allowing unlimited parallel readers.

## Verification

1. Verify WAL and Pragmas:
   ```bash
   python3 -c "
   import sqlite3
   c = sqlite3.connect('test.db')
   assert c.execute('PRAGMA journal_mode=WAL').fetchone()[0] == 'wal'
   assert c.execute('PRAGMA busy_timeout=5000').fetchone() is not None
   assert c.execute('PRAGMA foreign_keys=ON').fetchone() is not None
   print('VERIFICATION: PASS')
   "
   ```
2. Verify online backup functionality with concurrent writes:
   Run `python3 ~/.hermes/skills/systems-engineering/sqlite-production-hardening/scripts/sqlite_backup.py test`.
