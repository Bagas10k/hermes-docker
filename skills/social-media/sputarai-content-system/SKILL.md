---
name: sputarai-content-system
description: "Use when producing, auditing, or maintaining Sputar AI."
version: 1.0.0
author: Bagas & Hermes Agent
---

# Sputar AI Content System (@sputarai)

SputarAI (`@sputarai`) berfokus pada edukasi AI agentik bagi orang awam, bukan lagi akun berita teknologi atau gawai. Mulai dari masalah sehari-hari, jelaskan konsep dengan bahasa sederhana, berikan contoh alur dan batas kewenangan agen. Perkembangan AI menjadi bahan belajar, bukan pemicu wajib unggah berita.

Untuk komentar dan DM, muat `instagram-publishing-automation` beserta `references/sputarai-live-api-check.md`. Bedakan akses baca yang berhasil, pengiriman balasan yang teruji, dan auto-reply yang benar-benar aktif; HTTP 200 pada endpoint baca tidak membuktikan kemampuan kirim. Jangan menghidupkan dispatcher berita lama hanya karena koneksi API valid.

## Comment → DM link
Untuk sistem kata kunci komentar → DM materi yang bisa dikonfigurasi per postingan, muat `references/comment-to-dm-runtime.md`. Runner dan timer terpisah dari mesin berita; bedakan terpasang standby, kampanye aktif, dan pengiriman nyata yang telah diverifikasi.

## 1. Lokasi Proyek & Layanan Inti
- **Direktori Kode Aktif:** `/home/ubuntu/hermes-backup/projects/penelitian-pola-pikir-ai/`
- **Layanan PM2:** `sputarai-ml-scorer` (ID 5, port HTTP `127.0.0.1:3055`)
  - Skrip server ML: `/home/ubuntu/sputarball/ml_scorer/server.py`
  - Venv: `/home/ubuntu/ml-resource-kit/.venv/bin/python`
  - Model: `sentence-transformers/all-MiniLM-L6-v2`
- **Database Utama:** SQLite `/home/ubuntu/hermes-backup/projects/penelitian-pola-pikir-ai/data/db/chronicle.sqlite`
- **Catatan Arsitektur Obsidian:** `/home/ubuntu/otak-koding/BUKU_CATATAN/010-arsitektur-sputarai-ml-trend-scorer.md`

## 2. Struktur Berkas Kunci
- `server.js`: Web server Express & endpoint API internal.
- `scripts/editorial-ai.js`: Generator naskah warta berbahasa Indonesia alami berbasis LLM.
- `scripts/instant-news-dispatcher.js`: Pengirim otomatis dan pemicu publikasi Instagram.
- `scripts/content-cms.js`: Pengelola artikel dan pipeline status berita.
- `public/carousel.html`: Template visual carousel 4 slide untuk rendering Puppeteer.

## 3. Standar Edukasi 4 Slide (@sputarai)
Satu unggahan mengajarkan satu pemahaman; carousel tepat 4 slide (rasio 4:5):
- **Slide 1:** Pertanyaan awam atau masalah sehari-hari dan hasil belajar.
- **Slide 2:** Konsep atau analogi sederhana; jelaskan setiap istilah teknis.
- **Slide 3:** Contoh masukan → langkah agen → hasil, termasuk batas dan peran manusia yang relevan.
- **Slide 4:** Rangkuman, latihan kecil atau pertanyaan diskusi.

Jangan mengarang hasil demo, penghematan, atau klaim bebas salah. Bedakan agen yang memilih langkah dan menggunakan alat dari otomatisasi beraturan. Gunakan data sintetis netral. Pedoman lengkap ada di skill `content-intelligence`, referensi `references/sputarai-editorial-direction.md`. Perubahan pedoman tidak membuktikan generator atau publisher telah diubah.

## Desain produksi yang telah disetujui
- Kontrak format kanonis: `/home/ubuntu/hermes-backup/projects/penelitian-pola-pikir-ai/content-studio/design-contract.json`.
- Default produksi: empat slide 1080×1350, masing-masing loop dua detik 30 fps; teks utama diam, ilustrasi SVG bergerak sesuai sebab-akibat, SFX palet yang disetujui tertanam di MP4.
- **VISUAL WAJIB ACAK setiap konten baru, WARNA BRANDING TETAP.** Palet warna identitas brand TIDAK BOLEH berubah (paper #F4F2EB, ink #171819, blue #1644A2, yellow #F3C84B, muted #4B4D50, Inter Tight). Yang WAJIB diacak setiap konten baru:
  1. Gaya ilustrasi SVG (objek, metafora visual, komposisi, sudut gambar).
  2. Struktur hook (rumus berbeda dari konten terakhir).
  3. Layout dan tata letak elemen dalam slide.
  4. Mencari referensi visual terbaru di internet sebelum mendesain.
- Pertahankan standar teknis (1080×1350, 2s loop, 30fps, SFX, penekanan kata) tapi BEBAS di aspek visual dan tematik.
- Tidak ada izin otomatis untuk publikasi, penggantian mesin berita, atau klaim generator sudah berjalan hanya dari persetujuan desain.

## Revisi visual cepat dan fokus feed
- Utamakan satu headline pendek dan satu visual utama pada cover; hindari banyak level tipografi, metadata, label diagram, serta footer verbal yang memecah fokus orang awam.
- Saat pemilik meminta fokus desain dan menonaktifkan QC, revisi langsung artefak yang dituju, render sekali, dan kirim gambar/video di respons yang sama. Dilarang keras menunda pengiriman artefak untuk menjalankan sub-agent QC, suite aplikasi, atau putaran inspeksi visual tambahan; nyatakan cakupan pratinjau tanpa mengklaim sudah diaudit.
- Dilarang keras membalas teks klaim "sudah dikirim" atau menampilkan status tanpa menyertakan tag lampiran `MEDIA:/path/absolut` pada respons tersebut. Jika artefak (PNG/MP4) telah selesai dirender, sertakan langsung path MEDIA fisiknya di akhir pesan agar langsung tampil di Telegram.
- Untuk pekerjaan motion, periksa MCP `bakmotion` yang sudah tersedia sebelum menulis pipeline baru. Gunakan kemampuan yang sesuai untuk storyboard/render/effects tanpa mengganti desain yang sudah disetujui dengan template generik. Jika adapter atau kontrol yang diperlukan belum ada, jelaskan keterbatasan spesifik dan gunakan kode kustom hanya pada bagian yang dibutuhkan; jangan menyimpulkan MCP tidak berguna karena satu hasil dibuat tanpa MCP.
- Bedakan katalog MCP yang berhasil dibaca dari render MP4 yang berhasil dijalankan. Jangan mengklaim pipeline MCP sudah menghasilkan video ketika hanya memanggil katalog atau storyboard.
- Perlakukan arah gaya baru sebagai kandidat sampai pemilik menilai gambarnya. Jangan mengubah publisher atau template produksi hanya dari persetujuan atas konsep.

## Palet suara yang disetujui
Untuk SFX, gunakan `references/approved-sfx-palette.md`: tiga rekaman Mixkit dan resep mix yang disukai pemilik sudah disimpan dalam bank aset privat. Persetujuan ini untuk karakter suara, bukan izin publikasi otomatis.

## Hook berbasis masalah dan arah produk
- Awali hook dari kejadian sehari-hari yang dikenali audiens, bukan nama teknologi atau daftar kemampuan AI. Sambungkan masalah → kebiasaan kerja yang perlu dipertanyakan → mekanisme solusi → tawaran jasa yang spesifik.
- Gunakan sudut provokatif yang mengkritik proses/kebiasaan, bukan menghina orang atau mengarang fakta. Jangan menyebut hook lebih efektif sebelum ada data respons audiens.
- Pertahankan ilustrasi dan gerak yang sudah disukai saat yang diminta hanya revisi hook. Pilihan kata baru tidak mengizinkan desain ulang seluruh komposisi.
- Untuk Bakmotion storyboard, `platform=universal` mendukung preview 4:5; `instagram` ditolak oleh tool. Pakai `beats` terstruktur dengan `narration` tidak kosong, bukan menaruh instruksi produksi di `script` yang dipecah menjadi teks layar. Pada perilaku yang teramati, durasi 2 detik diubah menjadi 4 detik; jangan mengklaim loop 2 detik dihasilkan langsung oleh MCP jika ekspornya memakai renderer terpisah.

## Landing Page & Funnel Konversi
- Landing page live: https://www.jajandigital.web.id/sputarai/ (file: /home/ubuntu/penelitian-pola-pikir-ai/public/sputarai/index.html)
- CTA WhatsApp konsultasi: 085764985114 (nomor khusus SputarAI, bukan WA pribadi Bagas)
- Auto-reply komentar IG aktif: timer systemd `sputarai-comment-dm.timer` 2 menit, config `config/comment-dm.json`, sending ON
- Alur konversi: komentar keyword → DM otomatis berisi link landing page → pengunjung klik → halaman jasa → tombol WA
- Caption DILARANG berisi disclaimer/kredit sumber ("Visual ini ilustrasi konsep...", rujukan Anthropic, label SFX Mixkit). Bersih tanpa label AI/sumber.

## Sistem Optimasi Konten Anti-Template
Panduan lengkap ada di `references/content-optimization-framework.md`. Inti:
- Siklus mingguan: kumpulkan sinyal → skor ide (matriks 5 kriteria) → hipotesis → produksi → evaluasi.
- Portofolio 70/20/10: 70% tema terbukti sudut baru, 20% variasi, 10% eksperimen berani.
- Ubah satu variabel per eksperimen. Bandingkan minimal 3-5 postingan sebelum simpulkan.
- Gunakan pembanding internal (median 10 postingan terakhir sendiri), bukan patokan universal.
- Bank kalimat pelanggan: catat persis kata-kata asli dari DM/komentar/WA, pakai sebagai hook.
- Rotasi hook dan struktur: maksimal 2x berturut-turut pola yang sama.
- Log eksperimen diisi tiap Jumat.

## 4. Gaya Bahasa & Anti-AI Slop
- Wajib 100% Bahasa Indonesia alami, santai, dan cerdas.
- Dilarang frasa klise terjemahan LLM kaku (seperti 'merevolusi lanskap', 'menyelam lebih dalam', 'game changer').
- Jangan gunakan emoji pada teks grafis UI/render.
