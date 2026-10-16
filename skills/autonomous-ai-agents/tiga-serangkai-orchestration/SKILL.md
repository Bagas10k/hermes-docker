---
name: tiga-serangkai-orchestration
description: "Use when executing complex tasks. Enforces 2-5 agents."
version: 1.0.0
author: "Bagas Cihuy & Hermes Agent"
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [multi-agent, tiga-serangkai, subagent, orchestration, debate, qc-gatekeeper]
    related_skills: [autonomous-orchestrator, grill-me, requesting-code-review]
---

# Tiga Serangkai Sub-Agent Orchestration Protocol

Protokol resmi orkestrasi sub-agent otonom untuk tugas tingkat menengah dan kompleks dalam ekosistem Bagas Cihuy. Menegakkan batas kuantitas (2 s.d. 5 sub-agent), siklus debat kritik pra-eksekusi, dan gerbang verifikasi empiris pasca-eksekusi.

## 1. Lingkup Penerapan (Scope & Bounds)

### Sensitivitas Pemicu: Menengah (pilihan Bagas)
- Aktifkan `delegate_task` bila tugas memerlukan beberapa langkah yang dapat dipisah menjadi alur kerja independen dengan penalaran, atau membutuhkan audit/QC independen: fitur baru, refaktorisasi, riset multi-sumber, audit sistem, dan bug multi-modul.
- Untuk dampak besar atau risiko tinggi, aktifkan pengawas independen meskipun langkah eksekusinya sedikit. Tetapkan kriteria penerimaan dan batas tugas sebelum delegasi.
- Jangan delegasikan hanya karena jumlah langkah banyak: bila alurnya mekanis, saling bergantung erat, atau berupa beberapa panggilan alat tanpa penalaran terpisah, kerjakan langsung (gunakan `execute_code` untuk batch mekanis).

### Kapan Dilewati (Bypass / Direct Execution)
- Tugas mikro dan operasional sepele: membaca 1 berkas singkat, memeriksa status port/service, kueri satu baris, atau pengecekan waktu.
- Satu panggilan alat, atau tugas yang memerlukan klarifikasi/interaksi pengguna: panggil alat langsung atau tanyakan ke Bagas; sub-agent tidak dapat meminta klarifikasi.
- General Manager mengeksekusi langsung bila manfaat pemeriksaan paralel tidak melebihi biaya token, latensi, dan koordinasi.

---

## 2. Formasi Sub-Agent (2 s.d. 5 Pekerja per Gelombang)

Rentang 2-5 berlaku sebagai **formasi per gelombang**, bukan plafon total. Jumlah pekerja yang boleh lahir sepanjang satu tugas **tidak dibatasi** selama ada anggaran; yang dibatasi adalah berapa yang berjalan bersamaan per gelombang.

Batas kerasnya bukan angka, melainkan **anggaran**: kedalaman (`delegation.max_spawn_depth`, bawaan 1 = datar; 2 = anak boleh punya anak; tanpa plafon atas), plafon konkurensi (`delegation.max_concurrent_children`), batas waktu anak (`child_timeout_seconds`), dan aturan berhenti setelah 2 kegagalan berturut pada cabang yang sama.

Konsekuensi bila plafon dilepas tanpa anggaran: biaya berlipat tiap tingkat kedalaman, dan kegagalan senyap pada cabang terdalam tidak lagi terlihat oleh induk. Untuk protokol lengkap cabang, gerbang gabung, dan rembukan antar-agen, muat `fleet-branch-merge-protocol`.

1. **Formasi 2 Sub-Agent:**
   - Worker 1: Si Eksekutor (Pembuat kode, konfigurasi, atau perumus solusi teknis).
   - Worker 2: Si Pengawas (Auditor mutu, tester verifikasi, dan QC independen).
2. **Formasi 3 Sub-Agent (Standar Tiga Serangkai):**
   - Worker 1: Si Pintar (Periset, perancang arsitektur, dan validator referensi).
   - Worker 2: Si Eksekutor (Pelaksana instruksi teknis di terminal/lingkungan kerja).
   - Worker 3: Si Pengawas (Auditor mutu dan penguji empiris).
3. **Formasi 4-5 Sub-Agent (Skala Besar):**
   - Worker 1 s.d. N-1: Pemecahan spesialis domain (misal: Backend, Frontend, Data Pipeline, Dokumentasi).
   - Worker Terakhir (Wajib): 1 Si Pengawas independen sebagai gerbang verifikasi.

---

## 3. Protokol Debat Pra-Eksekusi (Si Pintar vs Si Eksekutor)

Khusus untuk proyek yang membutuhkan ketelitian tinggi, arsitektur baru, atau perintah yang berpotensi ambigu:

1. **Maksimal 3 Putaran Kritik:**
   - Si Pintar menyusun draf rancangan dan batasan solusi.
   - Si Eksekutor menguji kelayakan lapangan (kondisi RAM, port, dependensi, risiko kegagalan) dan melempar kritik serangan.
   - Si Pintar merevisi rancangan berdasarkan kritik tersebut.
2. **Aturan Selesai Cepat (Early Exit):**
   - Jika pada putaran 1 atau 2 rancangan sudah terbukti kokoh dan disepakati kedua pihak, debat langsung disudahi. Jangan memaksakan hingga 3 putaran.
3. **Pagar Pengaman & Eskalasi (Circuit Breaker):**
   - Jika setelah putaran ke-3 belum tercapai kesepakatan, ATAU jika ditemukan ambiguitas **kebutuhan bisnis**:
   - **WAJIB STOP EKSEKUSI** dan tanyakan ke Mas Bagas (1 pertanyaan bertahap, format pilihan ganda terstruktur dengan rekomendasi di awal).

   **Pembatasan penting — jangan salah tanya:** yang dinaikkan ke Mas Bagas hanya **kebutuhan, kondisi lapangan, preferensi, dan keputusan berdampak besar**. Kekurangan **pengetahuan teknis, referensi, cara pakai pustaka, atau pilihan alat** TIDAK ditanyakan ke pengguna — dicari sendiri ke internet, dokumentasi resmi, atau basis kode. Tanya ke pengguna untuk hal teknis membuang waktu pengguna dan menghasilkan jawaban yang lebih lemah daripada sumber primer.
   - Kekurangan **kesepakatan antar-bagian pekerjaan** diselesaikan lewat rembukan antar-agen berbasis artefak tertulis (lihat `fleet-branch-merge-protocol`), bukan dengan menaikkannya ke pengguna.
   - Sub-agent tidak punya kanal `clarify`; pertanyaan yang benar-benar harus naik dilewatkan induk, bukan ditanyakan langsung oleh anak.

---

## 4. Protokol QC Pasca-Eksekusi (Hak Veto Si Pengawas)

Setiap artefak yang selesai dikerjakan oleh Si Eksekutor wajib diaudit secara empiris oleh Si Pengawas:

1. **Pengujian Nyata Tanpa Asumsi:**
   - Dilarang percaya klaim verbal. Buktikan dengan output curl, inspeksi status proses, cek berkas fisik, atau tes unit.
2. **Jatah Rework Terbatas (Maksimal 2 Kali Revisi):**
   - Jika status pengujian **REJECT (VETO)**: Si Pengawas memberikan daftar temuan cacat konkret (file, line, error log).
   - Si Eksekutor diberi kesempatan melakukan perbaikan maksimal 2 kali putaran.
3. **Eskalasi Kegagalan:**
   - Jika revisi ke-2 tetap gagal memenuhi kriteria penerimaan, eksekusi dihentikan total dan bukti pengujian diserahkan ke Mas Bagas untuk intervensi langsung.

---

## 5. Pelaporan & Pembukuan

Setelah verifikasi Si Pengawas menyatakan **PASS**:
1. General Manager merangkum hasil kerja lugas untuk Mas Bagas (apa yang berubah, bukti uji, status akhir, dan estimasi token).
2. Data setoran dan ringkasan pelajaran dicatat ke basis pengetahuan Obsidian oleh Asisten Manager (Bikagent).
