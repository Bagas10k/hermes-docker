---
name: fleet-branch-merge-protocol
description: "Use when parallel agents merge work into a verified core."
version: 0.2.0
platforms: [linux, macos]
metadata:
  hermes:
    tags: [multi-agent, parallel, branch-merge, verification-gate, unbounded-depth, consensus, file-ownership]
    related_skills: [autonomous-orchestrator, tiga-serangkai-orchestration, multiagent-worktree-orchestration, multiagent-consensus-circuit-breaker]
---

# Fleet Branch & Merge Protocol

Protokol orkestrasi armada sub-agent paralel untuk ekosistem LangitDev (Bagas Cihuy, VPS 4-core / 16 GB RAM, arsitektur database-per-tenant). Mengatur sistem isolasi cabang kerja, gerbang verifikasi bukti sebelum penggabungan (*evidence-first merge gate*), tata kelola kedalaman tanpa plafon berbasis disiplin anggaran ketat, konsensus artefak tertulis tanpa interupsi manusia, dan penjadwalan antrean paralel bebas hambatan (*zero idle worker*).

## When to Use
- Menggabungkan kode dari banyak sub-agent paralel ke cabang utama tanpa risiko tabrakan modifikasi (*write collisions*) atau regresi pada puluhan tenant ERP.
- Mengelola pendelegasian sub-agent bertingkat (anak melahirkan anak) dengan jaminan keamanan token dan memori agar tidak menguras sumber daya VPS.
- Menyelesaikan pertentangan antarmuka atau kebutuhan konsensus antarsub-agent secara otonom melalui pertukaran artefak tertulis tanpa mengganggu fokus Mas Bagas.
- Menjadwalkan antrean tugas paralel dinamis dengan prinsip pengisian slot instan demi efisiensi prosesor.

Don't use for:
- Tugas tunggal sekuensial berskala kecil yang tuntas dalam satu putaran tanpa pembuatan cabang kerja.
- Tugas inspeksi atau pembacaan berkas murni (*read-only*) tanpa modifikasi basis kode repositori.

## Prerequisites
- Repositori Git lokal aktif dengan konfigurasi `delegation.worktree_isolation: true`. **Periksa dulu bahwa direktori kerja memang repo git**: setelan ini hanya berlaku di git repo dengan backend terminal lokal, dan di luar itu ia turun diam-diam ke ruang kerja bersama (isolasi tidak terjadi meski setelannya menyala).
- Manifest kepemilikan berkas `.fleet/kepemilikan.json` terbit **sebelum** pekerja pertama lahir (lihat langkah 0 Procedure).
- Python 3.10+ standard library saja (`re`, `json`, `hashlib`, `dataclasses`, `pathlib`) — skrip gerbang tidak butuh dependensi pihak ketiga.
- Pemahaman konfigurasi `delegation.max_spawn_depth` dan batasan tool bawaan Hermes Agent.
- Ketersediaan skill rujukan: `autonomous-orchestrator`, `tiga-serangkai-orchestration`, `multiagent-worktree-orchestration`, `multiagent-consensus-circuit-breaker`.

## Quick Reference
```bash
# 1. Alokasi cabang terisolasi untuk tugas armada
git worktree add -b fleet/<task-id> /tmp/kanvas-worktrees/<task-id> main

# 2. Deklarasikan kepemilikan berkas SEBELUM pekerja lahir (satu berkas = satu penulis)
mkdir -p .fleet && $EDITOR .fleet/kepemilikan.json

# 3. Eksekusi pengujian deterministik pada HEAD sebelum merge
pytest /tmp/kanvas-worktrees/<task-id>/tests --quiet

# 4. Gerbang verifikasi (6 pilar) - WAJIB lulus sebelum langkah 5
python3 ~/.hermes/skills/autonomous-ai-agents/fleet-branch-merge-protocol/scripts/gerbang_gabung.py

# 5. Penggabungan aman setelah status gerbang LULUS
git merge --no-ff -m "[FLEET] Gabung terverifikasi fleet/<task-id>" fleet/<task-id>
git worktree remove --force /tmp/kanvas-worktrees/<task-id>
git branch -d fleet/<task-id>
```

## Procedure

0. **Pembagian Kepemilikan Berkas (Satu Berkas = Satu Penulis)**

   Sebelum pekerja apa pun lahir, induk membagi berkas menjadi **kepemilikan eksklusif**: setiap berkas punya tepat satu penulis, dan daftar itu mengikat. Ini pembagiannya:

   | Wilayah | Penulis tunggal | Isi |
   |---|---|---|
   | Berkas modul | pemilik modul | kode implementasi, uji modulnya sendiri |
   | Berkas kontrak | Perancang | antarmuka, skema data, tipe |
   | Berkas uji lintas modul | **QC** | uji integrasi, pemeriksa gerbang |
   | Berkas indeks/dokumen akar | induk | daftar isi, README, changelog |

   **Aturan mutlak:** tidak ada dua pekerja menulis berkas yang sama, kapan pun. Berkas bersama (indeks, konfigurasi, berkas rute, migrasi) **hanya ditulis induk** — bukan karena induk lebih pintar, tetapi karena berkas bersama adalah tempat semua orang bertemu, dan pertemuan di satu berkas adalah definisi bentrok.

   *Akibat kegagalan:* dua penulis pada satu berkas menghasilkan tulisan yang saling menimpa. Pekerja yang selesai terakhir menang, pekerjaan yang lain hilang tanpa jejak, dan tidak ada yang bisa menentukan versi mana yang benar — verifikasi jadi mustahil.

1. **Isolasi Cabang Mandiri Berbasis Git Worktree**
   Setiap sub-agent koding wajib dialokasikan ke ruang kerja terisolasi (`git worktree` dan cabang independen `fleet/<task-id>`), bukan bekerja langsung pada direktori inti. Agen induk mendefinisikan batas cakupan berkas yang boleh disentuh (`lingkup_berkas`).
   *Akibat kegagalan:* Menulis langsung pada cabang inti memicu tabrakan penulisan (*file overwrite*), riwayat commit kotor, dan merembesnya perubahan setengah jadi ke basis data tenant aktif.

2. **Gerbang Verifikasi Bukti pada HEAD Sebelum Penggabungan — Dijalankan QC (Evidence-First Merge Gate)**

   Gerbang ini adalah **pekerjaan QC**, bukan pekerjaan induk. Induk boleh memicunya, tetapi **penilai yang memutuskan lolos/tidak adalah Pengawas (QC) yang berbeda dari pelaksana yang diperiksa**. Bila induk memeriksa hasil pekerjaannya sendiri, itu bukan QC — itu pemeriksaan diri.

   Gerbang menginspeksi ulang bukti fisik pada commit HEAD cabang kerja sebelum `git merge` dieksekusi. Laporan mandiri sub-agent ("pekerjaan selesai", "LGTM") dikarantina sebagai **data tidak tepercaya**.

   **Urutan eksekusi (dua tahap, jangan dibalik):**
   - **Tahap 1 — Pemeriksa deterministik (QC, biaya token nol):** jalankan `scripts/gerbang_gabung.py` — 6 pilar (uji, kredensial, lingkup, target wajib, kepemilikan/bentrok, pergeseran kontrak). Ini menyaring mayoritas cacat tanpa biaya model.
   - **Tahap 2 — Penilaian semantik (QC, berbasis LLM):** hanya untuk hal yang benar-benar butuh pertimbangan: apakah kode memenuhi maksud tugas, apakah ada logika salah yang tetap lolos uji, apakah perubahan cocok dengan kontrak yang disepakati.

   **QC tidak menilai pekerjaannya sendiri.** QC yang sama tidak boleh (a) menulis kode yang diperiksa, (b) menjadi pelaksana pada cabang yang sama. Bila hanya ada satu pekerja yang tersedia untuk memeriksa, pekerjaan itu **tidak boleh digabung ke inti** sampai ada penilai independen.

   *Syarat mutlak:* Verifikasi tuntas SEBELUM penggabungan, bukan sesudahnya.
   *Akibat kegagalan:* Memverifikasi setelah penggabungan menyebabkan kode cacat meresap ke basis kode utama; rollback di sistem multi-tenant memaksa penghentian layanan puluhan basis data klien.

2b. **Ronde Perbaikan Antara QC dan Pelaksana**

   QC mengeluarkan **temuan konkret** (berkas, baris, perintah yang membuktikan, keluaran galat) — bukan "kurang bagus". Pelaksana memperbaiki, lalu QC memeriksa ulang **pada HEAD baru**, bukan pada HEAD lama. Maksimal 2 putaran.

   Bila putaran ke-2 tetap gagal: yang dihentikan **cabangnya**, bukan gerbangnya. Naikkan ke Mas Bagas dengan bukti kegagalan, atau delegasikan ulang dengan lingkup lebih kecil. Melewati gerbang karena "sudah mentok" adalah cara paling langsung memasukkan cacat ke produksi.

   **Pemisahan tugas dalam pelaporan:** yang menyatakan **LULUS** harus QC, bukan pelaksana. Bila pelaksana melaporkan hasilnya sendiri sebagai lulus, itu bukan laporan — itu klaim.

3. **Matriks Otorisasi Penggabungan Otomatis vs Izin Manusia**
   - **Penggabungan Otomatis (Zero-Click Gate):** Diizinkan untuk perubahan berlingkup terbatas yang lolos 100% gerbang deterministik (dokumentasi teknis, penambahan file tes baru, perbaikan bug lokal dalam modul tertutup).
   - **Wajib Izin Manusia (1-Click Mas Bagas):** Wajib meminta konfirmasi eksplisit pengguna untuk setiap perubahan yang menyentuh skema database tenant, logika mutasi keuangan/pembayaran, kunci rahasia/lingkungan produksi, dan arsitektur inti sistem (`SYSTEM/`).
   - *Akibat kegagalan:* Menggabungkan perubahan struktural keuangan secara otomatis memicu risiko ketidaksesuaian saldo akuntansi klien dan sanksi audit.

4. **Gerbang Verifikasi Deterministik (Skrip Nyata, 6 Pilar)**

   Skrip lengkap ada di `scripts/gerbang_gabung.py` — jalankan untuk uji invariannya sendiri:

   ```bash
   python3 ~/.hermes/skills/autonomous-ai-agents/fleet-branch-merge-protocol/scripts/gerbang_gabung.py
   # -> LULUS: 11 uji invarian gerbang lolos.
   ```

   Enam pilar yang diperiksa:

   | # | Pilar | Menangkap |
   |---|---|---|
   | 1 | Uji lulus (exit code) | Kode yang tidak berjalan |
   | 2 | Tidak ada kredensial bocor | Token/kunci masuk ke repositori |
   | 3 | Kepatuhan lingkup berkas | Pekerja menyentuh berkas di luar kontraknya |
   | 4 | Berkas target wajib benar-benar diubah | "Selesai" tanpa mengerjakan apa pun |
   | 5 | Kepemilikan berkas + bentrok antar-pekerja | Dua penulis pada satu berkas |
   | 6 | **Pergeseran kontrak antarmuka** | Bentrok semantik yang tidak terlihat git |

   Pilar 6 adalah yang paling sering hilang dari sistem serupa, dan yang paling mahal akibatnya: dua pekerja mengubah berkas berbeda, masing-masing benar sendiri, tetapi bentuk data di antaranya berubah. Git tidak mendeteksinya, uji per-modul lulus, sistem tetap terkompilasi — kerusakannya baru muncul saat kedua bagian dijalankan bersamaan. Yang mendeteksinya hanyalah perbandingan **sidik kontrak** (fungsi `sidik_kontrak`).

   Panggil sebagai pustaka:

   ```python
   from gerbang_gabung import periksa_gerbang_gabung, muat_kepemilikan, sidik_kontrak

   hasil = periksa_gerbang_gabung(
       berkas_diubah=daftar_berkas,
       lingkup_berkas=lingkup, berkas_target_wajib=target,
       kode_keluar_uji=exit_code, konten_berkas_map=isi_berkas,
       berkas_pekerja_lain=berkas_pekerja_lain, ada_konflik_git=ada_konflik,
       kepemilikan=muat_kepemilikan(".fleet/kepemilikan.json"), penulis=nama_pekerja,
       sidik_kontrak_sebelum=sidik_lama, kontrak_sekarang=kontrak_kini, id_kontrak="K-01",
   )
   if not hasil.lulus:
       raise SystemExit("Gerbang menolak penggabungan:\n" + "\n".join(hasil.temuan_gerbang))
   ```

   Manifest kepemilikan (`.fleet/kepemilikan.json`) dibaca lewat `muat_kepemilikan()`:

   ```json
   {"berkas": {"app.py": "pekerja-a", "rute.py": "induk", "modul/pesanan.py": "pekerja-b"}}
   ```

   Aturan gerbang: **semua temuan dikumpulkan, bukan berhenti di temuan pertama.** QC perlu melihat seluruh daftar cacat sekaligus untuk memperbaikinya dalam satu putaran — berhenti di temuan pertama memaksa putaran perbaikan berulang dan membuang jatah rework 2 kali.

5. **Tata Kelola Kedalaman Tanpa Plafon Berbasis Anggaran (Unbounded Depth)**
   - **Arsitektur Tingkat Hermes:** Pengaturan `delegation.max_spawn_depth` menentukan kedalaman delegasi. Nilai bawaan adalah 1 (armada datar tanpa hierarki). Angka 2 berarti agen anak diizinkan melahirkan cucu; angka 3 mengizinkan hierarki 3 tingkat. Secara komputasi Hermes tidak menetapkan batas atas (tanpa plafon).
   - **Distribusi Peran Berbasis Kedalaman:** Peran sub-agent ditentukan secara mutlak oleh KEDALAMAN posisi, bukan oleh instruksi teks atau permintaan tugas. Sub-agent dengan kedalaman `< max_spawn_depth` otomatis berstatus `orchestrator` (mempertahankan hak `delegate_task`). Sub-agent pada tingkat terdalam (`leaf`) murni berstatus kuli eksekusi.
   - **Restriksi Tool Ketat:** Agen peran `leaf` DILARANG memanggil `delegate_task`, `clarify`, `memory`, `send_message`, dan `cronjob`. Agen `orchestrator` mempertahankan `delegate_task` untuk dekomposisi lanjutan, namun tetap DILARANG memanggil `clarify`, `memory`, `send_message`, dan `cronjob`. Kedua peran tetap memiliki akses penuh ke `execute_code`.
   - **Konsekuensi Komunikasi Pengguna:** Sub-agent anak TIDAK BISA bertanya langsung kepada Mas Bagas karena tool interaksi diblokir sistem. Segala bentuk eskalasi wajib merayap naik melalui rantai agen induk.
   - **Pengendali Anggaran Nyata (bukan plafon jumlah):** Jumlah sub-agent **tidak dibatasi** — yang mengendalikan adalah anggaran, bukan angka. Tanpa rem anggaran, biaya token dan thread proses meledak berlipat per tingkat secara eksponensial ($O(B^D)$). Pada VPS 4-core / 16 GB RAM, ledakan sub-agent liar memicu Linux OOM-killer yang merusak proses PM2 dan basis data. Rem yang wajib dipasang:
     - `child_timeout_seconds` (rekomendasi 180-300 detik) — anak yang menggantung memakan slot dan token tanpa hasil.
     - Pemutus sirkuit kegagalan: bila satu cabang gagal 2 kali berturut-turut pada tujuan yang sama, dilarang melahirkan anak baru pada cabang itu; hentikan rantai tersebut seketika.
     - Pemeriksaan ringkas sebelum menaikkan kedalaman: apakah tugas benar-benar butuh anak, atau cukup dikerjakan anak yang sudah berjalan? Menaikkan kedalaman untuk tugas yang tidak butuh anak hanya menambah biaya dan titik kegagalan senyap.
     - Pantau konsumsi RAM VPS; hentikan penambahan pekerja bila mendekati batas, karena OOM-killer membunuh proses acak (termasuk PM2 dan basis data tenant), bukan hanya sub-agent.

6. **Protokol Rembukan Sesama Agen Melalui Pertukaran Artefak Tertulis**
   - **Prinsip Mandiri Tanpa Interupsi:** Dilarang menginterupsi Bagas Cihuy untuk persoalan sintaks bahasa, dokumentasi modul, cara integrasi dependensi, atau penelusuran galat teknis. Jika kurang pengetahuan teknis, sub-agent wajib melakukan riset mandiri (membaca web, dokumentasi resmi, atau basis kode lokal).
   - **Batas Eskalasi ke Pengguna:** Tanya ke Mas Bagas HANYA untuk: (a) kebutuhan logika bisnis tenant riil, (b) kendala perangkat keras atau lingkungan nyata di luar server, (c) pilihan preferensi arsitektur yang hanya diketahui pemilik sistem, atau (d) keputusan berdampak besar yang tidak dapat disimpulkan dari data.
   - **Komunikasi Berbasis Berkas (Artefak Tertulis):** Karena sub-agent tidak memiliki soket komunikasi langsung antar-sesama, rembukan diwujudkan lewat pertukaran dokumen fisik di direktori proyek bersama:
     - `KONTRAK-ANTARMUKA.md`: Diterbitkan oleh agen perancang sebelum koding dimulai; memuat spesifikasi skema JSON, tipe data input/output, dan batasan invariant. Seluruh sub-agent hilir wajib membaca berkas ini sebelum mengetik kode.
     - `TEMUAN.md`: Dokumentasi temuan lapangan, keterbatasan library, atau bug internal yang ditemukan selama eksekusi.
     - `KEPUTUSAN.md`: Keputusan konsensus teknis yang mengikat seluruh armada. Jika terjadi ketidaksepakatan antar-agen, keputusan agen induk bersifat final.
     - Untuk pembobotan konsensus dan pencegahan halusinasi kelompok, rujuk `multiagent-consensus-circuit-breaker` (voting terbobot bukti empiris) dan `byzantine-multiagent-debate` (audit quorum BFT).
   - *Akibat kegagalan:* Bertanya hal sepele ke pengguna menurunkan kecepatan eksekusi dan merusak fokus bisnis; sebaliknya, beroperasi tanpa kontrak tertulis memicu ketidakcocokan antarmuka modul saat digabungkan.

7. **Manajemen Kerja Paralel yang Efisien (Dynamic Slotted Pipeline)**
   - **Dekomposisi Kecil dan Banyak:** Pecah pekerjaan besar menjadi unit-unit tugas kecil berdurasi 1-3 menit daripada beberapa tugas raksasa. Tugas kecil mencegah pekerja cepat menganggur menunggu pekerja yang paling lambat.
   - **Pengawas Ikut Menghitung Slot:** Pengawas adalah pekerja, bukan biaya di luar hitungan — ia memakai satu slot konkurensi dan membakar token. 3 pelaksana + 1 pengawas = 4 slot terpakai. Mengabaikan ini membuat plafon konkurensi jebol dan pekerja terakhir tidak pernah dapat slot.
   - **Pengisian Ulang Slot Seketika (Slot Refilling):** Jangan menunggu satu gelombang (*batch*) selesai penuh. Begitu satu sub-agent menuntaskan pekerjaannya dan lolos gerbang verifikasi, langsung isi slot konkurensi yang kosong dengan tugas antrean berikutnya.
   - **Larangan Pengambilalihan Tugas Berjalan:** Pekerjaan yang telah didelegasikan kepada satu sub-agent pantang diambil alih oleh sub-agent lain. Mengambil alih tugas memicu penulisan berkas tumpang tindih (*race condition*) dan membatalkan keabsahan audit gerbang.
   - **Penanganan Pekerja Macet:** Jika transkrip satu sub-agent berhenti bergerak melampaui batas toleransi sementara yang lain berjalan maju, segera eksekusi `stop`. Ambil hasil parsial yang valid di disk, lalu delegasikan sisa tugas yang belum selesai sebagai tugas baru.
   - **Mandor Pantang Berdiam Diri:** Selagi sub-agent bekerja di worktree masing-masing, agen induk memanfaatkan waktu tunggu untuk menyiapkan skrip verifikasi, memeriksa log parsial, mengagregasi dokumentasi, atau merapikan indeks repositori.
   - *Akibat kegagalan:* Antrean kaku berbasis gelombang membuang 40-60% siklus CPU VPS; pengambilalihan tugas aktif menyebabkan kerusakan berkas yang tidak dapat dipulihkan.

## Pitfalls
- **Bentrok Semantik yang Lolos Deteksi (Semantic Merge Conflict):** Dua pekerja mengubah berkas berbeda secara terpisah, masing-masing benar sendiri, tetapi **kontrak di antara keduanya berubah** — fungsi mengembalikan bentuk lain, kolom berubah tipe, nama field berubah. Git tidak mendeteksi ini (tidak ada baris yang bertabrakan), uji per-modul lulus, dan sistem tetap terkompilasi. Yang rusak baru muncul saat kedua bagian dijalankan bersamaan. Ini bahaya terbesar sistem paralel karena **tidak ada alarm**. Pencegahannya bukan penggabungan yang lebih pintar, melainkan **kontrak antarmuka tertulis** yang diterbitkan Perancang sebelum koding, plus uji integrasi milik Pengawas yang menjalankan kedua sisi bersamaan.
- **Verifikasi Pasca-Gabung (Post-Merge Trap):** Menggabungkan cabang ke inti sebelum pengujian tuntas. Akibatnya: kode rusak mencemari cabang inti dan memicu pemadaman layanan pada tenant ERP.
- **Klaim Mandiri Tanpa Verifikasi Ulang (Self-Report Blindness):** Mempercayai klaim sub-agent bahwa fiturnya telah berjalan sempurna tanpa menguji langsung commit HEAD. Akibatnya: kode stub atau implementasi palsu meresap ke sistem.
- **Ledakan Rekursi Tanpa Anggaran (Spawning Explosion):** Mengaktifkan kedalaman tak terbatas tanpa batas waktu dan tanpa pemantauan RAM. Jumlah pekerja boleh tak terbatas, tetapi tanpa `child_timeout_seconds` dan pemantauan memori, biaya token meledak dan OOM-killer VPS membunuh proses PM2 serta basis data tenant — bukan hanya sub-agent.
- **Eskalasi Trivial ke Pengguna (Human Distraction Fatigue):** Mengajukan pertanyaan teknis yang jawabannya ada di dokumentasi atau web ke Mas Bagas. Akibatnya: memperlambat laju proyek dan membebani pengguna dengan rincian implementasi.
- **Antrean Tunggu Gelombang Kaku (Wave Stall Bottleneck):** Menunggu seluruh tugas dalam satu gelombang selesai sebelum memulai tugas baru. Akibatnya: pemborosan sumber daya komputasi VPS karena agen cepat menganggur lama.

## Verification
- **QC** menjalankan skrip gerbang dan memastikan keluaran `LULUS: 11 uji invarian gerbang lolos.` Induk boleh memicunya, tetapi penilai yang memutuskan lolos/tidak adalah QC yang berbeda dari pelaksana.
- Periksa **kepemilikan berkas**: setiap berkas yang berubah wajib muncul di `.fleet/kepemilikan.json` dengan tepat satu penulis. Berkas bersama yang disentuh pekerja (bukan induk) adalah pelanggaran.
- Untuk setiap pasangan modul yang saling memanggil: jalankan uji integrasi yang menyentuh **kedua sisi** pada commit yang akan digabung, bukan hanya uji masing-masing modul.
- Periksa status Git worktree: pastikan seluruh cabang kerja `fleet/*` telah dibersihkan secara atomik setelah penggabungan terverifikasi.
- Pastikan berkas `KONTRAK-ANTARMUKA.md` dan `KEPUTUSAN.md` terbit pada direktori kerja sebelum fase koding paralel dimulai.

*Skipped: implementasi soket IPC antar-proses p2p, memilih pertukaran dokumen berbasis disk lokal.*
*Add when: frekuensi sinkronisasi status antar-agen melampaui kemampuan I/O disk pada armada di atas 50 pekerja aktif.*
