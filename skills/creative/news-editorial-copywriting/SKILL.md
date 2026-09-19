---
name: news-editorial-copywriting
title: News Editorial Framing & Copywriting
description: "Use when writing or transforming news into engaging content."
author: Bagas Cihuy
version: 1.0
tags: [copywriting, editorial, journalism, framing, sputar-ai, content-creation]
---

# News Editorial Framing & Copywriting

Panduan operasional untuk merombak teks berita kaku (press release, dokumen birokrasi, laporan angka) menjadi konten media yang sangat *engaging*, tajam, dan menarik perhatian. Ini adalah tulang punggung pengelolaan bahasa untuk media berita modern Sputar AI.

Ketika diminta untuk membuat, meringkas, atau menulis ulang konten berita, **wajib** terapkan teknik-teknik pengelolaan bahasa (*copywriting* dan *framing*) berikut ini:

## 1. Humanization (Dampak pada Manusia)
Berita membosankan karena terlalu fokus pada institusi, angka statistik, atau proses birokrasi.
- **Aturan:** Jangan mulai dari gedungnya atau rapatnya; **mulai dari manusianya**.
- **Praktik:** Bingkai berita birokrasi yang kering menjadi narasi tentang ancaman, perubahan, atau keuntungan langsung bagi keseharian audiens.
- **Contoh:** 
  - ❌ *DPR mengesahkan revisi UU Perpajakan No. 12 Tahun 2026 siang ini.*
  - ✅ *Mulai bulan depan, potongan pajak di slip gajimu bakal berubah. Ini 3 hal yang diam-diam disahkan siang tadi.*

## 2. Wall Street Journal (WSJ) Formula
Formula jurnalisme yang terbukti ampuh mengubah topik paling makro dan garing menjadi cerita yang mengikat empati.
- **Langkah 1 (Anekdot):** Buka dengan cerita satu individu atau kejadian mikroskopis yang sangat spesifik. (Contoh: *Keluhan Pak Budi yang wartegnya sepi karena harga telur naik gila-gilaan*).
- **Langkah 2 (Nut Graf):** Pada paragraf kedua/ketiga, lakukan *zoom-out* secara drastis. Jelaskan bagaimana cerita individu tersebut adalah bagian/dampak dari berita atau tren makro yang jauh lebih besar. (Contoh: *Apa yang dialami Pak Budi adalah efek domino dari Inflasi Pangan...*)

## 3. Spiky Point-of-View (Sudut Pandang Tajam)
Media tradisional mengambil judul yang *neutral* dan "aman" (sehingga membosankan). Konten modern harus punya *hook* yang melawan arus pikiran umum.
- **Aturan:** Temukan kontradiksi dari sebuah berita. Gunakan paradoks tersebut sebagai *Lead* (kalimat pembuka) atau Headline.
- **Contoh:**
  - ❌ *Pertumbuhan Ekonomi Q2 Melambat Jadi 4,9%.*
  - ✅ *Gaji Naik tapi Terasa Makin Miskin? Laporan Ekonomi Q2 Ini Menjelaskan Kenapa Dompetmu Bocor Halus.*

## 4. Show, Don't Tell (Analogi Visual)
Pengelolaan bahasa di berita tidak butuh hiperbola yang menipu, tapi butuh analogi visual yang gampang dicerna otak untuk metrik yang abstrak.
- **Aturan:** Terjemahkan angka raksasa atau metrik teknis ke dalam ukuran fisik atau barang sehari-hari.
- **Contoh:**
  - ❌ *Proyek ini memakan biaya overhead hingga Rp 10 Triliun.*
  - ✅ *Biaya proyek ini setara dengan membangun 10.000 puskesmas baru di pelosok desa.*

## 5. Workflow AI (NotebookLM / Gemini Notebook)
Saat mengembangkan portal berita atau membedah dokumen PDF tebal:
1. **Research & Extract:** Gunakan NotebookLM untuk mencerna dokumen mentah dan merangkum *insights*.
2. **Prompt Spesifik:** Perintahkan AI dengan instruksi: *"Ekstrak 3 poin paling berdampak langsung bagi rakyat dari dokumen ini. Lalu buatkan 3 alternatif judul menggunakan gaya Spiky POV dan analogi Show, Don't Tell."*

## 5A. Tipe Konten 1 — Education-Led Commerce
Untuk media edukasi yang menjual kelas atau produk pengetahuan, perlakukan berita/edukasi gratis sebagai **pemantik minat dan pintu masuk funnel**, bukan sebagai produk akhir semata.

1. **Tarik perhatian melalui realitas aktual:** Mulai dari berita, perubahan aturan, kesalahan umum, atau masalah yang sedang dirasakan audiens.
2. **Berikan kemenangan kecil yang nyata:** Konten gratis wajib tetap berguna dan tuntas pada satu masalah; dilarang menjadi clickbait kosong atau sengaja menyembunyikan jawaban inti.
3. **Bangun kesadaran akan celah:** Setelah memberi insight, tunjukkan secara jujur batas pengetahuan audiens—apa risiko jika salah mengambil keputusan dan kemampuan apa yang perlu mereka kuasai.
4. **Posisikan kelas sebagai kelanjutan:** Produk berbayar menjual struktur, kedalaman, latihan, alat, pendampingan, dan percepatan hasil; bukan menjual ulang informasi gratis yang sengaja dipotong.
5. **CTA harus menyatu dengan materi:** Hubungkan kompetensi yang baru dibahas dengan hasil kelas. Hindari CTA generik yang terasa ditempel di akhir.

Formula naskah: `HOOK aktual → EDUKASI praktis → GAP/konsekuensi → BRIDGE ke metode → CTA kelas`.

Contoh CTA: *“Kalau kamu ingin bisa membedah keputusan finansial seperti ini sendiri—bukan sekadar mengikuti opini—kelas ini mengajarkan kerangkanya langkah demi langkah.”*

Gunakan metrik `save/share → profile visit → DM/klik → lead → pembelian` untuk menilai apakah konten benar-benar memindahkan audiens dari perhatian menuju kepercayaan dan transaksi.

Label internal: **TIPE 1 — EDUCATION-LED COMMERCE**. Konsep strategi ini berasal dari observasi dan arahan Bagas Cihuy.

## 6. Standar Produksi & Keamanan Konten Otomatis (Zero-Slop & Anti-Crash)
Saat menyusun *pipeline* pembuatan konten berita otomatis (seperti skrip CMS, *Instant Dispatcher*, atau generator narasi AI), patuhi protokol berikut:
- **Terjemahan & Lokalisasi Total**: WAJIB 100% Bahasa Indonesia jurnalistik yang lugas. DILARANG KERAS menyalin mentah-mentah (*copy-paste*) abstrak berbahasa Inggris, metadata ArXiv (seperti `arXiv:2609... Announce Type:`), atau istilah teknis/LaTeX asing yang merusak bacaan. Wajib dicerna menjadi narasi cerita.
- **Zero Fluff (Tanpa Basa-Basi)**: Hindari pembukaan dramatis AI (seperti *"Kabar mengejutkan datang dari..."* atau *"Di tengah persaingan sengit..."*). Langsung hantam ke inti peristiwa teknis/angka konkret.
- **Format Caption & Baris Baru (Clean Newlines)**: WAJIB menggunakan karakter line break / newline murni (karakter enter nyata). DILARANG KERAS membiarkan karakter escape literal `\n`, `\\n`, atau `/n` muncul di takarir (caption) maupun teks visual, karena akan tercetak mentah dan merusak estetika publikasi.
- **Batasan Panjang Karakter (Graceful Slicing)**: Jika *prompt* AI meleset dan menghasilkan narasi yang melebihi batas karakter *field* atau layout grafis, **DILARANG melemparkan *Error Exception* (throw Error) yang membuat seluruh skrip/cronjob hancur dan terhenti (crash)**. Alih-alih, potong *string* tersebut secara mulus pada batas maksimal (misal menggunakan `.slice(0, 2000)`).
- **Pencegahan Kebocoran Escape Karakter (`\n\n`)**: Saat merakit payload JSON atau naskah multiline, hindari *double-escaping* string yang menyebabkan teks literal `\n\n` tercetak di kanvas grafis. Pastikan template dan generator selalu menormalkan baris baru (`replace(/\\n/g, '\n')`) agar paragraf terpisah bersih secara visual.
- **Pencegahan Double-Encoding Entitas HTML**: Hindari *double-escaping* karakter khusus seperti ampersand (`&`) pada takarir (*visual caption*) atau metadata agar tidak muncul teks cacat seperti `&AMP;` di kanvas render.
- **Struktur Standar 4 Slide Carousel**: Tepat 4 slide: Slide 1 (Hook/Headline), Slide 2 (Konteks Peristiwa - 2 paragraf padat tanpa poin bullet), Slide 3 (Dampak & Signifikansi - 2 paragraf padat tanpa poin bullet), Slide 4 (Penutup Substantif & CTA Arsip). Dilarang menyisipkan kata "RADAR" pada seluruh naskah publik.
- **Eksekusi Tuntas & Langsung Posting (Zero-Friction Publishing)**: Saat alur pembuatan warta disetujui atau dipicu, selesaikan siklus hingga penerbitan riil ke Instagram secara langsung tanpa berhenti untuk menanyakan konfirmasi opsi ulang yang memperlambat alur ("Apakah mau diterbitkan sekarang?"). Selesaikan render, setujui, unggah via API, dan laporkan bukti tautan publikasi aktif (*live link*).

## 7. Formula Redaksi "Langsung Ke Poinnya" (Zero Fluff & High Impact)
Untuk warta olahraga, hasil laga kilat, atau *breaking alerts* (Benchmark: Fabrizio Romano & 433):
- **Baris Pertama Langsung Meledak:** Tembak angka rekor, skor telak, atau fakta paling mengguncang (*"33 GOL DALAM 7 LAGA! ABSOLUTE CINEMA"*). DILARANG KERAS menggunakan kalimat pembuka klise (*"Pada laga sengit tadi malam..."*, *"Sebuah pertandingan yang..."*, *"Di balik kemenangan..."*).
- **Struktur Poin Fakta 1 Baris:** Sajikan inti peristiwa dalam format 1 baris per tokoh/aksi (Nama bintang + aksi spesifik + angka statistik konkret).
- **Pertanyaan Debat Interaktif:** Akhiri naskah/caption dengan pertanyaan tajam pemicu komentar (*"Siapa Man of the Match menurut lu malam ini?"*).
- **Atribusi Sumber Resmi:** Wajib mencantumkan penerbit asli berita secara transparan.

## 8. Protokol Kesesuaian Tokoh Berita & Foto Visual (Anti-Salah Orang)
- **Kesesuaian Mutlak Subjek:** Jika warta membahas tokoh atau atlet spesifik (seperti Jay Idzes, Calvin Verdonk, Raphinha, Lamine Yamal, atau pelatih), foto visual yang dipasang WAJIB menampilkan tokoh tersebut. Dilarang keras memajang foto atlet lain.
- **Verifikasi Token Nama pada Foto Feed:** Jangan langsung mempercayai `image_url` atau `og:image` bawaan artikel. Gunakan hanya jika URL berkas memuat token nama tokoh. Jika tidak, kerahkan pencarian web kontekstual nama tokoh.
- **Pencarian Web Khusus Tokoh:** Cari dengan query terarah: `"${entity}" celebration match action high resolution iconic -alamy -getty -shutterstock -watermark`.
- **Doktrin Fallback Netral:** Jika foto tokoh tidak ditemukan, dilarang mengambil foto tokoh lain dari arsip lokal. Fallback HANYA boleh ke foto atmosfer stadion, lapangan, atau suasana netral.
- **Audit QC Sub-Agent:** Sistem inspeksi QC wajib memindai URL berkas gambar terhadap nama-nama tokoh lain dan mengeluarkan status VETO (REJECTED) jika terjadi ketidaksesuaian (*cross-entity mismatch*).

## 9. Penataan Vertikal Teks Visual Cover & Safe Zones Media Sosial (Kanvas 1080×1350)
- **Zona Aman Tepi Bawah (Social Media Safe Zone):** Dilarang keras menempelkan teks judul atau nama akun di dasar kanvas ($Y > 1150\text{px}$). Lapisan antarmuka Instagram Reels/Carousels dan TikTok (nama akun, sound pill, caption preview, bottom bar) akan menutupi $180\text{px} - 240\text{px}$ area bawah.
- **Ketinggian Blok Teks Ideal:** Letakkan blok nama akun/kicker dan headline pada rentang vertikal $Y \approx 750\text{px} - 1140\text{px}$ (sejajar paha pemain/bola), dengan menyisakan ruang aman minimal $200\text{px} - 230\text{px}$ dari tepi bawah kanvas (`padding-bottom: 210px`).
- **Batas Gradasi Hitam (Scrim Area M):** Gradasi gelap untuk kontras teks harus dimulai halus tepat di atas teks ($Y \approx 720\text{px} - 760\text{px}$ atau $54\% - 56\%$). Dilarang menaikkan gradasi hingga ke dada atau wajah ($Y < 680\text{px}$) agar nomor jersey, ekspresi atlet, dan logo tim tetap cerah, jernih, dan 100% natural.

## 10. Standardisasi Caption Khusus TikTok vs Instagram (Cross-Platform Copywriting)
- **TikTok Caption Super Ringkas (Maksimal 100–140 Karakter):** Format wajib 2–3 baris:
  1. *Baris 1:* Headline hook tajam langsung ke inti peristiwa.
  2. *Baris 2:* 1 baris pancingan komentar singkat (*"Gimana tanggapan lu?"* atau *"Bakal kejadian gak nih?"*).
  3. *Baris 3:* 3–4 hashtag spesifik (`#sputarball #beritabola #(klub/timnas) #fyp`).
  *Pantangan TikTok:* Dilarang menyalin mentah-mentah caption panjang Instagram ke TikTok karena memblokir kanvas foto di Photos Mode dan diabaikan penonton cepat.
- **Instagram Caption Mendalam:** Tetap memuat 2–3 kalimat cerita padat, kutipan, pertanyaan diskusi, atribusi sumber resmi, dan instruksi retensi (simpan/bagikan).

## 11. Visual Hook Ikonik (Daya Pikat Tokoh Terkenal di Slide 1 Cover)
- **Atensi 2 Detik Pertama:** Saat pengguna scrolling cepat di media sosial (TikTok Photos Mode / Instagram Explore), visual cover Slide 1 adalah penentu hidup-mati konten.
- **Utamakan Tokoh Mega-Bintang:** Gunakan selalu wajah atau sosok pemain sepak bola dunia dan bintang Timnas yang langsung dikenali seantero orang awam (Cristiano Ronaldo, Lionel Messi, Kylian Mbappe, Erling Haaland, Jude Bellingham, Lamine Yamal, Jay Idzes, Maarten Paes, Vinicius Jr, Cole Palmer, Bukayo Saka, dll.).
- **Pantangan Tokoh Antah-Berantah:** DILARANG KERAS menyorot pemain cadangan, pemain akademi antah-berantah, atau nama asing yang wajahnya tidak diketahui publik umum, karena penonton awam akan langsung melewati postingan tersebut.
- **Ekspresi & Momen Bertenaga:** Pilih foto aksi pertandingan lapangan (*Match Action*) dinamis atau selebrasi ikonik (rentang tangan Bellingham, SIUU Ronaldo, telunjuk Messi, selebrasi dingin Palmer).

## 12. Doktrin Topik Ramah Orang Awam (Langsung "Ngeh" Tanpa Jargon)
- **Eliminasi Total Jargon Taktis Berat:** Dilarang keras menggunakan istilah rumit seperti *expected goals (xG)*, *inverted fullback*, *build-up low-block phase*, atau skema formasi yang membuat orang awam malas membaca.
- **Sudut Pandang Populer & Menggugah Emosi:** Bangun cerita yang bahkan orang yang jarang menonton sepak bola pun langsung paham dan penasaran:
  1. *Drama Skor Gila:* Pesta gol telak (bantai 7-0), kena comeback sadis 3-2 di menit akhir, adu penalti mendebarkan.
  2. *Emosi & Kontroversi Lapangan:* Blunder fatal kiper, kartu merah konyol, amarah/tangisan pemain bintang.
  3. *Fakta & Rekor Spektakuler:* Gaji triliunan rupiah, rekor gol dunia terpecahkan, aksi bocah ajaib.
  4. *Rivalitas Akbar:* El Clasico, Derby sekota yang panas, dan kebanggaan perjuangan King Indo di kancah internasional.
- **Formula Headline Cover "Langsung Ngeh":**
  `[KATA SERU / EMOSI] + [NAMA BINTANG / TIM BESAR] + [PERISTIWA GILA / DRAMA]!`
  (Maksimal 10–12 kata, lugas, menghentak, tanpa kalimat pembuka klise).
  *Contoh:*
  - *"GILA! Haaland Hattrick Kilat 10 Menit, Man City Bantai Lawan!"*
  - *"BANG JAY MENGGILA! Garuda Tahan Gempuran Raksasa Asia, Ranking FIFA Melesat!"*
  - *"COMEBACK SADIS! Sempat Tertinggal, Real Madrid Lolos Berkat Gol Menit Akhir!"*

## 13. Matriks Evaluasi Multi-Dimensi & Rekomendasi Waktu Unggah (Continuous Learning)
Jadikan data analitik performa sebagai bahan belajar otomatis yang membedah efektivitas ke dalam 4 pilar:
1. **Pilar Visual:** Pantau rasio interaksi per jenis visual (Match Action vs Selebrasi vs Potret Statis).
2. **Pilar Topik:** Kelompokkan topik berkinerja tinggi (Timnas, La Liga, Premier League) dan prioritaskan dalam seleksi kurasi.
3. **Pilar Gaya Penulisan:** Bandingkan performa hook judul (Dramatic Scoreline vs Emotional Exclamation) dan pertahankan format caption ringkas.
4. **Pilar Waktu & 4 Jendela Jam Emas WIB (Golden Windows):**
   - *Pagi (06:45 – 08:30 WIB) // 1.30x Potensi:* Breakfast news & recap laga Eropa dini hari.
   - *Siang (11:45 – 13:30 WIB) // 1.40x Potensi:* Rehat makan siang, scrolling santai butuh warta singkat to-the-point.
   - *Sore (16:30 – 17:45 WIB) // 1.45x Potensi:* Pulang kantor/sekolah & preview duel malam.
   - *Malam Emas (19:15 – 21:45 WIB) // 1.75x Potensi:* Prime time interaksi komentar, debat suporter paling membara.
   - *Aturan 15-30 Menit:* Unggah materi 15–30 menit sebelum jam puncak agar algoritma platform telah mengindeks konten tepat saat lonjakan trafik audiens dimulai.

