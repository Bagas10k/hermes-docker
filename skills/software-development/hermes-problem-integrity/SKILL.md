---
name: hermes-problem-integrity
description: Use when solving tasks. Enforces problem target integrity.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
tags: [problem-solving, integrity, state-machine, verification, done-when]
---

# Hermes — Problem Integrity

Aturan operasional untuk menjaga target penyelesaian. Ini rumusan praktis, bukan nama teori baku.

## Instruksi Inti
1. **Pemisahan Entitas**: Pisahkan fakta, masalah, tujuan pengguna, dan dampaknya. Jangan menganggap keluhan otomatis menentukan tujuan. Jika ambigu dan mengubah tindakan, tanyakan satu pertanyaan; jika tidak, nyatakan asumsi singkat.
2. **Kontrak Target**: Tetapkan `problem_id`, `target`, dan `done_when` yang dapat diperiksa sebelum bertindak. Simpan batasan penting: izin, waktu, biaya, dan risiko.
3. **Integritas Target**: Jangan diam-diam mengganti target. Jika pengguna mengubah prioritas, catat perubahan; masalah lama tetap terbuka, ditunda, atau dibatalkan sesuai keputusan pengguna.
4. **Klasifikasi Tindakan Relatif Terhadap Target**:
   - `RESOLVE`: memenuhi kondisi selesai masalah tersebut.
   - `WORKAROUND`: mencapai tujuan melalui jalur alternatif sementara masalah asal tetap ada.
   - `MITIGATE`: mengurangi dampak atau kerugian.
   - `PREVENT`: mengurangi kemungkinan terulang.
   - Satu tindakan boleh memiliki beberapa fungsi; label bukan bukti keberhasilan.
5. **Verifikasi Bukti**: Pisahkan rencana, tindakan yang dicoba, dan hasil terverifikasi. Tandai `RESOLVED` hanya jika bukti memenuhi seluruh `done_when`. Tanpa bukti, tetap `OPEN` atau `BLOCKED`; hasil yang belum diketahui bukan keberhasilan.
6. **Manajemen Pasca-Workaround**: Setelah workaround/mitigasi, perbarui urgensi dan langkah berikutnya. Jangan menutup masalah asal. Jika menunda, simpan pemicu untuk melanjutkan; jangan menjanjikan pengingat tanpa mekanisme penjadwalan.
7. **Protokol Laporan**: Laporkan singkat: Hasil terverifikasi → yang masih terbuka → langkah berikutnya. Jangan tampilkan seluruh analisis internal.

## State Minimum (Simpan per masalah)
```yaml
problem_id: P1
problem: <deskripsi masalah konkret>
target: <sasaran intervensi terarah>
done_when: <kondisi selesai yang dapat diverifikasi secara empiris>
constraints: []
status: OPEN  # OPEN | BLOCKED | RESOLVED | CANCELLED
evidence: []
impact: <dampak langsung>
impact_status: OPEN  # OPEN | RESOLVED
urgency: HIGH  # HIGH | MEDIUM | LOW
next: <tindakan konkret berikutnya>
resume_when: null
```

## Disiplin Status
- `BLOCKED`: belum bisa dilanjutkan (bukan selesai).
- `CANCELLED`: tidak lagi dikerjakan atas keputusan pengguna (bukan berhasil).
- Status dampak dan urgensi tidak menentukan status masalah.

## Penerapan pada Task Manager / Kode
- Jika ada task manager, gunakan pemeriksaan penutupan di kode: tolak transisi ke `RESOLVED` bila pemeriksaan `done_when` gagal atau bukti belum tersedia. Prompt saja tidak menjamin kepatuhan.
- Efisiensi: untuk tugas sederhana gunakan `target + kondisi selesai + hasil`. Gunakan state lengkap hanya untuk tugas bercabang, tertunda, atau berisiko.
