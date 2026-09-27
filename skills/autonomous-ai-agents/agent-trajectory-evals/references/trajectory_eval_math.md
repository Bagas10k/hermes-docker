# Matematika & Arsitektur Evaluasi Trajektori Agen

## 1. Perumusan Formal Trajektori
Trajektori penalaran agentik dimodelkan sebagai Markov Decision Process (MDP) tereduksi:
$$T = \langle s_0, a_0, r_0, s_1, a_1, r_1, \dots, s_T \rangle$$
Di mana:
- $s_t$: State lingkungan pada giliran $t$ (konteks sistem + riwayat percakapan + environment state).
- $a_t$: Aksi agen (tool call spesifik dan argumen).
- $r_t$: Feedback deterministik dari lingkungan (eksekusi tool stdout/stderr/exit_code).

## 2. Formulasi Unbiased Pass@k
Pada pengujian generasi kode dan penalaran agen (HumanEval / SWE-bench), jika dihasilkan $n$ trajektori independen dan ditemukan $c$ trajektori yang lulus verifikator, estimasi probabilitas bahwa dari $k$ percobaan terdapat minimal satu solusi benar dihitung dengan:
$$\widehat{Pass@k} = 1 - \frac{\binom{n-c}{k}}{\binom{n}{k}} = 1 - \prod_{i=0}^{k-1} \frac{n - c - i}{n - i}$$
Kondisi batas:
- Jika $n - c < k$, maka suku kedua adalah 0, sehingga $\widehat{Pass@k} = 1.0$.
- Jika $c = 0$, maka $\widehat{Pass@k} = 0.0$.

## 3. Lensa 3 Mindset pada Evaluasi Agen
1. **Mekanistik-Kausal**:
   Mendeteksi causal intervention titik balik kegagalan. Apakah error pada langkah $t=5$ merupakan akibat langsung dari output alat pada langkah $t=2$ ($P(Error_{t=5} \mid do(Action_{t=2}))$)?
2. **Bayesian-Eksperimental**:
   Memperbarui keyakinan model terhadap reliabilitas tool. Jika sebuah tool gagal 3 kali berturut-turut pada lingkungan tertentu, prioritaskan fallback deterministik.
3. **Desain Sistem & Trade-offs**:
   Evaluasi rasio compute vs akurasi. Menjalankan verifikasi konsensus 5x menaikkan latensi $5\times$, namun meningkatkan $Pass@k$ dari 65% ke 92%.
