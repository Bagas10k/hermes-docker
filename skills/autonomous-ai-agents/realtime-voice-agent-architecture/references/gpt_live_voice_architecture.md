# 8 Pilar Arsitektur GPT Voice / Live Natural

Cetak biru arsitektur percakapan suara real-time tingkat tinggi yang meniru dinamika percakapan manusia alami.

## 1. Voice Gateway (Full-Duplex Streaming)
- Komunikasi dua arah persisten melalui WebSocket (`ws://` / `wss://`) atau WebRTC DataChannel / MediaStream.
- Menghilangkan latensi siklus buka-tutup koneksi HTTP.
- Memungkinkan pengiriman pesan kontrol asinkron kapan saja di tengah jalannya transmisi data.

## 2. Voice Activity Detection (VAD) Terukur
- Analisis energi amplitudo (RMS) dan spektrum frekuensi vokal manusia di sisi klien atau tepi jaringan (*edge*).
- Menetapkan ambang dinamis (*dynamic thresholding*) untuk membedakan desah napas/kebisingan ruangan dengan artikulasi kata.
- Menentukan batas senyap ucapan (*speech pause threshold*, umumnya 350-500ms) untuk turn-taking yang responsif.

## 3. Real-Time Interruption (Barge-In)
- Hak veto instan pengguna untuk memotong ucapan AI kapan saja.
- Sinyal interupsi memicu dua tindakan atomik:
  1. Klien mengosongkan antrean audio (`audioQueue = []`), menghentikan elemen audio, dan mereset status UI.
  2. Server memicu `abortController.abort()` untuk memutus inferensi LLM dan menghentikan proses sintesis TTS yang belum diputar.

## 4. Streaming Response & Audio Chunking
- Model LLM mengalirkan token (*token streaming*) dengan `stream: true`.
- Mesin penyaring memecah aliran teks berdasarkan klausa gramatikal (tanda koma, titik, tanda tanya, titik koma).
- Setiap klausa matang langsung disintesis menjadi paket audio dan dialirkan ke klien.
- Dapat mengurangi waktu tunggu dibanding menunggu seluruh paragraf; angka TTFA perlu diukur end-to-end termasuk jaringan, antrean, dan pemutaran audio.

## 5. Turn-Taking Cerdas
- Membedakan jeda berpikir sejenak pembicara dengan akhir pembicaraan sejati.
- Menggunakan konfirmasi ganda: level desibel VAD turun di bawah ambang kebisingan DAN deteksi jeda STT selesai.

## 6. Conversation Engine Terpusat (Stateful Session)
- Mempertahankan riwayat percakapan (*conversation state*) di memori RAM server selama sesi panggilan aktif.
- Menghindari pengiriman ulang transkrip panjang secara berulang-ulang di setiap giliran bicara pengguna.

## 7. Integrasi Agent & Omni-Knowledge
- Penyuntikan telemetri sistem real-time (RAM, beban CPU, status proses latar belakang).
- Akses basis data, dokumen operasional, dan grafik pengetahuan yang relevan dengan otoritas pengguna.

## 8. Voice Engine Berprosodi Alami
- Sintesis ucapan dengan variasi intonasi, modulasi kecepatan bicara yang fleksibel (misal percepatan +15% untuk bahasa Indonesia agar tidak kaku), serta jeda antarkalimat yang proporsional.
- Pembersihan mutlak seluruh karakter pemformatan Markdown sebelum teks masuk ke pita suara synthesizer.
