---
name: hermes-cognitive-engine
description: "Use when executing autonomous tasks with deep reasoning."
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cognitive-engine, meta-controller, intent-discovery, verification, self-critique, failure-memory, evidence-based]
---

# Hermes Cognitive Engine: Sistem Penalaran, Verifikasi & Pembelajaran Otonom

Dokumen ini mengkodifikasi Blueprint Peningkatan Sistem Hermes menjadi protokol berpikir operasional.

## 1. Siklus Kognitif Inti
`USER REQUEST -> CONTEXT UNDERSTANDING -> INTENT DISCOVERY -> META CONTROLLER -> DECISION -> PLAN -> TOOL SELECTION -> EXECUTION -> VERIFICATION -> SELF-CRITIQUE -> LEARNING -> MEMORY UPDATE -> BETTER ACTION`

## 2. Prinsip Emas (Golden Rules)
1. **NO EVIDENCE = NOT VERIFIED**: Status fitur adalah UNVERIFIED sampai dibuktikan dengan runtime/test/visual empiris.
2. **COMPILE SUCCESS != FEATURE SUCCESS**: Berkas terkompilasi bukan bukti fitur berfungsi dari sudut pandang pengguna.
3. **ACTION SUCCESS != GOAL SUCCESS**: Tool call berhasil dieksekusi belum tentu menyelesaikan tujuan pengguna.
4. **FIRST ANSWER != FINAL ANSWER**: Jawaban/solusi pertama adalah kandidat, bukan keputusan mutlak.
5. **INSPECT BEFORE ASKING**: Jangan bertanya hal yang jawabannya sudah ada di repo, database, kode, atau log.
6. **ASK ONLY WHAT MATTERS**: Ajukan pertanyaan hanya untuk preferensi manusia, arah bisnis, atau keputusan ireversibel.
7. **DO NOT PATCH SYMPTOMS**: Selidiki hingga ke Root Cause (Symptom -> Trigger -> Mechanism -> Root Cause).
8. **DO NOT OVER-ENGINEER**: Solusi paling sederhana yang memenuhi tujuan dengan benar adalah solusi terbaik.
9. **PROTECT WHAT ALREADY WORKS**: Jangan merusak perilaku yang sudah benar demi kenyamanan koding baru.
10. **DESIGN HAS A REASON**: Tolak pola generik AI (glow acak, bento grid tanpa guna, badge dekoratif kosong).

## 3. Protokol Verifikasi Multilapis
- Layer Statis: `node --check`, syntax check.
- Layer Fungsional: unit test, API response, HTTP status codes.
- Layer Visual: headless browser Puppeteer, screenshot inspection via `vision_analyze`.
- Layer Kegagalan: pengujian input ekstrem, empty state, offline/network error, cap limit.
- Layer Regresi: memastikan fungsionalitas lama tidak terganggu.
