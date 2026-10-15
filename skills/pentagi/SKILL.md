---
name: pentagi
description: Menjalankan dan mengelola PentAGI (Autonomous AI Agent Penetration Testing) on-demand via Docker untuk audit keamanan server, scanning celah web/API, dan validasi postur pertahanan. Hemat RAM, hanya aktif saat dibutuhkan.
license: MIT
metadata:
  author: Bagas Cihuy
  version: "1.0.0"
---

# PentAGI Skill — Autonomous Penetration Testing

Gunakan skill ini saat user meminta audit keamanan sistem, pengujian celah (penetration testing) otomatis pada port/domain/API internal atau eksternal yang diizinkan.

## Prinsip Operasional (Hemat RAM)
PentAGI membutuhkan stack PostgreSQL/pgvector dan worker container. Untuk menjaga efisiensi RAM VPS, kontainer **hanya dinyalakan saat tugas pentest berlangsung** dan **wajib dimatikan kembali setelah selesai**.

## Perintah Pengelolaan

Gunakan helper script di `scripts/manage.sh`:

1. **Inisialisasi / Setup**:
   ```bash
   ~/.hermes/skills/pentagi/scripts/manage.sh setup
   ```

2. **Nyalakan (On-Demand)**:
   ```bash
   ~/.hermes/skills/pentagi/scripts/manage.sh start
   ```
   Web UI & API akan aktif di port `8443` (bind `127.0.0.1:8443`).

3. **Cek Status**:
   ```bash
   ~/.hermes/skills/pentagi/scripts/manage.sh status
   ```

4. **Matikan (Bebaskan RAM)**:
   ```bash
   ~/.hermes/skills/pentagi/scripts/manage.sh stop
   ```

## Integrasi LLM & Keamanan
- Mendukung API key OpenAI, Gemini, Anthropic, DeepSeek, atau endpoint Ollama lokal.
- Jangan expose port 8443 secara publik tanpa autentikasi/tunnel aman.
- Pastikan target pentest memiliki izin eksplisit sebelum eksekusi pemindaian intensif.
