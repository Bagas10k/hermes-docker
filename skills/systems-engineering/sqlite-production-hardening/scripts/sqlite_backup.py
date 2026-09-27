#!/usr/bin/env python3
"""
Zero-downtime online backup helper for SQLite WAL databases.
"""
import argparse
import os
import sqlite3
import sys
import time

def perform_backup(src_path: str, dst_path: str, pages: int = 100, sleep_sec: float = 0.005) -> bool:
    if not os.path.exists(src_path):
        print(f"Error: Source database '{src_path}' does not exist.", file=sys.stderr)
        return False

    temp_dst = dst_path + ".tmp"
    if os.path.exists(temp_dst):
        try:
            os.remove(temp_dst)
        except OSError:
            pass

    src_conn = None
    dst_conn = None
    try:
        src_conn = sqlite3.connect(src_path, timeout=10.0)
        dst_conn = sqlite3.connect(temp_dst)
        
        # Stream backup page by page to leave headroom for active writers
        src_conn.backup(dst_conn, pages=pages, sleep=sleep_sec)
        
        dst_conn.close()
        src_conn.close()

        # Atomic rename
        os.replace(temp_dst, dst_path)
        print(f"Successfully backed up '{src_path}' to '{dst_path}'")
        return True
    except Exception as e:
        print(f"Backup failed: {e}", file=sys.stderr)
        if os.path.exists(temp_dst):
            try:
                os.remove(temp_dst)
            except OSError:
                pass
        return False
    finally:
        if dst_conn:
            try: dst_conn.close()
            except: pass
        if src_conn:
            try: src_conn.close()
            except: pass

def self_test():
    import tempfile
    src = tempfile.mktemp(suffix=".db")
    dst = tempfile.mktemp(suffix="_backup.db")
    
    conn = sqlite3.connect(src)
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("CREATE TABLE records (id INTEGER PRIMARY KEY, value TEXT);")
    conn.executemany("INSERT INTO records (value) VALUES (?);", [(f"item_{i}",) for i in range(500)])
    conn.commit()

    success = perform_backup(src, dst, pages=50, sleep_sec=0.001)
    if not success:
        print("Self test failed: perform_backup returned False", file=sys.stderr)
        sys.exit(1)

    verify_conn = sqlite3.connect(dst)
    count = verify_conn.execute("SELECT COUNT(*) FROM records;").fetchone()[0]
    verify_conn.close()
    conn.close()

    for p in [src, src + "-wal", src + "-shm", dst]:
        if os.path.exists(p):
            try: os.remove(p)
            except: pass

    if count == 500:
        print("SELF-TEST: PASS (Verified 500 records restored)")
        sys.exit(0)
    else:
        print(f"SELF-TEST: FAIL (Expected 500 records, got {count})", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="SQLite Online Backup CLI")
    subparsers = parser.add_subparsers(dest="command")

    backup_parser = subparsers.add_parser("backup", help="Run online backup")
    backup_parser.add_argument("--src", required=True, help="Source database file")
    backup_parser.add_argument("--dst", required=True, help="Destination backup file")
    backup_parser.add_argument("--pages", type=int, default=100, help="Pages per step (default: 100)")
    backup_parser.add_argument("--sleep", type=float, default=0.005, help="Sleep interval in seconds (default: 0.005)")

    subparsers.add_parser("test", help="Run self-test verification")

    args = parser.parse_args()
    if args.command == "backup":
        success = perform_backup(args.src, args.dst, pages=args.pages, sleep_sec=args.sleep)
        sys.exit(0 if success else 1)
    elif args.command == "test":
        self_test()
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
