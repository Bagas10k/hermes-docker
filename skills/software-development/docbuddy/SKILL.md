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
# 1. Adopsi template ONEFREQ yang belum ada (jumlah mengikuti versi; tidak menimpa)
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

## Mengemas Adaptor Dokumentasi yang Dipakai Ulang
1. Bedakan repo **templat** dari repo **proyek tujuan**: jangan klaim fakta, fitur, atau hasil runtime proyek tujuan sudah ada ketika paket masih berstatus unadapted. Baca isi arsip sumber tanpa menjalankannya; tempatkan skema/dokumen sumber di ruang nama terpisah (misalnya `pia/` dalam repo adaptor, `.pia/` dalam proyek tujuan), bukan menyalin `AGENTS.md` atau `CLAUDE.md` sumber di atas kontrak yang sudah berlaku.
2. Sediakan pratinjau pemasangan sebelum mode tulis; tolak konflik berkas dan tujuan berupa symlink **sebelum** menyalin apa pun. Uji dengan fixture sintetis: pratinjau tidak mengubah target, pemasangan mempertahankan berkas lama, pemasangan ulang ditolak. Ini mencegah penimpaan kontrak repo yang tidak terlihat dari instruksi “copy template”.
3. Validasi tautan lokal, ID dokumen unik, dan referensi lintas dokumen dengan uji negatif terfokus. Bedakan *template belum diadaptasi* dari dokumen terverifikasi: lulus integritas Markdown bukan bukti kebenaran proyek. Jika validator hanya mengindeks YAML frontmatter, nyatakan secara eksplisit bahwa ID pada tabel Markdown belum tercakup; batasi tautan ke akar dokumentasi bila validator mengklaim tidak membaca keluar area itu.
4. Sebelum publikasi, cek asal dan lisensi setiap bahan sumber; paket tanpa lisensi eksplisit jangan diberi lisensi baru secara sepihak. Jika pemilik telah mengizinkan repo tetapi tidak menentukan visibilitas, pilih privat dahulu atau minta keputusan visibilitas. Setelah tes lokal, buat/push repo lalu **baca balik** URL, visibilitas, commit dan README remote; jika belum terbit, laporkan lokal selesai tetapi publikasi belum selesai.

## Mengisi Dokumen ONEFREQ dari Bukti Repo (jalur manual)
Saat `docbuddy propose` tidak dipakai atau tidak ada CLI, empat berkas tetap harus terisi: `PROJECT_BRIEF.md`, `ARCHITECTURE.md`, `VERIFICATION.md`, `CURRENT_STATE.md`. Urutannya:

1. **Gali dulu, tulis belakangan.** Baca `ls -la` root, pemetaan route (`grep -nE "app\.(get|post|put|delete|use)\(" server.js`), daftar route router terpisah, `require(...)` unik, dan baris `listen(`/port. Satu sesi discovery 3–5 perintah jauh lebih murah daripada bolak-balik menebak.
4. **Cari adapter dokumen sumbernya sebelum menulis apa pun.** Adapter kerap berupa paket terpisah (zip di `~/.hermes/cache/documents/`, repo `pia/`, atau folder `.pia/` di proyek tujuan) dengan panduan wajib bernama `PROJECT-ADAPTER-PROMPT.md` (fase discovery → interogasi produk → pemetaan → dokumen → validasi → handoff). Jalankan `find /home/ubuntu -maxdepth 4 -iname '*adapter*' -not -path '*/node_modules/*'` dan baca panduan itu **sebelum** mengisi dokumen. Paket adapter sering berupa zip di cache dokumen — daftar isinya dengan `python3 -c "import zipfile; [print(i.file_size, i.filename) for i in zipfile.ZipFile('<paket>.zip').infolist()]"` lalu baca berkas panduannya tanpa mengekstrak ke proyek. Membaca hanya dokumen turunannya (`PROJECT-FACTS.md`, `DATA-API.md`, `PRD.md`) lalu menulis `.onefreq/` dengan gaya sendiri = melanggar skemanya: ID tidak tertelusur, aturan bisnis terduplikasi di dua tempat, dan fase interogasi produk terlewat. Dokumen `.pia/docs/` adalah kebenaran proyek; `.onefreq/` cukup merujuk, bukan mengulang inventaris. Bedakan juga isi paket adapter (masih `docs/` placeholder "not yet initialized") dari `.pia/docs/` di proyek tujuan yang sudah terisi — keberadaan keduanya bukan bukti bahwa adaptasi telah mengikuti protokol.
3. **Buktikan yang bisa dibuktikan sekarang**: `curl -s -o /dev/null -w '%{http_code}'` ke endpoint health, skrip test repo (catat exit code + jumlah uji lulus), dan hitung baris tabel DB read-only. Ubah baris `UNSET` menjadi `PASS` hanya dengan output nyata.
4. **Beri label tiap klaim dengan kosakata adapter yang berlaku**, bukan kosakata karangan sendiri: `observed` (terbukti dari kode/perintah), `specified` (dititahkan pemilik, belum dikode), `proposed` (usulan), `assumed`/`unknown`. Pemetaan `CONFIRMED`/`INFERRED`/`PROPOSED`/`UNKNOWN` hanya sah bila eksplisit dinyatakan sebagai padanan. Tabrakan kosakata membuat dokumen tidak bisa diaudit balik ke sumbernya, dan pakai ID stabil adapter (`REQ-*`, `FEAT-*`, `PAGE-*`, `DEC-*`) alih-alih membuat ID baru — dokumen tanpa ID tidak bisa ditelusuri lintas berkas.
5. **Uji batas kepercayaan, bukan hanya keberadaan route.** Cek auth dari sisi ingress dengan permintaan tanpa sesi (`POST` ke route destruktif) — hasilnya menentukan apakah menyebut “aman” boleh. Tulis konsekuensinya dalam bahasa operasional (mis. “port 3100 setara akses shell”).
6. **Catat dependensi keras di `ARCHITECTURE.md`**: upstream yang bila mati mematikan sebagian fitur, manifest dependensi yang hilang, symlink `node_modules`, dan `pm2 describe` → `exec cwd` yang tidak cocok dengan root repo.
7. **Tutup dengan audit integritas**: `rg UNSET .onefreq/<empat berkas>` harus kosong, lalu isi `build_tracker.json` dengan `status`, `done`, `next`, `risks` yang benar-benar terjadi.

Pitfall yang mahal waktu:
- **`write_file` menolak menimpa berkas yang belum dibaca penuh di sesi itu.** `read_file(limit=5)` tidak cukup; baca seluruh berkas (atau `limit=2000`) dulu, baru tulis — atau pakai `patch` untuk edit bertarget.
- **`patch` bisa berakhir non-exact** (mode block-anchor) dan menyisakan judul lama di atas judul baru, atau terpotong sebelum penutupnya. Setelah setiap patch pada Markdown besar, baca ulang berkas dan rapikan sisa duplikat dengan patch kecil berikutnya.
- **Hemat iterasi.** Empat berkas dokumentasi + tracker bisa menghabiskan seluruh anggaran tool call. Siapkan isi tiap berkas utuh di nalar, lalu tulis satu per satu; jangan menyelipkan uji verifikasi baru di tengah penulisan dokumen.
- **`UNSET` pada template bukan izin mengarang.** Bagian yang tidak bisa dibuktikan tetap `unknown` beserta tabel “unknowns dan discovery queue”, bukan diisi tebakan yang enak dibaca.
- **Mandat pemilik mengalahkan prioritas teknis pribadi.** Bila pemilik sudah menetapkan urutan (mis. “langsung eksekusi Fase 1 mode kanvas”), jangan menyusun ulang rencananya menjadi “fondasi dulu, fitur nanti”. Sampaikan risiko fondasi sebagai **langkah nol di dalam** urutan yang ia tetapkan (salinan berkas bertanggal / `git init` sebelum sentuhan kode pertama), bukan sebagai penundaan fiturnya. Kontrak AGENTS menyatakan urutan otoritas: instruksi pengguna terkini > kontrak produk/ADR > bukti repo > usulan.

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
