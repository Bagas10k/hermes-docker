# Edge SLM Tool-Calling Architecture & Technical Reference

## 1. Mekanistik & Batasan Matematis (Mechanism & Bounds)

Pada Small Language Models (SLMs) berukuran parameter 1.5B–3B yang beroperasi pada lingkungan terbatas (CPU edge, RAM <2GB):
1. **Representational Bottleneck**: Model kecil memiliki lapisan atensi lebih dangkal ($L \le 28$, $d_{\text{model}} \le 2048$), sehingga kemampuan melacak ketergantungan sintaksis format panjang (JSON bertingkat) menurun secara drastis saat context window melebihi 2.048 token.
2. **Grammar-Based Constrained Decoding (GBNF)**:
   Daripada mengandalkan prompting pasif (*prompt-and-pray*), sampler mesin inferensi (seperti `llama.cpp`) menerapkan filter logit biner deterministik sebelum penarikan token softmax:
   $$M_t(v) = \begin{cases} 0 & \text{jika token } v \in \mathcal{V} \text{ sah menurut automata GBNF} \\ -\infty & \text{jika melanggar grammar} \end{cases}$$
   $$P(x_t = v \mid x_{<t}) = \frac{\exp(z_t(v) + M_t(v))}{\sum_{u \in \mathcal{V}} \exp(z_t(u) + M_t(u))}$$
   Hal ini menjamin 100% kepatuhan struktur sintaksis tanpa token halusinasi tanda kurung atau pemisah koma ganda.

## 2. Bayesian & Evidence Calibration

- **Prior Risk of Hallucination**: Model 1.5B tanpa grammar memiliki tingkat kegagalan parsing JSON mentah berkisar 28%–42% pada multi-parameter tools.
- **Empirical Evidence**: Penerapan grammar GBNF memangkas invalid syntax rate menjadi 0.0%, namun tetap memiliki risiko semantic divergence (misalnya memilih nama tool di luar domain atau mengisi nilai integer di luar jangkauan valid).
- **Two-Tier Validation Gate**:
  - Tier 1 (Syntactic): GBNF grammar level di sampler.
  - Tier 2 (Semantic & Schema Invariants): Validasi Pydantic / JSON-Schema fail-closed sebelum mencapai sink eksekusi sistem.

## 3. Desain Sistem & Trade-Offs

- **Context Window Conservation**: Membatasi deklarasi alat aktif hanya 2–4 tools per giliran (menggunakan dynamic tooling MCP / intent routing) menghemat ~1.200 token dan menjaga TTFT (Time To First Token) pada CPU quad-core di bawah 350ms.
- **Fail-Closed Execution**: Jika validator Tier-2 menemukan pelanggaran batas aman (misalnya path traversal, unwhitelisted tool name), eksekusi digagalkan seketika dengan kode error deterministik, bukan ditebak secara permisif.
