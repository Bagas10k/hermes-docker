# Context Compaction & Prefix Cache Preservation Reference

Dokumentasi arsitektur pengelolaan batas memori percakapan, perlindungan KV prefix cache, dan mitigasi semantic drift.

## 1. Mekanisme KV-Cache Prefix Hashing
Model modern (Claude 3.5 Sonnet, GPT-4o, DeepSeek-V3, Gemini) menerapkan prefix caching berbasis hashing byte-level.
- Jika urutan pesan awal (System prompt, Memory core, User profile) berubah 1 karakter saja (misalnya timestamp disuntikkan di awal turn 0), **seluruh KV cache terbuang (100% cache miss)**.
- Akibat cache miss: latensi TTFT (Time-To-First-Token) melonjak dari ~300ms ke ~4.5 detik, dan biaya komputasi input berlipat ganda.

## 2. Struktur Tiga Kompartemen (Three-Tier Context Partitioning)
1. **Static Anchor Prefix (Tier 0)**:
   - System prompt dasar, aturan absolut, user profile, dan memori jangka panjang.
   - PANTANGAN: Dilarang mengedit atau menyuntikkan ringkasan dinamis di Tier 0.
2. **Compressible Middle History (Tier 1)**:
   - Log tool calls yang panjang (misalnya output `search_files` atau `read_file` besar yang telah diproses).
   - Riwayat percakapan usang (> 4 turn ke belakang).
   - Kandidat utama distilasi menjadi *Deterministic Execution Summary*.
3. **Active Working Window (Tier 2)**:
   - 2-4 turn terakhir (perintah pengguna saat ini dan respon agen langsung).
   - Wajib dipertahankan 100% verbatim agar tidak terjadi hilang arah percakapan (*conversational amnesia*).

## 3. Rumusan Distilasi Anti-Drift
Ringkasan handoff tidak boleh berupa narasi bebas yang mengaburkan instruksi. Format ringkasan wajib terstruktur:
- **Tujuan Aktif (Active Goal)**: Masalah yang sedang dipecahkan.
- **Batasan Keras (Hard Constraints)**: Larangan atau preferensi spesifik yang disebutkan pengguna.
- **Artefak Terverifikasi (Confirmed Artifacts)**: Daftar file/endpoint yang sudah selesai ditulis dan lulus verifikasi.
- **Status Terakhir (Current State)**: Langkah aktif berikutnya.
