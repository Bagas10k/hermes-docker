# Research and Operational Bounds: Multitier Safety Guardrails

Status: **TESTED_OFFLINE_ADMISSION_ONLY**

## Official References and Citations
1. **OWASP Top 10 for Large Language Model Applications (2025)**
   - *LLM01: Prompt Injection* — Highlights that untrusted inputs can manipulate execution flow. System prompt framing is not an isolation boundary or trusted control.
   - *LLM07: System Prompt Leakage & Misplaced Trust* — Recommends strictly decoupling semantic model outputs from policy decision and enforcement points.
2. **NIST SP 800-207: Zero Trust Architecture (August 2020)**
   - Section 2.1 & 3.1: Logical separation of Policy Decision Point (PDP, comprising Policy Engine and Policy Administrator) and Policy Enforcement Point (PEP).
   - Tenet 3 & Tenet 6: Per-session dynamic policy evaluation without implicit trust across internal networks or adjacent components.
3. **OWASP Command Injection Prevention & Safe Execution Guidelines**
   - Principle of strictly typed parameter binding over dynamic shell interpolation. Eliminating shell dispatchers prevents argv/shell injection attacks at the root.

## Architecture and Four-Tier Enforcement
1. **Tier 1: Deterministic Policy Engine (PDP)**
   - Validates caller identity, tenant tenancy, policy version, and explicit action-object allowlists.
   - Evaluates criteria deterministically prior to inspecting downstream evidence.
2. **Tier 2: Semantic Veto (Negative Filter Only)**
   - An LLM guardrail or classifier may issue a `VETO` to abort high-risk operations.
   - **Crucial Invariant:** Semantic `CLEAR` cannot grant permissions or override Tier 1 policy. Unknown or malformed semantic states fail closed.
3. **Tier 3: Sandbox Attestation Claims**
   - Verifies cryptographically signed claims regarding execution isolation (`network_disabled`, `read_only_root`, `no_new_privs`).
   - Bounds claims to exact `runtime_instance_id` and canonical `request_hash`.
4. **Tier 4: One-Use Consent and Durable Ledger**
   - Cryptographically bound consent token consumed atomically with request ID in SQLite WAL.
   - Prevents replay attacks and double-spending across requests.

## Three Mindsets Framework
- **Mechanism / Bounds (Amdahl's Law):**
  Deterministic admission and cryptographic checks are sequential bottlenecks before any parallel execution. Let parallelizable task execution time fraction be $P = 0.95$ and sequential guardrail admission fraction be $S = 0.05$. Maximum speedup theoretically achievable under infinite parallelism is $1 / 0.05 = 20\times$. For offline checks, hashing and SQLite commit take $<2\text{ ms}$, ensuring deterministic admission introduces negligible sequential overhead compared to model inference and external I/O.
- **Bayesian State Transitions:**
  - *Known:* Requests failing schema, hash mismatch, expired timestamps, or replaying tokens are guaranteed invalid ($P(\text{Malicious} \mid \text{Invalid Signature/Replay}) = 1.0$).
  - *Likely:* A request passing deterministic policy, semantic check, and sandbox claims is compliant under the current threat model, provided keys remain uncompromised.
  - *Uncertain:* Zero-day payload vulnerabilities within typed parameters or kernel sandbox escapes cannot be detected by user-space admission checking.
- **Trade-offs:**
  - Strict immutability and fail-closed behavior eliminate silent privilege escalations but cause brittle execution if upstream agents generate subtle schema mismatches.
  - Local SQLite WAL provides robust single-node replay prevention, but distributed clusters require Raft/consensus ledgers to prevent split-brain replay.
