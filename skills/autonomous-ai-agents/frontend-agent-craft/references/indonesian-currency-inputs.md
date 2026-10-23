# Input Mata Uang Indonesia: Display Terformat, Payload Mentah

## When to Use

Gunakan resep ini ketika form operasional menerima Rupiah dan pengguna perlu mencegah salah digit melalui pemisah ribuan otomatis. Jangan gunakan pada kuantitas, stok, berat, atau nilai satuan nonmoneter.

## Kontrak

Pisahkan dua representasi:

- **Display UI:** `150.000`, `150.000,50`, `54.321,1234`.
- **Payload server:** `150000`, `150000.50`, `54321.1234`.

Jangan mengirim titik ribuan ke validasi `numeric` backend. Jangan menurunkan presisi yang sudah menjadi kontrak database atau service.

## Prosedur

1. **Inventarisasi sebelum edit.** Cari semua `type="number"`, nama field yang mengandung `amount|price|cost|paid|nominal|fee|allowance`, dan formatter lokal yang sudah ada. Buat dua daftar:
   - uang: harga jual/beli, HPP, biaya, nominal, pembayaran;
   - bukan uang: qty, stok, berat, volume, kuantitas fisik.
2. **Pilih satu pemilik format.** Jika suatu field sudah punya display input + hidden raw input sendiri, pertahankan formatter itu atau migrasikan secara eksplisit; jangan menempelkan formatter global kedua karena dua listener akan saling menormalkan nilai.
3. **Ubah hanya field uang.** Gunakan pola atribut deklaratif:
   ```html
   <input type="text" inputmode="decimal"
          name="amount"
          data-currency-input
          data-currency-scale="2">
   ```
   `type="text"` wajib untuk display bertitik; `type="number"` tidak menerima `150.000` sebagai representasi ribuan yang portabel.
4. **Format pada tiga titik lifecycle:**
   - saat DOM siap: nilai `old()`/server raw → display;
   - saat `input`: pertahankan hanya digit, satu koma desimal, dan skala yang diizinkan; sisipkan titik tiap tiga digit;
   - saat `submit` pada capture-phase: buang semua titik ribuan dan ubah koma menjadi titik sebelum validasi browser/framework membaca payload.
5. **Modal create/edit harus memakai setter yang sama.** Jangan mengisi `.value = raw` langsung pada edit; panggil helper `setCurrencyInput(element, raw)` agar `150000.00` langsung terlihat `150.000,00`. Reset field opsional ke string kosong, bukan memaksa nol yang dapat terkirim tanpa sengaja.
6. **Backend tetap benteng terakhir.** Pertahankan `numeric`, batas positif/non-negatif, jumlah desimal, rentang DECIMAL, serta aritmetika decimal/BigDecimal. Formatter hanya mencegah salah input; bukan pengganti validasi.

## Matriks Uji Minimum

| Kasus | Display yang diharapkan | Payload yang diharapkan |
|---|---|---|
| ketik `150000` | `150.000` | `150000` |
| ketik `150000,50` | `150.000,50` | `150000.50` |
| nilai raw edit `54321.1234`, skala 4 | `54.321,1234` | `54321.1234` |
| field opsional kosong | kosong | kosong |
| quantity `12.5000` | tetap mengikuti aturan quantity | tidak disentuh formatter uang |

## Gate Verifikasi

- Tes view memastikan semua field uang memiliki atribut formatter dan field qty tidak memilikinya.
- Uji fungsi formatter dengan kasus display/raw di atas.
- Uji browser nyata: ketik/paste nominal, buka modal edit, lalu submit dan inspeksi payload/form value sesudah normalisasi.
- Jalankan suite transaksi/jurnal penuh untuk memastikan validasi numeric, presisi, dan posting akuntansi tidak berubah.

## Pitfall

- **Jangan sekadar menambahkan `.000` pada blur** — itu mengubah makna angka desimal dan tidak membantu saat pengguna sedang mengetik.
- **Jangan menormalkan semua titik tanpa grammar Indonesia yang jelas** — raw server memakai titik desimal, sedangkan display memakai titik ribuan; tentukan arah konversi berdasarkan lifecycle (raw→display vs display→raw), bukan dengan satu fungsi ambigu.
- **Jangan ubah kuantitas menjadi Rupiah** — qty dapat memiliki empat desimal bermakna dan pengelompokan uang membuat pengguna salah memahami satuan.
- **Jangan melonggarkan validasi backend setelah mengganti `type="number"` menjadi `text`** — keamanan nilai kini bergantung lebih besar pada validasi server.