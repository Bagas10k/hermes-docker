---
name: hermes-foundry-visual-canvas
description: Build and deploy modular visual DAG agent canvases.
version: 1.0.0
author: Bagas Cihuy
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes-foundry, visual-canvas, lego-builder, dag, toposort, kahn, vector-cables]
---

# Hermes Foundry Visual Canvas (Lego Block Builder)

Skill ini memandu perancangan, validasi, dan rendering kanvas modular visual (Visual Modular Canvas / Lego Block Builder) untuk merakit pipa agen AI berbasis graf DAG deterministik tanpa pustaka frontend eksternal yang berat.

## 1. Arsitektur Inti
- **Zero-Dependency Vector Canvas**: Menggunakan elemen SVG asli (`<svg>`) dan `<path>` kurva Bezier kubik dinamis:
  $$d = \text{M } x_1, y_1 \text{ C } x_1 + \Delta x \cdot 0.5, y_1 \text{ } x_2 - \Delta x \cdot 0.5, y_2 \text{ } x_2, y_2$$
- **In-Browser Kahn Toposort**: Validasi siklus melingkar (*deadlock cycle detection*) langsung di memori browser saat kabel ditarik:
  1. Hitung `inDegree` dan tabel ketetanggaan `adj`.
  2. Masukkan simpul `inDegree == 0` ke antrean (`queue`).
  3. Lakukan reduksi derajat. Jika simpul terproses $\ne$ total simpul, tolak koneksi kabel seketika (*instant rollback*).
- **Type-Checked Connector Ports**:
  - `trigger`: Hanya memiliki port output (sumber hulu murni).
  - `context`, `reasoning`, `tool`, `guardrail`, `output`: Memiliki port input dan output.
- **Sugiyama Hierarchical Auto-Layout**:
  - Menentukan kedalaman layer tiap simpul via algoritma longest path.
  - Mengelompokkan simpul ke kolom hierarki dan menggeser koordinat $X$ dan $Y$ dalam 1 klik.
- **Mobile Ergonomics**:
  - Touch panning & pinch/drag support.
  - Floating palette dock di desktop, otomatis beralih ke *Bottom Navigation Dock* pada layar $\le 768\text{px}$.

## 2. Standar Visual & Integritas
- **Zero-Emoji Policy**: Seluruh lencana status dan tipe modul menggunakan tipografi monokrom atau teks mono (`[TRIGGER]`, `[CONTEXT]`, `[TOOL]`).
- **Tactile Pastel Pop**: Latar belakang grid bintik Cartesian halus (`#FAF8F5`), kartu putih bergaris tepi lembut (`#E2E8F0`), bayangan fisik taktil.
- **1-Click Deployment Contract**: Mengonversi state nodes dan edges di DOM menjadi skema `AgentSpec` standar Rust foundry dan mem-POST ke `/api/agents`.
