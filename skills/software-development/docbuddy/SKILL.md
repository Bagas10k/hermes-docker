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
Jangan menganggap setiap proyek wajib mengadopsi seluruh paket. Tawarkan adopsi hanya saat cocok dengan tujuan pemilik proyek; paket terdiri dari `AGENTS.md`, `CLAUDE.md`, dan 15 file Markdown dalam `.onefreq/`.

## CLI Commands
Jalankan dari clone repositori DocBuddy (Python 3.11+, tanpa dependensi pihak ketiga):
```bash
# Salin template yang belum ada; file proyek yang sudah ada dipertahankan
python docbuddy.py adopt <path_proyek>

# Usulkan pengayaan berdasarkan manifest; tampilkan diff dan simpan proposal
python docbuddy.py propose <path_proyek> --proposal /tmp/docbuddy-proposal.json

# Terapkan hanya setelah meninjau proposal
python docbuddy.py apply <path_proyek> --proposal /tmp/docbuddy-proposal.json
```

## Prosedur Penerapan pada Repositori
1. Jelaskan tujuan dengan jujur: DocBuddy menyiapkan konteks dokumentasi untuk developer/AI coding agent; ia tidak membuat kode aplikasi atau berjalan di background.
2. Jalankan `python docbuddy.py adopt <project>` untuk menyalin hanya file template yang belum ada. Perintah ini tidak memindai manifest; jangan timpa atau gabungkan otomatis file milik proyek.
3. Minta pemilik mengisi tujuan dan batasan bisnis di `.onefreq/PROJECT_BRIEF.md`; jangan menyimpulkan dari nama folder atau dependency.
4. Jalankan `propose <project> --proposal <file>` dan tinjau diff. Pemindaian manifest hanya mengusulkan pembaruan untuk `.onefreq/ARCHITECTURE.md` dan `.onefreq/VERIFICATION.md`.
5. Jalankan `apply` hanya setelah pemilik menyetujui isi proposal. Proposal basi harus dibuat ulang karena pemeriksaan hash menolak target yang berubah.
6. Verifikasi setelah pekerjaan: jalankan `python -m unittest discover -s tests -v`, uji `adopt` pada proyek sintetis kosong dan proyek yang punya file sendiri, cek jumlah/path hasil, dan buka README remote setelah publikasi.

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
