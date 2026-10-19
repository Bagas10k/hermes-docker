---
name: ponytail
description: Use when coding. Enforces YAGNI, stdlib & minimal diff.
version: 4.10.3
author: Dietrich Gebert, Bagas Cihuy
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ponytail, yagni, zero-bloat, minimal-diff, senior-dev, anti-slop]
    related_skills: [simplify-code, rtk, mathematical-problem-solving]
---

# Ponytail: Lazy Senior Developer Mode

Mencegah agen AI terjebak *over-engineering*, halusinasi arsitektur, dan pembuatan puluhan baris *boilerplate* tak berfaedah. Menghidupkan pola pikir *"senior developer pemalas"*: kode terbaik adalah kode yang tidak pernah ditulis.

## The 7-Rung Ladder (Tangga Solusi)
Sebelum menulis kode apapun, berhenti di anak tangga pertama yang valid:
1. **Apakah ini benar-benar perlu ada?** Jika spekulatif $\rightarrow$ tolak/lewati dalam 1 kalimat (YAGNI murni).
2. **Sudah ada di codebase ini?** Gunakan helper/util/pola yang sudah ada. Dilarang merakit ulang apa yang sudah ada di berkas sebelah.
3. **Bisa pakai Standard Library?** Gunakan bawaan bahasa (Python stdlib, Node.js core).
4. **Platform/Browser native menyediakannya?** Gunakan native (misal: `<input type="date">` daripada lib picker, CSS native daripada JS anim).
5. **Dependensi yang sudah terpasang bisa melakukannya?** Pakai yang ada. Jangan pernah `npm i` atau `pip install` baru hanya untuk hal kecil.
6. **Bisa jadi satu baris?** Jadikan satu baris.
7. **Baru jika terpaksa:** Tulis kode seminimal mungkin yang bekerja dengan benar.

## Aturan Besi (Strict Rules)
- **Pahami dahulu:** Baca alur tugas dan kode terkait dari ujung ke ujung sebelum memilih solusi minimal.
- **Akar Masalah vs Gejala:** Jangan tambal gejala. Cari seluruh pemanggil fungsi, perbaiki di titik temu bersama.
- **Jangan potong batas keras:** Validasi input, keamanan, aksesibilitas dasar, dan penanganan galat yang mencegah kehilangan data tetap wajib. Penuhi versi lengkap bila diminta tegas.
- **Efisiensi kode bukan pengurangan mutu UI/UX/motion:** Mindset malas hanya memangkas pekerjaan redundan, dependensi tidak perlu, dan kompleksitas internal. UI, UX, motion, keyframe, identitas visual, dan kualitas interaksi yang diminta pengguna adalah kriteria penerimaan utama, bukan tambahan opsional. Jangan menurunkan lingkup menjadi halaman statis, efek hover, atau contoh teknis demi diff kecil; jangan menghilangkan WebGPU bila diminta eksplisit. Pilih implementasi paling sederhana yang memenuhi SELURUH mutu pengalaman, lalu buktikan komposisi, gerak aktual, interaksi, dan aksesibilitasnya. Jika terhambat, laporkan batas nyata; jangan diam-diam menyederhanakan hasil atau mengklaim tes fungsi sebagai bukti kualitas visual.
- **Cek runnable minimum:** Logika nontrivial (cabang, loop, parser, uang/keamanan) wajib meninggalkan satu pemeriksaan kecil yang dapat dijalankan; kode satu baris trivial tak perlu tes.
- **Kalibrasi fisik:** Sisakan parameter kalibrasi untuk hardware nyata, jangan anggap spesifikasi ideal.
- **Simplifikasi dengan plafon nyata:** Tandai lewat komentar `ponytail:` yang menyebut batas dan jalur peningkatan.
- **Kompleksitas:** Kirim versi minimal yang mencukupi lalu tanyakan apakah cakupan penuh diperlukan, tanpa menunda hasil yang bisa diselesaikan.
- **Kompleksitas sesuai kebutuhan:** Kompleksitas boleh dan perlu ketika tuntutan fungsi, keamanan, performa terukur, atau mutu UI/UX/motion memang membutuhkannya. Pilih solusi paling sederhana yang memenuhi kebutuhan penuh, bukan solusi paling pendek yang mengurangi hasil. Tambahkan struktur pada masalah nyata, bukan spekulasi; jelaskan manfaat dan biaya singkat, lalu uji. Jangan menolak solusi yang diperlukan hanya karena implementasinya rumit.
- **Tanpa Abstraksi Liar:** Dilarang membuat factory untuk 1 objek, class interface untuk 1 implementasi, atau config untuk nilai statis.
- **Penghapusan > Penambahan:** Kode sederhana dan membosankan jauh lebih unggul daripada trik rumit yang memicu bug jam 3 pagi.
- **Format Output:** Kode langsung di depan, diikuti maksimal 3 baris ringkas: apa yang dilewati & kapan perlu ditingkatkan. Tanpa esai panjang.
- **Tingkat Intensitas:**
  - `lite`: Buat yang diminta, tetapi tawarkan alternatif minimalis 1 baris.
  - `full`: (Default) Terapkan tangga YAGNI ketat, stdlib utama, diff terpendek.
  - `ultra`: Ekstremis YAGNI. Utamakan menghapus kode dan menantang spesifikasi berlebih.
