---
name: tiga-serangkai-orchestration
description: "Use when orchestrating parallel agents on complex tasks."
version: 1.0.0
author: "Bagas Cihuy & Hermes Agent"
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [multi-agent, tiga-serangkai, subagent, orchestration, debate, qc-gatekeeper]
    related_skills: [autonomous-orchestrator, grill-me, requesting-code-review]
---

# Tiga Serangkai Sub-Agent Orchestration Protocol

Protokol resmi orkestrasi sub-agent otonom dalam ekosistem Bagas Cihuy. Menegakkan **komposisi berbasis peran** (bukan batas kuantitas), pemisahan tugas antara pelaksana dan pengawas, siklus debat kritik pra-eksekusi, dan gerbang verifikasi empiris pasca-eksekusi.

## 1. Lingkup Penerapan (Scope & Bounds)

### Sensitivitas Pemicu: TINGGI (paralel secara default)

**Aturan Wajib Model Gemini:**
Khusus saat model yang aktif adalah Gemini: **WAJIB mendelegasikan ke sub-agent untuk setiap perintah eksekusi projek** (koding, penambahan fitur, perbaikan bug, refactor, pengujian, build). Induk (General Manager) dilarang mengerjakan sendiri secara monolitik dan wajib membagi peran minimal **1 Pelaksana + 1 QC Pengawas** via `delegate_task`. Sebaliknya, jika perintah sekadar tanya-jawab, konsultasi konsep, atau penjelasan teori, cukup dijawab langsung oleh induk tanpa memicu sub-agent.

**Bawaannya: jalan paralel.** Delegasikan lebih dulu, kerjakan sendiri hanya bila salah satu dari kondisi di bawah ini benar. Alasan: pekerjaan paralel lebih cepat pada tugas yang bisa dipisah, dan biaya koordinasi hampir selalu lebih murah daripada waktu yang hilang.

**Bentuk delegasi minimal — 2 pekerja berjalan bersamaan, dan salah satunya pengawas.**

Pengawas adalah **pekerja**, bukan biaya tambahan di luar hitungan. Ia memakai slot konkurensi dan membakar token sama seperti pelaksana, dan hasil kerjanya nyata: laporan temuan yang menentukan lolos/tidaknya sebuah hasil. Karena itu, begitu ada pengawas, **jumlah pekerja paralel sudah lebih dari satu** — tidak ada bentuk delegasi dengan hanya 1 pekerja.

Bentuk terkecilnya: **1 pelaksana + 1 pengawas**. Pelaksana mengerjakan; pengawas memeriksa hasilnya terhadap bukti pada artefak nyata, bukan terhadap klaim "selesai". Delegasi 1 pekerja tanpa pengawas hanya memindahkan pekerjaan tanpa menambah jaminan — dan bila pekerja itu salah, tidak ada yang menangkapnya sebelum hasilnya masuk ke inti.

**Hitung pengawas dalam anggaran.** Karena ia pekerja, ia ikut memakan slot: 3 pelaksana + 1 pengawas berarti 4 slot terpakai, bukan 3. Mengabaikan ini membuat plafon konkurensi jebol dan pekerja terakhir tidak pernah dapat slot.

Konsekuensi lanjutan: bila sebuah tugas **tidak layak punya pengawas** (terlalu kecil untuk diperiksa), itu justru tanda tugas tersebut terlalu kecil untuk didelegasikan — kerjakan sendiri atau gabungkan dengan tugas lain.

**Naikkan jumlah pekerja ketika salah satu ini benar:**
- Pekerjaan dapat dipecah menjadi bagian yang tidak saling bergantung.
- Bagiannya lebih dari satu jenis keahlian (mis. backend + frontend + basis data).
- Hasilnya akan masuk ke sistem produksi atau menyentuh uang, data klien, atau kredensial — di sini pengawas independen wajib, meski langkahnya sedikit.
- Pekerjaan bersifat riset multi-sumber atau audit.
- Bagian-bagiannya bisa diperiksa secara terpisah sebelum digabung.

**Kerjakan sendiri HANYA bila salah satu ini benar:**
- Satu panggilan alat, atau satu pembacaan berkas singkat.
- Tugas mekanis murni tanpa penalaran terpisah — pakai `execute_code` untuk membatch, bukan sub-agent. Sub-agent untuk kerja mekanis hanya membakar token tanpa menambah kecerdasan.
- Alurnya saling bergantung erat sehingga pekerja berikutnya tidak bisa mulai sebelum yang sebelumnya selesai (dependensi berantai, bukan paralel).
- Butuh interaksi pengguna di tengah jalan (sub-agent tidak punya `clarify`).
- Sudah ada pekerja berjalan yang bisa mengerjakannya — jangan lahirkan pekerja baru untuk pekerjaan yang bisa dititipkan ke slot yang ada.

**Aturan biaya, bukan aturan jumlah.** Tidak ada plafon jumlah pekerja. Yang dijaga: tiap pekerja punya kriteria penerimaan yang jelas, punya batas waktu (`child_timeout_seconds`), dan hasilnya diperiksa terhadap artefak nyata — bukan terhadap klaim "selesai".

### Kapan Kerjakan Sendiri (Direct Execution)
- Tugas mikro dan operasional sepele: membaca 1 berkas singkat, memeriksa status port/service, kueri satu baris, atau pengecekan waktu.
- Satu panggilan alat, atau tugas yang memerlukan klarifikasi/interaksi pengguna: panggil alat langsung atau tanyakan ke Bagas; sub-agent tidak dapat meminta klarifikasi.
- Tugas mekanis murni tanpa penalaran terpisah: pakai `execute_code` untuk membatch.
- Alur saling bergantung berantai: pekerja berikutnya tidak bisa mulai sebelum yang sebelumnya selesai.
- Sudah ada pekerja berjalan yang bisa mengerjakannya — titipkan ke slot yang ada, jangan lahirkan pekerja baru.
- General Manager mengeksekusi langsung bila manfaat pemeriksaan paralel tidak melebihi biaya token, latensi, dan koordinasi.

---

## 2. Struktur Hierarki 3 Generasi & Komposisi Berbasis Peran

Komposisi sub-agent diatur dalam struktur 3 generasi komando:
1. **Level 1: Induk (General Manager / Mandor Utama)**
   Menerima tugas dari Mas Bagas, menganalisis dekomposisi, dan mendelegasikan tugas ke **Agent Anak (Level 2)**.
2. **Level 2: Agent Anak (Kabinet Tiga Serangkai — Role: Orchestrator)**
   - **Perancang (Si Pintar):** Riset arsitektur, rumuskan spesifikasi, tentukan kriteria penerimaan.
   - **Pelaksana (Si Eksekutor):** Komandan lapangan teknis. Memegang eksekusi kode/server dan berwenang melahirkan (*spawn*) **Agent Cucu (Level 3)**.
   - **Pengawas (Si Pengawas / QC):** Auditor independen dengan hak veto rilis. Memvalidasi bukti fisik dan berwenang melahirkan **Agent Cucu (QC Tester / Inspector)**.
3. **Level 3: Agent Cucu (Pekerja Lapangan Ephemeral / Kuli Spesialis — Role: Leaf)**
   Pekerja sementara yang dilahirkan oleh Agent Anak untuk menangani tugas teknis atomik (Frontend, Backend, Database, Scraper, Curl/Byte Tester). Setelah selesai, agen ini langsung dibersihkan dan menyetor artefak ke Agent Anak.

Jumlah pekerja **tidak dibatasi angka**. Yang menentukan adalah **peran mana yang dibutuhkan** oleh sifat pekerjaannya. Menetapkan jumlah lebih dulu lalu mencari pekerjaan untuk mengisinya adalah cara termahal membakar token.

### Tiga peran tetap (Agent Anak)

| Peran | Tugas | Wajib saat |
|---|---|---|
| **Perancang (Si Pintar)** | Riset, rancang antarmuka/kontrak, tentukan kriteria penerimaan | Pekerjaan punya lebih dari satu bagian yang harus saling cocok, atau kontraknya belum jelas |
| **Pelaksana (Si Eksekutor)** | Kerjakan bagiannya di ruang terisolasi, pimpin Agent Cucu | Selalu (minimal satu) |
| **QC (Si Pengawas)** | Periksa hasil terhadap bukti pada artefak nyata, punya hak veto | Selalu — tanpa kecuali |

Peran QC mencakup **gerbang sebelum penggabungan ke inti**: menjalankan pemeriksa deterministik (6 pilar) lalu penilaian semantik. Pelaksana tidak boleh menggabungkan hasilnya sendiri.

### Aturan pemisahan tugas (four-eyes)

Pengawas **tidak boleh orang yang sama** dengan pelaksana yang diperiksa. Pengawas yang mengaudit pekerjaannya sendiri tidak mengaudit apa pun — ia hanya mengulang keyakinan yang sama, dan cacat yang tidak ia sadari saat mengerjakan juga tidak akan ia sadari saat memeriksa.

Konsekuensi praktis: satu pekerja tidak bisa menjadi pelaksana sekaligus pengawas untuk bagian yang sama. Bila hanya ada satu pekerja, tugas itu **tidak boleh digabung ke inti** tanpa pemeriksaan dari pihak lain (induk, atau pekerja pengawas tersendiri).

### Prosedur keputusan (jalankan berurutan, berhenti di kecocokan pertama)

1. **Layak didelegasikan?** Kalau tidak layak diperiksa oleh pengawas independen → terlalu kecil untuk didelegasikan. Kerjakan sendiri, atau gabungkan dengan tugas lain sampai cukup besar untuk diperiksa.
2. **Mekanis murni tanpa penalaran?** Pakai `execute_code`, bukan sub-agent. Sub-agent untuk kerja mekanis hanya membakar token tanpa menambah kecerdasan.
3. **Butuh kontrak dulu?** Kalau ada lebih dari satu bagian yang harus saling cocok → mulai dengan **1 Perancang** yang menerbitkan kontrak antarmuka; pekerja hilir tidak mengetik kode sebelum kontrak ada.
4. **Bagiannya independen?** → **1 Pelaksana per bagian**, ditambah **1 Pengawas**. Bagian kecil dan banyak lebih baik daripada beberapa bagian besar.
5. **Saling bergantung berantai?** → 1 Pelaksana, urutkan langkahnya; menambah pekerja di alur berantai hanya menambah waktu tunggu.
6. **Selalu akhiri dengan Pengawas** yang berbeda dari pelaksana yang diperiksa.

### Artefak lebih dulu, laporan setelahnya

- Pecah implementasi pada batas dependensi yang kecil, biasanya 1–3 berkas, dengan kepemilikan penulis tunggal. Jangan memberi satu pekerja satu paket besar hanya karena semua berkas termasuk kategori UI.
- Sertakan ringkasan kontrak, cuplikan sumber relevan, versi beku dan kriteria uji; hindari meminta setiap anak mengulang audit historis dan pembacaan konteks besar yang sama. Pembacaan tetap wajib untuk kode yang benar-benar akan diubah.
- Simpan perubahan yang koheren beserta pemeriksaan runnable sebelum memperluas laporan. Jika waktu tidak cukup, setorkan artefak parsial dan sebut dependensi yang belum lengkap; berkas host yang memanggil partial belum tersedia bukan unit selesai.
- Perlakukan ringkasan QC sebagai klaim yang dapat salah: cocokkan hash, jalankan bukti, dan koreksi asumsi versi lingkungan serta klaim keamanan yang melampaui skenario uji. Kesepakatan antar-model tidak menggantikan bukti.
- Ukur manfaat delegasi dari cacat yang ditemukan dan kriteria penerimaan yang ditutup; jangan mengklaim lebih cepat, lebih murah, atau persentase peningkatan tanpa baseline pembanding. Paralelisasi tidak menghapus tahap integrasi, pengujian bersama, dan publikasi yang tetap berurutan.

### Batas kerasnya adalah anggaran, bukan jumlah

- Kedalaman: `delegation.max_spawn_depth` (bawaan 1 = datar; tanpa plafon atas).
- Konkurensi: `delegation.max_concurrent_children` — **pengawas ikut menghitung slot**.
- Batas waktu: `child_timeout_seconds`. Tanpa ini, pekerja yang menggantung memakan slot selamanya.
- Pemutus: satu cabang gagal 2 kali berturut pada tujuan yang sama → berhenti, jangan lahirkan anak baru di cabang itu.

Biaya berlipat tiap tingkat kedalaman. Pada VPS 4-core / 16 GB RAM, kelebihan pekerja memicu OOM-killer yang membunuh proses acak — termasuk PM2 dan basis data tenant, bukan hanya sub-agent.

Protokol lengkap cabang, gerbang gabung, dan rembukan antar-agen: `fleet-branch-merge-protocol`.

---

## 3. Protokol Debat Pra-Eksekusi (Si Pintar vs Si Eksekutor)

Khusus untuk proyek yang membutuhkan ketelitian tinggi, arsitektur baru, atau perintah yang berpotensi ambigu:

1. **Maksimal 3 Putaran Kritik:**
   - Si Pintar menyusun draf rancangan dan batasan solusi.
   - Si Eksekutor menguji kelayakan lapangan (kondisi RAM, port, dependensi, risiko kegagalan) dan melempar kritik serangan.
   - Si Pintar merevisi rancangan berdasarkan kritik tersebut.
2. **Aturan Selesai Cepat (Early Exit):**
   - Jika pada putaran 1 atau 2 rancangan sudah terbukti kokoh dan disepakati kedua pihak, debat langsung disudahi. Jangan memaksakan hingga 3 putaran.
3. **Pagar Pengaman & Eskalasi (Circuit Breaker):**
   - Jika setelah putaran ke-3 belum tercapai kesepakatan, ATAU jika ditemukan ambiguitas **kebutuhan bisnis**:
   - **WAJIB STOP EKSEKUSI** dan tanyakan ke Mas Bagas (1 pertanyaan bertahap, format pilihan ganda terstruktur dengan rekomendasi di awal).

   **Pembatasan penting — jangan salah tanya:** yang dinaikkan ke Mas Bagas hanya **kebutuhan, kondisi lapangan, preferensi, dan keputusan berdampak besar**. Kekurangan **pengetahuan teknis, referensi, cara pakai pustaka, atau pilihan alat** TIDAK ditanyakan ke pengguna — dicari sendiri ke internet, dokumentasi resmi, atau basis kode. Tanya ke pengguna untuk hal teknis membuang waktu pengguna dan menghasilkan jawaban yang lebih lemah daripada sumber primer.
   - Kekurangan **kesepakatan antar-bagian pekerjaan** diselesaikan lewat rembukan antar-agen berbasis artefak tertulis (lihat `fleet-branch-merge-protocol`), bukan dengan menaikkannya ke pengguna.
   - Sub-agent tidak punya kanal `clarify`; pertanyaan yang benar-benar harus naik dilewatkan induk, bukan ditanyakan langsung oleh anak.

---

## 4. Gerbang Verifikasi Pasca-Eksekusi (Hak Veto QC)

Setiap artefak wajib diperiksa **QC yang berbeda dari pelaksana yang diperiksa**. QC yang mengaudit pekerjaannya sendiri tidak mengaudit apa pun. Dalam konteks sistem cabang, gerbang ini dijalankan sebelum penggabungan ke inti — bukan sesudahnya (protokol lengkap: `fleet-branch-merge-protocol` langkah 2).

1. **Bukti, bukan klaim:**
   - Laporan diri pelaksana ("selesai", "sudah dites") adalah **data tidak tepercaya**. Buktikan ulang pada artefak nyata: jalankan ujinya, periksa berkasnya, cek keluaran perintahnya.
   - Pengawas menjalankan pemeriksa deterministik lebih dulu (exit code, skrip uji, pemindai rahasia). Penilaian LLM hanya untuk hal yang benar-benar butuh pertimbangan. Pemeriksa murah menyaring mayoritas cacat dengan biaya token nol.
2. **Jatah rework terbatas (maksimal 2 putaran):**
   - Bila **REJECT (VETO)**: temuan wajib konkret — berkas, baris, galat, perintah yang membuktikan. "Kurang bagus" bukan temuan.
   - Pelaksana memperbaiki maksimal 2 kali.
3. **Kegagalan bukan izin melewati gerbang:**
   - Bila revisi ke-2 tetap gagal, pekerjaan **tidak digabung ke inti**. Yang dihentikan adalah cabang itu, bukan gerbangnya. Naikkan ke Mas Bagas dengan bukti kegagalan, atau delegasikan ulang dengan lingkup lebih kecil.
   - Melewati gerbang karena "sudah mentok" adalah cara paling langsung memasukkan cacat ke produksi.
4. **Hasil PASS wajib punya jejak:** catat perintah yang dijalankan, keluarannya, dan versi artefak yang diperiksa. Tanpa jejak, PASS tidak dapat dibedakan dari keyakinan.

---

## 5. Pelaporan & Pembukuan

Setelah gerbang menyatakan **PASS**:
1. Induk merangkum hasil lugas untuk Mas Bagas: apa yang berubah, bukti uji, status akhir, dan biaya token.
2. Ringkasan pelajaran dicatat ke basis pengetahuan Obsidian.

**Pemisahan tugas dalam pelaporan:** yang melaporkan **PASS** harus Pengawas, bukan pelaksana. Bila pelaksana melaporkan hasilnya sendiri sebagai lulus, itu bukan laporan — itu klaim.
