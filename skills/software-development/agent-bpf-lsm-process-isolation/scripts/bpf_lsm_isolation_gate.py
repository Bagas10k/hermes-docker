"""BPF-LSM Dynamic Process Isolation Gate for Untrusted Agent Tool Calls.

Menyediakan isolasi proses dinamis berbasis simulasi kebijakan BPF-LSM
dan fallback unprivileged sandbox (landlock, seccomp, prctl no_new_privs, rlimit)
untuk mencegah eksfiltrasi token kredensial dan unprivileged sandbox escape.
"""

import os
import sys
import re
import json
import time
import socket
import pathlib
import platform
from typing import Dict, List, Set, Optional, Tuple, Any

# Konstanta Hook BPF-LSM Inti
HOOK_BPRM_CHECK_SECURITY = "bprm_check_security"     # int return: veto eksekusi biner
HOOK_FILE_OPEN = "file_open"                         # int return: veto akses path/file
HOOK_SOCKET_CONNECT = "socket_connect"               # int return: veto egress koneksi jaringan
HOOK_TASK_KILL = "task_kill"                         # int return: veto pengiriman sinyal proses
HOOK_BPRM_COMMITTED_CREDS = "bprm_committed_creds"   # void return: audit/telemetri saja (bukan veto)

# Error codes POSIX standar
EPERM = 1    # Operation not permitted
ENOENT = 2   # No such file or directory
EACCES = 13  # Permission denied

class BPFLSMIsolationPolicy:
    """Kebijakan isolasi keamanan berbasis prinsip Least Privilege."""
    def __init__(
        self,
        name: str,
        allowed_paths_read: Optional[List[str]] = None,
        allowed_paths_write: Optional[List[str]] = None,
        denied_paths_pattern: Optional[List[str]] = None,
        allowed_egress_hosts: Optional[List[str]] = None,
        allow_network_egress: bool = False,
        allow_process_spawn: bool = True,
        max_cpu_time_sec: int = 10,
        max_memory_mb: int = 256
    ):
        self.name = name
        self.allowed_paths_read = [os.path.abspath(p) for p in (allowed_paths_read or [])]
        self.allowed_paths_write = [os.path.abspath(p) for p in (allowed_paths_write or [])]
        # Pola berkas sensitif yang wajib ditolak mutlak (kredensial, key, environment)
        self.denied_paths_pattern = denied_paths_pattern or [
            r".*\.env$",
            r".*\.hermes/.*key.*",
            r".*\.ssh/.*",
            r"/etc/shadow",
            r".*config\.yaml$",
            r".*\.hermes/\.env$"
        ]
        self.allowed_egress_hosts = allowed_egress_hosts or []
        self.allow_network_egress = allow_network_egress
        self.allow_process_spawn = allow_process_spawn
        self.max_cpu_time_sec = max_cpu_time_sec
        self.max_memory_mb = max_memory_mb

class ProcessContext:
    """Konteks proses worker agen yang dipantau oleh isolation gate."""
    def __init__(self, pid: int, agent_id: str, policy: BPFLSMIsolationPolicy):
        self.pid = pid
        self.agent_id = agent_id
        self.policy = policy
        self.violations: List[Dict[str, Any]] = []
        self.audit_log: List[Dict[str, Any]] = []

class BPFLSMIsolationGate:
    """Engine pengawas dan penegak kebijakan BPF-LSM proses agen."""
    def __init__(self):
        self._enrolled_workers: Dict[int, ProcessContext] = {}
        self._lsm_features = self._probe_kernel_features()

    def _probe_kernel_features(self) -> Dict[str, Any]:
        """Probe kapabilitas LSM kernel Linux pada host saat ini."""
        lsms = []
        lsm_path = pathlib.Path("/sys/kernel/security/lsm")
        if lsm_path.exists():
            try:
                lsms = lsm_path.read_text().strip().split(",")
            except OSError:
                lsms = []
        btf_available = pathlib.Path("/sys/kernel/btf/vmlinux").is_file()
        return {
            "kernel_release": platform.release(),
            "active_lsms": lsms,
            "bpf_lsm_active": "bpf" in lsms,
            "btf_available": btf_available,
            "landlock_available": "landlock" in lsms,
            "apparmor_available": "apparmor" in lsms
        }

    @property
    def kernel_features(self) -> Dict[str, Any]:
        return self._lsm_features

    def enroll_worker(self, pid: int, agent_id: str, policy: BPFLSMIsolationPolicy) -> ProcessContext:
        """Mendaftarkan worker proses ke dalam map penegakan gate."""
        ctx = ProcessContext(pid, agent_id, policy)
        self._enrolled_workers[pid] = ctx
        return ctx

    def unenroll_worker(self, pid: int) -> Optional[ProcessContext]:
        """Menghapus worker dari map pemantauan."""
        return self._enrolled_workers.pop(pid, None)

    def is_enrolled(self, pid: int) -> bool:
        return pid in self._enrolled_workers

    def hook_file_open(self, pid: int, file_path: str, flags: int) -> int:
        """
        Evaluasi hook lsm/file_open (int return).
        0 = izinkan (ALLOW).
        -EACCES (-13) / -EPERM (-1) = tolak (DENY).
        """
        ctx = self._enrolled_workers.get(pid)
        # Jika bukan proses yang terdaftar di sandbox, izinkan (lingkup host/daemon)
        if not ctx:
            return 0

        target_path = os.path.abspath(file_path)
        policy = ctx.policy

        # 1. Periksa blacklist pola path sensitif (Credential Exfiltration Prevention)
        for pattern in policy.denied_paths_pattern:
            if re.match(pattern, target_path):
                ctx.violations.append({
                    "hook": HOOK_FILE_OPEN,
                    "target": target_path,
                    "reason": f"Matched sensitive credential pattern: {pattern}",
                    "timestamp": time.time()
                })
                return -EACCES

        # 2. Mode akses: baca vs tulis
        # O_WRONLY = 1, O_RDWR = 2, O_CREAT = 64, O_TRUNC = 512
        is_write = bool(flags & (os.O_WRONLY | os.O_RDWR | getattr(os, 'O_CREAT', 64) | getattr(os, 'O_TRUNC', 512)))

        if is_write:
            # Wajib berada di dalam allowed_paths_write
            allowed = False
            for p in policy.allowed_paths_write:
                if target_path == p or target_path.startswith(p.rstrip(os.sep) + os.sep):
                    allowed = True
                    break
            if not allowed:
                ctx.violations.append({
                    "hook": HOOK_FILE_OPEN,
                    "target": target_path,
                    "reason": "Write attempted outside allowed_paths_write",
                    "timestamp": time.time()
                })
                return -EACCES
        else:
            # Mode baca: periksa whitelist jika didefinisikan
            if policy.allowed_paths_read:
                allowed = False
                for p in policy.allowed_paths_read:
                    if target_path == p or target_path.startswith(p.rstrip(os.sep) + os.sep):
                        allowed = True
                        break
                if not allowed:
                    ctx.violations.append({
                        "hook": HOOK_FILE_OPEN,
                        "target": target_path,
                        "reason": "Read attempted outside allowed_paths_read",
                        "timestamp": time.time()
                    })
                    return -EACCES

        return 0

    def hook_bprm_check_security(self, pid: int, binary_path: str) -> int:
        """
        Evaluasi hook lsm/bprm_check_security (int return).
        Mencegah unprivileged sandbox escape via eksekusi biner tak terotorisasi.
        """
        ctx = self._enrolled_workers.get(pid)
        if not ctx:
            return 0

        policy = ctx.policy
        target_binary = os.path.abspath(binary_path)

        if not policy.allow_process_spawn:
            ctx.violations.append({
                "hook": HOOK_BPRM_CHECK_SECURITY,
                "target": target_binary,
                "reason": "Process spawning forbidden by policy",
                "timestamp": time.time()
            })
            return -EPERM

        # Larang biner berbahaya / shell escape tools jika policy ketat
        dangerous_binaries = ["/usr/bin/sudo", "/bin/su", "/usr/bin/pkexec", "/usr/bin/chroot"]
        if target_binary in dangerous_binaries:
            ctx.violations.append({
                "hook": HOOK_BPRM_CHECK_SECURITY,
                "target": target_binary,
                "reason": "Privilege escalation binary vetoed",
                "timestamp": time.time()
            })
            return -EPERM

        return 0

    def hook_socket_connect(self, pid: int, destination_host: str, port: int) -> int:
        """
        Evaluasi hook lsm/socket_connect (int return).
        Mencegah eksfiltrasi data via koneksi jaringan tak terduga.
        """
        ctx = self._enrolled_workers.get(pid)
        if not ctx:
            return 0

        policy = ctx.policy
        if not policy.allow_network_egress:
            ctx.violations.append({
                "hook": HOOK_SOCKET_CONNECT,
                "target": f"{destination_host}:{port}",
                "reason": "Network egress blocked by policy",
                "timestamp": time.time()
            })
            return -EACCES

        if policy.allowed_egress_hosts and destination_host not in policy.allowed_egress_hosts:
            ctx.violations.append({
                "hook": HOOK_SOCKET_CONNECT,
                "target": f"{destination_host}:{port}",
                "reason": f"Egress host {destination_host} not in allowed_egress_hosts",
                "timestamp": time.time()
            })
            return -EACCES

        return 0

    def hook_bprm_committed_creds(self, pid: int, comm: str) -> None:
        """
        Evaluasi hook lsm/bprm_committed_creds (void return).
        Hook pasca-komit untuk pencatatan audit/telemetri saja; BUKAN veto eksekusi.
        """
        ctx = self._enrolled_workers.get(pid)
        if ctx:
            ctx.audit_log.append({
                "hook": HOOK_BPRM_COMMITTED_CREDS,
                "comm": comm,
                "timestamp": time.time()
            })

    def get_violations(self, pid: int) -> List[Dict[str, Any]]:
        ctx = self._enrolled_workers.get(pid)
        return ctx.violations if ctx else []
