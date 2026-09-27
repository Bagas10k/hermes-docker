# Evidence and architecture boundaries

## Retrieved primary sources
Retrieved 2026-09-24 WIB; publication dates below are not claims of a newest release.

1. Scalas & Yoshida, POPL 2019, **Less Is More: Multiparty Session Types Revisited**, DOI 10.1145/3290343. https://mrg.cs.ox.ac.uk/publications/less-is-more-multiparty-session-types-revisited/ — author-hosted abstract describes flaws in older subject-reduction proofs, behavioural type-level properties and model checking. Do not infer that all projection is unsound.
2. Yoshida & Hou, **Less is More Revisit: Association with Global Multiparty Session Types**, https://arxiv.org/html/2402.16741v2 — association relation repairs the proof route involving endpoint projection and mergeability. The fetched HTML was partial; only the abstract/introduction were inspected.
3. Barwell, Hou, Yoshida & Zhou, **Crash-Stop Failures in Asynchronous Multiparty Session Types**, https://arxiv.org/abs/2311.11851 (v6, 17 April 2025), LMCS 21(2:5), DOI 10.46298/lmcs-21(2:5)2025 — crash handling and optional reliable-participant assumptions are explicit parts of its guarantees. Abstract inspected; full proof not reproduced.
4. Same authors, **Designing Asynchronous Multiparty Protocols with Crash-Stop Failures**, https://arxiv.org/abs/2305.06238 (v2, 15 May 2023) — Teatrino extends Scribble and generates Scala using Effpi. Toolchain reported by paper; not installed, benchmarked, or production-validated here.

Exa/mcporter and agent-reach CLIs were unavailable; research used web_search/web_extract fallback. Scribble homepage fetch failed and was not used as evidence. No independently verified industry throughput benchmark was available; do not invent one.

## Mechanistic model
A configuration is C=(local states, per-channel FIFO queues). A send changes one role state and appends a label if the queue is below capacity; a receive changes one role state only if the head label matches. Successful termination requires all roles terminal AND all queues empty. A reachable nonterminal configuration with no enabled transition is a stuck-state witness.

For roles with state counts n_i, c directed channels, label alphabet size a and queue bound b, a crude state-space ceiling is product(n_i) * (sum_{k=0..b} a^k)^c. This is a finite abstraction bound, not a prediction of actual reachable states. BFS stores configurations and parent pointers; memory grows with reachable states, so max_states returns INCONCLUSIVE rather than success.

The helper does not project global types or validate MPST mergeability. Its labels abstract payloads; payload validation, cryptographic identity, timeouts and durable idempotency are separate layers. A loop with enabled actions can satisfy no-stuck-state while never terminating.

Amdahl speedup S=1/((1-p)+p/s) requires measured p. Runtime monitoring adds cost: T_new=T_old+T_monitor-T_avoided_recovery. Without measured avoided failures, claim an assurance improvement, not a latency improvement.

## Projection and branch knowledge
For A choosing yes/no to B, C cannot choose the correct continuation unless both branch projections merge or C receives a distinguishing label. A safe finite fixture explicitly makes B notify C on both outcomes. A negative fixture lets B terminate silently on no, leaving C blocked. This is a counterexample to the protocol fixture, not a general projection theorem.

## Bayesian experiment contract
Prior qualitative hypothesis: explicit branch notification eliminates the particular uninformed-role stuck state. Intervention: add only the missing B->C no notification and corresponding C receive. Predicted observation: stuck before, no stuck state after exhaustive finite exploration. Confidence becomes Known for the tested model; general deployment remains Uncertain. No numerical posterior is justified without a likelihood model.

Negative controls: mismatched label, circular receive, orphan message, queue capacity exhaustion, and exploration cutoff. Positive controls: handshake and explicit branch notification. No-stuck looping fixture tests that the report does not imply liveness.

## Architecture alternatives
- Runtime FSM: smallest integration cost, catches observed protocol deviations; cannot prove unvisited paths or prevent Byzantine semantic lies.
- Bounded FIFO exploration: generates actionable counterexamples and exposes capacity assumptions; susceptible to state explosion and abstraction gaps.
- MPST compiler/type checker: stronger communication guarantees when toolchain and implementation satisfy its exact calculus assumptions; requires protocol discipline and proof provenance.
- Crash-aware MPST/Teatrino: models crash-stop handling; does not automatically cover partitions, malicious agents, arbitrary recovery or perfect failure detection.

Optimize assurance and operational cost under hard constraints: authorized effects only, no silent message loss, bounded resources, explicit uncertainty. Prefer offline verification plus narrow runtime checks over serializing every unrelated message into one global sequence.

## Claim hygiene
A JSON schema is a payload contract, not an MPST proof. A signature authenticates a key, not the truth of content. Deadlock-freedom does not mean every remote endpoint stays available. A successful bounded test must retain the bound and must not be promoted to unbounded liveness. Prior vault claims of universal speedups, absolute safety and numeric posterior confidence lacked demonstrated evidence; treat them as disputed, not inherited facts.
