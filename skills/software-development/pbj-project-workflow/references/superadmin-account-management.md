# Pengelolaan Super Admin PBJ

## Identitas dan kontrak
- Simpan Super Admin di `super_account` melalui `SuperAccount`, bukan di tabel staf `account` dengan jabatan `SUPER_ADMIN`. Pada pembuatan dan perubahan staf, tolak pemberian jabatan tersebut; resolve dari kode jabatan, jangan hardcode ID seed.
- Pada jalur create/edit Super Admin, validasi `super_admin_id` sesi terhadap record nyata di server. Jangan menjadikan `is_super`, `tipe_akun`, atau string `kode_jabatan` kiriman klien sebagai bukti kewenangan. Pertahankan middleware rute yang sudah ada.
- Form tambah memakai `tipe_akun=staf|super_admin`; Super Admin membutuhkan `nama_pemilik`, `username`, `password` dan `password_confirmation`, tanpa profil karyawan otomatis. Pertahankan kontrak staf lama saat field tipe absen.
- Untuk rename, pisahkan hidden `username` target asli dari input `username_baru`. Jangan menautkan keduanya pada state Alpine yang sama. Username staf tetap read-only kecuali ada permintaan berbeda.

## Validasi dan audit
- Validasi username terhadap kedua tabel `account` dan `super_account`; saat rename, pengecualian unik memakai primary key target yang ditemukan server, bukan ID kiriman klien. Gunakan Laravel validation errors per field agar penanganan SPA dapat menampilkan alasan tepat, bukan respons JSON ad-hoc dengan key yang tidak dibaca layout.
- Kata sandi baru Super Admin minimal delapan karakter; penciptaan memerlukan konfirmasi. Editor harus menegakkan minimum sama di server dan HTML. Sandi opsional kosong tidak mengubah hash.
- Transaksikan perubahan Super Admin dan pencatatan audit. `AuditTrailService::catat()` menelan exception dan mengembalikan null: periksa hasilnya dan rollback ketika audit gagal. Whitelist username/nama untuk audit; jangan kirim seluruh model/request, password, hash atau session token.
- Pengecualian redirect manual memakai `withInput($request->except(['password', 'password_confirmation']))`. Penanganan exception manual tidak mendapat pengecualian password otomatis dari Laravel validation handler. Jangan mengirim raw exception/SQL ke pengguna.
- Login Super Admin lama mengisi `nama_pengguna` tetapi belum tentu `username`; resolve pelaku audit dari SuperAccount nyata. Rename diri menyelaraskan `nama_pengguna`, `username`, dan `nama_lengkap` setelah commit sambil mempertahankan ID dan sesi aktif. Rename akun lain tidak mengganti identitas pelaku. Jangan menulis ulang audit historis.

## UI dan verifikasi
- Render field staf dan Super Admin secara kondisional dengan `x-if`, bukan hanya `x-show`, agar field required tersembunyi tidak memblokir submit. Sandi Super Admin tidak memiliki nilai bawaan dan tidak dipulihkan setelah error.
- Pengiriman form normal pada layout PBJ dicegat SPA. Pesan error tampil di `#wadahPopUpGlobal`, bukan selalu banner lokal. Tombol menu tabel existing dikenali dari judul `Pilihan Aksi`, bukan ID tombol rekaan. Tutup popup sukses sebelum mengklik kontrol berikutnya.
- Uji login sesudah rename memakai browser context baru dan form login nyata. Rute login resmi mencakup `/` dan `/login`; buktikan username lama ditolak dengan ketidakhadiran tabel akun dan kehadiran form login, bukan mengasumsikan hanya satu URL.
- Jalankan `PBJ_TEST_SUPERADMIN=1 PBJ_TEST_SUPERADMIN_BROWSER=1 flock -w 180 /tmp/pbj-disposable-tests.lock python3 scripts/test-mysql-isolated.py` untuk MySQL sementara dan browser. Lingkungan Laravel testing melewati CSRF bawaan; jangan melabelinya sebagai uji negatif CSRF atau bukti produksi.
- Pengujian PHP cepat mendukung SQLite in-memory; mode MySQL wajib memeriksa konfigurasi efektif `pbj_test` sebelum mutasi fixture. Pastikan fixture mengikuti NOT NULL schema MySQL, bukan hanya schema SQLite longgar. Setiap tes memakai identitas sintetis dan tidak boleh dijalankan di `pbj_app`/`pbj_db`.
- Bind QC ke hash sumber/test. Laporan async REJECT versi lama tidak membatalkan PASS kandidat baru, tetapi temuan lamanya harus punya disposisi dan uji ulang. Jangan mengklaim race lintas tabel tertutup hanya dari validasi unik dan tes berurutan.
