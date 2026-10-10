---
name: motion-visual-systems
description: Use when designing motion for web interfaces or videos.
---
# Motion & Visual Systems

Gunakan untuk animasi web, presentasi, dan video motion. Muat juga `creative/genjutsu/_jutsu/motion-principles` untuk aksesibilitas/performa web dan `audio-driven-motion-graphics` untuk produksi video. Motion bukan hiasan: objek, posisi, dan waktunya harus menjelaskan aksi.

## 1. Pilih visualisasi dulu
1. Tuliskan **apa yang berubah** dan bukti visual sebelum memilih efek. `objek awal → tindakan → objek akhir` adalah kontrak per beat. Untuk konsep abstrak, tampilkan representasi yang jujur dan dikenali (berkas, tabel, terminal, laporan), bukan kartu generik sebagai bentuk fisik objek.
2. Pertahankan satu objek utama melintasi beat ketika relasinya masih sama. Jangan ganti seluruh halaman hanya karena kalimat narator berganti. Tempatkan objek yang sama pada posisi berdekatan agar mata bisa mengikutinya.
3. Hirarki: satu fokus utama, detail pendukung seperlunya, teks layar satu frasa. Pilih ikon/SVG yang menggambarkan *benda atau status*, bukan dekorasi. Hindari bayangan, glow, partikel, dan morph jika tidak membantu pemahaman.
4. Tentukan titik asal dan tujuan gerak: dari pemicu (tombol/permintaan), ke objek bekerja (panel), ke hasil. Jika penonton tak bisa menunjuk sebab dan akibat tanpa suara, revisi visual sebelum menambah animasi.

## 2. Peran gerak → kurva
- **Masuk / muncul:** cepat mulai lalu melambat (`ease-out`, contoh `cubic-bezier(.2,0,0,1)`); translasi pendek + opacity. Elemen utama boleh pegas teredam, bukan selalu overshoot.
- **Pindah keadaan / shared element:** percepatan dan perlambatan (`ease-in-out`) sambil mempertahankan identitas objek. Jangan reset posisinya tiba-tiba.
- **Keluar:** `ease-in`, lebih cepat dan lebih ringan daripada masuk; jangan tutupi penerusnya terlalu lama.
- **Umpan balik mikro:** respons cepat, tanpa gerak besar; status nyata baru hijau setelah operasi selesai.
- **Gerak yang mengikuti scroll, pointer, audio, atau data:** linear terhadap progres input; easing tambahan membuatnya tertinggal dari penyebabnya.
- **Penekanan:** satu peristiwa penting boleh skala ringan / underline / warna. Pegas pantul hanya untuk objek yang wajar terasa elastis, bukan teks penjelasan atau semua kartu.
- **Hold:** beri waktu baca; animasi berulang yang tidak menambah informasi adalah noise. Timing awal web dari `motion-principles`: mikro 100–150 ms, UI 200–300 ms, page 300–500 ms; sesuaikan konteks, jangan dijadikan aturan kaku video.

## 3. Rasa smooth yang dapat diuji
- Kurva posisi dan opacity harus dimulai/berakhir tanpa loncatan. Periksa kecepatan relatif: aksen bergerak cepat, panel utama lebih tenang, latar paling lambat atau diam. Hindari semua layer bergerak serentak.
- Tumpang-tindihkan akhir beat lama dan awal beat baru sedikit bila relevan; pastikan hanya satu judul utama terbaca pada tengah transisi. Gunakan interpolasi ter-clamp di Remotion agar tak overshoot di luar rentang.
- Web: utamakan `transform`/`opacity`, tidak animasikan ukuran/top/left per frame; jaga fokus keyboard dan `prefers-reduced-motion`. Video: hormati safe area, suara dan efek benar-benar masuk ke audio MP4; ukur durasi dengan ffprobe.
- Jangan sebut "60 FPS", "tanpa jank", atau "sinkron dengan suara" hanya dari kode. Periksa rekaman pada perangkat target/CPU lambat dan frame sekitar transisi, serta dengar hasil audio aktual.

## 4. Gerbang mutu sebelum kirim
- Ambil still **sebelum, tengah, sesudah** tiap perpindahan; untuk gerak halus inspeksi klip pendek, bukan cuma 2 gambar atau angka perbedaan piksel.
- Cek: objek tetap dikenali, tidak bertabrakan, tidak melompat, bacaannya cukup lama, keluaran/galat tidak dipalsukan, dan SFX memperkuat peristiwa alih-alih menutupi narasi.
- Untuk web, uji keyboard + reduced motion + viewport mobile/desktop; untuk video, probe durasi/resolusi/audio, sampling frame dan dengarkan campurannya. Uji tanpa suara untuk paham mekanisme; uji audio saja untuk cerita.
- Bila gerak tidak meningkatkan arah perhatian atau sebab-akibat, hapus. Skor keindahan bukan bukti; minta penonton tunjuk bagian yang dipahami dan yang terasa mengganggu.
- Jangan memakai satu pola kartu bertumpuk, kamera maju, dan label baru berulang sebagai seluruh video: hasilnya monoton dan dapat ditebak walau kurva easing halus. Rancang *peristiwa* yang mengubah keadaan objek: pemicu manusia → manipulasi langsung → sistem bereaksi → hambatan/galat yang terlihat → keputusan/perbaikan → hasil yang bisa dibandingkan. Variasikan komposisi dan jenis gerak sesuai aksi, bukan variasi dekoratif; pertahankan kontinuitas objek utama.
- Untuk rasa interaktif dalam video non-interaktif, gambarkan sebab yang eksplisit (kursor menekan, berkas diseret, sel diedit), respons segera, serta konsekuensi yang bertahan pada adegan berikutnya. **Tiap proses aktif memerlukan aktor visual yang tepat sasaran**: kursor untuk klik/seleksi, sorotan baris untuk pembacaan, caret untuk pengetikan, progress untuk kerja berjalan, dan status/hasil untuk verifikasi. Jangan tempel kursor dekoratif: ujungnya harus mengenai target *sebelum* keadaan target berubah; periksa frame sebelum dan sesudah. Jangan menyebut video interaktif sungguhan bila penonton tidak bisa mengendalikan hasil.
- Gerbang pembeda: putar 10 detik tengah tanpa audio kepada orang awam; jika ia hanya menyebut 'kartu berganti' atau tidak dapat menunjuk apa yang dipicu dan berubah, storyboard gagal meski frame terlihat rapi. Perbaiki mekanisme visual sebelum rerender 30 detik.

## Resep lintas platform
- CSS: `.enter { opacity:0; transform:translateY(12px) } .enter.ready { opacity:1; transform:none; transition:transform .28s cubic-bezier(.2,0,0,1),opacity .2s ease-out }` dan `@media(prefers-reduced-motion:reduce){.enter.ready{transition:none}}`.
- Remotion: `interpolate(frame,[a,b],[0,1],{easing:Easing.bezier(.2,0,0,1),extrapolateLeft:'clamp',extrapolateRight:'clamp'})`; gunakan `spring({frame:local,fps,config:{damping:16,stiffness:170,mass:.8}})` hanya untuk fokus yang layak berpegas. Kurva adalah titik awal yang harus ditinjau secara visual, bukan nilai optimum universal.

## Rujukan internal
- `creative/genjutsu/_jutsu/motion-principles` — timing, easing, a11y, performa.
- `creative-motion-lab` — fisika, shader/canvas bila perlu.
- `audio-driven-motion-graphics` — storyboard, rendering dan QA.
- `storytelling-narasi-video` — objek dulu, baru konsep; bahasa lisan dan sinkron cerita.
