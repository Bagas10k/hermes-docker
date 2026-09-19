---
name: autonomous-preference-evolution
description: "Self-evolving negative constraints and preferences pipeline. Automatically learns user dislikes, triggers post-task audits, enforces strict blocker before sending output, and locks rules without nagging."
version: 1.0.0
author: Bagas & Hermes
license: MIT
metadata:
  hermes:
    tags: [autonomous-learning, preferences, negative-constraints, self-audit, strict-blocker, zero-nagging]
---

# Autonomous Preference Evolution (Protokol Belajar Mandiri & Pantangan User)

Sistem evolusi mandiri 24/7 agar agen tidak pernah mengulangi kesalahan atau pola desain yang tidak disukai pengguna.

## 3 Pilar Inti Kolaboratif:
1. **Instant Feedback Scoring & Dislike Extraction:**
   - Setiap kali user memberikan kritik tajam, nilai rendah (< 6/10), atau koreksi ("jangan pakai X", "ini alay", "buang Y"):
   - Agen LANGSUNG membedah histori giliran terakhir, menarik akar penyebab ketidaksukaan tersebut secara spesifik, dan menguncinya ke memori / `SKILL.md` saat itu juga.
2. **Autonomous Negative Constraints & Strict Blocker:**
   - Sebelum kode/output dikonfirmasi selesai, agen wajib memvalidasi hasilnya terhadap daftar blacklist mutlak:
     - Dilarang teks bergradasi pelangi / multi-warna (wajib solid monokrom).
     - Dilarang menggunakan emoji untuk ikon UI/UX (wajib pure vector inline SVG 1.5px/2px).
     - Dilarang badge kicker dekoratif di atas hero headline.
     - Dilarang kotak logo/ikon generik (wajib pure wordmark).
     - Dilarang placeholder teks semu/lorem ipsum (wajib form-meets-function).
     - Dilarang grid bento kotak simetris kaku (wajib asimetris dinamis).
     - Dilarang teks bertabrakan dengan foto/elemen lain.
   - **Strict Blocker Rule:** Jika ditemukan pelanggaran sekecil apa pun, agen WAJIB menolak outputnya sendiri dan merombak ulang secara mandiri sebelum menunjukkannya ke pengguna.
3. **Periodic Post-Task & Idle Self-Audit:**
   - Pada waktu henti (idle), agen secara berkala mengevaluasi catatan dan kode yang baru saja dibangun untuk mencari potensi cacat arsitektur, memperbarui memori, dan mengunci aturan tanpa basa-basi.

## Sinyal Komunikasi:
- Catat diam-diam ke memory & `SKILL.md`.
- Beri sinyal konfirmasi ringkas dan tegas ke pengguna: `[Rule Terkunci: <poin pantangan>]` tanpa ceramah atau narasi panjang.
