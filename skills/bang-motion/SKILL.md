---
name: bang-motion
description: Membangun motion graphic sinematik di browser (promo video, opener, intro, bumper, kinetic typography, explainer/video penjelasan bergambar 16:9 atau 9:16) memakai HTML + CSS + GSAP (+ Three.js bila perlu), dengan hasil yang bergerak seperti video sungguhan — bukan slide presentasi. Gunakan skill ini setiap kali user meminta "video promo", "opener", "intro animasi", "motion graphic", "bumper", "kinetic typography", "animasi teks sinematik", "explainer", "video penjelasan" (jurnalisme visual, kartun edukasi, kolase), atau menunjukkan referensi video promosi/explainer dan ingin dibuatkan versi web-nya — bahkan bila mereka tidak menyebut kata "motion graphic" secara eksplisit. Juga gunakan bila user mengeluh hasil animasi web "seperti PPT/presentasi" dan ingin lebih sinematik, atau ingin merender animasi web menjadi file video MP4, atau ingin explainer kartun/animasi dibangun LANGSUNG di After Effects lewat bridge/MCP Higgsfield.
license: MIT
metadata:
  author: Bang Tutorial
  author_url: https://youtube.com/bangtutorial
  version: "1.20.0"
  updated: "2026-11-01"
  homepage: https://github.com/bangtutorial/bang-motion
---

# Bang Motion — motion graphic web yang bukan PPT

**v1.20.0 · by [Bang Tutorial](https://youtube.com/bangtutorial) · MIT.** Riwayat perubahan di `CHANGELOG.md`;
cara pasang di `README.md`.

Skill ini untuk AI coding agent apa pun (format Agent Skills terbuka).
Isinya hukum dan resep untuk motion graphic yang bergerak seperti video, bukan
presentasi — patuhi sebelum menulis kode.

## Bila user menilai hasil jelek: perbaiki, jangan menawar konsep

Untuk artefak video/motion yang brief-nya sudah disetujui, nilai buruk atau
permintaan koreksi adalah arahan memperbaiki dalam cakupan itu, bukan undangan
membela hasil atau meminta persetujuan yang sama lagi. Koreksi mismatch yang
terlihat, lalu serahkan artefak baru dengan bukti frame; jangan mengklaim selera
baru sudah berhasil sebelum dinilai pengguna. Tanyakan hanya informasi brief
yang benar-benar belum tersedia. Jangan menerapkan aturan video ini untuk
membongkar aplikasi kerja: refinement, restoration, dan redesign UI mengikuti
cakupan yang diotorisasi dalam `ui-ux-execution-standard`.

## Membandingkan kemampuan dengan alat lain

Baca dokumentasi resmi atau source alat pembanding sebelum menetapkan mesin,
format ekspor, biaya, dukungan lokal/cloud, atau batas fiturnya. Caption sosial
dan halaman showcase hanya membuktikan klaim yang benar-benar tercantum, bukan
arsitektur keseluruhan. Pisahkan skill/panduan pembuatan kode dari aplikasi
studio dan layanan inference; jangan menyebut skill ini engine milik sendiri,
bebas biaya model, atau otomatis berjalan 60 FPS. Jangan menyimpulkan Remotion
membatasi morphing atau bahwa HTML lebih unggul kualitasnya dari nama stack.
Bandingkan per kebutuhan dengan bukti yang setara; keunggulan kualitas atau
performa memerlukan brief, aset, ukuran output, dan hasil uji yang sebanding.
Jika belum diuji, nyatakan belum ada dasar menentukan pemenang.

## Prasyarat — hanya browser

Deliverable (`index.html`) hanya butuh browser modern + internet untuk CDN
(GSAP, font). Python dan Node **opsional**, dipakai hanya untuk alat kerja:
`scripts/serve.py` (server no-cache, cuma perlu bila memakai module lokal),
puppeteer (snapshot/verifikasi otomatis, `scripts/render-frames.cjs` → MP4).
Kalau user tidak punya keduanya: (1) tetap bangun satu-berkas, buka lewat
klik dua kali; (2) verifikasi visual lewat `?debug=1` (panel scrub) dan
screenshot manual per detik kunci; (3) MP4 lewat rekam layar (OBS / rekam
tab browser) — jelaskan bahwa hasil rekam layar bisa drop frame, dan render
frame-by-frame butuh Node. Jangan pernah membuat deliverable yang butuh
`npm install` untuk DITONTON.

**ffmpeg juga opsional.** Cek dulu (`ffmpeg -version`); bila tidak ada:

| Kebutuhan | Dengan ffmpeg | Tanpa ffmpeg |
|---|---|---|
| Sinkron VO (batas kalimat/paragraf) | `silencedetect` | `scripts/vo-pauses.html` — buka di browser, pilih audio, salin `SEG`/`PARA`; hasilnya sama persis (Web Audio, tanpa instal) |
| Durasi/format audio | `ffprobe` | angka `DUR` dari vo-pauses.html; browser memutar wav/mp3/m4a/ogg langsung |
| Export MP4 | gabung PNG dari `scripts/render-frames.cjs` | tidak ada MP4 — tawarkan instal satu perintah (`winget install Gyan.FFmpeg` / `brew install ffmpeg`) atau rekam layar |
| Mempelajari video referensi (ekstrak frame) | `fps=` + `tile=` | minta user mengirim screenshot di detik kunci, atau buka videonya di browser dan potret pada detik tertentu |

Tanpa ffmpeg alur explainer tetap lengkap sampai sinkron VO; hanya MP4 yang
butuh instalasi.

## Player — tidak ada, autoplay, loop

Default deliverable: **tanpa panel/player apa pun di layar**, langsung
memutar saat dibuka, dan mengulang dari awal saat selesai (`onComplete →
play(0)`; bila ada suara, audio ikut diulang). Kontrol tersembunyi: R ulang,
Space jeda. Panel scrub/jam hanya muncul dengan `?debug=1` (alat review),
dan `?clean=1` menahan autoplay untuk export. Ada suara? Coba `play()`
langsung; bila diblokir browser, tahan di frame 0 dan mulai pada klik
pertama — tanpa teks "ketuk untuk mulai". Ini sudah tertanam di kedua
starter.

## Larangan struktural — uji PPT yang bisa diperiksa mekanis

Model lain (dan kamu, bila lelah) akan jatuh ke pola ini walau sudah membaca
hukum di bawah. Sebelum menyerahkan, cek KODE, bukan perasaan:

1. `grep -c "class=\"scene\"\|<section" index.html` — bila ≥ 3 adegan
   berupa `<section>` yang dinyalakan-dimatikan dengan `autoAlpha`/opacity,
   **atau blok setinggi frame yang digeser vertikal (`y: -1920` per adegan)**:
   itu slide deck. Menggulir section bukan bahasa kamera. Adegan harus
   berganti karena DUNIA/KAMERA bergerak (kamera bergerak, whip ke sudut
   lain, push-through, latar berganti), bukan karena section di-fade atau
   di-translate. Pengecualian yang sah: **kartun panggung**
   (`references/kartun-panggung.md`) memakai cut/geser 96 px antar panggung
   — boleh, karena tiap panggung hidup penuh (≥10 benda beraksi), bukan
   gambar diam yang di-fade.
2. Ada benang merah visual yang bertahan: satu subjek (aksi kontinu) ATAU
   satu dunia kolase/kertas/putih yang disusuri kamera (kartun, foto,
   katalog, sketsa). Foto full-bleed berganti-ganti tanpa dunia bersama →
   PPT. Satu gambar + satu kalimat per adegan, berganti tiap adegan →
   tetap slideshow walau kameranya bergerak: tiap adegan 3–5 elemen yang
   masuk bertahap per frasa (explainer.md "Satu adegan = 3–5 elemen").
3. Per adegan hitung node teks: eyebrow/kicker + judul + body/kredit = 3
   tingkat → PPT. Maksimum dua: satu angka/kalimat besar + satu label dunia.
   Dokumen/stempel/blok tanggal berisi ≤ 3 baris pendek dihitung objek,
   bukan tingkat teks.
4. **Kartu berparagraf.** Adegan berisi kartu/kotak dengan kalimat penjelas
   2–3 baris ("Dulu: spaghetti code N×M — tiap aplikasi bikin connector
   sendiri…") adalah dokumen yang diberi animasi masuk. Kalau sebuah adegan
   butuh paragraf untuk dimengerti, informasi itu pindah ke gerak objek atau
   dipecah jadi dua adegan, satu pernyataan each.
5. **Komposisi 9:16 tidak boleh top-heavy.** Mengumpulkan seluruh kartu atau elemen di 60% bagian atas dan membiarkan 40% bagian bawah kosong melompong (dead space) membuat video terlihat menggantung. Komposisi wajib di-center secara vertikal, atau diseimbangkan dengan jangkar visual di area bawah (seperti live terminal daemon stream, telemetri bar, atau metrik tabular) agar kanvas terasa padat, berbobot, dan deliberate.
6. **Anti-objek dekoratif tanpa makna.** Untuk topik teknologi, gunakan objek dan hubungan yang menjelaskan mekanismenya; kotak bermata atau partikel acak bukan representasi arsitektur. Pilih gaya dari brief dan referensi, bukan otomatis obsidian/HUD untuk semua teknologi. Primitive SVG tetap sah untuk diagram matematis yang jelas; mutu ditentukan makna, proporsi, hirarki dan keterbacaan, bukan kerumitan bentuk.
7. Ken Burns (scale 1.0→1.05 pada foto) sebagai satu-satunya gerak → PPT.
   Gerak tiap detik harus datang dari BAHASA GERAK LATAR dari menu
   `techniques.md` §7c. Batang/garis melintas ke samping ("lane", "range",
   hujan partikel horizontal) bukan default; hanya bila tema memang
   kecepatan/aliran, dan tidak dua proyek berturut-turut.
6. Transisi hanya fade + scale bump + light leak di semua cut → template PPT.
7. Explainer dimulai dari starter GAYANYA: `starter-explainer-kartun`,
   `-jurnalisme`, `-katalog`, `-sketsa` (mode kolase), `starter-explainer`
   (aksi kontinu), atau `starter-explainer-panggung` (kartun panggung).
   BUKAN dari `assets/starter-opener.html` (opener teks), dan bukan dari nol.
8. **Miniatur adalah slide.** Kamera zoom < 1,08 sehingga subjek sebesar ibu
   jari dan ruang kosong mengisi separuh layar → PPT walau semua bergerak.
   Dunia dipecah jadi panggung seukuran frame, bukan satu peta besar yang
   dijelajahi (`kartun-panggung.md` Hukum 1).
9. **Kerangka template (opener/promo).** Adegan pertama teks diperbesar lalu
   keluar ke kiri; tiga tile/kartu fitur sejajar; kotak input diketik; urutan
   hook → fitur → fitur → janji → logo → CTA. Dua atau lebih tanpa tuntutan
   konsep → template. Pilih ulang kerangka dari `references/opener-konsep.md`.

Gagal satu poin saja → rombak sebelum ditunjukkan ke user.

## Jenis pekerjaan yang dicakup

Skill ini untuk motion graphic web secara UMUM. Explainer hanya salah satu
jenis — ia punya dokumen sendiri karena strukturnya beda.

| Jenis | Durasi lazim | Ciri | Resep |
|---|---|---|---|
| Opener / promo produk | 25–40 dtk | satu konsep dari menu, satu momen istimewa, penutup brand | `references/opener-konsep.md` + `references/techniques.md` |
| Bumper / ident / logo sting | 3–8 dtk | logo build-on, satu gerak tanda tangan | `techniques.md` |
| Intro / outro kanal | 5–12 dtk | nama kanal + tanda tangan gerak sama tiap episode | alur kerja di bawah |
| Kinetic typography / lirik | 15–60 dtk | teks adalah subjek; split per kata/huruf | `techniques.md` |
| Title / lower third | 2–6 dtk | elemen kecil di atas footage, masuk-keluar bersih | `techniques.md` |
| Explainer / video penjelasan | 30–90 dtk | fakta bersumber, entitas tampil, sudut pandang berganti | `references/explainer.md` + starter per gaya |

## Video informasi dan engine berbasis kode

- Prioritaskan pemahaman: tulis tujuan komunikasi, fakta/sumber, narasi, representasi visual, dan bukti yang harus terlihat untuk setiap beat sebelum mengode. Animasi UI bukan pengganti mesin video penjelasan.
- Visualisasikan besaran yang dibahas, bukan sekadar aliran dekoratif: pembentukan antrean harus memperlihatkan pekerjaan menunggu dan perubahan jumlahnya; bedakan arus masuk, kapasitas maksimum, keluaran aktual, dan stok awal.
- Cocokkan angka, satuan, label, dan kondisi waktu pada narasi dengan diagram di beat yang sama; grafik kapasitas enam tidak boleh mengiringi kalimat kapasitas empat tanpa perubahan keadaan yang jelas.
- Pisahkan resep bank, adapter renderer yang tersedia, dan hasil yang sudah diuji. Katalog puluhan preset bukan bukti semuanya dieksekusi; tolak adapter yang belum ada, jangan mengganti diam-diam.
- Gunakan telemetri DOM untuk bounds dan clipping teks; kotak aman tidak membuktikan isi kotak muat. Tetap periksa frame untuk makna dan komposisi, serta review audio untuk pelafalan. Lulus tes geometri bukan bukti penonton memahami.
- Perlakukan angka safe zone, batas kata, waktu baca, dan durasi preset sebagai kebijakan desain bertanda sumber/status, bukan hukum universal platform. Metadata lisensi bukan bukti hak pakai aset.
- Pertahankan perbedaan bukti: audio valid, render aktif, MP4 terprobe, MCP dapat dipanggil, mutu audio ditinjau, dan pemahaman manusia diuji adalah gerbang terpisah. Jangan mengganti gerbang yang belum diuji dengan skor estetika.

Untuk pengembangan pipeline/MCP video, ikuti urutan integrasi dan gerbang di `references/architecture.md` bagian **Engine video informasi**; untuk narasi terukur dan mixing kompatibel, lihat `references/vo-sync.md`.

## Hukum #1 — Ini video, bukan slide

- **Untuk opener: satu kalimat pendek + maksimal satu objek utama per adegan.**
- Batas copy opener tidak berlaku otomatis pada subtitle, penjelasan edukasi, atau atribusi sumber; ringkas headline tanpa menghapus syarat yang membuat klaim benar.
  Tidak ada kicker ("01 — FITUR"), sub-judul, paragraf keterangan, chip/badge.
- **Informasi baru = respons visual baru.** Pada explainer, ubah keadaan/aksi
  di dunia yang sama bila masih berhubungan; pergantian kalimat tidak wajib
  mengganti shot.
- **Daftar poin diganti visual, bukan otomatis tiga tile.** Pilih cara dari
  menu fitur `references/opener-konsep.md`; dua opener berturut-turut tidak
  memakai cara yang sama.
- **Adegan harus hidup.** Kamera boleh menetap saat objek membawa aksi.
- **"Zoom in-out" = ukuran shot, bukan napas kamera.**

Baca `references/anti-ppt.md` SEBELUM mendesain adegan.

## Hukum #2 — Deterministik atau mati

Tidak ada satu baris pun yang membaca jam sistem. Semua visual adalah fungsi
murni dari `tl.time()`: spektrum, angka berjalan, partikel, getar kamera
(sinus frekuensi tinggi, bukan `Math.random()`), posisi objek yang "mengalir"
(tween JARAK, bukan akumulasi kecepatan per frame). Konsekuensinya: scrub
akurat seperti timeline After Effects, dan render frame-by-frame menghasilkan
gambar identik setiap kali — **dengan syarat** state yang berubah lewat
callback juga deterministik (lihat "Jebakan": `suppressEvents`).

## Hukum #3 — Gaya lahir dari tema, bukan dari starter

1. **Style brief dulu, kode belakangan.** Tulis dan tunjukkan: tema + tiga
   kata sifat; konsep & sidik jari struktur; palet (hex + sumber, dari
   brand); font display berkarakter (bukan Poppins/Inter/Roboto); penekanan
   teks; bahasa latar per segmen; tanda tangan gerak; gerak latar (§7c);
   permukaan latar (§7d, ≥2 lapis); gaya render objek (§7e); transisi; satu
   momen istimewa.
2. **Starter adalah arsitektur, bukan gaya.** Abu-abu, font sistem, latar
   WebGL di starter adalah PLACEHOLDER.
3. **Referensi = ritme, bukan kulit.** Ambil durasi shot, transisi, hierarki
   atensi, energi. JANGAN ambil palet, font, tekstur, tata letak, kalimat,
   urutan adegan, momen unik.
4. **Berbeda dari proyek sebelumnya — kulit DAN kerangka.** Minimal tiga dari
   empat: palet, font, bahasa latar, tanda tangan gerak.
5. **Latar tidak default gelap**, dan tidak pernah statis.
6. **Bebas berekspresi** — hukum mengunci STRUKTUR, KONTRAS, KEBARUAN, bukan
   ekspresi.

### Arah gaya (pilih satu; boleh memadukan dua dengan sadar)

| Arah | Latar | Tipografi | Gerak khas | Cocok untuk |
|---|---|---|---|---|
| Sinematik gelap | gradasi nyaris hitam, partikel/nebula, bloom hanya di objek | grotesk tebal bersih | push-through, cahaya di depan lensa | alat kreatif, gaming, teknologi |
| Poster color-block | bidang warna solid besar berganti tiap adegan | display sangat tebal, huruf raksasa terpotong tepi | wipe blok, teks menabrak tepi | app konsumen, musik, event |
| Editorial terang | putih/krem, ruang kosong luas, garis tipis | serif display + grotesk kecil | geser halus, garis menggambar | produktivitas, finansial, SaaS |
| Kertas & cetak | tekstur kertas, potongan kolase, stempel | tulisan tangan + serif | benda terbang lalu mendarat | edukasi, komunitas, kuliner |
| Retro / analog | warna pudar, grain, garis scan, bingkai VHS | geometris 70–90-an | glitch terkendali, zoom kasar | nostalgia, musik |
| Brutalis mono | hitam-putih, grid keras | monospace + kondensasi | cut keras, blok bergeser, kursor | developer tools, teknis |
| Pastel ceria | pastel bertumpuk, bentuk bulat besar | rounded sans tebal | mantul elastis, bentuk mekar | anak, kesehatan, lifestyle |
| Mewah gelap | hitam + emas/perunggu, bayangan lembut | serif tinggi berspasi lebar | gerak lambat, sinar menyapu | fashion, otomotif, properti |
| Flat pop berfoto | netral terang + medan warna brand solid | sans geometris membulat tebal | foto pop, stiker meletup | fintech, e-commerce |
| Grainy gradient | dasar gelap/pekat; bentuk bergradien bercahaya | grotesk kecil atau display tebal | lapisan bentuk membuka, kamera menembus | tech, AI, musik, fintech |

## Hukum #4 — Teks hidup, latar tunduk

- Sentence case bobot 500–600. Kapital-tebal hanya untuk satu adegan.
- Judul/klaim/frase pendek DEFAULT TANPA TITIK.
- Sorotan kata OPSIONAL, diputuskan di style brief, satu bentuk per video.
- Dua adegan berturut-turut tidak sama dalam ukuran, arah masuk, posisi teks.
- Di KANTONG TEKS latar harus GELAP (≤25% luminance) atau TERANG (≥80%),
  tidak pernah "ramai sedang". Di luar kantong, latar justru kaya.
- **Headline menjelaskan gambar, bukan mengulang narasi.** Bila ada VO,
  headline memakai kata kunci yang SAMA dengan kalimat yang sedang diucapkan
  (mis. narasi "pintar, tapi buta" → headline "Pintar, tapi Buta."). Kalau
  headline dan narasi menyebut hal berbeda, penonton membaca dua cerita.

## Kualitas audio & sound design — standar wajib

Video yang secara visual benar tetap akan dinilai murahan (3/10) bila audionya kering, robotik, atau hening tanpa sound design.

1. **Haram TTS robotik/monoton.** Jangan gunakan Google Translate TTS untuk video penjelasan atau promo produk — suaranya datar layaknya mesin penjawab telepon. Gunakan **Neural TTS berkualitas tinggi** (misalnya `edge-tts` dengan suara neural alami seperti `id-ID-ArdiNeural` atau `id-ID-GadisNeural`) dengan intonasi dan kecepatan bicara yang manusiawi.
2. **Sound design multi-track adalah keharusan.** Video tidak boleh hening hanya berisi vokal. Selalu gabungkan minimal:
   - **Latar musik / ambient drone:** Drone synthesizer low-pass halus untuk menjaga tensi dan atmosfer (misal synth drone 55Hz/110Hz).
   - **SFX impact & foley:** Whoosh pada transisi antarbabak, sub-bass thud pada saat penguncian/drop elemen penting, klik UI pada saat kartu muncul, dan chime pada resolusi akhir.
3. **Urutan sinkronisasi VO yang benar:**
   - Tentukan jendela beat (start/end) sebelum membuat audio.
   - Tulis narasi per beat sesuai jendela; paskan dengan `atempo` (0,92×–1,25×).
   - Verifikasi onset dengan `silencedetect` (toleransi ±0,25 dtk).
   - Kunci timeline visual ke onset hasil ukur nyata.

## Sinkronisasi audio VO — urutan yang benar

Audio diproduksi DULU sebagai beat, visual menempel pada onset terukur.
Menulis narasi sebagai prosa lalu memotongnya agar muat ke durasi visual
selalu menghasilkan suara yang membicarakan hal yang tidak ada di layar.

1. **Tentukan jendela beat** (start/end per kalimat) SEBELUM membuat audio.
2. **Tulis narasi per beat**, dibatasi panjangnya oleh jendela itu — bukan
   sebaliknya. Kalau hasil TTS ternyata kepanjangan, **pendekkan kalimatnya**;
   jangan mendorong `atempo` melewati ~1,30 (terdengar tergesa) atau turun di
   bawah ~0,92 (terdengar cadel).
3. **Generate TTS per segmen**, ukur tiap segmen, paskan dengan `atempo`, lalu
   susun ke satu track pada offset absolut (`adelay`) + `amix`.
4. **Verifikasi onset dengan `silencedetect`**, jangan percaya perasaan:
   bandingkan `silence_end` dengan start beat (toleransi ±0,25 dtk).
5. **Kunci timeline visual ke onset terukur**, bukan ke jendela yang
   direncanakan: geser tween teks/aksi ke angka hasil ukur.
6. **Ikat audio ke jam timeline** (`gsap.ticker`, koreksi drift >0,08 dtk) dan
   ulangi bersama loop.

Resep lengkap + alat: `references/vo-sync.md`,
`scripts/build-vo-sync.py`, `scripts/render-frames.cjs`.

## Alur kerja

0. **Kenali jenisnya.** Explainer → buka `references/explainer.md` dan ikuti
   "Langkah nol": SATU pertanyaan berisi gaya, rasio, durasi, suara, plus
   pagar durasi. Jenis lain → tanya hanya yang tidak bisa diturunkan dari
   brief, dalam satu pertanyaan.
0b. **Style brief** ditulis dan disetujui sebelum kode.
1. **Serap referensi & sumber brand.** Warna, logo (path asli), font, klaim
   dari sumber resmi PRODUK.
2. **Rundown** tabel `detik | adegan | kalimat | visual`. Persetujuan dulu —
   merombak rundown murah, merombak kode mahal. (Kecuali user sudah menyuruh
   "koreksi sendiri": langsung eksekusi.)
3. **Scaffold** dari starter yang benar, ganti token warna/font/latar segera.
4. **Bangun adegan satu per satu** dengan resep `references/techniques.md`.
5. **Verifikasi VISUAL, bukan "kode jalan".** Potret 6–20 detik kunci,
   susun lembar kontak, nilai seperti sutradara. Perbaiki, potret lagi.
   JANGAN merender semua frame untuk mengecek.
6. **Serahkan SATU `index.html`** yang bisa diklik dua kali. **Export MP4
   hanya bila diminta** (`scripts/render-frames.cjs`).
7. **Khusus explainer:** naskah VO lengkap + ajakan merekam
   (`references/explainer.md` → "Penyerahan").

## Checklist sebelum menyerahkan

- [ ] Style brief ditulis & disetujui SEBELUM kode
- [ ] Tidak ada sisa placeholder starter; tidak ada kulit referensi yang disalin
- [ ] Berbeda dari proyek sebelumnya: minimal tiga dari palet/font/latar/tanda tangan
- [ ] Lolos 9 poin "Larangan struktural" — termasuk **tidak ada section yang
      digeser vertikal** dan **tidak ada kartu berparagraf**
- [ ] Teks hidup (Hukum #4); headline memakai kata kunci yang sama dengan VO
- [ ] Latar ≥2 lapis, bergerak di tiap adegan, tidak flat satu warna
- [ ] Motion blur berarah pada teks masuk/keluar; nol `Date.now()`/`Math.random()`
- [ ] Tanpa player di layar; autoplay; loop; `?debug=1` untuk scrub
- [ ] **VO: onset terukur cocok dengan beat visual (±0,25 dtk)** dan naskah
      tidak menyebut hal yang tidak muncul di layar
- [ ] **Label/teks yang berubah antar-beat terlihat di frame hasil export**
      (bukan hanya saat diputar)
- [ ] Geometri sambungan (colok/masuk/berhenti) diukur, bukan dikira-kira
- [ ] Sudah dipotret di detik kunci dan dilihat dengan mata — bukan render penuh
- [ ] Ada suara? Halaman menahan di frame awal bila autoplay diblokir
- [ ] Angka yang berubah tiap frame pakai `tabular-nums` + `min-width`

## Jebakan yang sudah memakan korban

Detail di `references/techniques.md` bagian "Jebakan", plus:

- **`tl.pause(t)` / `tl.seek(t)` MENSUPPRESS callback secara default**
  (`suppressEvents=true`). Semua `tl.call()`, dan efek samping yang dipasang
  di callback, TIDAK jalan saat snapshot maupun export frame-by-frame — hasil
  export jadi beda dari playback langsung. Pakai `tl.pause(t, false)` atau
  `tl.seek(t, false)` di skrip potret/render. Lebih aman lagi: jangan ubah
  state lewat callback untuk hal yang harus terlihat di frame.
- **Jangan mengubah `textContent` untuk label antar-beat.** `gsap.set(el,
  {textContent})` tidak andal dan callback bisa tersuppress. Pakai dua elemen
  label bertumpuk, lalu cross-fade `opacity` — deterministik saat scrub,
  seek, dan export.
- **Geometri sambungan diukur, bukan dikira-kira.** Untuk aksi "masuk ke
  slot", "mendarat di tepi", "berhenti di dalam", ukur `getBoundingClientRect`
  dari kedua elemen pada waktu tween selesai dan bandingkan. Elemen penerima
  harus `z-index` DI ATAS objek yang masuk supaya pin benar-benar terlihat
  hilang ke dalam, dan slot ditaruh di tepi yang menghadap objek.
- Bloom threshold rendah → layar putih; nebula additive menumpuk lewat bloom;
  selector CSS lebih spesifik mengalahkan `opacity:0` awal; module JS di-cache
  browser (pakai server `no-store`); objek 3D pipih diputar penuh jadi garis;
  kotak filter SVG default memotong ekor blur.

## After Effects — langsung lewat bridge Higgsfield

Bila AE terbuka, bridge `ae_*` tersambung, dan user meminta dibangun di AE,
baca `references/ae-bridge-higgsfield.md`. Bridge tidak bisa menyimpan/merender
dan tidak bisa menyusun ulang urutan layer — sebutkan itu dan buat layer dari
belakang ke depan.

## Isi paket

| Berkas | Kapan dibaca |
|---|---|
| `references/vo-sync.md` | SAAT ADA VO: jendela beat, TTS per segmen, `atempo` berbatas, `adelay`+`amix`, verifikasi `silencedetect`, mengunci visual ke onset |
| `scripts/build-vo-sync.py` | membangun satu track VO yang dipaksa pas ke jendela beat + mencetak onset hasil ukur |
| `scripts/render-frames.cjs` | export MP4: puppeteer + chromium, resume dari frame terakhir, seek `suppressEvents:false`, perintah ffmpeg akhir |
| `references/kartun-panggung.md` | KARTUN PANGGUNG: satu panggung per adegan, kamera ≥1,08, rig sendi |
| `assets/starter-explainer-panggung.html` | starter kartun panggung |
| `scripts/kepala-ekspresi.py` | kepala hasil generate → varian ekspresi + kedip |
| `references/ae-bridge-higgsfield.md` | bridge AE lewat MCP Higgsfield |
| `scripts/ae/bridge/aset-svg.py`, `svg2png.cjs`, `rig-tokoh.py` | aset ilustrasi → PNG 2×; generator rig karakter |
| `references/anti-ppt.md` | sebelum mendesain adegan |
| `references/opener-konsep.md` | OPENER/PROMO sebelum rundown |
| `references/explainer.md` | explainer/video penjelasan |
| `references/architecture.md` | saat scaffold |
| `references/techniques.md` | saat membangun adegan & efek |
| `references/roadmap.md` | mengembangkan skill ini |
| `assets/starter-opener.html` | titik awal OPENER/promo |
| `assets/starter-explainer*.html` | explainer per gaya |
| `scripts/serve.py` | dev server no-cache |
| `scripts/vo-pauses.html` | deteksi jeda VO di browser (pengganti ffmpeg) |
