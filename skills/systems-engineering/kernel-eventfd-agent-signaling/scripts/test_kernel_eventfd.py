#!/usr/bin/env python3
"""
test_kernel_eventfd.py - Unit test suite for kernel-eventfd-agent-signaling
"""

import os
import sys
import time
import errno
import unittest
import multiprocessing

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kernel_eventfd import EventFd, EventChannel, benchmark_eventfd

class TestKernelEventFd(unittest.TestCase):

    def test_01_creation_and_close(self):
        """Test proper creation, file descriptor allocation, and cleanup."""
        efd = EventFd()
        self.assertGreaterEqual(efd.fd, 0)
        self.assertFalse(efd.is_closed)
        fd_val = efd.fd
        efd.close()
        self.assertTrue(efd.is_closed)
        
        # Verify subsequent operations fail
        with self.assertRaises(ValueError):
            efd.notify(1)
        with self.assertRaises(ValueError):
            efd.wait(0)

    def test_02_basic_notify_and_read(self):
        """Test write counter accumulation and read reset behavior."""
        with EventFd(nonblock=True) as efd:
            efd.notify(1)
            efd.notify(2)
            efd.notify(3)
            # In counter mode (non-semaphore), read returns accumulated sum (1+2+3 = 6)
            val = efd.wait(timeout_sec=0.1)
            self.assertEqual(val, 6)
            
            # Immediately reading again should return 0 (EAGAIN)
            val2 = efd.try_read()
            self.assertEqual(val2, 0)

    def test_03_semaphore_mode(self):
        """Test EFD_SEMAPHORE flag: each read returns 1 and decrements counter by 1."""
        with EventFd(semaphore=True, nonblock=True) as efd:
            efd.notify(3)
            # Read 1
            self.assertEqual(efd.try_read(), 1)
            # Read 2
            self.assertEqual(efd.try_read(), 1)
            # Read 3
            self.assertEqual(efd.try_read(), 1)
            # Read 4 (empty)
            self.assertEqual(efd.try_read(), 0)

    def test_04_timeout_behavior(self):
        """Test wait timeout returns 0 without blocking indefinitely."""
        with EventFd(nonblock=True) as efd:
            t0 = time.perf_counter()
            val = efd.wait(timeout_sec=0.05)
            t1 = time.perf_counter()
            self.assertEqual(val, 0)
            self.assertGreaterEqual(t1 - t0, 0.04)

    def test_05_multiprocess_signaling(self):
        """Test eventfd signaling across separate OS processes via inherited/shared FD."""
        with EventFd(nonblock=False) as efd_p2c, EventFd(nonblock=False) as efd_c2p:
            fd_p2c = efd_p2c.fd
            fd_c2p = efd_c2p.fd

            def child_worker(recv_fd, send_fd):
                c_recv = EventFd(fd=recv_fd, nonblock=False)
                c_send = EventFd(fd=send_fd, nonblock=False)
                val = c_recv.wait(timeout_sec=2.0)
                if val == 42:
                    c_send.notify(100)

            proc = multiprocessing.Process(target=child_worker, args=(fd_p2c, fd_c2p))
            proc.start()

            efd_p2c.notify(42)
            resp = efd_c2p.wait(timeout_sec=2.0)
            proc.join(timeout=2.0)

            self.assertEqual(resp, 100)

    def test_06_channel_abstraction_and_stats(self):
        """Test high-level EventChannel abstraction and telemetry accounting."""
        channel = EventChannel()
        self.assertEqual(channel.stats["signals_sent"], 0)
        self.assertEqual(channel.stats["signals_received"], 0)

        channel.emit(5)
        channel.emit(10)
        self.assertEqual(channel.stats["signals_sent"], 2)

        res = channel.poll(timeout=0.05)
        self.assertEqual(res, 15)
        self.assertEqual(channel.stats["signals_received"], 1)
        self.assertEqual(channel.stats["events_processed"], 15)

        channel.close()

    def test_07_invalid_inputs(self):
        """Test boundary conditions and input validation."""
        with EventFd(nonblock=True) as efd:
            with self.assertRaises(ValueError):
                efd.notify(0)
            with self.assertRaises(ValueError):
                efd.notify(-5)
            with self.assertRaises(ValueError):
                efd.notify(0xFFFFFFFFFFFFFFFFFF)

if __name__ == "__main__":
    unittest.main()
