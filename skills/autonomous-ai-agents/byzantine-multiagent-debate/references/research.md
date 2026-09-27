# Evidence, assumptions, and experimental design

## Sources inspected
- Castro & Liskov, Practical Byzantine Fault Tolerance (1999): https://pmg.csail.mit.edu/papers/osdi99.pdf — replicated-state safety is a protocol property, not a semantic truth oracle. Liveness needs eventual favorable timing; authentication and replica fault bounds are assumptions.
- Zheng et al., Rethinking the Reliability of Multi-agent System: A Perspective from Byzantine Fault Tolerance: https://arxiv.org/html/2511.10400 — CP-WBFT uses prompt/hidden confidence probes and weighted information transmission. The paper reports experiments at 85.7% faulty nodes. This is experimental task performance, not removal of classical quorum bounds. Code linked by paper: https://github.com/Z1ivan/Byzantine-Fault-Tolerance-in-LLM-MAS (not executed here).
- Bertalanic & Fortuna, The Cost of Consensus (2026), v1: https://arxiv.org/html/2605.00914v1 — homogeneous N=10, R=3, 7–8B models, GSM-Hard/MMLU-Hard. Authors report 2.1–3.4x token cost relative to isolated correction for equal or lower accuracy. Do not generalize this to all heterogeneous or externally verified architectures. Code linked by paper: https://github.com/sensorlab/llm-debate-dynamics (not executed here).
- Guo et al., On Calibration of Modern Neural Networks (ICML 2017): https://proceedings.mlr.press/v70/guo17a.html — calibration and temperature scaling, evaluated on classification models, not proof that verbal LLM confidence is calibrated.

## Mechanistic bounds
Model output as f(model, prompt, shared evidence, topology, adversary, verifier) + error. Intervening on peer visibility while holding tasks and budgets fixed distinguishes communication effects from mere extra sampling.

Two quorum sets of weight at least q intersect in weight at least 2q-W. An honest signer must be in their intersection only if 2q-W>B, where B bounds Byzantine weight. Availability without Byzantine cooperation requires q<=W-B. Together feasibility requires W>3B. This derivation assumes fixed positive weights, authenticated identities, and honest sign-once per slot; cross-view safety requires additional lock rules. Using q=2f+1 blindly when n exceeds 3f+1 can be unsafe; use the general inequality.

For equal weights and exchangeable errors, variance of the mean error indicator is p(1-p)[1+(n-1)rho]/n. Effective independent sample count n/[1+(n-1)rho] is a variance diagnostic, not a majority-accuracy guarantee. Correlated errors can erase ensemble benefit.

Parallel agents reduce only the parallel fraction: S=1/((1-p)+p/s). Debate adds serial rounds and verification; no numerical speedup is claimed without profiling. All-to-all message growth is O(R*n^2); bounded coordinator collection is O(R*n) messages but concentrates trust and workload. Bound payload bytes as well as message counts.

## Bayesian evidence lens
Known: finite quorum intersection under declared assumptions; calibration arithmetic on supplied labels.
Likely: preserving independent first answers and requiring external evidence reduces conformity risk; task-dependent and not measured here.
Uncertain: improvement on this user's actual agent workload; robustness to adaptive malicious confidence probes.

Do not multiply likelihoods from agents citing the same source. Estimate calibration on held-out tasks, group splits by source/task family to avoid leakage, report confidence intervals across tasks. Verifier outputs must originate outside the untrusted agent payload. A boolean supplied by an agent is not evidence.

ECE = sum_b (|b|/N)*abs(mean confidence_b - mean correctness_b). Brier = mean((p-y)^2). ECE can be zero for a constant uninformative base-rate predictor. Report accuracy, coverage, and selective risk alongside both metrics.

## Predicted tests before execution
- Every pair of size-3 quorums among 4 replicas intersects in more than one replica; size-2 quorums need not.
- Duplicate identities never increase certificate weight; wrong task/epoch/digest invalidates receipts.
- Unanimous unsupported claims still abstain.
- Constant p=0.5 on balanced labels has ECE zero and Brier 0.25, illustrating that calibration is not truth convergence.

## Production architecture recommendation (not deployed)
Keep deterministic admission separate from epistemic ranking: authenticated transport -> fixed-membership receipt validation -> durable equivocation/lock ledger -> independent evidence verifier -> policy/authorization -> commit. Reuse a mature consensus library when distributed state-machine replication is genuinely needed; do not retrofit a research voting helper as PBFT.

Evaluate three matched-budget arms: independent voting, isolated self-correction, one bounded evidence challenge. Include poisoned citations, source duplication, high-confidence wrong agents, equivocation, replay, withheld votes, and network partitions. Measure per-task paired outcomes, wrong-consensus rate, abstention, tokens, RSS, p50/p95; never label fixture results as live model benchmarks.
