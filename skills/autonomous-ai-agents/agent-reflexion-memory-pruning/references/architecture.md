# Evidence-gated Reflexion architecture

## Source ledger (retrieved 2026-09-24)
- Shinn et al., Reflexion, https://arxiv.org/abs/2303.11366v4 : actor consumes feedback and reflective episodic memory without updating weights. HumanEval numbers are author-reported, not reproduced here. The reader proxy's HTTP publication timestamp is not the paper date; submission history identifies v4 as October 2023.
- Wu et al., LongMemEval, https://arxiv.org/abs/2410.10813v2 : evaluates extraction, multi-session reasoning, temporal reasoning, knowledge updates and abstention; separates indexing, retrieval and reading. Conversational memory results do not automatically transfer to action trajectories.
- Kwan and Chang, LongMemEval-V2, https://arxiv.org/html/2605.12493v1 : web-agent experience evaluated via Insert/Query and a fixed reader context budget. Tests static state, dynamics, workflows, gotchas and premise awareness. Authors report 72.5% average accuracy for AgentRunbook-C but substantial query latency. This is evidence of an accuracy/latency trade-off, not a local benchmark or production endorsement.

## Mechanism and causal boundaries
Let outcome Y = f(task, actor, tools, environment, retrieved_memory) + error. Reflection changes retrieved_memory, not model weights. A useful negative constraint is scoped: on failure condition C, avoid action A, choose B, and test outcome O. Merely observing success after reflection does not establish causality: retries and extra inference also change outcomes.

Separate actor, external evaluator, reflection generator, evidence validator, planner, and authorized snapshot committer. The generator cannot mark its own output verified or protected. Preserve immutable raw evidence separately from a compact active retrieval index. Apply retention/privacy deletion policies independently; 'immutable' is not permission to retain personal data forever.

Amdahl: S = 1 / ((1-p)+p/s). Illustrative only: if memory handling contributes p=.3 and is accelerated s=2, overall speedup is 1.17647, not 2. Local experiments did not measure production p. Report end-to-end p50/p95, memory bytes and recurrence separately from planner time.

## Bayesian calibration and promotion
A Beta(1,1) prior with three independent successes and zero failures yields Beta(4,1), posterior mean .8 and P(theta>.9)=.3439. Therefore the old '3-strike implies >90% confidence' shorthand is invalid. Repeated copies of one trace add no independent trials. Use disjoint task families and explicit outcome oracles; retain failures. Known: fixture invariants pass. Likely: evidence-gated context reduces stale retrieval. Uncertain: improvements in actual agent task success; no live model evaluation performed.

## Selection algorithm and bounds
Input schema is an array of exact records {id,scope,key,value,source,protected,stale,verified}. Boolean metadata must be issued by a trusted upstream validator. source is a provenance locator, not proof it exists. Planner:
1. Reject malformed records, duplicate IDs and invalid protected state.
2. Filter other scopes, stale and unverified records, logging reasons.
3. Group by exact key; quarantine differing active values together. A conflict touching policy blocks the entire plan.
4. Select one lexicographically stable representative per exact duplicate group, retaining every protected record.
5. Serialize id/key/value/source as JSONL; count actual UTF-8 bytes. Block if mandatory records exceed budget.
6. Add optional records in stable ID order while space remains. Produce decisions for all IDs; never modify input.

Runtime O(n log n + text_bytes); RAM O(n + text_bytes). This reference planner is not a streaming million-episode store, a tokenizer, or semantic optimizer. It intentionally uses conservative deterministic ordering rather than uncalibrated utility scores. Production indexing may use SQLite with key (tenant, project, environment_version, fact_key), optimistic snapshot versions, unique episode IDs, transactions and protected-policy manifests. Store large raw traces outside the hot index. Do not infer that the included script implements that database architecture.

## Hard constraints and options
Optimize retrieval cost and error subject to policy retention, scope isolation, provenance, budget and rollback. FIFO is cheap but can drop rare critical failures. Semantic similarity helps find candidates but cannot establish logical contradiction. Greedy utility ignores joint usefulness and requires trustworthy feedback. Exact-key quarantine is conservative and reproducible but can over-abstain and miss paraphrase conflicts. Timestamp recency alone never authorizes supersession.

For approved knowledge updates, create a versioned replacement with validity interval and supersedes edge after evidence review; never let an LLM delete conflicting records. On unresolved conflicts, abstain or escalate once with a notification flag. This planner never commits a memory snapshot.

## Empirical protocol and results
Prediction before execution: duplicate records collapse; conflicts quarantine both sides; protected overflow rejects; identical input gives deterministic output; original files remain byte-identical; malformed CLI input returns nonzero with empty stdout.
Executed `python3 scripts/test_prune.py`: 10 tests passed in 0.259 seconds, including actual subprocess CLI success/failure and input SHA-256 preservation. Tests are synthetic fixtures expressly for safety contracts, not fabricated real trajectories or claims of model quality. No network, production memory writes, LLM calls, or neural training in the suite.

Next evaluation (not yet run): fixed task-family split, fixed actor/tool versions, equal retry/token budgets across no-memory/FIFO/evidence-gated retrieval; paired success differences with bootstrap confidence intervals, failure recurrence, abstention on contradictory histories, privacy leakage tests, and measured p50/p95 end-to-end latency. Pre-register acceptance thresholds with owner before deployment. Stop exploration if additional probes cannot change the deployment decision: without live evaluation this remains a tested planner and candidate learning strategy.
