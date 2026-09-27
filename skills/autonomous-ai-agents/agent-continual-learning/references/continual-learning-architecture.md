# Arsitektur Continual Learning & Skill Crystallization pada Agen Otonom

Dokumen referensi teknis mendalam mengenai mekanisme stabilisasi memori, ekstraksi trajektori prosedural, dan sintesis skill otonom generasi baru.

## 1. Fondasi Matematis & Dilema Stabilitas-Plastisitas (Stability-Plasticity Dilemma)

Pada agen otonom berbasis Large Language Model (LLM), *Continual Learning* (CL) tidak dimediasi oleh backpropagation gradien berbiaya tinggi di waktu-nyata, melainkan melalui **In-Context Experience Consolidation & Dynamic Procedural Paging**.

Dilema klasik dinyatakan dalam optimasi multi-objektif:
$$\max_{\theta, \mathcal{M}} \left[ \mathbb{E}_{\tau \sim \mathcal{T}_{\text{new}}} [R(\tau \mid \mathcal{M})] - \lambda \cdot D_{\text{KL}}(\pi_{\mathcal{M}}(\cdot \mid s) \parallel \pi_{\mathcal{M}_{\text{base}}}(\cdot \mid s)) \right]$$

Di mana:
- $\mathcal{M}$ adalah himpunan skill dan memori terindeks.
- $\mathcal{T}_{\text{new}}$ adalah distribusi tugas-tugas baru.
- $D_{\text{KL}}$ mengukur divergensi perilaku agen pada tugas-tugas fundamental untuk mencegah *catastrophic forgetting*.
- $\lambda$ adalah penalti regularisasi stabilitas (analog dengan matriks informasi Fisher pada Elastic Weight Consolidation / EWC).

## 2. Siklus 4-Tahap Kristalisasi Skill Otonom

```
   +-----------------------+
   | Trajectory Mining     | -> Mengambil riwayat eksekusi SARO sukses
   +-----------+-----------+
               |
               v
   +-----------------------+
   | Heuristik 3-Strike    | -> Verifikasi frekuensi pengulangan >= 3x & konvergensi
   +-----------+-----------+
               |
               v
   +-----------------------+
   | Canonical Distillation| -> Abstraksi variabel, sintesis SKILL.md, & eliminasi noise
   +-----------+-----------+
               |
               v
   +-----------------------+
   | Regression Gate       | -> Verifikasi invariansi golden dataset bebas regresi
   +-----------------------+
```

## 3. Komponen Utama Skrip Pembantu `crystallize_skill.py`

Skrip pendukung mengimplementasikan:
1. **Parser Trajektori**: Mengekstrak transkrip tool calls dari basis data eksekusi atau log terstruktur.
2. **Normalizer Parameter**: Mengubah string absolut lokal `/home/ubuntu/...` menjadi variabel semantik `<workspace_dir>`.
3. **Hardline Validator**: Memeriksa panjang karakter deskripsi ($\le 60$), penutupan titik, ketersediaan bagian mandatori (*When to Use, Prerequisites, Quick Reference, Procedure, Pitfalls, Verification*).
4. **Collision Detector**: Memeriksa apakah nama skill sudah terdaftar atau bertabrakan dengan repositori resmi.
