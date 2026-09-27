# Cross-Agent Knowledge Distillation & Ephemeral State Absorption

Mathematical & Mechanistic Reference for Absorbing Ephemeral Multi-Agent Trajectories into Durable Knowledge Vaults.

---

## 1. Lensa Mekanistik-Kausal (Mechanism & Bounds)

### Model Sistem Absorpsi Memori
$$K_{t+1} = \Phi(K_t, \bigcup_{i=1}^M \mathcal{T}_i^{(t)}) - \Delta_{\text{prune}}$$

Di mana:
- $K_t$ adalah state durable knowledge base saat ini.
- $\mathcal{T}_i^{(t)}$ adalah trajectory ephemeral dari worker sub-agent $i \in \{1, \dots, M\}$.
- $\Phi$ adalah operator distilasi (ekstraksi fakta atomik, sanitasi noise, resolusi relasi).
- $\Delta_{\text{prune}}$ adalah pemangkasan noise/artefak temporer.

### Hukum Amdahl & Overhead Distilasi
Proses penggabungan state ephemeral tidak boleh menjadi sekuensial kritis:
$$S_{\text{latency}} = \frac{1}{(1 - p) + \frac{p}{N}}$$

Jika fase distilasi membutuhkan $O(M \cdot L)$ di mana $L$ adalah panjang log trajectory mentah, maka distilasi menjadi bottleneck.
Oleh karena itu, distilasi wajib dilakukan terdistribusi pada sub-agent boundary:
Sub-agent mengekstraksi **kandidat fakta atomik** ($O(1)$ transfer), bukan membuang seluruh log mentah ke meta-agent.

---

## 2. Lensa Bayesian-Eksperimental (Belief Updating)

### Corroboration & Multi-Witness Fusion
Ketika sub-agent $A$ mengamati fakta $E_A$ dengan confidence $c_A$, dan kemudian sub-agent $B$ yang independen mengamati fakta yang sama $E_B$ dengan confidence $c_B$:

$$P(H \mid E_A, E_B) = 1 - (1 - P(H \mid E_A)) \cdot (1 - P(E_B \mid H) \cdot \alpha)$$

Di mana $\alpha$ adalah discounting factor korelasi antar-pekerja (default 0.50 jika menggunakan base LLM yang sama, untuk mencegah false consensus).

### Value of Information (VOI) untuk Storage
Fakta baru hanya disimpan jika:
$$\text{VOI}_{\text{net}} = \mathbb{E}[\Delta \text{Decision Accuracy}] - \text{Storage / Context Token Cost} > 0$$

Fakta bernilai rendah (confidence $< 0.35$ atau detail log eksekusi lokal) dibuang seketika pada filter awal.

---

## 3. Lensa Desain Sistem & Optimasi (Structure & Trade-offs)

### Resolusi Konflik: Stable vs Mutable
- **Stable Invariant**: Fakta arsitektur, spesifikasi OS, konstanta lingkungan (`relation_mode = 'stable'`).
  - *Aturan*: Tabrakan nilai memicu **QUARANTINE**. Dilarang keras menimpa diam-diam.
- **Mutable State**: Status tugas, build artifact version, counter (`relation_mode = 'mutable'`).
  - *Aturan*: Nilai lama diarsipkan ke `history[]`, nilai baru dipromosikan jika $c_{\text{new}} \ge c_{\text{old}}$.

### Zero-Artifact Leakage Invariant
1. Tidak ada kredensial mentah (token, secret, API key, bearer) yang lolos ke durable knowledge.
2. Tidak ada string biner (base64 data URIs) yang menggelembungkan ukuran database.
3. Tidak ada ANSI terminal sequence atau progress spam.
