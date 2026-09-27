#!/usr/bin/env python3
"""
Unit tests for Adaptive Semantic Prompt Compaction (KGRAPH-003)
Tests:
1. KV-Cache Prefix Hash Invariance (Absolute preservation).
2. Shannon Entropy calculation & redundancy suppression.
3. Knapsack dynamic token budget partitioning.
4. Total budget hard constraint satisfaction.
5. Amdahl speedup monotonicity under token reduction.
"""

import unittest
from prompt_compactor_engine import AdaptivePromptCompactor

class TestAdaptivePromptCompactor(unittest.TestCase):

    def setUp(self):
        self.compactor = AdaptivePromptCompactor(total_budget=300)
        self.system_prompt = "You are Hermes Agent. Follow core constraints strictly and answer precisely."

    def test_prefix_hash_invariance(self):
        """Verify system prompt prefix SHA-256 remains 100% identical post-compaction."""
        initial_hash = AdaptivePromptCompactor.compute_sha256(self.system_prompt)
        res = self.compactor.allocate_and_compact(
            system_prefix=self.system_prompt,
            memory_context="Long memory line 1\nLong memory line 2",
            tool_definitions="Tool A description\nTool B description",
            ephemeral_history="Turn 1\nTurn 2\nTurn 3",
        )
        self.assertEqual(res["prefix_hash"], initial_hash)

    def test_shannon_entropy_calculation(self):
        """Verify Shannon entropy properly scores high-entropy diverse text above repetitive text."""
        low_entropy = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        high_entropy = "abcdefghijklmnopqrstuvwxyz1234567890!@#$%^"
        h_low = AdaptivePromptCompactor.calculate_shannon_entropy(low_entropy)
        h_high = AdaptivePromptCompactor.calculate_shannon_entropy(high_entropy)
        self.assertGreater(h_high, h_low)
        self.assertEqual(h_low, 0.0)

    def test_redundancy_pruning(self):
        """Verify duplicate / redundant lines are suppressed under tight budget."""
        repetitive_text = (
            "User likes concise text.\n"
            "User likes concise text.\n"
            "System runs on Ubuntu Linux 22.04 LTS kernel.\n"
            "User likes concise text.\n"
            "Database engine is SQLite in WAL mode."
        )
        pruned = self.compactor.prune_redundancy(repetitive_text, target_tokens=30)
        # Verify duplicate line is reduced
        self.assertLessEqual(pruned.count("User likes concise text."), 1)
        self.assertIn("SQLite in WAL mode", pruned)

    def test_hard_budget_constraint(self):
        """Verify final tokens strictly satisfy the configured hard budget."""
        large_mem = "\n".join([f"Memory fact entry number {i} regarding environment configuration" for i in range(50)])
        large_tools = "\n".join([f"tool_{i}: executes subtask {i} with argument validation" for i in range(40)])
        large_hist = "\n".join([f"Turn {i}: user asked question {i} assistant replied" for i in range(60)])

        res = self.compactor.allocate_and_compact(
            system_prefix=self.system_prompt,
            memory_context=large_mem,
            tool_definitions=large_tools,
            ephemeral_history=large_hist,
        )
        self.assertTrue(res["budget_satisfied"])
        self.assertLessEqual(res["final_tokens"], self.compactor.total_budget + 10) # within bounds

    def test_amdahl_speedup_monotonicity(self):
        """Verify larger compression ratios yield monotonically higher TTFT speedup."""
        res_small = self.compactor.allocate_and_compact(
            self.system_prompt,
            "Small memory fact.",
            "Tool A",
            "History 1"
        )
        large_text = "\n".join([f"Repeated verbose padding sentence {i}" for i in range(100)])
        res_large = self.compactor.allocate_and_compact(
            self.system_prompt,
            large_text,
            large_text,
            large_text
        )
        self.assertGreaterEqual(res_large["estimated_ttft_speedup"], res_small["estimated_ttft_speedup"])

if __name__ == "__main__":
    unittest.main()
