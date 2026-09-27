# Arsitektur DAG Task Splicing & Dynamic Topological Replanning

Dokumen referensi mendalam untuk arsitektur eksekusi alur kerja Directed Acyclic Graph (DAG) pada agen otonom generasi baru.

## 1. Landasan Teoretis: Graph Concurrency & Critical Path

Dalam sistem orkestrasi agen otonom modern (seperti Hermes Multi-Agent, LangGraph, atau n8n-style agentic workflows), tugas didekomposisi menjadi sekumpulan node $V$ dan relasi dependensi kausal $E$, membentuk graf $G = (V, E)$.

### Hukum Amdahl & Critical Path Formulation
Misalkan durasi serial dari seluruh node adalah:
$$T_{\text{serial}} = \sum_{v \in V} \text{duration}(v)$$

Waktu penyelesaian minimum graf di bawah konkurensi tak terbatas ditentukan oleh jalur kritis (*critical path*):
$$T_{\text{critical}} = \max_{p \in \text{Paths}(G)} \sum_{v \in p} \text{duration}(v)$$

Maksimum percepatan teoretis (*Theoretical Speedup Upper Bound*):
$$S_{\text{max}} = \frac{T_{\text{serial}}}{T_{\text{critical}}}$$

Fraksi paralel dari alur kerja adalah:
$$f_{\text{parallel}} = \frac{T_{\text{serial}} - T_{\text{critical}}}{T_{\text{serial}}}$$

Ketika agen memanggil beberapa sub-agen atau tools independen secara serentak pada Layer yang sama, durasi eksekusi terpangkas secara drastis tanpa melanggar batasan kausalitas data.

---

## 2. Dynamic Task Splicing (Penyisipan Node In-Flight)

Kelemahan perencana statis adalah ketidakmampuannya beradaptasi saat alat mengembalikan informasi baru yang menuntut langkah validasi tambahan sebelum eksekusi berbahaya.

### Mekanisme Splicing
Ketika sebuah node $v_{\text{target}}$ memerlukan prakondisi baru (misalnya pra-pemeriksaan AST sebelum `patch` berkas):
1. Inisialisasi node baru $v_{\text{new}}$ dengan status `pending`.
2. Ambil seluruh himpunan pendahulu $\text{Pred}(v_{\text{target}}) = \{u \in V \mid (u, v_{\text{target}}) \in E\}$.
3. Alihkan relasi:
   $$\forall u \in \text{Pred}(v_{\text{target}}), \quad E \leftarrow (E \setminus \{(u, v_{\text{target}})\}) \cup \{(u, v_{\text{new}})\}$$
4. Hubungkan node baru ke target:
   $$E \leftarrow E \cup \{(v_{\text{new}}, v_{\text{target}})\}$$
5. Verifikasi invariansi asiklik ($\text{CycleCheck}(G) = \text{False}$).

---

## 3. Causal Cone Isolation & Failure Pruning

Jika sebuah node $v_{\text{fail}}$ mengalami galat fatal (misalnya unit test gagal total atau resource eksternal tidak dapat diakses):
- Menjalankan seluruh node berikutnya adalah pemborosan token dan komputasi (*Token Waste Loop*).
- Menghapus seluruh workflow adalah reaksi berlebihan (*destructive wipe*).

### Solusi: Forward Causal Cone
Himpunan node terdampak kausal ke depan didefinisikan sebagai:
$$\text{Cone}^{+}(v) = \{w \in V \mid \text{terdapat jalur berarah dari } v \text{ ke } w\}$$

Langkah penanganan:
1. Tandai $v_{\text{fail}}$ dengan status `failed`.
2. Tandai seluruh $w \in \text{Cone}^{+}(v_{\text{fail}})$ dengan status `skipped`.
3. Node yang berada di luar kerucut kausal ($\forall u \notin \text{Cone}^{+}(v_{\text{fail}})$) tetap berstatus `pending` atau `running` dan dapat menyelesaikan tugasnya secara independen.

---

## 4. Evaluasi Status Node & Penomoran Paralel

Pada eksekusi konkuren serentak:
- **Penomoran Node:** Hindari tabrakan ID dengan menyertakan `call_id` unik pada setiap tool invocation (`node_tool_${message_id}_${call_id}`).
- **Layering Sugiyama:** Hitung deretan derajat masuk ($\text{in-degree}$) untuk menyusun tampilan UI DAG yang simetris dan rapi tanpa garis silang tumpang-tindih.
- **Transparansi State:** Setiap node menyimpan catatan mikrodetik durasi, input JSON, dan output receipt untuk audit trail terverifikasi.
