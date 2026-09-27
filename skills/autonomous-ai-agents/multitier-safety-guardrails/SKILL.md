---
name: multitier-safety-guardrails
description: Use when validating layered agent admission gates.
version: 0.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [authorization, safety, admission, sandbox, consent]
    related_skills: [agent-quarantine-gateway, agent-adversarial-red-teaming]
---

# Multitier Safety Guardrails

Build deterministic admission before any privileged dispatcher. This stdlib offline reference never executes an action. Status: **TESTED_OFFLINE_ADMISSION_ONLY** (run verification before relying on local results).

## When to Use
- Review layered authorization, semantic veto, sandbox evidence, and one-use consent contracts.
- Test malformed, stale, replayed, or mutated requests before integrating an executor.
- Do not use this checker as a sandbox, command sanitizer, production identity provider, or prompt-injection detector.

## Prerequisites
Python 3.11+ standard library. Trusted configuration and durable SQLite ledger must be owned by the enforcement service, inaccessible to agents. No credentials or network are needed for tests. Real deployments require authenticated identity, isolated evidence issuers, trusted time, sandbox measurement, and an executor coupled to admission.

## Quick Reference
Run with Hermes `terminal` from this skill directory:
```text
python3 -B -m unittest discover -s scripts -p 'test_*.py' -v
python3 -B scripts/admission.py --help
python3 -B scripts/admission.py --trust trusted.json --ledger consent.sqlite < envelope.json
```
CLI returns JSON and exit 0 for offline admission, 2 for denial. Trust/ledger paths are operator inputs, never model-controlled. No shell commands in a request are accepted. Fixture helpers live in the test module, not a production issuer.

## Procedure
1. Authenticate the caller outside model context. Load exact policy and separate issuer keys from trusted operator storage. Reject missing/unknown fields and invalid types; never coerce `true` into an integer.
2. Snapshot canonical request bytes once. Bind all evidence to SHA-256 of the entire request, including principal, tenant, action, object, payload digest, runtime instance, policy version, deadline, and request ID. Hashing binds bytes, not truth or authority.
3. Enforce deterministic authorization first: fixed action/object allowlist, tenant/principal match, resource budgets, and policy version. Semantic `clear` cannot grant permission. Unknown, timeout, absent, or veto results deny.
4. Authenticate semantic and sandbox records with independent role keys, exact schemas, bounded freshness, and request binding. Require a sandbox profile with network disabled, read-only root, no privileges, resource caps, and matching runtime instance. An authenticated claim is not a live sandbox measurement: production needs a trusted attester measuring the actual instance.
5. Authenticate fresh consent covering this exact request. Atomically consume both consent ID and request ID in SQLite only after every gate passes. Concurrent replay has at most one admission. A crash after consumption burns consent; do not retry blindly or undo consumption.
6. Return only an immutable canonical snapshot for a trusted future dispatcher. There is deliberately no dispatcher here. A production executor must revalidate freshness, policy/revocation and the actual runtime at dispatch; prevent TOCTOU, pin object revisions/digests and binary/config identity, and execute only the admitted snapshot.
7. Record reason codes without raw content or secrets. Treat parse/verification/storage errors as denial; test negative inputs and concurrency before deployment. Keep ledger for at least the full evidence/replay horizon; rollback/deletion invalidates the one-use guarantee.

## Pitfalls
- Regex matching and random delimiter nonces are neither authorization nor isolation. They can assist detection/formatting only; decoded, indirect and novel attacks remain possible.
- `sandbox_verified: true` in a model-provided object proves nothing. This demo verifies HMAC authenticity and expected claims, not OS enforcement or remote hardware attestation.
- Shared-key HMAC requires trusted verifier and issuers. A compromised verifier with keys can forge records. Deploy role-separated services and stronger attestation/key-management mechanisms as appropriate.
- An argv array alone does not stop argument injection. Prefer typed library operations; do not add a generic shell operation to this allowlist.
- SQLite uniqueness provides local durable replay protection only while its trusted ledger is preserved. No multi-host consensus, exactly-once execution, revocation service or crash-recovery execution protocol is provided.
- Input limits reduce parser abuse but are not process CPU/RAM isolation. Filesystem, network, kernel and side-channel safety are outside this checker.

## Verification
Run the full offline suite and CLI tests; verify denial for mutation, wrong signatures, stale evidence, unauthorized targets, unknown semantic states, invalid sandbox claims, duplicate JSON keys, replay and ledger errors. See [research and bounds](references/research.md) for fetched official sources, three mindsets, assumptions and evidence limits. Do not report production security, sandbox enforcement, detector accuracy, or latency from these tests.
