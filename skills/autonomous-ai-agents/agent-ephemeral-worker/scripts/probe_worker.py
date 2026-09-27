import os
import sys
import time
import shutil
import tempfile
import unittest
from pathlib import Path

class EphemeralWorkerSandbox:
    def __init__(self, worker_id: str, memory_limit_mb: int = 128, timeout_s: float = 2.0):
        self.worker_id = worker_id
        self.memory_limit_mb = memory_limit_mb
        self.timeout_s = timeout_s
        self.base_dir = tempfile.mkdtemp(prefix=f"ephemeral_worker_{worker_id}_")
        self.is_active = True
        self.allocated_bytes = 0

    def write_file(self, rel_path: str, data: bytes):
        if not self.is_active:
            raise RuntimeError("Worker sandbox has been disposed.")
        target = Path(self.base_dir) / rel_path
        if not target.resolve().is_relative_to(Path(self.base_dir).resolve()):
            raise ValueError("Path traversal attempt blocked.")
        
        # Enforce memory/disk limit
        if self.allocated_bytes + len(data) > self.memory_limit_mb * 1024 * 1024:
            raise MemoryError("Worker memory/scratchpad quota exceeded.")
        
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        self.allocated_bytes += len(data)

    def execute_task(self, task_func):
        if not self.is_active:
            raise RuntimeError("Worker sandbox has been disposed.")
        start = time.perf_counter()
        try:
            result = task_func(self.base_dir)
            elapsed = time.perf_counter() - start
            if elapsed > self.timeout_s:
                raise TimeoutError(f"Task exceeded execution timeout of {self.timeout_s}s")
            return {"status": "success", "result": result, "elapsed_s": elapsed}
        except Exception as e:
            return {"status": "failed", "error": str(e), "elapsed_s": time.perf_counter() - start}

    def dispose(self):
        if self.is_active:
            self.is_active = False
            shutil.rmtree(self.base_dir, ignore_errors=True)

class TestEphemeralWorkerSandbox(unittest.TestCase):
    def test_sandbox_lifecycle(self):
        worker = EphemeralWorkerSandbox("test_01", memory_limit_mb=10, timeout_s=1.0)
        self.assertTrue(os.path.exists(worker.base_dir))
        
        # Write within bounds
        worker.write_file("sub/test.txt", b"hello ephemeral worker")
        read_back = (Path(worker.base_dir) / "sub/test.txt").read_bytes()
        self.assertEqual(read_back, b"hello ephemeral worker")

        # Execute task
        res = worker.execute_task(lambda d: len(os.listdir(d)))
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["result"], 1)

        # Dispose and verify zero leak
        path = worker.base_dir
        worker.dispose()
        self.assertFalse(os.path.exists(path))
        self.assertFalse(worker.is_active)
        
        # Operation after disposal must fail
        with self.assertRaises(RuntimeError):
            worker.write_file("fail.txt", b"data")

    def test_path_traversal_barrier(self):
        worker = EphemeralWorkerSandbox("test_traversal", memory_limit_mb=10)
        try:
            with self.assertRaises(ValueError):
                worker.write_file("../escape.txt", b"forbidden")
        finally:
            worker.dispose()

    def test_quota_exhaustion_barrier(self):
        worker = EphemeralWorkerSandbox("test_quota", memory_limit_mb=1) # 1 MB
        try:
            with self.assertRaises(MemoryError):
                worker.write_file("large.bin", b"X" * (2 * 1024 * 1024))
        finally:
            worker.dispose()

if __name__ == "__main__":
    unittest.main()
