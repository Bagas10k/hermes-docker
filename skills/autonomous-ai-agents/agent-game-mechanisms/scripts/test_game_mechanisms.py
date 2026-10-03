#!/usr/bin/env python3
"""
Deterministic Unit Tests for Truthful VCG Auction & Game Mechanisms
Menguji pembuktian matematis DSIC, alokasi lelang Vickrey, dan zero-deficit.
"""

import unittest
from vcg_auction_engine import VCGAuctionEngine, AgentBid

class TestVCGAuction(unittest.TestCase):

    def setUp(self):
        self.engine = VCGAuctionEngine()

    def test_01_second_price_allocation(self):
        """Pemenang penawar tertinggi membayar harga tertinggi kedua."""
        bids = [
            AgentBid(agent_id="agent_A", valuation=100.0, bid=100.0),
            AgentBid(agent_id="agent_B", valuation=75.0, bid=75.0),
            AgentBid(agent_id="agent_C", valuation=40.0, bid=40.0),
        ]
        res = self.engine.run_single_item_second_price(bids)
        self.assertEqual(res.winner_id, "agent_A")
        self.assertEqual(res.payment_price, 75.0)
        self.assertEqual(res.winner_surplus, 25.0) # 100 - 75

    def test_02_truthfulness_dsic_invariant(self):
        """Membuktikan secara deterministik bahwa menawar bohong tidak pernah menguntungkan."""
        true_val = 80.0
        opponents = [90.0, 60.0, 50.0] # Lawan tertinggi adalah 90.0
        # Coba overbidding (100) dan underbidding (70, 30)
        lies = [120.0, 95.0, 70.0, 40.0, 10.0]
        
        is_dsic = self.engine.verify_truthfulness_invariant(true_val, opponents, lies)
        self.assertTrue(is_dsic, "Pelanggaran DSIC: ada kebohongan yang menghasilkan surplus lebih tinggi!")

    def test_03_truthfulness_when_winning(self):
        """Ketika agen menang secara wajar (true_val=100 vs opp=80), berbohong tidak menambah surplus."""
        true_val = 100.0
        opponents = [80.0, 60.0]
        lies = [150.0, 110.0, 90.0, 85.0, 50.0]
        
        is_dsic = self.engine.verify_truthfulness_invariant(true_val, opponents, lies)
        self.assertTrue(is_dsic)

    def test_04_empty_bids_exception(self):
        """Daftar kosong wajib memicu ValueError."""
        with self.assertRaises(ValueError):
            self.engine.run_single_item_second_price([])

if __name__ == "__main__":
    unittest.main()
