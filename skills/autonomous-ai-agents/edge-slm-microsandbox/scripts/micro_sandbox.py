#!/usr/bin/env python3
"""
Ephemeral Micro-Sandbox for Edge SLM Tool Calling
Menyediakan isolasi runtime berkecepatan tinggi (<5ms startup) tanpa Docker.
Menggunakan POSIX rlimit (RLIMIT_AS, RLIMIT_CPU, RLIMIT_NOFILE) dan subproses terisolasi.
"""

import os
import sys
import time
import signal
import resource
import subprocess
from dataclasses import dataclass
from typing import Optional, List, Dict

@dataclass
class EphemeralResourceQuota:
    max_memory_bytes: int = 128 * 1024 * 1024  # 128 MB RAM
    max_cpu_seconds: int = 3                   # 3 detik CPU time
    max_wall_time_seconds: float = 5.0         # 5 detik Wall clock timeout
    max_open_files: int = 64                   # File descriptor limit
    max_output_bytes: int = 64 * 1024          # 64 KB output buffer cap

@dataclass
class SandboxResult:
    exit_code: int
    stdout: str
    stderr: str
    duration_s: float
    is_success: bool
    killed_by: Optional[str] = None
    output_truncated: bool = False

def _build_preexec(quota: EphemeralResourceQuota):
    def preexec():
        # 1. Batasi Virtual Memory (RLIMIT_AS)
        try:
            resource.setrlimit(resource.RLIMIT_AS, (quota.max_memory_bytes, quota.max_memory_bytes))
        except (ValueError, OSError):
            pass

        # 2. Batasi CPU time (RLIMIT_CPU)
        try:
            resource.setrlimit(resource.RLIMIT_CPU, (quota.max_cpu_seconds, quota.max_cpu_seconds))
        except (ValueError, OSError):
            pass

        # 3. Batasi Open File Descriptors (RLIMIT_NOFILE)
        try:
            resource.setrlimit(resource.RLIMIT_NOFILE, (quota.max_open_files, quota.max_open_files))
        except (ValueError, OSError):
            pass

        # 4. Isolasi Process Group agar killpg dapat membersihkan seluruh child
        os.setpgrp()

    return preexec

def run_in_microsandbox(
    cmd: List[str],
    quota: Optional[EphemeralResourceQuota] = None,
    stdin_data: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    cwd: Optional[str] = None
) -> SandboxResult:
    if quota is None:
        quota = EphemeralResourceQuota()

    start_time = time.monotonic()
    clean_env = env if env is not None else {
        "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
        "LANG": "C.UTF-8",
        "PYTHONUNBUFFERED": "1"
    }

    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE if stdin_data else subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=clean_env,
            cwd=cwd,
            preexec_fn=_build_preexec(quota)
        )
    except Exception as e:
        duration = time.monotonic() - start_time
        return SandboxResult(
            exit_code=127,
            stdout="",
            stderr=f"Spawn failed: {str(e)}",
            duration_s=duration,
            is_success=False,
            killed_by="spawn_error"
        )

    killed_by = None
    try:
        stdout_raw, stderr_raw = proc.communicate(
            input=stdin_data.encode('utf-8') if stdin_data else None,
            timeout=quota.max_wall_time_seconds
        )
    except subprocess.TimeoutExpired:
        killed_by = "timeout"
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except OSError:
            pass
        stdout_raw, stderr_raw = proc.communicate()

    duration = time.monotonic() - start_time
    exit_code = proc.returncode

    # Deteksi penyebab terminasi jika ada signal
    if killed_by is None and exit_code is not None:
        if exit_code < 0:
            sig = -exit_code
            if sig == signal.SIGXCPU:
                killed_by = "cpu_limit"
            elif sig in (signal.SIGSEGV, signal.SIGABRT):
                killed_by = "memory_limit"
            elif sig == signal.SIGKILL:
                killed_by = "sigkill"
            else:
                killed_by = f"signal_{sig}"
        elif exit_code != 0:
            stderr_str = stderr_raw.decode('utf-8', errors='replace')
            if "MemoryError" in stderr_str:
                killed_by = "memory_limit"

    out_truncated = len(stdout_raw) > quota.max_output_bytes
    stdout_str = stdout_raw[:quota.max_output_bytes].decode('utf-8', errors='replace')
    stderr_str = stderr_raw[:quota.max_output_bytes].decode('utf-8', errors='replace')

    return SandboxResult(
        exit_code=exit_code if exit_code is not None else -1,
        stdout=stdout_str,
        stderr=stderr_str,
        duration_s=duration,
        is_success=(exit_code == 0 and killed_by is None),
        killed_by=killed_by,
        output_truncated=out_truncated
    )

if __name__ == "__main__":
    import json
    if len(sys.argv) < 2:
        print("Usage: micro_sandbox.py <command...>")
        sys.exit(1)
    res = run_in_microsandbox(sys.argv[1:])
    print(json.dumps({
        "exit_code": res.exit_code,
        "is_success": res.is_success,
        "killed_by": res.killed_by,
        "duration_s": round(res.duration_s, 4),
        "stdout": res.stdout,
        "stderr": res.stderr
    }, indent=2))
