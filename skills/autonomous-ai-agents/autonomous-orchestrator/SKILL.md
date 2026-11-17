---
name: autonomous-orchestrator
description: Spawn sub-agents for complex or noisy technical tasks.
version: 1.2.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [orchestration, sub-agents, delegation, parallel-execution]
---

# Autonomous Orchestrator (Mandor dan Kuli)

Atur delegasi via `delegate_task` untuk tugas panjang, debugging ruwet, skrip masif, atau kerja berulang yang akan mengotori chat utama. Versi lengkap (contoh, alasan, detail): `references/full-guide.md`.

## Kapan mendelegasikan
- **Default proaktif:** tugas teknis (coding, debugging, audit, optimasi, perancangan, dokumen/skrip, penelusuran bercabang) dipecah ke sub-agent paralel, minimal 1 Pelaksana + 1 QC Pengawas. Maks `delegation.max_concurrent_children` (3) per batch; batch yang melebihi batas ditolak utuh, jadi pecah dulu.
- **Jawab langsung** hanya untuk obrolan, klarifikasi santai, cek status 1 baris, atau konfirmasi arahan ke Mas Bagas.
- **Jangan delegasikan** diagnosis awal yang bisa Mandor tuntaskan dalam <= 5 tool call, atau tugas yang butuh interaksi pengguna.

## Hierarki 3 generasi
1. **Mandor (induk/GM):** terima mandat Mas Bagas, jaga Pre-Task Gate dan budget resource, orkestrasi Anak/Cucu, verifikasi bukti artefak sebelum lapor.
2. **Anak (role `orchestrator`):** `🧠 Si Pintar` (riset kausal, arsitektur), `⚡ Si Eksekutor` (lapangan, service, pimpin kuli), `🛡️ Si Pengawas` (mencatat celah/missed secara independen; tanpa wewenang melooping eksekusi). Memecah sasaran makro jadi tugas Cucu.
3. **Cucu (role `leaf`, ephemeral):** `🔍 Analis` (log, potongan kode, kueri), `⚡ Kuli` (tes, patch terisolasi, curl), `🛡️ QC` (byte gambar, status HTTP, artefak disk). Lahir saat dipanggil, setor bukti, selesai.

Mode: forum/thread = sekuensial bergantian agar konteks utuh dan tanpa race condition; DM = paralel di latar, satu laporan terstruktur berbukti biner.

## Kontrak tugas sub-agent
- Sub-agent tidak membaca chat: sematkan path absolut, nama fungsi, aturan desain, dan batas keamanan ("jangan sentuh database/production") di `context`.
- **Zero-decision & bounded:** arsitektur diputuskan induk; child menerima satu artefak konkret, <= 3 berkas utama, kriteria biner, 4–6 tool call, tulis berkas di langkah awal; gagal → lapor fakta biner, jangan looping eksplorasi. Batas di prompt bukan timeout runtime: kecilkan unit kerja agar child selesai dalam hitungan menit.
- **Isolasi berkas (gitai/Scion):** child hanya mengedit berkas yang ditugaskan; dua child tidak menyentuh berkas yang sama dalam satu batch; Mandor menggabungkan patch bersinggungan secara berurutan (compare-and-swap).
- Patuhi `/home/ubuntu/STANDAR_KERJA_DAN_INTEGRITAS_BAGAS.md`: bukti dulu baru lapor, dilarang overclaim, uji visual di browser riil.
- Sub-agent mewarisi model induk (`delegation.model/provider` kosong); profil `~/.hermes/profiles/<nama>/` bukan sub-agent. Sebut nama model hanya setelah satu `curl` nyata ke endpoint provider. QC idealnya model beda keluarga; ganti model QC hanya setelah diuji nyata.

## Setelah child selesai
- Laporan diri bukan bukti: periksa status runtime, exit reason, diff, output mentah; jalankan tes integrasi/regresi pada hasil gabungan. Hasil `max_iterations`, `interrupted`, atau tes gagal = parsial. Bila gagal, bedakan cacat implementasi dari fixture dan karantina hunk worker yang bermasalah saja; jangan revert/reset seluruh berkas di worktree kotor.
- Mode background: kerjakan jalur independen lalu akhiri giliran; jangan polling transcript.
- Layanan persisten diluncurkan Mandor (`pm2 start <script> --name <n> --cwd <dir>` + `pm2 save`, atau systemd) lalu cek listener (`ss -ltnp`); proses latar child mati bersama child.
- Child gagal karena provider: baca `~/.hermes/cache/delegation/live/<deleg_id>/task-N.log`; untuk 429/503 jangan kirim ulang ke model yang sama — ambil alih atau pecah tugas.
- Notifikasi `bot_mode_dm.py` terpotong padahal exit 0: baca receipt `<target_profile_home>/runtime/bot_live_delivery/<delivery_id>.json` (field `reply`, status `settled`).

## Laporan progres ke Mas Bagas
Tiap pulse multi-langkah, bahasa awam: `STATUS: SEDANG BEKERJA | SELESAI | TERBLOKIR`, `Sedang dikerjakan:` tindakan + target konkret, `Sudah selesai:` hasil nyata, `File yang diubah:` path atau `belum ada`, `Hasil tes:` bukti atau `belum dijalankan`, `Sisa pekerjaan:` langkah tersisa.
- Dilarang progress bar/persentase/nama fase/identitas agen tanpa pekerjaan nyata. Agen macet → `TERBLOKIR` + durasi, hentikan atau ambil alih.
- Jangan menutup tugas di tiap hasil parsial atau minta izin ulang setelah implementasi disetujui; serahkan satu laporan akhir changed/unfinished/tests/challenges. Batas runtime → catat checkpoint yang bisa dilanjutkan tanpa discovery ulang.
- "gimana"/"lanjut" = minta pulse enam field dari status nyata (path, PID, port, tes terakhir).
- Hemat anggaran iterasi: gabungkan discovery (port, pm2, ingress, routing) dalam sedikit perintah; kirim pulse sebelum anggaran habis.
- Bila diminta melihat kerja live, tampilkan artefak nyata (alat aktif, file/perintah, diff, exit status, lifecycle sub-agent); format rapi bukan pengganti observabilitas.
- Telegram: status armada (jumlah pekerja, peran, sasaran) diperbarui in-place (`edit_message`, jeda >= 1,5 s); cek armada via `/agents` atau `/tasks`.

## Runtime & konfigurasi
- Health check pilar: `/home/ubuntu/check-5pilar.sh` atau `./check.sh` di root pilar (`website-pbj`, `kasir-bangunan-app`, `dasbor-jajan-digital`, `sputarball`).
- Tugas multi-step: baca/perbarui `build_tracker.json` di root proyek sebelum mulai dan setelah milestone teruji.
- `config.yaml` terproteksi; ubah via CLI: `hermes config set delegation.reasoning_effort medium` (hindari `high` untuk leaf; terukur ~41% lebih cepat) dan isi minimal satu `delegation.fallback_providers` (mis. `custom:nbgate`).
