---
name: sandboxed-agent-adapters
description: "Use when building sandboxed context readers and KV memory."
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [security, sandboxing, path-traversal, kv-store, sqlite-wal, triggers, zero-leak]
---

# Sandboxed Agent Adapters & Resilient KV Memory

Pola baku rekayasa adapter agen modular untuk menangani pemicu eksternal (Cron/Webhook), pembaca basis pengetahuan terisolasi anti-traversal, dan penyimpanan state persisten antar-run tanpa alokasi memori berlebih.

## 1. Sandboxed Vault / Context Reader
- **Ancaman**: Path traversal attack (`../`, symlink spoofing, pembacaan file privat di luar root).
- **Aturan Baku**:
  1. *Component-wise Inspection*: Iterasi setiap komponen path relatif; tolak keras jika memuat komponen `..` sebelum menyentuh filesystem.
  2. *Canonical Root Boundary*: Setelah di-join dengan `vault_root`, resolusikan `canonicalize()` dan pastikan mutlak diawali dengan `root.canonicalize()`.
  3. *Bounded Reading*: Wajib membatasi jumlah baris yang dibaca (default: 500 baris) untuk melindungi stack/heap dari lonjakan OOM saat membaca berkas besar.

## 2. Resilient SQLite KV Memory
- **Karakteristik**: State persisten antar-run yang tetap hidup saat proses di-reload/crash tanpa butuh server Redis tambahan.
- **Aturan Baku**:
  1. *Composite Primary Key*: Gunakan `PRIMARY KEY (namespace, key)` agar multi-agen tidak saling menabrak state.
  2. *Atomic Upsert*: Gunakan `INSERT INTO kv_memory ... ON CONFLICT(namespace, key) DO UPDATE` untuk mencegah race condition.
  3. *Atomic Increment*: Operasi increment metrik/counter wajib dievaluasi dalam satu transaksi SQL.
  4. *Deterministic TTL*: Kolom `expires_at` dievaluasi saat operasi `GET`. Jika terlewati, data otomatis dihapus dan mengembalikan `None`.

## 3. Webhook & Cron Inbound Adapters
- **Webhook Deduplikasi & Verifikasi**:
  - Hashing payload menggunakan SHA-256 untuk idempotensi eksekusi.
  - Verifikasi token autentikasi rahasia sebelum meneruskan event ke pipeline agen.
- **Cron Ticker**:
  - Normalisasi jadwal ke format timestamp terstandar dengan penetapan zona waktu eksplisit (e.g., `Asia/Jakarta`).
