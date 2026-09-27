# Arsitektur Matematika Counterfactual Regret Minimization (CFR)

## 1. Landasan Teori CFR pada Autonomous Agent
Dalam sistem multi-agen dan eksekusi sekuensial, setiap simpul keputusan direpresentasikan sebagai information set $I \in \mathcal{I}$.

Bila pada langkah $t$, agen memilih aksi $a \in A(I)$ di bawah strategi $\sigma^t$, utilitas faktual yang diperoleh adalah:
$$u(I, \sigma^t)$$

Utilitas kontrafaktual (*counterfactual utility*) jika agen memilih aksi $a$ secara deterministik adalah:
$$u(I, a, \sigma^t_{-i})$$

Regret sesaat (*instantaneous regret*) didefinisikan sebagai selisih:
$$R^t(I, a) = u(I, a, \sigma^t_{-i}) - u(I, \sigma^t)$$

Regret kumulatif (*cumulative regret*) hingga putaran $T$:
$$R^T(I, a) = \sum_{t=1}^T R^t(I, a)$$

## 2. Algoritma Regret-Matching
Pemilihan aksi pada putaran $T+1$ dihitung dengan memotong regret negatif:
$$R^{T,+}(I, a) = \max(0, R^T(I, a))$$

Strategi baru $\sigma^{T+1}(I, a)$ dihitung secara proporsional:
$$\sigma^{T+1}(I, a) = \begin{cases} 
\frac{R^{T,+}(I, a)}{\sum_{b \in A(I)} R^{T,+}(I, b)} & \text{jika } \sum_b R^{T,+}(I, b) > 0 \\
\frac{1}{|A(I)|} & \text{lainnya (kebijakan seragam)}
\end{cases}$$

Teorema Blackwell menjamin bahwa ketika $\frac{1}{T} \sum_{a} R^{T,+}(I, a) \to 0$, kebijakan rata-rata agen konvergen ke Nash Equilibrium atau Pareto optimal subset.

## 3. Invariant State Backtracking Bounds
Setiap mutasi state sistem $S_{k} \to S_{k+1}$ wajib memenuhi kendala invarian keras:
$$g(S_{k+1}) \le 0$$

Bila $g(S_{k+1}) > 0$ (terjadi pelanggaran batas memori RAM 9.0GB, korupsi data, atau kegagalan fatal), algoritma memicu operasi pemulihan instan:
$$\text{Restore}(S_k) \quad \text{di mana } k = \max \{ j < k+1 \mid g(S_j) \le 0 \}$$
Cabang cacat dipangkas dari riwayat aktif dan ditandai dengan penalti penyesalan counterfactual $R(I, a_{\text{defect}}) \ll 0$.
