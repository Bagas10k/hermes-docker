---
name: erp-client-onboarding-migration
description: "Use when onboarding an ERP client: opening balances."
version: 0.1.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [erp, onboarding, migration, opening-balance, accounting, multi-tenant]
---

# Prosedur Migrasi Klien ERP dan Penyusunan Saldo Awal

Skill ini adalah prosedur baku memindahkan klien baru ke sistem ERP (dari Excel, Accurate, Zahir, atau Odoo) pada arsitektur database-per-tenant. Fokusnya adalah integritas pemindahan saldo buku besar, sub-ledger, dan persediaan hingga serah terima.

**Rujukan wajib dibaca lebih dulu:**
- `erp-engineering-doctrine` — invarian akuntansi inti, 23 invarian mutlak, urutan pengerjaan modul.
- `database-design-migrations` — tata kelola skema dan migrasi aman.
- Vault doktrin: `~/otak-koding/10-Rekayasa-ERP-dan-Akuntansi-Sistem/` — rujukan bergaya kurung-siku-ganda di bawah menunjuk ke berkas catatan di folder ini (nama berkas = isi tanda kurung + `.md`).

---

## 1. When to Use
Gunakan saat:
- Onboarding tenant baru pada basis data terisolasi.
- Mengimpor data master dan saldo awal cut-off dari sistem lama klien.
- Menyetel pemetaan akun (COA) dan menyusun saldo awal pembukuan berpasangan.
- Memvalidasi kebenaran matematis buku besar sebelum akses operasional diserahkan ke klien.

---

## 2. Prerequisites (Syarat Mutlak Sebelum Mulai)
Wajib diperoleh dan divalidasi dari klien sebelum migrasi dieksekusi:
1. **Neraca Saldo (Trial Balance) Resmi:** Per tanggal cut-off, ditandatangani manajemen klien. **Invarian:** Total Debit == Total Kredit. Tanpa neraca saldo seimbang dari sistem lama, proses DILARANG dimulai; memigrasi neraca pincang menjamin kegagalan rekonsiliasi dan sengketa audit.
2. **Bagan Akun (COA) Sumber:** Daftar kode dan nama akun sistem lama beserta hierarkinya.
3. **Daftar Piutang Usaha per Faktur:** Rincian faktur terbuka (nomor faktur, nama pelanggan, tanggal faktur, tanggal jatuh tempo, sisa nominal).
4. **Daftar Hutang Usaha per Faktur:** Rincian faktur pembelian terbuka (nomor faktur, nama pemasok, tanggal faktur, tanggal jatuh tempo, sisa nominal).
5. **Posisi Stok per Gudang per SKU:** Kuantitas fisik per gudang, satuan, harga perolehan unit (FIFO/Average), dan total nilai persediaan.
6. **Daftar Aset Tetap:** Nilai perolehan, akumulasi penyusutan, nilai buku, dan sisa masa manfaat.
7. **Daftar Karyawan & Master Entitas:** Data pelanggan, pemasok, gudang, dan barang yang sudah dinormalisasi.

---

## 3. Procedure (Urutan Eksekusi Migrasi)

### Langkah 1: Tetapkan Tanggal Pisah Batas (Cut-Off Date) & Bekukan Sistem Lama
Tentukan tanggal cut-off (misal: akhir bulan, 31 Desember 23:59). Klien wajib menghentikan seluruh pencatatan transaksi di sistem lama.
*Akibat jika dilanggar:* Muncul mutasi melayang di sistem lama yang tercecer dari migrasi, membuat saldo awal langsung usang saat go-live.

### Langkah 2: Petakan Bagan Akun (COA Mapping)
Petakan setiap akun lama ke kode akun standar ERP (`[[Bagan-Akun-Chart-of-Accounts-Dan-Tipe-Saldo-Normal]]`). Akun lama tanpa padanan harus dibuatkan akun baru yang sah menurut PSAK atau digabungkan atas persetujuan tertulis klien.

```sql
CREATE TABLE pemetaan_akun (
    id_tenant       UUID NOT NULL,
    kode_akun_lama  TEXT NOT NULL,
    nama_akun_lama  TEXT NOT NULL,
    id_akun_baru    BIGINT NOT NULL REFERENCES akun(id),
    CONSTRAINT pk_pemetaan PRIMARY KEY (id_tenant, kode_akun_lama)
);
```
*Akibat jika dilanggar:* Salah klasifikasi tipe akun merusak hierarki pohon buku besar dan menghasilkan laporan keuangan yang salah saji.

### Langkah 3: Impor Entitas Induk Sesuai Ketergantungan Foreign Key
Impor data master sesuai urutan hierarki referensial:
1. Gudang & Lokasi -> 2. Kategori Barang & Satuan -> 3. Barang/SKU -> 4. Mitra (Pelanggan & Pemasok) -> 5. Bagan Akun (COA).
Normalisasi nama mitra dan bersihkan spasi liar untuk mencegah entitas ganda.
*Akibat jika dilanggar:* Foreign key violation saat migrasi data transaksi atau duplikasi identitas yang memecah riwayat pelanggan.

### Langkah 4: Susun Jurnal Saldo Awal Berpasangan Lewat Akun Penyeimbang
Saldo awal dicatat sebagai jurnal umum per tanggal cut-off. Pasangan debit dan kredit diikat sementara menggunakan akun `3-9999 Akun Penyeimbang Saldo Awal` (Opening Balance Equity) (`[[Hukum-Kekekalan-Double-Entry-Bookkeeping]]`). Terapkan penanda idempotensi dengan sidik payload kanonik (`[[Pola-Idempotensi-Transaksi-Keuangan]]`).
*Akibat jika dilanggar:* Jurnal tidak seimbang ditolak basis data trigger, atau eksekusi ulang menghasilkan saldo ganda tanpa terdeteksi.

### Langkah 5: Impor Piutang & Hutang Rinci per Faktur Terbuka
Wajib mencatat per nomor faktur dengan tanggal faktur asli dan tanggal jatuh tempo yang valid, BUKAN angka total gelondongan. Lawan jurnal sub-ledger adalah akun penyeimbang migrasi `3-9999`.
*Akibat jika dilanggar:* Memasukkan angka total gelondongan menghancurkan laporan umur piutang (aging schedule) dan pelunasan parsial mustahil dialokasikan (`[[Termin-Pembayaran-Dan-Alokasi-Pembayaran-Ke-Faktur]]`).

### Langkah 6: Impor Stok Awal Fisik dan Jurnal Nilai Persediaan
Kuantitas fisik dimasukkan ke modul persediaan per gudang per SKU (`[[Kartu-Stok-Dan-Ledger-Persediaan-Auditable]]`). Nilai rupiahnya dijurnal simultan: Debit Persediaan Barang Dagang, Kredit `3-9999 Akun Penyeimbang`.
*Akibat jika dilanggar:* Modul gudang mencatat kuantitas tetapi buku besar persediaan bernilai nol, merusak perhitungan HPP saat barang pertama dijual (`[[Valuasi-Persediaan-FIFO-dan-Moving-Average]]`).

### Langkah 7: Rekonsiliasi & Nolkan Akun Penyeimbang Sementara
Setelah seluruh saldo buku besar, piutang, hutang, aset tetap, dan persediaan selesai diposting:
$$\text{Saldo Akhir } (3\text{-}9999) = \sum \text{Debit} - \sum \text{Kredit} = 0$$
Akun penyeimbang `3-9999` WAJIB bersaldo tepat Rp 0,00.
*Akibat jika dilanggar:* Saldo penyeimbang bukan nol membuktikan ada komponen neraca yang terlewat, tercatat ganda, atau salah hitung.

### Langkah 8: Kunci Periode Saldo Awal sebagai Keras Tutup
Tutup periode akuntansi saldo awal secara permanen dengan status `keras_tutup` (`[[Periode-Akuntansi-Closing-Dan-Locking]]`). Buka periode baru untuk operasional berjalan.
*Akibat jika dilanggar:* Pengguna operasional dapat menyusupkan transaksi mundur ke periode cut-off yang merusak saldo pembukaan.

### Langkah 9: Verifikasi Silang Sebelum Serah Terima
Jalankan pengujian otomatis dan lakukan rekonsiliasi bersama akuntan klien sebelum serah terima kredensial admin.
*Akibat jika dilanggar:* Klien menemukan selisih angka saat sistem sudah aktif beroperasi, memicu perbaikan data darurat di produksi.

---

## 4. Verifikasi Serah Terima (Uji Otomatis Wajib Lolos)

Gunakan fungsi verifikasi berikut untuk menguji integritas data tenant sebelum penandatanganan Berita Acara Serah Terima:

```python
def verifikasi_saldo_awal_tenant(koneksi, id_tenant: str, tanggal_cutoff: str, neraca_target: dict):
    # 1. Total Debit == Total Kredit Jurnal Saldo Awal
    jurnal = koneksi.execute(
        """SELECT COALESCE(SUM(debit), 0) AS deb, COALESCE(SUM(kredit), 0) AS kre
           FROM jurnal_baris jb JOIN jurnal j ON j.id = jb.id_jurnal
           WHERE j.id_tenant = %s AND j.tanggal = %s""",
        (id_tenant, tanggal_cutoff)
    ).fetchone()
    assert jurnal["deb"] == jurnal["kre"], f"Jurnal tidak seimbang: D={jurnal['deb']} K={jurnal['kre']}"

    # 2. Akun Penyeimbang Nol Mutlak
    penyeimbang = koneksi.execute(
        """SELECT COALESCE(SUM(jb.debit - jb.kredit), 0) AS saldo
           FROM jurnal_baris jb JOIN akun a ON a.id = jb.id_akun
           WHERE a.id_tenant = %s AND a.kode = '3-9999'""",
        (id_tenant,)
    ).fetchone()["saldo"]
    assert penyeimbang == 0, f"Akun penyeimbang 3-9999 belum nol: {penyeimbang}"

    # 3. Total Piutang Sub-ledger == Total Piutang Neraca Saldo
    total_piutang = koneksi.execute(
        "SELECT COALESCE(SUM(sisa_tagihan), 0) AS total FROM faktur_penjualan WHERE id_tenant = %s AND status = 'buka'",
        (id_tenant,)
    ).fetchone()["total"]
    assert total_piutang == neraca_target["total_piutang"], "Total piutang sub-ledger berbeda dari neraca saldo"

    # 4. Total Hutang Sub-ledger == Total Hutang Neraca Saldo
    total_hutang = koneksi.execute(
        "SELECT COALESCE(SUM(sisa_tagihan), 0) AS total FROM faktur_pembelian WHERE id_tenant = %s AND status = 'buka'",
        (id_tenant,)
    ).fetchone()["total"]
    assert total_hutang == neraca_target["total_hutang"], "Total hutang sub-ledger berbeda dari neraca saldo"

    # 5. Nilai Fisik Persediaan == Nilai Akun Persediaan Neraca
    nilai_persediaan = koneksi.execute(
        "SELECT COALESCE(SUM(kuantitas * harga_perolehan), 0) AS total FROM kartu_stok WHERE id_tenant = %s",
        (id_tenant,)
    ).fetchone()["total"]
    assert nilai_persediaan == neraca_target["nilai_persediaan"], "Nilai fisik kartu stok tidak cocok dengan neraca"

    # 6. Neraca Seimbang: Aset == Kewajiban + Ekuitas
    neraca = koneksi.execute(
        """SELECT
             SUM(CASE WHEN a.tipe = 'aset' THEN (jb.debit - jb.kredit) ELSE 0 END) AS aset,
             SUM(CASE WHEN a.tipe = 'kewajiban' THEN (jb.kredit - jb.debit) ELSE 0 END) AS kewajiban,
             SUM(CASE WHEN a.tipe = 'ekuitas' THEN (jb.kredit - jb.debit) ELSE 0 END) AS ekuitas
           FROM jurnal_baris jb JOIN akun a ON a.id = jb.id_akun JOIN jurnal j ON j.id = jb.id_jurnal
           WHERE a.id_tenant = %s AND j.tanggal <= %s""",
        (id_tenant, tanggal_cutoff)
    ).fetchone()
    assert neraca["aset"] == (neraca["kewajiban"] + neraca["ekuitas"]), "Persamaan dasar akuntansi tidak seimbang"

    # 7. Sebaran Tanggal Jatuh Tempo Piutang Wajar
    sebaran_jt = koneksi.execute(
        "SELECT COUNT(DISTINCT tanggal_jatuh_tempo) AS jml FROM faktur_penjualan WHERE id_tenant = %s",
        (id_tenant,)
    ).fetchone()["jml"]
    if neraca_target["jumlah_faktur_piutang"] > 1:
        assert sebaran_jt > 1, "Seluruh piutang jatuh tempo pada tanggal yang sama (indikasi tanggal dummy)"

    # 8. Integritas Jumlah SKU
    total_sku = koneksi.execute(
        "SELECT COUNT(*) AS total FROM barang WHERE id_tenant = %s AND aktif = true",
        (id_tenant,)
    ).fetchone()["total"]
    assert total_sku == neraca_target["jumlah_sku"], "Jumlah master SKU tidak cocok dengan sistem lama"
```

---

## 5. Pitfalls (Pola Kegagalan Fatal Lapangan)
1. **Memasukkan Piutang/Hutang sebagai Angka Total Gelondongan:** Menghancurkan laporan umur piutang (aging schedule) dan modul penagihan. Pembayaran faktur pertama oleh klien tidak dapat dialokasikan karena ketiadaan nomor referensi faktur asli.
2. **Kuantitas Persediaan Tanpa Jurnal Nilai Buku:** Mengunggah stok fisik ke modul gudang tetapi lupa membukukan jurnal persediaan ke akun `1-1300`. Akibatnya, neraca saldo timpang dan HPP menjadi nol saat penjualan perdana.
3. **Menggunakan Tanggal Hari Ini untuk Saldo Awal:** Memasukkan saldo awal dengan tanggal eksekusi impor alih-alih tanggal cut-off. Akibatnya, saldo awal mengotori laporan laba rugi dan mutasi operasional periode berjalan.
4. **Mengimpor Master Data Kotor Tanpa Pembersihan:** Mengimpor nama kontak dengan ejaan ganda (misal "CV Maju Jaya" dan "Maju Jaya CV"). Akibatnya, saldo piutang terpecah ke dua entitas berbeda dan plafon kredit jebol.
5. **Eksekusi Impor Berulang Tanpa Idempotensi:** Menjalankan ulang skrip migrasi yang gagal di tengah jalan tanpa transaksi atomik atau tanpa kunci idempotensi (`sidik_payload`). Akibatnya, nilai saldo awal berlipat ganda (*double balance*).
6. **Menganggap 'Impor Berhasil Tanpa Error' sebagai Bukti Kebenaran:** Kode keluar 0 pada skrip impor hanya membuktikan sintaks lolos, bukan membuktikan angka benar. Data bisa masuk dengan nominal nol atau salah petik kolom tanpa memicu pengecualian database.

---

## 6. Verification
Kebenaran migrasi saldo awal BUKAN diukur dari berhasilnya skrip tanpa pesan galat (*zero error exit*). Satu-satunya bukti keabsahan migrasi adalah keterlacakan penuh (*full audit trail*):
- Setiap angka pada neraca pembuka ERP dapat ditelusuri balik ke dokumen sumber neraca saldo klien.
- Seluruh 8 pengujian pada fungsi `verifikasi_saldo_awal_tenant` lolos tanpa toleransi selisih (`assert == 0`).
- Akuntan atau penanggung jawab keuangan klien menandatangani Berita Acara Serah Terima (BAST) setelah memverifikasi laporan neraca saldo perdana yang dicetak langsung dari sistem ERP.

*Skipped: Migrasi riwayat mutasi transaksi detail tahun-tahun sebelumnya; arsipkan sistem lama dalam bentuk read-only untuk kebutuhan audit.*
*Add when: Regulasi industri atau kontrak klien secara eksplisit mewajibkan pelaporan komparatif multi-tahun langsung dari satu database operasional.*
