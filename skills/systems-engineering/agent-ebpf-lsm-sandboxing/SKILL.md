---
name: agent-ebpf-lsm-sandboxing
description: "Use when evaluating BPF-LSM agent admission gates."
version: 0.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [agent-security, ebpf, lsm, admission, sandbox]
    related_skills: [agent-ephemeral-sandboxing]
---

# BPF-LSM Agent Admission Gates

Design fail-closed admission for untrusted agent workers. This skill supplies a read-only prerequisite probe and tested admission model, not a deployed kernel sandbox.

## When to Use
- Evaluating kernel-enforced execution and filesystem policy for agent tools.
- Distinguishing an audit hook from a hook that can deny an operation.
- Do not use to claim that temporary directories or resource limits isolate arbitrary code.

## Prerequisites
- Linux; Python 3 standard library for the probe and tests.
- Real deployment additionally requires an enabled BPF LSM, compatible BTF, libbpf/clang/bpftool, reviewed privileges, and an authorized disposable VM.
- Read [research and deployment contract](references/research.md) before designing a policy.
- Never change boot parameters, attach host-wide programs, or reboot production during research.

## Quick Reference
Run with the `terminal` tool from this skill directory:
- `python3 scripts/admission_probe.py` — read-only host inspection; exit 2 means unavailable or unverified, not a command to enable it.
- `python3 scripts/admission_probe.py --test` — deterministic admission-model regression tests.

## Procedure
1. Define adversary, assets, worker identity, inherited FDs and network requirements. Completion: a concrete allow/deny matrix, including loader compromise and cgroup escape.
2. Probe the active LSM list and BTF availability. Completion: absent or unreadable prerequisites refuse admission; kernel version alone never grants it.
3. Separate `bprm_check_security` and `file_open` authorization from `bprm_committed_creds` notification. Completion: each deny requirement maps to a supported integer-returning hook on the actual target kernel.
4. Use libbpf CO-RE and target-kernel selftests in an authorized disposable VM. Preserve earlier BPF-LSM MAC denial (`if (ret) return ret`). Completion: verifier log, attachment lifetime, target scope, and negative control recorded. Do not confuse MAC return semantics with cgroup BPF-LSM semantics.
5. Keep worker blocked until policy identity, scope, attachment and canary denial are verified by a trusted supervisor. Completion: missing evidence, detach or stale policy prevents new workers; existing workers are stopped by an independent supervisor before losing protection.
6. Combine minimal mounts, dropped capabilities, `no_new_privs`, seccomp and resource quotas; close unneeded inherited FDs. Completion: fork/exec, namespace transitions, FD passing, rename/symlink, network and loader-crash cases covered.
7. Measure identical allowed/denied workloads with and without the policy. Completion: report sample count, p50/p95/p99, errors, map memory and audit drops; no universal sub-microsecond claim.

## Pitfalls
- `bprm_committed_creds` is a void post-commit hook, not an execution veto.
- `file_open` alone is not complete read/write mediation: existing and transferred descriptors require explicit coverage.
- BTF presence does not imply BPF LSM is active. Kernel versions do not prove feature availability.
- An audit event or SIGKILL after an operation is not proof the effect was prevented.
- Worker-controlled cgroups, policy maps or loader FDs defeat the trust boundary.
- Runtime map absence must deny enrolled workers; untracked means neither trusted nor safely sandboxed.
- Losing the link may remove enforcement. Keep attachment lifecycle outside the worker.
- Seccomp does not dereference pathname pointers; user-notification continuation needs a separate race analysis.
- A Linux 5.15 host cannot be assumed to expose newer Landlock network ABIs.
- Python model tests prove control logic only, not kernel enforcement or resistance to kernel exploits.

## Verification
The model suite must reject each missing gate and preserve upstream denial. The live probe must never label a worker admitted: it has not loaded or tested any policy. Full acceptance requires disposable-VM kernel tests and real negative-effect checks. Record blocked integration honestly rather than weakening admission.
