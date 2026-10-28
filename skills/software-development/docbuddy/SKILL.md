---
name: docbuddy
description: Use when adopting, proposing, or updating evidence-based repository documentation via DocBuddy CLI.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [docbuddy, onefreq, documentation, manifest-scanner, architecture, verification, offline]
    related_skills: [cabinet-discipline-and-anti-overtesting, structured-project-execution, otak-koding]
---

# DocBuddy & ONEFREQ Documentation Workflow

Kakas baris perintah deterministik berbasis bukti untuk menghasilkan dan memperbarui dokumen proyek `.onefreq/ARCHITECTURE.md` dan `.onefreq/VERIFICATION.md` tanpa API AI eksternal.

## Kapan Digunakan
- Memulai proyek baru atau menata dokumentasi proyek yang sudah ada.
- Menyediakan kontrak kanonik `AGENTS.md` agar seluruh agen (Hermes, Claude Code, Cursor, Codex) memahami batasan dan arsitektur repositori.
- Memperbarui snapshot arsitektur dan kontrak uji setelah penambahan dependensi/framework baru.

## Alur Kerja CLI yang Terverifikasi
Untuk proyek dalam SOP build Bagas, kontrak `AGENTS.md` + `.onefreq/` wajib ada sebelum perubahan kode. Pada discovery, jika salah satunya belum ada, jalankan `docbuddy-adopt .` dari root proyek; wrapper hanya menyalin template yang belum ada tanpa menimpa berkas existing. Bila wrapper tidak tersedia, `docbuddy adopt .` adalah bootstrap setara. Setelah adopsi, baca dan sesuaikan kontrak dengan brief dan batas proyek. Paket mencakup `AGENTS.md`, `CLAUDE.md`, dan Markdown di `.onefreq/`. Adopsi tidak meng-enrich file existing; untuk itu jalankan `propose`, tinjau diff/scope, lalu `apply` hanya setelah persetujuan eksplisit.

## CLI Commands
Pada host ini CLI berada di `~/.local/bin/docbuddy`; wrapper berada di `~/.local/bin/docbuddy-adopt` (pastikan direktori tersebut ada di `PATH`). Di host/repo lain, gunakan entrypoint instalasi yang benar atau `python3 <path-ke-docbuddy>/docbuddy.py`. Jalankan dari terminal:
```bash
# 1. Adopsi template (menyalin 17 file template ONEFREQ yang belum ada)
docbuddy adopt <path_proyek>

# 2. Usulkan pengayaan manifest (.onefreq/ARCHITECTURE.md & VERIFICATION.md)
docbuddy propose <path_proyek> --proposal /tmp/docbuddy-proposal.json

# 3. Terapkan proposal setelah ditinjau
docbuddy apply <path_proyek> --proposal /tmp/docbuddy-proposal.json

# 4. State Tracking (Pencegah Amnesia Konteks pada Build Panjang)
docbuddy state <path_proyek>
docbuddy state <path_proyek> --status IN_PROGRESS --goal "Implementasi fitur X" --slice "Modul A selesai" --next "Lanjut modul B" --blocker "Menunggu approval Mas Bagas"

# 5. ADR Logging (Decision Provenance)
docbuddy adr <path_proyek> --title "Pilihan Database Locking" --decision "lockForUpdate" --why "Mencegah race condition kasir" --alternatives "Timestamp"

# 6. Report Generation (Engineering Execution Report v2.0)
docbuddy report <path_proyek> --status ACCEPTED --deployment STAGING_TESTED

# 7. Verification Contract Runner
docbuddy verify <path_proyek>
docbuddy verify <path_proyek> --run
```

## Prosedur Penerapan pada Repositori
1. Jelaskan tujuan dengan jujur: DocBuddy menyiapkan konteks dokumentasi untuk developer/AI coding agent; ia tidak membuat kode aplikasi atau berjalan di background.
2. Pada discovery awal, jika `AGENTS.md` atau `.onefreq/` belum ada, jalankan `docbuddy-adopt .` dari root repo (fallback `docbuddy adopt .`) sebelum edit kode. Keduanya hanya menyalin template yang hilang dan mempertahankan berkas yang sudah ada; verifikasi hasil dan baca kontrak. Pengayaan bukan bagian dari adoption: `docbuddy propose <project> --proposal <file>` menampilkan diff; tinjau diff/scope, lalu `docbuddy apply` hanya setelah persetujuan eksplisit. Jangan gunakan wrapper/otomasi yang menyembunyikan diff atau langsung menerapkan proposal.
3. Minta pemilik mengisi tujuan dan batasan bisnis di `.onefreq/PROJECT_BRIEF.md`; jangan menyimpulkan dari nama folder atau dependency.
4. Jalankan `propose <project> --proposal <file>` dan tinjau diff. Pemindaian manifest hanya mengusulkan pembaruan untuk `.onefreq/ARCHITECTURE.md` dan `.onefreq/VERIFICATION.md`.
5. Terapkan dengan `apply` hanya jika diff sudah ditinjau dan ada persetujuan eksplisit: konfirmasi Mas Bagas untuk perubahan bermakna, atau mandat tugas yang secara jelas mencakup pembaruan rutin tersebut. Proposal basi harus dibuat ulang karena pemeriksaan hash menolak target yang berubah.
6. Verifikasi integritas paket DocBuddy (bukan test suite repo target) dengan `python -m unittest discover -s tests -v` dari root checkout DocBuddy. Uji `adopt` pada fixture sintetis kosong dan fixture yang sudah memiliki file; bandingkan byte file existing sebelum/sesudah. Periksa jalur dan konten template hasil. Jika proyek diterbitkan, baca kembali README remote.

## Pemeriksaan Nama, Klaim, dan Rilis
- Saat mengganti nama proyek, periksa konsistensi nama pada nama berkas, modul/import Python, identitas CLI/help, contoh README, dan URL remote; pertahankan nama paket template sumber hanya jika memang masih menjadi bagian produk dan jelaskan asalnya.
- Sebelum menyatakan nama lama sudah hilang, cari seluruh berkas yang dikelola, lalu verifikasi pohon berkas remote dan README yang diterbitkan. Pemeriksaan tag tidak membuktikan isi berkas bersih.
- Bedakan eksplisit adopsi template, pemindaian, usulan, persetujuan, dan penerapan. Jangan menyebut `adopt` otomatis memindai/mengisi dokumen jika implementasi menjalankan langkah itu terpisah.
- Jelaskan fungsi produk dengan bahasa awam sebelum daftar fitur; jangan membiarkan pembaca menyangka alat dokumentasi menghasilkan aplikasi, memantau repo, atau menyunting semua Markdown.
- Laporan harus menyebut hasil yang benar-benar diverifikasi dan cakupan cek; jika pemeriksaan penuh gagal atau terlewat, ungkapkan sebelum menyebut rilis selesai.

## Batasan & Prinsip
- `adopt` menyalin 17 file template yang belum ada dan mempertahankan file tujuan yang sudah ada; ia bukan langkah pemindaian.
- `propose` hanya menghasilkan diff/proposal untuk `.onefreq/ARCHITECTURE.md` dan `.onefreq/VERIFICATION.md`; ia tidak mengubah target.
- `apply` hanya menerima dua target tersebut dan menolak proposal jika target berubah sejak proposal dibuat.
- Jangan mengklaim semua direktori rahasia atau isi repo tidak dibaca berdasarkan pengecualian terbatas; sebutkan hanya pola yang benar-benar diverifikasi dalam implementasi.
- Template ONEFREQ punya asal/identitas sendiri. Jangan menghapus atribusi atau mengubah path `.onefreq/` saat mengganti nama produk kecuali migrasi format memang diminta.
