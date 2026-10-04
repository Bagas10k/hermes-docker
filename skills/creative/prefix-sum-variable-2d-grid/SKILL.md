---
name: prefix-sum-variable-2d-grid
description: "Virtualize variable 2D grid with prefix sum binary search."
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [virtualization, 2d-grid, prefix-sums, binary-search, ui-ux, zero-slop]
    related_skills: [unified-2d-virtual-panes, bidirectional-2d-virtual-grid, virtualized-dom-windowing]
---

# Prefix-Sum Variable Dimension Virtual 2D Grid

Virtualize dense 2D data grids with non-uniform variable row heights and column widths using cumulative prefix sums and binary search.

## When to Use
- Rendering large spreadsheets, financial ledgers, or matrix data where rows and columns have variable sizes.
- Computing visible slice windows in $O(\log R + \log C)$ time complexity.
- Calculating exact cell physical geometry (top, left, width, height) in $O(1)$ time.

## Quick Reference
```python
from scripts.prefix_sum_grid import Variable2DVirtualGrid, Virtual2DViewport

grid = Variable2DVirtualGrid(row_heights=[30.0, 45.0, 60.0], col_widths=[100.0, 150.0])
viewport = Virtual2DViewport(scroll_top=20.0, scroll_left=50.0, viewport_height=600.0, viewport_width=800.0)
window = grid.compute_visible_window(viewport)
```

## Mathematical Bounds & Invariants
- **Memory Footprint**: $O(R + C)$ auxiliary memory for 1D prefix arrays, avoiding $O(R \times C)$ full grid matrices.
- **Window Query Complexity**: $O(\log R + \log C)$ via binary search (`bisect_right`) over monotonic prefix sums.
- **Cell Geometry Lookup**: $O(1)$ offset and size resolution.
- **Zero CLS & Overscan**: Margin buffer ($K_{\text{rows}}, K_{\text{cols}}$) prevents empty flash during rapid viewport scrolling.
