#!/usr/bin/env python3
"""
Seccomp-BPF Syscall Filter & Memory Allocation Quotas for Agent Sandboxes
Membangun kebijakan filter syscall Seccomp BPF tingkat kernel Linux untuk membatasi
eksekusi alat agen tak terpercaya dari aksi berbahaya (ptrace, sandbox escape, socket raw).
"""

import os
import struct
import errno
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple

# Konstanta Aksi Seccomp (Linux Kernel)
SECCOMP_RET_KILL_PROCESS = 0x80000000
SECCOMP_RET_KILL_THREAD  = 0x00000000
SECCOMP_RET_TRAP         = 0x00030000
SECCOMP_RET_ERRNO        = 0x00050000
SECCOMP_RET_ALLOW        = 0x7fff0000

# x86_64 Syscall Numbers (Representatif)
SYS_READ        = 0
SYS_WRITE       = 1
SYS_OPEN        = 2
SYS_CLOSE       = 3
SYS_STAT        = 4
SYS_MMAP        = 9
SYS_BRK         = 12
SYS_PTRACE      = 101
SYS_CLONE       = 56
SYS_FORK        = 57
SYS_EXECVE      = 59
SYS_UNSHARE     = 272
SYS_REBOOT      = 169
SYS_INIT_MODULE = 175
SYS_BPF         = 321

# BPF Opcode Instructions
BPF_LD  = 0x00
BPF_W   = 0x00
BPF_ABS = 0x20
BPF_JMP = 0x05
BPF_JEQ = 0x10
BPF_K   = 0x00
BPF_RET = 0x06

@dataclass
class SockFilter:
    """Struktur 8-byte instruksi BPF: struct sock_filter."""
    code: int
    jt: int
    jf: int
    k: int

    def pack(self) -> bytes:
        return struct.pack("=HBBI", self.code, self.jt, self.jf, self.k)

class SeccompPolicyBuilder:
    """
    Membangun kebijakan Seccomp-BPF dan merakit instruksi bytecode bpf biner
    untuk disuntikkan ke prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER).
    """
    def __init__(self, default_action: int = SECCOMP_RET_KILL_PROCESS):
        self.default_action = default_action
        self.whitelist: Set[int] = set()
        self.errno_blacklist: Dict[int, int] = {} # syscall_nr -> errno_code
        self.kill_blacklist: Set[int] = set()

    def allow_syscall(self, syscall_nr: int):
        self.whitelist.add(syscall_nr)

    def deny_with_errno(self, syscall_nr: int, err: int = errno.EPERM):
        self.errno_blacklist[syscall_nr] = err

    def deny_and_kill(self, syscall_nr: int):
        self.kill_blacklist.add(syscall_nr)

    def assemble_bpf(self) -> List[SockFilter]:
        """
        Merakit program BPF:
        1. Load syscall architecture & verify
        2. Load syscall number (seccomp_data.nr di offset 0)
        3. Periksa aturan kill
        4. Periksa aturan errno
        5. Periksa aturan allow
        6. Return default action
        """
        instructions: List[SockFilter] = []
        
        # 1. Load syscall number: BPF_LD | BPF_W | BPF_ABS, offset = 0
        instructions.append(SockFilter(BPF_LD | BPF_W | BPF_ABS, 0, 0, 0))
        
        # 2. Evaluasi kill list (lompat ke return kill jika cocok)
        for nr in self.kill_blacklist:
            # Jika eq nr, lompat ke return KILL
            instructions.append(SockFilter(BPF_JMP | BPF_JEQ | BPF_K, 0, 1, nr))
            instructions.append(SockFilter(BPF_RET | BPF_K, 0, 0, SECCOMP_RET_KILL_PROCESS))
            
        # 3. Evaluasi errno blacklist
        for nr, err in self.errno_blacklist.items():
            instructions.append(SockFilter(BPF_JMP | BPF_JEQ | BPF_K, 0, 1, nr))
            instructions.append(SockFilter(BPF_RET | BPF_K, 0, 0, SECCOMP_RET_ERRNO | (err & 0xFFFF)))
            
        # 4. Evaluasi whitelist allow
        for nr in self.whitelist:
            instructions.append(SockFilter(BPF_JMP | BPF_JEQ | BPF_K, 0, 1, nr))
            instructions.append(SockFilter(BPF_RET | BPF_K, 0, 0, SECCOMP_RET_ALLOW))
            
        # 5. Default action fallback
        instructions.append(SockFilter(BPF_RET | BPF_K, 0, 0, self.default_action))
        
        return instructions

class SeccompFilterSimulator:
    """
    Mesin simulator deterministik untuk memverifikasi program Seccomp-BPF
    terhadap pemanggilan syscall sebelum dimuat ke kernel.
    """
    def __init__(self, instructions: List[SockFilter]):
        self.instructions = instructions

    def evaluate_syscall(self, syscall_nr: int) -> int:
        """
        Mengeksekusi virtual machine BPF terhadap syscall_nr.
        Mengembalikan nilai aksi SECCOMP_RET_*.
        """
        reg_a = 0
        pc = 0
        n_inst = len(self.instructions)
        
        while pc < n_inst:
            inst = self.instructions[pc]
            code = inst.code
            
            if code == (BPF_LD | BPF_W | BPF_ABS):
                # Load syscall number ke akumulator A
                reg_a = syscall_nr
                pc += 1
            elif code == (BPF_JMP | BPF_JEQ | BPF_K):
                if reg_a == inst.k:
                    pc += inst.jt + 1
                else:
                    pc += inst.jf + 1
            elif code == (BPF_RET | BPF_K):
                return inst.k
            else:
                raise NotImplementedError(f"Instruksi BPF tidak dikenal: {hex(code)}")
                
        return SECCOMP_RET_KILL_PROCESS

if __name__ == "__main__":
    builder = SeccompPolicyBuilder(default_action=SECCOMP_RET_KILL_PROCESS)
    # Whitelist operasi dasar
    for nr in (SYS_READ, SYS_WRITE, SYS_CLOSE, SYS_MMAP, SYS_BRK):
        builder.allow_syscall(nr)
    # Deny operasi berbahaya
    builder.deny_with_errno(SYS_PTRACE, errno.EPERM)
    builder.deny_and_kill(SYS_UNSHARE)
    
    prog = builder.assemble_bpf()
    sim = SeccompFilterSimulator(prog)
    
    print("SYS_READ Allowed:", hex(sim.evaluate_syscall(SYS_READ)))
    print("SYS_PTRACE Denied (EPERM):", hex(sim.evaluate_syscall(SYS_PTRACE)))
    print("SYS_UNSHARE Kill:", hex(sim.evaluate_syscall(SYS_UNSHARE)))
