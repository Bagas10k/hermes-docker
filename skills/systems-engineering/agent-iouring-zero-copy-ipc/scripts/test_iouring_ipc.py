#!/usr/bin/env python3
"""
Deterministic Unit Tests for Linux io_uring Zero-Copy IPC & SQ/CQ Engine
Menguji invariant SQ/CQ ring buffer, zero-copy socket transfers, dan batching throughput.
"""

import unittest
import socket
import errno
import time
from iouring_ipc_engine import (
    IOUringIPCEngine, SQE, CQE,
    IORING_OP_NOP, IORING_OP_SOCKET_SEND, IORING_OP_SOCKET_RECV
)

class TestIOUringIPC(unittest.TestCase):

    def setUp(self):
        self.ring = IOUringIPCEngine(entries=32)
        self.s1, self.s2 = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
        self.ring.register_socket(self.s1)
        self.ring.register_socket(self.s2)

    def tearDown(self):
        self.ring.unregister_socket(self.s1)
        self.ring.unregister_socket(self.s2)
        self.s1.close()
        self.s2.close()

    def test_01_power_of_two_enforcement(self):
        """Ukuran ring buffer wajib merupakan power-of-two (2^N)."""
        with self.assertRaises(ValueError):
            IOUringIPCEngine(entries=30)
        valid_ring = IOUringIPCEngine(entries=64)
        self.assertEqual(valid_ring.ring_size, 64)

    def test_02_nop_batch_submission(self):
        """Menguji submission NOP ops secara batch tanpa interupsi."""
        for i in range(10):
            ok = self.ring.prep_nop(user_data=1000 + i)
            self.assertTrue(ok)
        
        self.assertEqual(self.ring.get_pending_sq(), 10)
        submitted = self.ring.submit_and_wait()
        self.assertEqual(submitted, 10)
        self.assertEqual(self.ring.get_pending_sq(), 0)
        self.assertEqual(self.ring.get_available_cq(), 10)

        # Verifikasi keteraturan CQE
        for i in range(10):
            cqe = self.ring.peek_cqe()
            self.assertIsNotNone(cqe)
            self.assertEqual(cqe.user_data, 1000 + i)
            self.assertEqual(cqe.res, 0)
            self.ring.advance_cq(1)
        
        self.assertEqual(self.ring.get_available_cq(), 0)

    def test_03_zero_copy_socket_rpc_transfer(self):
        """Menguji transfer payload biner antar-agen via socket pair asinkron."""
        payload = b'{"jsonrpc": "2.0", "method": "agent_heartbeat", "id": 42}'
        
        # 1. Submit SEND SQE dari s1
        ok = self.ring.prep_send(self.s1.fileno(), payload, user_data=42)
        self.assertTrue(ok)
        
        submitted = self.ring.submit_and_wait()
        self.assertEqual(submitted, 1)
        
        cqe = self.ring.peek_cqe()
        self.assertIsNotNone(cqe)
        self.assertEqual(cqe.user_data, 42)
        self.assertEqual(cqe.res, len(payload))
        self.ring.advance_cq(1)

        # 2. Submit RECV SQE di s2
        ok = self.ring.prep_recv(self.s2.fileno(), length=1024, user_data=43)
        self.assertTrue(ok)
        
        submitted = self.ring.submit_and_wait()
        self.assertEqual(submitted, 1)
        
        cqe_recv = self.ring.peek_cqe()
        self.assertIsNotNone(cqe_recv)
        self.assertEqual(cqe_recv.user_data, 43)
        self.assertEqual(cqe_recv.res, len(payload))
        self.ring.advance_cq(1)

    def test_04_error_handling_unregistered_fd(self):
        """Memverifikasi penanganan deskriptor berkas tidak dikenal (EBADF)."""
        ok = self.ring.prep_send(fd=9999, data=b"FAIL", user_data=99)
        self.assertTrue(ok)
        self.ring.submit_and_wait()
        
        cqe = self.ring.peek_cqe()
        self.assertIsNotNone(cqe)
        self.assertEqual(cqe.res, -errno.EBADF)
        self.ring.advance_cq(1)

    def test_05_ring_full_backpressure(self):
        """Memverifikasi backpressure ketika SQ mencapai kapasitas maksimum."""
        small_ring = IOUringIPCEngine(entries=4)
        for i in range(4):
            self.assertTrue(small_ring.prep_nop(user_data=i))
        # SQE ke-5 wajib ditolak karena antrean penuh
        self.assertFalse(small_ring.prep_nop(user_data=5))

    def test_06_batch_throughput_benchmark(self):
        """Benchmark deterministik: memproses batch SQE dalam hitungan mikrodetik."""
        ring = IOUringIPCEngine(entries=64)
        batch_size = 50
        
        t0 = time.perf_counter()
        for i in range(batch_size):
            ring.prep_nop(user_data=i)
        ring.submit_and_wait()
        t1 = time.perf_counter()
        
        duration_us = (t1 - t0) * 1_000_000
        per_op_us = duration_us / batch_size
        # Validasi batas performa: per-op wajib di bawah 50 mikrodetik di VPS
        self.assertLess(per_op_us, 50.0)

if __name__ == "__main__":
    unittest.main()
