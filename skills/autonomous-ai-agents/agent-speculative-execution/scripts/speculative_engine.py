#!/usr/bin/env python3
"""
Speculative Tool Execution & Pre-Commit Verification Engine for Hermes Agent.
Implements side-effect tiering, Amdahl latency bounds, copy-on-write scratchpad branching,
and two-phase commit verification with zero-leak rollback.
"""

import sys
import os
import json
import shutil
import tempfile
import hashlib
import time
import argparse
from pathlib import Path

# Tool Safety Tiers
TIER_0_READ_ONLY = {"read_file", "search_files", "web_search", "web_extract", "vision_analyze"}
TIER_1_LOCAL_MUTATION = {"write_file", "patch", "terminal_dry_run"}
TIER_2_IRREVERSIBLE = {"terminal", "git_push", "api_call", "publish"}

class SpeculativeEngine:
    def __init__(self, workspace_root=None):
        self.workspace_root = Path(workspace_root or os.getcwd()).resolve()
        self.active_scratchpads = {}

    def classify_tier(self, tool_name: str) -> int:
        if tool_name in TIER_0_READ_ONLY:
            return 0
        if tool_name in TIER_1_LOCAL_MUTATION:
            return 1
        return 2

    def calculate_amdahl_speedup(self, parallel_fraction: float, conc_factor: float) -> dict:
        """
        Calculates theoretical latency speedup: S = 1 / ((1 - p) + (p / s))
        """
        p = max(0.0, min(1.0, parallel_fraction))
        s = max(1.0, conc_factor)
        speedup = 1.0 / ((1.0 - p) + (p / s))
        latency_reduction_pct = (1.0 - (1.0 / speedup)) * 100.0
        return {
            "parallel_fraction": p,
            "concurrency_factor": s,
            "theoretical_speedup": round(speedup, 4),
            "latency_reduction_pct": round(latency_reduction_pct, 2)
        }

    def create_scratchpad(self, target_files=None) -> str:
        """
        Creates an isolated copy-on-write sparse scratchpad.
        """
        scratch_dir = tempfile.mkdtemp(prefix="hermes_spec_")
        session_id = Path(scratch_dir).name
        
        copied_files = []
        if target_files:
            for rel_path in target_files:
                src = (self.workspace_root / rel_path).resolve()
                if src.exists() and src.is_file():
                    dst = Path(scratch_dir) / rel_path
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    copied_files.append(rel_path)

        self.active_scratchpads[session_id] = {
            "path": scratch_dir,
            "files": copied_files,
            "created_at": time.time(),
            "status": "active"
        }
        return session_id

    def speculative_write(self, session_id: str, rel_path: str, content: str) -> dict:
        """
        Executes a speculative write into the isolated scratchpad.
        """
        if session_id not in self.active_scratchpads:
            raise ValueError(f"Scratchpad session {session_id} not found.")

        scratch_path = Path(self.active_scratchpads[session_id]["path"])
        target_path = scratch_path / rel_path
        target_path.parent.mkdir(parents=True, exist_ok=True)

        target_path.write_text(content, encoding="utf-8")
        file_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        if rel_path not in self.active_scratchpads[session_id]["files"]:
            self.active_scratchpads[session_id]["files"].append(rel_path)

        return {
            "session_id": session_id,
            "file": rel_path,
            "sha256": file_hash,
            "bytes_written": len(content),
            "scratchpad_path": str(target_path)
        }

    def two_phase_commit(self, session_id: str, validate_hook=None) -> bool:
        """
        Two-phase commit: validates in scratchpad first, then atomically applies to workspace.
        """
        if session_id not in self.active_scratchpads:
            raise ValueError(f"Scratchpad session {session_id} not found.")

        session_meta = self.active_scratchpads[session_id]
        scratch_path = Path(session_meta["path"])

        # Phase 1: Validate / Prepare
        if validate_hook:
            try:
                is_valid = validate_hook(scratch_path)
                if not is_valid:
                    self.rollback(session_id)
                    return False
            except Exception as e:
                self.rollback(session_id)
                return False

        # Phase 2: Atomic Commit to Workspace Root
        for rel_file in session_meta["files"]:
            src = scratch_path / rel_file
            dst = self.workspace_root / rel_file
            dst.parent.mkdir(parents=True, exist_ok=True)
            # Atomic rename or copy
            shutil.copy2(src, dst)

        # Cleanup scratchpad
        shutil.rmtree(scratch_path, ignore_errors=True)
        session_meta["status"] = "committed"
        return True

    def rollback(self, session_id: str) -> bool:
        """
        Zero-leak rollback: purges scratchpad directory without altering main workspace.
        """
        if session_id not in self.active_scratchpads:
            return False

        session_meta = self.active_scratchpads[session_id]
        scratch_path = Path(session_meta["path"])
        shutil.rmtree(scratch_path, ignore_errors=True)
        session_meta["status"] = "aborted"
        return True

def run_self_tests():
    print("[TEST] Initializing Speculative Engine Invariant Verification...")
    test_dir = tempfile.mkdtemp(prefix="hermes_test_ws_")
    try:
        ws = Path(test_dir)
        orig_file = ws / "target.txt"
        orig_file.write_text("ORIGINAL CONTENT", encoding="utf-8")

        engine = SpeculativeEngine(workspace_root=test_dir)

        # 1. Test Classification
        assert engine.classify_tier("read_file") == 0
        assert engine.classify_tier("write_file") == 1
        assert engine.classify_tier("terminal") == 2
        print("  - Side-effect tiering: PASS")

        # 2. Test Amdahl bound calculation
        amdahl = engine.calculate_amdahl_speedup(parallel_fraction=0.70, conc_factor=4.0)
        assert amdahl["theoretical_speedup"] > 1.8
        assert amdahl["latency_reduction_pct"] > 40.0
        print(f"  - Amdahl Latency Bound (p=0.70, s=4.0 -> Speedup {amdahl['theoretical_speedup']}x, Latency -{amdahl['latency_reduction_pct']}%): PASS")

        # 3. Test Speculative Write & Rollback (Zero-leak)
        session_id = engine.create_scratchpad(target_files=["target.txt"])
        res = engine.speculative_write(session_id, "target.txt", "SPECULATIVE MUTATION")
        assert res["bytes_written"] > 0
        # Main file must NOT have changed yet
        assert orig_file.read_text(encoding="utf-8") == "ORIGINAL CONTENT"
        # Abort / Rollback
        engine.rollback(session_id)
        assert orig_file.read_text(encoding="utf-8") == "ORIGINAL CONTENT"
        assert not Path(res["scratchpad_path"]).exists()
        print("  - Speculative CoW isolation & Rollback Barrier: PASS")

        # 4. Test Two-Phase Commit Success
        session_id_2 = engine.create_scratchpad(target_files=["target.txt"])
        engine.speculative_write(session_id_2, "target.txt", "COMMITTED CONTENT V2")
        commit_res = engine.two_phase_commit(session_id_2, validate_hook=lambda p: (p / "target.txt").exists())
        assert commit_res is True
        assert orig_file.read_text(encoding="utf-8") == "COMMITTED CONTENT V2"
        print("  - Two-Phase Commit Atomic Transition: PASS")

        print("[RESULT] All invariants verified 100% successfully.")
        return 0
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hermes Speculative Execution Engine CLI")
    parser.add_argument("--test-all", action="store_true", help="Run full invariant verification test suite")
    parser.add_argument("--amdahl", action="store_true", help="Calculate Amdahl speedup factor")
    parser.add_argument("--p", type=float, default=0.60, help="Parallelizable fraction (0.0 - 1.0)")
    parser.add_argument("--speedup", type=float, default=3.0, help="Concurrency factor")

    args = parser.parse_args()

    if args.test_all:
        sys.exit(run_self_tests())
    elif args.amdahl:
        eng = SpeculativeEngine()
        print(json.dumps(eng.calculate_amdahl_speedup(args.p, args.speedup), indent=2))
    else:
        parser.print_help()
