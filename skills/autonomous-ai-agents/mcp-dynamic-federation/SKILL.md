---
name: mcp-dynamic-federation
description: Federated on-demand MCP tool discovery and scoping.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [mcp, federation, tool-discovery, scoping, security, token-efficiency]
    related_skills: [hermes-agent, autonomous-orchestrator, mathematical-problem-solving]
---

# MCP Dynamic Federation & Capability Scoping

Arsitektur federasi tool Model Context Protocol (MCP) generasi baru untuk menghubungkan puluhan MCP server tanpa membanjiri konteks agen. Menggunakan pola penemuan on-demand, scoping izin berbasis token (OAuth 2.1), dan dukungan transpor ganda (stdio & Streamable HTTP).

## When to Use

- Agen terhubung ke banyak MCP server (5+ server atau 50+ tools) yang menghabiskan puluhan ribu token jika seluruh schema dimuat di awal.
- Memerlukan pembatasan hak akses tool (least privilege) untuk memisahkan tool baca murni (*read/query*) dari aksi mutatif berbahaya (*write/admin*).
- Menghubungkan server MCP modern (spesifikasi `2026-07-28`+) dengan transpor Streamable HTTP atau stdio ber-caching TTL.
- Don't use for: Koneksi ad-hoc 1 tool ringan tanpa konfigurasi multi-server (gunakan `mcporter` langsung).

## Prerequisites

- Python 3.10+ dengan package `mcp` (versi 2.0+) dan `jsonschema`.
- Node.js (npx) jika menggunakan server berbasis JavaScript/TypeScript.
- Kredensial server tersimpan aman di `.env` (bukan di dalam file konfigurasi publik).

## Quick Reference

```bash
# Uji federasi engine dan validasi isolasi scope
python3 ~/.hermes/skills/autonomous-ai-agents/mcp-dynamic-federation/scripts/mcp_federation_engine.py

# Periksa status koneksi server MCP di Hermes
hermes mcp catalog
```

## Procedure

1. **Inisialisasi Registry Ringkas**:
   - Daftarkan metadata tool (nama, deskripsi 1 baris, cakupan scope, mutasi flag) ke katalog lokal tanpa menyertakan `inputSchema` lengkap.
   - Kriteria selesai: Ukuran manifest di bawah 2.000 token untuk 100+ tools.

2. **Penyaringan Berbasis Scope (Least Privilege Gate)**:
   - Evaluasi token sesi agen terhadap permission yang dibutuhkan tool (`read`, `write`, `admin`).
   - Tolak resolusi schema dengan tantangan `insufficient_scope` jika hak akses belum diberikan.
   - Kriteria selesai: Tool berbahaya tidak dapat diakses sebelum ada step-up authorization eksplisit.

3. **Resolusi Schema On-Demand (Deferred Hydration)**:
   - Ketika agen membutuhkan kapabilitas spesifik, lakukan pencarian (`search_tools`) lalu ambil schema lengkap (`resolve_schema`) hanya untuk tool yang terpilih.
   - Kriteria selesai: Schema lengkap disuntikkan secara dinamis saat eksekusi tanpa mencemari system prompt awal.

4. **Eksekusi Multi-Transport**:
   - Rujuk panggilan ke subprocess `stdio` atau endpoint `Streamable HTTP` dengan header protokol yang sesuai (`MCP-Protocol-Version`).
   - Simpan state session menggunakan opaque handle jika tool bersifat stateful.
   - Kriteria selesai: Panggilan menghasilkan JSON terstruktur valid tanpa kegagalan koneksi.

## Pitfalls

- **Scale Degradation**: Menempatkan lebih dari 30 tool candidates sekaligus pada satu giliran prompt menurunkan akurasi pemilihan hingga di bawah 50%. Wajib gunakan penyaringan 2 lapis (kategori -> pencarian top-5).
- **Stale Cache vs Dynamic Tools**: Server yang memancarkan `notifications/tools/list_changed` harus segera memicu pembatalan cache lokal agar skema baru tidak tertolak.
- **Hardcoded Absolute Paths**: Hindari path absolut mesin lokal di manifest konfigurasi server.

## Verification

Jalankan test suite internal:
```bash
python3 ~/.hermes/skills/autonomous-ai-agents/mcp-dynamic-federation/scripts/mcp_federation_engine.py
```
Output wajib menyatakan `MCP Federation Unit Test Verified: 100% OK`.
