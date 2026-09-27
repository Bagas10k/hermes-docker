---
name: hermes-autopilot
description: "Use when running autopilot mode for autonomous learning."
version: 1.0.0
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
- **Aktifkan**: "aktifkan autopilot", "mode autopilot on", "nyalakan autopilot"
  - Menjalankan `cronjob_manage(action='resume', job_id=...)` dan memperbarui `AUTOPILOT/state.json` ke status `active`.
- **Nonaktifkan**: "matikan autopilot", "mode autopilot off", "jeda autopilot"
  - Menjalankan `cronjob_manage(action='pause', job_id=...)` dan memperbarui `AUTOPILOT/state.json` ke status `paused`.
- **Status & Audit**: "status autopilot", "laporan autopilot"
  - Membaca dan menampilkan status siklus, jumlah riset tersimpan, dan antrean keputusan yang membutuhkan arahan.

## 2. Arsitektur Siklus 30 Menit (3-Mindset Learning Cycle)
Setiap 30 menit ketika mode aktif:
1. **Identifikasi Celah (Gap Detection)**:
   - Audit vault `/home/ubuntu/otak-koding/` dan `knowledge_roadmap` di `state.json`.
   - Pilih satu topik spesifik yang belum lengkap pembahasannya.
2. **Pengumpulan Bukti Empiris (Data Gathering)**:
   - Gunakan `web_search`, dokumentasi resmi, atau paper ilmiah terverifikasi.
   - Haram mengutip asumsi atau data fiktif.
3. **Sintesis Solusi (3 Mindsets)**:
   - *Mekanistik*: Formula matematis, batasan sistem, hukum Amdahl.
   - *Bayesian*: Prior vs Evidence, kalibrasi skor keyakinan (Known/Likely/Uncertain).
   - *Desain Sistem*: Pareto trade-off, efisiensi RAM/latensi, resistensi kegagalan.
4. **Pencatatan Pengetahuan**:
   - Tulis catatan terstruktur ke `/home/ubuntu/otak-koding/AUTOPILOT/01-SIKLUS-RISET/` atau kategori vault yang sesuai.
   - Hubungkan tautan dua arah `[[wikilink]]` agar terintegrasi ke neural graph 3D.
5. **Pemeriksaan Eskalasi (Escalation Gate)**:
   - Jika ditemukan dilema arsitektur, simpangan kritis, atau ambiguitas tinggi, masukkan ke `pending_decisions`.
   - **Aturan Veto/Tanya**: Jika `pending_decisions >= 3` atau ada keputusan bercabang berisiko:
     - Hentikan ekspansi riset baru.
     - Formulasikan pertanyaan bertahap (*"satu soal satu soal"*) dengan opsi pilihan ganda terstruktur (rekomendasi di awal).
     - Kirimkan langsung ke Mas Bagas di obrolan ruang kerja Telegram.

## 3. Direktori & Berkas Inti
- `AUTOPILOT/state.json`: Status aktif, penghitung siklus, daftar roadmap, antrean eskalasi.
- `AUTOPILOT/01-SIKLUS-RISET/`: Berkas catatan hasil riset mandiri per siklus.
- `AUTOPILOT/02-ANTREAN-KEPUTUSAN/`: Log keputusan yang telah dikonfirmasi atau butuh konfirmasi.
- `~/.hermes/scripts/hermes_autopilot_engine.py`: CLI kontrol cepat engine autopilot.
