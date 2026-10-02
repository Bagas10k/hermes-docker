---
name: decision-intelligence
description: "Use when evaluating alternatives via multi-criteria math."
version: 1.0.0
author: Bagas Cihuy (Bagas Saputra)
license: MIT
---

# Decision Intelligence: Multi-Criteria Choice & Bias Guard Engine

Framework pengambilan keputusan rasional terstruktur untuk mengevaluasi dan memilih alternatif terbaik (arsitektur sistem, inovasi teknologi, prioritas roadmap, atau dependensi) dengan parameter terstandarisasi di bawah ketidakpastian.

Pencipta & Hak Cipta Mutlak: Bagas Cihuy (Bagas Saputra).

---

## 1. Inti Doktrin & Formula Keputusan

Keputusan terbaik bukan yang paling populer, melainkan yang memadukan nilai nyata, kelayakan eksekusi, kekuatan bukti empiris, mitigasi risiko, dan reversibilitas:

$$\text{Best Decision} = \text{High Value} + \text{Feasible} + \text{Evidence-Backed} + \text{Risk-Controlled} + \text{Reversible When Uncertain}$$

### Aturan Pokok:
1. **Pemisahan Elemen Bersih**: Pisahkan secara eksplisit antara preferensi subjektif, bukti empiris, ketidakpastian lingkungan, biaya salah pilih (*blast radius*), dan derajat reversibilitas opsi.
2. **Penyaring Kendala Keras (Hard Constraints Gate)**:
   - Evaluasi opsi terhadap batasan mutlak (`must_have` dan `must_not`) sebelum pembobotan.
   - Opsi yang melanggar kendala keras otomatis digugurkan (skor 0.0) tanpa membuang komputasi evaluasi.
3. **Pintu Bukti Empiris (Evidence Gate)**:
   - Opsi dengan bukti lemah ($\le 4/10$) dilarang terpilih pada keputusan berdampak tinggi tanpa mitigasi eksperimen murah/cepat (*spike test*) terlebih dahulu.
   - Derajat keyakinan (*confidence*) diturunkan proporsional terhadap ketidakpastian data.

---

## 2. Matriks Pemilih Metode (Method Selector)

Pilih metode evaluasi yang sesuai dengan konteks dan batasan waktu:

| Kondisi Masalah | Metode Terpilih | Fokus & Karakteristik |
| :--- | :--- | :--- |
| Multi-kriteria standar, trade-off jelas | **Weighted Utility** | Pembobotan terstandarisasi $0-10$, cepat, transparan |
| Kriteria saling bertentangan tajam | **AHP-Lite (Pairwise)** | Menghitung konsistensi bobot antar-pasang kriteria |
| Ingin dekat solusi ideal & jauh dari terburuk | **TOPSIS-Lite** | Mengukur jarak Euclidean ke batas ideal positif & negatif |
| Ketidakpastian hasil & probabilitas terukur | **Expected Utility** | $\sum P(s) \cdot U(s)$ memaksimumkan utilitas harapan |
| Risiko kritis / taruhan besar | **Minimax Regret** | Meminimalkan penyesalan terburuk jika asumsi meleset |
| Waktu sempit & keputusan mudah dibatalkan | **Satisficing** | Opsi pertama yang melampaui batas ambang kelayakan |
| Bukti lemah pada taruhan besar | **Value of Information (VOI)** | Tunda keputusan besar, jalankan uji coba kecil terarah |

---

## 3. Mesin Penilaian 9-Parameter (Scoring Engine)

Setiap alternatif dinilai pada skala $0 \text{ s/d } 10$:

1. `impact` (Bobot Default 0.20): Besaran nilai atau daya ungkit hasil jika berhasil.
2. `strategic_fit` (Bobot Default 0.15): Keselarasan dengan visi sistem & preferensi Mas Bagas.
3. `feasibility` (Bobot Default 0.15): Kemudahan implementasi teknis dan ketersediaan perkakas.
4. `speed` (Bobot Default 0.10): Kecepatan mencapai hasil pertama yang dapat diverifikasi.
5. `cost_efficiency` (Bobot Default 0.10): Kehematan sumber daya (RAM $\le$ 9.0 GB, CPU, kuota token).
6. `risk_safety` (Bobot Default 0.10): Tingkat keamanan sistem dan ketahanan terhadap galat.
7. `reversibility` (Bobot Default 0.08): Kemudahan opsi dibatalkan/dialihkan bila terjadi kendala.
8. `novelty_edge` (Bobot Default 0.07): Keunggulan pembeda unik yang melampaui kebiasaan lama.
9. `evidence_strength` (Bobot Default 0.05): Kualitas data empiris dan rekam jejak keberhasilan nyata.

Normalisasi Bobot: $\sum_{i=1}^n w_i = 1.0$.

### Formula Penilaian & Penalti Risiko:
$$\text{Final Score} = \sum_{i=1}^n (w_i \cdot s_i) - \text{Risk Penalty}$$

*Tingkat Penalti Risiko:*
- **Low Risk**: $0.0$
- **Medium Risk**: $0.5$
- **High Risk**: $1.0$
- **Critical Risk**: $2.0$

*Margin Tipis ($\Delta \le 0.3$):* Jika skor dua kandidat teratas terpaut $\le 0.3$, jangan putuskan tergesa-gesa; gunakan parameter `reversibility` dan `evidence_strength` sebagai pembeda penentu, atau lakukan uji tanding purwarupa minimal (*spike test*).

---

## 4. Penjaga Bias Kognitif (Cognitive Bias Guard)

Sebelum mengesahkan keputusan, lewati 8 filter penangkal bias (Kahneman & Tversky):

1. **Confirmation Bias**: Wajib mencari minimal satu skenario kegagalan terburuk atau data yang melemahkan opsi favorit.
2. **Availability Bias**: Menolak memberikan nilai tinggi hanya karena suatu teknologi/opsi baru saja dibahas atau viral di linimasa.
3. **Anchoring Bias**: Menilai setiap alternatif secara mandiri terhadap kebutuhan proyek, bukan terpaku pada angka/spesifikasi opsi pertama yang dilihat.
4. **Status Quo Bias**: Memastikan opsi bertahan tidak menang semata-mata karena kenyamanan kebiasaan lama; uji terhadap batasan baru.
5. **Novelty Bias**: Menghukum opsi baru/keren dengan penalti bukti jika belum terbukti stabil di lingkungan produksi serupa.
6. **Sunk Cost Fallacy**: Menghapus pertimbangan waktu, tenaga, atau biaya historis yang sudah terlanjur keluar; evaluasi efisiensi ke depan dari titik saat ini.
7. **Loss Aversion**: Menilai potensi keuntungan secara objektif tanpa ketakutan berlebihan terhadap risiko yang dapat dimitigasi.
8. **Overconfidence Bias**: Membatasi status keyakinan maksimal pada level `medium` atau `low` jika belum diverifikasi langsung di lingkungan nyata.

---

## 5. Kontrak Output Standar (Output Contract)

Setiap analisis keputusan wajib menghasilkan 7 bidang deterministik:

```yaml
winner: "Nama opsi terpilih"
confidence: "low | medium | high"
ranked_options:
  - { rank: 1, name: "Opsi Terpilih", score: 8.2 }
  - { rank: 2, name: "Alternatif B", score: 7.5 }
why:
  - "Alasan keunggulan kausal 1"
  - "Alasan keunggulan kausal 2"
risk: "Risiko utama yang harus dimitigasi"
next_action: "Langkah konkret berikutnya yang langsung dieksekusi"
fallback: "Opsi cadangan jika rute utama terhambat"
```

---

## 6. Jebakan Umum (Pitfalls)

- **Menilai tanpa normalisasi bobot:** Total bobot kriteria harus tepat bernilai $1.0$ agar perbandingan skor antar-opsi valid secara matematis.
- **Mengabaikan reversibilitas saat bukti rendah:** Memilih opsi satu arah (*irreversible*) dengan bukti minim mengundang risiko fatal; pilih opsi dengan reversibilitas tinggi saat menghadapi ketidakpastian.
- **Memilih berdasarkan popularitas:** Popularitas di komunitas bukan bukti kecocokan arsitektur pada batasan sumber daya nyata.
