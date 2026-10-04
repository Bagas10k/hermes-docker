"""
Prefix-Sum Variable Dimension Virtual 2D Grid Indexer.
Provides O(1) interval measurement via 1D prefix sums and O(log N) bisect coordinate lookup
for non-uniform variable row heights and column widths in high-density virtual 2D panes.
"""

from bisect import bisect_right
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Optional


@dataclass(frozen=True)
class Virtual2DViewport:
    scroll_top: float
    scroll_left: float
    viewport_height: float
    viewport_width: float
    overscan_rows: int = 2
    overscan_cols: int = 2


@dataclass(frozen=True)
class GridWindowRange:
    start_row: int
    end_row: int
    start_col: int
    end_col: int
    row_offset: float
    col_offset: float
    total_height: float
    total_width: float
    visible_cell_count: int


class VariableDimensionIndexer:
    """
    1D cumulative prefix sum indexer for variable-size discrete intervals.
    prefix_sums[i] = sum(sizes[0] ... sizes[i-1]), with prefix_sums[0] = 0.
    """

    def __init__(self, sizes: List[float], min_dimension: float = 1.0):
        if not sizes:
            raise ValueError("Dimension sizes list cannot be empty.")
        self.min_dimension = max(1.0, float(min_dimension))
        self.sizes = [max(self.min_dimension, float(s)) for s in sizes]
        self.count = len(self.sizes)
        
        # Build cumulative prefix sum array of length N + 1
        self.prefix_sums = [0.0] * (self.count + 1)
        for i, s in enumerate(self.sizes):
            self.prefix_sums[i + 1] = self.prefix_sums[i] + s

    @property
    def total_size(self) -> float:
        return self.prefix_sums[-1]

    def get_dimension(self, index: int) -> float:
        if 0 <= index < self.count:
            return self.sizes[index]
        raise IndexError(f"Index {index} out of bounds (0..{self.count - 1})")

    def get_offset(self, index: int) -> float:
        """Return cumulative start offset for element `index` in O(1)."""
        idx = max(0, min(self.count, index))
        return self.prefix_sums[idx]

    def get_range_size(self, start_idx: int, end_idx: int) -> float:
        """Return cumulative distance between start_idx and end_idx in O(1)."""
        s = max(0, min(self.count, start_idx))
        e = max(0, min(self.count, end_idx))
        if e <= s:
            return 0.0
        return self.prefix_sums[e] - self.prefix_sums[s]

    def find_index_at_offset(self, offset: float) -> int:
        """
        Binary search the index enclosing the given scroll offset in O(log N).
        Returns integer index in range [0, count - 1].
        """
        if offset <= 0.0:
            return 0
        if offset >= self.total_size:
            return max(0, self.count - 1)

        # bisect_right on prefix_sums:
        # prefix_sums[0] = 0, prefix_sums[1] = size[0], ...
        # For offset in [prefix_sums[k], prefix_sums[k+1]), bisect_right returns k + 1.
        idx = bisect_right(self.prefix_sums, offset) - 1
        return max(0, min(self.count - 1, idx))


class Variable2DVirtualGrid:
    """
    Two-dimensional virtualized grid window manager with variable row heights
    and variable column widths. Computes visible slices in O(log R + log C).
    """

    def __init__(
        self,
        row_heights: List[float],
        col_widths: List[float],
        min_cell_size: float = 8.0,
    ):
        self.row_indexer = VariableDimensionIndexer(row_heights, min_dimension=min_cell_size)
        self.col_indexer = VariableDimensionIndexer(col_widths, min_dimension=min_cell_size)

    @property
    def total_height(self) -> float:
        return self.row_indexer.total_size

    @property
    def total_width(self) -> float:
        return self.col_indexer.total_size

    @property
    def row_count(self) -> int:
        return self.row_indexer.count

    @property
    def col_count(self) -> int:
        return self.col_indexer.count

    def compute_visible_window(self, viewport: Virtual2DViewport) -> GridWindowRange:
        """
        Calculates visible range of rows and columns with overscan padding.
        Time complexity: O(log R + log C)
        """
        # Clamp scroll coordinates
        st = max(0.0, min(self.total_height - 1.0, viewport.scroll_top))
        sl = max(0.0, min(self.total_width - 1.0, viewport.scroll_left))

        # Bottom-right bounds
        bottom_offset = st + max(1.0, viewport.viewport_height)
        right_offset = sl + max(1.0, viewport.viewport_width)

        # Binary search visible window bounds
        first_row = self.row_indexer.find_index_at_offset(st)
        last_row = self.row_indexer.find_index_at_offset(bottom_offset)

        first_col = self.col_indexer.find_index_at_offset(sl)
        last_col = self.col_indexer.find_index_at_offset(right_offset)

        # Apply overscan padding
        start_row = max(0, first_row - viewport.overscan_rows)
        end_row = min(self.row_count, last_row + 1 + viewport.overscan_rows)

        start_col = max(0, first_col - viewport.overscan_cols)
        end_col = min(self.col_count, last_col + 1 + viewport.overscan_cols)

        # Cumulative physical start offsets for absolute CSS positioning
        row_offset = self.row_indexer.get_offset(start_row)
        col_offset = self.col_indexer.get_offset(start_col)

        cell_count = (end_row - start_row) * (end_col - start_col)

        return GridWindowRange(
            start_row=start_row,
            end_row=end_row,
            start_col=start_col,
            end_col=end_col,
            row_offset=row_offset,
            col_offset=col_offset,
            total_height=self.total_height,
            total_width=self.total_width,
            visible_cell_count=cell_count,
        )

    def get_cell_geometry(self, row: int, col: int) -> Dict[str, float]:
        """
        Return top, left, height, and width for cell at (row, col) in O(1).
        """
        if not (0 <= row < self.row_count and 0 <= col < self.col_count):
            raise IndexError(f"Cell ({row}, {col}) out of grid bounds.")

        top = self.row_indexer.get_offset(row)
        height = self.row_indexer.get_dimension(row)
        left = self.col_indexer.get_offset(col)
        width = self.col_indexer.get_dimension(col)

        return {
            "top": top,
            "left": left,
            "height": height,
            "width": width,
            "bottom": top + height,
            "right": left + width,
        }
