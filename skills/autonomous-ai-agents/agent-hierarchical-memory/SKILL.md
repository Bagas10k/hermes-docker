---
name: agent-hierarchical-memory
description: Hierarchical virtual memory and dynamic paging for agents.
version: 0.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [memory, virtual-paging, long-horizon, autonomous-agents, kv-cache]
    related_skills: [context-compaction-curator, agent-test-time-compute]
---

# Agent Hierarchical Virtual Memory & Dynamic Paging

Arsitektur memori virtual 3-tier terstruktur untuk autonomous AI agents yang beroperasi pada tugas jangka panjang (*long-horizon workflows*): Tier-1 (Core Pinned Prefix RAM), Tier-2 (Episodic Dynamic Paging Cache), dan Tier-3 (Procedural Disk Storage Vault).

## When to Use
- Mengelola konteks agen pada tugas multi-langkah panjang (>30 gilir/turns) agar tidak kehabisan context window.
- Mencegah rusaknya KV-cache / prefix caching engine inferensi akibat pemangkasan naif di awal prompt.
- Melakukan eviksi terstruktur berbasis utilitas per token (Knapsack selection) dari memori kerja ke penyimpanan sekunder.
- Membaca dan memanggil kembali (*page-in*) fragmen memori yang sebelumnya telah diarsip ke disk.

Don't use for:
- Sesi tanya jawab pendek satu putaran tanpa riwayat interaksi.
- Pengganti database relasional penuh untuk query transaksi bisnis enterprise.

## Prerequisites
- Python 3.8+ (tersedia secara native di environment).
- Modul internal `scripts/memory_paging_engine.py` untuk operasi paging deterministik.

## How to Run
Jalankan uji validasi invariansi memori virtual:
`terminal(command="python3 ~/.hermes/skills/autonomous-ai-agents/agent-hierarchical-memory/scripts/memory_paging_engine.py")`

## Quick Reference
- Pin Halaman Core (Tier-1): `vm.pin_core_page(page_id, content, importance=1.0)`
- Paging-In ke Working Memory (Tier-2): `vm.page_in(page_id, content, importance=0.7)`
- Dapatkan Alokasi Token: `vm.get_token_usage()`
- Bentuk Prompt Konteks Aktif: `vm.build_active_context()`

## Procedure
1. Inisialisasi arsitektur `HierarchicalVirtualMemory` dengan batas token Tier-1 dan Tier-2.
2. Sematkan (*pin*) instruksi mutlak, persona, dan batasan utama sistem ke Tier-1 Core RAM. Blok ini tidak akan pernah dieviksi.
3. Saat mengeksekusi tugas, masukkan hasil tool dan artefak kerja sementara ke Tier-2 via `page_in()`.
4. Jika kuota Tier-2 terlampaui, engine secara otomatis mengevaluasi rasio utilitas per token $U(p)/|p|_{\text{tokens}}$ dan memindahkan halaman utilitas terendah ke Tier-3 Disk Vault.
5. Saat halaman lama dibutuhkan kembali berdasarkan referensi ID atau pencarian semantik, panggil `page_in(page_id)` untuk menukarnya kembali ke Tier-2.
6. Bangun context prompt menggunakan `build_active_context()` untuk menjaga struktur prefix monotonic bagi akselerasi prompt caching.

## Pitfalls
- **Dynamic Timestamps in System Prefix**: Menempatkan waktu dinamis (detik/menit) di baris pertama prompt Tier-1 menggagalkan prefix caching di sisi server inferensi LLM. Simpan stempel waktu di metadata atau blok dinamis Tier-2.
- **Unbounded Memory Bloat**: Menolak eviksi Tier-2 menyebabkan context overflow fatal ($O(N^2)$ attention compute). Selalu terapkan batas token keras.
- **Lost Updates on Evicted Pages**: Mengubah data pada halaman yang berada di Tier-3 tanpa memanggil `page_in` dapat menimbulkan desinkronisasi status.

## Verification
- Jalankan skrip engine paging: pastikan seluruh invariansi lolos (`ALL HIERARCHICAL VIRTUAL MEMORY INVARIANTS TESTED SUCCESSFULLY`).
- Pastikan bahwa halaman yang disematkan di Tier-1 tetap bertahan saat eviksi massal terjadi.
