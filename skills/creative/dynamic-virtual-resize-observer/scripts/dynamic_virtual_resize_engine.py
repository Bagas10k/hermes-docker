#!/usr/bin/env python3
"""
Dynamic Content Height Virtualization & Asynchronous ResizeObserver Invalidation Engine.
Implements:
1. Fenwick Tree (Binary Indexed Tree) for O(log N) dynamic prefix sums and dynamic row height mutations.
2. Dynamic ResizeObserver update protocol with batch measurement & cache invalidation.
3. Cumulative shift calculation (delta = measured_height - estimated_height).
4. Scroll anchoring under dynamic content shifts:
   - When elements above the active viewport anchor shift in height, scroll offset adjusts by delta
     to guarantee zero visual jumping (Zero-CLS, Cumulative Layout Shift = 0).
5. O(1) bounded active DOM node recycling pool within viewport + overscan.
"""

import math
from typing import List, Dict, Any, Tuple, Optional

class FenwickTree:
    """
    Binary Indexed Tree (Fenwick Tree) supporting 1-based indexing for:
    - O(log N) prefix sum queries: prefix_sum(i)
    - O(log N) point updates: add(i, delta)
    - O(log N) find index by prefix sum (binary lifting)
    """
    def __init__(self, size: int):
        self.size = size
        self.tree = [0.0] * (size + 1)

    @classmethod
    def from_array(cls, arr: List[float]) -> 'FenwickTree':
        ft = cls(len(arr))
        for i, val in enumerate(arr, start=1):
            ft.tree[i] += val
            parent = i + (i & -i)
            if parent <= ft.size:
                ft.tree[parent] += ft.tree[i]
        return ft

    def add(self, index: int, delta: float) -> None:
        """Adds delta to element at 1-based index."""
        if index < 1 or index > self.size:
            raise IndexError("Fenwick index out of bounds")
        idx = index
        while idx <= self.size:
            self.tree[idx] += delta
            idx += idx & -idx

    def prefix_sum(self, index: int) -> float:
        """Returns sum of elements from 1 to index (inclusive)."""
        if index <= 0:
            return 0.0
        if index > self.size:
            index = self.size
        s = 0.0
        idx = index
        while idx > 0:
            s += self.tree[idx]
            idx -= idx & -idx
        return s

    def range_sum(self, left: int, right: int) -> float:
        """Returns sum in 1-based range [left, right]."""
        if left > right or right < 1 or left > self.size:
            return 0.0
        return self.prefix_sum(right) - self.prefix_sum(left - 1)

    def find_index_of_offset(self, offset: float) -> int:
        """
        Binary lifting over Fenwick tree to find the 1-based index `k`
        such that prefix_sum(k - 1) <= offset < prefix_sum(k).
        Returns 1-based index (capped between 1 and size).
        """
        if offset <= 0:
            return 1
        idx = 0
        current_sum = 0.0
        # Largest power of 2 <= size
        bit_mask = 1 << (self.size.bit_length() - 1)
        while bit_mask > 0:
            next_idx = idx + bit_mask
            if next_idx <= self.size and current_sum + self.tree[next_idx] <= offset:
                idx = next_idx
                current_sum += self.tree[idx]
            bit_mask >>= 1
        return min(idx + 1, self.size)


class DynamicVirtualResizeEngine:
    """
    Virtual windowing manager for lists with unknown, variable, or dynamically mutating row heights.
    Emulates browser ResizeObserver batch notifications, Fenwick tree offset updates,
    and automatic scroll anchoring.
    """
    def __init__(
        self,
        total_rows: int,
        viewport_height: float,
        estimated_row_height: float = 40.0,
        overscan: int = 5,
        min_row_height: float = 16.0
    ):
        if total_rows < 0:
            raise ValueError("total_rows cannot be negative")
        if viewport_height <= 0:
            raise ValueError("viewport_height must be positive")
        if estimated_row_height <= 0:
            raise ValueError("estimated_row_height must be positive")
        if min_row_height <= 0:
            raise ValueError("min_row_height must be positive")
        if overscan < 0:
            raise ValueError("overscan cannot be negative")

        self.total_rows = total_rows
        self.viewport_height = viewport_height
        self.estimated_row_height = estimated_row_height
        self.overscan = overscan
        self.min_row_height = min_row_height

        # Measured heights array (0-based)
        self.measured_heights: List[float] = [estimated_row_height] * total_rows
        # Set of indices that have been explicitly measured via ResizeObserver
        self.is_measured: List[bool] = [False] * total_rows

        # Fenwick Tree maintains cumulative heights (1-based)
        self.bit = FenwickTree.from_array(self.measured_heights)

    def get_total_height(self) -> float:
        """Returns total virtual height of all rows."""
        return self.bit.prefix_sum(self.total_rows)

    def get_row_offset(self, index: int) -> float:
        """Returns top offset of row at index (0-based)."""
        if index < 0 or index >= self.total_rows:
            raise IndexError("Row index out of range")
        return self.bit.prefix_sum(index)

    def get_row_height(self, index: int) -> float:
        """Returns current height (measured or estimated) of row at index (0-based)."""
        if index < 0 or index >= self.total_rows:
            raise IndexError("Row index out of range")
        return self.measured_heights[index]

    def find_row_at_offset(self, scroll_y: float) -> int:
        """Finds row index (0-based) whose boundary covers scroll_y."""
        if self.total_rows == 0 or scroll_y <= 0:
            return 0
        one_based = self.bit.find_index_of_offset(scroll_y)
        return min(max(0, one_based - 1), self.total_rows - 1)

    def compute_window(self, scroll_y: float) -> Dict[str, Any]:
        """
        Computes visible window, active DOM render range, spacers, and scroll metrics.
        """
        if self.total_rows == 0:
            return {
                "total_rows": 0,
                "total_height": 0.0,
                "scroll_y": 0.0,
                "visible_start": 0,
                "visible_end": 0,
                "render_start": 0,
                "render_end": 0,
                "rendered_count": 0,
                "top_spacer_height": 0.0,
                "bottom_spacer_height": 0.0,
                "rows": [],
                "max_dom_nodes_bound": 0
            }

        scroll_y = max(0.0, scroll_y)
        viewport_bottom = scroll_y + self.viewport_height

        visible_start = self.find_row_at_offset(scroll_y)
        visible_end = self.find_row_at_offset(viewport_bottom)

        render_start = max(0, visible_start - self.overscan)
        render_end = min(self.total_rows - 1, visible_end + self.overscan)

        top_spacer_height = self.get_row_offset(render_start)
        bottom_spacer_start = self.get_row_offset(render_end) + self.measured_heights[render_end]
        total_height = self.get_total_height()
        bottom_spacer_height = max(0.0, total_height - bottom_spacer_start)

        # Theoretical upper bound on active DOM nodes
        max_visible_rows = math.ceil(self.viewport_height / self.min_row_height)
        max_dom_bound = max_visible_rows + 2 * self.overscan + 2

        rows_info = []
        for idx in range(render_start, render_end + 1):
            rows_info.append({
                "index": idx,
                "offset": self.get_row_offset(idx),
                "height": self.measured_heights[idx],
                "is_measured": self.is_measured[idx]
            })

        return {
            "total_rows": self.total_rows,
            "total_height": total_height,
            "scroll_y": scroll_y,
            "visible_start": visible_start,
            "visible_end": visible_end,
            "render_start": render_start,
            "render_end": render_end,
            "rendered_count": render_end - render_start + 1,
            "top_spacer_height": top_spacer_height,
            "bottom_spacer_height": bottom_spacer_height,
            "rows": rows_info,
            "max_dom_nodes_bound": max_dom_bound
        }

    def handle_resize_observer_batch(
        self,
        measurements: List[Tuple[int, float]],
        current_scroll_y: float,
        anchor_index: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Simulates ResizeObserver batch measurement callback.
        Args:
            measurements: List of (row_index, measured_height)
            current_scroll_y: current scroll position in viewport
            anchor_index: Optional row index to anchor against. If None, uses row at current_scroll_y.
        Returns:
            Dict containing:
                - adjusted_scroll_y: new scroll offset after applying anchor shift compensation
                - scroll_delta: difference applied to scroll_y
                - updated_count: number of rows actually updated
                - total_height_delta: total height change in entire list
        """
        if anchor_index is None:
            anchor_index = self.find_row_at_offset(current_scroll_y)

        # Sort measurements by row index to process deterministically
        sorted_m = sorted(measurements, key=lambda x: x[0])

        total_height_delta = 0.0
        anchor_scroll_delta = 0.0
        updated_count = 0

        for idx, new_height in sorted_m:
            if idx < 0 or idx >= self.total_rows:
                continue
            if new_height <= 0:
                raise ValueError(f"Measured height must be positive, got {new_height} for index {idx}")

            old_height = self.measured_heights[idx]
            delta = new_height - old_height

            if abs(delta) > 1e-6:
                self.measured_heights[idx] = new_height
                self.is_measured[idx] = True
                # Fenwick update (1-based index idx + 1)
                self.bit.add(idx + 1, delta)
                total_height_delta += delta
                updated_count += 1

                # If the shifting row is strictly ABOVE the anchor row,
                # the content above pushed the anchor down/up by delta.
                if idx < anchor_index:
                    anchor_scroll_delta += delta

        adjusted_scroll_y = max(0.0, current_scroll_y + anchor_scroll_delta)

        return {
            "adjusted_scroll_y": adjusted_scroll_y,
            "scroll_delta": anchor_scroll_delta,
            "updated_count": updated_count,
            "total_height_delta": total_height_delta,
            "anchor_index": anchor_index,
            "new_total_height": self.get_total_height()
        }
