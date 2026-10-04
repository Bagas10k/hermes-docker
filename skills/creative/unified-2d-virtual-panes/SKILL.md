---
name: unified-2d-virtual-panes
description: "Four-quadrant 2D virtual panes and sync sticky headers."
version: 0.1.0
author: Bagas Cihuy, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [creative, ui-ux, virtualization, 2d-grid, performance]
    related_skills: [bidirectional-2d-virtual-grid, virtualized-dom-windowing]
---

# Unified 2D Virtual Panes Skill

Four-quadrant virtual layout compositing engine for dense 2D data grids (spreadsheets, matrix telemetry, financial books) ensuring synchronous sticky headers and index columns across decoupled viewport panes.

## When to Use

- Rendering massive multi-dimensional grids ($10^5+$ cells) with frozen top rows and frozen left columns.
- Eliminating cross-axis scroll desynchronization or sticky header shearing during high-frequency inertia gestures.
- Decoupling DOM hierarchy into four discrete quadrants (NW corner, NE header row, SW index column, SE virtual body) while maintaining unified pointer/wheel dispatch.
- Don't use for: Single-axis virtual lists (use `virtualized-dom-windowing`), static non-virtual tables under 100 rows.

## Architecture & Mathematical Bounds

The four-quadrant composition partitions total grid geometry $(W_{total}, H_{total})$ into:
1. **NW (North-West)**: Frozen intersection matrix ($W_{frozen} = C_{pinned} \cdot w_{col}$, $H_{frozen} = R_{pinned} \cdot h_{row}$).
2. **NE (North-East)**: Horizontal header stream ($W_{body} = W_{total} - W_{frozen}$, $H_{frozen}$), transforms $\Delta x = -scroll_x, \Delta y = 0$.
3. **SW (South-West)**: Vertical index column stream ($W_{frozen}$, $H_{body} = H_{total} - H_{frozen}$), transforms $\Delta x = 0, \Delta y = -scroll_y$.
4. **SE (South-East)**: 2D virtualized content body ($W_{body}, H_{body}$), transforms $\Delta x = -scroll_x, \Delta y = -scroll_y$.

Amdahl & Memory Bound:
- Unvirtualized DOM count: $N_{dom} = R \cdot C$. For $1,000 	imes 500$, $N_{dom} = 500,000$ elements ($pprox 120	ext{ MB}$ memory footprint, layout lockup).
- Bounded 4-quadrant slice: $N_{dom} = (R_{pinned} \cdot C_{pinned}) + (R_{pinned} \cdot C_{vis}) + (R_{vis} \cdot C_{pinned}) + (R_{vis} \cdot C_{vis}) \le 350$ nodes total, yielding steady 60 FPS and zero layout shift.

## How to Run

Execute the test suite and pane manager verification:
```bash
python3 ~/.hermes/skills/creative/unified-2d-virtual-panes/scripts/test_pane_manager.py
```

## Quick Reference

- `Unified2DVirtualPaneManager`: Core state and geometric coordinate solver.
- `scroll_to(x, y)`: Clamps input to $[0, 	ext{max}]$ and synchronizes all four quadrants.
- `get_quadrant_transforms()`: Retrieves exact hardware-accelerated CSS `translate3d` values.
- `compute_visible_range()`: Computes zero-CLS row and column bounding box with configurable overscan.
- `render_manifest()`: Generates full layout topology for virtual rendering pipeline.

## Verification

Run deterministic unit tests validating all boundary clamping, cross-quadrant coordinate alignment, and virtual node counts:
```bash
python3 -m unittest discover -s ~/.hermes/skills/creative/unified-2d-virtual-panes/scripts
```
