---
name: mumu-desktop-delivery
description: Use when building, packaging, or developing mumu desktop Windows companion & VPS connector.
---

# mumu desktop (Windows Companion & VPS Gateway)

Skill terpadu untuk arsitektur, sekuriti, build packaging, dan integrasi runtime mumu Windows Desktop Companion (mengonsolidasikan mumu-desktop-delivery, mumu-desktop-project, dan coucou-windows-desktop).
Atribusi & hak cipta mutlak milik Bagas Cihuy (Bagas Saputra).

## 1. Identitas, Desain, dan Workspace
- **Nama Aplikasi:** `mumu` (lowercase). Target Windows 10/11.
- **Mascot & Motion UI:** 100% animasi otentik Coucou Dynamic Island (superellipse `Math.pow(Math.abs(ca), 2/2.7)`, 28 WAV audio cues, solid ink eyes, cursor tracking global via `screen.getCursorScreenPoint()`). Soft organic morphing (stretch, squash, expressive).
- **Workspace Utama:**
  - Desktop source: `/home/ubuntu/coucou-desktop`
  - Web companion: `/home/ubuntu/coucou-companion-web`
  - Upstream reference: `/home/ubuntu/coucou/windows`
  - Unduhan publik: `https://www.jajandigital.web.id/coucou/mumu-desktop-windows-x64.zip`
- **Tampilan & Kontrol:**
  - Floating companion window, toggle instan via `Ctrl + Shift + M`.
  - Autostart Windows via `shell:startup` shortcut tanpa mengaktifkan kendali laptop langsung.

## 2. Batas Keamanan & Model Akses
- **Local Control Guard:** Kendali mouse/keyboard laptop hanya aktif saat sesi lokal dimulai eksplisit dari app mumu (bukan via Telegram/WhatsApp). Stop control harus selalu tampak.
- **Physical Input Interruption:** Gerakan mouse fisik atau ketikan pengguna otomatis menjeda (pause) automasi; wajib explicit Resume.
- **Network Resilience:** Kehilangan koneksi memblokir instruksi baru; koneksi ulang tidak otomatis melanjutkan tanpa konfirmasi. Jangan mematikan paksa proses yang sedang berjalan.
- **Privilege & UAC:** Aksi berisiko/destruktif wajib konfirmasi pengguna; jangan pernah bypass Windows UAC.
- **Pairing & Kredensial:** Single-use owner-approved pairing code, simpan kredensial aman di OS lokal, akses dapat dicabut (revocable). Jangan tanam kredensial server di dalam paket installer publik.
- **Screenshots:** Transmisi screenshot ke model AI hanya diperbolehkan saat kendali aktif dan tidak dijeda; tidak ada default arsip screenshot.
- **Laptop vs VPS Decoupling:** Laptop mati hanya menghentikan client Windows; server VPS Hermes, PM2, dan gateway berjalan 24/7. Sesi server tetap lanjut secara mandiri.

## 3. Matriks Perintah & Routing Eksekusi
- **Routing Lokal:** Kata kunci lokal (`/win <cmd>`, `buka <app>`, `screenshot`, `baterai`, `info laptop`) dieksekusi di Win32 client via child_process/PowerShell.
- **Routing Remote Server:** Kata kunci server (`/sh <cmd>`, `pm2 status`, `uptime`, `df -h`, `catat: <ide>`, query AI umum) dieksekusi di VPS.
- **Fast-Path Shell (sub-150ms):** Perintah sistem terdefinisi (`uptime`, `free -m`, `git status`) langsung dieksekusi via `child_process.execSync` dengan timeout 15s dan batas buffer 512KB tanpa membuang token ke LLM.
- **Autonomous Agent Backend:** Perintah reasoning/pembuatan proyek di-route ke `hermes chat --query-file - -Q --oneshot --continue <session> --create-if-missing --yolo` dengan batas waktu 35s dan `--max-turns 10`. Cegah delegasi rekursif sub-agent untuk interaksi cepat.

## 4. Packaging, Build, & Delivery Gates
- **Packaging di Linux tanpa Wine:** Gunakan `electron-builder --win dir --x64` untuk menghasilkan folder unpacked, lalu kompres ke `.zip`. Jangan panggil target NSIS mentah yang membutuhkan Wine.
- **Verifikasi Konten ZIP:** Selalu pastikan `mumu.exe` dan `resources/app.asar` ada di dalam arsip sebelum dipublikasikan.
- **Asynchronous IPC Listeners:** Di Electron CommonJS (`.cjs`), selalu deklarasikan listener `ipcMain.handle` sebagai `async (event, raw) => ...` saat ada `await`. Jalankan `node -c src/*.cjs` sebelum build asar.
- **Tauri to Electron Bridge:** Sediakan shim `window.__TAURI_INTERNALS__` di `preload.cjs` (`invoke`, `transformCallback`, `metadata`) yang memetakan ke `ipcMain.handle('tauri:invoke')`.
- **Public Binary Whitelist:** Pastikan berkas installer publik di-whitelist di reverse proxy (`privacy-boundary.js` `isPublic`) agar unduhan tidak terblokir HTTP 401.
- **Child Process EPIPE Guard:** Selalu pasang handler `child.stdin.on('error', () => {})` untuk mencegah crash node jika child process exit sebelum pipe tertutup.
