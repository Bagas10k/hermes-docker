---
name: virtual-grid-engine
description: Virtualize massive 2D grids, Fenwick trees & frozen panes.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [virtualization, 2d-grid, spreadsheet, fenwick-tree, prefix-sums, frozen-panes, zero-cls, dom-recycling]
    related_skills: [spanning-cell-2d-grid, high-density-data-surfaces, zero-layout-shift-artifacts]
---

# Virtual 2D Grid Engine

Engine terpadu virtualisasi grid 2D simultan berkinerja tinggi untuk tabel data masif, spreadsheet (>100.000 baris x >500 kolom), dan antarmuka berkepadatan tinggi. Mengonsolidasikan arsitektur komputasi koordinat: Dual-Axis Fenwick Tree, Prefix-Sum Binary Search, Four-Quadrant Frozen Panes, dan Bounded DOM Windowing.

## When to Use
- Merender lembar kerja (spreadsheet), buku besar finansial, atau matriks telemetri masif dengan ukuran baris/kolom dinamis atau heterogen.
- Virtualisasi dua arah (sumbu X dan Y) dengan penguncian DOM aktif konstan $O(1)$ (< 350 - 700 elemen DOM aktif).
- Membutuhkan penyesuaian ukuran interaktif (*drag-to-resize*) dengan kalkulasi mutasi cepat $O(\log N)$ via Binary Indexed Tree (Fenwick Tree) tanpa lonjakan layout (Zero Cumulative Layout Shift / CLS).
- Membagi tampilan menjadi 4 kuadran tersinkronisasi (*frozen panes*: sudut NW, header kolom NE, indeks baris SW, dan badan sel SE).
- Menghitung irisan sel tampak (*visible window*) dan spacer kompensasi scroll secara deterministik.

## Arsitektur & Strategi Algoritma

### 1. Dual-Axis Dynamic Fenwick Tree ($O(\log N)$ Resize Mutation)
Untuk skenario di mana pengguna aktif mengubah ukuran baris/kolom secara interaktif:
- **Point Update**: $O(\log N)$ via bitwise LSB propagation (`idx += idx & -idx`).
- **Prefix Query**: $O(\log N)$ untuk menghitung offset kumulatif fisik.
- **Binary Lifting**: $O(\log N)$ menemukan baris/kolom aktif pada offset scroll tertentu tanpa pencarian linear.

```python
# Penggunaan Dynamic Fenwick 2D
from fenwick_2d_grid import DynamicFenwick2DGrid, Viewport2D

grid = DynamicFenwick2DGrid(row_heights=[24.0] * 100000, col_widths=[100.0] * 500)
grid.resize_row(10, 80.0) # O(log R)
grid.resize_col(4, 160.0) # O(log C)
window = grid.compute_visible_window(Viewport2D(scroll_top=500.0, scroll_left=200.0, viewport_height=600.0, viewport_width=800.0))
```

### 2. Monotonic Prefix Sums & Binary Search ($O(\log R + \log C)$ Window Query)
Untuk grid berdimensi statis atau batch-loaded dengan ukuran heterogen:
- Memori bantu efisien: $O(R + C)$ tanpa mengalokasikan matriks 2D $O(R \times C)$.
- Resolusi batas tampak via `bisect_right` dalam waktu $O(\log R + \log C)$.
- Resolusi koordinat fisik sel tunggal dalam $O(1)$.

```python
# Penggunaan Variable Prefix Sum
from prefix_sum_grid import Variable2DVirtualGrid, Virtual2DViewport

grid = Variable2DVirtualGrid(row_heights=[30.0, 45.0, 60.0], col_widths=[100.0, 150.0])
viewport = Virtual2DViewport(scroll_top=20.0, scroll_left=50.0, viewport_height=600.0, viewport_width=800.0)
window = grid.compute_visible_window(viewport)
```

### 3. Four-Quadrant Unified Virtual Panes (Frozen Rows & Columns)
Mempartisi geometri total grid $(W_{\text{total}}, H_{\text{total}})$ menjadi 4 kuadran viewport:
1. **NW (North-West)**: Sudut beku persimpangan $(W_{\text{frozen}}, H_{\text{frozen}})$, tanpa translasi scroll.
2. **NE (North-East)**: Aliran header kolom horizontal, translasi $\Delta x = -\text{scroll}_x, \Delta y = 0$.
3. **SW (South-West)**: Aliran indeks baris vertikal, translasi $\Delta x = 0, \Delta y = -\text{scroll}_y$.
4. **SE (South-East)**: Badan sel virtual 2D, translasi $\Delta x = -\text{scroll}_x, \Delta y = -\text{scroll}_y$.

Menjamin sinkronisasi scroll absolut antar kuadran dan mencegah efek *shearing* (robekan visual) saat inersia scroll cepat.

### 4. Bounded DOM Windowing & Spacer Conservation
- **Plafon Alokasi DOM Aktif**:
  $$K_{\text{cells}} = \left(\lceil H_{\text{vp}} / H_{\text{min\_row}} \rceil + 2 \cdot \text{overscan}_y + 2\right) \times \left(\lceil W_{\text{vp}} / W_{\text{min\_col}} \rceil + 2 \cdot \text{overscan}_x + 2\right) \ll N_{\text{total}}$$
- **Konservasi Dimensi Ruang Spacer**:
  $$H_{\text{total}} = H_{\text{top\_spacer}} + H_{\text{rendered\_slice}} + H_{\text{bottom\_spacer}}$$
  $$W_{\text{total}} = W_{\text{left\_spacer}} + W_{\text{rendered\_slice}} + W_{\text{right\_spacer}}$$
- **Scroll Anchoring**: Menyesuaikan offset scroll otomatis saat baris/kolom sebelum titik jangkar mengalami perubahan ukuran:
  $$S_{x, \text{adjusted}} = S_x + \sum_{c < \text{anchor\_col}} \Delta W_c, \quad S_{y, \text{adjusted}} = S_y + \sum_{r < \text{anchor\_row}} \Delta H_r$$
