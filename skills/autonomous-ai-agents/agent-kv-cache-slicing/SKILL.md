---
name: agent-kv-cache-slicing
description: KV-cache compaction and cross-turn attention slicing.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [kv-cache, attention-slicing, context-optimization, token-budget, agent-runtime]
    related_skills: [context-compaction-curator, edge-slm-tool-calling, agent-hierarchical-memory]
---

# Agent KV-Cache Slicing & Attention Compactor

Skill ini mengelola kompresi dinamis Key-Value Cache (KV-Cache) dan pemotongan perhatian lintas giliran (cross-turn attention slicing) untuk agen otonom yang beroperasi pada siklus panjang, menjaga penggunaan RAM/VRAM tetap terikat tanpa merusak koherensi penalaran.

## When to Use

- Gunakan ketika agen mengeksekusi percakapan multi-turn panjang (>10 giliran) di mana latensi Time-To-First-Token (TTFT) atau Inter-Token Latency (ITL) mulai melambat akibat saturasi memori.
- Gunakan saat merancang runtime agen lokal (vLLM, llama.cpp, SGLang) dengan batasan keras VRAM/RAM (misalnya VPS dengan memori terbatas).
- Jangan gunakan untuk percakapan pendek satu giliran (single-shot turn) di mana overhead kompresi melebihi penghematan I/O.

## Prerequisites

- Python 3.10+ (stdlib `hashlib`, `math`, `typing`).
- Akses baca atau kontrol parameter inferensi runtime LLM (`kv_cache_budget`, `sliding_window`).

## Quick Reference

Jalankan pengujian integritas invarian kompresi KV-cache:
```bash
# 1. Uji Attention Sinks & H2O Heavy-Hitter Evacuation
python3 ~/.hermes/skills/autonomous-ai-agents/agent-kv-cache-slicing/scripts/kv_cache_compactor.py

# 2. Uji Differential Trajectory Pruning & Checkpoint Slicing (SLM-005)
python3 ~/.hermes/skills/autonomous-ai-agents/agent-kv-cache-slicing/scripts/test_kv_cache_slicing.py -v
```

## Modul Diferensial Slicing & Checkpoint (SLM-005)

Modul `kv_cache_slicer.py` menyediakan in-place zero-copy rollback untuk eksekusi spekulatif pada model SLM edge:
- `fork_checkpoint(label)`: Kunci state KV-cache sebelum mengeksekusi aksi cabang.
- `prune_to_checkpoint(label)`: Memotong sequence ke checkpoint tanpa alokasi heap baru, memulihkan 100% prefix bersama dengan percepatan Amdahl $\ge 4.5\times$.

## Procedure

1. **Inisialisasi Prefix Sink Zone**:
   - Kunci token awal (minimal 4 token pertama) sebagai *Attention Sinks*.
   - Validasi hash SHA-256 prefix sink agar kompatibel dengan engine prefix caching hardware.

2. **Terapkan Dynamic Window Buffering**:
   - Pertahankan jendela token lokal terakhir ($W \ge 16$) untuk integritas kelanjutan kalimat.

3. **Pruning Berbasis Heavy-Hitter (H2O)**:
   - Hitung akumulasi massa perhatian pada token perantara.
   - Evakuasi token dengan skor utilitas terendah saat batas memori tercapai:
     $$\text{size}(\text{cache}) \le B_{\max}$$

4. **Kalkulasi Kecepatan Amdahl**:
   - Pantau rasio percepatan latensi decode sesuai formula Amdahl:
     $$S_{\text{latency}} = \frac{1}{(1 - p) + \frac{p}{s}}$$

## Pitfalls

- **Menghapus Attention Sink Token**: Membuang 4 token pertama merusak distribusi normalisasi softmax attention dan menyebabkan output acak/halusinasi total (*perplexity explosion*).
- **Inkonsistensi Prefix Hash**: Mengubah susunan token awal membatalkan prefix caching di level engine inferensi, memicu recomputasi $O(N)$ yang mahal.

## Verification

- Jalankan skrip pembantu `kv_cache_compactor.py` dan pastikan seluruh asersi lulus:
  1. Prefix hash tidak berubah selama proses evakuasi.
  2. Ukuran cache tidak pernah melebihi $B_{\max}$.
  3. Rasio kompresi dan percepatan Amdahl terverifikasi secara deterministik.
