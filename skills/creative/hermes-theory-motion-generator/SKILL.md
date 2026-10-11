---
name: hermes-theory-motion-generator
description: Generate visual-first theory motion videos from a prompt.
---

# Hermes Theory Motion Generator

## Gate produksi visual motion Bagas Cihuy

WAJIB sebelum generate motion: untuk proyek theory-motion, baca SELURUH `VISUAL_MOTION_PRODUCTION_STANDARD.md` dan `VISUAL_MOTION_RULES.md` di root proyek sebelum naskah, scene plan, aset, coding atau render. Standar dari PDF Bagas Cihuy mewajibkan pemilihan 12 jenis visual berdasarkan relasi informasi, scene plan terstruktur (tujuan, narasi, alasan visual, entities/relationships, animation beats, risiko/validasi, fallback), manifest asal/lisensi aset, animatic sebelum final, serta uji tanpa suara, audio saja, mobile dan rubrik review berbukti. Jangan skip gate atau mengarang skor; pemeriksaan belum dilakukan harus dilaporkan belum diuji. Dokumen tersebut menjadi standar produksi dan QA; brief terbaru pengguna mengalahkan default. Standar dan atribusi: Bagas Cihuy.

- Utamakan satu tujuan belajar dan satu studi kasus konsisten. Demonstrasikan input → tindakan/tool → data kembali → hasil; kartu teks dan glow bukan demonstrasi proses.
- Labeli data buatan dan tool-call animasi sebagai SIMULASI / DATA ILUSTRATIF. Jangan klaim angka riil, eksekusi nyata, laporan diterbitkan atau audit bebas kesalahan tanpa bukti.
- Bedakan LLM, pola kontrol agent, dan sifat agentik: bukan tangga kecerdasan resmi. Agentik dapat memakai satu atau beberapa agent; multi-agent tidak otomatis lebih benar.
- Storyboard wajib SEBELUM render: interval frame, VO, objek aktif, kamera, perpindahan data, dependensi status, SFX dan panduan pemilihan akhir.
- Default lanjutan proyek: tema terang Warm Paper, Navy, Cobalt/Amber; 1080×1350 4:5, 60fps. Susun ulang vektor portrait, jangan crop/letterbox landscape. Default ini menggantikan resolusi/render lama di bawah ketika melanjutkan proyek tersebut.
- Periksa preview 360px: informasi utama target minimal 16px efektif. Ukuran efektif = font sumber × zoom kamera × lebar preview / lebar komposisi. Label aktif tidak boleh terpotong; overview mikro tidak boleh membawa pesan utama.
- Hitung kontras warna aktual; jangan klaim WCAG dari vision. Normal text ≥4.5:1, large text ≥3:1.
- Ukur durasi VO sebelum timeline; singkatkan naskah atau panjangkan adegan, jangan kompres ucapan ekstrem. Target percepatan tambahan ≤1.25×. Periksa seluruh audio, sinkronisasi, truncation, masking; ukur loudness/peak.
- Sebelum memilih jalur produksi, periksa kapabilitas MCP yang tersedia sesuai kebutuhan visual/motion spesifik melalui discovery on-demand; gunakan bila mempercepat artefak nyata atau memberi verifikasi yang tidak tersedia pada tool lokal. Jangan memanggil MCP hanya karena tersedia, jangan instal/otorisasi server tanpa kebutuhan jelas; Remotion/aset existing tetap dipakai bila lebih langsung.
- Reuse helper/aset, deterministic frame motion, tanpa dependencies baru atau install otomatis sebagai QA. Jalankan tsc dan tes terkait; generic tests tidak membuktikan kualitas visual.
- Render langsung: `npx remotion render src/index.ts <CompositionId> output/<nama>.mp4 --gl=angle --concurrency=2`. Hindari wrapper hardcoded landscape. Background notify=true lalu tunggu exit; prefix Output/Rendered bukan sukses.
- ffprobe artifact aktual; contact sheet, sample fokus full-resolution, adjacent zoom/morph/transfer dan mobile preview wajib. Inspeksi vision yang bertentangan dengan gambar/kode/probe tidak valid; ulang atau laporkan QA belum tersedia.
- Laporkan lulus/gagal/belum diuji secara terpisah; uji audiens tidak bisa diganti skor vision. Jangan publikasi tanpa izin. Bagian publikasi otomatis di bawah bukan otorisasi untuk proyek ini.
- Stop final jika label utama terpotong, VO belum diperiksa, simulasi diklaim nyata, atau materi hanya terbaca saat pause.
- Untuk revisi setelah skor pengguna rendah, bandingkan referensi dan render pada batas adegan, bukan hanya contact sheet. Gunakan MCP lokal `training-kit/motion_reference_mcp.py` bila bekerja di theory-motion: `scan_boundaries` menandai pergantian piksel besar, `sample_transition` memberi frame sebelum/saat/sesudah, dan `check_continuity` menguji deklarasi ID objek. Sinyal ini hanya mengarahkan inspeksi; jangan mengklaim morph, kualitas, atau peningkatan skor tanpa playback dan penilaian pengguna.

Standar rekayasa otomatisasi video motion graphics edukasi sains/teori ("Visual-First Motion Engine"):
Prinsip utama: Penonton wajib bisa memahami alur teori fisis/sains hanya dengan melihat visualnya (bahkan tanpa audio/suara).

## Alur Eksekusi Otomatis

Ketika Mas Bagas memberikan instruksi seperti:
`Jelaskan tentang [Teori / Konsep A]` atau `Buatkan motion tentang [Teori A]`

1. **Riset & Naskah Narasi Visual-First:**
   - Susun naskah edukatif 20-30 detik (4-5 kalimat padat).
   - Setiap kalimat wajib memiliki padanan metafora visual konkret (misal: potongan melintang benda berongga, tabung ukur air terdesak, panah vektor gaya $F_A$ vs $W$, partikel acak vs teratur).
   - Hindari kartu teks statis yang membosankan. Utamakan diagram fisis, simulasi gerak, dan komparasi visual berdampingan.

2. **Sintesis Audio & Transkripsi Stempel Waktu:**
   - Hasilkan audio via `edge-tts` (suara natural `id-ID-ArdiNeural` atau `id-ID-GadisNeural`).
   - Ekstrak stempel waktu per kata dan per kalimat menggunakan `faster-whisper` CPU int8 via `/home/ubuntu/hermes-motion-engine/pipeline/transcriber.py`.

3. **Choreography & Remotion Compilation:**
   - Petakan setiap rentang waktu kalimat $[t_{start}, t_{end}]$ ke adegan Remotion.
   - Render MP4 vertikal 1080x1920 30 FPS via Remotion headless CLI:
     `npx remotion render <CompositionId> <OutputPath> --concurrency=4 --gl=angle`

4. **Pengiriman & Akses Publik:**
   - Video otomatis tersedia di symlink publik:
     `https://www.jajandigital.web.id/kanvas/media/motion/<nama_video>.mp4`
   - Kirimkan langsung ke Telegram menggunakan `MEDIA:/path/to/video.mp4`.
   - Pastikan kepatuhan mutlak pada Doktrin Nol Emoji di seluruh visual dan pesan.
