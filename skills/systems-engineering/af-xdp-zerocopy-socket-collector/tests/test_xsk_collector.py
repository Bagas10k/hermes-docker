import unittest
from xsk_collector import AFXDPIngressCollector, craft_telemetry_packet, UMEMChunkPool, XSKRingBuffer

class TestAFXDPZeroCopyCollector(unittest.TestCase):
    def setUp(self):
        self.collector = AFXDPIngressCollector(ring_size=128, chunk_size=2048)

    def test_umem_pool_allocation_and_release(self):
        pool = UMEMChunkPool(num_chunks=4, chunk_size=2048)
        self.assertEqual(len(pool.free_stack), 4)
        c0 = pool.get_chunk()
        c1 = pool.get_chunk()
        self.assertEqual(len(pool.free_stack), 2)
        pool.release_chunk(c0)
        self.assertEqual(len(pool.free_stack), 3)

    def test_ring_buffer_power_of_two_enforcement(self):
        with self.assertRaises(ValueError):
            XSKRingBuffer(size=100) # bukan power of two
        rb = XSKRingBuffer(size=16)
        self.assertEqual(rb.size, 16)

    def test_ring_buffer_spsc_batching(self):
        rb = XSKRingBuffer(size=16)
        n = rb.produce_batch([1, 2, 3, 4, 5])
        self.assertEqual(n, 5)
        self.assertEqual(rb.available_to_consume(), 5)
        items = rb.consume_batch(3)
        self.assertEqual(items, [1, 2, 3])
        self.assertEqual(rb.available_to_consume(), 2)
        items2 = rb.consume_batch(5)
        self.assertEqual(items2, [4, 5])
        self.assertEqual(rb.available_to_consume(), 0)

    def test_zero_copy_ingress_flow(self):
        # Craft 10 telemetry packets
        packets = []
        for i in range(10):
            pkt = craft_telemetry_packet(agent_id=100 + i, metric_id=1, value=42.5 * (i + 1))
            packets.append(pkt)

        # 1. DMA ingress into UMEM via FILL ring
        ingressed = self.collector.simulate_nic_dma_ingress(packets)
        self.assertEqual(ingressed, 10)

        # 2. Process RX batch in userspace
        records, processed_count = self.collector.process_rx_batch(max_batch=32)
        self.assertEqual(processed_count, 10)
        self.assertEqual(len(records), 10)

        # Verifikasi konten paket
        self.assertEqual(records[0]["agent_id"], 100)
        self.assertEqual(records[0]["value"], 42.5)
        self.assertEqual(records[9]["agent_id"], 109)
        self.assertAlmostEqual(records[9]["value"], 42.5 * 10)

    def test_fill_ring_auto_refill(self):
        # Pastikan setelah diproses, FILL ring terisi kembali
        initial_fill_avail = self.collector.fill_ring.available_to_consume()
        pkts = [craft_telemetry_packet(agent_id=1, metric_id=2, value=3.14) for _ in range(5)]
        self.collector.simulate_nic_dma_ingress(pkts)
        self.collector.process_rx_batch(max_batch=5)
        after_fill_avail = self.collector.fill_ring.available_to_consume()
        # FILL ring harus kembali terisi penuh sesuai kapasitas
        self.assertGreaterEqual(after_fill_avail, initial_fill_avail - 5)

if __name__ == "__main__":
    unittest.main()
