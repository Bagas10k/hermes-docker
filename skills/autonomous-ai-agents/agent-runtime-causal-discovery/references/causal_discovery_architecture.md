# Technical Architecture: Runtime Causal Graph Discovery & Do-Calculus Bounds

## Executive Summary
Autonomous AI agents operating in complex environments frequently fall into correlation-causation fallacies: observing that two variables or events occur together ($P(Y \mid X=x)$) and incorrectly assuming direct manipulability ($P(Y \mid do(X=x))$). In multi-agent DAG execution and tool-calling loops, this manifests as premature stopping, erroneous credit assignment, and cascade failures.

This architecture formalizes **Runtime Causal Graph Discovery** and **Pearl's Do-Calculus Bounds** inside agentic loops, synthesizing findings from CausaLab (Yang et al., 2026), Auto-Bench, and Pearl's Structural Causal Models (SCMs).

---

## 1. Mathematical Formulation

### 1.1 Structural Causal Model (SCM)
A runtime system is modeled as an SCM $M = \langle U, V, F, P(U) \rangle$:
- $U = \{U_1, \dots, U_n\}$: Exogenous background/noise variables.
- $V = \{V_1, \dots, V_m\}$: Endogenous observable system states, tool outcomes, and node metrics.
- $F = \{f_1, \dots, f_m\}$: Structural assignment equations where $V_i = f_i(PA_i, U_i)$, with $PA_i \subseteq V \setminus \{V_i\}$.
- $G$: Directed Acyclic Graph (DAG) induced by parent-child relations $PA_i \to V_i$.

### 1.2 Pearl's Do-Calculus (Hard Intervention)
When an agent actively intervenes on variable $X_k$ setting it to constant $x^*$:
$$do(X_k = x^*)$$
1. **Graph Surgery (Parent Severance):**
   $$PA'_{k} = \emptyset, \quad f'_k(PA'_k, U_k) = x^*$$
   All incoming directed edges $(\cdot \to X_k)$ are severed in the mutilated graph $G_{\overline{X_k}}$.
2. **Downstream Propagation:**
   The distribution of downstream response $Y$ under intervention is:
   $$P(Y \mid do(X_k = x^*)) = \sum_{v \setminus \{y, x_k\}} \prod_{j \neq k} P(V_j \mid PA_j)$$

### 1.3 Soft Shift-Intervention (Laboratory / Elastic Parameter Bounds)
In environments where hard-do is physically or syntactically unavailable (e.g., modifying thread priority or memory allocations without killing upstream pipelines), a shift-intervention is applied:
$$X_k = f_k(PA_k, U_k) + \delta_k$$
Incoming edges are retained while shifting baseline intercept, isolating directional elastic response $\frac{\partial Y}{\partial \delta_k}$.

---

## 2. The 3-Mindset Problem Solving Lens

### 2.1 Mekanistik-Kausal (Mechanism & Bounds)
- **Amdahl Causal Speedup Bound:**
  $$S_{\text{causal}} = \frac{1}{(1 - f_{\text{crit}}) + \frac{f_{\text{crit}}}{s}}$$
  Interventions on non-critical nodes ($f_{\text{crit}} \approx 0$) yield zero causal throughput gain regardless of observed correlation.
- **Topological Invariant:**
  $G$ must remain strictly acyclic ($\text{Cycles}(G) = \emptyset$). Adding edge $u \to v$ is rejected immediately if $v \rightsquigarrow u$ exists in transitive closure.

### 2.2 Bayesian-Eksperimental (Evidence & Belief Updating)
- **Posterior Probability of Mechanism:**
  $$P(M \mid D) = \frac{P(D \mid M) P(M)}{\sum_{M'} P(D \mid M') P(M')}$$
- **Value of Information (VOI) Experiment Selection:**
  $$\text{VOI}_{\text{net}}(do(X)) = \mathbb{E}[\Delta \text{Entropy}(G)] - \text{Cost}(X)$$
  Agents avoid probing nodes where directional ambiguity is already zero or budget cost exceeds informational gain.
- **Consistency Verification Gate:**
  Mitigates premature stopping (the #1 failure mode in CausaLab benchmark) by validating reconstructed SCM against all historical observations and interventions.

### 2.3 Desain Sistem & Optimasi (Structure & Trade-offs)
- **Constraint-First Pruning:**
  Compute Pearson/Spearman correlation matrices across streaming observations; prune edges below $\tau_{\text{corr}} = 0.25$ before allocating expensive active interventions.
- **Zero-Allocation Data Structures:**
  Topological sorts, DAG cycle validation, and equation evaluations operate in $O(|V| + |E|)$ time and sub-millisecond CPU footprints (<2ms for 20 nodes).
