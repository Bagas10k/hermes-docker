import os
import unittest
import struct
import time
from shm_ring_buffer import (
    SharedMemoryRingBuffer,
    HEADER_MAGIC,
    HEADER_VERSION,
    HEADER_SIZE,
    SLOT_HEADER_SIZE
)


class TestSharedMemoryRingBuffer(unittest.TestCase):
    def setUp(self):
        self.shm_name = f"test_ring_{os.getpid()}_{int(time.time()*1000)%100000}"
        self.ring = SharedMemoryRingBuffer(
            self.shm_name,
            capacity=16,
            slot_size=128,
            create=True
        )

    def tearDown(self):
        if self.ring:
            self.ring.unlink()

    def test_power_of_two_enforcement(self):
        """Test invariant: capacity and slot_size must be powers of 2."""
        with self.assertRaises(ValueError):
            SharedMemoryRingBuffer("invalid_cap", capacity=15, slot_size=128, create=True)
        with self.assertRaises(ValueError):
            SharedMemoryRingBuffer("invalid_slot", capacity=16, slot_size=100, create=True)

    def test_single_push_and_pop(self):
        """Test push single item, verify exact payload and metadata, then pop."""
        payload = b"TEST_PAYLOAD_DATA_XYZ"
        success, seq = self.ring.push(metric_type=42, payload=payload)
        self.assertTrue(success)
        self.assertEqual(seq, 0)

        # Check stats
        stats = self.ring.stats()
        self.assertEqual(stats["write_seq"], 1)
        self.assertEqual(stats["read_seq"], 0)
        self.assertEqual(stats["unconsumed_count"], 1)

        # Pop
        item = self.ring.pop()
        self.assertIsNotNone(item)
        self.assertEqual(item["seq"], 0)
        self.assertEqual(item["metric_type"], 42)
        self.assertEqual(item["payload"], payload)
        self.assertEqual(item["len"], len(payload))

        # Second pop should be empty
        self.assertIsNone(self.ring.pop())

    def test_capacity_overflow_backpressure(self):
        """Test buffer full condition: cannot push when write_seq - read_seq >= capacity."""
        for i in range(16):
            success, seq = self.ring.push(metric_type=i, payload=f"MSG_{i}".encode())
            self.assertTrue(success)
            self.assertEqual(seq, i)

        # 17th push must fail (backpressure)
        success, seq = self.ring.push(metric_type=99, payload=b"OVERFLOW")
        self.assertFalse(success)
        self.assertEqual(seq, 16)

        # Pop 1 item
        popped = self.ring.pop()
        self.assertEqual(popped["metric_type"], 0)

        # Now push should succeed
        success, seq = self.ring.push(metric_type=99, payload=b"RECOVERED")
        self.assertTrue(success)
        self.assertEqual(seq, 16)

    def test_peek_latest_without_popping(self):
        """Test peek_latest returns newest entry without advancing read cursor."""
        self.assertIsNone(self.ring.peek_latest())
        self.ring.push(1, b"FIRST")
        self.ring.push(2, b"SECOND")

        peeked = self.ring.peek_latest()
        self.assertIsNotNone(peeked)
        self.assertEqual(peeked["metric_type"], 2)
        self.assertEqual(peeked["payload"], b"SECOND")

        # Verify pop still returns the first
        popped1 = self.ring.pop()
        self.assertEqual(popped1["payload"], b"FIRST")
        popped2 = self.ring.pop()
        self.assertEqual(popped2["payload"], b"SECOND")

    def test_torn_read_commit_barrier_prevention(self):
        """Test commit_seq barrier: simulated uncommitted slot cannot be popped."""
        # Manually write to slot 0 without committing
        write_seq = 0
        slot_off = self.ring._slot_offset(write_seq)
        
        # Invalidate commit_seq
        struct.pack_into("=Q", self.ring.mm, slot_off, 0)
        # Advance write_seq to simulate crash mid-write
        self.ring._set_write_seq(1)

        # Pop should detect uncommitted slot and return None (zero torn read)
        item = self.ring.pop()
        self.assertIsNone(item)

    def test_multi_client_shared_memory_attach(self):
        """Test secondary client attaches to existing /dev/shm ring buffer and reads data."""
        self.ring.push(10, b"INTER_PROCESS_FRAME")

        # Attach secondary reader
        client_reader = SharedMemoryRingBuffer(self.shm_name, create=False)
        try:
            stats = client_reader.stats()
            self.assertEqual(stats["unconsumed_count"], 1)

            popped = client_reader.pop()
            self.assertIsNotNone(popped)
            self.assertEqual(popped["payload"], b"INTER_PROCESS_FRAME")
            self.assertEqual(popped["metric_type"], 10)
        finally:
            client_reader.close()


if __name__ == "__main__":
    unittest.main()
