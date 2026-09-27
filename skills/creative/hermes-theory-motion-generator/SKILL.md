---
name: hermes-theory-motion-generator
description: Generate visual-first theory motion videos from a prompt.
---

# Hermes Theory Motion Generator

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
