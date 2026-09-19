# JajanDigital: preferensi dan kontrak pengguna

## Landing personal
- Gunakan Poppins, putih terang dengan aksen merah dan kuning yang harmonis. Pengguna menginginkan citra premium seperti web perusahaan besar/Apple: perkenalan personal dengan teks besar, elemen latar 3D perspektif, kedalaman serta cahaya halus.
- Seimbangkan efek 3D dengan permintaan eksplisit animasi smooth, simple, dan bukan AI-slop. Hindari shimmer berulang, badge dekoratif, statistik semu, kartu berlebihan, dan gerakan yang mengganggu bacaan. Sediakan reduced-motion.
- Permintaan terbaru menetapkan DepoBudget `/depobudget/` dan Telemetry `/telemetry/` sebagai dua tautan proyek di beranda. Menampilkan tautan bukan izin membuka akses: pengguna memilih keduanya tetap wajib verifikasi Telegram. Berita sebelumnya diizinkan publik; jangan mengubah izin berita hanya karena navigasi beranda berubah.

## Autentikasi yang diminta, bukan klaim sudah tersedia
- Pengguna meminta `/private/` memakai verifikasi Telegram dan ingat perangkat: perangkat/browser baru perlu verifikasi; perangkat yang sudah dipercaya tidak perlu verifikasi pada setiap kunjungan.
- Verifikasi penerima Telegram yang berwenang sebelum implementasi. Jangan menyimpulkan ID akun yang boleh menyetujui dari display name atau asumsi.
- Gunakan token perangkat aman dengan expiry dan revocation, bukan fingerprint sebagai bukti identitas. Jelaskan bahwa cookie terhapus/browser baru berarti perangkat baru.
- Lindungi server-side routes, APIs, downloads dan WebSocket, serta periksa bypass melalui port upstream. Jangan menyebut UI login atau tautan tersembunyi sebagai pengamanan lengkap.
- Jangan mengklaim verifikasi Telegram/ingat perangkat sudah aktif hanya karena kontraknya sudah disepakati; perlukan implementasi dan uji positif/negatif nyata.
