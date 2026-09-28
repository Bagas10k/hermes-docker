# SKILL MIGRATION PLAN — PENGEMBANGAN SKILL OS
**Tanggal:** 28 September 2026  
**Prinsip:** 6 Tahap Bertahap (S0 s.d. S5) tanpa gangguan pada runtime produksi.

---

## Tahap S0 — Skill Inventory Read-Only (STATUS: COMPLETED)
- Menghasilkan `SKILL_INVENTORY.md` dan `SKILL_OVERLAP_MAP.md`.
- Tidak ada modifikasi file skill.

## Tahap S1 — Metadata Registry Shadow Mode (STATUS: NEXT)
- Mengekstrak frontmatter YAML dari 232 skill ke satu file ringkas `skills_registry.json`.
- Menyediakan fungsi pencarian metadata berbasis keyword & intent tanpa memuat isi teks SKILL.md.
- Acceptance Test: Pencarian intent "bento grid" mengembalikan `bento-grid-spatial-composer` dalam < 5ms.

## Tahap S2 — NO_SKILL + Dependency + Conflict Resolver Shadow
- Memasang aturan `NO_SKILL`: jika task hanya edit 1 baris teks atau operasi shell biasa, tolak pemanggilan skill.
- Memasang Conflict Resolver: jika intent web design, prioritaskan `bento-grid-spatial-composer` dan suppress `genjutsu`.

## Tahap S3 — Skill Chain Canary
- Menguji pembentukan rantai skill otomatis: `intent: "buat landing page"` -> Chain: [`design-md`, `bento-grid-spatial-composer`, `typography-ux-copy`, `impeccable`].
- Jalankan di 1 proyek uji coba (sandbox).

## Tahap S4 — Performance Evidence Ledger
- Mencatat durasi eksekusi, jumlah tool call, dan status kelulusan pengujian untuk setiap skill yang dipakai.

## Tahap S5 — Continuous Improvement Pipeline
- Skill yang gagal diverifikasi (skor < 5 atau rejected by QC) otomatis ditandai dan dibuatkan proposal perbaikan di sandbox sebelum disentuh di repositori utama.
