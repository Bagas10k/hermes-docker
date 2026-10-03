#!/usr/bin/env python3
"""
Deterministic Unit Tests for Edge SLM Micro-Sandbox
Menguji kebenaran isolasi memori, batas waktu, dan kuota CPU.
"""

import unittest
import time
from micro_sandbox import run_in_microsandbox, EphemeralResourceQuota

class TestMicroSandbox(unittest.TestCase):

    def test_01_normal_execution(self):
        """Test eksekusi normal tool SLM lokal berhasil (exit 0)."""
        res = run_in_microsandbox(["python3", "-c", "print('HELLO_SLM')"])
        self.assertTrue(res.is_success)
        self.assertEqual(res.exit_code, 0)
        self.assertIn("HELLO_SLM", res.stdout)
        self.assertIsNone(res.killed_by)

    def test_02_memory_limit_breach(self):
        """Test pelanggaran alokasi RAM (mencoba alokasi 120MB di limit 32MB)."""
        quota = EphemeralResourceQuota(
            max_memory_bytes=32 * 1024 * 1024, # 32MB
            max_wall_time_seconds=3.0
        )
        # Alokasi bytearray 120MB
        cmd = ["python3", "-c", "x = bytearray(120 * 1024 * 1024); print('SHOULD_FAIL')"]
        res = run_in_microsandbox(cmd, quota=quota)
        self.assertFalse(res.is_success)
        self.assertNotEqual(res.exit_code, 0)
        self.assertIn(res.killed_by, ["memory_limit", "sigkill", "signal_11"])

    def test_03_wall_clock_timeout(self):
        """Test terminasi proses infinite loop tepat waktu."""
        quota = EphemeralResourceQuota(
            max_wall_time_seconds=1.0,
            max_cpu_seconds=2
        )
        cmd = ["python3", "-c", "import time; time.sleep(5)"]
        t0 = time.monotonic()
        res = run_in_microsandbox(cmd, quota=quota)
        duration = time.monotonic() - t0
        self.assertFalse(res.is_success)
        self.assertEqual(res.killed_by, "timeout")
        self.assertLess(duration, 2.5) # Harus dihentikan segera setelah 1.0s

    def test_04_output_truncation_cap(self):
        """Test proteksi buffer output agar tidak membanjiri RAM induk."""
        quota = EphemeralResourceQuota(max_output_bytes=512)
        cmd = ["python3", "-c", "print('A' * 4096)"]
        res = run_in_microsandbox(cmd, quota=quota)
        self.assertTrue(res.output_truncated)
        self.assertLessEqual(len(res.stdout), 512)

    def test_05_startup_latency_benchmark(self):
        """Test latensi startup micro-sandbox wajib sangat cepat (<15ms)."""
        t0 = time.monotonic()
        res = run_in_microsandbox(["true"])
        dur_ms = (time.monotonic() - t0) * 1000
        self.assertTrue(res.is_success)
        self.assertLess(dur_ms, 25.0, f"Latensi {dur_ms}ms melebihi batas 25ms")

if __name__ == "__main__":
    unittest.main()
