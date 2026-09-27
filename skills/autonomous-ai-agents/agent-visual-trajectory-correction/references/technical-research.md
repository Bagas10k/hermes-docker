# VISION-004 — temporal verification research and contracts

## Scope and evidence labels

Status: **TESTED_OFFLINE_ONLY**. VISION-003 admits geometry before dispatch; this extension checks the temporal trajectory after an action may have been sent. No screenshot detector, browser adapter, network executor or probabilistic classifier is implemented. Distinguish (A) fetched source contracts, (B) proposed engineering rules, and (C) synthetic tests. None establishes live safety or performance.

## A. Authentic fetched sources

Sources were read through agent-reach's documented Jina Reader route, except RFC normative body which was also fetched directly as plain text. Reader metadata dates are not publication dates. No claim of exhaustive/latest literature.

1. Hermes official Skills documentation: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills . Describes user-local skills, scripts/references, `skill_manage`, frontmatter and platform gating. Supports packaging, not correctness of this controller.
2. Playwright official Auto-waiting: https://playwright.dev/docs/actionability . `click` checks unique resolution, visible, stable, receives-events and enabled; timeout produces TimeoutError. Stability means equal bounding box over two animation frames. These are preconditions for input, not proof an order/save completed. Do not convert timeout into proof of non-execution.
3. Playwright official Assertions: https://playwright.dev/docs/test-assertions . Async assertions re-fetch and re-test until a predicate or timeout. This supports bounded observation polling. Retrying a read-only assertion is distinct from retrying a mutating action; do not wrap a publish/pay click inside a retry assertion callback.
4. RFC 9110 §9.2.2: https://www.rfc-editor.org/rfc/rfc9110.html#name-idempotent-methods ; direct body https://www.rfc-editor.org/rfc/rfc9110.txt . Defines idempotence in terms of intended server effect and says clients SHOULD NOT automatically retry non-idempotent requests unless semantics are known idempotent or the original was never applied. This is HTTP scope, not a guarantee about GUI buttons. This helper deliberately uses a stricter rule: no automatic non-idempotent replay at all.
5. Xie et al., OSWorld, arXiv:2404.07972, abstract page https://arxiv.org/abs/2404.07972 (page identifies v2, 2024). The abstract describes real-computer tasks with execution-based evaluation and grounding/operational-knowledge deficiencies. Motivation for checking application state, not validation of our state machine. No benchmark results reproduced.
6. Shinn et al., Reflexion, arXiv:2303.11366, abstract page https://arxiv.org/abs/2303.11366 (page identifies v4, 2023). Feedback reflected into episodic memory can inform later trials without weight updates. This motivates structured error observations; free-text reflection does not authorize replay, establish causality, or replace a verifier. Abstract-level review only, not experimental replication.

## B. Three design mindsets

### Mechanism / first principles / Amdahl

The failure mechanism is an open loop: input acknowledgement is confused with remote effect, then retry amplifies uncertainty. Separate admission, reservation/dispatch, observation, semantic verification, reconciliation and termination. A timeout bounds local waiting, not a remote transaction. Closed-loop correction is selective observation first, not reflexive clicking.

Optimize the measured bottleneck, not merely the Python branch. Total time includes capture, transport, grounding, queueing, application settling and semantic readback. Amdahl's analytical model `S = 1 / ((1-f) + f/s)` limits benefit from accelerating fraction f by s. This is design reasoning; no numerical browser speedup or live stage timings are claimed. Re-read text/structured state before recapturing large screenshots when it is the authoritative evidence needed.

### Bayesian / epistemic discipline

Known: documented tool semantics, deterministic test outcomes under supplied fixtures. Hypothesis: correlated semantic readback plus temporal gates reduces accidental replay versus visual-delta heuristics. Unknown: actual false acceptance, delay distributions, adapter faults, GUI causality, deployment safety. Do not invent confidence values or multiply DOM and visual scores as independent likelihoods. Visual and DOM outputs can share the same stale render or malicious text. Missing/ambiguous evidence remains unknown; an `authoritative` flag is an adapter assertion, not an authenticated proof minted by this helper.

### Design / RAM and bounded work

One active tracker has fixed slots and four bounded identifier strings (each at most 128 characters). It retains scalar counters and latest sequence/capture time, no screenshots or history. Attempts are capped at 8; checks at 1024; sequence at signed-64-bit maximum; times must be finite, nonnegative and at most 1e12. Per-call work and retained state are bounded relative to these caps. Input objects already exist before validation, so these bounds do not prevent an upstream parser from allocating an enormous payload. Bound adapter queues/decoded images separately. No measured RSS claim; the flood test checks retained structure and counters only.

## State and evidence contract

`Tracker(action, context, target, predicate, start=..., idempotent=False, timeout=30, max_age=2, max_attempts=2, max_checks=16)` treats attempt 1 as possibly dispatched. Defaults are engineering policy, not experimentally calibrated GUI thresholds. Use the same trusted monotonic clock for start/capture/now; never compare timestamps from another machine or browser without a calibrated adapter.

`Observation` binds action/context/target/predicate, attempt, global sequence, capture time, outcome, semantic boolean, authority flag, and a diagnostic visual flag. Context is a trusted epoch encompassing app/tab/document/tenant/workflow. A semantic predicate must name a concrete task-specific assertion, such as the persisted receipt with exact action receipt key and target account—not an arbitrary toast saying Success. Adapter must verify intent transition and causality where required; a pre-existing satisfied predicate is not evidence that this attempt executed.

Accepted captures are strictly newer than dispatch reservation and prior accepted capture, no later than now, within max_age, and have a strictly increasing sequence. Same-time captures are rejected conservatively even if a low-resolution clock would make them legitimate. Wrong contexts and attempts do not advance the accepted watermark. Invalid schema terminates conservatively. Every active call, even a discarded observation, consumes a check; the next call after the cap stops without processing. Deadline is absolute across retries and inclusive: now >= deadline stops.

| Evidence / condition | Decision |
|---|---|
| Valid authoritative complete + semantic true | SUCCESS, absorbing |
| Valid authoritative pending, semantic false/unknown | OBSERVE (read only) |
| Missing, stale, wrong correlation, unknown, untrusted or contradictory | RECONCILE (read only) |
| Authoritative absent + false, idempotent, budgets left | RETRY; reserve/consume next attempt now |
| Authoritative absent + false, non-idempotent or exhausted | STOP, absorbing |
| Deadline/check cap/bad clock/schema, possible effect unresolved | STOP_RECONCILE, absorbing |

RETRY advances attempt and observation floor atomically inside the local call. A duplicate call with old evidence cannot obtain a second reservation. No automatic retry is allowed merely because the predicate is false, no screenshot changed, or an input API returned an error. A reservation that the adapter did not dispatch may still exhaust budget: conservative lost liveness is preferred to duplicate effects.

Terminal states are absorbing even if later evidence reports success. This prevents a delayed callback from reviving execution. Preserve late evidence outside this tracker for manual reconciliation; never relabel STOP_RECONCILE as confirmed remote failure. Do not construct a new tracker to bypass the same logical action's budget.

## Adapter obligations and unresolved races

- Authenticate observations, reject page-authored instructions and policy, enforce authorization separately, serialize all step/dispatch operations and persist action+attempt reservations before external dispatch.
- A retry recommendation requires fresh VISION-003 grounding plus authorization and another authoritative state check at the dispatch barrier. The pure helper cannot close a readback-to-click race or guarantee exactly-once delivery.
- App-level idempotency must be scoped to the exact intended resource and effect. A checkbox toggle is not an idempotent set-value operation. A button caption is not a semantics contract.
- Expected navigation must have predeclared correlation mapping; arbitrary context substitution is forbidden. This helper does not implement cross-context migration.
- Crash recovery, restart-safe deadlines, durable receipts and multi-process locks are not implemented. Do not infer no effect from losing in-memory state.
- Bound reconciliation reads/timeouts externally; the helper does not schedule timers. If nobody calls it, no deadline callback fires. Stop remote scheduling at terminal state; remote operations may still finish later.

## C. Synthetic verification and live gate

Run `python3 -B -m unittest discover -s . -p 'test_*.py' -v` using `terminal` from the skill's scripts directory. Tests cover semantic success, equal-capture relabelling, unknown/non-idempotent handling, visual changes, authority, contradictions, identity/attempt mismatch, stale/future/pre-dispatch frames, sequence ordering, retries, deadlines, terminal absorption, malformed numeric/schema/policy values and bounded flood retention.

Development evidence: helper-presence and missing-Tracker checks failed before implementation. The initial expanded suite detected same-capture evidence being relabelled with a higher sequence; strict capture monotonicity fixes that regression. Additional characterization tests were written after the core implementation, so full strict TDD is not claimed.

Before any real use, sandbox-test dropped dispatch ACKs, delayed writes, wrong tabs/tenants, post-navigation identity, crash between journal and dispatch, duplicate callbacks, semantic false positives, and an irreversible-action simulator with an independently counted effect ledger. Measure capture-to-postcondition latency and peak memory independently. This offline suite neither performs these integrations nor licenses production deployment.
