---
name: context-compaction-curator
description: "Curate agent context, preserve prefix cache, and save tokens."
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [context-compaction, prefix-cache, token-optimization, memory-curator, flow-state]
    related_skills: [otak-koding, mathematical-problem-solving]
---

# Context Compaction & Semantic Memory Distillation

Skill ini mengelola kompresi konteks riwayat percakapan agen otonom: memangkas token pembengkakan (*token bloat*), melindungi *KV prefix cache*, mencegah *semantic drift* pada handoff tugas, dan menjaga responsivitas koding instan (*flow state*).

## When to Use
- Konteks percakapan mendekati batas aman token (> 50.000 token atau jendela riwayat membengkak > 25 giliran).
- Riwayat eksekusi dipenuhi ratusan baris keluaran tool `read_file`, `terminal`, atau `search_files` yang sudah tidak dibutuhkan lagi.
- Sesi agen terasa melambat (TTFT tinggi akibat hilangnya prefix cache hit).
- Ingin membuat titik simpan (*checkpoint handoff*) tugas yang padat tanpa kehilangan batasan instruksi pengguna.

Don't use for:
- Sesi obrolan baru atau pendek (< 6 giliran pesan).
- Penyimpanan memori permanen lintas sesi (gunakan `memory` atau `skill_manage`).

## Prerequisites
- Python 3.8+ (stdlib saja, zero external dependencies).
- Berkas skrip `context_compactor.py` di direktori `scripts/`.

## Quick Reference
Kompilasi dan kompres berkas log percakapan:
```bash
python3 ~/.hermes/skills/autonomous-ai-agents/context-compaction-curator/scripts/context_compactor.py --input session.json --output session_compacted.json --max-tokens 8000
```

## Procedure

1. **Partisi Konteks 3 Lapis (Three-Tier Partitioning)**:
   - *Tier 0 (Static Prefix)*: Kunci system prompt dan profil pengguna secara mutlak. Jangan ubah satu karakter pun agar KV-cache tetap 100% valid.
   - *Tier 1 (Compressible Middle)*: Identifikasi giliran lama (di luar 4 giliran terakhir). Pangkas luaran tool yang panjang menjadi ringkasan status keluar.
   - *Tier 2 (Active Window)*: Pertahankan 4 pesan terakhir apa adanya (*verbatim*) untuk menjaga koherensi pemikiran langsung.

2. **Eksekusi Distilasi Deterministik**:
   - Jalankan `scripts/context_compactor.py` pada berkas sesi target.
   - Periksa bahwa artefak berkas yang telah dibuat, batasan keras pengguna, dan status tugas terangkum dalam node `compacted_context_summary`.

3. **Verifikasi Integritas**:
   - Pastikan penghematan token mencapai 40%–70%.
   - Pastikan tidak ada aturan negatif atau batasan pengguna (*user constraints*) yang hilang selama distilasi.

## Pitfalls
- **Prefix Invalidation Trap**: Menaruh teks tanggal, jam, atau ringkasan baru di awal prompt sistem merusak seluruh hash KV-cache, memicu latensi tinggi dan biaya komputasi membengkak.
- **Aggressive Tail Pruning**: Menghapus pesan pengguna terbaru menyebabkan halusinasi atau kebingungan agen terhadap tujuan saat ini.
- **Narrative Drift**: Ringkasan berbentuk narasi fiktif sering menghilangkan detail path file atau instruksi larangan kritis. Selalu gunakan format poin terstruktur.

## Verification
- Jalankan uji mandiri pada berkas pesan sintetis:
  ```bash
  python3 ~/.hermes/skills/autonomous-ai-agents/context-compaction-curator/scripts/context_compactor.py --input /tmp/test_session.json
  ```
- Output wajib menunjukkan status `COMPACTED`, `prefix_preserved: true`, dan `saved_pct > 30%`.
