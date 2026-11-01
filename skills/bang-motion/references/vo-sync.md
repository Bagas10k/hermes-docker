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

`apad` wajib per input; tanpa itu `amix` memotong segmen terpendek.

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
