## 1. Solusi Akses API & "Peran Developer Tidak Memadai"
Sistem Meta Developer sangat ketat saat memberikan *Access Token*. Kegagalan paling umum saat membuat App dan mengambil token adalah munculnya popup error: *"Peran Developer Tidak Memadai"*.

**Pitfalls & Syarat Mutlak (Wajib):**
- **Status Akun:** Akun Instagram target WAJIB diubah menjadi **Akun Profesional / Kreator**. Akun pribadi (Personal) akan langsung ditolak sistem Meta.
- **Pilih jalur login aktual:** Facebook Login memerlukan akun profesional yang terhubung ke Facebook Page dan token yang sesuai. Instagram Login tidak mewajibkan Facebook Page. Jangan meminta pengguna menghubungkan ulang atau membuat aplikasi baru hanya karena izin komentar belum diperiksa. Rujukan resmi: https://developers.facebook.com/docs/instagram-platform/overview
- **Persetujuan Penguji (Tester Invite):** Setelah mendaftarkan akun sebagai "Penguji" di *App Roles* Meta Developer, statusnya akan menggantung ("Menunggu Persetujuan"). Jangan mencari tombol persetujuan di desktop.
  - **Cara Menyetujui:** Masuk ke aplikasi Instagram (via smartphone) > **Pengaturan dan Privasi** > **Situs Web dan Aplikasi** (atau **Izin Situs Web**) > **Undangan Penguji** > Klik **Setujui**. (Atau langsung buka URL: `https://www.instagram.com/accounts/manage_access/` di browser web yang sedang login Instagram target).

## 2. Generate Long-Lived Access Token
Token awal yang digenerate oleh *Graph API Explorer* hanya bertahan 1-2 jam.
- **Publikasi dan komentar terpisah:** Pada Facebook Login, `instagram_content_publish` mengizinkan publikasi, sedangkan balas komentar memerlukan `instagram_manage_comments` beserta izin dasar dan Page yang relevan. Pada Instagram Login, gunakan `instagram_business_basic` dan `instagram_business_manage_comments` untuk komentar. Periksa jalur autentikasi, scope, dan masa berlaku token aktual; jangan menganggap semua token atau hasil perpanjangan selalu berumur 60 hari.
- **Balas komentar:** `POST /<IG_COMMENT_ID>/replies` dengan `message`. Adanya API resmi bukan bukti auto-reply sudah diimplementasikan: logika penerimaan komentar, penyusunan jawaban, deduplikasi, dan pengiriman harus tersedia. Pertanyaan tentang kemampuan bukan izin untuk mengirim balasan publik. Rujukan resmi: https://developers.facebook.com/docs/instagram-platform/comment-moderation
