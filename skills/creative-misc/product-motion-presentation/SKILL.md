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

## Revisi gaya (restyle) film yang sudah ada

Urutannya:

1. Backup render dan komposisi gaya lama ke `out/bak-<gaya>-r<N>-<jam>/` sebelum menyentuh scene.
2. Bedah referensi lewat frame berurutan, lalu tulis `LOOK.md` di root proyek. Isinya gramatika saja: panggung/latar, perangkat/kartu, cara teks masuk, transisi, peran warna (hex), skala tipe. Konten referensi tidak diambil.
3. Restyle **scene 1 dulu** sebagai teladan. Snapshot di beberapa detik lokal, perbaiki, lalu snapshot ulang. Ganti juga warna latar root di `index.html`, karena celah antar-scene memperlihatkan latar root.
4. Kunci jadwal sfx di `index.html` (tidak diubah). Setiap aksi visual di scene baru harus mendarat di detik lokal sfx yang sudah ada. Dump dulu timing sfx per scene sebagai kontrak.
5. Sisa scene didelegasikan maksimal 2 scene per worker, dengan berkas terpisah. Context worker wajib menyebut: baca `LOOK.md` dan scene 1 sebagai teladan, hanya boleh edit berkas miliknya, dilarang render atau publish, dan sertakan daftar detik sfx scene tersebut.
6. Mandor menjalankan `hyperframes check` dan snapshot per scene atas hasil gabungan, baru render draf.

Pitfall verifikasi visual:
- Cek elemen kecil yang ditumpuk (pil miring di atas teks, stiker di tepi kartu) dengan crop region beresolusi penuh. Contact sheet menyembunyikan tumpang tindih tipis yang memotong huruf tinggi (f terbaca t).
- Baca vonis vision secara harfiah. "Masih bisa ditebak tapi terpotong" berarti GAGAL. Perbaiki dan snapshot ulang sebelum melaporkan "bersih" ke Bagas. Melaporkan bersih sebelum vonis lolos adalah overclaim.
