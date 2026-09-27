# Architecture and evidence: bounded prompt/grammar evolution

Attribution: Bagas Cihuy & Hermes Agent. Evidence classes below distinguish source claims from local verification.

## Primary sources
1. GEPA paper, arXiv:2507.19457v2, revised 2026-02-14: https://arxiv.org/abs/2507.19457 . Describes reflective Genetic-Pareto search over trajectories and combination of complementary candidates. Abstract reports average 6% improvement over GRPO and up to 35x fewer rollouts on its evaluated tasks. These are author-reported results, not universal speedups or locally reproduced measurements.
2. Official DSPy GEPA API: https://dspy.ai/api/optimizers/GEPA/overview/ . Current retrieved signature includes `max_metric_calls`, `reflection_minibatch_size`, `candidate_selection_strategy`, `use_merge`, `num_threads`, and `track_stats`. Version-sensitive API; pin installed versions.
3. Official DSPy optimization guide: https://dspy.ai/getting-started/gepa-optimization/ (legacy https://dspy.ai/learn/optimization/optimizers/ redirects). Training provides reflection cases, validation selects Pareto candidates; omitting validation reuses training. Final test must remain separate.
4. MIPROv2 API and embedded source: https://dspy.ai/api/optimizers/MIPROv2/ . Bootstraps demos, proposes grounded instructions, and jointly searches their combinations using Bayesian optimization. This is not the same mechanism as GEPA reflection.
5. llama.cpp GBNF guide: https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md . GBNF constrains generated syntax, with root/nonterminal/terminal rules. It does not validate truth or application authorization.
6. OpenAI prompt caching: https://platform.openai.com/docs/guides/prompt-caching . Exact prefix matches are necessary; put stable instructions first, dynamic material last. Tools/images must match. Provider conditions and minimum lengths are provider-specific, not universal.

## Mechanistic specification
Represent candidate x=(I,D,G), task instructions I, demonstrations D, grammar representation G. Immutable policy prefix P, evaluator V, model revision M, and tool authorization A are outside the search space.

Output y=f(P,I,D,G,M,input,decoder_state)+sampling_error. Measure quality Q, invariant failures H, p95 latency L, peak RSS R, and total optimization cost C. Maximize Q subject to H=0, L<=Lmax, R<=Rmax, C<=Cmax; do not trade permission failures for average reward.

A bounded GEPA-style outer loop: evaluate parent on a reflection minibatch; collect sanitized verifier feedback; propose an instruction edit; reevaluate on matched examples; retain useful improvements and selection-set complementarity; optionally merge complementary candidates; stop at explicit total cost and metric-call bounds. Keep candidate lineage and rejected candidates. Use official implementation rather than claiming this prose reproduces all algorithm details.

Few-shot alternative: bootstrap demos only from verified training traces. Group splits by source/task before selection; example IDs alone cannot detect paraphrase leakage. Search demos and instructions via MIPROv2 when evidence indicates demonstrations drive errors. A deterministic baseline and random-search baseline help distinguish optimizer value from extra budget.

Grammar optimization should initially optimize equivalent serialization or compilation, not weaken semantic acceptance. GBNF syntax requires actual backend compilation; JSON parsing or a regular expression is not a substitute. Finite positive/negative corpus tests detect known regressions but cannot prove language equivalence. Restrict grammar search to approved transformations; escalate any change to allowed outputs or tool schema.

## Bayesian experimental discipline
Prediction before tests: admission must reject a candidate with better reward but a changed prefix, overlapping splits, missing measurements, grammar failure, invariant violations, or budget excess. These are tested locally using explicitly synthetic fixtures.

For real stochastic quality, record paired per-task outcomes under matched model/configuration; aggregate repeated samples at the task level rather than treating correlated rollouts as independent. Use paired bootstrap confidence intervals for bounded score differences; for binary outcomes inspect discordant pairs. Set margin and confidence method before final test. Report interval and sample size, not invented confidence percentages.

Known: source-documented APIs and exact-prefix cache requirement. Tested locally: fail-closed report admission branches. Likely: immutable prefix reduces avoidable cache invalidation. Uncertain: model-specific improvement, prefix hit rate, grammar decoder overhead, production p95. No live model or grammar backend benchmark is implied by helper tests.

## System design and bounds
Serial controller owns budgets, immutable manifest, and candidate lineage; bounded workers evaluate independent examples; an independent verifier returns machine-readable failures; artifact registry stores finalists; deployment remains a separate authorized operation.

If a fraction p of end-to-end time can be improved by factor s, Amdahl speedup is 1/((1-p)+p/s). Before optimization, measure p across prefill, decode, tools, and queueing. Improving prompt prefill does not accelerate serial tools. Search cost adds a separate term: amortized time per future request = serving_time + optimization_time / future_request_count. Break-even requires saved_time_per_request * future_request_count > optimization_time. No p or speedup is assumed here.

RAM scales with worker count times per-worker state plus shared immutable datasets; stream trace files instead of keeping unbounded transcripts. Bound reflection tokens independently of metric calls, because one metric call can hide multiple model/tool calls. Use request timeouts and a monotonic deadline. Compare warm/cold-cache distributions and p95; cache hash equality is necessary, not sufficient, for hits.

## Live integration recipe (not executed here)
Inspect installed `dspy.GEPA` signature. Define evaluator accepting gold, prediction, trace and predictor context, returning `dspy.Prediction(score=..., feedback=...)`; keep feedback free of secrets. Instantiate with metric, authorized reflection_lm, `auto=None`, explicit `max_metric_calls`, small `num_threads`, and `track_stats=True`; compile a copied student with `trainset` and `valset`. Save candidate to a new artifact; never overwrite deployed prompts. Recheck optional metric parameters such as program_trace against pinned version.

The helper consumes external measurements and precomputed paired lower bounds. It cannot attest that supplied flags or statistics are truthful. Maintain raw signed/hash-addressed evidence, dataset manifests, model metadata, backend compile output, and independent review. Its approval is only `admitted_for_review`, never deployment permission.
