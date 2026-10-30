---
name: mcp-engineering-workflow
description: "Use when building or registering custom MCP servers."
version: 1.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [mcp, model-context-protocol, fastmcp, iconify, server-registration, cli]
---

# MCP Engineering & Registration Workflow

Skill panduan baku untuk membuat, mengonfigurasi, dan mendaftarkan server MCP (Model Context Protocol) ke Hermes Agent secara aman, cepat, dan teruji.

## 1. Aturan Keras Keamanan Konfigurasi (Guardrail Invariant)
- **Dilarang keras mengedit `~/.hermes/config.yaml` secara manual via file editor/patch.** Hermes memiliki guardrail keamanan yang menolak pengeditan langsung file konfigurasi utama oleh alat agen (`Refusing to write to Hermes config file`).
- **Gunakan CLI resmi `hermes mcp add`:** Selalu daftarkan MCP melalui antarmuka perintah CLI resmi Hermes.
- **Pipa Otomasi Non-Interaktif:** Pada eksekusi terminal nir-interaktif / sub-agent, `hermes mcp add` akan menanyakan konfirmasi `Enable all N tools? [Y/n/select]:` dan membatalkan jika stdin kosong. Gunakan:
  ```bash
  echo "Y" | hermes mcp add <name> --command <executable> --args <args...>
  ```

## 2. Pola Pembuatan MCP Server Lokal Bebas Token (Zero-Auth FastMCP)
Jika pengguna meminta server MCP tanpa API key atau tanpa login:
- Manfaatkan venv internal Hermes (`/home/ubuntu/.hermes/hermes-agent/venv/bin/python`) yang sudah memiliki dependensi `mcp` (`from mcp.server.mcpserver import MCPServer`) dan `httpx`.
- Simpan berkas server di direktori terisolasi (misal `/home/ubuntu/mcp-<nama>/server.py` atau repo `/home/ubuntu/<repo>/<pkg>/server.py`).
- **Pitfall Resolusi `sys.path` Paket:** Ketika Hermes mengeksekusi script server secara langsung (`--args .../server.py`), Python menyetel `sys.path[0]` ke folder `server.py`, bukan root paket. Jika mengimpor modul saudaranya (`from pkg.core...`), akan muncul `ModuleNotFoundError` yang mengakibatkan error `✗ Failed to connect: Connection closed`. Wajib selipkan path resolver di baris teratas `server.py`:
  ```python
  import sys, os
  sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
  ```
- Implementasikan stdio async server menggunakan `asyncio.run(server.run_stdio_async())`.
- Gunakan `@server.tool()` dengan type hinting dan docstring yang jelas.

Contoh struktur dasar:
```python
#!/usr/bin/env python3
import asyncio
from mcp.server.mcpserver import MCPServer

server = MCPServer("my-tool")

@server.tool()
def my_action(param: str) -> str:
    """Deskripsi fungsi."""
    return f"Hasil: {param}"

if __name__ == "__main__":
    asyncio.run(server.run_stdio_async())
```

## 3. Alur Verifikasi Biner (3-Step Verification)
Sebelum melaporkan ke pengguna bahwa MCP siap digunakan, wajib jalankan 3 langkah verifikasi:
1. **Uji Script Standalone:**
   Jalankan fungsi modul langsung via Python CLI untuk memastikan tidak ada error sintaks, import, atau jaringan:
   ```bash
   /home/ubuntu/.hermes/hermes-agent/venv/bin/python -c "import sys; sys.path.insert(0, '/home/ubuntu/mcp-<nama>'); from server import ..."
   ```
2. **Uji Koneksi & Tool Discovery Hermes:**
   ```bash
   hermes mcp test <name>
   ```
   Pastikan muncul output `✓ Connected` dan daftar tools terdeteksi lengkap.
3. **Audit Status Terdaftar & Enable Recovery:**
   ```bash
   hermes mcp list
   ```
   Pastikan status server berada pada kondisi `✓ enabled`.
   *Pitfall Status Disabled:* Jika pendaftaran awal sempat gagal koneksi, Hermes akan mencatatnya sebagai `✗ disabled`. Untuk mengaktifkannya kembali tanpa menghapus konfigurasi:
   ```bash
   hermes config set mcp_servers.<name>.enabled true
   ```
   Untuk memuat tools ke sesi yang sedang berjalan, kirim command `/reload-mcp`.

## 4. Standar Repositori Open-Source GitHub
Jika MCP dinaikkan statusnya menjadi proyek/repositori publik GitHub:
- Sediakan struktur paket standar Python: `pyproject.toml` dengan CLI entrypoint di `[project.scripts]`, `README.md` berstandar showcase (badges, manifesto, tabel tool, arketipe visual), `LICENSE` (MIT), dan `.gitignore`.
- Lengkapi dengan CLI mandiri (`cli.py`) agar tool bisa dieksekusi dari terminal pengguna tanpa wajib membuka Hermes/MCP client.
- Sediakan unit test suite di folder `tests/` yang memvalidasi seluruh fungsi logika inti secara deterministik.
- Pola Arsitektur Dual Engine: Kombinasikan *Chassis Generator* (membuat komponen baru) dan *Transmute Engine* (linter + auto-healer untuk merombak kode eksisting).

## 5. Lifecycle & Demonstrasi Visual Aset
- **Pembaruan / Hapus Server:** Gunakan `hermes mcp remove <name>` sebelum mendaftarkan ulang jika ada perubahan path atau struktur command.
- **Showcase Visual ke Pengguna:** Jika MCP menghasilkan artefak grafis/UI (seperti ikon SVG), render grid pratinjau ke berkas HTML temporer, tangkap screenshot via Chromium headless (`chromium --headless --no-sandbox --disable-gpu --screenshot=<path> <html-path>`), dan kirim langsung ke Telegram menggunakan `MEDIA:<path>.png`.
