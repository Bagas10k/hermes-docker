---
name: erp-engineering-doctrine
description: "Use when building or auditing ERP/accounting systems."
---

# Doktrin Rekayasa ERP & Akuntansi Sistem

Membangun ERP bukan membangun aplikasi CRUD yang kebetulan menghitung uang. Perbedaan mendasar: **galat di ERP menjadi dokumen audit**. Setiap keputusan teknis dinilai dari satu pertanyaan: *jika ini rusak, apakah angka di laporan keuangan salah tanpa ada yang tahu?*

Repositori lengkap: `~/otak-koding/10-Rekayasa-ERP-dan-Akuntansi-Sistem/`

---

## 1. Hierarki Otoritas (Baca Sebelum Mengoding)

Ketika ada konflik antar aturan, urutan otoritasnya:

1. **Hukum akuntansi & standar (PSAK/IFRS)** — tidak dapat dinegosiasikan oleh preferensi teknis.
2. **Invarian basis data** (constraint, trigger, index unik) — tidak dapat dilewati oleh jalur kode apa pun.
3. **Invarian domain** (aturan di lapisan entitas/use case).
4. **Konvensi kode & gaya** — paling rendah, dapat diubah kapan saja.

**Konsekuensi praktis:** setiap aturan bisnis yang menyangkut uang atau saldo wajib punya penegakan di lapisan 2. Aturan yang hanya hidup di lapisan 3 adalah utang yang akan gagal audit.

---

## 2. Invarian Mutlak (Haram Dilanggar)

### 2.1 Uang & Angka
- **I-1:** Nominal uang wajib `NUMERIC(19,2)` / `DECIMAL(19,2)`. `FLOAT`/`DOUBLE` adalah pelanggaran berat — pembulatan titik mengambang terakumulasi menjadi selisih nyata pada jutaan baris.
- **I-2:** Simpan `debit` dan `kredit` sebagai dua kolom terpisah dengan `CHECK (debit >= 0 AND kredit >= 0)` dan `CHECK ((debit > 0 AND kredit = 0) OR (kredit > 0 AND debit = 0))`. Jangan pernah menyimpan "nominal bertanda".
- **I-3:** Pembulatan pajak/potongan ditetapkan **satu kali di satu tempat** dan dicatat sebagai baris jurnal eksplisit. Selisih pembulatan bukan noise — ia akun tersendiri.

### 2.2 Jurnal & Saldo
- **I-4:** Jurnal yang sudah diposting bersifat **imutabel**. Koreksi = jurnal pembalik (`jenis='pembalik'`, `id_jurnal_asal` merujuk jurnal asal, debit dan kredit ditukar), bukan `UPDATE`/`DELETE`.
- **I-5:** Jurnal pembalik tidak dapat dibalik kembali. Cegah dengan `UNIQUE` pada `id_jurnal_asal`.
- **I-6:** Saldo akun adalah **turunan** (`SUM(debit) - SUM(kredit)`), bukan nilai tersimpan yang diperbarui terpisah. Dua sumber kebenaran pasti akan berbeda.
- **I-7:** Keseimbangan ditegakkan dengan `CONSTRAINT TRIGGER ... DEFERRABLE INITIALLY DEFERRED` (diperiksa saat commit), bukan `CHECK` per baris.
- **I-8:** Akun kepala (`adalah_posting = FALSE`) tidak dapat menerima baris jurnal. Ditegakkan lewat trigger, bukan validasi form.

### 2.3 Periode & Waktu
- **I-9:** Posting diperiksa terhadap **tanggal jurnal**, bukan tanggal hari ini. Pengguna dapat memasukkan tanggal mundur.
- **I-10:** Periode `keras_tutup` menolak seluruh posting. Koreksi jatuh di periode berjalan.
- **I-11:** Hanya satu periode `terbuka` per tenant — tegakkan dengan `CREATE UNIQUE INDEX ... WHERE status = 'terbuka'`.
- **I-12:** Saldo awal periode **tidak pernah** diinput manual. Ia turunan dari jurnal periode sebelumnya.

### 2.4 Persediaan & HPP
- **I-13:** Metode valuasi (FIFO / Moving Average) dikunci saat transaksi terjadi. HPP tercatat pada detik mutasi keluar, bukan dihitung ulang saat laporan.
- **I-14:** Stok negatif dicegah `CHECK (saldo_tersedia >= 0)` di basis data. Bila kebijakan bisnis mengizinkan negatif sementara, gantikan dengan **akun penampung** + laporan pengecualian harian — jangan hapus kendala tanpa pengganti.
- **I-15:** Mutasi stok wajib dua sisi: `kartu_stok` (kuantitas) dan jurnal (nilai). Tidak ada mutasi kuantitas tanpa jurnal nilai.

### 2.5 Multi-Tenant
- **I-16:** Identitas tenant untuk otorisasi hanya dari sumber yang tidak dapat dikendalikan klien: subdomain yang dipetakan ke tabel internal, atau klaim token bertanda tangan. Header `X-Tenant-Id` hanya petunjuk, wajib diverifikasi ulang.
- **I-17:** Setiap unit eksekusi (request, job antrean, cron, migrasi) memiliki tepat satu tenant. Job tanpa `tenant_id` di payload wajib **gagal**, bukan jalan dengan tenant default.
- **I-18:** Seluruh kunci cache, nama berkas, nama antrean berprefiks `tenant:<id>:`. Cache tanpa prefiks adalah penyebab kebocoran nomor satu.
- **I-19:** Konteks tenant yang tidak ada harus **melempar galat**, bukan mengembalikan `None`. Gagal-tertutup mengubah kebocoran senyap menjadi kegagalan berisik.

### 2.6 Idempotensi & Konsistensi
- **I-20:** Webhook eksternal wajib idempoten lewat tabel penanda dengan `UNIQUE(id_tenant, jenis, sidik_payload)`.
- **I-21:** Penanda dan efek berada dalam **satu transaksi**. Transaksi terpisah menciptakan jendela kehilangan uang yang tidak terdeteksi.
- **I-22:** Sidik payload dihitung dari **JSON terkanonikalisasi** (`sort_keys=True`, separator tanpa spasi), bukan body mentah.
- **I-23:** Penulisan domain + niat kirim pesan berada dalam satu transaksi (`outbox`). Jangan pernah kirim ke broker di dalam blok transaksi basis data.

---

## 3. Pola Kegagalan yang Berulang

| Kode | Mode Kegagalan | Gejala | Perbaikan |
|---|---|---|---|
| F-1 | Baca-lalu-tulis untuk mutasi | Saldo hilang saat konkuren | Tulis mutasi sebagai operasi **relatif** (`SET x = x - 1`), bukan nilai absolut |
| F-2 | Stok tidak negatif hanya di kode | Stok minus setelah skrip perbaikan data | `CHECK` di basis data |
| F-3 | Cache tanpa prefiks tenant | Laporan tenant A muncul di tenant B | Prefiks di lapisan abstraksi cache |
| F-4 | Migrasi skema tidak fan-out | Satu tenant skema lama, galat muncul berbulan kemudian | Verifikasi hash skema seluruh tenant di CI |
| F-5 | Konteks tenant di variabel global | Bocor antar-tugas asinkron | `contextvars`, plus uji paralel |
| F-6 | Job antrean tanpa konteks tenant | Job menulis ke tenant default | Skema payload tervalidasi, gagal-tertutup |
| F-7 | Deadlock karena urutan kunci tak tetap | Kasir melihat galat mentah | Urutan kunci global + retry idempoten |
| F-8 | `SERIALIZABLE` tanpa retry `40001` | Tim menurunkan isolasi kembali | Retry terbatas dengan backoff |
| F-9 | Outbox menumpuk tanpa alarm | Kehilangan data perlahan | Peringatan pada `percobaan > N` |
| F-10 | Saldo disimpan terpisah dari jurnal | Laporan tidak rekonsiliasi | Jadikan saldo turunan murni |

---

## 4. Urutan Pengerjaan Modul ERP

Jangan membangun modul sesuai urutan yang diminta klien. Bangun sesuai urutan ketergantungan:

1. **`buku_besar`** — akun, jurnal, periode. Semua modul lain bergantung padanya. Bangun dan kunci invariannya lebih dulu.
2. **`persediaan`** — barang, gudang, kartu stok, saldo. Bergantung pada buku besar untuk nilai.
3. **`pembelian`** — pesanan beli, penerimaan, faktur beli (three-way matching).
4. **`penjualan`** — pesanan jual, pengiriman, faktur jual.
5. **`piutang` / `hutang`** — turunan dari faktur dan pembayaran.
6. **`kas_bank`** — rekonsiliasi dan mutasi bank.
7. **Laporan** — selalu turunan dari jurnal, tidak pernah tabel laporan tersendiri.

**Aturan:** modul `persediaan` tidak boleh menulis jurnal sendiri. Ia memanggil `buku_besar.catat_jurnal(...)`. Format jurnal berubah di satu tempat saja.

---

## 5. Checklist Audit Sebelum Rilis

Jalankan sebelum setiap rilis yang menyentuh jalur uang:

- [ ] Seluruh kolom nominal bertipe `NUMERIC`/`DECIMAL` — grep untuk `FLOAT`, `DOUBLE`, `REAL`.
- [ ] Setiap mutasi saldo/stok ditulis sebagai operasi relatif, bukan hasil hitung aplikasi.
- [ ] Uji paralel: N penulisan bersamaan menghasilkan saldo tepat.
- [ ] Uji jurnal tidak seimbang: harus **ditolak** basis data, bukan hanya divalidasi aplikasi.
- [ ] Uji webhook ganda: dikirim 5x, jurnal hanya bertambah 1x.
- [ ] Uji periode tertutup: posting ke periode `keras_tutup` gagal.
- [ ] Uji konteks tenant paralel: tidak ada kebocoran antar-tugas.
- [ ] Uji batas modul: tidak ada impor lintas modul di luar `antarmuka`.
- [ ] Uji pohon akun: tidak ada siklus, tipe anak = tipe induk.
- [ ] Uji hash skema seluruh tenant identik.

---

## 6. Verifikasi Doktrin (Wajib di CI)

Doktrin yang tidak diverifikasi akan lapuk dalam hitungan bulan. Skrip `scripts/verifikasi_catatan_erp.py` memeriksa setiap catatan: frontmatter YAML lengkap, tautan wikilink tidak putus, dan setiap catatan punya minimal satu fungsi uji invarian ber-`assert`. Tautan putus menandakan catatan baru ditulis tanpa memperbarui indeks; catatan tanpa uji menandakan klaim tanpa bukti.

```bash
python3 scripts/verifikasi_catatan_erp.py ~/otak-koding/10-Rekayasa-ERP-dan-Akuntansi-Sistem/
```

Jalankan setiap kali menambah atau mengubah catatan doktrin. Keluar kode 1 bila ada pelanggaran.

---

## 7. Cara Memakai Skill Ini

1. **Sebelum mengoding modul baru:** baca bagian 2 yang relevan dan bagian 4 untuk urutan.
2. **Saat menulis kode:** setiap kali menulis `UPDATE` pada kolom saldo, kuantitas, atau status dokumen — berhenti, tanya: *invarian mana yang sedang saya sentuh, dan apakah ia ditegakkan di basis data?*
3. **Saat mengaudit sistem yang sudah ada:** jalankan checklist bagian 5 sebagai daftar temuan, dan hitung berapa banyak yang gagal.
4. **Saat menjawab pertanyaan desain:** jawab dengan konsekuensi kegagalan, bukan dengan preferensi.

---

## 8. Referensi Inti

- Horngren, C. et al. *Introduction to Financial Accounting* — siklus akuntansi, jurnal, penutup.
- Ikatan Akuntan Indonesia — *PSAK* (koreksi kesalahan, penyajian laporan).
- Kleppmann, M. *Designing Data-Intensive Applications* — isolasi, konsistensi, partisi.
- Berenson, H. et al. *A Critique of ANSI SQL Isolation Levels* (SIGMOD 1995).
- Ports, D. & Grittner, K. *Serializable Snapshot Isolation in PostgreSQL* (VLDB 2012).
- Helland, P. *Idempotence Is Not a Medical Condition* (ACM Queue, 2012).
- Evans, E. *Domain-Driven Design* — batas konteks dan bahasa bersama.
- Chong, F. & Carraro, G. *Architecture Strategies for Catching the Long Tail* (MSDN, 2006) — taksonomi multi-tenancy.
