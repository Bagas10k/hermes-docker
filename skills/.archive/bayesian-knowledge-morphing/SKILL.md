---
name: bayesian-knowledge-morphing
description: "Use when learning from scores via Bayesian knowledge morph."
version: 1.0.0
author: Bagas & Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bayesian-learning, knowledge-morphing, priority-queue, semantic-upsert, anti-duplication, value-evaluation]
---

# Bayesian Knowledge Morphing Skill

Sistem pembelajaran otonom berbasis umpan balik nilai numerik (skor 1–10), pembaruan keyakinan Bayesian, kalkulasi prioritas intervensi (*Worth-It Delta*), dan mutasi pengetahuan kanonikal (*Semantic Upsert*) tanpa duplikasi konteks.

## When to Use

- Pengguna memberikan evaluasi multi-kriteria berbasis skor (seperti `grid:2, anim:4, copy:5, smooth:6`).
- Sistem perlu menentukan komponen mana yang paling mendesak diperbaiki (*Worth-It Delta*) sebelum menyentuh kode.
- Sistem perlu memperbarui aturan atau pantangan tanpa menumpuk catatan markdown baru yang menduplikasi konteks sebelumnya.
- **Don't use for:** Bug crashing tunggal (gunakan `systematic-debugging`), atau query tanya-jawab biasa.

## Core Formula & Mathematical Bounds

1. **Prioritas Deviasi Terbesar (Amdahl Bottleneck First):**
   $$\Delta_i = (10 - s_i) \times W(d_i)$$
   - Bobot Kategori ($W$):
     - Arsitektur / Grid / Struktur: $1.5$ (Kritis fondasional)
     - Logika / Invarian / Keamanan: $1.5$ (Non-negotiable)
     - Copywriting & Tone: $1.2$
     - Motion & Fisika Pegas: $1.0$
     - Kosmetik & Aksen: $0.8$
   - Intervensi diurutkan secara menurun berdasarkan $\Delta_i$. Masalah dengan defisit terbesar wajib diselesaikan dan diverifikasi secara terisolasi sebelum beralih ke dimensi berikutnya.

2. **Pembaruan Keyakinan Bayesian (Belief Updating):**
   $$P_t(\text{Pola Berhasil}) = \alpha P_{t-1} + (1 - \alpha) \left(\frac{s_i}{10}\right)$$
   - Bobot data baru $(1 - \alpha) = 0.65$ memastikan sistem cepat beradaptasi terhadap koreksi pengguna.
   - Skor $< 5$ memicu status `CRITICAL_MUTATION_REQUIRED`.

3. **Mekanisme Semantic Morphing (Anti-Duplikasi):**
   - Setiap pola memiliki `canonical_key` unik (contoh: `ui.layout.grid_container`, `ui.motion.spring_physics`).
   - **Jika pola sudah ada:** Mutasi data lama ke versi baru ($v1 \to v2$). Aturan yang terbukti gagal langsung dipindahkan ke `deprecated_patterns`, dan solusi yang terbukti berhasil menggantikan `active_solutions`.
   - Melarang penambahan berkas catatan baru jika konteks pembahasannya sama.

## CLI Commands & Workflows

1. **Evaluasi Skor Masukan Pengguna:**
   ```bash
   mission-control eval "grid:2,anim:4,copy:5,smooth:6"
   ```
2. **Cek Status Seluruh Node Pengetahuan Kanonikal:**
   ```bash
   mission-control eval
   ```
3. **Pemadatan & Deduplikasi Store:**
   ```bash
   mission-control eval compact
   ```

## Pitfalls

- **Multi-Factor Smearing:** Memperbaiki semua aspek sekaligus (mengubah grid, animasi, teks, dan warna dalam 1 perubahan). Wajib mengisolasi perbaikan pada prioritas defisit tertinggi ($\Delta_{\max}$) terlebih dahulu.
- **Append-Only Context Bloat:** Menulis catatan evaluasi baru di markdown setiap kali ada koreksi tanpa memutasi catatan lama. Gunakan `canonical_key` upsert agar memori dan store tetap steril.
- **Cosmetic Patching on Score < 5:** Menambal warna atau padding kecil saat skor $< 5$. Skor di bawah 5 mewajibkan pembongkaran total dari referensi utuh, bukan penambalan kosmetik.
- **Pseudo-Bento 2-Column Trap:** Mengelompokkan antarmuka menjadi 2 kolom raksasa (sidebar 65%/35%) dan menamainya bento. Bento grid sejati membutuhkan interlocking multi-module (hero manifesto, tactical switch card, square micro-tiles, dan full-width anchor).
