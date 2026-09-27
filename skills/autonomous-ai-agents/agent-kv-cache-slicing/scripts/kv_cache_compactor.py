"""KV-Cache Slicing & Attention Compactor Engine for Long-Horizon Autonomous Agents.

Provides algorithmic bounds and pruning policies:
1. Attention Sink Preservation (first K initial prompt tokens locked).
2. Recent Window Eviction (sliding window of last W generation tokens).
3. H2O (Heavy Hitter Oracle) Cumulative Attention Score Selection for intermediate tokens.
4. Prefix Cache Integrity Verification (ensures SHA-256 hash invariance of prompt prefix).
"""

import hashlib
import math
from typing import List, Dict, Any, Tuple

class KVCacheBlock:
    def __init__(self, token_id: int, token_str: str, layer_idx: int, importance_score: float = 0.0, is_sink: bool = False):
        self.token_id = token_id
        self.token_str = token_str
        self.layer_idx = layer_idx
        self.importance_score = importance_score
        self.is_sink = is_sink
        self.access_count = 0

class DynamicKVSlicer:
    def __init__(self, sink_size: int = 4, recent_window_size: int = 16, max_cache_budget: int = 32):
        if sink_size + recent_window_size > max_cache_budget:
            raise ValueError("sink_size + recent_window_size cannot exceed max_cache_budget")
        self.sink_size = sink_size
        self.recent_window_size = recent_window_size
        self.max_cache_budget = max_cache_budget
        self.cache: List[KVCacheBlock] = []

    def load_prompt_prefix(self, tokens: List[Tuple[int, str]]):
        """Loads prompt tokens, marking initial sink_size as immutable sinks."""
        self.cache.clear()
        for idx, (t_id, t_str) in enumerate(tokens):
            is_sink = (idx < self.sink_size)
            self.cache.append(KVCacheBlock(
                token_id=t_id,
                token_str=t_str,
                layer_idx=0,
                importance_score=100.0 if is_sink else 1.0,
                is_sink=is_sink
            ))

    def get_prefix_hash(self) -> str:
        """Returns cryptographic hash of sink tokens ensuring prefix stability."""
        sink_bytes = b"".join(b.token_str.encode("utf-8") for b in self.cache[:self.sink_size])
        return hashlib.sha256(sink_bytes).hexdigest()

    def record_attention_mass(self, attention_matrix: List[float]):
        """Updates cumulative attention mass across active cache blocks."""
        if len(attention_matrix) != len(self.cache):
            raise ValueError(f"Attention vector size ({len(attention_matrix)}) must match cache size ({len(self.cache)})")
        for idx, score in enumerate(attention_matrix):
            self.cache[idx].importance_score += score
            self.cache[idx].access_count += 1

    def append_token(self, token_id: int, token_str: str, attention_dist: List[float]) -> Dict[str, Any]:
        """Appends new token and applies compacting/slicing policy if budget is exceeded."""
        if len(attention_dist) != len(self.cache):
            raise ValueError(f"Attention vector size ({len(attention_dist)}) must match current cache ({len(self.cache)})")
        
        # Update existing importance before appending
        self.record_attention_mass(attention_dist)
        
        # Append new token
        new_block = KVCacheBlock(token_id=token_id, token_str=token_str, layer_idx=0, importance_score=1.0, is_sink=False)
        self.cache.append(new_block)
        
        evicted = None
        # Check eviction if over budget
        if len(self.cache) > self.max_cache_budget:
            evicted = self._evict_least_important()
            
        return {
            "current_size": len(self.cache),
            "evicted_token": evicted.token_str if evicted else None,
            "prefix_hash": self.get_prefix_hash()
        }

    def _evict_least_important(self) -> KVCacheBlock:
        """Evicts 1 token outside of sink zone and recent window using H2O minimum importance."""
        # Immutable bounds:
        # [0 : sink_size] -> Protected Sinks
        # [len - recent_window_size : len] -> Protected Recent Window
        candidate_start = self.sink_size
        candidate_end = len(self.cache) - self.recent_window_size
        
        if candidate_start >= candidate_end:
            # Cannot evict from protected zones, drop earliest non-sink
            evict_idx = self.sink_size
        else:
            # Find candidate with lowest importance_score
            min_score = float('inf')
            min_idx = candidate_start
            for idx in range(candidate_start, candidate_end):
                if self.cache[idx].importance_score < min_score:
                    min_score = self.cache[idx].importance_score
                    min_idx = idx
            evict_idx = min_idx
            
        return self.cache.pop(evict_idx)

    def calculate_amdahl_speedup(self, sequence_length: int, memory_bandwidth_gbps: float = 68.0) -> Dict[str, float]:
        """Calculates theoretical speedup of KV cache slicing via memory-bound Amdahl formulation.
        
        Uncompressed Attention: Memory I/O = 2 * n_layers * n_heads * d_head * seq_len * precision_bytes.
        Compressed Attention: Memory I/O bound capped at max_cache_budget.
        """
        if sequence_length <= self.max_cache_budget:
            return {"speedup_ratio": 1.0, "vram_reduction_pct": 0.0}
        
        compression_ratio = self.max_cache_budget / sequence_length
        # Assuming memory I/O accounts for 75% of decode step latency (p = 0.75)
        p = 0.75
        s = 1.0 / compression_ratio
        speedup = 1.0 / ((1.0 - p) + (p / s))
        vram_reduction = (1.0 - compression_ratio) * 100.0
        
        return {
            "speedup_ratio": round(speedup, 2),
            "vram_reduction_pct": round(vram_reduction, 2),
            "compression_ratio": round(compression_ratio, 3)
        }

def run_self_verification() -> bool:
    """Verifies core invariants: sink preservation, prefix hash invariance, and bounded memory."""
    slicer = DynamicKVSlicer(sink_size=4, recent_window_size=8, max_cache_budget=16)
    
    # Invariant 1: Prefix Sink Protection
    prompt_tokens = [(i, f"tok_{i}") for i in range(12)]
    slicer.load_prompt_prefix(prompt_tokens)
    initial_hash = slicer.get_prefix_hash()
    
    # Invariant 2: Dynamic Token Streaming & Eviction
    for i in range(12, 30):
        current_len = len(slicer.cache)
        # Mock attention weights giving high weight to sink and recent tokens
        weights = [1.0 if idx < 4 else (0.1 if idx < current_len - 4 else 0.8) for idx in range(current_len)]
        res = slicer.append_token(token_id=i, token_str=f"gen_{i}", attention_dist=weights)
        assert res["current_size"] <= 16, f"Cache exceeded max budget: {res['current_size']} > 16"
        assert res["prefix_hash"] == initial_hash, "Prefix hash altered during eviction!"

    # Invariant 3: Sinks remain intact
    for idx in range(4):
        assert slicer.cache[idx].token_str == f"tok_{idx}", f"Sink token {idx} corrupted!"

    # Invariant 4: Speedup math
    perf = slicer.calculate_amdahl_speedup(sequence_length=128)
    assert perf["speedup_ratio"] > 1.0, "Theoretical speedup should exceed 1.0"
    assert perf["vram_reduction_pct"] > 50.0, "VRAM reduction should exceed 50%"
    
    return True

if __name__ == "__main__":
    if run_self_verification():
        print("ALL KV-CACHE SLICING INVARIANTS VERIFIED (PASS)")
