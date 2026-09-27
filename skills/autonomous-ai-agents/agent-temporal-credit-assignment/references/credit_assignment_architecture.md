# Architecture: Temporal Credit Assignment & Counterfactual Trajectory Evaluation

## 1. Mathematical Foundations
In long-horizon multi-step autonomous agent execution, the final outcome $R_{final} \in \{0, 1\}$ provides delayed feedback. Evaluating each intermediate tool action requires solving the **Temporal Credit Assignment Problem**.

### Counterfactual Difference Reward (Difference Rewards)
For an agent trajectory $\tau = (s_0, a_0, s_1, a_1, \dots, s_T, a_T)$:
$$D(a_t) = R(\tau) - R(\tau \setminus \{a_t\})$$
Where $R(\tau \setminus \{a_t\})$ models the counterfactual trajectory without action $a_t$.

### Shapley Value Marginal Contribution
In multi-agent / sub-agent delegation:
$$\phi_i(v) = \sum_{S \subseteq N \setminus \{i\}} \frac{|S|!(|N| - |S| - 1)!}{|N|!} (v(S \cup \{i\}) - v(S))$$
This accurately attributes team success to specific specialist sub-agents, preventing free-rider anomalies where passive sub-agents inherit false positive credit.

### Amdahl Latency Contribution Bounds
$$S_{speedup} = \frac{1}{(1 - p) + \frac{p}{s}}$$
Where $p$ represents the execution fraction contributed by action step $a_t$:
$$p_t = \frac{\text{Duration}(a_t)}{\sum_{k=1}^T \text{Duration}(a_k)}$$
If $p_t \ge 0.25$, step $a_t$ is designated as an architectural critical bottleneck.

## 2. Decision Boundaries & Pruning Policy
1. **Positive Credit ($C(a_t) > 0.2$)**: Crystallize into persistent procedural knowledge / skill memory.
2. **Neutral Step ($0 \le C(a_t) \le 0.2$)**: Necessary context collection; retain in working context without elevation.
3. **Negative Credit ($C(a_t) < -0.1$)**: Token bloat or hallucinated tool loop; prune from handoff trace and inject negative constraint into `conflicts.json` / episodic memory.
