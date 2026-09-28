---
name: hermes-agent-foundry-builder
description: "Use when creating or running agents via Foundry Rust engine."
version: 1.0.0
author: Bagas Cihuy
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [foundry, rust, multi-agent, visual-dag, stress-test, zero-gc, production]
---

# Hermes Agent Foundry Builder

Skill komprehensif untuk merancang, mengompilasi, memvalidasi, mengeksekusi, dan menguji stres agen otonom menggunakan **Hermes Agent Foundry (Rust Engine & Studio)** karya Bagas Cihuy.

## 1. Arsitektur & Prinsip Inti
- **Engine Zero-GC / Ephemeral Worker**: Berbasis Rust (Axum, Tokio, SQLite WAL, Serde).
- **Latency & Footprint**: Eksekusi worker ephemeral sub-milidetik (<50us), daemon PM2 <10MB, throughput >700 req/s.
- **Strict Invariants**:
  1. **Zero-Emoji Policy**: Sanitasi seluruh output ke format teks murni atau SVG icon monokrom.
  2. **Deterministic DAG**: Deteksi siklus via Algoritma Kahn sebelum agen diizinkan berjalan.
  3. **Circuit Breaker**: Trip otomatis jika langkah > max_steps atau thrashing loop identik 3x berulang.
  4. **Strict Token & Timeout Budgeting**: Setiap run agen memiliki batas konsumsi token keras.

## 2. API Endpoints Produksi (`http://127.0.0.1:3200`)
- `GET /api/health` : Status kesehatan engine dan model memori.
- `POST /api/dag/validate` : Validasi siklus dan topological sort DAG.
- `POST /api/compiler/prompt-to-agent` : Kompilasi teks prompt bahasa alami ke spesifikasi agen DAG lengkap.
- `GET /api/templates` : Daftar katalog template bawaan siap pakai (Content, Finance, DevOps, Code Review, Docs).
- `GET /api/agents` & `POST /api/agents` : Manajemen persistensi agen di basis data SQLite.
- `POST /api/agents/:id/trigger` : Memicu eksekusi agen melalui Ephemeral Worker Engine.
- `GET /api/runs` : Audit trail riwayat eksekusi agen (status, durasi, token).

## 3. Alur Kerja Standar (Workflow)
1. **Perancangan Prompt atau Desain Visual**:
   - Kirim deskripsi tugas ke `POST /api/compiler/prompt-to-agent`.
   - Atau buat modul di antarmuka kanvas web `public/` (Visual Canvas & Touch Gestures).
2. **Validasi Pra-Eksekusi**:
   - Periksa ketiadaan dependensi melingkar (*no circular dependency*).
   - Pastikan data binding mengalir searah (tidak ada forward reference).
3. **Pemicu & Observasi**:
   - Panggil `POST /api/agents/:id/trigger` dengan payload JSON.
   - Ambil metrik `execution_time_us`, `tokens_consumed`, dan `step_logs`.
4. **Stress Testing Invariant**:
   - Lakukan stress test konkuren menggunakan Python `concurrent.futures`.
   - Pastikan error rate 0.0% dan memory leak nihil.
