---
name: hermes-autopilot
description: "Use when running autopilot mode for autonomous learning or relentless task execution."
version: 2.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [autopilot, autonomous-learning, self-evolution, knowledge-expansion, problem-solving, escalation]
    related_skills: [otak-koding, mathematical-problem-solving, autonomous-orchestrator]
---

# Hermes Autopilot: Sistem Belajar Mandiri Otonom & Eskalasi Keputusan

Skill ini mengelola siklus belajar mandiri otonom (Autopilot Mode) bagi Hermes Agent untuk terus memperluas wawasan dan memecahkan celah pengetahuan tanpa menunggu perintah manual, dengan protokol eskalasi bertahap ke Mas Bagas.

## 1. Pemicu Perintah (Command Triggers)
- **Eksekusi Tugas Otonom (Relentless Task-Execution)**:
  - "aktifkan autopilot", "jalankan autopilot", "mode autopilot on", "autopilot kerjakan ini" saat ada proyek atau tugas yang belum tuntas.
  - **Prinsip Dasar**: Keputusan dipegang 100% oleh Hermes Agent. Tidak ada interupsi meminta izin atau bertanya di tengah proses eksekusi. Sistem bekerja terus-menerus tanpa henti dengan satu-satunya batas alami adalah habisnya kuota token konteks atau selesainya seluruh kriteria keberhasilan (*definition of done*).
- **Siklus Belajar Mandiri (Knowledge Expansion)**:
  - Mengaktifkan cronjob riset mandiri berkala (30 menit) ke Obsidian Vault `/home/ubuntu/otak-koding/`.
- **Nonaktifkan**: "matikan autopilot", "mode autopilot off", "jeda autopilot"
  - Menjeda eksekusi otonom dan cronjob terkait.
- **Status & Audit**: "status autopilot", "laporan autopilot"
  - Membaca dan menampilkan status siklus, sisa token, delta progres, dan catatan eksekusi.

## 2. Protokol Eksekusi Tugas Otonom (Relentless Task Protocol)
Ketika mode eksekusi tugas otonom diaktifkan oleh Mas Bagas:
1. **Otoritas Keputusan 100% & Tanpa Jeda**:
   - Hermes memegang kendali penuh perancangan, koding, pengujian, dan refaktorisasi.
   - Dilarang berhenti untuk menanyakan izin atau pilihan remeh kepada pengguna; lakukan keputusan terbaik berdasarkan Tiga Mindset Problem Solving.
2. **Pengaman Loop Buntu (*Zero-Delta Circuit Breaker*)**:
   - Sistem memantau perubahan progres empiris di setiap siklus eksekusi ($y_{t+1} - y_t$).
   - Jika terjadi **3 kali iterasi berturut-turut tanpa perbaikan metrik/status baru (*zero delta progress*)**, eksekusi dijeda otomatis untuk mencegah pemborosan token (*token runaway*), lalu mengirimkan eskalasi terfokus ke Telegram Mas Bagas.
3. **Invarian Keamanan Keras (*Hard Safety Boundaries*)**:
   - Bebas mengubah kode, menambah berkas, merombak arsitektur, dan menjalankan test runner pada repositori kerja aktif.
   - **PANTANGAN MUTLAK**:
     * Dilarang me-restart daemon PM2 sistem inti (`pm2 restart ...`).
     * Dilarang memodifikasi file gateway/runtime utama (`server.js`, auth routing).
     * Dilarang mengeksekusi aksi destruktif database produksi (`DROP TABLE`, `TRUNCATE`) atau `git push --force`.
4. **Pola Konsensus Multi-Agen (*Consensus Mesh & Peer Review*)**:
   - Mengorkestrasi agen-agen spesialis (Architect, Backend, Frontend, QA Specialist, Toolsmith, Bekagent).
   - Setiap rencana arsitektur ditinjau silang oleh agen terkait.
5. **Pemutus Kebuntuan Empiris (*Proof-by-Benchmark*)**:
   - Jika timbul silang pendapat teknis antar-agen, kebuntuan tidak diperdebatkan secara verbal.
   - Agen menyusun dua purwarupa minimal (*spike benchmark*); pendekatan dengan bukti metrik empiris terbaik (latensi tail, efisiensi RAM, stabilitas lulus tes) otomatis menjadi keputusan final.
6. **Protokol Hening Taktis Telegram (*Tactile Silence*)**:
   - Mencegah spam obrolan: tidak mengirim pesan di setiap langkah mikro.
   - Pesan Telegram hanya dikirim pada kondisi:
     * *Milestone* tercapai (misal: "Purwarupa A menang benchmark p95, lanjut implementasi").
     * Kuota token konteks menipis kritis ($<15\%$).
     * *Circuit breaker* terpicu karena loop buntu.
     * Laporan akhir komprehensif saat seluruh tugas tuntas 100% lengkap dengan bukti nyata.

## 3. Doktrin Siklus Belajar Mandiri Mas Bagas (Continuous Kaizen Loop)
Hakikat sejati dari Autopilot Bagas Cihuy adalah **Siklus Belajar dan Penyempurnaan Mandiri Tanpa Henti**:
1. **Eksekusi Proyek/Fitur**: Bangun solusi fungsional nyata, teruji, dan tanpa overclaim.
2. **Ekstraksi Kekurangan (Gap List)**: Di akhir setiap eksekusi, secara objektif bedah apa batas, kelemahan, dan celah mekanistik dari hasil tersebut.
3. **Langsung Perbaiki Tanpa Disuruh**: Begitu Gap List teridentifikasi, agen **LANGSUNG MENGEKSEKUSI PERBAIKANNYA** secara bertahap pada siklus berikutnya tanpa menunggu balasan atau instruksi Mas Bagas.
4. **Pelaporan Transparan**: Kirim laporan terstruktur ke chat (Hasil Terverifikasi -> Gap List -> Tindakan Perbaikan yang Sedang Dijalankan), namun **TIDAK PERNAH MENUNGGU RESPON MANUSIA** untuk mulai bekerja lagi. Mesin langsung bergerak sendiri.

## 4. Arsitektur Siklus Riset (3-Mindset Learning Cycle)
Ketika autopilot aktif:
1. **Identifikasi Celah (Gap Detection)**: Audit vault `/home/ubuntu/otak-koding/` dan `knowledge_roadmap` di `state.json`. Ambil kekurangan dari Gap List riset terakhir.
2. **Pengumpulan Bukti Empiris (Data Gathering)**: Dokumentasi resmi, paper terverifikasi, atau penulisan kode uji mandiri. Haram mengutip asumsi atau data fiktif.
3. **Sintesis Solusi (3 Mindsets)**: Mekanistik (rumus/bounds), Bayesian (updating bukti), Desain Sistem (trade-off nyata).
4. **Pencatatan Pengetahuan**: Tulis catatan terstruktur ke `/home/ubuntu/otak-koding/AUTOPILOT/01-SIKLUS-RISET/` dan hubungkan tautan `[[wikilink]]` di `KNOWLEDGE/INDEX.md`.
5. **Ekspansi Roadmap Mandiri (Continuous Autonomous Expansion - Anti-Stop)**:
   - Dilarang keras menghentikan riset atau menunggu konfirmasi Mas Bagas saat autopilot aktif.
   - Jika antrean `knowledge_roadmap` menipis atau habis, agen WAJIB langsung mengambil kekurangan pada **Gap List** hasil riset terakhir, mengekspansinya menjadi target riset baru, dan langsung mengeksekusinya tanpa jeda.
   - Keputusan teknis diambil 100% secara otonom menggunakan Tiga Mindset Problem Solving. Jangan pernah memblokir eksekusi dengan `blocks_new_research: true`.
   - Laporan dikirimkan sebagai ringkasan hasil nyata yang telah selesai, bukan pertanyaan meminta izin.

## 4. Direktori & Berkas Inti
- `AUTOPILOT/state.json`: Status aktif, penghitung siklus, daftar roadmap, antrean eskalasi.
- `AUTOPILOT/01-SIKLUS-RISET/`: Berkas catatan hasil riset mandiri per siklus.
- `AUTOPILOT/02-ANTREAN-KEPUTUSAN/`: Log keputusan yang telah dikonfirmasi atau butuh konfirmasi.
- `~/.hermes/scripts/hermes_autopilot_engine.py`: CLI kontrol cepat engine autopilot.
