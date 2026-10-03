#!/usr/bin/env python3
"""
Deterministic Unit Tests for Differential Trajectory Pruning & KV-Cache Slicing
Menguji kebenaran pemotongan in-place, pelestarian prefix, dan efisiensi Amdahl.
"""

import unittest
from kv_cache_slicer import KVCacheManager

class TestKVCacheSlicing(unittest.TestCase):

    def setUp(self):
        self.mgr = KVCacheManager(max_context_length=1000, hidden_dim=32)

    def test_01_prefix_conservation(self):
        """Prefix system prompt wajib tetap identik setelah cabang gagal dipangkas."""
        prefix_tokens = [10, 20, 30, 40, 50]
        self.mgr.append_tokens(prefix_tokens)
        self.mgr.fork_checkpoint("system_ready")

        # Tambahkan spekulasi tool yang gagal
        speculative_tokens = [999, 888, 777]
        self.mgr.append_tokens(speculative_tokens)
        self.assertEqual(self.mgr.get_context_length(), 8)

        # Lakukan prune ke checkpoint
        pruned_count, speedup = self.mgr.prune_to_checkpoint("system_ready")
        self.assertEqual(pruned_count, 3)
        self.assertEqual(self.mgr.get_context_length(), 5)
        self.assertEqual(self.mgr.tokens, prefix_tokens)
        self.assertGreater(speedup, 1.0)

    def test_02_nested_checkpoints(self):
        """Uji hierarki checkpoint bersarang (A -> B -> rollback B -> rollback A)."""
        self.mgr.append_tokens([1, 2])
        self.mgr.fork_checkpoint("A")

        self.mgr.append_tokens([3, 4])
        self.mgr.fork_checkpoint("B")

        self.mgr.append_tokens([5, 6])
        self.assertEqual(self.mgr.get_context_length(), 6)

        # Rollback ke B
        pruned_b, _ = self.mgr.prune_to_checkpoint("B")
        self.assertEqual(pruned_b, 2)
        self.assertEqual(self.mgr.get_context_length(), 4)
        self.assertEqual(self.mgr.tokens, [1, 2, 3, 4])

        # Rollback ke A
        pruned_a, _ = self.mgr.prune_to_checkpoint("A")
        self.assertEqual(pruned_a, 2)
        self.assertEqual(self.mgr.get_context_length(), 2)
        self.assertEqual(self.mgr.tokens, [1, 2])

    def test_03_amdahl_speedup_scaling(self):
        """Semakin besar fraksi prefix yang di-reuse, semakin tinggi Amdahl speedup factor."""
        self.mgr.append_tokens(list(range(90))) # 90 token prefix
        self.mgr.fork_checkpoint("large_prefix")

        self.mgr.append_tokens(list(range(10))) # 10 token cabang spekulatif
        pruned, speedup = self.mgr.prune_to_checkpoint("large_prefix")
        self.assertEqual(pruned, 10)
        # f = 90 / 100 = 0.90 -> Speedup > 4.5x
        self.assertGreaterEqual(speedup, 4.5)

    def test_04_context_overflow_error(self):
        """Memastikan buffer overflow memicu BufferError tanpa crash memori."""
        small_mgr = KVCacheManager(max_context_length=10)
        small_mgr.append_tokens(list(range(10)))
        with self.assertRaises(BufferError):
            small_mgr.append_tokens([11])

if __name__ == "__main__":
    unittest.main()
