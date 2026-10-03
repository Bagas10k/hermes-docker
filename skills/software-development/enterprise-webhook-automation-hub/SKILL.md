---
name: enterprise-webhook-automation-hub
description: Use when building enterprise webhook automation systems. Zero-drop transactional queue, HMAC signature verification, idempotency guard, and exponential backoff retry.
tags: [webhook, automation, enterprise, sqlite-wal, zero-drop, idempotency, retry-backoff, dead-letter-queue]
category: software-development
version: 1.0.0
---

# Enterprise Webhook & Event-Driven Automation Hub

Skill ini menyediakan arsitektur standar industri untuk menangani webhook bisnis dari berbagai pihak ketiga (WhatsApp Cloud API / Baileys, Stripe, Midtrans, Shopify, GitHub, Google Forms, Typeform) tanpa risiko kehilangan data (*zero-drop guarantee*) dan tanpa eksekusi ganda (*idempotency protection*).

---

## 1. Masalah Nyata di Lingkungan Klien Perusahaan

Ketika klien menghubungkan sistem pembayaran atau pesanan (misal: Midtrans atau WhatsApp) ke server:
1. **Double Charging / Double Leads**: Pihak ketiga sering mengirim ulang webhook yang sama jika koneksi lambat. Tanpa *Idempotency Guard*, sistem akan mencatat order 2 kali atau mendebit saldo dobel.
2. **Data Hilang saat Server Restart**: Jika webhook diproses langsung di memori HTTP handler tanpa disimpan ke disk terlebih dahulu, crash server atau reboot saat deployment akan menghapus order pelanggan yang belum diproses (*data loss*).
3. **API Downstream Down**: Jika API CRM (HubSpot/Google Sheets) sedang down atau kena rate limit (HTTP 429/503), webhook akan gagal jika tidak ada *Exponential Backoff + Dead-Letter Queue (DLQ)*.

---

## 2. Arsitektur 4 Lapis (The 4-Pillar Pipeline)

```
[ Pihak Ketiga: WA / Midtrans / Stripe ]
                   │
                   ▼ (HTTP POST)
┌──────────────────────────────────────────────┐
│  Layer 1: Cryptographic Signature Verifier   │ -> Tolak jika HMAC salah (HTTP 401)
└──────────────────────┬───────────────────────┘
                       ▼
┌──────────────────────────────────────────────┐
│  Layer 2: Idempotency Key Guard              │ -> Abaikan jika sudah diproses (HTTP 200)
└──────────────────────┬───────────────────────┘
                       ▼
┌──────────────────────────────────────────────┐
│  Layer 3: SQLite WAL Zero-Drop Inbox Queue   │ -> Tulis ke disk dulu, balas HTTP 200 instan
└──────────────────────┬───────────────────────┘
                       ▼
┌──────────────────────────────────────────────┐
│  Layer 4: Async Dispatcher & Worker Engine   │
│  - Exponential Backoff + Jitter              │ -> Sukses: status COMPLETED
│  - Dead-Letter Queue (DLQ)                   │ -> Gagal > 5x: status DEAD_LETTER
└──────────────────────────────────────────────┘
```

---

## 3. Komponen & CLI Sistem

File inti terpasang di:
- Engine: `~/.hermes/skills/software-development/enterprise-webhook-automation-hub/scripts/webhook_hub.py`
- HTTP Server: `~/.hermes/skills/software-development/enterprise-webhook-automation-hub/scripts/webhook_server.py`
- CLI Global: `/usr/local/bin/webhook-hub`

### Perintah CLI Global:
```bash
# 1. Cek status antrean dan metrik
webhook-hub status

# 2. Jalankan batch pemrosesan event
webhook-hub process --limit 50

# 3. Kembalikan event di Dead-Letter Queue (DLQ) ke antrean aktif
webhook-hub retry-dlq
```

---

## 4. Contoh Integrasi Python Langsung

```python
from webhook_hub import WebhookHub, SignatureVerifier

hub = WebhookHub()

# Daftarkan handler bisnis
def handle_whatsapp_lead(payload):
    customer = payload.get("from")
    text = payload.get("text")
    print(f"Mengirim notifikasi CRM untuk {customer}: {text}")
    return True

hub.register_handler("whatsapp.lead", handle_whatsapp_lead)

# Ingest event masuk (aman dari duplikasi)
ok, msg, event_id = hub.ingest_webhook(
    provider="whatsapp",
    event_type="whatsapp.lead",
    idempotency_key="wamid_AB1234CD",
    payload={"from": "6282185504003", "text": "Butuh otomasi sistem"}
)

# Jalankan worker
stats = hub.process_pending_events(batch_size=10)
```

---

## 5. Verifikasi & Pengujian
Seluruh modul diverifikasi menggunakan test suite deterministik:
```bash
python3 ~/.hermes/skills/software-development/enterprise-webhook-automation-hub/tests/test_webhook_hub.py
```
Hasil: 7/7 test passed (HMAC, Stripe, Midtrans, Idempotency, State Machine, Exponential Backoff, Konkurensi SQLite WAL).
