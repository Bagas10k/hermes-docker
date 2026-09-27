---
name: multiagent-worktree-orchestration
description: "Run parallel coding agents in git worktrees safely."
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [multi-agent, git-worktree, parallel-execution, ade, orca-evolution, gatekeeper]
    related_skills: [autonomous-orchestrator, agent-intervention-dag-splicing, subagent-concurrency-memory-bounds]
---

# Multi-Agent Git Worktree Fleet Orchestration

Orkestrasi armada sub-agen koding paralel berbasis Git Worktrees terisolasi dengan deduplikasi dependensi, pemantauan kausalitas ketergantungan tugas, dan gerbang verifikasi pengujian otomatis.

## When to Use
- Menjalankan 2 atau lebih sub-agen koding independen secara paralel pada satu repositori Git tanpa konflik branch.
- Mencegah tabrakan file atau race condition saat beberapa agen mengedit basis kode yang sama.
- Menghindari pemborosan disk dan memori akibat duplikasi dependensi (`node_modules` atau `target/`).
- Menggantikan proses manual review konvensional dengan gerbang verifikasi invarian otomatis (*Autonomous Quality Gate*).

Don't use for:
- Tugas non-koding atau pembacaan berkas murni (gunakan `delegate_task` standar tanpa worktree).
- Satu tugas sekuensial tunggal yang tidak memerlukan isolasi cabang.

## Quick Reference
```bash
# 1. Buat worktree terisolasi di path sementara
git worktree add -b fleet/<task-id> /tmp/kanvas-worktrees/<task-id> main

# 2. Hubungkan dependensi bersama (deduplikasi cache Node.js & Rust)
ln -s /path/to/main/node_modules /tmp/kanvas-worktrees/<task-id>/node_modules
ln -s /path/to/main/target /tmp/kanvas-worktrees/<task-id>/target

# 3. Jalankan verifikasi invarian sebelum merge
npm test --prefix /tmp/kanvas-worktrees/<task-id>
# atau pada repositori Rust:
cargo test --manifest-path /tmp/kanvas-worktrees/<task-id>/Cargo.toml --quiet

# 4. Semi-otonom merge (hanya setelah status READY_TO_MERGE) dan bersihkan worktree
git merge --no-ff -m "[FLEET] Merge terverifikasi fleet/<task-id>" fleet/<task-id>
git worktree remove --force /tmp/kanvas-worktrees/<task-id>
git branch -d fleet/<task-id>
```
Rujukan detail arsitektur:
- [Deduplikasi & Protokol Gerbang Mutu](references/deduplication_and_gatekeeper.md)
- [Hermes Cognitive Bridge & Dekomposisi Kausal](references/cognitive_bridge_decomposition.md)

## Procedure
1. **Periksa Status Repositori Induk:**
   Pastikan branch utama berada dalam status bersih (`clean working tree`) sebelum membuat cabang kerja baru.
2. **Alokasikan Worktree Terisolasi:**
   Gunakan direktori kerja sementara di `/tmp/kanvas-worktrees/<task-id>` untuk mencegah polusi pada pohon direktori utama.
3. **Deduplikasi Dependensi via Symlink/Hardlink:**
   Dilarang keras menjalankan instalasi dependensi ulang di setiap worktree baru. Buat tautan simbolik (`symlink`) ke cache dependensi repositori induk: `node_modules` untuk JavaScript/TypeScript atau `target/` (serta variabel lingkungan `CARGO_TARGET_DIR`) untuk repositori Rust. Ini memangkas waktu kompilasi/tes dari puluhan detik menjadi sub-detik (< 0.05s) serta menghemat gigabytes disk.
4. **Delegasikan Sub-Agent ke Ruang Kerja Terisolasi:**
   Tugaskan sub-agent dengan jalur absolut menuju worktree miliknya (`workdir=/tmp/kanvas-worktrees/<task-id>`). Sub-agent bebas memodifikasi file dan menjalankan pengujian lokal.
5. **Eksekusi Gerbang Mutu Invarian (Si Pengawas Gate):**
   Sebelum cabang kerja dinyatakan siap gabung, jalankan 4 lapisan validasi otomatis:
   - Validasi sintaksis/AST parser (exit code 0).
   - Eksekusi unit test deterministik (exit code 0).
   - Audit sanitasi kunci rahasia/kredensial (bebas kebocoran token/kunci).
   - Kepatuhan nol emoji pada kode, log, dan antarmuka.
6. **Otorisasi Semi-Otonom & Pembersihan Atomik:**
   Jika lolos seluruh gerbang mutu, promosikan status cabang menjadi `READY_TO_MERGE`. Jangan melakukan auto-merge buta; wajibkan otorisasi 1-klik manual oleh arsitek manusia (*Semi-Autonomous Verification*). Setelah terkonfirmasi berhasil dimerge, segera hapus direktori worktree dengan `git worktree remove --force` dan hapus branch lokalnya untuk membebaskan inode dan ruang disk.
7. **Dekomposisi Kognitif Otomatis (Cognitive Auto-Planner):**
   Gunakan model penalaran untuk memecah instruksi koding bahasa alami tingkat tinggi menjadi 2-4 sub-tugas terstruktur. Setiap sub-tugas wajib memiliki ID unik, deskripsi goal presisi, array dependensi kausal (membentuk DAG asiklik), serta perintah uji deterministik (`cargo test` atau `npm test`). Jalankan validasi algoritma Kahn sebelum alokasi worktree untuk menjamin graf bebas dari siklus sirkular.
8. **Integrasi Antarmuka Multi-Mode (VS Code Explorer + Docked Parallel Fleet):**
   Alih-alih membangun aplikasi mandiri yang memecah konsentrasi pengguna, integrasikan armada worktree ke dalam antarmuka kerja utama (KANVAS) melalui arsitektur 3 mode kerja:
   - `Mode Naskah`: perumusan PRD, draf ide, dan dokumentasi arsitektur.
   - `Mode Kode / VS Code`: penjelajah berkas nyata di disk (`/api/fs/tree`, `/api/fs/read`, `/api/fs/save`), tab berkas terbuka, nomor baris, pintasan simpan instan (`Ctrl+S`), dan dock kontrol armada paralel di bawah editor.
   - `Mode Chat AI`: area diskusi penalaran model bahasa penuh untuk pendalaman konsep tanpa distraksi.

## Pitfalls
- **The Clone Trap vs Core Mechanism Integration:** Saat pengguna meminta sistem bekerja seperti alat referensi (misal Orca), jangan membuat antarmuka mandiri yang meniru layout alat tersebut secara terpisah. Pengguna menginginkan **mekanisme eksekusinya** (eksekusi paralel terisolasi tanpa tabrakan / zero collision) yang disematkan langsung ke antarmuka utama (KANVAS) dalam bentuk Mode Kode (VS Code-like file access + docked parallel runner).
- **Karakter Petir U+26A1 pada Standar Nol Emoji:** Simbol petir `⚡` (`\u26a1`) terdaftar sebagai simbol/emoji piktorial dalam Unicode. Dalam sistem dengan Doktrin Nol Emoji ketat, penggunaan `⚡` memicu pelanggaran verifikasi. Selalu gunakan teks eksplisit seperti `[ORCA-STYLE PARALEL]` atau kurung siku ASCII murni.
- **Streaming Chunks vs Non-Streaming JSON pada Router Lokal:** Saat memanggil 9Router (`127.0.0.1:20128`) untuk dekomposisi kognitif, kelalaian menyetel `"stream": false` menyebabkan router mengembalikan potongan raw SSE (`data: {"id": ...}`) yang memecahkan `JSON.parse`. Selalu kirimkan `"stream": false` secara eksplisit pada payload dekomposisi terstruktur.
- **Siklus Melingkar pada Rencana AI (LLM Hallucinated Cycles):** Model penalaran terkadang menghasilkan dependensi dua arah (misal A bergantung pada B, dan B bergantung pada A). Wajibkan gerbang validasi topologis (algoritma Kahn) sebelum memicu pembuatan worktree agar proses penjadwalan tidak macet (deadlock).
- **Duplikasi Dependensi Tanpa Symlink:** Menjalankan `npm install` atau `cargo build` di setiap worktree menduplikasi gigabytes data dan menghabiskan batas kuota disk/RAM server. Selalu tautkan `node_modules` atau `target` cache dari repositori induk.
- **Auto-Merge Buta Tanpa Otorisasi Manusia:** Menggabungkan otomatis seluruh cabang yang lolos uji tanpa persetujuan arsitek dapat merusak visi desain atau menghasilkan regresi arsitektur tak terduga. Terapkan doktrin Semi-Otonom: uji otomatis 100%, merge manual 1-klik.
- **Siklus Require Mandiri pada Modul Uji Tiruan (Circular Self-Require):** Saat sub-agent menulis ulang file modul di worktree dan menyematkan `require('./index')` di dalam `index.js`, Node.js mengeksekusi self-require siklis sebelum ekspor terbentuk, memicu `TypeError: not a function` palsu. Pisahkan berkas definisi modul dan berkas skrip pengujian (`test.js`).
- **Mempercayai Laporan Mandiri Agen (Self-Report Bias):** Menganggap kode sub-agent bebas bug hanya dari ringkasan teks. Wajibkan eksekusi unit test langsung dan validasi exit code secara programatis.
- **Ketergantungan Kausal yang Rusak (Stale Downstream Work):** Membiarkan agen hilir terus bekerja saat agen hulu mengubah kontrak fungsi atau skema data. Batalkan kerucut kausal hilir seketika (*causal cone cancellation*) saat terjadi intervensi hulu.
- **Penghapusan Worktree Tanpa Verifikasi Perubahan:** Memanggil `git worktree remove --force` saat ada berkas penting yang belum di-commit menyebabkan hilangnya kode kerja sub-agent secara permanen. Periksa status git sebelum penghapusan.

## Verification
- Verifikasi isolasi: pastikan perubahan berkas di `/tmp/kanvas-worktrees/<task-id>` tidak terlihat di direktori repositori utama sebelum proses merge.
- Verifikasi pembersihan: jalankan `git worktree list` untuk memastikan tidak ada alokasi worktree usang (*stale worktree*) yang tertinggal setelah tugas tuntas.
