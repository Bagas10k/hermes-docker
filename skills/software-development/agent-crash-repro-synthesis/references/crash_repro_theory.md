# Deterministic Crash Reproduction Loops & Minimal Repro Synthesis

## 1. Algorithmic Overview: Delta Debugging (ddmin)
Delta Debugging (Zeller, 2002) guarantees finding a 1-minimal test case:
- A test case $c \subseteq C$ is 1-minimal if $c$ reproduces the crash, but removing any single element $e \in c$ fails to reproduce the crash.
- Algorithm complexity: $O(|C|^2)$ worst-case, $O(|C| \log |C|)$ average case.

## 2. Mathematical Formulation
Let $C = \{c_1, c_2, \dots, c_m\}$ be the set of input elements (e.g. lines, AST tokens, HTTP request parameters).
Let $r(c) \in \{\text{PASS}, \text{FAIL}, \text{UNRESOLVED}\}$ be the outcome function.
A minimal reproducer $c^*$ satisfies:
$$r(c^*) = \text{FAIL} \quad \wedge \quad \forall e \in c^*, \; r(c^* \setminus \{e\}) \neq \text{FAIL}$$

### Amdahl Bounds on Debugging Cycles
When debugging complex agent failure loops, let $p$ be the fraction of triage time spent in reproduction, and $s$ be the speedup factor of minimal repro vs full-trace debugging:
$$S = \frac{1}{(1 - p) + \frac{p}{s}}$$
Minimizing repro input size from $10^4$ tokens to $<10$ tokens reduces test execution time per iteration from $12\text{s}$ to $0.05\text{s}$ ($s \approx 240$), driving reproduction speedup close to the theoretical ceiling $1/(1-p)$.

## 3. Crash Signature & Fingerprint Invariance
A crash reproducer must maintain strict fingerprint identity:
$$\text{FP}(E) = \text{Hash}(\text{Type}(E) \parallel \text{Basename}(\text{CulpritFile}) \parallel \text{Line}(E))$$
If a reduced test case raises a different exception $\text{FP}(E') \neq \text{FP}(E)$, the minimization step is rejected to avoid false-positive regressions.

## 4. Flakiness & Non-Deterministic Gate
An automated crash reproducer runs an assertion check over $K$ consecutive runs:
$$P(\text{crash} \mid c) = \frac{1}{K} \sum_{i=1}^K \mathbb{I}[r_i(c) = \text{FAIL}]$$
A reproducer is accepted as deterministic if and only if $P(\text{crash} \mid c) = 1.0$ across $K \ge 5$ runs. If $0 < P(\text{crash} \mid c) < 1.0$, the failure is classified as non-deterministic/flaky and quarantined.
