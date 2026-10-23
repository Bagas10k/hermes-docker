# Bootstrap Saldo Awal dan Guard Kas/Bank

Gunakan resep ini hanya untuk **onboarding pertama**. Saldo awal periode berikutnya selalu berasal dari penutupan periode sebelumnya.

## Kontrak minimum

- Tabel draf singleton: `transaction_date`, `cash_amount DECIMAL(19,2)`, `bank_amount DECIMAL(19,2)`, `status draft|posted`, `journal_entry_id`, `posted_at`.
- Draf boleh direvisi dan belum memengaruhi laporan.
- Posting berada dalam satu transaksi dan mengunci baris singleton:
  - Debit `1101 Kas Tunai` bila nilai > 0.
  - Debit `1102 Bank` bila nilai > 0.
  - Kredit `3101 Ekuitas Saldo Awal` sebesar total.
- Tolak total nol saat posting.
- Setelah `posted`, trigger basis data menolak UPDATE/DELETE. Koreksi memakai jurnal penyesuaian.
- Unique key menegakkan satu bootstrap; validasi service bukan pengganti constraint.

## Prosedur implementasi Laravel

1. Tulis tes RED untuk `draft → revise → post → immutable`, keseimbangan debit=kredit, dan rollback.
2. Tambahkan migration baru; jangan menulis ulang migration historis yang mungkin sudah diterapkan.
3. Validasi uang dari string dengan `BigDecimal`, skala maksimal 2, non-negatif, dan batas `DECIMAL(19,2)` sebelum membuka transaksi.
4. Di `post()`, `lockForUpdate()` singleton, tulis header+lines jurnal, lalu ubah status ke `posted` dalam `DB::transaction()` yang sama.
5. Buat satu `AccountBalanceService` yang menghitung saldo aset dari `SUM(debit)-SUM(credit)` memakai nilai string/`BigDecimal`.
6. Untuk setiap transaksi keluar, panggil `assertSufficient(account, amount, excludeJournalId?)` **di dalam transaksi sebelum write pertama**. Saat mengubah dokumen lama, keluarkan jurnal lama dari saldo agar nominal yang sedang diganti tidak dihitung dua kali.
7. Tangkap galat bisnis di controller menjadi HTTP 422 atau `back()->withInput()->withErrors()`, tetapi biarkan transaksi rollback.
8. Buat halaman Jurnal Umum auth-only terpisah dari COA. SSR catatan terbaru untuk fallback; polling bounded hanya saat dokumen terlihat.

## Audit semua jalur keluar

Cari berdasarkan efek akuntansi, bukan menu:

```bash
rg "account_code.*1101|account_code.*1102|creditAccount.*1101|creditAccount.*1102" app tests
rg "recordExpense\(|recordRitase\(|receive\(" app tests
```

Klasifikasikan setiap temuan:

- **Masuk** Kas/Bank: penjualan tunai/transfer, setoran modal — tidak perlu guard keluar.
- **Keluar** Kas/Bank: pengeluaran, ritase, pembelian tunai/bank, refund — wajib guard.
- **Transfer internal** Kas↔Bank: guard hanya sisi sumber dan jurnal tetap seimbang.

## Tes minimum

- Draf dapat direvisi tanpa menciptakan jurnal.
- Posting Kas 10 juta + Bank 5 juta menghasilkan debit 15 juta dan kredit 15 juta.
- Posting kedua, update, dan delete setelah posted ditolak.
- Tanpa saldo pembukaan, semua jalur keluar gagal tertutup tanpa baris parsial.
- Nominal tepat sama dengan saldo boleh; lebih satu sen harus ditolak.
- Pengeluaran, ritase, dan pembelian tunai/bank rollback lengkap saat saldo kurang.
- Feed initial memuat terbaru; `after_id` hanya mengembalikan ID lebih besar dan dibatasi.
- Guest tidak dapat membuka halaman maupun endpoint feed.
- Jalankan suite terfokus, lalu suite penuh; perbarui fixture lama dengan helper pembukaan yang **dipanggil eksplisit**.

## Batas pembuktian

SQLite `:memory:` membuktikan kontrak fungsional dan rollback, tetapi tidak membuktikan perilaku lock MySQL/PostgreSQL. Sebelum rilis stateful, lakukan uji dua request konkuren pada engine target dan pastikan hanya satu debit yang lolos saat saldo cukup untuk satu transaksi saja.
