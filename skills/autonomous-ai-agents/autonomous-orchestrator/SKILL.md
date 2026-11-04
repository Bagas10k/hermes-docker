---
name: autonomous-orchestrator
description: Spawn sub-agents for complex or noisy technical tasks.
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [orchestration, sub-agents, delegation, parallel-execution]
---

# Autonomous Orchestrator (Sistem Mandor dan Kuli)

Skill ini digunakan untuk mengatur delegasi pekerjaan ke sub-agent menggunakan alat `delegate_task`. Gunakan saat menghadapi tugas panjang, debugging ruwet, penulisan skrip masif, atau tugas berulang yang akan mengotori riwayat chat utama jika dikerjakan sendiri oleh agen utama (Mandor).

## 🚀 Kebijakan Orkestrasi Sensitivitas Tinggi (Mandat Mas Bagas: Konkurensi Paralel Maksimal)

Mandor WAJIB bersikap proaktif dan responsif memecah pekerjaan ke sub-agent paralel via `delegate_task`:

1. **Default Proaktif (High Sensitivity):**
   - Setiap kali Mas Bagas memberikan tugas kerja teknis (coding, debugging, audit, optimasi, perancangan, penulisan dokumen/skrip, penelusuran sistem bercabang), Mandor LANGSUNG memecahnya ke armada sub-agent paralel (minimal 1 Pelaksana + 1 QC Pengawas).
   - Jangan menahan eksekusi di Mandor sendirian jika tugas dapat dibagi menjadi jalur paralel independen. Konkurensi memangkas durasi dan menjamin mutu lewat isolasi konteks kerja.
2. **Kapan Mandor Menjawab Langsung (Tanpa Delegasi)?**
   - HANYA untuk percakapan/obrolan biasa, klarifikasi pertanyaan santai, atau cek status instan 1 baris tanpa proses kerja.
   - Segala bentuk tugas operasional, verifikasi sistem, audit, atau rekayasa multi-langkah WAJIB langsung melibatkan armada sub-agent.
3. **Pemanfaatan Kapasitas Penuh (Hingga 3 Pekerja Simultan):**
   - Manfaatkan slot paralel (maksimal 3 sub-agent per batch) untuk menyelesaikan pekerjaan jauh lebih cepat.
   - Contoh pembagian:
     - Worker 1: Pelaksana implementasi / backend / logika
     - Worker 2: Pelaksana frontend / antarmuka / data
     - Worker 3: QC Pengawas independen (verifikasi empiris, cek exit code, uji runtime)

## Kapan Menggunakan Sub-Agent?
1. **Refactoring / Coding Skala Besar:** Memperbaiki sistem, menulis API baru, merombak CSS.
2. **System Debugging:** Menelusuri log error, memeriksa dependensi, dan menambal bug.
3. **Data Processing:** Membaca ribuan baris log, mengonversi format data, menerjemahkan dokumen berukuran besar.
4. **Research:** Mencari dokumentasi API, membaca forum, atau menggali referensi.

**TIDAK cocok untuk sub-agent:**
- Percakapan santai / tanya jawab murni tanpa pekerjaan sistem
- Konfirmasi arahan langsung ke Mas Bagas

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
     - `🛡️ Si Pengawas`: Pencatat kekurangan & celah yang terlewat (missed) secara independen, tanpa wewenang melooping tindakan eksekusi.
   - **Tugas:** Menerima sasaran makro dari Mandor, memecahnya menjadi sub-task mikro untuk Agent Cucu.

3. **Level 3: Agent Cucu (Pekerja Lapangan Ephemeral / Kuli — role: `leaf`)**
   - **Karakter:** Eksekutor tugas ber-resource kecil, fokus satu hal spesifik, sementara (*ephemeral*).
   - **Spesialisasi:**
     - `🔍 Analis Cucu`: Menganalisis log, membaca potongan kode, ekstraksi teks, kueri database.
     - `⚡ Kuli Eksekutor`: Menjalankan skrip pengujian, patching berkas terisolasi, curl endpoint.
     - `🛡️ QC Cucu`: Memeriksa byte gambar, mengecek status HTTP, inspeksi artifact disk.
   - `Sifat`: Lahir saat task dipanggil (`delegate_task`), selesai menyetor bukti, langsung dimusnahkan agar hemat RAM.

## Mode Operasi: Forum Diskusi Terbuka vs Chat Pribadi (DM)

1. **Forum Diskusi Terbuka (Discussion Thread / Ruang Sidang):**
   - **Tujuan:** Deliberasi arsitektur, kesepakatan desain, transparansi peran kabinet, dan konfirmasi langsung ke Mas Bagas.
   - **Karakteristik Alur:** **Sekuensial (bergantian)** pada antarmuka percakapan. Agen merespons satu demi satu agar konteks utuh dan tidak terjadi tabrakan koding (*race condition*).
   - **Persepsi Waktu:** Terasa lebih lama karena merupakan akumulasi waktu penalaran model + eksekusi alat nyata (shell/curl/browser) di server per giliran. Bukan karena koneksi internet lambat.
2. **Chat Pribadi / DM (Direct Execution & Background Sprint):**
   - **Tujuan:** Kecepatan, pengerjaan minim obrolan (*zero slop*), dan hasil bersih.
   - **Karakteristik Alur:** **Paralel di latar belakang** via `delegate_task`. Mandor melepas sub-agent (Anak/Cucu) simultan pada berkas/jalur terisolasi tanpa membanjiri ruang chat.
   - **Output:** Satu laporan terstruktur dengan bukti biner (exit code, status HTTP, bukti render fisik).

## Model Sub-Agent: Resolusi & Verifikasi

- Anak `delegate_task` **tidak mewarisi model percakapan induk** bila `delegation.model` + `delegation.provider` dipin di `config.yaml`; rantai cadangannya `delegation.fallback_providers`. Tanpa pin, anak mengikuti model induk.
- **Profil bukan sub-agent.** `~/.hermes/profiles/<nama>/` adalah proses Hermes terpisah (punya `model.default` sendiri) dan tidak pernah dipakai `delegate_task`. Jangan menjawab "sub-agent pakai model X" dari daftar profil.
- **Buktikan nama model dengan satu `curl` nyata** ke endpoint provider sebelum menyebutkannya ke Mas Bagas — entri di config bukan bukti endpoint melayaninya.
- QC independen sebaiknya memakai model **beda keluarga** dari pelaksana; QC se-keluarga mewarisi blind spot yang sama. Ganti model QC hanya setelah model pengganti diuji nyata.

## Optimasi Efisiensi & Latensi Delegasi (Reasoning Effort & Fallback)

1. **Reasoning Effort untuk Worker (Medium/Low):**
   - Hindari `delegation.reasoning_effort: high` untuk sub-agent pelaksana/kuli (leaf worker). Pada model dengan native thinking (seperti Gemini Flash Thinking), effort `high` menghasilkan pemikiran internal mendalam selama 20+ detik sebelum tool call pertama keluar.
   - Setel `delegation.reasoning_effort: medium` (atau `low` untuk eksekusi skrip murni). Pengujian empiris membuktikan penurunan durasi API dari ~26 detik menjadi ~15 detik (~41% lebih cepat) tanpa menurunkan akurasi tool call.
2. **Redundansi Provider (Fallback Chain):**
   - Wajib mendaftarkan minimal 1 entri pada `delegation.fallback_providers` (misal `custom:nbgate`) agar sub-agent tidak tertahan (*stall*) ketika provider utama mengalami antrean atau spike latensi.
3. **Konfigurasi Resmi Hermes:**
   - Berkas `~/.hermes/config.yaml` diproteksi dari pengeditan langsung oleh agen (`refusing to write`). Selalu gunakan CLI resmi:
     `hermes config set delegation.reasoning_effort medium`
     `hermes config set delegation.fallback_providers '[{"provider": "custom:nbgate", "model": "ag/gemini-3.8-flash-high"}]'`
4. **Pemantauan Status Armada di Telegram (/agents & Live HUD):**
   - Perintah resmi gateway untuk mengecek aktivitas agent dan background delegation adalah `/agents` (jamak) atau `/tasks` (alias `/agent` tunggal sudah didukung di CLI command definition).
   - Pola Live HUD Card: Saat mengorkestrasi sub-agent paralel, terapkan pembaruan status *in-place* (`edit_message` dengan jeda throttling `EDIT_INTERVAL >= 1.5s`) agar ruang obrolan Telegram tetap rapi (*zero chat spam*) tanpa memicu flood control.

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
   Setelah sub-agent selesai, Mandor wajib memeriksa diff aktual dan menjalankan tes integrasi/regresi relevan pada kandidat gabungan. Jika gagal, bedakan cacat implementasi dari kegagalan fixture, lalu koreksi atau karantina hanya hunk milik worker yang terbukti bermasalah. Gunakan snapshot awal sebagai batas kepemilikan; jangan melakukan revert/reset seluruh berkas pada worktree kotor karena dapat menghapus revisi lain.

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
5. **Pitfall drift/hang leaf:** Aktivitas tool bukan otomatis progres. Berikan satu artefak konkret, paling banyak tiga berkas utama, kriteria biner dan batas 4–6 tool call; sertakan konteks yang sudah diperiksa agar worker tidak mengulang audit. Jangan menganggap batas dalam prompt sebagai timeout yang ditegakkan runtime. Bila delegasi berjalan sinkron sehingga Mandor tidak dapat memberi pulse atau mengambil alih selama panggilan, kecilkan unit kerja sebelum dispatch—jangan menyerahkan satu subsystem dengan anggaran pendek di atas kertas. Pada mode background, kerjakan jalur independen dan gunakan lifecycle/control yang tersedia jika ada sinyal drift; jangan menunggu atau polling transcript sebagai pengganti pekerjaan. Sesudah hasil masuk, periksa status runtime, exit reason, diff dan output mentah; klaim `SELESAI` atau `GO` dari hasil `max_iterations`, `interrupted`, atau dengan tes gagal tetap parsial. Verifikasi hunk yang tersimpan, ambil alih sisa yang jelas, dan simpan anggaran untuk satu QC independen atas sumber final. Jangan delegasikan diagnosis awal bila Mandor dapat menentukannya dalam ≤5 tool call.
6. **Inspeksi Respon Bot Mode (`message_agent`) Terpotong:** Notifikasi penyelesaian background runner `bot_mode_dm.py` pada gateway/TUI dapat terpotong (`[… output truncated — showing last 0 chars]`). Jika runner selesai dengan exit code 0, jangan anggap handoff gagal atau kosong; baca durable receipt fisik di `<target_profile_home>/runtime/bot_live_delivery/<delivery_id>.json` atau lewat `tools.bot_live_delivery.read_delivery_result(profile_home, delivery_id)` untuk mengekstrak field `reply` lengkap berstatus `settled`.

## Kontrak Laporan Progres Konkret

Untuk setiap tugas multi-langkah, setiap pulse kepada Mas Bagas wajib memakai bahasa awam dan memuat:

1. `STATUS: SEDANG BEKERJA | SELESAI | TERBLOKIR`.
2. `Sedang dikerjakan:` tindakan konkret dan targetnya; contoh: “membaca konfigurasi Telegram untuk mencari pengaturan status”, bukan “audit berjalan”.
3. `Sudah selesai:` hasil nyata yang telah diperoleh, bukan nama fase.
4. `File yang diubah:` path berkas; tulis `belum ada` jika belum menyentuh kode.
5. `Hasil tes:` perintah/bukti nyata; tulis `belum dijalankan` bila memang belum.
6. `Sisa pekerjaan:` langkah konkret yang belum selesai.

Dilarang mengirim progress bar atau persentase tanpa daftar pekerjaan yang dapat dipahami. Identitas/peran agen bukan penjelasan pekerjaan. Jika agen macet, laporkan `TERBLOKIR`, sebut durasinya, hentikan atau ambil alih. Jangan menjadikan setiap audit atau hasil parsial sebagai penutupan tugas dan permintaan izin ulang ketika implementasi sudah disetujui. Berikan pulse singkat pada bukti baru, teruskan acceptance item yang belum tertutup, dan serahkan satu laporan akhir changed/unfinished/tests/challenges; jika batas runtime memaksa berhenti, catat checkpoint yang dapat dilanjutkan tanpa mengulang discovery. Untuk tugas panjang, buat dan perbarui `build_tracker.json` di workspace tugas sebelum perubahan kode pertama serta setelah milestone teruji.

Kontrak teks ini adalah fallback komunikasi, bukan pengganti observabilitas live. Jika Mas Bagas meminta melihat apa yang sedang dikerjakan atau kode apa yang berubah, tampilkan artefak eksekusi pada permukaan yang mendukungnya: alat aktif, target file/perintah, diff, hasil/exit status, dan lifecycle sub-agent. Jangan menyatakan masalah visibilitas selesai hanya karena format laporan sudah lebih rapi; uji permukaan live dengan satu pekerjaan sintetis aman dan bukti render aktual.

## Fast Runtime Verification & Persistent Tracking
1. **One-Command Health Check 5 Pilar:** Gunakan skrip master `/home/ubuntu/check-5pilar.sh` atau skrip lokal `./check.sh` di root pilar target (`website-pbj`, `kasir-bangunan-app`, `dasbor-jajan-digital`, `sputarball`). Verifikasi selesai dalam ≤2 detik tanpa loop perintah manual berulang.
2. **Durable State Tracker (`build_tracker.json`):** Untuk tugas multi-step di pilar aktif, baca dan perbarui berkas fisik `build_tracker.json` di root proyek target sebelum memulai dan setelah mencapai milestone baru agar status tidak hilang oleh kompaksi sesi.