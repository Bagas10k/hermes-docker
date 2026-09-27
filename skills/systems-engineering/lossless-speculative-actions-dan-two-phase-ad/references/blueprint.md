# Lossless Speculative Actions & Two-Phase Adaptive Verification untuk Agen Otonom

Status: TESTED
Kategori: Autopilot / Agentic Acceleration / Distributed Systems
Tautan Terkait: [[SYSTEM/KNOWLEDGE_ENGINE]], [[KNOWLEDGE/INDEX]], [[Speculative-Tool-Execution-PASTE-dan-Lossless-Rollback]], [[Speculative-Tool-Execution-dan-Causal-Rollback-Barrier]], [[SYSTEM/AGOTIMA_OPERASIONAL_HERMES]]

---

## 1. Latar Belakang & Motivasi Rekayasa
Pada sistem multi-agen dan arsitektur LLM modern, hambatan latensi kritis bukan lagi sekadar pemrosesan token (*time-to-first-token*), melainkan **interaksi sekuensial lingkungan (*environment round-trip latency*)**. Agen otonom umumnya beroperasi dalam loop serial:
$$\text{Observe} \to \text{Reason (Thought)} \to \text{Plan Action} \to \text{Tool Execution} \to \text{Next Observation}$$

Jika setiap pemanggilan tool (REST API, pencarian web, kueri database, atau MCP call) memakan 400–1200ms, alur 5-langkah menghasilkan latensi interaktif 3–8 detik. Menunggu output satu per satu membatasi throughput sistem interaktif real-time.

Terinspirasi dari *branch prediction / speculative execution* mikroprosesor dan *speculative decoding* pada inferensi LLM, makalah ICLR 2026 *"Speculative Actions: A Lossless Framework for Faster Agentic Systems"* (arXiv:2510.04371) serta arsitektur *Two-Phase Adaptive Speculation* merumuskan paradigma dekomposisi **Speculator vs Actor** yang menjamin sifat **Lossless Semantics**.

---

## 2. Sintesis Tiga Mindset Problem Solving

### A. Lensa Mekanistik-Kausal (Mechanism & Bounds)
Model sistem formal:
Sistem dipecah menjadi dua entitas independen:
1. **Actor ($\mathcal{A}$)**: Model primer berkemampuan penalaran tinggi (misal: frontier LLM) yang menentukan *ground truth* semantik dan side-effects yang sah. Memiliki latensi eksekusi rata-rata $T_{\mathcal{A}}$.
2. **Speculator ($\mathcal{S}$)**: Model kecil berlatensi ultra-rendah (misal: distilled model / fast classifier / statistical heuristic) yang memprediksi kandidat aksi berikutnya $\{a_1, a_2, \dots, a_k\}$ dengan latensi $T_{\mathcal{S}} \ll T_{\mathcal{A}}$.

Ketika Actor memproses langkah $t$, Speculator secara spekulatif mengeksekusi aksi $a_{t+1}$ pada lingkungan yang terisolasi (*sandboxed / prefetch buffer*).

#### Formula Batas Speedup Spekulasi:
Probabilitas kecocokan prediksi Speculator terhadap keputusan final Actor dinotasikan sebagai akurasi spekulasi $\alpha = P(a_{\text{spec}} = a_{\text{actor}})$.

Waktu siklus per langkah:
- Jika spekulasi tepat (Hit, probabilitas $\alpha$):
  $$T_{\text{hit}} = \max(T_{\mathcal{A}}, T_{\mathcal{S}} + T_{\text{tool\_exec}}) \approx T_{\mathcal{A}}$$
  (Eksekusi tool terjadi bersamaan dengan proses reasoning Actor).
- Jika spekulasi meleset (Miss, probabilitas $1 - \alpha$):
  $$T_{\text{miss}} = T_{\mathcal{A}} + T_{\text{tool\_exec}} + T_{\text{revert}}$$
  di mana $T_{\text{revert}}$ adalah overhead kompensasi atau pengabaian buffer.

Batas rasio speedup sistem ($S$):
$$S = \frac{T_{\text{sequential}}}{E[T_{\text{speculative}}]} = \frac{T_{\mathcal{A}} + T_{\text{tool\_exec}}}{\alpha \cdot \max(T_{\mathcal{A}}, T_{\text{tool\_exec}}) + (1 - \alpha)(T_{\mathcal{A}} + T_{\text{tool\_exec}} + T_{\text{revert}})}$$

Jika $T_{\mathcal{A}} \approx T_{\text{tool\_exec}}$ dan $T_{\text{revert}} \approx 0$ (pada tool idempotent/read-only), batas teoretis maksimum speedup untuk spekulasi tunggal adalah:
$$S_{\max} = \frac{2 T}{T} = 2.0 \quad (\text{penurunan latensi hingga } 50\%)$$

Berdasarkan Hukum Amdahl, fraksi kritis yang dapat dipercepat ($p$) adalah durasi tool calling di luar verifikasi Actor.

### B. Lensa Bayesian-Eksperimental (Evidence & Belief Updating)
Kapan spekulasi agresif menguntungkan secara matematis?
Terapkan kalkulasi **Value of Information & Net Speculation Gain**:

Biaya spekulasi terdiri dari token compute Speculator $C_{\mathcal{S}}$ dan komputasi tool calling $C_{\text{tool}}$.
Keuntungan spekulasi adalah penghematan waktu $\Delta T = T_{\text{tool\_exec}}$.

Expected Net Gain ($\mathbb{E}[G]$):
$$\mathbb{E}[G] = \alpha \cdot \Delta T - (1 - \alpha) \cdot T_{\text{rollback\_cost}} - \lambda \cdot (C_{\mathcal{S}} + C_{\text{tool}})$$

Ambang batas Bayesian untuk memicu eksekusi spekulatif:
Pemicuan spekulatif hanya diizinkan jika keyakinan posterior $P(\text{Match} \mid \text{Context}) > \theta^*$, di mana:
$$\theta^* = \frac{T_{\text{rollback\_cost}} + \lambda C_{\text{waste}}}{\Delta T + T_{\text{rollback\_cost}}}$$

Pada tool read-only (seperti `search_files`, `read_file`, `web_search`), $T_{\text{rollback\_cost}} \to 0$, sehingga nilai ambang batas $\theta^*$ turun drastis (~0.25–0.30). Sebaliknya, pada tool bermutasi disk/database (`write_file`, `patch`, `execute_code` mutatif), $T_{\text{rollback\_cost}}$ tinggi atau tidak terhingga, sehingga $\theta^* \to 1.0$ (dilarang spekulasi tanpa isolasi transaksional sempurna).

### C. Lensa Desain Sistem & Optimasi (Structure & Trade-offs)
Untuk menjamin **Lossless Semantics** (hasil akhir identik 100% dengan eksekusi serial murni), arsitektur wajib memenuhi 3 pilar proteksi:

1. **Safety Envelopes (Klasifikasi Kemampuan Tool)**:
   - *Class 0 (Pure Read/Idempotent)*: `web_search`, `read_file`, `cat`, `grep`, `get_*`. Bebas dieksekusi spekulatif seketika (prefetching).
   - *Class 1 (Reversible Mutations)*: `write_file` ke file staging/temporary, `INSERT` pada database dalam `SAVEPOINT` aktif. Eksekusi spekulatif diizinkan dengan pembatalan rollback otomatis (`ROLLBACK TO SAVEPOINT`).
   - *Class 2 (Irreversible / External Effects)*: Pembayaran API, posting medsos, mutasi berkas produksi permanen. DILARANG spekulatif, wajib menunggu konfirmasi verifikasi Actor.

2. **Semantic Guard & Verification Gate**:
   - Actor menghasilkan payload aksi ground truth $a_{\text{ground}}$.
   - Matcher mengevaluasi kesetaraan semantik:
     $$\text{Match}(a_{\text{ground}}, a_{\text{spec}}) = \begin{cases} 1 & \text{jika } \text{tool\_name identik } \wedge \text{args\_hash identik} \\ 0 & \text{lainnya} \end{cases}$$
   - Jika cocok, hasil di buffer staging langsung di-commit ke memori konteks agen tanpa jeda I/O.
   - Jika tidak cocok, buffer dibuang (*discard*), dan aksi $a_{\text{ground}}$ dieksekusi secara standar.

3. **Two-Phase Adaptive Transition (ASP $\to$ VSP)**:
   - *Phase I: Aggressive Speculation Phase (ASP)*: Dijalankan pada tugas berstruktur deterministik tinggi (misal: pipeline audit, pengecekan dependensi berkala).
   - *Phase II: Verified Speculation Phase (VSP)*: Jika entropi output Speculator tinggi atau tingkat kepastian $< \theta^*$, sistem beralih ke VSP di mana penalaran Actor berjalan penuh di jalur kritis dan spekulasi ditahan.

---

## 3. Matriks Implementasi pada Arsitektur Agen Hermes

| Komponen | Implementasi Praktis di Ekosistem Hermes |
|---|---|
| **Speculator** | Model lokal cepat / rule-based lookahead (MiniLM / heuristic command pattern) |
| **Actor** | General Manager Hermes / model frontier (`gpt-5.5`, Claude 3.5 Sonnet) |
| **Prefetch Buffer** | In-memory key-value cache dengan TTL singkat (60 detik) untuk read-only tools |
| **Rollback Barrier** | Git staging dirty tree check / filesystem shadow layer sebelum commit |
| **Safety Filter** | Whitelist tool: hanya `read_file`, `search_files`, `web_search`, `curl (GET)` |

---

## 4. Kesimpulan & Aturan Operasional
1. **Aturan Whitelist Spekulasi**: Hanya Class 0 (Read-only/Idempotent) yang diizinkan untuk speculative prefetching tanpa sandboxing OS penuh.
2. **Lossless Invariant**: Output context yang disajikan ke pengguna dan catatan memori permanen tidak boleh memuat jejak spekulasi yang meleset (*zero hallucination leakage*).
3. **Efisiensi Token**: Membatalkan kandidat spekulasi di level I/O memory lokal sebelum token observasi dimasukkan ke prompt history LLM, menghemat hingga 40–55% token konteks yang terbuang pada spekulasi gagal.
