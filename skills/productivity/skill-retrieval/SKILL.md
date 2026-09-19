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
