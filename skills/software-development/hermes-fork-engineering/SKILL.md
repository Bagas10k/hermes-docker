---
name: hermes-fork-engineering
description: Use when creating or modifying a personal fork of Hermes.
version: 1.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, fork, git, tui, installer, build, testing]
    related_skills: [hermes-agent, test-driven-development, github]
---

# Hermes Fork Engineering & Custom Delivery

## When to Use
- Mengembangkan, mengklon, atau memodifikasi fork pribadi dari repositori Hermes Agent.
- Menambahkan atau merombak komponen visual antarmuka TUI Ink (seperti Live Workspace Panel gaya OpenCode).
- Menyiapkan kontrak skrip instalasi kustom (`./install.sh`) agar dapat dipasang langsung dari GitHub klon tanpa merusak instalasi host.

---

## 1. Isolasi Lingkungan & Keamanan Mutlak
- **Pantang Sentuh Instalasi Aktif:** Jangan pernah mengubah repositori bawaan host di `~/.hermes/hermes-agent` atau venv aktifnya. Seluruh pengembangan fork wajib dilakukan pada direktori terisolasi (misal: `~/hermes-bagas`).
- **Pembersihan Rahasia Git:** Pastikan `.env`, `auth.json`, `state.db`, dan berkas `.db` lainnya selalu terabaikan di `.gitignore` sebelum melakukan push perdana ke remote privat.
- **Remote Naming Invariant:**
  - `origin`: repositori fork milik pengguna (misal: `git@github.com:Bagas10k/hermes-bagas.git`).
  - `upstream`: repositori resmi Nous Research (`https://github.com/NousResearch/hermes-agent.git`).

---

## 2. Kontrak Installer Klon Mandiri (Linux-First)
Ketika fork dipasang via `git clone <repo> && ./install.sh`:
1. **Dynamic Origin Detection:** Skrip `./install.sh` di root wajib mendeteksi remote `origin` dari klon lokal secara dinamis (`git remote get-url origin`) dan mengekspornya ke `HERMES_REPO_URL`. Ini mencegah installer otomatis kembali ke repo resmi Nous Research.
2. **Preserve Active Branch:** Jika argumen `--branch` tidak disertakan, installer wajib membaca branch aktif (`git symbolic-ref --quiet --short HEAD`) agar pengembang yang menguji branch fitur tidak diam-diam di-reset ke `main`.
3. **Dokumentasi & Klaim Platform Jujur:** Jangan mengklaim platform "verified" (misal: Linux x86_64, Windows, macOS) jika belum melewati pengujian instalasi bersih secara utuh (*clean-host release gate*). Nyatakan sebagai "verification target" atau "developed Linux-first".

---

## 3. Alur Kerja Modifikasi TUI Ink (React/TypeScript)
1. **Prasyarat Build:**
   - Jalankan `npm run build:ink --workspace ui-tui` sebelum Vitest mengimpor `@hermes/ink`.
2. **TDD Unit Testing dengan Mock Streams:**
   - Gunakan `PassThrough` dari `node:stream` sebagai pengganti `stdout`/`stdin` untuk `renderSync` Ink dalam tes.
   - Panggil `view.unmount()` dan `view.cleanup()` di akhir tes agar tidak memicu unhandled rejection pada `writeDiffToTerminal`.
3. **Kepatuhan Linting & Import Sorting:**
   - Proyek menggunakan `eslint-plugin-perfectionist/sort-imports`.
   - Urutan impor lokal harus tepat secara alfabetis (misal: `./liveWorkspacePanel.js` harus mendahului `./loopBar.js`).
   - Jangan tinggalkan impor tak terpakai (`unused-imports/no-unused-imports`).
4. **Verifikasi Pre-Commit:**
   - Pastikan path `ruff` dari test environment tersedia di `PATH` saat commit jika hook Lefthook memerlukannya:
     ```bash
     TEST_BIN="$(find ~/.hermes/installs -path '*/venv/bin' | grep test-environment | head -n 1)"
     PATH="$TEST_BIN:$PATH" git commit -m '...'
     ```

---

## 4. Jebakan Verifikasi Render TUI (Wajib Dibaca Sebelum Klaim PASS)
1. **`dist/entry.js` bukan renderer mandiri.** Berkas itu klien WebSocket ke gateway. Menjalankan `node ui-tui/dist/entry.js` di PTY kosong hanya menghasilkan escape sequence terminal + spinner braille koneksi (beberapa ratus byte, tanpa teks layout). Output PTY yang hanya berisi escape/spinner adalah sinyal harness salah, BUKAN bukti komponen ter-render. Klaim "PTY render PASS" dari bukti ini adalah overclaim.
2. **`patchConsole: false` wajib.** Ink menambal `console` secara default, sehingga `console.log` di dalam probe hilang dan probe yang berfungsi tampak kosong. Selalu kirim `renderSync(..., { patchConsole: false, stdout, stdin })`.
3. **Pisahkan dua tingkat klaim.** Render komponen (`renderSync` + `PassThrough`, cetak frame hasil `stripAnsi`) membuktikan komponen itu sendiri. Render `AppLayout` penuh butuh gateway aktif dan merupakan klaim terpisah — jangan gabungkan.
4. **Panel yang ter-mount belum tentu berisi data.** Integrasi layout yang hanya mengirim `status`/`theme` menghasilkan panel kosong. Wajib derivasi data nyata:
   - *Active Tool:* Ambil elemen terakhir dari `turnStore.tools` (`tools.at(-1)`).
   - *Last Command & Exit Code:* Ambil baris proses terbaru dari `useProcessRows(now)`, periksa `exitCode` hanya saat status bukan `running`.
   5. **Uji PTY end-to-end hanya sah bila harness gateway-nya hidup.** `tests/e2e/core/terminal/_pty.py::PtyHermes.wait_ready()` menunggu UI masuk raw mode; klien `entry.js` baru sampai ke sana setelah `bootstrapLocalGateway()` (`gateway_bootstrap.py --start`) memberi grant WebSocket. Bila bootstrap gagal, keduanya berhenti dengan `timed out after 120s waiting for the UI to take the terminal (raw mode)`. **Sebelum menyalahkan kode sendiri, jalankan tes TUI milik upstream (`test_terminal_transcript_pty.py::...[tui-turns]`).** Bila tes upstream gagal identik, itu batas lingkungan, bukan regresi fork — catat di docstring tes dan jangan klaim PASS.
   6. **`hermes_cli/tui_dist/` adalah artefak build dan di-.gitignore.** Menyalin `ui-tui/dist/entry.js` ke sana membuat `_find_bundled_tui()` melewati `npm install`/rebuild saat peluncuran, tetapi berkas itu tidak ikut ter-commit — jangan kira ia tersedia setelah clone bersih.
   7. **Claim hijau hanya dari bukti segar.** Setiap kali `ui-tui/src`, `install.sh`, atau `tests/` berubah, jalankan ulang gate sebelum menyatakan PASS; commit lewat hook Lefthook butuh `ruff` di `PATH`.
   - *Subagents:* Filter hanya status `running` dan `queued` dari `agentRoster`.
5. **Responsiveness Guard:** Hanya pasang panel samping jika kolom terminal mencukupi (`cols >= 110`). Pada layar sempit, pertahankan fallback ke `ToolTrail` inline bawaan.
6. **E2E PTY Test Harness Invariants:**
   - Saat menulis tes PTY untuk TUI (`tests/e2e/core/terminal/...`), **wajib** sertakan `pytest.mark.live_system_guard_bypass`. Tanpa marker ini, fixture `live_system_guard` internal akan mencegat dan memblokir proses PTY hingga timeout.
   - Hitung kedalaman path ke `REPO_ROOT` secara akurat (`parents[4]` untuk berkas di `tests/e2e/core/terminal/`). Kesalahan offset membuat `@pytest.mark.skipif` terpicu tanpa disadari (silent skip).
   - Inisialisasi TUI penuh lewat `PtyHermes` membutuhkan proses Python CLI meluncurkan Node subprocess gateway dan menyelesaikan handoff raw-mode terminal (`wait_ready()`). Alokasikan batas waktu pengujian minimal 180s–300s jika menjalankan siklus end-to-end lengkap.
   - **Sandbox Directory Isolation:** `PtyHermes` memvalidasi bahwa path direktori sementara sandbox **tidak boleh** berada di dalam `~/.hermes` (`assert operator not in (self.hermes_home.resolve(), ...)`). Jika `TMPDIR` di host disetel ke dalam subfolder `.hermes` (misal `~/.hermes/cache/scratch`), instansiasi `tempfile.TemporaryDirectory()` tanpa parameter eksplisit akan memicu AssertionError seketika. Selalu lewatkan `tempfile.TemporaryDirectory(dir='/tmp')`.
   - **TUI Launcher Rebuild Check (`_tui_need_rebuild`):** Saat CLI meluncurkan `--tui` di checkout Git, CLI memanggil `_tui_need_rebuild()`. Jika paket prebuilt `hermes_cli/tui_dist/entry.js` tidak ada dan cache stempel source mendeteksi perubahan, launcher akan otomatis menjalankan `prepare_launch_dependencies()` (termasuk verifikasi npm dependencies dan re-bundle) sebelum menyerahkan kontrol ke proses Node.js. Salin bundle hasil build ke `hermes_cli/tui_dist/entry.js` untuk bypass instan saat pengujian.
   - **Interactive Terminal Reset Sequence & Telemetry Prompt:** Pada startup terminal interaktif (`isatty() == True`), CLI mengirimkan sequence reset mode terminal (`_TERMINAL_INPUT_MODE_RESET_SEQ` sepanjang 154 byte). Selain itu, pastikan konfigurasi telemetry (`telemetry.shared_metrics.offer_version`) sudah terisi di `config.yaml` sandbox via `write_hermes_home`, jika tidak, CLI akan menampilkan dialog curses interaktif `Help improve Hermes?` yang memblokir proses PTY selamanya.
   - **TUI Client Gateway Dependency:** `entry.js` yang diluncurkan oleh Node.js bukan standalone server melainkan WebSocket client yang memanggil `bootstrapLocalGateway` (`gateway_bootstrap.py --start`) via child process untuk memastikan daemon backend aktif sebelum me-render interface utama. Uji mandiri tanpa gateway yang siap akan tertahan pada fase handoff socket.
   - **Cleanup:** Gunakan `term.close()`, bukan `term.kill()` (metode `kill` tidak ada di kelas `PtyHermes`).
