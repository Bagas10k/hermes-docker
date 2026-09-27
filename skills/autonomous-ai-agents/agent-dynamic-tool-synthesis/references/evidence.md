# Evidence, mechanism, and limits — EVO-003

Author: Bagas Cihuy & Hermes Agent. Retrieved 2026-09-24 WIB; actual initial clock: `2026-09-24T10:13:00+07:00`. Primary pages were read through agent-reach's documented Jina reader route (`curl https://r.jina.ai/<URL>`). `agent-reach check-update` was unavailable (command not found); the reader route worked. No benchmark claims below are local measurements unless explicitly marked.

## Primary sources and what they establish

1. **Cai et al., Large Language Models as Tool Makers (LATM)**, arXiv:2305.17126, v2 submitted 2024-03-11. https://arxiv.org/abs/2305.17126 . Retrieved abstract: separates a powerful tool maker from a lighter tool user; caches reusable functionality and amortizes making cost. Supports the architecture motivation, NOT host isolation or correctness of every generated tool. We retrieved the abstract, not a full-paper experimental replication.
2. **Wang et al., Voyager**, arXiv:2305.16291, v2 submitted 2023-10-19. https://arxiv.org/abs/2305.16291 . Retrieved abstract describes executable skill libraries, environment feedback, execution errors, self-verification and iterative program improvement. It does NOT establish one-shot reliability or general sandbox integrity. Minecraft results do not transfer directly to business tools.
3. **MCP Tools specification, pinned 2025-06-18**. https://modelcontextprotocol.io/specification/2025-06-18/server/tools . Defines discovery/call/list-change behavior, input/output schemas, server input validation/access controls/rate limiting/output sanitization and client timeout/confirmation/audit guidance. Dynamic discovery is not permission to execute newly generated host code. This helper implements no MCP transport and claims no newer version support.
4. **Wasmtime official Security**. https://docs.wasmtime.dev/security.html . All outside interaction goes through linked imports; linear-memory bounds and control-flow checks are runtime mechanisms, with acknowledged defense-in-depth tradeoffs and ongoing side-channel work. Supports a possible future deny-import WASM architecture, not a claim that this Python process is isolated. No Wasmtime runtime was installed or exercised here.
5. **Python official `ast` documentation**, https://docs.python.org/3/library/ast.html#ast.literal_eval . Explicitly warns that even `literal_eval` may exhaust memory/C stack/CPU; `ast.parse` may crash on sufficiently complex input. Motivates small byte/depth budgets and avoiding arbitrary Python syntax, not a proof that a custom parser is formally secure. Retrieved page was the current 3.14 documentation; the actual helper uses no AST API and ran on Python 3.11.16.

## Threat model and admission architecture

Untrusted material: manifest bytes and invocation argument bytes. Trusted: Python interpreter, this implementation, host application, owner authentication, clock and library imports. The model may propose data; it cannot select Python classes, imports, paths, native symbols or executable function bodies.

Pipeline: requirement → proposed DSL manifest → independent business fixtures → strict decoding → allowlisted RPN instructions → immutable tuple + SHA-256 content/policy digest → owner-bound in-memory capability → bounded interpretation → revoke/expiry/close.

Compilation here means lowering a tiny declarative language to instruction tuples; it is not Python bytecode, JIT, native plugin compilation, or a demonstrated autonomous generator. Manually authored fixtures exercise admission, not the probability that an LLM synthesizes a correct program zero-shot.

`admit` accepts only raw bytes. No returned Tool object can be re-admitted through a bypass. `evaluate` is a lower-level trusted function: callers must provide compiler output, not hand-built Tool objects. A hostile Python caller could modify module internals; this is explicitly outside the boundary. Handle ownership is not authentication: the host must supply owner from verified identity, never from model-selected JSON.

Limits: 4096 bytes per JSON message, JSON nesting at most 4, 1–8 declared inputs, 64 instructions, stack at most 16, exact integers with absolute value ≤10^12 at inputs/constants/every intermediate result, 32 live entries, TTL in (0,300] seconds, 1–100 attempts per handle. `bool`, floats, NaN, duplicate JSON keys, extra fields, unknown variables/opcodes and non-single-result programs reject. Multiplication operates on bounded operands before checking its bounded result. Negative integer division uses Python floor semantics. Registry calls serialize through a lock: this prevents local concurrent quota overspend, not a distributed race solution.

Expiry uses trusted monotonic time and rejects at `now >= deadline`. Purging is lazy on registry operations. Running interpretation is not interrupted by TTL; the accepted program has finite instruction count. Authorized failed attempts consume quota; wrong-owner attempts do not. Revocation/close drop references, not secure memory erasure. There is no wall-clock hard deadline, process memory quota, global rate limit, network service, persistent store, signing, or OS sandbox.

## Mechanistic equations

Let m be instructions, d maximum stack depth, b the bit width of permitted integers. Evaluation work is O(m * C_arith(b)); interpreter working stack is O(d*b). These are algorithmic bounds, not measured RSS or hard CPU deadlines. The decoder first caps bytes and nesting; total process memory still depends on Python and the trusted host's request concurrency.

For repeated tasks, `C_dynamic(n) = C_make + C_validate + n*(C_dispatch + C_exec)`; reuse beats the old path only if `n > (C_make+C_validate)/(C_old-C_dispatch-C_exec)` with a positive denominator. TTL may prevent reaching break-even. Admission retries increase setup cost; counting only successful tools biases the estimate.

Amdahl with normalized overhead: `S = 1 / ((1-p) + p/s + h)`. Hypothetical p=0.6, s=4, h=0.05 yields S≈1.667 (computed with Python). This is an illustration, NOT measured speedup. Runtime acceleration cannot remove synthesis, review, context, RPC and human approval costs in the serial fraction.

Capability usability: `usable = owner_match AND present AND now<deadline AND remaining>0 AND registry_open`. Model confidence is not a term in this predicate.

## Bayesian evidence ledger

Posterior odds satisfy `O(H|E)=O(H)*P(E|H)/P(E|not H)`. No numerical prior or likelihood is calibrated here, so no invented security probability is reported.

- **Known (local, finite evidence):** 15 unittest methods pass; hostile Python-shaped strings are rejected as tokens without executing them; 220 pricing-grid fixtures match an independent arithmetic expression; a 40-call threaded trial permits exactly a quota of 7; expiry, revocation, close, capacity and schema negatives pass. These are reproducible observations, not universal proofs.
- **Known (source-reported):** LATM motivates cost amortization; Voyager uses iterative feedback; MCP schemas and Wasmtime import boundaries have the specified roles above.
- **Likely (reasoned):** a small no-I/O DSL has a smaller execution attack surface than arbitrary Python, and reuse can reduce cost at sufficient repetition. Confirm with workload-specific measurements and independent review.
- **Uncertain:** zero-shot synthesis success rate, adversarial generalization, formal interpreter correctness, production latency, process resource exhaustion under load, sandbox escape resistance, and integration with actual MCP/Hermes tool lifecycle. Tests here do not measure them.

Correlated unit cases should not be counted as independent likelihood multipliers. A failure can strongly falsify an invariant; many passes only cover the sampled state space.

## Pareto tradeoffs and proposed production work

| Choice | Benefit | Cost / boundary |
|---|---|---|
| Restricted pure integer DSL (executed) | Inspectable finite work, no candidate I/O primitives | No arbitrary libraries, strings, external APIs or floating point |
| Short TTL and small quota (executed) | Less stale authority, easy task-local revocation | Less cache reuse, more synthesis/admission cost |
| Serialized registry lock (executed) | Simple exact quota behavior | Reduced throughput; not multi-process/distributed |
| Denied-import WASM worker (proposal) | More expressivity with an actual runtime boundary | Runtime audit, import review, memory/fuel/deadline enforcement and side-channel concerns |
| External microVM (proposal) | Stronger process/kernel separation options | Startup/memory/operations overhead; still needs I/O policy and host-side validation |

Before arbitrary-code production: separate compiler worker from execution worker; pin image/runtime/toolchain; verify digest/signature and policy version; deny filesystem/network/environment imports by default; enforce memory/fuel and external kill deadline; authenticate owner; use task-scoped lease and registry fencing; validate outputs; log metadata without secrets; independently attempt resource exhaustion and escape tests in disposable infrastructure. None of these production controls were demonstrated in this cycle. Never replace an isolation failure with host execution.

## Executed verification

Linux x86_64, kernel 5.15.0-119-generic, glibc 2.35; Python 3.11.16. Cross-platform stdlib audit supports the declared platforms, but only Linux was run.

`python3 -B scripts/test_admission.py -v` from the skill directory returned `Ran 15 tests ... OK` (0.053s on the recorded run; duration is not a performance benchmark). Compiler missing-feature test failed then passed; registry lifetime missing-feature test failed then passed. The additional negative/regression matrix was added after those implementations; do not claim every test had an observed red phase.

No arbitrary untrusted Python, sandbox escape probe, compiler worker, model generation call, network tool invocation or production plugin was executed. Candidate code-looking strings in tests remain inert input data.
