# Invariant-Driven Agent Trajectory Self-Grading Architecture

## 1. Lensa Mekanistik-Kausal (Mechanism & Bounds)
Sistem evaluasi mandiri agen otonom mengeliminasi ketergantungan pada LLM judge yang rentan halusinasi, bias verbositas, dan non-deterministik. Model evaluasi dirumuskan secara eksplisit:

$$y = f(\text{Trajectory}, \text{State Diff}, \text{Hard Invariants}) \in \{0, 1\}$$

Setiap langkah dalam trajektori dievaluasi terhadap himpunan kendala keras (Hard Invariant Gates) $G = \{g_1, g_2, \dots, g_m\}$:
$$g_i(S_{\text{final}}) \le 0 \quad \forall i \in \{1, \dots, m\}$$

Batas kecepatan penyelesaian diatur oleh Hukum Amdahl:
$$S_{\text{latency}} = \frac{1}{(1 - p) + \frac{p}{s}}$$
di mana optimasi trajektori memprioritaskan eliminasi langkah no-op, redundansi `grep`/`cat`, dan token bloat loops sebelum mengecilkan variasi prompt lokal.

## 2. Lensa Bayesian-Eksperimental (Evidence & Belief Updating)
- **Prior vs Likelihood**: Agen tidak mempercayai keberhasilan tugas berdasarkan klaim verbal ("task completed successfully").
- **Audit Diff Nyata**: Keberhasilan hanya diakui jika bukti empiris $E$ (state diff, checksum, exit code = 0, AST syntax check) mengonfirmasi hipotesis $H$.
- **Pembaruan Keyakinan**:
  $$P(H \mid E) = \frac{P(E \mid H) P(H)}{P(E)}$$
  Jika ada satu pelanggaran invarian ($E_{\text{violation}}$), $P(H \mid E) = 0$ secara seketika (Fail-Closed Zero-Tolerance Gate).

## 3. Lensa Desain Sistem & Optimasi Pareto
- **Formulasi Optimasi**:
  $$\max_{\tau \in \mathcal{T}} \text{Score}(\tau) \quad \text{subject to} \quad g_i(S_{\text{final}}) \le 0$$
- **Fungsi Objektif**:
  $$\text{Score}(\tau) = 100 \times \left(1 - 0.4 \times \frac{N_{\text{noop}}}{N_{\text{total}}}\right) \times \frac{1}{1 + \frac{N_{\text{total}}}{20}}$$
  Trajektori dengan mutasi tidak sah di luar direktori target langsung digugurkan (Score = 0.0, Status = REJECTED).
- **Evolusi Trajektori**: Trajektori yang lolos seluruh invarian diperingkatkan berdasarkan efisiensi langkah dan konsumsi token untuk mengkristalisasi rute optimal ke dalam memori prosedural.
