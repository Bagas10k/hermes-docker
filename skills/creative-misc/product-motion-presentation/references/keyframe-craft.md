# Keyframe & kerapian gerak (GSAP di HyperFrames)

Dipakai saat menulis atau merevisi timeline adegan, terutama bila draf dikeluhkan "kurang halus" atau "belum rapi". Sintaks keyframes dan CustomEase ada di skill `gsap` bagian 6, daftar plugin dan resep di `gsap/references/video-capability-map.md`; berkas ini memuat keputusan craft dan QC-nya.

## 1. Satu elemen, satu deret keyframe

Gerak multi-tahap pada elemen yang sama (masuk → nudge → keluar) ditulis sebagai satu tween, sehingga kecepatan di setiap titik keyframe ditentukan ease segmen, bukan oleh sambungan dua tween yang kebetulan berdekatan.

```js
tl.to('#%%card', {
  duration: 1.6, ease: 'none',            // kurva seluruh blok: datar, biar segmen yang membentuk
  keyframes: {
    '0%':   { y: 40, autoAlpha: 0 },
    '35%':  { y: 0, autoAlpha: 1, ease: 'expo.out' },
    '80%':  { y: -4 },                     // hold yang tetap hidup (gerak mikro searah)
    '100%': { y: -28, autoAlpha: 0, ease: 'power2.in' },
    easeEach: 'power1.inOut'
  }
}, 0.2);
```

- Keadaan awal tersembunyi tetap ditulis lewat CSS/`gsap.set` (aturan frame 0 di `scene-generator-delegation.md`).
- Jangan menumpuk tween lain pada properti yang sama selama blok keyframe berjalan.

## 2. Ease menurut peran (titik awal, 30 fps)

| Peran | Ease | Durasi patokan |
| --- | --- | --- |
| Masuk UI/kartu/teks | `expo.out`, `power3.out`, atau CustomEase `0.16,1,0.3,1` | 0,45–0,7 dtk |
| Keluar | `power2.in` / `power3.in` | 40–50% durasi masuk |
| Pop stiker/badge | `back.out(1.4–1.7)` | 0,35–0,5 dtk |
| Kamera push/zoom momen kunci | `power3.inOut` / `expo.inOut` | 0,6–0,9 dtk |
| Kamera saat hold baca (opsional) | satu arah, `power1.inOut`, ≤ 3% scale | sepanjang hold |
| Kursor berpindah | `power2.inOut`, lalu tekan scale 1→0,92→1 | 0,5–0,8 dtk + 0,12 dtk |
| Angka menghitung | `power2.out` / `expo.out` | 0,6–1,2 dtk |
| Denyut glow | `sine.inOut` yoyo (satu-satunya tempat yoyo) | 0,4–0,6 dtk per setengah siklus |

- Satu ease untuk semua gerak (misalnya `sine.inOut` di semua kamera dan glow) membuat film terasa mengambang tanpa aksen.
- `back.out(3)` pada elemen UI terlihat seperti mainan; simpan pantulan besar untuk aksen tunggal yang disengaja.
- Di sambungan transisi, cerminkan ease (`power3.in` keluar → `power3.out` masuk) agar kecepatan sama di kedua sisi potongan.

## 3. Kamera: satu lapis bermotivasi

- Maksimal satu wrapper kamera beranimasi per adegan. Zoom pembuka, zoom momen kunci, dan pull-out ditulis sebagai satu track keyframe pada wrapper itu.
- Setiap gerak kamera punya sebab: push ke target klik/angka, pull-out saat sistem terbentuk, match-cut ke adegan berikut. Dalam satu hold, arah kamera konsisten; tidak ada kamera yoyo.
- Bila tetap perlu drift: satu lapis, satu arah per adegan, ≤ 2% scale atau ≤ 8 px, tanpa rotasi, dan tidak di-compose dengan zoom.
- Batasi scale dan `transform-origin` supaya elemen penting tetap di dalam kanvas pada puncak zoom.

## 4. Checklist kerapian tata letak (per adegan)

- Margin aman tetap (titik awal 1440×1080: ±80 px kiri/kanan, ±64 px atas/bawah). Judul memakai x dan baseline yang sama antar-adegan.
- Ukuran dan posisi perangkat konsisten antar-adegan berurutan; serah-terima memakai angka left/top/width/height.
- Komposisi mengisi sebagian besar frame. Area kosong lebih dari separuh layar terbaca belum selesai.
- Label dan kartu sejajar pada tepi atau baseline yang sama; jarak antar-elemen diambil dari satu skala spasi (8/16/24/32/48).
- Stiker/badge: 2–3 per adegan, tersebar di kuadran berbeda di luar titik fokus, tidak menutupi bezel perangkat, label, atau teks, dan tidak terpotong tepi frame termasuk saat rotasi dan zoom puncak.
- Satu fokus per momen: maksimal dua elemen besar bergerak bersamaan; sisanya diam atau bergerak mikro.
- Setiap elemen yang masuk punya animasi keluar atau bertahan sampai cut. Aksi terakhir selesai (ekor ease-out) sebelum transisi dimulai.

## 5. QC grafik keyframe (sebelum render)

Pakai versi hyperframes yang di-pin proyek.

```bash
npx --yes hyperframes@<pin> keyframes compositions/sN.html --json > $TMPDIR/kf_sN.json
npx --yes hyperframes@<pin> keyframes compositions/sN.html --shot $TMPDIR/kf_sN_cam.png --selector '#sN-cam'
```

- Output teks `--shot` sudah mencetak rentang keyframe dan setiap lapis `composed with`. Baca teks itu dulu; PNG onion-skin (9 sampel default, `--from/--to` untuk rentang) dipakai untuk melihat lintasan. `--layout strip` hanya berlaku untuk selector SVG.
- Jalankan perintah tanpa pipe (`| tail`) bila exit code dibutuhkan, karena exit pipeline adalah exit perintah terakhir.
- Struktur JSON yang teramati pada v0.9.33: `compositions[0].tweens[]` dengan `start`, `end`, `ease`, `target`, `keyframes[].properties`, `composedWith[].selector`. Periksa `_meta.version` bila hasil parsing aneh.

Analisis otomatis (skrip skill, sudah diuji pada 11 adegan r7):

```bash
S=~/.hermes/skills/creative-misc/product-motion-presentation/scripts/kf_qc.py
python3 $S $TMPDIR/kf_sN.json --png $TMPDIR/lanes_sN.png   # laporan + grafik lajur
python3 $S $TMPDIR/kf_sN.json --strict                      # exit 1 bila gagal syarat
python3 $S --selftest
```

Skrip mencetak distribusi ease, `back.out` > 2, overlap target+properti, sambungan patah (kecepatan ujung tween A tidak sama dengan awal tween B yang menempel, misalnya `expo.out` lalu `none`), lapis kamera (nama wrapper cocok `cam|rig|drift|zoom|camera|push`), puncak tween aktif, dan jumlah tween buta-QC. Grafik lajur: satu baris per target, abu tua = tween, abu muda = ambient sepanjang adegan, merah = sambungan patah/overlap. Pakai grafik ini untuk melihat jeda kosong dan fokus ganda sebelum render.

Syarat lulus (`--strict`):
- Tidak ada satu ease yang menguasai lebih dari separuh tween, dan tidak ada `back.out` di atas 2.
- Nol overlap target+properti dan nol sambungan patah.
- Kamera: tepat satu lapis beranimasi.
- Nol tween buta-QC. Analyzer statis tidak bisa menghitung tween yang posisi, durasi, target, atau nilainya berupa variabel JS, loop, atau fungsi (start dilaporkan ~1e9 dan end kosong). Generator Python wajib menginterpolasi angka literal ke JS (`duration:0.6`, posisi `1.2`, selector tetap), bukan `for` atau `const d=...` di skrip adegan. Tanpa itu, sebagian besar timeline tidak terlihat oleh QC.
- Puncak tween aktif dibandingkan antar-adegan; puncak tinggi di satu momen adalah kandidat fokus ganda yang dicek di frame.

Baseline r7 (dinilai 3/10), untuk pembanding ronde berikutnya: 11 dari 11 adegan GAGAL. Semua adegan punya kamera 3 lapis (`cam`+`rig`+`drift`), 9 adegan punya 22–27 tween buta-QC (lebih banyak dari tween yang terbaca), `back.out` 2,2–3 di s6/s7/s9/s11, overlap di s3/s9/s11, sambungan patah di s7/s9.

## 6. Lembar keyframe sebelum kode

Sebelum menulis JS satu adegan, tulis tabel keyframe pendek di brief atau komentar generator. Satu baris per elemen yang bergerak:

| Elemen | Detik lokal: keadaan | Ease per segmen | Sebab |
| --- | --- | --- | --- |
| kamera `#sN-cam` | 0: scale 1 → 0,9: 1,18 fokus tombol → 3,2: 1,18 → 3,9: 1 | `power3.inOut`, hold `none`, `power3.inOut` | klik Terbitkan |
| kursor | 0,4: luar → 1,1: tombol → 1,2: tekan 0,92 → 1,32: 1 | `power2.inOut`, `power2.out` | |

Tabel ini menjadi kontrak: setiap baris = satu tween `keyframes`, detik-detiknya literal, dan aksi baris berikut mulai 0,1–0,2 dtk sebelum baris sebelumnya selesai. QC membandingkan grafik lajur dengan tabel; elemen yang tidak ada di tabel tidak boleh bergerak.
