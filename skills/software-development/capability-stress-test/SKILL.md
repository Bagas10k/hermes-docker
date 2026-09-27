---
name: capability-stress-test
description: "Autonomous engineering capability benchmark and stress testing."
version: 1.0.0
author: Bagas Cihuy, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [stress-test, capability, engineering-agent, audit, evaluation, self-critique, anti-slop]
    related_skills: [otak-koding, design-reference-interpreter, requesting-code-review]
---

# Capability Stress Test — Autonomous Engineering Benchmark

## Overview
Protokol evaluasi kapabilitas rekayasa otonom untuk agen cerdas. Menguji apakah agen mampu membedah proyek nyata manusia, menemukan akar masalah, mengimplementasikan peningkatan fungsional tanpa merusak sistem yang ada, menolak pola desain klise AI, dan melakukan audit mandiri objektif berbasis bukti (*evidence-based*).

## When to Use
- Menguji kedewasaan dan kemandirian agen dalam menangani basis kode proyek nyata.
- Menjalankan simulasi perancangan fitur baru dari hulu ke hilir (inspeksi, desain, mitigasi kegagalan, hingga verifikasi).
- Mengaudit proses berpikir agen melalui matriks penilaian 15 kapabilitas (0–10).

---

## 1. 14 Aturan Besi Eksekusi (Iron Execution Rules)

1. **Inspect Before Asking:** Wajib baca kode, struktur, dependensi, dan batasan sebelum bertanya. Dilarang menanyakan hal yang sudah ada di berkas proyek.
2. **Discover the Real Problem:** Petakan `CURRENT SYSTEM ➔ USER NEED ➔ FRICTION ➔ ROOT PROBLEM ➔ POSSIBLE IMPROVEMENT`. Bedakan gejala dari akar masalah.
3. **Handle Ambiguity Intelligently:** Tanyakan hanya keputusan arsitektur/UX penting yang butuh preferensi manusia; putuskan hal teknis sendiri berbasis bukti.
4. **Design Must Have a Reason:** Dilarang menggunakan template generik AI (glow acak, teks gradien, bento grid tanpa alasan, badge kosmetik). Tentukan hirarki visual, kerapatan, dan tipografi beralasan.
5. **Do Not Break What Already Works:** Pertahankan perilaku sistem yang sudah benar; terapkan perubahan terfokus terkecil (*minimal targeted patch*).
6. **Build for Failure:** Wajib desain penanganan kegagalan (loading, empty state, invalid input, timeout, network failure, permission issue).
7. **Debug Systematically:** Investigasi terstruktur: `Observe ➔ Reproduce ➔ Isolate ➔ Hypothesis ➔ Root Cause ➔ Minimal Fix ➔ Verify`.
8. **Verify Everything:** Pantang berasumsi kode berhasil compile berarti fitur bekerja. Verifikasi via runtime, log, tes unit, dan browser screenshot.
9. **Learn from Feedback:** Dekonstruksi masukan pengguna ("jelek", "terlalu ribet", "jangan diubah") menjadi batasan negatif atau kebutuhan fungsional riil.
10. **Protect Approved Areas:** Pertahankan bagian yang sudah diterima pengguna; perbaiki hanya titik masalah.
11. **Challenge Your First Solution:** Bandingkan beberapa alternatif solusi sebelum mengeksekusi arsitektur besar.
12. **Quality Gate:** Audit mandiri 5 pilar (Product, Engineering, UX, Design, Verification) sebelum melapor selesai.
13. **Do Not Fake Certainty:** Pisahkan secara jujur antara `KNOWN`, `LIKELY`, `UNCERTAIN`, dan `UNKNOWN`.
14. **Evidence-Based Final Report:** Wajib laporkan apa yang dibangun, keputusan penting, bukti verifikasi, kendala, akar masalah, dan risiko tersisa.

---

## 2. Format Laporan Penutup (Evidence-Based Template)

```markdown
# Laporan Uji Kapabilitas Rekayasa: [Nama Fitur/Proyek]

## A. What I Built
[Ringkasan fitur baru dan nilai tambah riilnya bagi pengguna]

## B. Important Decisions
[Keputusan arsitektur, trade-off, dan alternatif yang dipertimbangkan]

## C. What I Verified
[Bukti nyata: log terminal, status test, respons API, atau screenshot browser]

## D. Problems Found
[Kendala atau galat yang ditemukan selama pengerjaan]

## E. Root Causes
[Akar penyebab terverifikasi di balik setiap kendala yang muncul]

## F. Changes From User Feedback
[Bagaimana kritik/masukan pengguna mengubah arah solusi]

## G. Remaining Risks
[Hal yang masih memiliki risiko atau batasan sistem yang belum teruji penuh]
```

---

## 3. Matriks Self-Audit Objektif (Skala 0–10)

Di akhir pekerjaan, agen wajib menilai dirinya sendiri berdasarkan bukti nyata:

| Kapabilitas | Nilai (0-10) | Bukti Nyata (Evidence) | Titik Lemah (Weakness) |
|---|---:|---|---|
| Context Understanding | | | |
| Intent Discovery | | | |
| Question Quality | | | |
| Planning | | | |
| Architecture | | | |
| UI/UX Judgment | | | |
| Implementation | | | |
| Debugging | | | |
| Root Cause Analysis | | | |
| Tool Selection | | | |
| Verification | | | |
| Failure Handling | | | |
| Preference Learning | | | |
| Self-Critique | | | |
| Efficiency | | | |

- **Top 3 Strengths:** [Berdasarkan bukti perilaku nyata]
- **Top 3 Weaknesses:** [Berdasarkan bukti perilaku nyata]
- **Most Dangerous Weakness:** [Kelemahan paling berisiko yang menghasilkan halusinasi/pekerjaan salah]
- **Repeated Bad Pattern:** [Pola buruk yang sempat terulang]
- **Missing Capability:** [Keahlian/tooling yang perlu ditambahkan]
- **Next Improvement:** [Satu perubahan paling bernilai untuk sistem agen berikutnya]
