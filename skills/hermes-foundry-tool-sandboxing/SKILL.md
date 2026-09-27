---
name: hermes-foundry-tool-sandboxing
description: Use when sandboxing agent tools, shell, and HTTP requests.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
metadata:
  tags: [security, sandboxing, tools, rust, defense-in-depth, ssrf-protection, zero-leak]
---

# Hermes Foundry Tool Sandboxing & Execution Boundary

Skill ini mengkodifikasi standar pertahanan berlapis (*Defense-in-Depth*) untuk alat eksekusi agen lapangan otonom.

## 1. Prinsip Utama (Deterministic Parameter Coercion)
Setiap panggilan alat (`ToolCallRequest`) wajib melewati validasi deterministik di layer runtime sebelum berinteraksi dengan kernel atau jaringan luar:

1. **Terminal Command Filtering**:
   - Terapkan pemindaian token blacklist: `rm -rf /`, `mkfs`, `:(){ :|:& };:`, `dd if=`, `> /dev/`, `chmod -R 777 /`, `shutdown`, `reboot`.
   - Gunakan hard timeout terisolasi (`tokio::time::timeout`) untuk mencegah hang tak terhingga.
2. **SSRF Defense Gate**:
   - Blokir akses ke metadata service cloud: `169.254.169.254`, `metadata.google.internal`.
   - Batasi protokol hanya `http://` dan `https://` (tolak mutlak `file://`, `gopher://`, `ftp://`).
3. **Resource Bound**:
   - Pasang kuota pemangkasan respons jaringan (misal maks 2MB) agar tidak memicu Out-of-Memory (OOM).
4. **Browser/DOM Script Sanitization**:
   - Blokir manipulasi `document.cookie` dan `localStorage.clear()` pada interaksi browser evaluatif.
