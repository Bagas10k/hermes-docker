# Mathematical Foundations of Semantic Prompt Compaction

## 1. Information-Theoretic Entropy Modeling

Let a prompt message $M$ be represented as a discrete sequence of characters/tokens $X = (x_1, x_2, \dots, x_N)$ drawn from alphabet $\Sigma$. The empirical probability of symbol $c \in \Sigma$ is:
$$p(c) = \frac{\text{count}(c)}{N}$$

The Shannon entropy $H(X)$ measures the average informational content:
$$H(X) = - \sum_{c \in \Sigma} p(c) \log_2 p(c)$$

A high $H(X)$ denotes high informational novelty and diversity, whereas low $H(X)$ represents repetitive, redundant boilerplate.

## 2. Dynamic Knapsack Token Partitioning

Given a strict context window budget $B_{\text{total}}$ and a locked system prefix $P$ with token length $L(P)$, the remaining dynamic budget is:
$$B_{\text{rem}} = B_{\text{total}} - L(P)$$

The non-prefix partitions (Tools $\mathcal{T}$, Memory $\mathcal{M}$, and Ephemeral History $\mathcal{H}$) are allocated dynamic budgets using weight vector $w = (w_{\mathcal{T}}, w_{\mathcal{M}}, w_{\mathcal{H}})$ subject to:
$$w_{\mathcal{T}} + w_{\mathcal{M}} + w_{\mathcal{H}} = 1.0, \quad w_i \ge 0$$
$$\text{Budget}(i) = \lfloor w_i \cdot B_{\text{rem}} \rfloor$$

## 3. KV-Cache Prefix Invariance Bound

In modern transformer architectures (vLLM, SGLang, TensorRT-LLM), prefix caching reuses computed Key-Value activations across requests sharing identical token prefixes.
Let $\text{Prefix}(M)$ denote the immutable system prompt. The prefix invariant requires:
$$\text{SHA256}(\text{Prefix}(M_{\text{raw}})) \equiv \text{SHA256}(\text{Prefix}(M_{\text{compact}}))$$
Any modification to the prefix breaks the radix attention tree, dropping KV cache hit rate from ~90% to 0%, inducing an attention recomputation latency spike:
$$T_{\text{recompute}} = O(L(P)^2 \cdot d)$$

## 4. Amdahl's Law for TTFT Latency

Let $p$ be the fraction of Time-to-First-Token (TTFT) dedicated to the quadratic prefill attention stage ($p \approx 0.65 - 0.75$), and $s = \frac{L_{\text{raw}}}{L_{\text{compact}}}$ be the compression ratio. The theoretical latency speedup $S$ is bounded by:
$$S = \frac{1}{(1 - p) + \frac{p}{s}}$$
When $s \to \infty$, the maximum speedup asymptotically approaches $\frac{1}{1 - p}$.
