# Kontrak bisnis operasional Kasir V2

Gunakan saat merancang atau melanjutkan implementasi operasional kasir/admin. Ini keputusan pengguna dan pelajaran verifikasi, bukan bukti fitur selesai. Instruksi terbaru dan tracker aktual mengalahkan status historis.

## Sumber dan batas kerja

- Dokumen kandidat: `/home/ubuntu/kasir-bangunan-rebuild/docs/rancangan-operasional-v2.md`, `docs/v2-contract.md`, `docs/build_tracker_v2.json`, `docs/v2-qc-disposition.md`. Baca status aktual sebelum melanjutkan.
- Source aktif pernah berada di `/home/ubuntu/kasir-bangunan-app` dengan bind mount langsung ke produksi. Verifikasi ulang mount; worktree kandidat tidak membuktikan rilis aktif.
- Pengguna meminta kode domain/layar fresh, rencana dan kontrak `.md`, PDF rancangan sebelum implementasi, serta progres konkret. Fresh bukan izin menghapus akun/transaksi atau membuat dua sumber kebenaran stok/jurnal.
- Penggantian aplikasi aktif setelah backup telah dipilih. Ini bukan izin reset database atau promosi kode parsial. Tetap siapkan rekonsiliasi, restore rehearsal, uji target engine/browser, dan rollback.
- Untuk revisi besar, pengguna meminta 3–7 pertanyaan penting di awal sekaligus, lalu eksekusi dalam lingkup yang disetujui tanpa konfirmasi rutin. Ini pengecualian dari kebiasaan klarifikasi biasa satu-per-satu; batas risiko/sprint tetap berlaku.

## Keputusan bisnis yang dikunci

- Peran operasional kasir/admin; admin memegang master. Izin wajib server-side, bukan hanya tombol tersembunyi.
- Kasir mengajukan pembayaran utang supplier; admin mengesahkan. Usulan belum mengurangi saldo atau membuat jurnal. Pisahkan persetujuan dari pembayaran aktual bila uang belum keluar.
- Penggajian ditunda; master karyawan/staf tetap termasuk. Jangan menambah otomatisasi absensi/lembur atau mengiklankan payroll selesai.
- Ongkir yang ditagihkan pelanggan dan biaya sopir dicatat terpisah, bukan hanya selisih bersih.
- Klien mengisi data sendiri. Excel hanya master produk, pelanggan, supplier, karyawan/staf, dan mobil. Saldo awal lewat formulir terpisah. Riwayat penjualan lama tidak termasuk impor master; database aktif tidak dikosongkan.
- Modal awal kasir = uang kembalian per hari/shift, bukan revenue atau saldo pembukaan akuntansi. Sumber boleh admin atau sisa shift sebelumnya; nominal/sumber tercatat. Carry bukan pendapatan baru. Saldo bank tidak dicampur uang fisik laci.
- Kasir menghitung uang fisik saat tutup shift; admin memeriksa jika selisih. Selisih tidak otomatis menjadi biaya/pendapatan. Alur review admin harus menjaga expected/count/difference historis dan jejak keputusan. Jangan menganggap blokir semua shift berikutnya sebagai keputusan pengguna.
- Utang supplier dan piutang pelanggan boleh dicicil, dengan alokasi/riwayat terhadap tagihan asal. Cicilan tunai pelanggan disahkan kasir; transfer menunggu verifikasi admin. Pending belum menambah bank atau mengurangi piutang.
- Transfer penjualan baru boleh belum lunas meski barang diserahkan. Nota/surat jalan harus menampilkan belum lunas. Verifikasi transfer tidak mengulang revenue, HPP, atau stok.
- Kasir/admin boleh diskon tanpa plafon jabatan/persetujuan tambahan. Validasi negatif/over-discount tetap wajib. Diskon per barang dahulu, lalu diskon pada subtotal barang tersisa; keduanya boleh digabung. Ongkir tidak ikut diskon.
- Surat jalan wajib untuk pengiriman; ambil sendiri cukup nota. Dokumen pengiriman tidak memposting stok/penjualan kedua. Ritase/keuangan sopir perlu keterlacakan ke pengiriman.
- Tema tetap hijau-putih yang ringkas dan jelas untuk kasir. Struktur/fungsi dahulu; arah visual sudah dipilih, tidak perlu ditanya ulang tanpa kebutuhan baru.

## Bedakan keputusan pengguna dari desain turunan

- Nominal/persen, alokasi pembayaran lintas faktur, metode DP, rincian resolusi selisih, refund/pembalikan, dan mapping legacy harus eksplisit dalam kontrak. Pilihan mandiri yang diizinkan dilabel keputusan implementasi, bukan diklaim sebagai persetujuan pengguna.
- DP kredit tidak boleh diasumsikan tunai secara diam-diam bila transfer mungkin dimaksud. Metode DP eksplisit; transfer pending tidak masuk kas laci/bank.
- Backup gzip valid bukan bukti restore. SQLite bukan bukti precision/locking MariaDB. Render Blade bukan bukti transaksi browser.

## Pelajaran verifikasi yang dapat digunakan ulang

- Periksa API library terpasang: kandidat Brick Math memakai `RoundingMode::HalfUp`, bukan `HALF_UP`; PHP lint belum tentu mendeteksi konstanta salah sebelum dieksekusi.
- Catch `RuntimeException` yang luas dapat mengubah `HttpException` 403 menjadi 422; teruskan exception otorisasi HTTP terlebih dahulu.
- HPP dipertahankan empat desimal sampai snapshot item. Respons uang/replay tetap dua desimal walaupun SQLite membuang nol belakang.
- Idempotensi mencakup pemilik dan hash payload, bukan hanya unique key. Sebelum menerima temuan race, telusuri lock yang diambil sebelum pengecekan key; uji dua koneksi target engine untuk klaim konkurensi.
- Ikat review ke hash source dan bukti nyata. Pisahkan bug terkonfirmasi, kemampuan belum tersedia, dan hipotesis/NOT RUN. QC menambah catatan, bukan memicu loop eksekusi tanpa batas.
- Perubahan tracker/dokumen saja cukup divalidasi JSON/link/diff yang relevan; jangan mengulang npm install/build/suite hijau tanpa perubahan runtime atau kebutuhan bukti baru. Jika verifier diwajibkan, laporkan resepnya: Vite readiness HTTP404 bukan Laravel acceptance. Hindari bootstrap yang meng-upgrade dependency tanpa lockfile.
- Simpan output/exit status asli; gunakan pipefail untuk pipeline. Jangan menyatakan tes lulus dari exit perintah terakhir setelah perintah tes gagal.
