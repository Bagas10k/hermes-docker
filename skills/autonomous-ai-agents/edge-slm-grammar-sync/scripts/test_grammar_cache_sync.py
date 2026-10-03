#!/usr/bin/env python3
"""
Deterministic Unit Tests for Grammar-Guided KV-Cache Slicing Sync
Menguji sinkronisasi atomik token dan grammar state rollback.
"""

import unittest
from grammar_cache_sync import GrammarKVSynchronizer

class TestGrammarKVSync(unittest.TestCase):

    def setUp(self):
        self.sync = GrammarKVSynchronizer()

    def test_01_atomic_rollback_terminals(self):
        """Rollback wajib memulihkan expected_terminals yang 100% sama dengan saat checkpoint."""
        self.sync.feed_token("{")
        self.sync.feed_token('"action"')
        self.sync.feed_token(":")
        
        # Simpan checkpoint
        self.sync.fork_checkpoint("after_colon")
        expected_at_cp = set(self.sync.get_allowed_next_terminals())
        self.assertEqual(expected_at_cp, {'"query"', '"exec"', '"read"'})

        # Masukkan cabang spekulatif
        self.sync.feed_token('"query"')
        self.sync.feed_token(",")
        self.assertNotEqual(self.sync.get_allowed_next_terminals(), expected_at_cp)

        # Rollback
        pruned, snap = self.sync.rollback_to_checkpoint("after_colon")
        self.assertEqual(pruned, 2)
        self.assertEqual(self.sync.get_allowed_next_terminals(), expected_at_cp)
        self.assertEqual(self.sync.parsed_str, '{"action":')

    def test_02_multiple_nested_rollback(self):
        """Memastikan rollback bertingkat memulihkan status parser tanpa desinkronisasi."""
        self.sync.feed_token("{")
        self.sync.fork_checkpoint("cp1")

        self.sync.feed_token('"action"')
        self.sync.feed_token(":")
        self.sync.fork_checkpoint("cp2")

        self.sync.feed_token('"read"')
        self.assertEqual(self.sync.get_context_length(), 4)

        # Rollback ke cp2
        pruned2, _ = self.sync.rollback_to_checkpoint("cp2")
        self.assertEqual(pruned2, 1)
        self.assertEqual(self.sync.get_context_length(), 3)

        # Rollback ke cp1
        pruned1, _ = self.sync.rollback_to_checkpoint("cp1")
        self.assertEqual(pruned1, 2)
        self.assertEqual(self.sync.get_context_length(), 1)
        self.assertEqual(self.sync.tokens, ["{"])

    def test_03_invalid_checkpoint_exception(self):
        """Checkpoint tidak valid wajib memicu KeyError."""
        with self.assertRaises(KeyError):
            self.sync.rollback_to_checkpoint("non_existent")

if __name__ == "__main__":
    unittest.main()
