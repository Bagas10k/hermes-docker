---
name: mcp-auth-security
description: MCP OAuth resource indicators and confused-deputy defense.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [mcp, oauth, rfc8707, security, confused-deputy, tool-governance]
    related_skills: [mcp-dynamic-federation, agent-quarantine-gateway]
---

# MCP Auth Security Skill

Arsitektur pertahanan otentikasi dan otorisasi untuk ekosistem Model Context Protocol (MCP) tool servers. Menerapkan RFC 8707 Resource Indicators, audiens-terikat, isolasi token per tool, dan pencegahan serangan confused-deputy pada agen otonom.

## When to Use

- Menerapkan pengamanan otentikasi OAuth 2.1 pada MCP tool server (HTTP/SSE/WebSocket).
- Mengisolasi hak akses alat agar MCP server pihak ketiga tidak dapat membajak token ke server lain.
- Mencegah kebocoran token (*confused-deputy problem*) saat agen memanggil multi-server MCP.
- Don't use for: Pemanggilan tool stdio lokal sederhana tanpa konektivitas jaringan atau multi-tenant boundary.

## Prerequisites

- Python 3.10+ (stdlib `hmac`, `hashlib`, `base64`, `json`).
- Akses ke Authorization Server yang mendukung RFC 8707 Resource Indicators.

## How to Run

Jalankan engine verifikasi token dan audit anti-passthrough melalui skrip:

```bash
python3 ~/.hermes/skills/autonomous-ai-agents/mcp-auth-security/scripts/mcp_auth_engine.py --test
```

## Quick Reference

- **Mint Audience-Bound Token:** Ikat token ke URI kanonikal resource target (`aud = canonical_resource_uri`).
- **Validate Inbound Token:** Periksa tanda tangan, kedaluwarsa (`exp`), audiens (`aud`), dan scope yang dibutuhkan.
- **Anti-Passthrough Gate:** Cegah MCP server meneruskan inbound bearer token ke API eksternal hilir.

## Procedure

1. **Deklarasikan Canonical Resource URI:**
   Setiap MCP server wajib memiliki identitas URI kanonikal tetap (misal `https://mcp.internal/tools/database`).
2. **Terbitkan Token Berbasis RFC 8707:**
   Klien atau agen meminta token otorisasi dengan menyertakan parameter `resource`. Authorization server menyematkan URI ini ke klaim `aud`.
3. **Validasi Audience di Sisi MCP Server:**
   Sebelum memproses eksekusi fungsi tool, MCP server memverifikasi kecocokan `claims["aud"] == canonical_resource_uri`. Tolak jika terjadi perbedaan.
4. **Isolasi Alur Hilir (Zero Passthrough):**
   Pastikan MCP server tidak menyertakan token inbound saat memanggil dependensi lain; gunakan token baru yang dialokasikan khusus untuk tujuan hilir tersebut.

## Pitfalls

- **Ambient Bearer Tokens:** Menggunakan token OAuth umum tanpa klaim `aud` spesifik membuka celah serangan confused-deputy lintas server.
- **Token Passthrough Leak:** Meneruskan header `Authorization: Bearer <token>` ke API eksternal pihak ketiga membocorkan hak akses pengguna.
- **Replay Window:** Token berdurasi panjang tanpa validasi `jti` atau revocation list rentan serangan pengulangan (*replay attack*).

## Verification

Jalankan suite pengujian unit terstandar:

```bash
python3 ~/.hermes/skills/autonomous-ai-agents/mcp-auth-security/scripts/mcp_auth_engine.py --test
```

Kriteria lulus:
1. Token sah dengan resource URI yang tepat diterima (`ok == True`).
2. Token beda audiens ditolak seketika dengan pesan `Audience mismatch`.
3. Permintaan dengan scope kurang ditolak seketika (`Insufficient scope`).
4. Engine anti-passthrough memastikan token tidak pernah diteruskan ke hilir.
