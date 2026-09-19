---
name: mathematical-problem-solving
description: "Use when debugging complex bugs. Solves via 3 mindsets."
version: 1.0.0
author: Bagas Cihuy (Nous Research / Hermes Agent)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [problem-solving, mathematical-mindset, debugging, token-optimization, root-cause, causal-inference, bayesian]
    related_skills: [systematic-debugging, test-driven-development]
---

# Tiga Mindset Problem Solving & Protokol Efisiensi Token

## Ringkasan Eksekutif

Kerangka kerja pemecahan masalah deterministik berbasis matematika murni. Kerangka ini menggabungkan penalaran kausal, inferensi Bayesian dengan evaluasi Value of Information (VOI), serta optimasi sistem terkendala — dirancang khusus untuk memecahkan masalah teknis rumit dengan **konsumsi token seminimal mungkin**.

---

## Bagian 1: Sintesis Tiga Mindset Matematis

### 1. Lensa Mekanistik-Kausal (Mechanism & Bounds)
* **Modelkan Sistem Secara Eksplisit:**
  $$y = f(\text{input}, \text{parameter}, \text{keadaan}, \text{lingkungan}) + \epsilon$$
  Jangan pernah menduga output tanpa memetakan fungsi transformasinya.
* **Intervensi Kausal vs Observasi Semu:**
  Bedakan korelasi $P(Y \mid X=x)$ dari kausalitas intervensi $P(Y \mid do(X=x))$. Hilangkan dugaan berbasis kebetulan temporal.
* **Batas Matematis Sebelum Bekerja (Hukum Amdahl):**
  $$S_{\text{latency}} = \frac{1}{(1 - p) + \frac{p}{s}}$$
  Kenali fraksi kritis sistem sebelum mengoptimasi komponen periferal.
* **Pohon Kausal Terbatas:**
  Hentikan penelusuran tak berujung; cari tingkat sebab yang menghasilkan intervensi terarah, prediksi terukur, dan uji pembeda empiris.

### 2. Lensa Bayesian-Eksperimental (Evidence & Belief Updating)
* **Pembaruan Keyakinan Proporsional:**
  $$P(H \mid E) = \frac{P(E \mid H) P(H)}{P(E)}$$
  Perbarui hipotesis secara adil terhadap bobot bukti empiris.
* **Prediksi Apriori:**
  Tuliskan prediksi sebelum melihat output pengujian. Isolasi variabel kontrol (satu intervensi per pengujian).
* **Value of Information (VOI):**
  $$\text{VOI}_{\text{net}} = \mathbb{E}[\text{Nilai Keputusan Baru}] - \text{Biaya Token/Komputasi Probe}$$
  Hanya jalankan probe diagnostik jika VOI positif dan mampu mendiskualifikasi setidaknya satu cabang hipotesis.
* **Nilai Tes Negatif:**
  Bukti yang menggugurkan hipotesis sama berharganya dengan konfirmasi.

### 3. Lensa Desain Sistem & Optimasi (Structure & Trade-offs)
* **Optimasi Terkendala Keras:**
  $$\arg\min_x J(x) \quad \text{terhadap} \quad g_i(x) \le 0$$
  Kebenaran logika, keamanan, dan integritas fungsional adalah kendala keras ($g(x) \le 0$) yang tidak boleh dikompromikan demi skor kosmetik.
* **Inovasi Struktur:**
  Ubah topologi alur kerja, bukan sekadar memodifikasi parameter lokal (hapus dependensi redundant, parallelize independent checks).
* **Evaluasi Distribusi Nyata:**
  Tolak klaim performa rata-rata yang menyembunyikan tail latency ($p95 / p99$).

---

## Bagian 2: Protokol Investigasi Minimal-Token (Token Reduction Engine)

Masalah umum saat agen AI mendiagnosis sistem adalah **Token Bloat Loop**: melakukan puluhan putaran tool call satu per satu (`grep` -> baca konteks -> `grep` lagi), yang mengirim ulang puluhan ribu token konteks berkali-kali.

Terapkan aturan operasional wajib berikut untuk memangkas konsumsi token hingga 80-90%:

### Aturan 1: Script-over-Turns (Batch Diagnostic Probe)
* **PANTANGAN:** Menjalankan 10–30 tool call terpisah secara beruntun untuk mengecek file, diff, proses, dan hash.
* **WAJIB:** Buat satu skrip diagnostik ringkas (Python inline atau Bash compound command) yang memeriksa seluruh komponen secara paralel, lalu kembalikan **hanya ringkasan terstruktur (JSON/bullet poin)** ke konteks agen.
* **Penghematan:** Mengurangi 30 putaran (30x re-sending prompt) menjadi 1–2 putaran saja.

Contoh satu eksekusi terpadu:
```bash
python3 -c '
import json, os, subprocess
results = {
  "pm2": subprocess.getoutput("pm2 jlist"),
  "config_diff": subprocess.getoutput("diff -u /path/a /path/b"),
  "auth_valid": "OK"
}
print(json.dumps(results, indent=2))
'
```

### Aturan 2: Filter Output Ketat di Tingkat Shell
* **PANTANGAN:** Menjalankan `grep -rn` atau `cat` tanpa batas yang mencetak ribuan baris, memicu *truncation to disk*, dan memaksa pembacaan file cache sekunder.
* **WAJIB:**
  - Gunakan `grep ... | head -n 20` atau `tail -n 20`.
  - Filter direktori bising: `--exclude-dir={node_modules,cache,logs,.git,venv}`.
  - Tampilkan hanya file path (`-l`) sebelum memutuskan membaca isi file spesifik.

### Aturan 3: Gunakan `execute_code` untuk Reduksi Data
* Ketika perlu menganalisis log ratusan megabyte atau ribuan entri:
  - Jangan alirkan log mentah ke context LLM.
  - Gunakan `execute_code` (Python session kernel) untuk memfilter, agregasi, dan menghitung statistik di memori Python lokal.
  - Cetak (print) hanya output akhir yang sudah terdestilasi ke stdout LLM.

### Aturan 4: Pohon Uji Biner (Binary Hypothesis Elimination)
* Rancang tes diagnostik pertama yang membagi ruang kemungkinan menjadi dua (50/50):
  - *Contoh:* "Apakah masalahnya di layer Proxy/Jaringan atau di layer Aplikasi Internal?"
  - Satu `curl 127.0.0.1:<port>` langsung menggugurkan separuh pohon kemungkinan tanpa perlu memeriksa puluhan file konfigurasi web proxy.

---

## Checklist Eksekusi Cepat

Sebelum mengeksekusi pemeriksaan sistem:
- [ ] Apakah saya bisa menguji hipotesis ini dalam 1 batch script daripada beberapa kali round-trip?
- [ ] Apakah output perintah dibatasi (`head`, `grep`, filter field) agar tidak membanjiri konteks?
- [ ] Apakah probe ini memiliki Value of Information (VOI) yang jelas untuk mendiskualifikasi hipotesis?
- [ ] Apakah saya menguji variabel kontrol secara terisolasi?
- [ ] Apakah solusi yang dirancang memperbaiki akar struktur kausal, bukan sekadar menambal gejala?
