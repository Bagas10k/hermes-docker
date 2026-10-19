---
name: autonomous-orchestrator
description: Spawn sub-agents for complex or noisy technical tasks.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [orchestration, sub-agents, delegation, parallel-execution]
---

# Autonomous Orchestrator (Sistem Mandor dan Kuli)

Skill ini digunakan untuk mengatur delegasi pekerjaan ke sub-agent menggunakan alat `delegate_task`. Gunakan saat menghadapi tugas panjang, debugging ruwet, penulisan skrip masif, atau tugas berulang yang akan mengotori riwayat chat utama jika dikerjakan sendiri oleh agen utama (Mandor).

## Kapan Menggunakan Sub-Agent?
1. **Refactoring / Coding Skala Besar:** Memperbaiki sistem, menulis API baru, merombak CSS.
2. **System Debugging:** Menelusuri log error, memeriksa dependensi, dan menambal bug.
3. **Data Processing:** Membaca ribuan baris log, mengonversi format data, menerjemahkan dokumen berukuran besar.
4. **Research:** Mencari dokumentasi API, membaca forum, atau menggali referensi.

## Peran Arsitektur (Hierarki 3 Generasi: Mandor, Anak, Cucu)

1. **Level 1: Mandor (Agen Induk / General Manager)**
   - Menerima mandat langsung dari Mas Bagas.
   - Mengendalikan gerbang orkestrasi (Pre-Task Gate) dan resource budget host.
   - Mengorkestrasi Level 2 (Anak) dan Level 3 (Cucu).
   - Memvalidasi bukti empiris artefak fisik sebelum melapor ke Mas Bagas.

2. **Level 2: Agent Anak (Kabinet Tiga Serangkai — role: `orchestrator`)**
   - **Karakter:** Arsitek dan perancang divisi berpikiran matang, berorientasi solusi strategis.
   - **Trio Inti:**
     - `🧠 Si Pintar`: Riset kausal, pemodelan sistem, arsitektur teknis.
     - `⚡ Si Eksekutor`: Komandan lapangan sistem, penanganan service, pimpinan kuli.
     - `🛡️ Si Pengawas`: Quality control independen, audit kepatuhan, hak veto rilis.
   - **Tugas:** Menerima sasaran makro dari Mandor, memecahnya menjadi sub-task mikro untuk Agent Cucu.

3. **Level 3: Agent Cucu (Pekerja Lapangan Ephemeral / Kuli — role: `leaf`)**
   - **Karakter:** Eksekutor tugas ber-resource kecil, fokus satu hal spesifik, sementara (*ephemeral*).
   - **Spesialisasi:**
     - `🔍 Analis Cucu`: Menganalisis log, membaca potongan kode, ekstraksi teks, kueri database.
     - `⚡ Kuli Eksekutor`: Menjalankan skrip pengujian, patching berkas terisolasi, curl endpoint.
     - `🛡️ QC Cucu`: Memeriksa byte gambar, mengecek status HTTP, inspeksi artifact disk.
   - **Sifat:** Lahir saat task dipanggil (`delegate_task`), selesai menyetor bukti, langsung dimusnahkan agar hemat RAM.

## Panduan Menggunakan `delegate_task`
Gunakan tool `delegate_task` untuk mengirim tugas. Berikan `context` sejelas mungkin karena sub-agent tidak memiliki riwayat chat ini.

## Protokol Kolaborasi Multi-Agent Simultan (Prinsip gitai / Scion)
Ketika mendelegasikan beberapa sub-agent bekerja bersamaan pada satu proyek:
1. **Sparse File Allocation (Alokasi Berkas Terisolasi):**  
   Setiap sub-agent HANYA boleh diberi izin membaca dan mengedit berkas yang ditugaskan secara eksplisit. Dilarang memberikan mandat edit terbuka pada seluruh folder proyek.
2. **Pencegahan File Contention (Kunci Jalur):**  
   Mandor (Orchestrator) wajib memastikan tidak ada 2 sub-agent yang mengedit berkas yang sama dalam satu batch giliran tugas.
3. **Landing & Conflict Resolution (Compare-and-Swap):**  
   Jika ada dua tugas yang bersinggungan, Mandor bertindak sebagai resolver pusat yang menggabungkan patch kode secara sekuensial dan menjalankan uji biner sebelum commit permanen.
4. **Verifikasi Pasca-Landing (Test After Landing):**  
   Setelah sub-agent selesai, Mandor wajib menjalankan regression test otomatis. Jika gagal, commit/perubahan sub-agent tersebut di-revert seketika tanpa merusak kode sub-agent lainnya.

## Aturan Keselamatan (Production Safety)
1. Selalu berikan **batas yang jelas** (context) ke sub-agent (contoh: "jangan sentuh database, jangan upload ke production").
2. **Kepatuhan Mutlak Kontrak Integritas Mas Bagas:**  
   Setiap mandat delegasi wajib mematuhi standar `/home/ubuntu/STANDAR_KERJA_DAN_INTEGRITAS_BAGAS.md`:
   - Buktikan dulu, baru lapor (wajib lampirkan bukti empiris / status exit code / diff).
   - Dilarang keras halusinasi atau overclaim hasil.
   - Sub-agent eksekutor dibatasi maksimal 6 tool call (wajib tulis berkas di langkah awal, dilarang loop riset tak berujung).
   - Pengujian visual wajib dilakukan secara fisik di peramban riil, bukan sekadar tes biner teks.
3. Sub-agent **tidak bisa** membaca chat history. Semua info krusial (jalur file absolut, nama fungsi, rule desain) HARUS disematkan ke dalam `context`.
4. Setelah sub-agent selesai, **Mandor wajib memverifikasi hasil kerjanya** (contoh: curl endpoint, baca head file) sebelum dilaporkan ke pengguna. Jangan sekadar menjadi "kurir" tanpa paham apa yang diperbaiki sub-agent.