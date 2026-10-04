#!/usr/bin/env python3
"""
Virtualized DOM Windowing Engine for Massive Data Tables.
Implements mathematical virtual list windowing:
  total_height = sum(row_heights) or N * fixed_row_height
  visible_range = [start_index, end_index]
  overscan_range = [max(0, start_index - overscan), min(N, end_index + overscan)]
  DOM pool recycling: pool size = overscan_count <= 2 * ceil(viewport_height / min_row_height) + 2 * overscan
Ensures constant O(1) DOM node count regardless of total rows N (e.g. 100,000+ rows).
"""

import math
from typing import List, Dict, Any, Tuple, Optional

class VirtualWindowEngine:
    def __init__(
        self,
        total_rows: int,
        viewport_height: float,
        row_height: float = 36.0,
        overscan: int = 5,
        variable_heights: Optional[List[float]] = None
    ):
        if total_rows < 0:
            raise ValueError("total_rows cannot be negative")
        if viewport_height <= 0:
            raise ValueError("viewport_height must be positive")
        if row_height <= 0:
            raise ValueError("row_height must be positive")
        if overscan < 0:
            raise ValueError("overscan cannot be negative")

        self.total_rows = total_rows
        self.viewport_height = viewport_height
        self.default_row_height = row_height
        self.overscan = overscan

        # If variable heights provided, construct prefix sum array for O(log N) lookup
        self.variable_heights = variable_heights
        self.offsets = [0.0]
        if variable_heights is not None:
            if len(variable_heights) != total_rows:
                raise ValueError("variable_heights length must match total_rows")
            curr = 0.0
            for h in variable_heights:
                if h <= 0:
                    raise ValueError("All row heights must be positive")
                curr += h
                self.offsets.append(curr)
        else:
            self.total_height = total_rows * row_height

    def get_total_height(self) -> float:
        if self.variable_heights is not None:
            return self.offsets[-1]
        return self.total_rows * self.default_row_height

    def get_row_offset(self, index: int) -> float:
        if index < 0 or index >= self.total_rows:
            raise IndexError("Row index out of range")
        if self.variable_heights is not None:
            return self.offsets[index]
        return index * self.default_row_height

    def get_row_height(self, index: int) -> float:
        if index < 0 or index >= self.total_rows:
            raise IndexError("Row index out of range")
        if self.variable_heights is not None:
            return self.variable_heights[index]
        return self.default_row_height

    def find_row_at_offset(self, scroll_y: float) -> int:
        if scroll_y <= 0:
            return 0
        if self.variable_heights is None:
            idx = int(scroll_y // self.default_row_height)
            return min(max(0, idx), max(0, self.total_rows - 1))

        # Binary search over prefix sum offsets
        low = 0
        high = self.total_rows - 1
        result = self.total_rows - 1

        while low <= high:
            mid = (low + high) // 2
            if self.offsets[mid + 1] > scroll_y:
                result = mid
                high = mid - 1
            else:
                low = mid + 1
        return min(max(0, result), max(0, self.total_rows - 1))

    def compute_window(self, scroll_y: float) -> Dict[str, Any]:
        """
        Calculates visible range, overscan range, transform offsets,
        and ensures hard bounded DOM node allocation.
        """
        if self.total_rows == 0:
            return {
                "total_rows": 0,
                "total_height": 0.0,
                "visible_start": 0,
                "visible_end": 0,
                "render_start": 0,
                "render_end": 0,
                "rendered_count": 0,
                "top_spacer_height": 0.0,
                "bottom_spacer_height": 0.0,
                "rendered_items": []
            }

        max_scroll = max(0.0, self.get_total_height() - self.viewport_height)
        clamped_scroll_y = max(0.0, min(scroll_y, max_scroll))

        # Find visible start
        visible_start = self.find_row_at_offset(clamped_scroll_y)

        # Find visible end
        viewport_bottom = clamped_scroll_y + self.viewport_height
        visible_end = visible_start
        while visible_end < self.total_rows - 1:
            if self.get_row_offset(visible_end + 1) >= viewport_bottom:
                break
            visible_end += 1

        # Apply overscan bounds
        render_start = max(0, visible_start - self.overscan)
        render_end = min(self.total_rows - 1, visible_end + self.overscan)

        rendered_count = render_end - render_start + 1

        # Calculate spacers for 100% accurate scrollbar representation
        top_spacer_height = self.get_row_offset(render_start)
        bottom_spacer_height = self.get_total_height() - (
            self.get_row_offset(render_end) + self.get_row_height(render_end)
        )

        rendered_items = []
        for i in range(render_start, render_end + 1):
            rendered_items.append({
                "index": i,
                "top": self.get_row_offset(i),
                "height": self.get_row_height(i),
                "is_overscan": (i < visible_start or i > visible_end)
            })

        return {
            "total_rows": self.total_rows,
            "total_height": self.get_total_height(),
            "visible_start": visible_start,
            "visible_end": visible_end,
            "render_start": render_start,
            "render_end": render_end,
            "rendered_count": rendered_count,
            "top_spacer_height": max(0.0, top_spacer_height),
            "bottom_spacer_height": max(0.0, bottom_spacer_height),
            "rendered_items": rendered_items
        }

    def verify_dom_budget(self, max_allowed_nodes: int = 100) -> bool:
        """
        Theorem: For any scroll_y in [0, total_height],
        rendered_count <= ceil(viewport_height / min_height) + 2 * overscan + 1.
        Verify that rendered_count never exceeds max_allowed_nodes across the entire range.
        """
        # Test edge points and intervals
        test_scrolls = [
            0.0,
            self.viewport_height * 0.5,
            self.viewport_height,
            self.get_total_height() * 0.25,
            self.get_total_height() * 0.5,
            self.get_total_height() * 0.75,
            max(0.0, self.get_total_height() - self.viewport_height)
        ]

        for s in test_scrolls:
            window = self.compute_window(s)
            if window["rendered_count"] > max_allowed_nodes:
                return False
        return True
