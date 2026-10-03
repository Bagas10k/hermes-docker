#!/usr/bin/env python3
"""
Differential Trajectory Pruning & KV-Cache Slicing Simulator
Mengelola pemangkasan cabang penalaran gagal dan slicing KV-cache in-place
untuk inferensi lokal SLM berlatensi rendah pada edge devices.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import time

@dataclass
class CheckpointMeta:
    label: str
    token_index: int
    created_at: float
    metadata: Dict[str, str] = field(default_factory=dict)

class KVCacheManager:
    def __init__(self, max_context_length: int = 4096, hidden_dim: int = 64):
        self.max_context_length = max_context_length
        self.hidden_dim = hidden_dim
        
        # Simulasi buffer memori linear (in-place sliceable)
        self.tokens: List[int] = []
        self.key_cache: List[List[float]] = []
        self.value_cache: List[List[float]] = []
        
        self.checkpoints: Dict[str, CheckpointMeta] = {}
        self.checkpoint_stack: List[str] = []
        
        # Telemetri penghematan komputasi
        self.total_tokens_generated = 0
        self.total_tokens_pruned = 0
        self.prefill_evals_saved = 0

    def append_tokens(self, token_ids: List[int]):
        """Menambahkan token baru dan menghasilkan KV cache entry."""
        for tid in token_ids:
            if len(self.tokens) >= self.max_context_length:
                raise BufferError("Context window limit exceeded")
            self.tokens.append(tid)
            # Dummy embedding vector representatif
            dummy_kv = [float(tid % 100) / 100.0] * self.hidden_dim
            self.key_cache.append(dummy_kv)
            self.value_cache.append(dummy_kv)
            self.total_tokens_generated += 1

    def fork_checkpoint(self, label: str, metadata: Optional[Dict[str, str]] = None) -> CheckpointMeta:
        """Menyimpan checkpoint sebelum mengeksekusi cabang spekulatif."""
        cp = CheckpointMeta(
            label=label,
            token_index=len(self.tokens),
            created_at=time.time(),
            metadata=metadata or {}
        )
        self.checkpoints[label] = cp
        self.checkpoint_stack.append(label)
        return cp

    def prune_to_checkpoint(self, label: str) -> Tuple[int, float]:
        """
        Memotong KV-cache secara in-place (O(1) memory slicing).
        Mengembalikan jumlah token yang dipangkas dan Amdahl speedup factor.
        """
        if label not in self.checkpoints:
            raise KeyError(f"Checkpoint '{label}' tidak ditemukan")
        
        target_idx = self.checkpoints[label].token_index
        current_len = len(self.tokens)
        pruned_count = current_len - target_idx
        
        if pruned_count < 0:
            raise ValueError("Target index berada di depan panjang konteks saat ini")
        
        # In-place slice: tidak mengalokasikan memori baru
        del self.tokens[target_idx:]
        del self.key_cache[target_idx:]
        del self.value_cache[target_idx:]
        
        self.total_tokens_pruned += pruned_count
        self.prefill_evals_saved += target_idx # Token prefix yang tidak perlu dihitung ulang
        
        # Bersihkan checkpoint turunan
        while self.checkpoint_stack and self.checkpoint_stack[-1] != label:
            stale_label = self.checkpoint_stack.pop()
            self.checkpoints.pop(stale_label, None)
            
        # Amdahl speedup factor terhadap full replay dari token 0
        fraction_reused = target_idx / max(1, current_len)
        # S = 1 / ((1 - f) + (f / k)) dengan k (cache read vs compute) ~ 10x
        speedup = 1.0 / max(0.01, (1.0 - fraction_reused) + (fraction_reused / 10.0))
        
        return pruned_count, round(speedup, 2)

    def get_context_length(self) -> int:
        return len(self.tokens)

    def get_telemetry(self) -> Dict[str, float]:
        total = self.total_tokens_generated
        reused = self.prefill_evals_saved
        ratio = round((reused / max(1, total + reused)) * 100, 2)
        return {
            "current_length": len(self.tokens),
            "total_tokens_generated": self.total_tokens_generated,
            "total_tokens_pruned": self.total_tokens_pruned,
            "prefill_tokens_saved": self.prefill_evals_saved,
            "compute_efficiency_pct": ratio
        }

if __name__ == "__main__":
    mgr = KVCacheManager()
    mgr.append_tokens([101, 102, 103, 104, 105]) # System prompt + Tool schema (5 tokens)
    mgr.fork_checkpoint("step_1_intent")
    
    mgr.append_tokens([201, 202, 203]) # Spekulasi cabang A (3 tokens)
    print("Sebelum prune:", mgr.get_context_length()) # 8
    
    pruned, speedup = mgr.prune_to_checkpoint("step_1_intent")
    print(f"Dipangkas: {pruned} token, Speedup Amdahl: {speedup}x")
    print("Setelah prune:", mgr.get_context_length()) # 5
    print("Telemetri:", mgr.get_telemetry())
