---
name: bidirectional-2d-virtual-grid
description: "Virtualize massive 2D grids with dual-axis scroll anchor."
version: 1.0.0
author: Bagas Cihuy, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [virtualization, 2d-grid, spreadsheet, fenwick-tree, zero-cls]
    related_skills: [dynamic-virtual-resize-observer, virtualized-dom-windowing]
---

# Bidirectional 2D Virtual Grid Skill

Engine virtualisasi grid 2D simultan (baris dan kolom variabel) berkinerja tinggi untuk aplikasi lembar kerja masif (*massive spreadsheets*), tabel pivot analitik, dan antarmuka bento grid multidimensi (>100.000 baris x >500 kolom). Memanfaatkan pohon Fenwick 1D terpisah (*decoupled dual-axis Fenwick trees*) untuk mengunci alokasi sel DOM aktif konstan $O(1)$ dan menjamin posisi visual jangkar tetap utuh saat ukuran sel berubah (Zero Cumulative Layout Shift).

## When to Use
- Merender lembar kerja (spreadsheet) atau data surface besar dengan ratusan kolom dan ratusan ribu baris.
- Memerlukan virtualisasi dua arah (sumbu X dan sumbu Y) secara simultan dengan ukuran sel fleksibel.
- Mencegah ledakan DOM ($50.000.000$ sel direduksi menjadi $<700$ sel aktif di layar).
- Menangani mutasi ukuran sel asinkron (kolom melebar/baris meninggi) dengan kompensasi scroll otomatis (*bidirectional scroll anchoring*).

## How to Run
Gunakan engine Python helper untuk menghitung irisan sel 2D yang aktif dan mengelola kompensasi mutasi ukuran:
```bash
python3 -c "
from bidirectional_2d_grid_engine import Bidirectional2DVirtualGrid
grid = Bidirectional2DVirtualGrid(total_rows=100000, total_cols=500, viewport_width=1200.0, viewport_height=800.0)
win = grid.compute_2d_window(scroll_x=2000.0, scroll_y=50000.0)
print(f'Active Cells: {win[\"active_cell_pool_count\"]} (Rows: {win[\"rows\"][\"rendered_count\"]}, Cols: {win[\"cols\"][\"rendered_count\"]})')
"
```

## Quick Reference
1. **Inisialisasi Grid 2D**:
   `grid = Bidirectional2DVirtualGrid(total_rows, total_cols, viewport_width, viewport_height, default_row_height=32.0, default_col_width=120.0)`
2. **Kalkulasi Jendela Tampilan 2D**:
   `window = grid.compute_2d_window(scroll_x, scroll_y)`
3. **Pembaruan Mutasi Ukuran Sel Asinkron**:
   `res = grid.handle_2d_resize_batch(row_updates=[(r, h), ...], col_updates=[(c, w), ...], current_scroll_x=x, current_scroll_y=y, anchor_row=ar, anchor_col=ac)`
4. **Kompensasi Posisi Jangkar**:
   Gunakan `res["adjusted_scroll_x"]` dan `res["adjusted_scroll_y"]` pada wadah scroll untuk mempertahankan titik pandang pengguna tanpa lonjakan layout.

## Invarian Matematis
- **Batas Kumpulan Sel Aktif (Active Cell Pool Budget)**:
  $$K_{\text{cells}} = \left(\lceil H_{\text{vp}} / H_{\text{min\_row}} \rceil + 2 \cdot \text{overscan}_y + 2\right) \times \left(\lceil W_{\text{vp}} / W_{\text{min\_col}} \rceil + 2 \cdot \text{overscan}_x + 2\right) \ll N_{\text{total}}$$
- **Konservasi Dimensi Dua Arah**:
  $$H_{\text{total}} = H_{\text{top\_spacer}} + H_{\text{rendered\_slice}} + H_{\text{bottom\_spacer}}$$
  $$W_{\text{total}} = W_{\text{left\_spacer}} + W_{\text{rendered\_slice}} + W_{\text{right\_spacer}}$$
- **Kompensasi Jangkar 2D (Bidirectional Scroll Anchoring)**:
  $$S_{x, \text{adjusted}} = S_x + \sum_{c < \text{anchor\_col}} \Delta W_c, \quad S_{y, \text{adjusted}} = S_y + \sum_{r < \text{anchor\_row}} \Delta H_r$$
