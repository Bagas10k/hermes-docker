---
name: seccomp-bpf-sandbox-filter
description: "Use when restricting dangerous Linux syscalls and memory execution in agent tool sandboxes via Seccomp-BPF filters."
category: systems-engineering
version: 1.0.0
---

# Seccomp-BPF Syscall Filter & Memory Quotas

Penerapan filter syscall Linux Seccomp (SECure COMPuting with Berkeley Packet Filter) untuk membatasi ruang serang alat agen eksternal tak terpercaya (*untrusted tools*).

## Kapan Digunakan
- Mengisolasi eksekusi terminal/sub-agen yang mengeksekusi kode pihak ketiga.
- Mencegah *sandbox escape*, pengambilalihan hak akses kernel via `ptrace`, manipulasi namespace via `unshare`, dan modifikasi modul kernel via `init_module`.
- Memberikan sinyal galat elegan (`EPERM` atau `EACCES`) untuk syscall non-esensial alih-alih merusak seluruh runtime agen.

## Arsitektur BPF Filter
1. **Header Verification**: Validasi arsitektur ABI (`AUDIT_ARCH_X86_64`) pada header filter.
2. **Syscall Inspection**: Membaca offset nomor syscall pada struktur kernel `seccomp_data.nr`.
3. **Multi-tier Decision Tree**:
   - `SECCOMP_RET_ALLOW (0x7fff0000)`: Mengizinkan syscall komputasi esensial (`read`, `write`, `close`, `mmap`, `brk`).
   - `SECCOMP_RET_ERRNO (0x00050000 | errno)`: Memblokir pemanggilan berbahaya (`ptrace`, `bpf`) dengan pesan *permission denied*.
   - `SECCOMP_RET_KILL_PROCESS (0x80000000)`: Terminasi instan jika terjadi upaya manipulasi namespace atau eskalasi hak istimewa kernel (`unshare`, `reboot`, `init_module`).

## Validasi Empiris
- Engine: `seccomp_bpf_filter.py`
- Test Suite: `test_seccomp_bpf_filter.py` (5 pengujian deterministik, 100% lulus dalam 0.002s).
