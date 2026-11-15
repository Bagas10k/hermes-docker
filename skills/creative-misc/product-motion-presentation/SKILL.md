---
name: product-motion-presentation
description: Use when making Bagas's product promo or showcase videos.
---
# Product Motion Presentation — Bagas

- Jawab pertanyaan penonton **“yang dibangun itu apa?”** dengan bentuk produk yang dikenali sebelum angka atau fitur. Benda yang disebut (ruang kerja, berkas, draf) harus tampak rupa, isi, serta perubahan nyata; jangan mengganti animasi produk dengan screenshot/rekaman layar atau kartu abstrak berlabel.
- Untuk gaya modular: ruang kosong → komponen bermakna muncul bertahap → hubungan sebab-akibat terbentuk → komponen berkumpul menjadi satu sistem. Morph sekitar 1–1,5 detik sebagai titik awal; hold baca sekitar 3 detik diisi detail relevan, bukan gerak dekoratif. Kursor mengenai target sebelum keadaan berubah.
- Kunci audiens, satu keputusan yang ingin dipengaruhi, dan satu studi kasus yang relevan sebelum memilih aset. Untuk pimpinan perusahaan, tunjukkan satu alur kerja konkret beserta titik persetujuan manusia dan cara menguji manfaatnya; jangan menyamakan simulasi dengan bukti ROI.
- Bila pengguna memberi Reel sebagai patokan **hasil**, ambil sampel lintas durasi dan periksa beberapa frame berurutan; dekompilasi hubungan objek, perubahan angka/status, ritme, dan hierarki. Bedakan video tutorial tentang cara membuat video dari video hasil yang ingin ditiru. Tulis kontrak adaptasi: satu objek/data konsisten yang berubah bertahap, bagian yang tidak boleh disalin, serta adegan yang membuktikan mekanisme. Jangan memakai rekaman, audio, logo, atau frame referensi sebagai bahan keluaran bila diminta animasi orisinal tanpa impor video.
- Ekstrak DNA visual nyata dari referensi secara langsung (sampling warna via skrip atau inspeksi piksel): ukur gradient latar (top/mid/bottom), warna teks paling kontras, warna aksen per scene, dan rasio gelap-terang panel tengah. Hindari mengarang palet atau memakai default krem/putih jika referensi menggunakan gradient lavender-ke-mint atau dark panel khusus. Terapkan kontras per scene: scene penjelasan teknis memakai kartu terang bergradien, scene kesimpulan/keputusan memakai dark panel pekat untuk menegaskan bobot akhir.
- Hindari tombol aksi tetap aktif bersamaan dengan status yang sudah selesai: saat status berubah menjadi 'DISETUJUI', gantikan tombol klik dengan konfirmasi status tercatat agar tidak membingungkan penonton. Pastikan animasi kursor menekan tombol (scale/press feedback) selesai SEBELUM status berubah.
- Voice-over singkat mengikuti aksi visual pada rentang yang sama. Buka dengan contoh/kontras konkret, ikuti pertanyaan audiens, perlihatkan mekanisme dan bukti, tutup dengan akibat serta batas. Contoh konten akun lain adalah referensi struktur, bukan template yang disalin atau bukti klaim.
- Saat melanjutkan video, periksa storyboard, komposisi, dan animatic yang sudah ada sebelum membuat baru. Pakai ulang hanya jika studi kasus, pesan, dan adegan cocok dengan brief terbaru; animatic lama yang hanya mirip tema boleh ditawarkan sebagai referensi berlabel, bukan sebagai draf video baru. Jika naskah dan animatic berbeda, selaraskan keduanya dan ukur durasi VO sebelum mengklaim progres produksi. Jangan hanya memperlambat video lama lalu menumpang VO baru: teks, objek yang disetujui, cabang keputusan, dan waktu aksi harus sama dengan ucapan; bila tidak, ubah komposisi atau naskah lebih dulu dan kirim sebagai referensi lama, bukan animatic baru.
- Bandingkan **hasil render dan frame berurutan** dengan referensi pengguna. Render/test hijau tidak membuktikan kualitas visual. Bila membuat satu aset motion untuk web dan video, pertahankan satu sumber animasi (misalnya Lottie JSON) dan uji konsumsi nyata di keduanya: browser memuat SVG serta interaksi replay/reduced-motion, komposisi video merender aset yang sama, ffprobe durasi/dimensi/audio, lalu inspeksi frame tengah dan akhir. Status menunggu persetujuan jangan berubah menjadi disetujui tanpa tindakan manusia yang terlihat; label dan objek yang disetujui harus konsisten. Laporkan batas verifikasi per permukaan: build dan tes repo tidak membuktikan integrasi video penuh atau kualitas editorial. Ilustrasi wajib diberi label dan tidak diklaim sebagai eksekusi produk nyata.
- Format 4:5 dan objek/logo resmi dipilih ketika diminta; jangan menganggap semua tugas video otomatis 4:5 (contoh lain yang pernah dipakai: 4:3 lanskap 1440×1080, 30 fps). Draf privat sampai ditinjau.

## Preferensi tetap Bagas untuk video promo

- Sebelum render apa pun (termasuk draf), kirim storyboard sebagai **gambar** lebih dulu: satu lembar PNG berisi panel per adegan (layar, gerak, SFX, sumber) + timeline, terbit di folder statis publik sebagai `<proyek>-storyboard-r<N>.png`, lalu tunggu persetujuan. Bagas ingin menilai alur sebelum biaya render keluar.
- Draf dulu, render penuh menunggu persetujuan. Draf terbit di folder statis publik dengan nama `<proyek>-draft-r<N>.mp4` (naikkan N tiap revisi) supaya revisi lama tidak tertimpa. Laporkan tautannya beserta batas verifikasi.
- Musik hanya dipakai jika lisensi komersialnya jelas (misal CC BY). Tulis atribusinya di caption dengan format `Musik: <judul> – <artis> (<lisensi>)`. Tanpa lisensi jelas, jangan pakai musik itu.
- Aksen brand yang terang/neon (misal lime) hanya untuk isi pil, label, atau tombol, dengan tinta gelap di atasnya. Jangan dipakai sebagai warna teks di latar terang, karena kontrasnya jatuh jauh di bawah 7:1.
- Video lama yang akan diganti dibiarkan utuh di foldernya. Buat proyek baru (`<proyek>-v2`), jangan menimpa.
- Jangan menulis nama atau tautan berkas `.png`/`.mp4` di chat sebelum berkas itu benar-benar ada di folder publik. Chat Bagas merender tautan menjadi kartu pratinjau, dan kartu itu error bila berkasnya belum ada.
- Setelah storyboard ACC dan Bagas bilang "lanjut"/"gas", jangan minta konfirmasi lagi. Kerjakan sampai draf terbit, dan pakai sub-agent bila diminta.
- Jika pesan Bagas terpotong, tanyakan bagian yang hilang di laporan yang sama dan masukkan sebelum render berikutnya. Jangan menebak isinya.

## Standar gerak & suara minimum (berlaku untuk setiap draf)

Bagas menolak draf yang "bagus tapi datar". Kelima hal ini wajib ada sejak draf pertama, bukan baru ditambahkan setelah ia mengeluh:

- **Video tidak pernah diam, tapi tidak goyang.** Gambar yang beku ≥ 0,4 detik dihitung cacat, dan frame 0 sudah berisi gambar tanpa pembuka hitam. Isi "tidak diam" dengan rantai aksi bermakna yang saling tumpang tindih (aksi berikut mulai 0,1–0,2 dtk sebelum aksi sebelumnya selesai), detail kecil yang hidup (kursor, ketikan, angka, indikator), atau satu push kamera searah saat hold baca. Jangan menumpuk drift/rig/zoom kamera yang bolak-balik: transform gabungannya membuat skala naik-turun dan pusat bingkai meloncat, sehingga terbaca sebagai goyangan buatan mesin dan menjatuhkan nilai kerapian.
- **Zoom masuk-keluar yang tegas** di momen kunci: klik, angka penting, ganti perangkat atau adegan. Push halus 3–10% saja belum dihitung sebagai zoom. Zoom tidak boleh memotong elemen penting (tombol, label, stiker, perangkat) di tepi frame; snapshot setiap adegan di detik puncak zoom-nya, karena zoom yang ditambahkan belakangan sering mendorong elemen tepi yang tadinya aman keluar layar.
- **Glow aksen** (misalnya lime) pada tombol aktif, angka kunci, kartu aktif, dan logo, dengan denyut halus yang digerakkan timeline. Glow hanya menegaskan elemen, tidak menggantikan kontras teks ≥ 7:1.
- **SFX bervariasi.** Pakai satu suara untuk tiap jenis aksi (klik, kartu muncul, angka mengunci, zoom, kilau/glow, transisi, logo), dan jangan biarkan satu suara mendominasi. Patokannya: suara yang sama dipakai paling banyak sekitar 8 kali per 60 detik. Setiap zoom diberi suara zoom dan logo diberi dentuman. Preferensi ini menggantikan batas "~2 swish per film" di skill `real-sound`. Aturan "satu suara klik untuk satu film" tetap berlaku untuk aksi klik. SFX baru dipotong bagian sunyi di awalnya (supaya bunyinya jatuh tepat di aksi) dan disamakan kerasnya sebelum dipakai.
- **Rapi = semua item storyboard ACC muncul.** Sebelum render, cocokkan storyboard dengan isi tiap adegan satu per satu, termasuk baris tabel, label, dan posisi kursor.

## Kerapian & kehalusan gerak (wajib, dinilai Bagas)

Draf yang lolos checklist isi tetap dinilai rendah bila geraknya patah atau tata letaknya berantakan. Tabel ease, aturan kamera, checklist tata letak, dan perintah QC ada di `references/keyframe-craft.md`; sintaks GSAP keyframes/CustomEase ada di skill `gsap`.

- Gerak multi-tahap pada satu elemen ditulis sebagai satu tween `keyframes` (persen + `easeEach`), bukan rangkaian `tl.to` terpisah, karena sambungan antar-tween memutus kecepatan sehingga gerak tampak patah.
- Ease dipilih menurut peran (masuk, keluar, pop, kamera, kursor, angka, denyut glow), bukan satu ease untuk semua. Keluar 40–50% lebih singkat dari masuk; pop maksimal `back.out(1.7)`; ease di sambungan dicerminkan (`power3.in` keluar → `power3.out` masuk).
- Satu track kamera per adegan pada satu wrapper, dan setiap gerak kamera punya sebab (klik, angka, reveal, ganti adegan).
- Satu fokus per momen: maksimal dua elemen besar bergerak bersamaan. Setiap elemen yang masuk punya animasi keluar atau bertahan sampai cut; tidak ada elemen yang muncul/hilang dalam 1 frame.
- Tata letak: margin aman dan posisi judul tetap antar-adegan, ukuran perangkat konsisten antar-adegan berurutan kecuali zoom disengaja, komposisi mengisi sebagian besar frame, label sejajar, stiker tersebar di luar fokus tanpa menutupi bezel/label dan tetap di dalam safe area saat zoom puncak.
- Sebelum menulis JS adegan, tulis lembar keyframe (satu baris per elemen bergerak: detik lokal, keadaan, ease, sebab). Generator menulis detik dan durasi sebagai angka literal, karena analyzer HyperFrames tidak bisa membaca posisi berupa variabel atau loop dan tween itu lolos dari QC.
- Sebelum render, jalankan `hyperframes keyframes --json` per adegan lalu `scripts/kf_qc.py <json> --png lanes.png --strict`. Laporkan vonis dan grafik lajurnya bersama pengukuran momen diam. Baseline r7 (3/10): 11 dari 11 adegan gagal.
- Sebelum membangun efek atau adegan dari nol, cek peta kemampuan: `references/hyperframes-capability-map.md` (blok registry, perintah CLI per tahap) dan `gsap/references/video-capability-map.md` (plugin GSAP yang aman untuk render beserta resepnya).

## Revisi dari keluhan draf

0. Bila Bagas memberi nilai rendah dan meminta skill di-upgrade dulu, patch skill (aturan + perintah QC) sebelum menyentuh video. Untuk ronde revisi apa pun, tulis artefak pertama (patch skill, brief worker, atau `rN_fx.py`) paling lambat sekitar 8 tool call setelah permintaan; riset berikutnya menyempurnakan berkas yang sudah tertulis. Giliran yang habis di diagnosis berakhir dengan nol perubahan.
1. Ukur render lama sebelum mengedit, dan ubah setiap keluhan menjadi angka. Untuk keluhan "kurang halus/rapi", tambahkan distribusi ease, overlap properti, dan jumlah lapis kamera dari `hyperframes keyframes --json` (lihat `references/keyframe-craft.md`). Momen diam per adegan dideteksi dengan perbedaan antar-frame (skrip `build/qc_motion.py` di proyek, atau alternatifnya filter ffmpeg `freezedetect` dengan d=0.4). Hitung pemakaian tiap suara dari daftar `AUDIO`, catat zoom dan glow apa saja yang sudah ada per adegan, lalu buat checklist storyboard → adegan. Laporkan angka-angka ini ke Bagas sebagai diagnosis, karena angka lebih jujur daripada "sudah diperbaiki".
2. Tetapkan syarat lulus yang jelas ya/tidak-nya: 0 momen diam, suara terbanyak ≤ sekitar 8 kali, setiap adegan punya ≥ 1 zoom tegas, ada glow di CTA/angka/logo, dan checklist storyboard 100%.
3. Pisahkan pekerjaan isi adegan dari efek global. Penjelasannya ada di `references/scene-generator-delegation.md` bagian "Ronde revisi".
4. Jalankan lagi pengukuran yang sama pada render baru sebelum publish, dan tulis hasilnya di laporan.

## Membangun film baru dari storyboard ACC (banyak adegan)

Pola: generator Python milik mandor + satu berkas adegan per worker + pratinjau terisolasi di scratch. Detailnya ada di `references/scene-generator-delegation.md` (struktur berkas, kontrak `SC`/`AUDIO`, urutan kerja, aturan penulisan adegan untuk brief).

- Kirim worker paling lambat sekitar 5 langkah setelah "lanjut". Jangan membaca ulang storyboard penuh, dokumentasi skill, atau inventaris aset di konteks mandor. Tulis brief yang menunjuk rentang baris storyboard dan path dokumentasi, lalu biarkan worker yang membacanya. Discovery di konteks mandor menghabiskan jatah iterasi, sehingga giliran berakhir tanpa satu worker pun terkirim.
- Buktikan pipeline generator dengan satu adegan contoh (lint 0 error + satu snapshot dilihat) sebelum dispatch. Brief yang menunjuk contoh berformat salah akan menggandakan kesalahan ke semua worker.

## Revisi gaya (restyle) film yang sudah ada

Urutannya:

1. Backup render dan komposisi gaya lama ke `out/bak-<gaya>-r<N>-<jam>/` sebelum menyentuh scene.
2. Bedah referensi lewat frame berurutan, lalu tulis `LOOK.md` di root proyek. Isinya gramatika saja: panggung/latar, perangkat/kartu, cara teks masuk, transisi, peran warna (hex), skala tipe. Konten referensi tidak diambil.
3. Restyle **scene 1 dulu** sebagai teladan. Snapshot di beberapa detik lokal, perbaiki, lalu snapshot ulang. Ganti juga warna latar root di `index.html`, karena celah antar-scene memperlihatkan latar root.
4. Kunci jadwal sfx di `index.html` (tidak diubah). Setiap aksi visual di scene baru harus mendarat di detik lokal sfx yang sudah ada. Dump dulu timing sfx per scene sebagai kontrak.
5. Sisa scene didelegasikan maksimal 2 scene per worker, dengan berkas terpisah. Context worker wajib menyebut: baca `LOOK.md` dan scene 1 sebagai teladan, hanya boleh edit berkas miliknya, dilarang render atau publish, dan sertakan daftar detik sfx scene tersebut.
6. Mandor menjalankan `hyperframes check` dan snapshot per scene atas hasil gabungan, baru render draf.

Pitfall verifikasi visual:
- `check`/`snapshot` di root proyek mengaudit `index.html` yang sedang terpasang. Sebelum generator menulis ulang `compositions/` dan `index.html`, yang teraudit masih revisi lama. Laporkan hasil itu sebagai "revisi lama", jangan sebagai bukti revisi baru.
- Perkecil contact sheet sebelum dikirim ke vision (`ffmpeg -i sheet.png -vf scale=1440:-1 sheet_s.jpg`); PNG berukuran MB sering time out, sedangkan JPG ±100 KB lolos. Pakai crop region beresolusi penuh hanya untuk detail kecil.
- Cek elemen kecil yang ditumpuk (pil miring di atas teks, stiker di tepi kartu) dengan crop region beresolusi penuh. Contact sheet menyembunyikan tumpang tindih tipis yang memotong huruf tinggi (f terbaca t).
- Bila vision menandai elemen miring, setengah tampak, atau salah posisi, petakan detik absolut ke detik lokal adegan dan cek di JS apakah ada tween yang sedang aktif pada elemen itu. Frame di tengah animasi masuk bukan bug. Snapshot ulang setelah tween selesai untuk membedakan elemen yang macet dari elemen yang sedang bergerak, sebelum memperbaiki atau melaporkannya.
- Baca vonis vision secara harfiah. "Masih bisa ditebak tapi terpotong" berarti GAGAL. Perbaiki dan snapshot ulang sebelum melaporkan "bersih" ke Bagas. Melaporkan bersih sebelum vonis lolos adalah overclaim.
