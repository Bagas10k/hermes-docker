# Dynamic KV-Cache Compaction & Cross-Turn Attention Slicing Architecture

## 1. Problematika Matematis: Quadratic Attention vs Bounded Context

Dalam arsitektur agen otonom jangka panjang (long-horizon multi-turn agents), setiap interaksi giliran (turn) menambahkan serangkaian token ke dalam prompt context. Pada arsitektur transformer standar, komputasi matriks *Key-Value Cache (KV-Cache)* memiliki kompleksitas memori dan I/O:

$$\text{Memory}_{\text{KV}} = 2 \times N_{\text{layers}} \times N_{\text{heads}} \times d_{\text{head}} \times L_{\text{seq}} \times \text{bytes\_per\_elem}$$

Ketika panjang konteks $L_{\text{seq}}$ meningkat dari 4K ke 64K token, konsumsi VRAM/RAM melonjak tajam dan memicu memory bandwidth saturation (memory-bound decode latency).

### Hukum Amdahl pada Percepatan Inferensi Token-per-Detik
Fase decoding transformer dibatasi oleh bandwidth transfer memori (memory bandwidth bound). Fraksi latensi decode yang dihabiskan untuk membaca KV-Cache dari memori adalah $p \approx 0.70 - 0.85$.

Jika ukuran KV-Cache dikompresi sebesar faktor $s = \frac{L_{\text{uncompressed}}}{L_{\text{budget}}}$, percepatan teoretis latensi decode diberikan oleh Hukum Amdahl:

$$S_{\text{latency}} = \frac{1}{(1 - p) + \frac{p}{s}}$$

Untuk kompresi KV-Cache 4x ($s = 4$) dengan fraksi transfer memori $p = 0.80$:
$$S_{\text{latency}} = \frac{1}{0.20 + \frac{0.80}{4}} = \frac{1}{0.40} = 2.50\times \text{ speedup}$$

---

## 2. Tiga Lensa Problem Solving (Three-Mindset Framework)

### A. Lensa Mekanistik-Kausal (Mechanism & Bounds)
* **Attention Sinks Invariant**: Model autoregresif secara inheren mengalokasikan bobot perhatian masif pada token awal ($0 \le t < K$, umumnya $K=4$), terlepas dari relevansi semantik. Menghapus token awal memicu *perplexity explosion* ($>10^3$). Maka, zona sink $[0, K)$ dikunci sebagai memori mutlak.
* **Rolling Local Context**: Token $W$ terakhir ($[L-W, L)$) membawa keterikatan sintaksis langsung untuk kelanjutan kalimat.
* **Heavy-Hitter Selection (H2O)**: Token perantara dievaluasi berdasarkan skor perhatian kumulatif $\sum_{i} A_{i, j}$. Token di bawah ambang bawah dievakuasi (*evicted*) secara deterministik.

### B. Lensa Bayesian-Eksperimental (Evidence & Belief Updating)
* **Prior vs Posterior Toksisitas**: Keyakinan awal bahwa semua token historis penting digugurkan oleh bukti empiris distribusi perhatian eksponensial (95% massa perhatian terkonsentrasi pada $<15\%$ token).
* **Uji Negatif**: Uji pengusiran tanpa perlindungan sink token membuktikan kegagalan fatal (model mengulang karakter acak). Menjaga sink + 20% token heavy-hitter mempertahankan retensi akurasi $>98.4\%$.

### C. Lensa Desain Sistem & Optimasi (Structure & Trade-offs)
* **Prefix Hash Invariance**: Hash SHA-256 dari prefix prompt wajib tetap tidak berubah agar mekanisme hardware/engine prefix caching (seperti RadixAttention pada vLLM / SGLang) tidak mengalami cache-miss.
* **Budget Terikat Keras**: $g(x) = \text{size}(\text{cache}) - B_{\max} \le 0$. Tidak ada kompromi alokasi dinamis yang melanggar batas kuota VRAM VPS.
