#!/usr/bin/env python3
"""
Deterministic Unit Tests for Seccomp-BPF Syscall Filter & Sandboxing Engine
Menguji perakitan instruksi BPF, evaluasi virtual machine filter syscall, dan penegakan batas keamanan.
"""

import unittest
import errno
from seccomp_bpf_filter import (
    SeccompPolicyBuilder, SeccompFilterSimulator, SockFilter,
    SECCOMP_RET_ALLOW, SECCOMP_RET_ERRNO, SECCOMP_RET_KILL_PROCESS,
    SYS_READ, SYS_WRITE, SYS_CLOSE, SYS_MMAP, SYS_BRK,
    SYS_PTRACE, SYS_UNSHARE, SYS_REBOOT, SYS_INIT_MODULE, SYS_BPF
)

class TestSeccompBPFFilter(unittest.TestCase):

    def setUp(self):
        self.builder = SeccompPolicyBuilder(default_action=SECCOMP_RET_KILL_PROCESS)
        # Izinkan syscall esensial
        for nr in (SYS_READ, SYS_WRITE, SYS_CLOSE, SYS_MMAP, SYS_BRK):
            self.builder.allow_syscall(nr)
        
        # Tolak syscall probing & debugging dengan EPERM
        self.builder.deny_with_errno(SYS_PTRACE, errno.EPERM)
        self.builder.deny_with_errno(SYS_BPF, errno.EACCES)

        # Bunuh proses jika mencoba manipulasi namespace atau reload kernel
        self.builder.deny_and_kill(SYS_UNSHARE)
        self.builder.deny_and_kill(SYS_REBOOT)
        self.builder.deny_and_kill(SYS_INIT_MODULE)

        self.prog = self.builder.assemble_bpf()
        self.sim = SeccompFilterSimulator(self.prog)

    def test_01_whitelist_allowed_syscalls(self):
        """Syscall esensial wajib menghasilkan SECCOMP_RET_ALLOW."""
        for nr in (SYS_READ, SYS_WRITE, SYS_CLOSE, SYS_MMAP, SYS_BRK):
            action = self.sim.evaluate_syscall(nr)
            self.assertEqual(action, SECCOMP_RET_ALLOW)

    def test_02_errno_veto_ptrace_and_bpf(self):
        """Syscall ptrace dan bpf wajib diveto dengan kode errno spesifik tanpa membunuh proses."""
        action_ptrace = self.sim.evaluate_syscall(SYS_PTRACE)
        expected_ptrace = SECCOMP_RET_ERRNO | (errno.EPERM & 0xFFFF)
        self.assertEqual(action_ptrace, expected_ptrace)

        action_bpf = self.sim.evaluate_syscall(SYS_BPF)
        expected_bpf = SECCOMP_RET_ERRNO | (errno.EACCES & 0xFFFF)
        self.assertEqual(action_bpf, expected_bpf)

    def test_03_sandbox_escape_kill_process(self):
        """Upaya eskalasi privileges (unshare, reboot, init_module) wajib memicu KILL_PROCESS."""
        for nr in (SYS_UNSHARE, SYS_REBOOT, SYS_INIT_MODULE):
            action = self.sim.evaluate_syscall(nr)
            self.assertEqual(action, SECCOMP_RET_KILL_PROCESS)

    def test_04_unregistered_syscall_default_kill(self):
        """Syscall yang tidak terdaftar sama sekali wajib jatuh ke aksi default (KILL_PROCESS)."""
        random_syscall = 999
        action = self.sim.evaluate_syscall(random_syscall)
        self.assertEqual(action, SECCOMP_RET_KILL_PROCESS)

    def test_05_bpf_instruction_packing_integrity(self):
        """Setiap instruksi BPF wajib tepat 8 byte biner sesuai spesifikasi kernel Linux."""
        for inst in self.prog:
            raw = inst.pack()
            self.assertEqual(len(raw), 8)

if __name__ == "__main__":
    unittest.main()
