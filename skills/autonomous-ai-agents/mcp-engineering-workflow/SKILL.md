---
name: mcp-engineering-workflow
description: "Use when building or registering custom MCP servers."
version: 1.2.0
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

## 2. Pola Pembuatan MCP Server Lokal

1. Temukan interpreter yang akan menjalankan server dan periksa SDK-nya pada interpreter itu (`importlib.metadata.version('mcp')` dan uji import). Jangan menganggap `python3`, executable `pip`, runtime browser, dan venv Hermes menunjuk lingkungan yang sama.
2. Pilih API sesuai SDK: v1 memakai `from mcp.server.fastmcp import FastMCP`; v2 memakai `from mcp.server.mcpserver import MCPServer`. Verifikasi migrasi terhadap dokumentasi SDK sebelum mengganti import. Untuk v2, stdio async dapat dijalankan dengan `asyncio.run(server.run_stdio_async())` seperti contoh di bawah.
3. Tambahkan/pin dependensi dalam venv proyek bila perlu; jangan meng-upgrade runtime agen bersama untuk memperbaiki satu server. Gunakan interpreter itu juga saat tes dan pendaftaran.
4. Tanpa API key/login hanya berarti tidak perlu autentikasi penyedia; stdio lokal bukan sandbox OS dan tidak boleh diekspos sebagai HTTP publik tanpa batas akses. Batasi output path, durasi kerja dan subprocess sesuai fungsi tool.
5. Simpan server di direktori proyek terisolasi dan gunakan import lokal relatif/path resolver yang benar, bukan `sys.path` ke salinan helper pribadi di luar repo. Clone bersih harus mempunyai sumber yang sama dengan server yang diuji.
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

## 3. Alur Verifikasi Biner

Pisahkan source ditulis, import berhasil, wire call berhasil, registrasi, enabled dan aktivasi sesi. Jangan melaporkan salah satunya sebagai bukti semuanya.

Sebelum registrasi, lakukan smoke test stdio nyata dengan `StdioServerParameters` + `stdio_client` + `ClientSession`: `initialize()` → `list_tools()` → `call_tool()` menggunakan payload representatif. Periksa isi hasil dan status error, bukan hanya jumlah nama tool. Type hint `dict` tidak memvalidasi bentuk nested storyboard; jalankan payload negatif untuk tipe salah, field wajib hilang dan nilai di luar batas. Discovery yang berhasil belum membuktikan render/side effect sebuah tool.

Jika registrasi masuk cakupan tugas, lanjutkan langkah klien berikut:
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
- **Pola Arsitektur Dual Engine & Anti-Slop Invariants:** Pada MCP antarmuka/desain, kombinasikan *Chassis Generator* (membuat komponen dari 5 arketipe dunia) dan *Transmute Engine* (linter + auto-healer). Tanamkan aturan keras anti-slop: larangan mutlak kicker badge mengambang, eliminasi tag pamer teknis (`Zero AI-Slop`, `WCAG AAA`), serta pembersihan kontras otomatis.

## 5. Lifecycle & Demonstrasi Visual Aset
- **Pembaruan / Hapus Server:** Gunakan `hermes mcp remove <name>` sebelum mendaftarkan ulang jika ada perubahan path atau struktur command.
- **Showcase Visual ke Pengguna:** Jika MCP menghasilkan artefak grafis/UI (seperti ikon SVG atau layout antarmuka), render grid pratinjau ke berkas HTML temporer, tangkap screenshot via Chromium headless (`chromium --headless --no-sandbox --disable-gpu --screenshot=<path> <html-path>`), dan kirim langsung ke Telegram menggunakan `MEDIA:<path>.png`.
