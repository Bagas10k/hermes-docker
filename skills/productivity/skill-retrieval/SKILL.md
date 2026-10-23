---
name: skill-retrieval
description: "Dynamic skill retrieval & curation: retrieve and inject only query-relevant skills on the fly."
version: 1.0.0
author: ChonSong & Hermes
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skills, retrieval, curation, token-optimization, agentskillos]
---

# Skill Retrieval (Dynamic Skill Curation)

Skill Retrieval memecahkan masalah kelebihan token pada agen yang memiliki ratusan skill terpasang. Alih-alih memuat seluruh pustaka ke context window, sistem mengindeks kemampuan dan menginjeksi top-3 sampai top-20 skill paling relevan secara dinamis.

## Arsitektur

1. **Flat Indexing**: Menyusun seluruh deskripsi skill ke dalam indeks pencarian terstruktur.
2. **Pre-Filtering**: Menyaring kandidat skill teratas berdasarkan kesesuaian semantik / intent pengguna.
3. **LLM Gate / Dynamic Bundle**: Mengelompokkan skill yang relevan dengan level pembebanan:
   - `must` (★): Wajib dimuat untuk tugas saat ini.
   - `should` (▸): Disarankan untuk alur kerja pelengkap.
   - `consider` (·): Opsional jika dibutuhkan penanganan khusus.

## Prosedur Resolusi Nama Skill

1. Jika nama kanonis belum pasti, panggil `skills_list` lebih dulu dan pilih nama persis dari hasilnya.
2. Panggil `skill_view` dengan nama kanonis **tanpa** menambah tanda baca, komentar, status, sufiks diagnosis, atau tebakan apa pun ke argumen nama.
3. Jika pemanggilan gagal, baca alasan kegagalan dan ubah strategi sekali; jangan mengulang argumen identik. Cari ulang melalui `skills_list` atau pilih skill kelas-level terdekat.
4. Setelah nama berhasil dimuat, pertahankan ejaan persis itu untuk seluruh sesi. Nama tampilan, kategori, dan path bukan lisensi untuk “memperbaiki” identifier.

**Pitfall:** Jangan menggabungkan catatan seperti `invalid?` atau komentar debugging ke identifier skill — resolver memperlakukan seluruh string sebagai nama literal, sehingga retry identik hanya mengulang kegagalan tanpa menambah bukti.
