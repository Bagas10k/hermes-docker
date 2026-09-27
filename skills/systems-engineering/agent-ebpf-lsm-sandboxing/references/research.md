# Evidence and deployment contract

## Primary sources inspected
- https://docs.kernel.org/bpf/prog_lsm.html — privileged MAC instrumentation; chained return values; libbpf attachment and link destruction.
- https://raw.githubusercontent.com/torvalds/linux/v5.15/include/linux/lsm_hook_defs.h — target-version declarations: `bprm_committed_creds` returns void; `bprm_check_security` and `file_open` return int.
- https://docs.kernel.org/userspace-api/seccomp_filter.html — syscall-number/scalar filtering, no pointer dereference; seccomp is only one part of confinement.
- https://docs.kernel.org/userspace-api/landlock.html — ABI-dependent filesystem/network rights. Do not apply latest documentation's ABI assumptions to old kernels.
- https://tetragon.io/docs/concepts/enforcement/ — production enforcement architecture; return override versus signals. SIGKILL alone does not ensure a write never happened.

A attempted v5.15 `security/bpf/Kconfig` fetch returned 404; no Kconfig claim rests on it. The inspected `security/Kconfig` did not contain the searched definition. No claim of a complete build-config audit is made.

## Mechanism and bounds
Input is a worker launch request plus trusted policy evidence. Admission requires the conjunction of active BPF LSM, BTF, attachment, verified scope, verified policy and canary denial. This is a logical model, not an attestation protocol. A real supervisor must obtain fresh evidence from trusted kernel/control-plane state and prevent TOCTOU between admission and exec.

Model latency as T = T_model + T_setup + T_tool + n_hook*c_hook + T_audit. Optimization of a fraction p by factor s obeys S = 1/((1-p)+p/s). No p or per-hook latency was measured here. BPF verification constrains programs; it does not provide a universal sub-microsecond bound under scheduler, cache and map contention.

Resource objective: minimize tail latency and memory subject to no unauthorized effect, no worker access to policy mutation, and bounded process resources. Map memory grows with entry count, key/value size and allocator overhead; per-CPU maps additionally scale with CPU count. Kernel-resident never means zero memory.

## Bayesian evidence ledger
- Known from source: post-commit void hook cannot return an execution denial; MAC programs must preserve prior rejection.
- Known from live read-only probe: host kernel 5.15.0-119-generic exposes `lockdown,capability,landlock,yama,apparmor`, not `bpf`; BTF exists; clang and bpftool absent.
- Prediction before model tests: removing any one gate refuses admission; upstream denial survives a later allow.
- Likely design benefit: pre-effect authorization avoids the irreversible-effect window of audit-plus-kill. This does not prove whole-sandbox completeness.
- Uncertain: verifier acceptance, hook coverage, loader crash handling and p95/p99 of a real deployment. These require a disposable compatible VM.
- No numeric security posterior is invented. Missing active BPF LSM is enough to reject local deployment without further privileged probes (positive VOI stop condition).

## Design choices and failure tests
Prefer maintained libbpf CO-RE or a reviewed production policy engine over a custom loader. Compare BPF-LSM's privileged system-wide control with unprivileged Landlock, syscall-focused seccomp, and microVM isolation; none substitutes for all others. Keep loader and maps inaccessible to agent code. Scope using trusted workload identity and controlled cgroups, not PID alone. Enroll before exec; prevent worker migration; define cleanup before cgroup reuse.

Required authorized VM cases: allowed operation; denied open with unchanged file; denied exec with no child effect; inherited/SCM_RIGHTS FDs; rename/symlink traversal; child process inheritance; attempted cgroup migration; policy-map eviction; loader exit and link loss; denied network operation; full audit ring with denial intact. Test identity and helper support on the exact kernel. A missing case keeps deployment CANDIDATE.

Read-only probe exit 2 is expected non-admission, not a broken research run. It deliberately cannot output admitted=true because it never checks attachment or canary denial. Local unit tests use synthetic evidence and establish only model invariants. Do not turn fixture fields into worker-supplied launch authorization.

## Reproduction and benchmark plan
Use an isolated VM, pinned kernel/libbpf/compiler versions, a reviewed policy hash and fixed workloads. Alternate baseline/policy runs; record allowed/denied distributions separately, p50/p95/p99, errors, throughput, CPU and map bytes. Measure startup and steady-state independently. Audit samples may drop without changing deny decisions. Published product capabilities are not measured performance evidence; this research reports no industry performance number or executed eBPF benchmark.
