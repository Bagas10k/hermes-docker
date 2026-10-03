#!/usr/bin/env python3
"""
test_hybrid_eventfd_shm_ipc.py - Unit test suite for hybrid-eventfd-shm-ipc
"""

import os
import sys
import time
import unittest
import multiprocessing as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hybrid_eventfd_shm_ipc import HybridEventFdShmQueue, KernelEventFd

class TestHybridEventFdShmIpc(unittest.TestCase):

    def test_01_power_of_two_and_init(self):
        """Test capacity validation and power-of-two requirement."""
        with self.assertRaises(ValueError):
            HybridEventFdShmQueue(capacity=10)
        with self.assertRaises(ValueError):
            HybridEventFdShmQueue(capacity=0)

        q = HybridEventFdShmQueue(capacity=32)
        self.assertEqual(q.capacity, 32)
        self.assertEqual(q.mask, 31)
        q.close()

    def test_02_single_producer_consumer_roundtrip(self):
        """Test basic push, notification, and pop data integrity."""
        q = HybridEventFdShmQueue(capacity=16)
        payload = b"agent_heartbeat_payload_123"
        
        ok = q.push(payload, notify=True)
        self.assertTrue(ok)

        recv = q.pop(timeout_sec=0.1)
        self.assertEqual(recv, payload)

        # Queue should be empty now
        self.assertIsNone(q.try_pop())
        q.close()

    def test_03_zero_cpu_idle_timeout(self):
        """Test wait timeout when queue is empty terminates accurately."""
        q = HybridEventFdShmQueue(capacity=16)
        t0 = time.perf_counter()
        val = q.pop(timeout_sec=0.05)
        t1 = time.perf_counter()

        self.assertIsNone(val)
        self.assertGreaterEqual(t1 - t0, 0.045)
        q.close()

    def test_04_buffer_full_backpressure(self):
        """Test queue backpressure when pushing beyond capacity."""
        q = HybridEventFdShmQueue(capacity=4)
        for i in range(4):
            self.assertTrue(q.push(f"msg_{i}".encode(), notify=False))
        
        # 5th push must fail (backpressure)
        self.assertFalse(q.push(b"overflow_msg", notify=False))

        # Drain one item, then push must succeed
        self.assertEqual(q.try_pop(), b"msg_0")
        self.assertTrue(q.push(b"recovered_msg", notify=False))
        q.close()

    def test_05_concurrent_multiprocess_mpmc(self):
        """Test concurrent multi-process producer and consumer data integrity."""
        q = HybridEventFdShmQueue(capacity=64)
        num_items_per_producer = 100
        num_producers = 3
        num_consumers = 3
        total_items = num_producers * num_items_per_producer

        def producer_worker(queue, prod_id):
            for i in range(num_items_per_producer):
                msg = f"P{prod_id}:{i}".encode()
                while not queue.push(msg, notify=True):
                    time.sleep(0.001)

        manager = mp.Manager()
        results = manager.list()

        def consumer_worker(queue, out_list):
            while len(out_list) < total_items:
                item = queue.pop(timeout_sec=0.1)
                if item is not None:
                    out_list.append(item)

        producers = [mp.Process(target=producer_worker, args=(q, p)) for p in range(num_producers)]
        consumers = [mp.Process(target=consumer_worker, args=(q, results)) for p in range(num_consumers)]

        for c in consumers:
            c.start()
        for p in producers:
            p.start()

        for p in producers:
            p.join(timeout=3.0)
        
        deadline = time.time() + 3.0
        while len(results) < total_items and time.time() < deadline:
            time.sleep(0.05)

        for c in consumers:
            c.terminate()

        self.assertEqual(len(results), total_items)
        # Verify no items corrupted or lost
        decoded = [item.decode() for item in results]
        for p in range(num_producers):
            for i in range(num_items_per_producer):
                self.assertIn(f"P{p}:{i}", decoded)

        q.close()

    def test_06_payload_size_limit(self):
        """Test validation of payload limit (256 bytes)."""
        q = HybridEventFdShmQueue(capacity=16)
        oversized = b"X" * 257
        with self.assertRaises(ValueError):
            q.push(oversized)
        
        exact = b"Y" * 256
        self.assertTrue(q.push(exact))
        self.assertEqual(q.pop(timeout_sec=0.01), exact)
        q.close()

if __name__ == "__main__":
    unittest.main()
