## 1. Solusi Akses API & "Peran Developer Tidak Memadai"
Sistem Meta Developer sangat ketat saat memberikan *Access Token*. Kegagalan paling umum saat membuat App dan mengambil token adalah munculnya popup error: *"Peran Developer Tidak Memadai"*.

**Pitfalls & Syarat Mutlak (Wajib):**
- **Status Akun:** Akun Instagram target WAJIB diubah menjadi **Akun Profesional / Kreator**. Akun pribadi (Personal) akan langsung ditolak sistem Meta.
- **Tautan Facebook Page:** Akun Instagram target WAJIB ditautkan secara resmi ke sebuah Halaman Facebook (meski halamannya kosong). Meta Graph API menggunakan *Page Access Token* sebagai pintu masuk ke Instagram.
- **Persetujuan Penguji (Tester Invite):** Setelah mendaftarkan akun sebagai "Penguji" di *App Roles* Meta Developer, statusnya akan menggantung ("Menunggu Persetujuan"). Jangan mencari tombol persetujuan di desktop.
  - **Cara Menyetujui:** Masuk ke aplikasi Instagram (via smartphone) > **Pengaturan dan Privasi** > **Situs Web dan Aplikasi** (atau **Izin Situs Web**) > **Undangan Penguji** > Klik **Setujui**. (Atau langsung buka URL: `https://www.instagram.com/accounts/manage_access/` di browser web yang sedang login Instagram target).

## 2. Generate Long-Lived Access Token
Token awal yang digenerate oleh *Graph API Explorer* hanya bertahan 1-2 jam.
- **Prosedur:** Di *Graph API Explorer*, pilih target *Page Access Token*, beri izin `instagram_basic` dan `instagram_content_publish`. Klik tombol *Info (i)* pada token > *Open in Access Token Tool* > Klik *Extend Access Token* untuk mendapatkan token berumur 60 hari.
