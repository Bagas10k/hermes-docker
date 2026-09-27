#!/usr/bin/env python3
"""
Transactional Hot-Patching Engine with Shadow Workspace & Atomic Rollback.
Developed by Bagas Cihuy & Hermes Agent.
"""

import os
import sys
import shutil
import tempfile
import argparse
import subprocess
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional

class TransactionalPatchManager:
    def __init__(self, target_dir: str, shadow_root: Optional[str] = None):
        self.target_dir = Path(target_dir).resolve()
        if not self.target_dir.exists():
            raise FileNotFoundError(f"Target directory {self.target_dir} does not exist.")
        
        self.shadow_root = Path(shadow_root).resolve() if shadow_root else Path(tempfile.gettempdir()) / "hermes_shadow_patches"
        self.shadow_root.mkdir(parents=True, exist_ok=True)
        self.session_id = hashlib.sha256(os.urandom(16)).hexdigest()[:12]
        self.shadow_dir = self.shadow_root / f"tx_{self.session_id}"
        self.backup_dir = self.shadow_root / f"bak_{self.session_id}"
        self.modified_files: List[Path] = []
        self.committed = False

    def create_shadow_copy(self, file_paths: List[str]) -> Path:
        """Create isolated shadow workspace copy for target files (COW-style staged isolation)."""
        self.shadow_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        for fp in file_paths:
            src = (self.target_dir / fp).resolve()
            if not src.exists():
                raise FileNotFoundError(f"Target file {src} not found in {self.target_dir}")
            rel = src.relative_to(self.target_dir)
            shadow_dest = self.shadow_dir / rel
            backup_dest = self.backup_dir / rel
            
            shadow_dest.parent.mkdir(parents=True, exist_ok=True)
            backup_dest.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(src, shadow_dest)
            shutil.copy2(src, backup_dest)
            self.modified_files.append(rel)
            
        return self.shadow_dir

    def apply_patch(self, rel_path: str, patch_fn) -> bool:
        """Apply mutation function to the file inside shadow workspace."""
        shadow_file = self.shadow_dir / rel_path
        if not shadow_file.exists():
            raise FileNotFoundError(f"Shadow file {shadow_file} does not exist.")
        
        content = shadow_file.read_text(encoding="utf-8")
        new_content = patch_fn(content)
        shadow_file.write_text(new_content, encoding="utf-8")
        return True

    def verify_shadow_health(self, check_cmd: str, timeout: int = 30) -> Dict[str, Any]:
        """Phase 1: Run pre-commit health check and invariant test against shadow files."""
        env = os.environ.copy()
        env["HERMES_SHADOW_WORKSPACE"] = str(self.shadow_dir)
        env["PYTHONPATH"] = f"{self.shadow_dir}:{env.get('PYTHONPATH', '')}"
        
        try:
            res = subprocess.run(
                check_cmd,
                shell=True,
                cwd=str(self.shadow_dir),
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "success": res.returncode == 0,
                "exit_code": res.returncode,
                "stdout": res.stdout,
                "stderr": res.stderr
            }
        except subprocess.TimeoutExpired as e:
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Health check timed out after {timeout}s: {e}"
            }

    def commit(self, post_verify_cmd: Optional[str] = None) -> Dict[str, Any]:
        """Phase 2: Atomic commit to live target directory. Instant rollback on failure."""
        if not self.modified_files:
            return {"success": False, "error": "No files staged in transaction"}

        applied_files = []
        try:
            # Atomic file swap via tmp replacements
            for rel in self.modified_files:
                src_shadow = self.shadow_dir / rel
                target_dest = self.target_dir / rel
                tmp_dest = target_dest.with_suffix(target_dest.suffix + ".atomic_tmp")
                
                shutil.copy2(src_shadow, tmp_dest)
                os.replace(tmp_dest, target_dest)
                applied_files.append(rel)

            # Optional post-commit probe on live directory
            if post_verify_cmd:
                res = subprocess.run(
                    post_verify_cmd,
                    shell=True,
                    cwd=str(self.target_dir),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if res.returncode != 0:
                    raise RuntimeError(f"Post-commit live verification failed: {res.stderr or res.stdout}")

            self.committed = True
            # Clean up shadow
            shutil.rmtree(self.shadow_dir, ignore_errors=True)
            shutil.rmtree(self.backup_dir, ignore_errors=True)
            return {"success": True, "committed_files": [str(f) for f in applied_files]}

        except Exception as e:
            # Instant atomic rollback from backup
            rollback_errs = []
            for rel in applied_files:
                try:
                    src_bak = self.backup_dir / rel
                    target_dest = self.target_dir / rel
                    tmp_dest = target_dest.with_suffix(target_dest.suffix + ".rb_tmp")
                    shutil.copy2(src_bak, tmp_dest)
                    os.replace(tmp_dest, target_dest)
                except Exception as rb_e:
                    rollback_errs.append(str(rb_e))
            
            return {
                "success": False,
                "error": f"Commit failed: {e}. Rollback executed. Rollback errors: {rollback_errs}",
                "rolled_back": True
            }

    def rollback(self) -> bool:
        """Explicit pre-commit abort: discard shadow without altering live target."""
        shutil.rmtree(self.shadow_dir, ignore_errors=True)
        shutil.rmtree(self.backup_dir, ignore_errors=True)
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hermes Transactional Hot-Patching Engine")
    parser.add_argument("--target", required=True, help="Target workspace path")
    parser.add_argument("--files", nargs="+", required=True, help="Relative files to stage")
    parser.add_argument("--check-cmd", required=True, help="Command to run in shadow directory")
    args = parser.parse_args()

    mgr = TransactionalPatchManager(args.target)
    mgr.create_shadow_copy(args.files)
    print(f"Shadow workspace initialized: {mgr.shadow_dir}")
    v_res = mgr.verify_shadow_health(args.check_cmd)
    print(f"Shadow verification result: {v_res}")
    if not v_res["success"]:
        mgr.rollback()
        print("Verification failed. Aborted and rolled back shadow.")
        sys.exit(1)
    c_res = mgr.commit()
    print(f"Commit result: {c_res}")
    sys.exit(0 if c_res["success"] else 1)
