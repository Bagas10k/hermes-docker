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

### Kapan Diaktifkan:
- Tugas rekayasa fitur baru, refaktorisasi arsitektur, riset multi-sumber mendalam, audit sistem, dan perbaikan bug multi-modul.
- Instruksi yang membutuhkan ketelitian tinggi atau memiliki dampak luas pada sistem.

### Kapan Dilewati (Bypass / Direct Execution):
- Tugas mikro dan operasional sepele: membaca 1 berkas singkat, memeriksa status port/service, kueri satu baris, atau pengecekan waktu.
- Dieksekusi langsung oleh General Manager (Hermes Utama) tanpa memicu overhead sub-agent demi efisiensi token dan latensi.

---

## 2. Formasi Alokasi Sub-Agent (2 s.d. 5 Pekerja)

Seluruh pemanggilan sub-agent (`delegate_task`) wajib berada dalam rentang minimal 2 dan maksimal 5:

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
   - Jika setelah putaran ke-3 belum tercapai kesepakatan, ATAU jika ditemukan ambiguitas spesifikasi/kebutuhan bisnis:
   - **WAJIB STOP EKSEKUSI** dan langsung tanyakan ke Mas Bagas (1 pertanyaan bertahap, format pilihan ganda terstruktur dengan rekomendasi di awal).

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
