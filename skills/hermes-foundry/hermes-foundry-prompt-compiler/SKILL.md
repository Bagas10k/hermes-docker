---
name: hermes-foundry-prompt-compiler
description: Use when compiling text prompts to DAG agent schemas.
version: 1.0.0
author: Bagas Cihuy
license: MIT
metadata:
  hermes:
    tags: [hermes-foundry, prompt-compiler, dag, toposort, rust, no-code, zero-slop]
---

# Hermes Foundry Prompt Compiler

Pola operasional kompilasi bahasa alami (*Prompt-to-Agent*) menjadi skema agen DAG (*Directed Acyclic Graph*) deklaratif yang teruji dan bebas siklus pada runtime Hermes Agent Foundry.

## Intisari Arsitektur
1. **Deterministic Intent Extraction**:
   - Deteksi pemicu temporal: kata kunci (`setiap`, `cron`, `jam`, `menit`) -> `trigger.type = cron`; selain itu -> `webhook`.
   - Deteksi modul fungsional:
     - Riset (`cari`, `pantau`, `fetch`, `url`) -> `builtin.web_search`.
     - Kognisi (`analisis`, `ringkas`, `audit`, `evaluasi`) -> `hermes.reasoning.react`.
     - Aksi (`jalankan`, `kirim`, `eksekusi`, `lapor`) -> `builtin.terminal_exec`.
     - Penyimpanan (`simpan`, `catat`, `vault`, `obsidian`) -> `builtin.vault_reader`.

2. **Toposort & Algorithmic Cycle Validation**:
   - Seluruh simpul yang dirakit wajib divalidasi dengan algoritma Kahn via `petgraph` sebelum disimpan.
   - Menolak siklus tak hingga dan simpul yang terisolasi.

3. **RAM & Performance Contract**:
   - Kompilasi berjalan di level native Rust dalam hitungan < 1ms.
   - Runtime server mematuhi batas RAM < 15MB RSS.
