---
name: mode-planning
description: "Use when planning tasks. Plan-first habit before execution."
version: 1.0.0
author: "Bagas Cihuy & Hermes Agent"
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [planning, habit, plan-mode, pre-implementation, subagent-decomposition, decision-tree]
    related_skills: [grill-me, autonomous-orchestrator, tiga-serangkai-orchestration]
---

# Mode Planning (Kebiasaan Plan-First & Penyusunan Rencana Sistematis)

Skill kebiasaan (*habit skill*) untuk mengunci agen ke dalam **Mode Rencana Terstruktur** sebelum menyentuh kode atau melakukan perubahan pada sistem. Mencegah eksekusi impulsif, menegakkan prinsip dekomposisi subagent, dan memastikan keselarasan arsitektur dengan Mas Bagas.

## 1. Pemicu Pengaktifan (When to Use)
- Pengguna berkata: "mode planning", "susun rencana dulu", "bikin plan", "mari kita rencanakan", "evaluasi rencana ini", "rencanakan tugas ini".
- Sebelum menangani pekerjaan berdampak besar: arsitektur baru, migrasi skema database, integrasi sistem baru, perombakan UI, atau alur kerja multi-file.
- Saat instruksi pengguna memuat sasaran besar yang butuh pemecahan langkah terukur.

## 2. Enam Kebiasaan Mutlak Mode Planning (The 6 Invariants)

1. **Tahan Dorongan Menulis Kode Langsung (Zero Impulsive Execution):**
   - Dilarang membuat, memodifikasi, atau mem-patch kode produksi selama mode planning aktif.
   - Perubahan hanya boleh terjadi pada berkas draf rencana/spesifikasi jika diminta.
2. **Kumpulkan Fakta Mandiri dari Lingkungan (Explore First):**
   - Periksa basis kode nyata menggunakan `search_files`, `read_file`, dan `terminal` (read-only).
   - Jangan menanyakan hal teknis yang bisa dicari sendiri di sistem (lokasi file, port yang aktif, nama fungsi, dependensi).
3. **Wawancara Bertahap ala Bagas Cihuy ('Satu Soal Satu Soal'):**
   - Jika ada keputusan bisnis, preferensi desain, atau trade-off strategis yang ambigu: ajukan **1 pertanyaan per giliran**.
   - Sertakan opsi pilihan ganda terstruktur dengan **rekomendasi terbaik di urutan pertama** beserta alasan ringkasnya. Pantang memutuskan sepihak.
4. **Analisis Dekomposisi & Formulasi Sub-Agent:**
   - Evaluasi apakah pekerjaan layak dipecah ke subagent (paralel, isolasi komponen, atau Four-Eyes).
   - Tentukan peran: Siapa **Pelaksana** (kuli lapangan), dan siapa **Pengawas** (QC independen).
5. **Format Dokumen Rencana (Standard Plan Output):**
   Setiap rencana disusun rapi dengan struktur:
   - **A. Sasaran & Batasan**: Apa yang masuk lingkup (*in-scope*) dan apa yang tegas ditolak (*out-of-scope*).
   - **B. Analisis Dekomposisi Sub-Agent**: Pembagian tugas anak & cucu (atau justifikasi eksekusi tunggal).
   - **C. Rencana Langkah Bertahap (Step-by-Step DAG)**: Alur kerja bernomor urut dengan masukan dan keluaran jelas.
   - **D. Kriteria Pengujian Empiris (Acceptance Criteria)**: Pengujian konkret (status HTTP, exit code, visual browser screenshot).
   - **E. Rencana Mitigasi & Rollback**: Cara mengembalikan sistem jika terjadi kegagalan.
6. **Gerbang Lampu Hijau (Awaiting Explicit Green Light):**
   - Akhiri penyusunan rencana dengan konfirmasi: *"Apakah rencana ini sudah selaras dan disetujui? Balas 'lanjut' / 'gas' untuk mulai eksekusi, atau sebutkan penyesuaian jika ada."*
   - Dilarang mengeksekusi sebelum ada persetujuan eksplisit.
