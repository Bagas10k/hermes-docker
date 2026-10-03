#!/usr/bin/env python3
"""
Truthful VCG Auction & Game-Theoretic Resource Allocation Engine
Mengalokasikan kuota komputasi/token inferensi di antara sub-agen otonom
dengan kepastian insentif jujur (Dominant Strategy Incentive Compatibility / DSIC).
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

@dataclass
class AgentBid:
    agent_id: str
    valuation: float       # Nilai utilitas sebenarnya
    bid: float             # Nilai penawaran yang diajukan
    requested_units: int = 1

@dataclass
class AuctionResult:
    winner_id: str
    allocated_units: int
    payment_price: float   # Harga yang harus dibayar (eksternalitas sosial)
    winner_surplus: float  # Keuntungan bersih (valuation - payment)
    all_bids: List[Dict[str, float]]

class VCGAuctionEngine:
    def __init__(self, resource_name: str = "token_quota_slot"):
        self.resource_name = resource_name

    def run_single_item_second_price(self, bids: List[AgentBid]) -> AuctionResult:
        """
        Lelang Vickrey (Second-Price Sealed-Bid).
        Pemenang adalah penawar tertinggi, membayar harga penawar kedua tertinggi.
        Menjamin bahwa berbohong (bid != valuation) tidak pernah menghasilkan keuntungan lebih tinggi.
        """
        if not bids:
            raise ValueError("Daftar tawaran tidak boleh kosong")
        
        # Urutkan berdasarkan nilai tawaran secara menurun
        sorted_bids = sorted(bids, key=lambda b: b.bid, reverse=True)
        winner = sorted_bids[0]
        
        # Harga yang dibayar adalah tawaran tertinggi kedua (atau 0 jika tunggal)
        second_highest = sorted_bids[1].bid if len(sorted_bids) > 1 else 0.0
        
        payment = second_highest
        surplus = winner.valuation - payment
        
        return AuctionResult(
            winner_id=winner.agent_id,
            allocated_units=winner.requested_units,
            payment_price=round(payment, 4),
            winner_surplus=round(surplus, 4),
            all_bids=[{"agent_id": b.agent_id, "bid": b.bid, "valuation": b.valuation} for b in sorted_bids]
        )

    def verify_truthfulness_invariant(self, true_val: float, opponent_bids: List[float], lie_bids: List[float]) -> bool:
        """
        Membuktikan secara matematis dan empiris bahwa menawar jujur (bid == valuation)
        selalu memberikan utilitas bersih >= menawar tidak jujur (lie_bids).
        """
        # Surplus jika jujur
        truth_bid = AgentBid(agent_id="test_agent", valuation=true_val, bid=true_val)
        all_truth = [truth_bid] + [AgentBid(agent_id=f"opp_{i}", valuation=b, bid=b) for i, b in enumerate(opponent_bids)]
        truth_res = self.run_single_item_second_price(all_truth)
        
        truth_surplus = truth_res.winner_surplus if truth_res.winner_id == "test_agent" else 0.0
        
        # Uji setiap variasi kebohongan (overbidding atau underbidding)
        for lie in lie_bids:
            lie_bid = AgentBid(agent_id="test_agent", valuation=true_val, bid=lie)
            all_lie = [lie_bid] + [AgentBid(agent_id=f"opp_{i}", valuation=b, bid=b) for i, b in enumerate(opponent_bids)]
            lie_res = self.run_single_item_second_price(all_lie)
            
            lie_surplus = lie_res.winner_surplus if lie_res.winner_id == "test_agent" else 0.0
            
            # Dominant strategy: truth_surplus wajib >= lie_surplus
            if lie_surplus > truth_surplus + 1e-9:
                return False
                
        return True

if __name__ == "__main__":
    engine = VCGAuctionEngine()
    bids = [
        AgentBid(agent_id="architect", valuation=100.0, bid=100.0),
        AgentBid(agent_id="qa_agent", valuation=80.0, bid=80.0),
        AgentBid(agent_id="dev_backend", valuation=60.0, bid=60.0)
    ]
    res = engine.run_single_item_second_price(bids)
    print("Pemenang:", res.winner_id)
    print("Harga Bayar (Second-Price):", res.payment_price)
    print("Surplus Pemenang:", res.winner_surplus)
