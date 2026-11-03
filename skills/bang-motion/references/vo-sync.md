# Sinkronisasi VO ↔ visual

Tujuan: setiap kata yang diucapkan punya objek yang bergerak di bawahnya,
dan setiap aksi visual jatuh di bawah kata yang menjelaskannya.

## Urutan yang benar

1. Tulis **jendela beat** dulu (tabel `start | end | naskah`), jangan menulis
   prosa lalu memotongnya.
2. Batasi panjang naskah per beat oleh jendela itu.
3. Generate TTS **per beat**, ukur, paskan, susun pada offset absolut.
4. Ukur onset hasil jadi, lalu **geser tween visual ke onset terukur**.

Kalau dibalik (visual dulu → naskah dipaksa muat), hasilnya suara yang
membicarakan arsitektur Host/Client/Server sementara layar menampilkan
"Tinggal Colok". Penonton mendengar dua cerita.

## Batas tempo

| Kondisi | Tindakan |
|---|---|
| TTS 10–30% lebih panjang dari jendela | `atempo` 1,05–1,30 — masih wajar |
| TTS >30% lebih panjang | **pendekkan naskahnya**, jangan dorong tempo |
| TTS lebih pendek dari jendela | biarkan jeda; `atempo` minimum ~0,92 (di bawah itu terdengar cadel) |

Tempo 1,6× masih "pas durasi" tapi terdengar tergesa dan merusak authority
narasi. Itu kegagalan yang tidak terlihat di angka durasi.

## Membangun satu track

Tiap segmen diberi `adelay` pada offset absolut lalu digabung `amix`:

```
ffmpeg -i s1.mp3 -i s2.mp3 -i s3.mp3 \
  -filter_complex "[0:a]adelay=800|800,apad[a0];\
                   [1:a]adelay=8200|8200,apad[a1];\
                   [2:a]adelay=15600|15600,apad[a2];\
                   [a0][a1][a2]amix=inputs=3:duration=longest:dropout_transition=0,\
                   atrim=0:34.4[out]" \
  -map "[out]" -ar 44100 -c:a libmp3lame -b:a 192k vo_sync.mp3
```

Pilih padding sesuai tujuan: `amix=duration=longest` mempertahankan input terpanjang, sedangkan `duration=shortest` memang berhenti pada input terpendek. `apad=whole_dur=<durasi_final>` per input membuat akhir track eksplisit; tanpa `whole_dur`, padding bisa tak terbatas, sehingga batasi dengan `atrim` atau `-t`. Jangan mengandalkan padding tak terbatas dan `-shortest` sebagai sinkronisasi.

## Narasi terukur dan pemulihan TTS

1. Sintesis per kalimat/beat ke berkas sementara, verifikasi ukurannya dan durasi `ffprobe`, lalu rename atomik. Simpan receipt hash dari teks + voice + parameter + versi penyedia; cache hanya boleh dipakai jika seluruh kunci cocok, bukan karena nama file kebetulan sudah ada.
2. Jika provider gagal, simpan status/log yang meredaksi query URL berisi token. Periksa versi paket dan dokumentasi/rilis upstream; uji pembaruan pada venv proyek terpisah dengan satu kalimat, bukan meng-upgrade runtime Hermes atau menyintesis ulang seluruh naskah. Jalur yang teruji dapat dipin di dependensi proyek; jangan menjadikan satu error jaringan sebagai larangan permanen memakai penyedia.
3. Ukur leading silence tiap klip, susun offset absolut, lalu simpan caption `{text,start,end,timing}` dari audio nyata. Jangan memotong caption tiap jumlah kata tetap hingga kalimat berhenti pada satuan seperti “per”; pecah di batas frasa dan ukur ulang durasi tampil.
4. Jika durasi total fleksibel, perpanjang beat ke batas frame berikutnya. Jika durasi terkunci, ringkas naskah atau gunakan tempo berbatas. Jangan memaksa narasi panjang menjadi cepat hanya demi menepati visual yang telanjur dibuat.
5. Bedakan durasi klip, onset ucapan, dan forced alignment kata. `silencedetect` mengukur aktivitas audio, bukan membuktikan kata/intonasi benar. LUFS dan true peak bukan penilaian naturalitas; gunakan review dengar/earshot sebelum mendeskripsikan kualitas suara.

## Mixing ducking yang mudah diverifikasi

Materialisasikan satu `narration.wav` dari klip ber-offset terlebih dahulu. Campur WAV itu dengan track SFX terpisah; struktur dua tahap menghindari graf negosiasi format yang sulit didiagnosis saat dua `amix` dan sidechain berbagi cabang.

Contoh dua track yang telah dijalankan pada FFmpeg:

```sh
ffmpeg -hide_banner -y -i narration.wav -i cues.wav \
  -filter_complex '[0:a]aformat=sample_fmts=dbl:sample_rates=48000:channel_layouts=mono,asplit=2[v][key];[1:a]volume=0.3,aformat=sample_fmts=dbl:sample_rates=48000:channel_layouts=mono[fx];[fx][key]sidechaincompress=threshold=0.025:ratio=8:attack=8:release=180[duck];[v][duck]amix=inputs=2:normalize=0,alimiter=limit=0.89[out]' \
  -map '[out]' -ar 48000 mixed.wav
```

- Letakkan `volume` **sebelum** `aformat` terakhir pada input sidechain: `volume` dapat memilih format lain lagi, sehingga mengunci format lebih awal belum cukup.
- Reproduksi kegagalan dengan input nyata dan graf kecil; setelah probe lulus, jalankan graf penuh. Probe dua input bukan bukti seluruh pipeline selesai.
- Periksa opsi terpasang dengan `ffmpeg -h filter=alimiter` sebelum menambahkan opsi versi lain. Kompensasi delay limiter dari pengukuran bila dibutuhkan; jangan menebak dukungan `latency`.
- Meter output dengan `loudnorm=...:print_format=json`; bedakan `input_i/input_tp` yang terukur dari `output_i/output_tp` prediksi normalisasi. Menjalankan meter ke null tidak menormalisasi file yang disimpan.
- Simpan asal/lisensi SFX dan musik. Cue sintetis original bukan bank rekaman berlisensi, dan lisensi library TTS bukan otomatis izin komersial keluaran penyedianya.

## Verifikasi onset (bukan perasaan)

```
ffmpeg -hide_banner -i vo_sync.mp3 -af "silencedetect=noise=-35dB:d=0.3" -f null - 2>&1 \
  | grep -i silence
```

Ambil setiap `silence_end` sebagai onset bicara, bandingkan dengan kolom
`start` beat (toleransi ±0,25 dtk — TTS menyisakan hening 0,1–0,3 dtk di
awal). Selisih lebih besar = salah offset, bukan salah TTS.

## Mengunci visual ke onset

- Teks/headline masuk **0,05–0,2 dtk setelah** onset, bukan sebelum.
- Aksi objek (masuk/colok/meledak) ditaruh di kata kerja yang menyebutnya.
- Ikon yang mewakili daftar (baca / jalankan / kerja) dimunculkan satu per
  satu mengikuti sub-frasa, bukan sekaligus.
- Penutup ("Itu MCP.") diberi pukulan terakhir: wordmark muncul di kata itu,
  bukan di akhir durasi.

## Headline = kata yang diucapkan

Bila narasi "AI kamu pintar, tapi buta", headline "Pintar, tapi Buta" —
bukan "AI Terisolasi". Pemirsa membaca dan mendengar kalimat yang sama,
sehingga sinkronisasi terasa bahkan sebelum orang memeriksa timing.

## Audio di halaman

- Ikat ke `gsap.ticker`: koreksi bila `|vo.currentTime - tl.time()| > 0.08`.
- `onComplete` → `vo.currentTime = 0` lalu `tl.play(0)`.
- Autoplay diblokir: pasang `pointerdown`/`keydown` sekali untuk mulai audio
  pada gestur pertama; jangan menampilkan teks "ketuk untuk mulai".
- Jangan biarkan audio berjalan dengan jamnya sendiri — semua export
  frame-by-frame akan kehilangan sinkronisasinya.
