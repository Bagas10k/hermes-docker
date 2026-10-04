---
name: dynamic-fenwick-2d-grid
description: Dynamic O(log N) 2D grid resizing with Fenwick Trees.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [fenwick-tree, virtual-grid, 2d-panes, zero-cls, high-density]
    related_skills: [prefix-sum-variable-2d-grid, unified-2d-virtual-panes]
---

# Dynamic Fenwick 2D Grid

## When to Use
- Skenario tabel atau spreadsheet 2D interaktif dengan perubahan ukuran baris (*row height*) atau kolom (*column width*) secara dinamis.
- Mencegah layout shift (Zero CLS) saat pengguna menyeret (*drag-to-resize*) header tabel berkepadatan tinggi.
- Menggantikan prefix sum array statis $O(N)$ yang memerlukan rekalkulasi penuh setiap kali ukuran sel dimutasi.

## Overview & Architecture
Sistem menggunakan dua pohon Binary Indexed Tree (Fenwick Tree) 1D independen (satu untuk dimensi vertikal baris, satu untuk dimensi horizontal kolom).
- **Mutasi Ukuran (Point Update)**: $O(\log N)$ langsung via bitwise LSB propagation (`idx += idx & -idx`).
- **Pencarian Koordinat (Prefix Query)**: $O(\log N)$ untuk menghitung offset kumulatif.
- **Pencarian Sinar Biner (Binary Lifting)**: $O(\log N)$ menemukan baris/kolom aktif pada offset scroll tertentu tanpa operasi pencarian linear.

## How to Run
```bash
python3 -m unittest /home/ubuntu/.hermes/skills/creative/dynamic-fenwick-2d-grid/tests/test_fenwick_2d_grid.py
```

## Quick Reference
```python
from fenwick_2d_grid import DynamicFenwick2DGrid, Viewport2D

# Inisialisasi grid dengan tinggi baris & lebar kolom heterogen
grid = DynamicFenwick2DGrid(row_heights=[24.0] * 1000, col_widths=[100.0] * 50)

# Mutasi dinamis O(log N) saat drag-resize
grid.resize_row(10, 80.0)
grid.resize_col(4, 160.0)

# Hitung jendela virtual aktif dengan buffer overscan
viewport = Viewport2D(scroll_top=500.0, scroll_left=200.0, viewport_height=600.0, viewport_width=800.0)
window = grid.compute_visible_window(viewport)
```
