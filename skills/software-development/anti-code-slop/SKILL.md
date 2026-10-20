---
name: anti-code-slop
description: "Use when reviewing, auditing, or optimizing code to detect and eliminate AI Code Slop."
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [code-quality, anti-slop, clean-code, debugging, code-review, optimization]
    related_skills: [systematic-debugging, test-driven-development, ponytail]
---

# Anti-Code Slop & Clean Engineering Doctrine

Doktrin ini adalah standar resmi untuk mendeteksi, membasmi, dan memveto **AI Code Slop**—pola kode khas AI yang tampak rapi di permukaan tetapi sebenarnya rapuh, bertele-tele, menelan error, atau over-engineered.

## Apa itu Code Slop?
Slop bukanlah kode rusak; slop adalah **ketiadaan keputusan arsitektur**. Output rata-rata model AI ketika tidak diberi batasan rasa dan ketelitian.

## 6 Dosa Besar Code Slop (Hard Blockers / High Severity)

1. **Menelan Error (Swallowed Errors):**
   - Menggunakan `catch (e) {}` kosong atau `except: pass` yang membungkam kegagalan sistem.
   - *Aturan:* Tangani error secara eksplisit atau biarkan melempar (*throw/re-raise*) agar terdeteksi.

2. **Sisa Debug Liar di Produksi:**
   - Meninggalkan `console.log` / `print()` debug di alur eksekusi aplikasi.

3. **Abstraksi Liar (Speculative YAGNI):**
   - Membuat interface/factory untuk 1 kelas/objek tunggal.
   - Membuat wrapper 40 baris untuk fungsi standar yang bisa selesai dalam 3 baris.

4. **Komentar Narasi Malas AI:**
   - Komentar yang hanya mengulang baris kode berikutnya (misal: `// initialize variable` di atas variabel).
   - Komentar hanya boleh menjelaskan **MENGAPA** (*intent*), bukan **APA** yang sedang terjadi.

5. **Defensive Programming Berlebihan:**
   - Triple null check `if (x !== null && x !== undefined && typeof x === 'object')` pada internal state yang sudah divalidasi.
   - Perbandingan boolean eksplisit `if (isValid === true)`.

6. **Tes Palsu (Test Slop):**
   - Menulis asersi yang tidak bisa gagal (`assert True`) atau mengubah nilai tes agar hijau semata tanpa menguji perilaku riil.

## Cara Menggunakan Scanner Otomatis

Jalankan pemindaian otomatis sebelum mempromosikan kode ke produksi:

```bash
python3 /home/ubuntu/.hermes/skills/software-development/anti-code-slop/scripts/code_slop_scan.py <TARGET_DIRECTORY>
```

Jika ditemukan temuan `HIGH`, rilis wajib diveto (Exit code 1).
