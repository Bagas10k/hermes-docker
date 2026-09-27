#!/usr/bin/env python3
"""
Hierarchical Virtual Memory Paging Engine for Long-Horizon Agents.
Implements:
1. Three-tier memory hierarchy (Core RAM, Episodic Cache, Procedural Disk Vault).
2. Path-monotone prefix caching preservation (never evict system prompt or core directives).
3. Knapsack / Cost-utility evictions (Belady MIN approximation with recency + epistemic utility).
4. Page-in / Page-out lifecycle with deterministic token accounting.
"""

import hashlib
import json
import math
import sys
import time
from typing import Dict, List, Optional, Tuple, Any

class MemoryPage:
    def __init__(self, page_id: str, content: str, scope: str = "episodic", importance: float = 0.5):
        self.page_id = page_id
        self.content = content
        self.scope = scope  # "core", "episodic", "procedural"
        self.importance = importance
        self.access_count = 1
        self.created_at = time.time()
        self.last_accessed_at = self.created_at
        self.tokens = self._estimate_tokens(content)
        self.content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        # Standard conservative estimation: ~4 chars per token for English/code
        return max(1, math.ceil(len(text) / 4))

    def update_access(self):
        self.access_count += 1
        self.last_accessed_at = time.time()

    def utility_score(self, current_time: float) -> float:
        # Utility U = importance * (access_count / (1 + age_factor))
        age = max(0.1, current_time - self.last_accessed_at)
        decay = math.exp(-age / 3600.0)  # 1 hour half-life decay
        return (self.importance * 0.7 + 0.3 * min(5.0, self.access_count)) * decay

class HierarchicalVirtualMemory:
    def __init__(self, core_budget_tokens: int = 1500, episodic_budget_tokens: int = 4000):
        self.core_budget_tokens = core_budget_tokens
        self.episodic_budget_tokens = episodic_budget_tokens
        
        # Tier-1: Core In-Context RAM (Immutable/Pinned prefix + hot context)
        self.core_pages: Dict[str, MemoryPage] = {}
        
        # Tier-2: Episodic Paged Cache (Swappable working memory)
        self.episodic_pages: Dict[str, MemoryPage] = {}
        
        # Tier-3: Procedural Disk Vault (Evicted pages in durable store)
        self.procedural_vault: Dict[str, MemoryPage] = {}

    def get_token_usage(self) -> Dict[str, int]:
        core_tokens = sum(p.tokens for p in self.core_pages.values())
        episodic_tokens = sum(p.tokens for p in self.episodic_pages.values())
        vault_tokens = sum(p.tokens for p in self.procedural_vault.values())
        return {
            "core_tokens": core_tokens,
            "core_budget": self.core_budget_tokens,
            "episodic_tokens": episodic_tokens,
            "episodic_budget": self.episodic_budget_tokens,
            "vault_tokens": vault_tokens,
            "active_in_context": core_tokens + episodic_tokens
        }

    def pin_core_page(self, page_id: str, content: str, importance: float = 1.0) -> MemoryPage:
        """Pins a memory page to Tier-1 Core RAM. Core pages are protected from eviction."""
        page = MemoryPage(page_id, content, scope="core", importance=importance)
        self.core_pages[page_id] = page
        return page

    def page_in(self, page_id: str, content: Optional[str] = None, importance: float = 0.5) -> MemoryPage:
        """
        Loads a page into Tier-2 Episodic Working Memory.
        If budget is exceeded, triggers Knapsack utility-based eviction to Tier-3 Vault.
        """
        current_time = time.time()
        
        # If already in core, bump access and return
        if page_id in self.core_pages:
            self.core_pages[page_id].update_access()
            return self.core_pages[page_id]
            
        # If already in episodic, bump access and return
        if page_id in self.episodic_pages:
            self.episodic_pages[page_id].update_access()
            return self.episodic_pages[page_id]

        # If in procedural vault, swap in
        if page_id in self.procedural_vault:
            page = self.procedural_vault.pop(page_id)
            page.update_access()
        else:
            if content is None:
                raise ValueError(f"Page {page_id} not found in memory hierarchy and no content provided.")
            page = MemoryPage(page_id, content, scope="episodic", importance=importance)

        # Evict until page fits into episodic budget
        while True:
            current_episodic_tokens = sum(p.tokens for p in self.episodic_pages.values())
            if current_episodic_tokens + page.tokens <= self.episodic_budget_tokens:
                break
            if not self.episodic_pages:
                # Page itself exceeds budget, force single page allocation
                break
            self._evict_lowest_utility(current_time)

        self.episodic_pages[page_id] = page
        return page

    def _evict_lowest_utility(self, current_time: float) -> MemoryPage:
        """Selects lowest utility per token in Tier-2 and swaps it out to Tier-3 Vault."""
        lowest_id = None
        lowest_ratio = float("inf")
        
        for pid, p in self.episodic_pages.items():
            u = p.utility_score(current_time)
            ratio = u / max(1, p.tokens)
            if ratio < lowest_ratio:
                lowest_ratio = ratio
                lowest_id = pid
                
        if lowest_id is None:
            lowest_id = next(iter(self.episodic_pages))
            
        evicted = self.episodic_pages.pop(lowest_id)
        evicted.scope = "procedural"
        self.procedural_vault[lowest_id] = evicted
        return evicted

    def build_active_context(self) -> str:
        """
        Builds the active prompt context preserving Prefix Caching:
        [CORE TIER-1 (Static / Pinned Prefix)] -> [EPISODIC TIER-2 (Dynamic Working Paged)]
        """
        lines = []
        lines.append("=== TIER-1 CORE SYSTEM MEMORY (PINNED PREFIX) ===")
        for pid in sorted(self.core_pages.keys()):
            p = self.core_pages[pid]
            lines.append(f"[{p.page_id}] {p.content}")
            
        lines.append("\n=== TIER-2 EPISODIC WORKING MEMORY (PAGED IN) ===")
        # Sort by importance and recency to keep structure consistent
        sorted_episodic = sorted(self.episodic_pages.values(), key=lambda p: (p.importance, p.last_accessed_at), reverse=True)
        for p in sorted_episodic:
            lines.append(f"[{p.page_id} | imp:{p.importance:.1f}] {p.content}")
            
        return "\n".join(lines)

def run_self_test():
    vm = HierarchicalVirtualMemory(core_budget_tokens=100, episodic_budget_tokens=150)
    
    # 1. Pin Core Directives
    vm.pin_core_page("sys_directive", "Directives: 100% Zero Emoji, verify via tests, truth > pleasing.")
    assert "sys_directive" in vm.core_pages
    
    # 2. Add Episodic Pages
    vm.page_in("task_summary", "Working on AGENT-003 Hierarchical Virtual Memory & Paging engine.", importance=0.9)
    vm.page_in("tool_result_1", "Result from tool A: exit code 0, 45 bytes written to disk.", importance=0.4)
    vm.page_in("tool_result_2", "Result from tool B: intermediate cache initialized with 12 items.", importance=0.3)
    
    # Check token counts
    stats = vm.get_token_usage()
    assert stats["core_tokens"] > 0
    assert stats["episodic_tokens"] <= vm.episodic_budget_tokens
    
    # 3. Trigger Eviction by loading large page
    big_doc = "Documentation page: " + ("lorem ipsum architecture specification details " * 20)
    vm.page_in("big_doc", big_doc, importance=0.8)
    
    # Verify that lower importance pages were evicted to vault
    post_stats = vm.get_token_usage()
    assert len(vm.procedural_vault) > 0, "Lower utility pages should be moved to Tier-3 vault"
    assert "sys_directive" in vm.core_pages, "Core pinned page must never be evicted"
    
    # 4. Swap back in
    evicted_id = next(iter(vm.procedural_vault))
    swapped = vm.page_in(evicted_id)
    assert swapped.page_id in vm.episodic_pages
    
    ctx = vm.build_active_context()
    assert "TIER-1 CORE SYSTEM MEMORY" in ctx
    assert "TIER-2 EPISODIC WORKING MEMORY" in ctx
    print("ALL HIERARCHICAL VIRTUAL MEMORY INVARIANTS TESTED SUCCESSFULLY.")

if __name__ == "__main__":
    run_self_test()
