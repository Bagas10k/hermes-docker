#!/usr/bin/env python3
"""
Grammar-Guided Constrained Sampling & KV-Cache Slicing Synchronizer
Memastikan status parser GBNF/CFG selalu sinkron atomik dengan titik pemotongan KV-cache
pada inferensi lokal SLM berlatensi rendah.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set
import copy

@dataclass
class GrammarStateSnapshot:
    state_id: int
    expected_terminals: Set[str]
    rule_stack: List[str]
    raw_parsed_prefix: str

@dataclass
class SynchronizedCheckpoint:
    label: str
    token_index: int
    grammar_snapshot: GrammarStateSnapshot

class GrammarKVSynchronizer:
    def __init__(self):
        self.tokens: List[str] = []
        self.checkpoints: Dict[str, SynchronizedCheckpoint] = {}
        
        # State grammar parser deterministik (simulasi finite state automaton)
        self.current_state_id = 0
        self.expected_terminals: Set[str] = {"{", "["}
        self.rule_stack: List[str] = ["ROOT"]
        self.parsed_str: str = ""

    def feed_token(self, token: str):
        """Menerima token baru dan memajukan state parser grammar."""
        self.tokens.append(token)
        self.parsed_str += token
        self.current_state_id += 1
        
        # Simulasi transisi tata bahasa JSON/Tool call sederhana
        if token == "{":
            self.expected_terminals = {'"action"', '"type"'}
            self.rule_stack.append("OBJECT")
        elif token in ('"action"', '"type"'):
            self.expected_terminals = {":"}
        elif token == ":":
            self.expected_terminals = {'"query"', '"exec"', '"read"'}
        elif token in ('"query"', '"exec"', '"read"'):
            self.expected_terminals = {",", "}"}
        elif token == ",":
            self.expected_terminals = {'"args"', '"params"'}
        elif token == "}":
            self.expected_terminals = {"<EOS>"}
            if self.rule_stack and self.rule_stack[-1] == "OBJECT":
                self.rule_stack.pop()

    def fork_checkpoint(self, label: str) -> SynchronizedCheckpoint:
        """Kunci checkpoint atomik: Token KV-Cache + Grammar State."""
        snap = GrammarStateSnapshot(
            state_id=self.current_state_id,
            expected_terminals=set(self.expected_terminals),
            rule_stack=list(self.rule_stack),
            raw_parsed_prefix=self.parsed_str
        )
        cp = SynchronizedCheckpoint(
            label=label,
            token_index=len(self.tokens),
            grammar_snapshot=snap
        )
        self.checkpoints[label] = cp
        return cp

    def rollback_to_checkpoint(self, label: str) -> Tuple[int, GrammarStateSnapshot]:
        """Rollback atomik: Potong token array dan restore status parser tepat."""
        if label not in self.checkpoints:
            raise KeyError(f"Checkpoint '{label}' tidak ditemukan")
        
        cp = self.checkpoints[label]
        target_idx = cp.token_index
        pruned_tokens = len(self.tokens) - target_idx
        
        # 1. Slice token buffer in-place
        del self.tokens[target_idx:]
        
        # 2. Restore grammar state secara deterministik
        snap = cp.grammar_snapshot
        self.current_state_id = snap.state_id
        self.expected_terminals = set(snap.expected_terminals)
        self.rule_stack = list(snap.rule_stack)
        self.parsed_str = snap.raw_parsed_prefix
        
        return pruned_tokens, snap

    def get_allowed_next_terminals(self) -> Set[str]:
        return self.expected_terminals

    def get_context_length(self) -> int:
        return len(self.tokens)

if __name__ == "__main__":
    sync = GrammarKVSynchronizer()
    sync.feed_token("{")
    sync.feed_token('"action"')
    sync.feed_token(":")
    
    # Checkpoint sebelum memilih argumen
    sync.fork_checkpoint("arg_selection")
    print("Allowed at checkpoint:", sync.get_allowed_next_terminals())
    
    # Coba cabang salah
    sync.feed_token('"invalid_tool"')
    print("Tokens after wrong branch:", sync.tokens)
    
    # Rollback atomik
    pruned, snap = sync.rollback_to_checkpoint("arg_selection")
    print(f"Dipangkas: {pruned} token. Allowed restored:", sync.get_allowed_next_terminals())
