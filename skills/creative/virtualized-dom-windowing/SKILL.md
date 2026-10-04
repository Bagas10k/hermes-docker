---
name: virtualized-dom-windowing
description: Virtualize massive data tables with bounded DOM node recycling.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [virtualization, dom-recycling, high-density, performance, ui-ux]
    related_skills: [high-density-data-surfaces, zero-layout-shift-artifacts]
---

# Virtualized DOM Windowing

High-throughput virtual list and table DOM windowing engine. Keeps active DOM nodes strictly bounded ($O(1)$) even when displaying 100,000+ data rows at a steady 60 FPS.

## When to Use
- Rendering enterprise data tables with $> 1,000$ to $100,000+$ rows without memory bloat.
- Preventing browser jank and layout thrashing during fast scroll operations.
- Preserving accurate native scrollbar proportions with dynamic virtual spacers.

## Architecture & Mathematical Bounds
1. **DOM Node Budget Ceiling**:
   $$K_{\text{dom}} \le \left\lceil \frac{H_{\text{viewport}}}{H_{\text{row, min}}} \right\rceil + 2 \cdot \text{overscan} + 1$$
   Active DOM elements remain constant ($\approx 25 - 40$ nodes) regardless of whether total items $N = 1,000$ or $100,000$.
2. **Height Conservation Invariant**:
   $$H_{\text{top\_spacer}} + \sum_{i \in \text{rendered}} H_i + H_{\text{bottom\_spacer}} = H_{\text{total}}$$
3. **Lookup Complexity**:
   - Fixed height: $O(1)$ arithmetic index division.
   - Variable height: $O(\log N)$ binary search over prefix offset sums.

## Verification
- Unit test suite: `python3 /home/ubuntu/.hermes/skills/creative/virtualized-dom-windowing/scripts/test_virtual_window_engine.py` (5/5 tests pass deterministically).
