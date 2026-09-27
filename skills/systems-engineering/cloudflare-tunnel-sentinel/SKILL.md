---
name: cloudflare-tunnel-sentinel
description: Manage Cloudflare Tunnel edge ingress, probes, and metrics.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [cloudflare, tunnel, ingress, sentinel, zero-trust, networking]
    related_skills: [supabase-selfhosted-ops, live-sandbox-hot-preview]
---

# Cloudflare Tunnel Sentinel Skill

Skill ini mengelola, memantau, dan memverifikasi integritas koneksi Cloudflare Tunnel (`cloudflared`) untuk ingress publik VPS dengan nol port terbuka di firewall, observabilitas endpoint metrik lokal, dan supervisi proses PM2.

## When to Use

- Memverifikasi status kesehatan dan koneksi redundan edge tunnel (`cloudflared`).
- Memeriksa endpoint observabilitas `/ready` dan Prometheus `/metrics`.
- Melakukan audit supervisi proses tunnel di PM2 (`cf-tunnel-1`, `cf-tunnel-2`).
- Mendeteksi anomali jabat tangan QUIC (UDP) atau koneksi HA yang terdegradasi.

## Prerequisites

- Daemon `cloudflared` terpasang di host (`/home/ubuntu/.local/bin/cloudflared` atau system path).
- Token tunnel terisolasi di berkas rahasia (`--token-file`).
- Flag observabilitas `--metrics 127.0.0.1:<port>` aktif saat menjalankan tunnel.
- PM2 terpasang untuk supervisi proses tunnel persisten.

## Quick Reference

Jalankan skrip pemeriksa kesehatan sentinel:
`terminal(command="python3 ~/.hermes/skills/systems-engineering/cloudflare-tunnel-sentinel/scripts/cf_sentinel.py", timeout=15)`

Format JSON murni untuk integrasi otomatisasi:
`terminal(command="python3 ~/.hermes/skills/systems-engineering/cloudflare-tunnel-sentinel/scripts/cf_sentinel.py --json", timeout=15)`

Periksa endpoint ready secara langsung:
`terminal(command="curl -s http://127.0.0.1:20241/ready", timeout=5)`

## Procedure

1. **Audit Status Kesiapan Edge (/ready)**:
   - Evaluasi respons JSON dari `http://127.0.0.1:20241/ready`.
   - Kriteria sukses: `status == 200` dan `readyConnections >= 1` (standar HA: 4 koneksi).
2. **Audit Metrik Prometheus (/metrics)**:
   - Ambil metrik `cloudflared_tunnel_ha_connections` dan akumulasi `quic_client_closed_connections`.
   - Kriteria sukses: `cloudflared_tunnel_ha_connections >= 2`.
3. **Audit Supervisi Proses (PM2)**:
   - Periksa daftar proses PM2 (`cf-tunnel-1`, `cf-tunnel-2`).
   - Kriteria sukses: Status `online`, restart counter stabil, dan memori RSS stabil (<60 MB).

## Pitfalls

- **Token Expose di Process Table**: Jangan melewatkan token mentah via argumen CLI `--token`. Gunakan `--token-file` agar token aman dari inspeksi `ps aux`.
- **Missing Metrics Flag**: Jika flag `--metrics` tidak disertakan saat daemon start, probing lokal via port 20241 akan gagal (Connection Refused).
- **QUIC UDP Blackhole**: Jika provider jaringan memblokir UDP port 7844 keluar, tunnel beralih ke TCP fallback yang meningkatkan tail-latency.

## Verification

Buktikan konektivitas tunnel dengan mengeksekusi skrip sentinel lokal:
`terminal(command="python3 ~/.hermes/skills/systems-engineering/cloudflare-tunnel-sentinel/scripts/cf_sentinel.py --endpoint 127.0.0.1:20241", timeout=10)`
Pastikan output mencantumkan `[HEALTHY]` dan `HA Connections: 4`.
