---
name: agent-continual-learning
description: Continual learning and skill crystallization for agents.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [continual-learning, skill-crystallization, experience-replay, anti-forgetting, trajectory-distillation]
    related_skills: [agent-trajectory-evals, context-compaction-curator, autonomous-orchestrator]
---

# Agent Continual Learning & Skill Crystallization

Skill operasional untuk mengorkestrasi pembelajaran berkelanjutan (*continual learning*) tanpa katastrofe lupa (*catastrophic forgetting*), kristalisasi skill prosedural otomatis dari trajektori sukses, serta konsolidasi memori episodik ke semantik pada agen otonom.

## When to Use

- Agen berulang kali menyelesaikan tugas teknis kompleks dan ingin mengkristalisasi pola solusinya menjadi modul skill permanen yang dapat digunakan kembali.
- Menjaga stabilitas perilaku agen saat menyerap preferensi baru pengguna tanpa merusak pemahaman (*plasticity-stability trade-off*).
- Menghindari pembengkakan context window (*context bloat*) akibat penumpukan contoh mentah dengan mendistilasi trajektori menjadi ringkasan aturan kontraktual (In-Context Procedural Distillation).
- Mengevaluasi apakah suatu prosedur baru memenuhi syarat kristalisasi (*3-Strike Heuristic*) sebelum disimpan ke repositori skill permanen.

### Don't use for:

- Catatan memo sekali pakai atau fakta sementara yang hanya relevan untuk sesi berjalan (gunakan working memory atau session history).
- Fine-tuning model bobot neural parameter di server tanpa GPU; skill ini beroperasi pada tingkatan *in-context continuous memory and procedural crystallization*.

## Prerequisites

- Python 3.10+ dengan modul standar (`json`, `re`, `hashlib`, `pathlib`, `sqlite3`).
- Akses baca-tulis ke direktori skill user (`~/.hermes/skills/`) dan memori persisten.
- Skrip pembantu ekstraksi trajektori: `python3 ~/.hermes/skills/autonomous-ai-agents/agent-continual-learning/scripts/crystallize_skill.py`.

## Quick Reference

```bash
# Audit kandidat kristalisasi dari log trajektori eksekusi
python3 ~/.hermes/skills/autonomous-ai-agents/agent-continual-learning/scripts/crystallize_skill.py --audit

# Jalankan ekstraksi dan validasi pembentukan draf skill dari trajektori terverifikasi
python3 ~/.hermes/skills/autonomous-ai-agents/agent-continual-learning/scripts/crystallize_skill.py --extract --topic "nama-topik" --category "kategori"

# Uji stabilitas regresi dan deteksi catastrophic forgetting
python3 ~/.hermes/skills/autonomous-ai-agents/agent-continual-learning/scripts/crystallize_skill.py --verify-invariants
```

## Procedure

### 1. Ingestion & Filtering Trajektori Sukses (Success Trajectory Mining)
- Ambil trajektori eksekusi agen yang berstatus sukses (`exit_code == 0`, lolos verifikasi deterministik).
- Buang langkah-langkah bising (*noise pruning*): percobaan gagal sementara, sintaks typo yang diperbaiki seketika, dan pembacaan berkas non-kritis.
- Kriteria penyelesaian: Trajektori tereduksi menjadi urutan minimal State-Action-Reward-Observation (SARO) yang padat.

### 2. Evaluasi Ambang Batas Kristalisasi (3-Strike Invariant)
- Terapkan aturan 3-Strike: Prosedur hanya dikristalisasi jika pola urutan tindakan sukses yang sama telah terulang minimal 3 kali pada sesi/target yang berbeda dengan tingkat keberhasilan $\ge 90\%$.
- Hitung Information Gain $\Delta I$ untuk memastikan prosedur baru tidak sekadar duplikasi dari skill yang telah ada.
- Kriteria penyelesaian: Nilai signifikansi empiris terkonfirmasi lolos ambang batas tanpa redundansi.

### 3. Ekstraksi Kontrak & Sintesis SKILL.md (Procedural Distillation)
- Abstraksikan path spesifik atau nama file instans menjadi parameter generik (`<target-path>`, `<port>`, `<config-key>`).
- Formulasikan komponen inti: Deskripsi padat ($\le 60$ karakter diakhiri titik), *When to Use*, *Prerequisites*, *Quick Reference*, *Procedure* berindikator sukses, *Pitfalls* nyata, dan *Verification*.
- Kriteria penyelesaian: File draft SKILL.md lolos validasi sintaks YAML frontmatter dan batasan karakter.

### 4. Proteksi Anti-Forgetting (Stability Boundary Gate)
- Lakukan pengujian regresi cepat terhadap set tugas acuan (*golden test suites*) untuk memastikan injeksi skill baru tidak menurunkan akurasi tugas fundamental agen.
- Terapkan partisi memori EWC (*Elastic Weight Consolidation analog in prompt memory*): tetapkan bobot prioritas tinggi pada aturan dasar yang tidak boleh ditimpa.
- Kriteria penyelesaian: Tidak ada benturan batasan atau regresi instruksi inti.

## Pitfalls

1. **Premature Crystallization:** Mengkristalisasi prosedur yang baru berhasil 1 kali akibat kebetulan konteks, menghasilkan skill kaku (*overfitted*) yang gagal pada variasi input minor.
2. **Context Pollution:** Menyertakan log mentah puluhan kilobita ke dalam deskripsi skill, memboroskan token sistem prompt pada setiap interaksi.
3. **Silent Semantic Drift:** Revisi skill secara berulang tanpa pengujian regresi yang menyebabkan agen melupakan batasan keselamatan asli (*safety boundaries*).

## Verification

- Jalankan validator frontmatter mandiri:
  ```bash
  python3 -c '
  import yaml, pathlib
  p = pathlib.Path("~/.hermes/skills/autonomous-ai-agents/agent-continual-learning/SKILL.md").expanduser()
  text = p.read_text()
  assert text.startswith("---")
  parts = text.split("---")
  fm = yaml.safe_load(parts[1])
  assert len(fm["description"]) <= 60 and fm["description"].endswith(".")
  print("VALIDATION PASSED: Frontmatter and length conform to hardline standards.")
  '
  ```
- Pastikan skrip CLI diagnostik teruji dengan status exit code 0.
