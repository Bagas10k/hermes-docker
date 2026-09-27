# Live Intervention Splicing & Dynamic Topological Task Rescheduling Architecture

## 1. Executive Summary & Problem Formulation
Dalam orkestrasi autonomous agent multi-langkah, rencana kerja awal direpresentasikan sebagai Directed Acyclic Graph (DAG) tugas:
$$\mathcal{G}_0 = (\mathcal{V}_0, \mathcal{E}_0)$$
Di mana $\mathcal{V}$ adalah sekumpulan tugas (task nodes) dan $\mathcal{E}$ adalah dependensi kausal antar-tugas ($u \to v$ menandakan $v$ membutuhkan luaran $u$).

Pada runtime dinamis, kegagalan tool, perubahan spesifikasi, atau intervensi pengguna mengharuskan agen melakukan perubahan struktur rencana (live mutation). Pendekatan naif memiliki dua cacat fatal:
1. **Full Pipeline Re-execution (Wasteful)**: Mengulang seluruh tugas dari awal memboroskan token dan waktu komputasi, melanggar batas Amdahl.
2. **Untracked Mutation (Cascade Inconsistency)**: Menyisipkan atau mengubah tugas tanpa membatalkan tugas hilir (downstream tasks) yang bergantung pada kontrak lama, memicu halusinasi dan korupsi data.

## 2. Formalism & Invariants

### 2.1 Causal Cone Downstream Invalidation
Ketika sebuah node $u \in \mathcal{V}$ diintervensi atau diubah kontraknya (misal: modifikasi skema data atau perbaikan bug), himpunan simpul terdampak kausal (Causal Cone) didefinisikan sebagai penutupan transitif jangkauan downstream:
$$\mathcal{C}(u) = \{ v \in \mathcal{V} \mid u \rightsquigarrow v \}$$
Seluruh node $v \in \mathcal{C}(u)$ yang berstatus `COMPLETED` wajib ditransisikan ke `INVALIDATED`, dan node yang berstatus `RUNNING` wajib dikirimkan sinyal pembatalan kooperatif (`cancellation_requested = true`).

### 2.2 Splicing Transaction & Acyclic Invariant
Operasi penyambungan tugas (splicing) mendefinisikan transformasi:
$$\mathcal{G}_{t+1} = \text{Splice}(\mathcal{G}_t, \mathcal{V}_{\text{new}}, \mathcal{E}_{\text{add}}, \mathcal{E}_{\text{del}})$$
Dengan syarat batas keras (Hard Invariant):
1. **Acyclicity Bound**: $\mathcal{G}_{t+1}$ tidak boleh memuat siklus terarah terhubung:
   $$\forall \text{ cycle } C, \quad C \not\subset \mathcal{G}_{t+1}$$
2. **Atomic Rollback**: Jika terjadi pelanggaran siklus atau node tidak valid, state topologi $\mathcal{G}_t$ dikembalikan seketika secara atomik (zero-mutation).

### 2.3 Dynamic Kahn's Topological Rescheduling
Penjadwalan ulang dilakukan hanya untuk tugas yang belum selesai atau yang telah diinvalasi:
$$\mathcal{V}_{\text{sched}} = \{ v \in \mathcal{V} \mid \text{state}(v) \in \{\text{PENDING}, \text{INVALIDATED}\} \}$$
In-degree dihitung hanya dari dependensi yang belum selesai ($u \in \mathcal{V}_{\text{sched}}$). Tugas yang telah berstatus `COMPLETED` dan tidak terinvalasi dipertahankan tanpa eksekusi ulang.

### 2.4 Amdahl Speedup Bounds
Batas teoretis akselerasi konkurensi sisa jadwal dievaluasi via Hukum Amdahl:
$$S = \frac{1}{(1 - p) + \frac{p}{N}}$$
Di mana $p$ adalah fraksi tugas yang dapat dieksekusi paralel (berada pada lapisan konkurensi yang sama) dan $N$ adalah jumlah pekerja (workers).
