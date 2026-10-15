---
name: erpnext-sandbox
description: Use when running the self-hosted ERPNext sandbox.
version: 1.0.0
author: Bagas Cihuy
license: MIT
metadata:
  hermes:
    tags: [erpnext, frappe, docker, cloudflare-tunnel, erp, pbj-reference]
    related_skills: [cloudflare-tunnel-sentinel, pbj-project-workflow, private-saas-architecture]
---

# ERPNext Sandbox Skill

ERPNext (Frappe Framework, Python/Node/MariaDB/Redis) berjalan sebagai stack Docker terisolasi di VPS. Dipakai untuk meninjau modul ERP dan sebagai referensi skema untuk `website-pbj`.

## When to Use

- Menyalakan/mematikan sandbox ERPNext.
- Meninjau modul ERP (Accounts, Buying, Selling, Stock, CRM, Manufacturing).
- Menarik pola relasi tabel & flow procurement/stock untuk referensi Laravel `website-pbj`.

## Lokasi & Port

- Compose: `/home/ubuntu/erpnext-sandbox/docker-compose.yml`
- Frontend bind: `127.0.0.1:8088` (JANGAN 0.0.0.0)
- Path reverse-proxy: `/erpnext` -> `http://127.0.0.1:8088` (di `penelitian-pola-pikir-ai/server.js`)
- Tunnel cepat: PM2 app `erpnext-tunnel` (`~/.local/bin/run-erpnext-quicktunnel.sh`)

## Quick Reference

Nyalakan stack lengkap:
```bash
cd /home/ubuntu/erpnext-sandbox && docker compose up -d db redis-cache redis-queue && \
  docker compose run --rm configurator && docker compose run --rm create-site && \
  docker compose up -d backend websocket frontend
```

Matikan (bebaskan RAM ~500MB):
```bash
cd /home/ubuntu/erpnext-sandbox && docker compose down
```

Ambil URL tunnel:
```bash
pm2 logs erpnext-tunnel --lines 60 --nostream | grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" | tail -1
```

## Kredensial

- User: `Administrator`
- Password: `admin`

Sengaja dikembalikan ke default: sandbox ini **demo**, isinya data contoh. User meminta akses tanpa gesekan.

## Akses Publik (keputusan sadar)

Sandbox ini **terbuka tanpa autentikasi edge**. Basic Auth nginx pernah dipasang lalu dilepas atas permintaan user, karena pop-up browser menyulitkan dan ini hanya proyek contoh.

Konsekuensinya: siapa pun yang tahu URL quick tunnel bisa login sebagai Administrator. Isi sandbox hanya data contoh, jadi risikonya terbatas pada sandbox itu sendiri - **jangan pernah masukkan data nyata PBJ ke sini** selama akses terbuka.

Kalau perlu dikunci lagi, dua langkah:

1. Tulis `auth_basic` + `auth_basic_user_file` ke `nginx/security_headers.conf` (file itu sudah di-include template resmi).
2. Tambah `proxy_set_header Authorization "";` di `location @webserver` **dan** `location /socket.io` pada `nginx/frappe.conf.template` - tanpa ini Frappe membaca header Basic sebagai API token dan menjawab 401.

Buat hash dengan `openssl passwd -apr1` (format `$apr1$` saja yang diterima).

## Urutan Inisialisasi (WAJIB berurutan)

1. `docker compose up -d db redis-cache redis-queue` - tunggu `db-1` **healthy**.
2. `docker compose run --rm configurator` - menulis `sites/common_site_config.json`.
3. `docker compose run --rm create-site` - migrasi 830 DocType, ~5 menit. Jalankan di background.
4. `docker compose up -d backend websocket frontend` - baru UI hidup.

Melewati langkah 2 atau 3 membuat frontend mengembalikan 502.

## Pitfalls

- **`frappe.conf` ditulis ulang oleh `nginx-entrypoint.sh` saat start.** Mount file itu sebagai `:ro` membuat container crash-loop (`Read-only file system`). Sisipkan konfigurasi lewat `security_headers.conf` (sudah di-include template) atau patch `frappe.conf.template`.
- **Basic Auth bocor ke Frappe sebagai header `Authorization`.** Frappe membacanya sebagai API token, lalu menjawab 401 `WWW-Authenticate: Bearer`. Wajib `proxy_set_header Authorization "";` di `location @webserver` **dan** `location /socket.io` - nginx tidak mewarisi `proxy_set_header` level server begitu location mendefinisikan miliknya sendiri.
- **Hash htpasswd harus `$apr1$`** dari `openssl passwd -apr1`. Format `$6$` dan `{PLAIN}` ditolak tanpa pesan jelas (cuma 401).
- **create-site harus selesai sebelum frontend**: tanpa itu `/login` 502. Cek progres dengan `docker logs <create-site-container> | tr '\r' '\n' | grep -oE "\[=* *\] [0-9]+%" | tail -1`.
- **`docker compose up -d <svc>` sering "Created" bukan "Started".** Setelah force-recreate, cek `docker ps`; kalau status `Created`, jalankan `docker start <nama>`.
- **`docker compose up -d <svc>` bisa diblokir terminal tool** yang mengira itu server long-lived. Jalankan dengan `background=true`.
- **Asset ERPNext memakai path absolut `/assets/*`**, dan `/socket.io` juga di root. Karena itu ERPNext **tidak bisa** dipasang sebagai subpath (`/erpnext`) di domain yang sudah memakai `/assets` dan `/socket.io` - pakai subdomain terpisah.
- **privacy-boundary.js memblokir route baru dengan 401.** Daftarkan prefix di `src/privacy-boundary.js` (`isPublic`) sebelum mengakses lewat proxy.
- **Quick tunnel URL berubah setiap restart** `erpnext-tunnel`. Ambil ulang dari `pm2 logs`, jangan simpan.
- **Redis image harus `6.2-alpine`** (sesuai compose resmi). Versi 7 mengubah perilaku `redis_socketio`.

## Setup Company (wizard)

Instalasi mentah tidak punya Company, sehingga PO/Invoice tidak bisa dibuat. Jalankan wizard sekali:

```bash
curl -s -b cookies.txt -X POST "$URL/api/method/frappe.desk.page.setup_wizard.setup_wizard.setup_complete" \
  -H 'Content-Type: application/json' \
  -d '{"args":{"currency":"IDR","company_name":"PT PBJ Nusantara","company_abbr":"PBJN","country":"Indonesia","timezone":"Asia/Jakarta","language":"English","chart_of_accounts":"Standard","fy_start_date":"2026-01-01","fy_end_date":"2026-12-31","domain":"Distribution","setup_type":"Standard"}}'
```

Menghasilkan otomatis: 1 Company, 1 Fiscal Year, 96 Account (CoA), 5 Warehouse, 6 Item Group, 2 Cost Center.

**Jangan** buat Company lewat `frappe.client.insert` langsung - gagal dengan `LinkValidationError: Could not find Warehouse Type: Transit` karena wizard yang menyiapkan master tersebut.

## Submit Dokumen via API

`frappe.client.submit` **butuh dokumen lengkap**, bukan hanya `{doctype, name}`. Ambil dulu, baru submit:

```bash
curl -s -b cookies.txt "$URL/api/resource/Purchase%20Order/PO-NAME" > d.json
python3 -c "import json;print(json.dumps({'doc':json.load(open('d.json'))['data']}))" > dsub.json
curl -s -b cookies.txt -X POST "$URL/api/method/frappe.client.submit" \
  -H 'Content-Type: application/json' --data-binary @dsub.json
```

Mapper dokumen: `frappe.model.mapper.make_mapped_doc` dengan `method` + `source_name`:

| Dari | Ke | method |
|---|---|---|
| Purchase Order | Purchase Receipt | `erpnext.buying.doctype.purchase_order.purchase_order.make_purchase_receipt` |
| Purchase Order | Purchase Invoice | `erpnext.buying.doctype.purchase_order.purchase_order.make_purchase_invoice` |

Hasil mapper mengembalikan doc di **`message` langsung** (bukan `message.docs[0]`).

## Verification

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8088/login   # 200
curl -s -X POST https://<tunnel-url>/api/method/login \
  -H 'Content-Type: application/json' \
  -d '{"usr":"Administrator","pwd":"admin"}'                        # {"message":"Logged In"}
curl -s -b cookies.txt https://<tunnel-url>/api/method/frappe.client.get_count?doctype=DocType  # 830
```

## Referensi untuk website-pbj

Yang layak ditarik ke Laravel PBJ (bukan kodenya, tapi modelnya):

| Area ERPNext | Dokumen kunci | Nilai untuk PBJ |
|---|---|---|
| Buying | Purchase Order -> Purchase Receipt -> Purchase Invoice | 3-way matching pengadaan |
| Stock | Stock Entry, Stock Ledger Entry, Warehouse | ledger stok append-only + bin qty |
| Selling | Sales Order -> Delivery Note -> Sales Invoice | alur jual -> kirim -> tagih |
| Accounts | Journal Entry, GL Entry, Cost Center | double-entry + dimensi akuntansi |
| Approval | Workflow, Workflow Action | approval matrix berjenjang |

Kunci desain ERPNext yang penting: setiap transaksi dokumen memakai pola **submit/cancel** (draft -> submitted -> cancelled) dengan GL/Stock ledger entry hanya tertulis saat submit. Ini yang memberi audit trail bersih dan idempotensi - pola yang sama sebaiknya dipakai di modul transaksional PBJ.
