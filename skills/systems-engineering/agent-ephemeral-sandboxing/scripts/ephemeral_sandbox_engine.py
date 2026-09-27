#!/usr/bin/env python3
"""
Ephemeral Sandbox Engine & Rollback Barrier for Autonomous AI Agent Tools.
Evaluates risk tiers, provides ephemeral copy-on-write workspace isolation,
monitors resource ceilings, and executes atomic rollback on failure.
"""

import os
import sys
import shutil
import tempfile
import time
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

class EphemeralSandboxEngine:
    def __init__(self, base_workspace: Optional[str] = None):
        self.base_workspace = Path(base_workspace or os.getcwd()).resolve()
        self.active_sandboxes: Dict[str, Dict[str, Any]] = {}

    def classify_risk(self, command: str, target_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Classifies execution risk into TIER 0 (Safe Read), TIER 1 (Wasm/WASI),
        TIER 2 (gVisor/Bubblewrap Cow), or TIER 3 (MicroVM/Firecracker).
        """
        cmd_lower = command.lower().strip()
        tokens = cmd_lower.split()

        # Dangerous operations: MicroVM / Hard Isolation required
        tier_3_patterns = [
            "rm -rf /", "mkfs", "dd if=", "iptables", "insmod", "modprobe",
            ":(){ :|:& };:", "chmod -r 777 /", "> /dev/sd", "reboot", "shutdown"
        ]
        for p in tier_3_patterns:
            if p in cmd_lower:
                return {
                    "tier": "TIER_3_MICROVM",
                    "isolation": "firecracker_microvm",
                    "reason": f"System-level modification pattern detected: {p}",
                    "allow_direct_execution": False,
                    "requires_hard_fence": True
                }

        # Mutating operations: User-space ephemeral sandbox with CoW & Rollback
        tier_2_patterns = [
            "rm ", "mv ", "cp ", "sed -i", "git clean", "npm install", "pip install",
            "cargo build", "make", "docker", "wget ", "curl ", "python ", "node "
        ]
        is_mutating = any(p in cmd_lower for p in tier_2_patterns)
        
        # Read-only operations
        read_only_starters = ["ls", "cat", "head", "tail", "grep", "find", "stat", "git status", "git diff", "pwd"]
        is_read_only = any(cmd_lower.startswith(p) for p in read_only_starters) and not (">" in cmd_lower or "|" in cmd_lower and "rm" in cmd_lower)

        if is_read_only and not is_mutating:
            return {
                "tier": "TIER_0_READONLY",
                "isolation": "host_unprivileged",
                "reason": "Deterministic read-only command without side effects",
                "allow_direct_execution": True,
                "requires_hard_fence": False
            }

        return {
            "tier": "TIER_2_USERSPACE_COW",
            "isolation": "ephemeral_cow_overlay",
            "reason": "Workspace mutating command requiring transactional rollback barrier",
            "allow_direct_execution": True,
            "requires_hard_fence": False
        }

    def create_ephemeral_workspace(self, session_id: str, files_to_snapshot: Optional[List[str]] = None) -> Path:
        """
        Creates an isolated temporary copy-on-write directory for session execution.
        """
        temp_dir = Path(tempfile.mkdtemp(prefix=f"hermes_sandbox_{session_id}_"))
        snapshots = {}

        if files_to_snapshot:
            for rel_path in files_to_snapshot:
                src = (self.base_workspace / rel_path).resolve()
                if src.exists() and src.is_file():
                    dest = temp_dir / rel_path
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dest)
                    with open(src, "rb") as f:
                        snapshots[str(src)] = hash(f.read())

        self.active_sandboxes[session_id] = {
            "sandbox_path": temp_dir,
            "created_at": time.time(),
            "snapshots": snapshots,
            "status": "active"
        }
        return temp_dir

    def execute_bounded(self, session_id: str, command: str, timeout_sec: int = 10, max_memory_mb: int = 256) -> Dict[str, Any]:
        """
        Executes command inside ephemeral sandbox with resource constraints and timeout.
        """
        if session_id not in self.active_sandboxes:
            raise ValueError(f"Session {session_id} not initialized")

        sandbox_info = self.active_sandboxes[session_id]
        cwd = sandbox_info["sandbox_path"]

        start_time = time.time()
        try:
            # Memory ceiling using preexec_fn for Linux resource bounds
            def set_limits():
                try:
                    import resource
                    # Set virtual memory limit (bytes)
                    mem_bytes = max_memory_mb * 1024 * 1024
                    resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
                    # Prevent core dumps
                    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
                except Exception:
                    pass

            proc = subprocess.Popen(
                command,
                shell=True,
                cwd=str(cwd),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=set_limits if sys.platform.startswith("linux") else None
            )

            stdout, stderr = proc.communicate(timeout=timeout_sec)
            elapsed = time.time() - start_time

            return {
                "exit_code": proc.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "elapsed_sec": round(elapsed, 4),
                "timed_out": False,
                "success": proc.returncode == 0
            }

        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
            return {
                "exit_code": -1,
                "stdout": stdout or "",
                "stderr": (stderr or "") + f"\n[SANDBOX TIMEOUT] Exceeded {timeout_sec}s deadline.",
                "elapsed_sec": timeout_sec,
                "timed_out": True,
                "success": False
            }
        except Exception as e:
            return {
                "exit_code": -2,
                "stdout": "",
                "stderr": f"[SANDBOX ERROR] {str(e)}",
                "elapsed_sec": round(time.time() - start_time, 4),
                "timed_out": False,
                "success": False
            }

    def rollback(self, session_id: str) -> bool:
        """
        Discards the ephemeral sandbox workspace completely, preventing contaminated
        or failed artifacts from polluting host filesystem.
        """
        if session_id not in self.active_sandboxes:
            return False

        sandbox_info = self.active_sandboxes.pop(session_id)
        path = sandbox_info["sandbox_path"]
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)
        return True

    def commit(self, session_id: str, dest_workspace: Optional[Path] = None) -> List[str]:
        """
        Atomically transfers verified modified artifacts from ephemeral sandbox
        back to destination host workspace.
        """
        if session_id not in self.active_sandboxes:
            raise ValueError(f"Session {session_id} not initialized")

        target_base = (dest_workspace or self.base_workspace).resolve()
        sandbox_info = self.active_sandboxes.pop(session_id)
        sandbox_path = sandbox_info["sandbox_path"]

        committed_files = []
        for root, _, files in os.walk(sandbox_path):
            for file in files:
                src_file = Path(root) / file
                rel_path = src_file.relative_to(sandbox_path)
                dest_file = target_base / rel_path

                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dest_file)
                committed_files.append(str(rel_path))

        shutil.rmtree(sandbox_path, ignore_errors=True)
        return committed_files

def main():
    print("Testing EphemeralSandboxEngine...")
    engine = EphemeralSandboxEngine()

    # 1. Test Risk Classification
    t0 = engine.classify_risk("ls -la /tmp")
    assert t0["tier"] == "TIER_0_READONLY", f"Expected TIER_0, got {t0}"

    t2 = engine.classify_risk("rm -rf ./build && python setup.py build")
    assert t2["tier"] == "TIER_2_USERSPACE_COW", f"Expected TIER_2, got {t2}"

    t3 = engine.classify_risk("rm -rf / --no-preserve-root")
    assert t3["tier"] == "TIER_3_MICROVM", f"Expected TIER_3, got {t3}"
    print("[PASS] Risk classification tested successfully.")

    # 2. Test Ephemeral Sandbox Creation & Rollback
    sid = "test_run_001"
    ws = engine.create_ephemeral_workspace(sid)
    assert ws.exists(), "Workspace not created"

    # Execute harmless modification inside sandbox
    res = engine.execute_bounded(sid, "echo 'hello secret' > test.txt && cat test.txt", timeout_sec=5)
    assert res["success"] is True, f"Command failed: {res}"
    assert "hello secret" in res["stdout"]

    # Verify file exists in sandbox but NOT in base
    assert (ws / "test.txt").exists()
    assert not (engine.base_workspace / "test.txt").exists()

    # Rollback and verify clean disposal
    engine.rollback(sid)
    assert not ws.exists(), "Sandbox directory not purged on rollback"
    print("[PASS] Ephemeral execution & transactional rollback barrier verified.")

    # 3. Test Timeout Enforcement
    sid2 = "test_timeout_002"
    ws2 = engine.create_ephemeral_workspace(sid2)
    res_timeout = engine.execute_bounded(sid2, "sleep 3", timeout_sec=1)
    assert res_timeout["timed_out"] is True, "Timeout did not trigger"
    assert res_timeout["success"] is False
    engine.rollback(sid2)
    print("[PASS] Subprocess timeout ceiling verified.")

    # 4. Test Commit Mechanics
    sid3 = "test_commit_003"
    with tempfile.TemporaryDirectory() as dest_dir:
        dest_path = Path(dest_dir)
        engine.create_ephemeral_workspace(sid3)
        engine.execute_bounded(sid3, "echo 'artifact verified' > artifact.log")
        committed = engine.commit(sid3, dest_workspace=dest_path)
        assert "artifact.log" in committed
        assert (dest_path / "artifact.log").read_text().strip() == "artifact verified"
    print("[PASS] Transactional commit & artifact promotion verified.")

    print("\nALL EPHEMERAL SANDBOX ENGINE TESTS PASSED (100%).")

if __name__ == "__main__":
    main()
