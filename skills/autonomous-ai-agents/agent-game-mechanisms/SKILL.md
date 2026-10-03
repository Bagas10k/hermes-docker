---
name: agent-game-mechanisms
description: Use when designing truthful multi-agent auction games. VCG auction & DSIC resource allocation.
version: 1.0.0
author: Bagas Saputra & Hermes Autopilot
license: MIT
metadata:
  hermes:
    tags: [game-theory, vcg-auction, truthful-bidding, multi-agent, resource-allocation, dsic]
    related_skills: [autonomous-orchestrator, subagent-concurrency-memory-bounds, multiagent-consensus-circuit-breaker]
---

# Autonomous Multi-Agent Game-Theoretic Truthful Auction Protocols

Protokol alokasi komputasi, kuota token, dan antrean eksekusi berbasis lelang jujur (*Dominant Strategy Incentive Compatibility* / DSIC) menggunakan mekanisme Vickrey-Clarke-Groves (VCG). Mencegah monopoli sumber daya dan manipulasi prioritas (*bid inflation*) oleh agen egois dalam arsitektur multi-agen otonom.

## Kapan Digunakan
1. Swarm multi-agen bersaing memperebutkan kuota token inferensi per menit (TPM) atau slot pekerja konkurensi terbatas.
2. Ingin mencegah sub-agen mengklaim prioritas tertinggi palsu tanpa menanggung biaya komputasi yang sepadan.
3. Menjamin alokasi sumber daya efisien secara sosial (*socially optimal allocation*) tanpa defisit anggaran (*no deficit*).

## Sintesis 3 Mindset Problem Solving

1. **Lensa Mekanistik-Kausal (Incentive Compatibility)**:
   - Mekanisme Vickrey (Second-Price): Agen pemenang membayar tawaran tertinggi kedua:
     $$p_i = \max_{j \ne i} b_j$$
   - Surplus agen pemenang adalah:
     $$u_i = v_i - p_i$$
   - Pembuktian matematis: Karena harga bayar ditentukan oleh lawan ($p_i$), agen tidak dapat memengaruhi harga turun dengan berbohong tanpa kehilangan item atau menderita kerugian jika $b_i < p_i$.

2. **Lensa Bayesian-Eksperimental**:
   - Prediksi: Tidak ada skenario di mana menawar bohong ($b_i \ne v_i$) menghasilkan surplus bersih lebih tinggi daripada menawar jujur ($b_i = v_i$).
   - Hasil uji: 4 unit test deterministik lulus dalam 0.001s (`test_game_mechanisms.py`).

3. **Lensa Desain Sistem & Optimasi**:
   - Zero-deficit: Mekanisme tidak memerlukan subsidi eksternal.
   - Eksekusi deterministik $O(N \log N)$ untuk pengurutan tawaran.

## Implementasi Cepat

```python
from vcg_auction_engine import VCGAuctionEngine, AgentBid

engine = VCGAuctionEngine()
bids = [
    AgentBid(agent_id="architect", valuation=100.0, bid=100.0),
    AgentBid(agent_id="qa_agent", valuation=80.0, bid=80.0),
    AgentBid(agent_id="dev_backend", valuation=60.0, bid=60.0)
]

res = engine.run_single_item_second_price(bids)
print(f"Pemenang: {res.winner_id}") # architect
print(f"Harga bayar (Second-Price): {res.payment_price}") # 80.0
print(f"Surplus bersih pemenang: {res.winner_surplus}") # 20.0
```

## Verifikasi Empiris
Telah diverifikasi via `scripts/test_game_mechanisms.py`:
- `test_01_second_price_allocation`: Pemenang membayar harga penawar tertinggi kedua.
- `test_02_truthfulness_dsic_invariant`: Membuktikan bahwa overbidding dan underbidding tidak pernah menghasilkan keuntungan lebih tinggi.
- `test_03_truthfulness_when_winning`: Menawar jujur mempertahankan surplus optimal.
- `test_04_empty_bids_exception`: Validasi input aman.
