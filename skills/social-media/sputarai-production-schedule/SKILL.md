---
name: sputarai-production-schedule
description: "Use when scheduling or distributing SputarAI daily content."
version: 1.0.0
author: Bagas & Hermes Agent
---

# SputarAI Daily Production & Distribution Schedule

Panduan operasional jadwal harian pembuatan dan distribusi konten edukasi AI agentik SputarAI (@sputarai).

## 1. Spesifikasi Jadwal
- **Frekuensi posting:** Setiap hari (7x seminggu).
- **Target publikasi manual:** Pukul 08:00 WIB oleh Mas Bagas.
- **Waktu eksekusi generator & pengiriman pratinjau:** Pukul 21:00 WIB (malam sebelumnya).
- **Cronjob id:** `28cbe9034067` (`0 21 * * *`, daily 21:00 WIB).

## 2. Alur Operasional (Malam → Pagi)
1. **21:00 WIB (Sistem Otomatis):**
   - Cronjob memicu script/agent generator harian.
   - Pilih topik masalah UMKM acak (di luar 2 topik terakhir) dengan sudut kebiasaan keliru → solusi agen.
   - Render 4 slide MP4 durasi 4 detik (120 frame native @ 30fps), SFX termix ganda (0.3s & 2.3s).
   - Pastikan teks bebas overlap (`z-index: 2`, SVG hero `top: 620px` atau lebih rendah).
   - Buat draf caption bebas disclaimer/kredit sumber.
   - Kirimkan langsung ke Telegram dalam format `MEDIA:/path/motion-full-XX.mp4` agar langsung terlampir sebagai video fisik.
2. **Sinkronisasi Kata Kunci Campaign (Wajib):**
   - Daftarkan kata kunci CTA baru dari slide 4 (misal `STOK`, `GUDANG`, `NOTA`, `CHAT`) ke dalam berkas `config/comment-dm.json` pada array `campaigns[0].keywords`.
   - Jalankan `python3 -m unittest tests/test_comment_dm.py` untuk memastikan konfigurasi lolos validasi.
3. **21:00 - 07:59 WIB (Review Mas Bagas):**
   - Mas Bagas meninjau video pratinjau dan caption santai semalaman.
   - Jika perlu penyesuaian teks atau visual, revisi cepat dilakukan sebelum jam tayang.
3. **08:00 WIB (Publikasi Manual):**
   - Mas Bagas mengunggah 4 slide MP4 ke Instagram Feed @sputarai.
   - Auto-reply komentar (`sputarai-comment-dm.timer`) otomatis siaga mendeteksi kata kunci dari audiens dan mengirimkan link landing page ke DM.
