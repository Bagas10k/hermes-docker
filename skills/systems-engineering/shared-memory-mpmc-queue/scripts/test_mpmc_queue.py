#!/usr/bin/env python3
"""
Deterministic Unit Tests for Lock-Free MPMC Bounded Ring-Buffer
Menguji invarian multi-producer multi-consumer, FIFO ordering, backpressure, dan throughput konkuren.
"""

import unittest
import threading
import time
from mpmc_queue import LockFreeMPMCQueue

class TestLockFreeMPMCQueue(unittest.TestCase):

    def test_01_power_of_two_enforcement(self):
        """Kapasitas wajib power of two (2^N)."""
        with self.assertRaises(ValueError):
            LockFreeMPMCQueue(capacity=10)
        q = LockFreeMPMCQueue(capacity=16)
        self.assertEqual(q.capacity, 16)

    def test_02_fifo_order_and_empty(self):
        """Verifikasi urutan FIFO dan penanganan antrean kosong."""
        q = LockFreeMPMCQueue(capacity=8)
        self.assertIsNone(q.pop())
        self.assertTrue(q.is_empty())

        q.push(b"item_1")
        q.push(b"item_2")
        q.push(b"item_3")

        self.assertEqual(q.pop(), b"item_1")
        self.assertEqual(q.pop(), b"item_2")
        self.assertEqual(q.pop(), b"item_3")
        self.assertIsNone(q.pop())
        self.assertTrue(q.is_empty())

    def test_03_queue_full_backpressure(self):
        """Verifikasi backpressure saat antrean mencapai kapasitas maksimum."""
        q = LockFreeMPMCQueue(capacity=4)
        for i in range(4):
            self.assertTrue(q.push(f"data_{i}".encode()))
        
        # Item ke-5 wajib ditolak (False)
        self.assertFalse(q.push(b"overflow_item"))

        # Setelah 1 item diambil, push harus kembali berhasil
        self.assertEqual(q.pop(), b"data_0")
        self.assertTrue(q.push(b"new_item"))

    def test_04_concurrent_mpmc_correctness(self):
        """Menguji 4 thread produser dan 4 thread konsumen berjalan simultan tanpa data hilang."""
        capacity = 32
        q = LockFreeMPMCQueue(capacity=capacity)
        items_per_producer = 250
        num_producers = 4
        total_items = num_producers * items_per_producer
        
        received_items = []
        rec_lock = threading.Lock()

        def producer_worker(prod_id):
            for i in range(items_per_producer):
                payload = f"p{prod_id}_{i}".encode()
                while not q.push(payload):
                    time.sleep(0.0001)

        def consumer_worker():
            while True:
                item = q.pop()
                if item is not None:
                    with rec_lock:
                        received_items.append(item)
                        if len(received_items) == total_items:
                            break
                else:
                    with rec_lock:
                        if len(received_items) >= total_items:
                            break
                    time.sleep(0.0001)

        # Jalankan produser & konsumen bersamaan
        prods = [threading.Thread(target=producer_worker, args=(i,)) for i in range(num_producers)]
        cons = [threading.Thread(target=consumer_worker) for _ in range(4)]

        for c in cons:
            c.start()
        for p in prods:
            p.start()

        for p in prods:
            p.join(timeout=5.0)
        for c in cons:
            c.join(timeout=5.0)

        # Verifikasi bahwa SELURUH 1000 item diterima lengkap tanpa satupun yang hilang
        self.assertEqual(len(received_items), total_items)
        self.assertEqual(len(set(received_items)), total_items)

    def test_05_payload_size_boundary(self):
        """Memverifikasi penolakan data yang melebihi kapasitas buffer slot 256-byte."""
        q = LockFreeMPMCQueue(capacity=8)
        oversized = b"X" * 257
        with self.assertRaises(ValueError):
            q.push(oversized)

if __name__ == "__main__":
    unittest.main()
