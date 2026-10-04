---
name: dynamic-virtual-resize-observer
description: "Virtualize dynamic height DOM lists with zero-CLS scroll."
version: 1.0.0
author: Bagas Cihuy, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [virtualization, resize-observer, fenwick-tree, scroll-anchoring, zero-cls]
    related_skills: [virtualized-dom-windowing, zero-layout-shift-artifacts]
---

# Dynamic Virtual ResizeObserver Skill

Engine virtualisasi DOM berkinerja tinggi untuk daftar dan tabel dengan tinggi elemen variabel atau dinamis (kartu pesan, accordion, gambar lazy-load). Menggabungkan pohon Fenwick (Binary Indexed Tree) untuk kalkulasi offset prefix sum $O(\log N)$, batching ResizeObserver asinkron, dan scroll anchoring otomatis berstatus Zero Cumulative Layout Shift (CLS = 0).

## When to Use
- Merender daftar ratusan ribu elemen dengan tinggi bervariasi yang belum diketahui di awal.
- Konten memuat elemen yang membesar/mengecil secara dinamis (misal gambar termuat, teks diperluas) tanpa ingin layar melompat (*flicker-free scroll anchoring*).
- Menghindari reflow DOM masal dan menjaga alokasi node DOM aktif konstan $O(1)$.

## How to Run
Gunakan helper engine Python untuk menghitung rentang virtual dan mengkompensasi delta ResizeObserver:
```bash
python3 -c "
from dynamic_virtual_resize_engine import DynamicVirtualResizeEngine
engine = DynamicVirtualResizeEngine(total_rows=50000, viewport_height=600.0, estimated_row_height=45.0)
win = engine.compute_window(scroll_y=1200.0)
print(f'Rendered: {win[\"render_start\"]}..{win[\"render_end\"]} (DOM: {win[\"rendered_count\"]})')
"
```

## Quick Reference
1. **Inisialisasi**: `engine = DynamicVirtualResizeEngine(total_rows, viewport_height, estimated_row_height)`
2. **Kalkulasi Jendela**: `win = engine.compute_window(scroll_y)`
3. **Umpan ResizeObserver**: `result = engine.handle_resize_observer_batch([(idx, new_height), ...], current_scroll_y, anchor_index)`
4. **Scroll Anchoring**: Gunakan `result["adjusted_scroll_y"]` untuk menyesuaikan scroll container secara presisi.

## Invarian Matematis
- **Batas Alokasi DOM Aktif**: $K_{\text{dom}} \le \lceil H_{\text{viewport}} / H_{\text{min}} \rceil + 2 \cdot \text{overscan} + 2$
- **Konservasi Tinggi Total**: $H_{\text{total}} = H_{\text{top\_spacer}} + \sum_{i \in \text{render\_range}} H_i + H_{\text{bottom\_spacer}}$
- **Kompensasi Scroll Anchor**: $\Delta_{\text{scroll}} = \sum_{j < \text{anchor}} (H_{j, \text{new}} - H_{j, \text{old}})$
