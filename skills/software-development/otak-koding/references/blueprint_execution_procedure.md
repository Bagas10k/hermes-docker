# Prosedur Penanganan Blueprint Proyek & Eksekusi Otonom

Dokumen ini memuat prosedur standar ketika pengguna memberikan berkas cetak biru (blueprint arsip) dan mandat eksekusi mandiri tanpa jeda.

## 1. Dekompresi & Analisis Struktur Dokumen
- Jika pengguna mengirim berkas arsip (misal `.zip` blueprint PRD/arsitektur), dekompresi ke direktori kerja yang relevan (gunakan `python3 -c "import zipfile..."` jika `unzip` CLI belum tersedia).
- Jadikan struktur berkas dokumen blueprint sebagai patokan absolut untuk:
  1. Skema basis data relasional (`schema.sql` / model entitas).
  2. Batasan ruang lingkup MVP vs rilis lanjutan.
  3. Alur pengguna (*User Flows*) dan spesifikasi kontrol fungsional.

## 2. Disiplin Eksekusi Tanpa Henti ("Looping Sampai Token Habis")
- Jika pengguna secara tegas menginstruksikan untuk langsung eksekusi tanpa banyak tanya:
  - Jangan menanyakan persetujuan untuk hal-hal implementatif teknis yang sudah jelas pilihannya.
  - Terapkan siklus bertahap: rancang skema DB -> bangun backend/API -> integrasikan perutean -> bangun antarmuka web -> uji endpoint -> daftarkan ke portofolio & dokumentasikan ke vault.
  - Ajukan pertanyaan klarifikasi terarah hanya jika ada dependensi eksternal tak terhindarkan (kredensial rahasia, persetujuan risiko destruktif).

## 3. Penanganan Galat Akses & Pencegahan Tool Loop
- **Pencegahan Kueri Berulang (Idempotent Guardrail):** Dilarang mengulang kueri `search_files` atau inspeksi read-only yang identik berturut-turut jika sudah mendapatkan hasil atau tidak ada kemajuan. Jika menemui peringatan atau blokir pengulangan, segera hentikan pola kueri tersebut, gunakan data yang sudah diperoleh, atau beralih ke inspeksi target spesifik (misal membaca berkas secara langsung dengan `read_file` atau uji lewat `terminal` curl).
- **Root Cause Galat Akses:** Bila pengujian endpoint mengembalikan `401 Unauthorized` atau redirect `302`:
  - Segera periksa rantai middleware proteksi gateway/keamanan (misal `privacy-boundary.js`) dan pastikan path/prefix API sudah terdaftar di daftar publik yang diizinkan.
  - Jangan melakukan spekulasi pencarian di direktori node_modules atau modul pihak ketiga.

## 4. Standar Registrasi Portofolio & Build Final
- Setiap penambahan aplikasi web interaktif baru:
  - Daftarkan item ke daftar proyek katalog portofolio (`katalog-portofolio-web/src/main.jsx`).
  - Jalankan build produksi (`npm run build` di direktori katalog portofolio).
  - Sinkronkan aset hasil kompilasi ke direktori publik (`cp -r dist/* dist-public/`).
  - Lakukan verifikasi riil dengan `curl` ke endpoint portofolio dan verifikasi keberadaan nama proyek di aset JavaScript terkompilasi sebelum menyelesaikan pekerjaan.
