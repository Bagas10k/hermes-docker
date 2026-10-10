---
name: storytelling-narasi-video
description: Use when scripting spoken videos and voice-over.
---
# Storytelling Narasi Video

Untuk video edukasi bagi orang awam. Panduan produksi, bukan janji retensi. Dasar: riset komunikasi naratif [1], bahasa lugas CDC [2], praktik vokal Toastmasters [3][4], dan pengujian audiens YouTube [5].

## Cerita sebelum kalimat
1. Tentukan audiens, satu pertanyaan, dan satu hasil belajar yang dapat diceritakan ulang.
2. Kumpulkan fakta, sumber, batas, dan contoh nyata. Bedakan anekdot/ilustrasi dari bukti umum; narasi persuasif membawa tanggung jawab etis [1].
3. Rangkai **situasi spesifik → gangguan/pertanyaan → tindakan konkret → perubahan terlihat → jawaban dan batas**. Bayar rasa penasaran di akhir.
4. Untuk setiap beat, gambarkan input, tindakan, dan akibatnya. Hindari ikon yang hanya mengulang kata narator.

## Bahasa untuk telinga
- Buka dengan situasi, akibat, atau kontras yang benar; tanpa salam panjang, hiperbola, dan janji palsu.
- Subjek + kata kerja aktif; satu gagasan per kalimat; kata sehari-hari. Letakkan pesan utama lebih dulu dan gunakan bahasa audiens [2].
- Transisi kausal alami: “Karena…”, “Maka…”, “Tapi…”, “Hasilnya…”. Kurangi jargon, filler, dan terjemahan kaku. Istilah asing masuk sesudah contohnya.
- Penutup menjawab hook dan memberi satu takeaway yang bisa dicek. CTA hanya bila relevan.
- Baca keras: revisi frasa tersandung dan kalimat yang menghabiskan napas.

## Pengucapan & pengarahan suara
- Pisahkan teks yang benar-benar diucap dari anotasi: `teks | maksud emosi | kata fokus | jeda | visual`.
- Nada percakapan. Variasikan laju, volume, dan pitch karena makna, bukan drama otomatis; artikulasi jelas [3].
- Jeda pendek sebelum kata penting atau setelah pertanyaan/temuan memberi ruang berpikir [4]. Jangan pangkas jeda dengan mempercepat seluruh audio demi target durasi.
- Nama dan akronim: tulis panduan baca internal, dengarkan sampel, koreksi. SSML/alias pengucapan hanya jika mesin dan locale mendukung [6].
- Sintesis/rekam, dengarkan, koreksi tempo dan salah ucap; ukur durasi berkas audio dengan ffprobe, lalu ubah kata/jeda. Jangan mengaku sinkron kata jika belum diuji.

## Objek dulu, baru konsep
- Sebelum menulis penjelasan, daftar setiap kata benda penting: **nama → rupa (bentuk/ukuran/warna relatif) → bagian yang dikenali → letaknya terhadap objek lain → apa yang bergerak/berubah → bukti yang terlihat**. Verifikasi rupa dari objek/aset nyata; jangan mengarang detail. Jika abstrak (agen, API, memori), beri label sebagai **representasi visual**, bukan menyebut ikon/kartu sebagai bentuk fisik asli.
- Buka kemunculan pertama objek dengan gambaran yang bisa dibayangkan orang awam: “Di layar ada jendela terminal gelap; baris perintah masuk di atas, keluaran muncul di bawah.” Baru jelaskan istilah/fungsinya. Jangan berhenti di “sistem memproses data”.
- Tunjukkan satu transformasi kausal per beat: **sebelum → sentuhan/aksi → sesudah**. Kamera/ilustrasi harus memperlihatkan bagian yang berubah; narasi menyebut detail yang sama. Contoh: berkas kertas/ikon dokumen terbuka → baris disorot → angka masuk tabel → uji menandai sel yang keliru. Jangan menyamakan animasi dekoratif dengan bukti proses sungguhan.
- Pakai pembanding familiar hanya bila kemiripannya membantu dan batasnya jelas: “seperti meja kerja bercabang” menjelaskan pembagian tugas, bukan berarti agen adalah manusia sungguhan. Hindari analogi yang mengubah mekanisme.
- Uji tanpa label dan tanpa suara: minta penonton menunjuk objek, bagian yang bergerak, dan hasilnya. Jika hanya bisa menjawab “ada kartu dan panah”, revisi aset/shot menjadi objek atau antarmuka yang dikenali. Lalu uji audio tanpa gambar: pendengar harus bisa membayangkan bentuk dan perubahan penting tanpa dijejali deskripsi panjang.

## QC sebelum kirim
- Matriks: `rentang audio terukur | ucapan | satu aksi visual | teks layar <= satu frasa | klaim/bukti`.
- Tonton tanpa suara: apakah sebab-akibat terbaca? Dengar tanpa gambar: apakah cerita utuh? Periksa tiap klaim.
- Minta pendengar awam menceritakan ulang tanpa petunjuk; setelah rilis, pelajari retensi/umpan balik nyata, bukan mitos algoritma [5].
- Jangan karang kutipan, kemampuan produk, dampak, atau sumber. Contoh hipotetis diberi konteks sebagai contoh.

## Template singkat
```
Audiens / pertanyaan / satu pesan:
Fakta dan batas terverifikasi:
Hook → gangguan → aksi → bukti/perubahan → jawaban:
Naskah lisan:
Arahan suara (fokus, jeda, pelafalan):
Beat audio ↔ aksi visual:
Uji baca keras / durasi / klaim / pendengar:
```

Contoh kaku: “Hermes Agent mengorkestrasi multiagen dan tools secara paralel.”
Contoh lisan: “Kamu minta satu laporan. Satu agen membaca berkas; agen lain menjalankan alat. Hasilnya bertemu, lalu diperiksa sebelum sampai ke kamu.” Pastikan alur itu cocok dengan eksekusi nyata, bukan klaim universal.

## Sumber
[1] Dahlstrom (PNAS 2014), https://pmc.ncbi.nlm.nih.gov/articles/PMC4183170/
[2] CDC Plain Language, https://www.cdc.gov/health-literacy/php/develop-materials/plain-language.html
[3] Toastmasters Narrators, https://www.toastmasters.org/magazine/magazine-issues/2025/september/storytelling-tips-from-narrators
[4] Toastmasters Pauses, https://www.toastmasters.org/magazine/magazine-issues/2019/july/silence-is-golden
[5] YouTube Creators Audience & Optimize, https://www.youtube.com/creators/grow/understand-your-audience/ ; https://www.youtube.com/creators/grow/optimize-your-content/
[6] Microsoft Learn SSML Pronunciation, https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-synthesis-markup-pronunciation
