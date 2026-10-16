# Doktrin ERP & Akuntansi Sistem (folder vault `10-Rekayasa-ERP-dan-Akuntansi-Sistem/`)

Penunjuk ini ditulis terpisah karena `SKILL.md` utama sudah mencapai batas ukuran 100.000 karakter.

## Apa ini

32 catatan doktrin (9.267 baris) tentang rekayasa ERP dan akuntansi sistem, disusun per pilar. Isinya bukan teori akuntansi, melainkan invarian yang tidak boleh dilanggar beserta cara menegakkannya di lapisan basis data.

## Kapan memuat ini

Muat saat merancang atau mengaudit: sistem akuntansi, jurnal & buku besar, valuasi persediaan, siklus penjualan/pembelian, pajak (PPN/PPh), rekonsiliasi bank, kontrol internal, atau multi-tenant database-per-tenant.

## Urutan baca

1. `Daftar-Invarian-Mutlak-Rekayasa-ERP.md` — 23 invarian mutlak, 10 mode kegagalan, checklist audit sebelum rilis.
2. `Peta-Modul-Rekayasa-ERP.md` — tabel "kapan membuka catatan mana", diorganisasi per pilar.
3. Pilar 2 (akuntansi inti) sebelum Pilar 1 (arsitektur): memahami mengapa invarian akuntansi ada lebih penting daripada bagaimana mengisolasi tenant.

## Verifikasi

```bash
python3 ~/otak-koding/10-Rekayasa-ERP-dan-Akuntansi-Sistem/verifikasi_catatan_erp.py
```

Memeriksa frontmatter YAML, tautan wikilink tidak putus, dan setiap catatan punya fungsi uji invarian ber-`assert`. Keluar kode 1 bila ada pelanggaran — bisa langsung dipakai di CI.

## Skill terkait

- `erp-engineering-doctrine` — doktrin dalam bentuk skill (hierarki otoritas, 23 invarian, urutan pengerjaan modul, checklist audit).
- `erp-client-onboarding-migration` — memindahkan klien baru dan menyusun saldo awal.
- `database-design-migrations` — perubahan skema dan migrasi aman.
- `application-auth-security` — otorisasi, peran, tenant, pemisahan tugas.
