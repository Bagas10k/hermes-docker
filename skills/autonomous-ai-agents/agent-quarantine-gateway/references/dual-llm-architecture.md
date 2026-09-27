# Dual-LLM Privilege Separation & In-Flight Quarantine Architecture

## 1. Lensa Mekanistik-Kausal (Mechanism & Bounds)
Dalam sistem agen otonom, fungsi eksekusi alat didefinisikan sebagai:
$$E = f_{	ext{tools}}(Prompt_{	ext{system}}, Context_{	ext{history}}, Data_{	ext{untrusted}})$$

Ketika $Data_{	ext{untrusted}}$ dievaluasi dalam ruang interpretasi semantik yang sama dengan $Prompt_{	ext{system}}$, tidak ada pemisahan kausal antara *instruksi sistem* dan *data pasif*. Akibatnya:
$$P(	ext{Action}=	ext{Exploit} \mid 	ext{Injection} \in Data_{	ext{untrusted}}) > 0$$

Dengan **Pemisahan Dual-LLM**:
1. Reader Agent ($LLM_{	ext{unprivileged}}$): Memiliki fungsi terbatas $Extract: Data_{	ext{untrusted}} 	o Schema_{	ext{facts}}$ dengan set alat $\mathcal{T} = \emptyset$.
2. Executive Agent ($LLM_{	ext{privileged}}$): Mengevaluasi aksi alat $Action = f_{	ext{exec}}(System, Schema_{	ext{facts}})$ dengan set alat $\mathcal{T}_{	ext{tools}}$, tanpa pernah terpapar pada raw token $Data_{	ext{untrusted}}$.
3. Secara kausal, jalur manipulasi instruksi terputus:
$$P(	ext{Exploit} \mid do(	ext{Injection} \in Data_{	ext{untrusted}})) = 0$$

## 2. Lensa Bayesian-Eksperimental (Evidence & Belief Updating)
- **Prior ($P(H_{	ext{attack}})$)**: Input dari web publik atau email memiliki prior probabilitas serangan manipulasi token $pprox 0.05 - 0.15$.
- **Bukti ($E$)**: Kemunculan token override (*ignore previous*, *role change*, shell binary invocation).
- **Likelihood Ratio**: $P(E \mid H_{	ext{attack}}) / P(E \mid H_{	ext{benign}}) > 100$.
- **Pembaruan Keyakinan**: Jika skor ancaman $\ge 0.70$, keyakinan posterior $P(H_{	ext{attack}} \mid E) 	o 0.999$, memicu isolasi *fail-closed* seketika.

## 3. Lensa Desain Sistem & Optimasi (Structure & Trade-offs)
- **Trade-off Latensi vs Keamanan**:
  - Direct Concatenation: Latensi 0ms, Risiko Keamanan 100%.
  - Dual-LLM Full Inference: Latensi +1x LLM call, Biaya token +100%.
  - **Quarantine Gateway Hybrid (Solusi Teroptimasi)**:
    - Fast Regex & Entropy Classifier di runtime Python lokal (< 2ms, zero token).
    - Cryptographic Nonce Enveloping (< 0.1ms).
    - Hanya melakukan Reader LLM Pass jika input berasal dari domain eksternal berisiko tinggi atau dicurigai oleh fast scanner.
