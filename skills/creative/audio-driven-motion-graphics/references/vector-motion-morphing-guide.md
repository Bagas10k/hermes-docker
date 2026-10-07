# Hermes Vector Motion & Morphing Guide v1.0

Dokumen acuan desain dan spesifikasi teknis untuk mengotomatisasi video motion graphic vektor berbasis voice-over.

## 1. Prinsip Utama: Makna ke Bentuk (Semantic to Visual)

Formula alur kerja: `Makna → Objek → Hubungan → Transformasi → Timing`.
Jangan mencari satu gambar terpisah untuk setiap kalimat. Hermes menerjemahkan makna voice-over menjadi objek vektor sederhana, menentukan hubungan transformasi antarbentuk, lalu membuat satu rangkaian visual berkesinambungan (*continuity chain*) yang terus bertransformasi mengikuti narasi.

## 2. Hierarki Sumber Aset (Asset Sourcing)

1. **Primitive SVG:** Bentuk geometri dasar (`circle`, `ellipse`, `rect`, `rounded-rect`, `line`, `polyline`, `triangle`, `hexagon`, `arc`, `wave`, `blob`). Paling ringan dan ramah morph.
2. **Procedural SVG:** Dibangun dari resep grammar terstandarisasi (misal: database = top ellipse + body + separator_1 + separator_2).
3. **Internal Asset Library:** Reuse aset yang telah lulus QA di direktori `ASSETS/`.
4. **Reference Generation:** Digunakan hanya jika konsep sangat abstrak untuk mencari ide komposisi.
5. **Vector Reconstruction:** Rekonstruksi bersih menjadi SVG internal sesuai token desain.
*Haram menyematkan raster/bitmap (PNG/JPG base64) di dalam SVG.*

## 3. Standar Wajib SVG & Style Guide Vektor

- **Canvas Video:** 1080 x 1920 (9:16) untuk Reels/Shorts vertikal atau 1920 x 1080 (16:9).
- **SVG viewBox:** `0 0 512 512` standar tunggal seluruh aset.
- **Grid:** 8 px untuk alignment, sizing, dan snap.
- **Stroke Tokens:** Base 4 px (tokens: `[2, 4, 6] px`).
- **Corner Radius:** `[8, 16, 24, 32] px` (diambil dari token, dilarang nilai acak).
- **Kompleksitas Objek:** Maksimal 5–7 objek utama per adegan, maksimal 3 layer kedalaman (foreground, main, background).
- **Elemen Naming:** ID semantik stabil (`#body`, `#top`, `#separator`, `#indicator`) agar dapat ditargetkan animasi individual.

## 4. Empat Metode Morphing & Decision Tree

```
IF silhouette_similarity >= 0.75:
    -> TRUE_PATH_MORPH (Interpolasi path kurva A ke B)
ELSE IF reusable_parts >= 2:
    -> DECOMPOSITION_MORPH (Objek dipecah jadi komponen beralih fungsi)
ELSE IF spatial_relation_is_clear:
    -> TRANSFORM_MORPH (Posisi, skala, rotasi, radius, opacity)
ELSE:
    -> MASK_REVEAL_MORPH (Fallback wipe / radial reveal / directional slide)
```

- **Urutan Implementasi Teraman:** Transform morph → Decomposition morph → Morph vocabulary → True path morph.
- **Prinsip Fallback:** True path morph adalah fitur, bukan single point of failure. Setiap transisi wajib memiliki fallback transform/decomposition.

## 5. Visual Grammar: Bahasa Semantik ke Bentuk

| Konsep Bahasa | Metafora Visual Vektor | Motion Cue |
|---|---|---|
| **Pertumbuhan / Skala** | Bar chart, expanding circle, nested layers | Scale up, rise, accumulate |
| **Kecepatan / Efisiensi** | Garis arah, lintasan pendek, streak | Fast translation, tight stagger |
| **Masalah / Galat** | Misalignment, broken path, warning badge | Shake ringan, drift, red accent |
| **Solusi / Valid** | Alignment rapi, checkmark, jalur bersih | Snap to grid, settle, green/mint |
| **Koneksi / Relasi** | Node + garis konektor | Line draw, pulse antar node |
| **Analisis / Filter** | Scanner beam, funnel, branching | Scan sweep, eliminate node |
| **Keputusan** | Jalur bercabang (forking lines) | Cabang lain redup, satu jalur maju |
| **Otomasi** | Loop tertutup, conveyor, linked modules | Continuous flow, repeat cycle |

## 6. Tipografi, Subtitle & Antarmuka Mobile

1. **Subtitle Singkat & Terbaca:** Maksimal 2 baris pendek per beat bicara. Waktu disinkronkan langsung dari transkrip dan audio riil.
2. **Penekanan Kontekstual (Anti-Monoton):** Kata yang tegas, data angka, atau kontras makna diberi 1 jenis perlakuan (garis bawah aksen, skala 1.2x, atau penataan posisi), sementara kata lain tetap tenang.
3. **Safe-Area Mobile:** Visual dilarang menabrak batas atas (status bar), bawah (dock/caption), atau kanan (tombol like/share platform Shorts/Reels).
4. **Isolasi Pembicara:** Elemen grafis dan subtitle dilarang menutupi wajah pembicara yang sedang aktif di layar.
