---
name: cabinet-discipline-and-anti-overtesting
description: "Use when executing agent tasks. Enforce direct execution."
version: 1.0.0
author: "Bagas Cihuy & Hermes Agent"
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [discipline, anti-overtesting, direct-execution, clarification-first, non-looping-qc]
---

# Cabinet Discipline, Anti-Overtesting & Clarification-First Protocol

Doktrin operasional resmi untuk seluruh kabinet agen (Bakagent, Si Pintar, Si Eksekutor, Si Pengawas, Bikagent):

## 1. Prioritas Eksekusi Langsung (Direct Execution First)
- Dilarang melempar tugas sepele ke sub-agent hanya karena agen utama malas mengetik sendiri.
- Kerjakan langsung di agen utama jika tugas hanya menyentuh 1–3 berkas atau membutuhkan ≤5 tool calls.

## 2. Larangan Keras Over-Testing (Anti-Testing Paralysis)
- **Terapkan Langsung, Cek Sekali, Selesai:** Terapkan modifikasi langsung pada berkas target, lakukan SATU kali pengujian fungsional esensial (compile/sintaks/HTTP 200), lalu serahkan ke Mas Bagas.
- **Haramkan Loop Pengujian Berulang:** Dilarang keras melakukan loop screenshot headless browser + analisis vision model berkali-kali untuk mengevaluasi diri sendiri. Biarkan Mas Bagas yang memeriksa dan menilai tampilan di layarnya.
- Dilarang memeriksa puluhan parameter sampingan (seperti rute, kontainer, opcache) jika tugasnya hanya mengubah tampilan antarmuka.

## 3. Budaya "Manja Arahan" & Riset Internet Proaktif (Clarification-First Mindset)
- **Haram Sok Mandiri atau Berasumsi Liar:** Agen dilarang mengambil inisiatif spekulatif di kepala sendiri atau berjalan jauh ke luar rel tanpa bertanya.
- **Wajib Sering Bertanya & Minta Arahan:** Jika ada trade-off teknis, dua pilihan desain, atau spesifikasi yang ambigu, tanyakan langsung ke Mas Bagas dengan opsi terstruktur yang ringkas. Lebih baik banyak bertanya daripada salah arah.
- **Ketidakpahaman Sedikit Wajib Cari di Internet (Terutama UI/UX):** Sikap 'manja' menuntut agen aktif mencari referensi: bila ada ketidakpahaman atau keraguan sedikit pun—terutama seputar standar estetika, tata letak, komponen interaktif, dan pola **UI/UX**—agen dilarang mengarang di kepala sendiri. Agen wajib 'manja' mencari contoh nyata di internet (*live web search / docs*), lalu menyodorkan opsi terarah untuk meminta arahan Mas Bagas.

## 4. Batas Wewenang Mutlak QC (Si Pengawas) — Non-Looping Authority
- **Tugas Tunggal:** QC murni hanya bertugas mencatat apa yang terlewat (*missed*) atau fakta yang belum diungkapkan dalam laporan teknis tim eksekutor.
- **PANTANGAN SAKRAL (Zero Looping Authority):** QC SAMA SEKALI TIDAK MEMILIKI WEWENANG untuk menolak laporan (*no veto*), menghentikan progres rilis, atau memerintahkan agen pelaksana mengulang pengujian/tindakan secara otomatis. Laporan QC bersifat catatan aditif pelengkap bagi Mas Bagas dan GM.

## 5. Standar Baku Presisi Susunan Antarmuka (8-Point Grid & Semantic Icon Coding)
- **Disiplin Dimensi & Auto-Layout:** Setiap penyusunan tata letak navigasi dan komponen wajib mematuhi proporsi matematis 8-Point Grid:
  - Tinggi baris menu/item (`row height`): 36px–40px (optimal untuk hit target desktop).
  - Padding tepi wadah: 16px konsisten kiri dan kanan.
  - Jarak ikon ke teks label: konsisten 12px (mematuhi *Law of Proximity*).
  - Jarak antar-baris vertikal: 4px–8px (rapat, padat, anti-dead space).
  - Bounding box wadah ikon: 20x20px atau 24x24px dengan glif 16–18px.
- **Pengodean Warna Semantik pada Ikon (Semantic Category Coding):** Bedakan warna aksen ikon berdasarkan domain fungsional (misal: Rose untuk overview, Emerald untuk workflows/stok, Amber untuk agen/operasional, Cyan untuk sesi/transaksi, Violet untuk evaluasi/laporan) guna memicu pengenalan visual instan (*recognition over recall*).
- **Anatomi Seragam & Keselarasan Sejajar:** Susunan baris identik: `[Ikon Aksen di Kiri] ➔ [Teks Label 14px Medium] ➔ [Ruang Fleksibel] ➔ [Badge/Meta di Kanan]`.

## 6. Sensitivitas Maksimal UI Motion Morphing (Default Trigger)
- **Refleks Baku Antarmuka Interaktif:** Setiap kali membuat atau memodifikasi tombol, kartu, modal, accordion, dropdown, atau ikon navigasi, agen wajib secara refleks menerapkan in-place motion morphing fluida 60 FPS:
  - **Transisi Ikon Vektor:** Gunakan `universal-icon-morphing` (arclength resampling + rotational alignment) untuk setiap pergantian state ikon interaktif (menu➔close, play➔pause, sun➔moon, chevron➔cross, status dots).
  - **Ekspansi Kontainer & Kartu:** Gunakan `motion-ui-lifecycle-and-morphing` / GSAP FLIP untuk peleburan kartu ringkas menjadi panel detail (*in-place expansion*) dan accordion tabel elastis.
  - **Haram Pop-Up Kaku:** Dilarang keras menampilkan dialog modal yang tiba-tiba menimpa layar tanpa kontinuitas geometris fisik (*zero spatial context rupture*).
  - **Kurva Gerak Inersia:** Wajib gunakan kurva spring `cubic-bezier(0.16, 1, 0.3, 1)` atau `power3.out` pada 60 FPS GPU-accelerated.

## 7. Hermes Engineering Execution Model Integration (Kanon Rekayasa Sistem)
- **Pekerjaan Selesai Karena Terbukti, Bukan Karena Kode Ditulis:** Pengembangan fitur/perbaikan bug adalah perpindahan dari *known baseline* menuju *verified target state*. Kode selesai diketik belum berarti pekerjaan selesai; selesai hanya jika terbukti pada runtime aktual tanpa regresi.
- **Logika Berhenti & 3 Status Terminal (Stopping Logic):**
  - **`ACCEPTED`:** Seluruh kriteria penerimaan (AC) wajib terpenuhi, pengujian esensial lulus, invarian bisnis terjaga, dan bukti dapat ditelusuri.
  - **`BLOCKED`:** Fakta penentu belum diketahui, dependensi/kredensial belum ada, atau butuh persetujuan Mas Bagas. Berhenti dan tanyakan (Manja Arahan), menolak berspekulasi.
  - **`NOT ACCEPTED`:** Pengujian gagal dan tidak dapat dituntaskan aman dalam lingkup tugas, batas percobaan (3x) atau batas waktu (30 menit) tercapai. Putus loop dan paparkan gap secara jujur.
- **4 Tingkat Klaim Pembuktian:**
  1. *Observed:* File berubah / diff terlihat (belum membuktikan fungsi bekerja).
  2. *Executed:* Perintah test dijalankan, exit code 0 (belum membuktikan seluruh aturan bisnis terpenuhi).
  3. *Verified:* Skenario terisolasi lulus pada runtime uji (belum membuktikan deployment produksi aman).
  4. *Accepted:* Seluruh kriteria penerimaan dalam kontrak disahkan (belum berarti sudah rilis ke server klien).
- **Definisi "Cukup" (Anti-Overengineering):** Kesempurnaan tanpa batas bukan kriteria selesai. Kecukupan tercapai saat persyaratan fungsional inti dan kontrol risiko terpenuhi. Tambahan ide dicatat ke backlog, tidak boleh memperluas tugas aktif secara liar.

## 8. Jebakan Kinerja & Solusi Cepat (Pitfalls)
- **Testing Paralysis:** Mengulang loop screenshot Chromium + `vision_analyze` berkali-kali untuk mengevaluasi diri sendiri membuang waktu dan token; terapkan modifikasi langsung pada kode, verifikasi fungsional esensial sekali, dan serahkan ke Mas Bagas.
- **QC Looping Deadlock:** Mengizinkan unit evaluasi/QC memveto rilis atau memerintahkan siklus revisi berulang secara otomatis memicu macet; perlakukan laporan QC sebagai catatan aditif, bukan pemblokir alur kerja.
- **Sok Mandiri Tanpa Konfirmasi:** Merancang arsitektur spekulatif atau memilih arah desain sepihak tanpa bertanya ke pengguna berujung penolakan total; selalu 'manja arahan' dengan menyodorkan 1-2 opsi terarah saat menghadapi ambiguitas.
- **Static UI Fallback Trap:** Membuat transisi instan atau pop-up kaku tanpa animasi morphing melanggar preferensi visual pengguna; aktifkan in-place morphing 60 FPS secara default pada setiap interaksi komponen.
