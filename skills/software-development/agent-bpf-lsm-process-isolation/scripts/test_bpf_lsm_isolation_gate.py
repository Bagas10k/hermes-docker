"""Deterministic Unit Tests for BPF-LSM Dynamic Process Isolation Gate."""

import os
import unittest
import time
from bpf_lsm_isolation_gate import (
    BPFLSMIsolationGate,
    BPFLSMIsolationPolicy,
    HOOK_FILE_OPEN,
    HOOK_BPRM_CHECK_SECURITY,
    HOOK_SOCKET_CONNECT,
    HOOK_BPRM_COMMITTED_CREDS,
    EACCES,
    EPERM
)

class TestBPFLSMIsolationGate(unittest.TestCase):
    def setUp(self):
        self.gate = BPFLSMIsolationGate()
        self.policy = BPFLSMIsolationPolicy(
            name="sandboxed-agent-tool",
            allowed_paths_read=["/tmp/agent-workdir", "/usr/lib", "/etc/ssl"],
            allowed_paths_write=["/tmp/agent-workdir/output"],
            allow_network_egress=False,
            allow_process_spawn=True
        )
        self.worker_pid = 4242
        self.gate.enroll_worker(self.worker_pid, "subagent-coder-1", self.policy)

    def test_01_kernel_feature_probe(self):
        """Memverifikasi probe kapabilitas LSM kernel Linux berjalan aman & deterministik."""
        features = self.gate.kernel_features
        self.assertIn("kernel_release", features)
        self.assertIn("active_lsms", features)
        self.assertIsInstance(features["active_lsms"], list)
        self.assertIsInstance(features["bpf_lsm_active"], bool)

    def test_02_unenrolled_process_unrestricted(self):
        """Proses host di luar sandbox tidak boleh terhambat oleh isolasi worker."""
        host_pid = 1001
        self.assertFalse(self.gate.is_enrolled(host_pid))
        # Akses file sensitif oleh host diizinkan oleh gate (scope isolasi khusus worker)
        res = self.gate.hook_file_open(host_pid, "/home/ubuntu/.hermes/.env", os.O_RDONLY)
        self.assertEqual(res, 0)
        # Eksekusi biner oleh host diizinkan
        res_exec = self.gate.hook_bprm_check_security(host_pid, "/usr/bin/sudo")
        self.assertEqual(res_exec, 0)

    def test_03_credential_exfiltration_file_open_veto(self):
        """Upaya pembacaan kredensial sensitif (.env, config.yaml, ssh) wajib ditolak mutlak (-EACCES)."""
        # Uji baca .env
        res1 = self.gate.hook_file_open(self.worker_pid, "/home/ubuntu/.hermes/.env", os.O_RDONLY)
        self.assertEqual(res1, -EACCES)

        # Uji baca ssh key
        res2 = self.gate.hook_file_open(self.worker_pid, "/home/ubuntu/.ssh/id_rsa", os.O_RDONLY)
        self.assertEqual(res2, -EACCES)

        # Uji baca config.yaml
        res3 = self.gate.hook_file_open(self.worker_pid, "/home/ubuntu/.hermes/config.yaml", os.O_RDONLY)
        self.assertEqual(res3, -EACCES)

        violations = self.gate.get_violations(self.worker_pid)
        self.assertEqual(len(violations), 3)
        self.assertTrue(any("credential pattern" in v["reason"] for v in violations))

    def test_04_filesystem_write_boundary(self):
        """Penulisan di luar allowed_paths_write wajib ditolak (-EACCES)."""
        # Tulis di folder output yang sah -> ALLOW
        res_ok = self.gate.hook_file_open(self.worker_pid, "/tmp/agent-workdir/output/result.txt", os.O_WRONLY)
        self.assertEqual(res_ok, 0)

        # Tulis di luar folder output -> DENY
        res_fail = self.gate.hook_file_open(self.worker_pid, "/tmp/agent-workdir/escape.sh", os.O_WRONLY)
        self.assertEqual(res_fail, -EACCES)

        # Tulis di /etc/hosts -> DENY
        res_root = self.gate.hook_file_open(self.worker_pid, "/etc/hosts", os.O_RDWR)
        self.assertEqual(res_root, -EACCES)

    def test_05_network_egress_blocking(self):
        """Mencegah transmisi token/data ke internet ketika network egress dinonaktifkan."""
        res = self.gate.hook_socket_connect(self.worker_pid, "attacker-c2.com", 443)
        self.assertEqual(res, -EACCES)
        violations = self.gate.get_violations(self.worker_pid)
        self.assertTrue(any("Network egress blocked" in v["reason"] for v in violations))

    def test_06_privilege_escalation_binary_veto(self):
        """Eksekusi binary sudo/su/chroot untuk privilege escalation wajib diveto (-EPERM)."""
        res_sudo = self.gate.hook_bprm_check_security(self.worker_pid, "/usr/bin/sudo")
        self.assertEqual(res_sudo, -EPERM)

        res_su = self.gate.hook_bprm_check_security(self.worker_pid, "/bin/su")
        self.assertEqual(res_su, -EPERM)

        # Binary biasa dalam workdir diizinkan jika allow_process_spawn=True
        res_python = self.gate.hook_bprm_check_security(self.worker_pid, "/usr/bin/python3")
        self.assertEqual(res_python, 0)

    def test_07_post_commit_audit_hook_semantics(self):
        """bprm_committed_creds adalah hook audit (void return) dan tidak menghasilkan veto eksekusi."""
        # Panggil committed creds
        self.gate.hook_bprm_committed_creds(self.worker_pid, "python3-worker")
        ctx = self.gate._enrolled_workers[self.worker_pid]
        self.assertEqual(len(ctx.audit_log), 1)
        self.assertEqual(ctx.audit_log[0]["hook"], HOOK_BPRM_COMMITTED_CREDS)
        self.assertEqual(ctx.audit_log[0]["comm"], "python3-worker")

    def test_08_worker_unenrollment_lifecycle(self):
        """Worker yang selesai ditutup dapat dihapus dari pengawasan secara atomik."""
        self.assertTrue(self.gate.is_enrolled(self.worker_pid))
        removed = self.gate.unenroll_worker(self.worker_pid)
        self.assertIsNotNone(removed)
        self.assertFalse(self.gate.is_enrolled(self.worker_pid))
        # Setelah di-unenroll, hak akses kembali ke default host
        res = self.gate.hook_file_open(self.worker_pid, "/home/ubuntu/.hermes/.env", os.O_RDONLY)
        self.assertEqual(res, 0)

if __name__ == '__main__':
    unittest.main()
