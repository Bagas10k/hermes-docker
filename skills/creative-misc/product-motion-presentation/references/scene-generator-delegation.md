# Generator adegan + delegasi paralel (HyperFrames)

Dipakai saat membangun film baru ≥ 6 adegan dari storyboard yang sudah ACC dan pekerjaannya dibagi ke beberapa worker. Tujuannya: worker tidak pernah menyentuh berkas yang sama, dan setiap worker bisa menguji adegannya sendiri tanpa menunggu yang lain.

## Struktur berkas (`build/`)

| Berkas | Pemilik | Isi |
| --- | --- | --- |
| `gen_rN.py` | mandor | BASE CSS (palet, `@font-face`, kelas umum), ART (stiker SVG), HELP (helper JS timeline), `TIMES {sid:(start,dur)}`, `compose()` per adegan, penulis `index.html` root (durasi = jumlah TIMES adegan yang ada, `data-motion-blur`, musik, `<audio>` SFX dari AUDIO) |
| `scenes_t.py` | mandor | contoh minimal 1 adegan yang sudah terbukti lolos lint, jadi acuan format worker |
| `scenes_a.py`, `_b`, `_c` | satu worker per berkas | `SC = {'sN': (html, js, css)}`, `AUDIO = [(t_absolut, key, vol[, dur[, media_start]])]` |
| `scenes.py` | mandor | `SC = {**A, **B, **C}`; `AUDIO = AA + AB + AC`; assert urutan `s1..sN` |
| `WORKER_BRIEF.md` | mandor | kontrak lengkap, aturan keras, cara uji, format laporan |

Konvensi markup (diganti oleh generator):
- `%%` diganti `sN-` (id unik per adegan) dan `@@` diganti `sN`.
- Baris CSS berawalan `R ` diskop menjadi `#sN `.
- `<!--CUR-->` adalah posisi kursor. Elemen setelah `<!--OVER-->` berada di luar kamera (flash, mask layar penuh).
- JS berisi badan timeline `tl` dengan waktu LOKAL adegan. AUDIO memakai waktu ABSOLUT video.

CLI generator: `python3 gen_rN.py <modul_scenes> <out_dir>`. Bila `out_dir` ≠ proyek, symlink `assets`, `hyperframes.json`, dan `package.json` ke `out_dir`. Hasilnya pratinjau terisolasi di scratch: adegan pertama modul mulai di 0, dan lint/snapshot/check jalan di sana (snapshot ±8 dtk). Root proyek tidak tersentuh.

## Urutan kerja

1. Mandor menulis generator dan `scenes_t.py`, lalu membuktikan pipeline. Generate ke scratch, jalankan `lint` sampai 0 error, `snapshot --at ...`, lalu lihat PNG: font termuat? warna benar? Baru setelah itu tulis brief.
2. Tulis `WORKER_BRIEF.md` dan `scenes.py`, lalu kirim semua worker paralel dalam SATU panggilan delegasi. Context tiap worker cukup berisi:
   - perintah "baca brief dulu" dan nama berkas miliknya,
   - folder pratinjau scratch,
   - rentang baris storyboard untuk adegannya,
   - TIMES absolut,
   - bagaimana adegan terakhirnya harus menyambung ke adegan berikutnya.
3. Pembagian worker:
   - Adegan berkesinambungan (match-cut perangkat, morph objek) dipegang satu worker. Frame terakhir adegan N harus identik posisi dan ukurannya dengan frame pertama adegan N+1.
   - Rantai berkesinambungan lebih dari 2 adegan biasanya menghabiskan jatah iterasi satu worker. Mandor menulis spesifikasi frame serah-terima di brief (left/top/width/height/rotasi perangkat dan isi layar pada detik batas), lalu rantai dibagi ke dua worker yang sama-sama mematuhi angka itu.
   - Worker terakhir memegang adegan ajakan dan logo, termasuk frame akhir yang harus utuh terbaca.
4. Selama worker jalan, kerjakan hal independen (`build_tracker.json`), lalu akhiri giliran. Jangan polling transcript.
5. Saat hasil masuk:
   - Worker yang berstatus `max_iterations`/terpotong dianggap parsial walaupun laporannya "SELESAI". Verifikasi berkasnya sendiri sebelum dipakai: `py_compile`, kunci `SC` sesuai adegan yang ditugaskan, jumlah dan rentang waktu entri `AUDIO` berada di dalam TIMES-nya, lint 0 error, serta grep `Math.random`, `repeat:-1`, `Date`, dan warna anotasi storyboard. Lanjut hanya jika semua lolos; sisanya diambil alih mandor, bukan dikirim ulang utuh.
   - `py_compile`, lalu `python3 gen_rN.py` ke proyek.
   - `check --json` di root.
   - Snapshot titik tengah tiap adegan dan setiap batas antar-adegan.
   - Perbaiki temuan, render draft, cek ffprobe (durasi = root `data-duration`, ada stream audio), lalu publish `<proyek>-draft-rN.mp4`.
   - Render dijalankan sebagai proses latar dengan notifikasi selesai (`render -o out/<nama>.mp4 > out/render-rN.log 2>&1; echo EXIT=$?`). Perbarui `build_tracker.json` (berkas, hasil cek, output, langkah berikut) sebelum render, kirim pulse, lalu akhiri giliran. Jangan memakai tool call untuk mengecek render berulang (`kill -0`, `tail`, `ps`); jatah iterasi habis sebelum render selesai dan giliran berakhir tanpa verifikasi. Tunggu notifikasi selesai, lalu lanjutkan ffprobe dan publish di giliran berikutnya. Jangan menyebut tautan hasil sebelum ffprobe dan publish selesai.

## Ronde revisi (draf sudah ada, Bagas memberi keluhan)

- Kepemilikan berkas dipisah menurut jenis perbaikan, tidak menurut adegan saja. Worker memegang `scenes_a/b/c.py` untuk memperbaiki isi yang tertinggal atau salah (elemen storyboard yang hilang, teks terlalu kecil, layar kosong, kursor menutupi label). Mandor memegang lapisan efek global (zoom, glow, jadwal SFX) di modul terpisah (`build/rN_fx.py`) bersama generator dan `index.html`.
- Brief worker wajib melarang penambahan zoom, glow, atau SFX, dan melarang render penuh. Bila efek ditulis dua pihak, akan ada dua tween pada properti yang sama (scale/filter), dan audio terduplikasi.
- Worker menulis `build/rN_audit.md`: setiap item storyboard → status (ada/diperbaiki/hilang) beserta detik lokalnya. Mandor memakai berkas ini sebagai checklist sebelum render.
- Brief memuat daftar temuan dengan detik dan nama adegan dari diagnosis mandor, supaya worker tidak mengaudit ulang dari nol.

### Lapisan efek global (`rN_fx.py`)

- Salin `compositions/` revisi sebelumnya ke `build/r<N-1>-compositions-bak/` sebelum generator menulis ulang. Bila elemen hilang setelah efek global dipasang, `diff` berkas adegan lama vs baru untuk menemukan hunk penyebabnya, jangan menebak dari kode generator.
- Kamera dimiliki satu pihak. Bila mandor memegang zoom global, brief melarang worker menganimasikan wrapper kamera, dan `rN_fx.py` menulis satu track keyframe kamera per adegan (push/zoom/pull) pada satu wrapper. Jangan menambah wrapper `.drift`/`.rig` di atas tween kamera adegan: lapis transform yang di-compose saling melawan sehingga skala naik-turun dan pusat meloncat. Cek dengan `hyperframes keyframes compositions/sN.html --shot <png> --selector '#sN-cam'`; lebih dari satu baris `composed with` berarti cacat.
- Prefix `R ` hanya menskop awal baris. Tulis satu selector per rule (`R .drift{...}` lalu `R .rig{...}`), jangan menggabungkan selector berskop dengan koma. Selector kedua lolos tanpa skop, dan pembungkus kamera `position:absolute;inset:0` yang ikut berlaku di luar adegan akan menutupi elemen `<!--OVER-->` (kartu penutup, flash).
- Simpan daftar elemen penting per adegan yang wajib tetap di dalam frame saat zoom. Batasi scale dan `transform-origin` supaya bbox elemen itu setelah di-scale tetap di dalam kanvas dengan margin, lalu snapshot di detik puncak zoom tiap adegan.
- Glow berbasis `filter` dan motion blur dengan banyak penggerak menaikkan biaya per frame. Log render lalu memuat `Reduced auto worker count ... calibration-p95=<ms>` dan worker turun ke 1, sehingga render jauh lebih lama dari revisi sebelumnya. Hitung batas atas waktu = jumlah frame × p95 ÷ worker, lalu sampaikan rentang itu ke Bagas, bukan "belum bisa dipastikan". Bila terlalu lama, kurangi lapisan filter/blur sebelum render.

## Aturan penulisan adegan (masukkan ke brief; mencegah peringatan `check`)

- Frame 0 sudah berisi gambar. Jangan mulai dari layar hitam atau kosong, walau hanya setengah detik.
- Hold baca tetap hidup lewat gerak detail bermakna yang digerakkan `tl` (kursor, ketikan, angka, indikator) atau satu push kamera searah, karena layar beku ≥ 0,4 detik terasa seperti video macet. Jangan memakai drift kamera bolak-balik (yoyo atau `fromTo` sepanjang adegan) sebagai pengisi; itu terbaca goyang.
- Jurnal atau transaksi tiruan ditampilkan lengkap: setiap baris debit punya baris kredit pasangannya, dan totalnya seimbang. Baris yang hilang langsung terlihat oleh penonton yang paham akuntansi.

- Keadaan awal tersembunyi ditulis lewat CSS/atribut atau `gsap.set`, bukan `tl.set(..., 0)`. `tl.set` di posisi 0 tidak terender saat playhead tepat di 0, sehingga elemen bocor di frame 0.
- Teks bacaan minimal 28 px pada sisi pendek 1080. Teks yang hanya tekstur diberi `data-layout-ignore`. Isi UI tiruan (tabel, sidebar) tetap kena aturan ini bila dimaksudkan untuk dibaca.
- Elemen `z-index:-1` (mask/latar dalam) butuh induk ber-`isolation:isolate`. Tanpa itu, elemen tertutup latar root dan hilang dari gambar.
- Dua tween pada properti yang sama tidak boleh tumpang tindih waktunya (kursor x/y, scale token). Potong tween awal atau pakai `overwrite:"auto"`.
- Deterministik: tanpa `Math.random()` tanpa seed, `Date`, timer, `repeat:-1`, maupun CSS animation/transition. Semua yang tampak harus fungsi dari waktu `tl`.
- SFX ber-ekor (riser, revcym) dimulai di titik impact − durasi berkas, agar puncaknya jatuh tepat di aksi. Ekornya (`t + dur`) juga tidak boleh melewati akhir adegan atau titik potong berikutnya. Audit semua entri `AUDIO` terhadap TIMES, lalu potong lewat field `dur` bila ada yang melewati batas, karena suara yang masih berbunyi di adegan berikutnya terdengar seperti salah sambung.
- Angka yang harus sama (debit = kredit, total = jumlah baris) digerakkan oleh satu tween bersama: durasi, ease, dan waktu mulai identik. Penghitung terpisah dengan kecepatan berbeda membuat frame di tengah terlihat tidak seimbang.
- Kursor mendarat dengan ujungnya di tepi atau sudut target, sehingga badan kursor tidak menutupi label tombol saat ditekan.
- Layar perangkat atau UI tiruan diisi sampai tepi bawah. Area kosong yang lebar terbaca sebagai layar yang belum selesai.
- Info `text_box_overflow` / `container_overflow` dari mask baris teks (`.ln { overflow:hidden }`) saat teks masih di bawah mask hanyalah info, bukan kegagalan, asalkan snapshot setelah teks naik terlihat utuh.
- Anotasi storyboard (`.tag`, `.ann`, warna anotasi) tidak boleh masuk video.
