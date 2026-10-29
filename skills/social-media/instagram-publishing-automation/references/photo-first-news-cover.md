# Photo-First News Cover — Spesifikasi Hasil Bedah Referensi

Sumber pembelajaran: post `instagram.com/p/DfEbKUIHyFj` (@ohmeygatt) plus 4 post berita lain di grid akun yang sama (DfExUdon63u, DfEv6h0H6PR, DfEcm5cn0Hn, DfETCElx40k).

## 1. Temuan inti dari referensi

1. **Foto full-bleed 4:5 (1080×1350)** sampai keempat tepi. Nol border, nol rounded corner, nol kartu melayang.
2. **Nol branding di dalam gambar.** Empat dari lima cover tidak punya logo, handle, atau watermark. Tidak ada badge, tidak ada kicker dekoratif.
3. **Teks hanya bila perlu.** Kalau ada, teks putih di area yang digelapkan: kicker kecil ber-tracking lebar + garis merah tipis, lalu satu headline.
4. **Merah dipakai sebagai penanda, bukan warna brand.** Motif paling konsisten: coretan/lingkaran merah untuk menunjuk subjek.
5. **Fotonya dokumenter dan spesifik.** Orang yang benar-benar terlibat, lokasi nyata, produk nyata. Bukan stok abstrak, bukan ilustrasi vektor.
6. **Crop ketat pada subjek.** Subjek mengisi sekitar 40–60% frame; konteks lingkungan tetap terbaca.

Kesimpulan: kekuatan gaya ini **bukan pada ornamen grafis**, tapi pada ketepatan memilih foto. Ornamen justru ditekan seminimal mungkin.

## 2. Aturan pemilihan aset ("sesuai dan pas")

Urutan prioritas:
1. Foto asli subjek berita: orang, lembaga, produk, atau perangkat yang disebut di berita.
2. Foto dokumenter lokasi/perangkat nyata yang relevan (jalan, pabrik, lab, data center, kendaraan).
3. Foto arsip berlisensi (Wikimedia Commons CC BY / CC BY-SA / public domain), atribusi ditulis di caption.

Dilarang:
- Render 3D kartun, ilustrasi vektor, ikon, atau clipart.
- Stok abstrak "AI" (jaringan saraf menyala, glow biru-ungu, bola partikel).
- Foto ber-watermark komersial (shutterstock, gettyimages, plus.unsplash, premium_photo).
- Gambar yang subjeknya tidak berhubungan dengan isi berita, hanya karena "terlihat teknologi".

Lima syarat wajib sebelum aset dipakai:
1. Subjek cocok dengan isi berita.
2. Lebar sumber minimal 1080 px.
3. Setelah crop 4:5, sensor/wajah/bagian utama subjek tidak terpotong.
4. Ada area cukup gelap atau kosong di 30% atas atau bawah untuk teks.
5. Lisensi jelas dan atribusi siap ditulis di caption.

## 3. Struktur dua slide

- **Slide 1 (hook):** foto + kicker + satu headline maksimal dua baris, total ≤6 kata. Tanpa paragraf, tanpa angka pendukung kedua.
- **Slide 2 (CTA):** foto yang sama di-blur dan digelapkan, satu blok teks ajakan membaca caption, satu kalimat penunjuk arah.
- **Caption:** seluruh isi berita, angka, konteks teknologi, dan tautan sumber.

## 4. Tipografi

- Headline: condensed bold, 118–150 px, line-height ~0.95, maksimal dua baris.
- Kicker: mono 19–22 px, uppercase, tracking +5–6 px.
- Handle: mono 19 px, putih, kecil, di sudut bawah.

## 5. Warna dan perlakuan foto

- Teks: putih `#FFFFFF` pada latar gelap; tinta `#141414` jika ditaruh di langit terang/area putih.
- Aksen: merah `#C8201E`, maksimal 5% area, hanya garis atau penanda.
- Scrim: gradien hitam di 30% atas/bawah, alpha 0.40–0.64 sesuai kerumitan latar; cukup untuk keterbacaan tanpa mematikan foto.
- Grade: kontras +5–6%, saturasi disesuaikan. Jangan diproses jadi duotone atau hitam-putih.

## 6. Larangan tata letak

- Jangan menaruh teks di atas sensor, kepala, wajah, atau bagian utama subjek. Beri jarak aman minimal 40–50 px.
- Jangan mengulang angka di slide dan caption dengan nilai berbeda; slide memakai angka yang dibulatkan, caption memuat angka presisi beserta sumbernya.
- Jangan menambah badge, nomor halaman besar, ornamen sudut, atau efek glow.

## 7. Adaptasi teks terhadap objek (aturan wajib)

Teks tidak boleh ditempel di posisi tetap. Posisi, ukuran, warna, dan kekuatan scrim mengikuti isi foto:

1. **Pilih band paling kosong.** Hitung energi tepi (edge energy) pada band atas 0–34% dan band bawah 60–100%. Band dengan energi terendah menjadi tempat teks.
2. **Pilih warna tinta dari luminansi band itu.** Rata-rata luminansi > 148 → tinta gelap `#141414` + scrim putih tipis. Di bawah itu → tinta putih `#FFFFFF` + scrim hitam.
3. **Kekuatan scrim mengikuti kerumitan.** Band makin ramai → scrim makin kuat (0.40–0.64). Area sudah rata → scrim minimal.
4. **Kicker memakai warna tinta yang sama**, bukan merah. Merah hanya untuk garis aksen 5px.
5. **Footer punya pembacaan sendiri.** Luminansi patch kiri-bawah menentukan warna handle dan nomor halaman; bila ambigu (96–205) tambahkan scrim bawah 0.34.
6. **Jarak aman ke subjek.** Blok judul maksimal dua baris, ukuran awal 122–136 px, menyusut otomatis sampai muat lebar aman. Bila masih menyentuh sensor/kepala, geser ke band satunya.

Implementasi acuan: `scripts/photo_cover.py` (PIL, tanpa dependensi tambahan).

## 8. Membedah referensi sebelum mendesain (tanpa login)

1. **Buka post referensi, ambil cover aslinya.** `meta[property="og:image"]` memberi berkas 640×640 hasil crop tengah — cukup untuk membaca gaya, tapi memotong tepi 4:5. Untuk frame penuh, cari `<img>` dengan `naturalWidth` ≥ 1000 di DOM (bisa 1080×1350).
2. **Jangan simpulkan dari satu post.** Buka 4–6 post lain di grid profil, ambil `og:image` masing-masing, susun contact sheet, lalu bandingkan: apakah teks muncul konsisten, atau justru kebanyakan tanpa teks? Pola berulang itulah sistemnya.
3. **Periksa apakah itu desain atau foto.** Unduh dan lihat pikselnya sebelum menulis CSS/kanvas. Banyak akun berita memakai foto jurnalistik polos; menambahkan tipografi di atasnya berarti membuat gaya baru, bukan meniru.
4. **Aset legal:** Wikimedia Commons (`generator=search&gsrnamespace=6&prop=imageinfo`) menyediakan CC BY / CC BY-SA. Unduh dengan header User-Agent yang jelas, dan tulis atribusi di caption. Jangan pakai foto ber-watermark komersial.
5. **Verifikasi hasil secara visual, bukan hanya exit code.** Render, periksa posisi piksel bounding box teks terhadap subjek, lalu pastikan: teks tidak menutup subjek (gap > 40px), kontras cukup, tidak ada elemen terpotong.
