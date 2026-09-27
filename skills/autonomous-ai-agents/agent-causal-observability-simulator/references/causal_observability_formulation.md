# Mathematical & Causal Formalization of Latency and Resource Simulator

Dokumen ini menyajikan landasan teoretis Structural Causal Model (SCM), Pearl do-calculus, dan formulasi optimasi terkendala untuk observabilitas dan simulasi intervensi alur kerja agen otonom.

---

## 1. Structural Causal Model (SCM) untuk Pipeline Agen

Pipeline agen otonom dimodelkan sebagai Directed Acyclic Graph (DAG) terbobot:
$$\mathcal{G} = (\mathcal{V}, \mathcal{E})$$

Di mana:
- $\mathcal{V} = \{v_1, v_2, \dots, v_n\}$ adalah kumpulan node eksekusi (Trigger, Planner, Subagents, Tools, Evaluator).
- $\mathcal{E} \subseteq \mathcal{V} \times \mathcal{V}$ adalah sisi ketergantungan kausal. Jika $(u, v) \in \mathcal{E}$, maka output state atau kontrol dari $u$ wajib selesai sebelum $v$ dapat dieksekusi.

Setiap node $v_i$ memiliki variabel keadaan multi-dimensi:
$$X_i = (L_i, M_i, C_i)$$
- $L_i \in \mathbb{R}^+$: Latensi eksekusi (ms)
- $M_i \in \mathbb{R}^+$: Konsumsi memori RAM (MB)
- $C_i \in \mathbb{R}^+$: Biaya komputasi / token API (USD)

Relasi struktural kausal didefinisikan sebagai:
$$L_i = f_i(\mathbf{Pa}(v_i), U_i)$$
di mana $\mathbf{Pa}(v_i)$ adalah himpunan parent langsung dari $v_i$, dan $U_i$ adalah variabel noise latar belakang.

---

## 2. Kalkulasi Jalur Kritis (Critical Path Method - CPM)

Untuk setiap node $v_i$ yang diurutkan secara topologis:

### Earliest Start Time ($ES$):
$$ES(v_i) = \begin{cases} 
0, & \text{jika } \mathbf{Pa}(v_i) = \emptyset \\
\max_{p \in \mathbf{Pa}(v_i)} EF(p), & \text{jika } \mathbf{Pa}(v_i) \neq \emptyset
\end{cases}$$

### Earliest Finish Time ($EF$):
$$EF(v_i) = ES(v_i) + L_i$$

Total latensi end-to-end dari pipeline adalah:
$$L_{\text{total}} = \max_{v_i \in \mathcal{V}} EF(v_i)$$

Jalur Kritis ($\mathcal{CP}$) adalah rantai berurutan dari node sumber ke node target yang menentukan nilai $L_{\text{total}}$:
$$\mathcal{CP} = \langle v_{(1)}, v_{(2)}, \dots, v_{(k)} \rangle \quad \text{di mana } ES(v_{(j+1)}) = EF(v_{(j)})$$

---

## 3. Pearl Do-Calculus & Graph Surgery

Observasi empiris pasif merefleksikan distribusi kondisional $P(Y \mid X = x)$. Dalam sistem terdistribusi, korelasi antara pemanggilan tool $X$ dan lonjakan latensi $Y$ dapat dipengaruhi oleh pembaur tersembunyi (confounder $Z$, seperti CPU throttling atau I/O wait).

Intervensi eksplisit dimodelkan dengan operator do-calculus Pearl:
$$P(Y \mid do(X = x))$$

### Operasi Graph Surgery:
1. Putus seluruh panah masuk ke node target:
   $$\mathbf{Pa}_{\mathcal{G}_{\overline{X}}}(X) = \emptyset$$
2. Tetapkan nilai variabel secara deterministik:
   $$X = x^*$$
3. Evaluasi propagasi counterfactual ke seluruh node downstream (causal descendants):
   $$\mathbf{Desc}(X) = \{v \in \mathcal{V} \mid X \rightsquigarrow v\}$$

---

## 4. Batas Kecepatan Amdahl (Amdahl's Law Speedup Bounds)

Fraksi kontribusi suatu node $v_i$ terhadap total jalur kritis adalah:
$$p_i = \frac{L_i}{L_{\text{total}}}$$

Batas teoretis percepatan sistem jika $v_i$ dioptimasi sebesar faktor $s \ge 1$ (misal melalui caching, compile-time dispatch, atau parallelization):
$$S_{\text{latency}} = \frac{1}{(1 - p_i) + \frac{p_i}{s}}$$

### Invarian Amdahl:
Jika $p_i < 0.20$ (kontribusi node kurang dari 20%), maka meskipun komponen tersebut dipercepat tak terhingga ($s \to \infty$), percepatan sistem maksimum tidak akan pernah melampaui:
$$\lim_{s \to \infty} S_{\text{latency}} = \frac{1}{1 - 0.20} = 1.25\times$$

**Rekomendasi Rekayasa:** Selalu alokasikan intervensi optimasi pada node dengan $p_i \ge 0.35$ yang berada tepat di jalur kritis $\mathcal{CP}$.

---

## 5. Optimasi Terkendala Keras (Constrained System Optimization)

Formulasi pemilihan intervensi terbaik:
$$\min_{\mathbf{a} \in \mathcal{A}} J(\mathbf{a}) = \alpha L_{\text{total}}(\mathbf{a}) + \beta C_{\text{total}}(\mathbf{a})$$
terhadap kendala keras $g_j(\mathbf{a}) \le 0$:
1. $M_{\text{peak}}(\mathbf{a}) - 9000 \le 0$ (Batas keras RAM server VPS 9.0 GB)
2. $L_{\text{total}}(\mathbf{a}) - L_{\text{ceiling}} \le 0$ (Batas SLA latensi)
3. $\text{ErrorRate}(\mathbf{a}) = 0$ (Invarian kebenaran logika)
