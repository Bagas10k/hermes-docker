---
name: agent-dynamic-tool-synthesis
description: Use when admitting generated ephemeral tools.
version: 0.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [agents, synthesis, admission, ephemeral, security]
    related_skills: [agent-ephemeral-worker, mcp-dynamic-federation]
---

# Dynamic Tool Synthesis: Bounded Admission

Admit generated integer-expression tools into an offline, ephemeral registry. This is a restricted DSL interpreter, not a Python sandbox, native compiler, MCP server, or demonstrated zero-shot generator.

## When to Use
- A model proposes small pure formulas for scores, integer unit conversions, or pricing in minor currency units.
- Generated capabilities need input validation, bounded evaluation, owner scoping, expiry, and revocation.
- Do not use for arbitrary Python, shell, filesystem/network access, secrets, or production isolation.

## Prerequisites
- Python 3.11+ standard library; no network, packages, credentials, or service changes.
- Read [evidence and threat model](references/evidence.md) and [API](references/api.md).
- Trusted host process and callers; only candidate manifests and argument bytes may be untrusted. Owner IDs must come from a trusted authentication layer.

## Quick Reference
Via `terminal`, with workdir set to this skill directory:
- `python3 -B scripts/test_admission.py -v`
- Import `scripts/admission.py` into a trusted application; API usage is in the linked reference.

## Procedure
1. [ ] Define a pure integer formula and independent expected examples; do not authorize side effects based on model claims.
2. [ ] Serialize the exact manifest to bytes. `compile_tool` must reject unsupported keys, duplicate JSON keys, unknown inputs/opcodes, oversized input, and invalid stack shape.
3. [ ] Check business meaning against independent examples. Syntactic admission does not establish correctness, units, or safety of downstream decisions.
4. [ ] Register under an authenticated owner with explicit TTL and call quota. Keep the opaque handle private; verify the returned digest against the intended manifest.
5. [ ] Invoke using exact-key JSON integer arguments. Every invocation validates owner, expiry, quota, values, and intermediate numeric bounds.
6. [ ] Revoke the handle or close the registry at task end. Verify calls fail thereafter. Expiry is checked lazily, not by background cleanup.
7. [ ] For arbitrary-code needs, stop this path. Design and independently verify an external runtime with denied imports, no inherited credentials, CPU/memory limits and termination before considering production use.

## Pitfalls
- No `eval`, `exec`, imports from candidates, subprocesses, or dynamic Python compilation; the DSL compiles only to immutable instruction tuples.
- Python privacy and owner strings are not an OS security boundary. A malicious host caller can tamper with this process.
- TTL does not preempt running work or securely erase memory. Quota is per handle, not global request rate limiting.
- Digest identifies content and policy; it is not a signature or proof of provenance.
- Do not inherit unverified sandbox/zero-leak claims from adjacent skills. Discovery, worker lifecycle, and new-program admission are distinct tasks.
- Platform audit: cross-platform stdlib only; executed verification is Linux/Python 3.11, not macOS or Windows.

## Verification
Run the full offline test command above. Require all cases to pass, including hostile syntax as inert data, numeric bounds, expiry at the exact deadline, ownership, revocation, quota, and concurrency. Test evidence and production-only proposals are separated in the reference; never report this helper as executing arbitrary untrusted plugins.
