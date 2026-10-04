"""
Dynamic Real-Time 2D Cell Resizing via Binary Indexed Trees (Fenwick Trees).
Enables O(log N) dynamic dimension updates and O(log N) prefix offset queries
for real-time interactive row/column resizing in high-density virtual 2D panes.
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Optional


@dataclass(frozen=True)
class Viewport2D:
    scroll_top: float
    scroll_left: float
    viewport_height: float
    viewport_width: float
    overscan_rows: int = 2
    overscan_cols: int = 2


@dataclass(frozen=True)
class VisibleWindow2D:
    start_row: int
    end_row: int
    start_col: int
    end_col: int
    offset_y: float
    offset_x: float
    total_height: float
    total_width: float
    visible_cells: int


@dataclass(frozen=True)
class CellGeometry:
    row: int
    col: int
    y: float
    x: float
    height: float
    width: float


class FenwickTree1D:
    """
    1D Binary Indexed Tree (Fenwick Tree) supporting:
    - O(log N) point update: update_size(index, new_size)
    - O(log N) prefix query: query_prefix(index) = sum of sizes[0..index-1]
    - O(log N) binary lifting / search: find_index_at_offset(offset)
    """

    def __init__(self, sizes: List[float], min_dimension: float = 1.0):
        if not sizes:
            raise ValueError("Dimension sizes list cannot be empty.")
        self.min_dimension = max(1.0, float(min_dimension))
        self.count = len(sizes)
        self.sizes = [max(self.min_dimension, float(s)) for s in sizes]
        
        # 1-indexed Fenwick tree array of size count + 1
        self.tree = [0.0] * (self.count + 1)
        self._build()

    def _build(self) -> None:
        """Linear-time O(N) tree initialization."""
        for i, val in enumerate(self.sizes):
            idx = i + 1
            self.tree[idx] += val
            parent = idx + (idx & -idx)
            if parent <= self.count:
                self.tree[parent] += self.tree[idx]

    @property
    def total_size(self) -> float:
        """Returns the total accumulated size across all elements."""
        return self.query_prefix(self.count)

    def get_size(self, index: int) -> float:
        """Returns size of element at index in O(1)."""
        if 0 <= index < self.count:
            return self.sizes[index]
        raise IndexError(f"Index {index} out of bounds (0..{self.count - 1})")

    def query_prefix(self, count: int) -> float:
        """
        Calculates cumulative sum of sizes[0 .. count - 1] in O(log N).
        count: number of elements included (0 <= count <= self.count).
        """
        if count <= 0:
            return 0.0
        idx = min(self.count, count)
        total = 0.0
        while idx > 0:
            total += self.tree[idx]
            idx -= (idx & -idx)
        return total

    def get_offset(self, index: int) -> float:
        """Returns cumulative start offset for element at `index` in O(log N)."""
        return self.query_prefix(index)

    def get_range_size(self, start_idx: int, end_idx: int) -> float:
        """Returns cumulative span between start_idx and end_idx in O(log N)."""
        s = max(0, min(self.count, start_idx))
        e = max(0, min(self.count, end_idx))
        if e <= s:
            return 0.0
        return self.query_prefix(e) - self.query_prefix(s)

    def update_size(self, index: int, new_size: float) -> float:
        """
        Dynamically updates the size of element at `index` in O(log N).
        Returns the delta applied.
        """
        if not (0 <= index < self.count):
            raise IndexError(f"Index {index} out of bounds (0..{self.count - 1})")
        
        clamped_new_size = max(self.min_dimension, float(new_size))
        old_size = self.sizes[index]
        delta = clamped_new_size - old_size
        self.sizes[index] = clamped_new_size

        # Propagate delta up the Fenwick tree
        idx = index + 1
        while idx <= self.count:
            self.tree[idx] += delta
            idx += (idx & -idx)
        return delta

    def batch_update(self, updates: Dict[int, float]) -> None:
        """Apply multiple size updates efficiently."""
        for idx, new_size in updates.items():
            self.update_size(idx, new_size)

    def find_index_at_offset(self, offset: float) -> int:
        """
        Finds the 0-based element index enclosing the given scroll offset in O(log N)
        using binary lifting on powers of two directly on the Fenwick tree.
        """
        if offset <= 0.0:
            return 0
        total = self.total_size
        if offset >= total:
            return max(0, self.count - 1)

        # Binary lifting on Fenwick tree
        idx = 0
        current_sum = 0.0
        # Determine highest power of 2 <= count
        bit_mask = 1
        while (bit_mask << 1) <= self.count:
            bit_mask <<= 1

        while bit_mask > 0:
            next_idx = idx + bit_mask
            if next_idx <= self.count:
                if current_sum + self.tree[next_idx] <= offset:
                    idx = next_idx
                    current_sum += self.tree[next_idx]
            bit_mask >>= 1

        # idx is the count of items strictly before offset
        return min(self.count - 1, idx)


class DynamicFenwick2DGrid:
    """
    Two-dimensional virtualized grid window manager with dynamic runtime
    row and column resizing powered by dual 1D Fenwick Trees.
    Allows real-time interactive user drag resizing without layout shifts (Zero CLS).
    """

    def __init__(
        self,
        row_heights: List[float],
        col_widths: List[float],
        min_row_height: float = 12.0,
        min_col_width: float = 24.0,
    ):
        self.rows_tree = FenwickTree1D(row_heights, min_dimension=min_row_height)
        self.cols_tree = FenwickTree1D(col_widths, min_dimension=min_col_width)

    @property
    def row_count(self) -> int:
        return self.rows_tree.count

    @property
    def col_count(self) -> int:
        return self.cols_tree.count

    @property
    def total_height(self) -> float:
        return self.rows_tree.total_size

    @property
    def total_width(self) -> float:
        return self.cols_tree.total_size

    def resize_row(self, row_idx: int, new_height: float) -> float:
        """Resize a specific row height dynamically in O(log R)."""
        return self.rows_tree.update_size(row_idx, new_height)

    def resize_col(self, col_idx: int, new_width: float) -> float:
        """Resize a specific column width dynamically in O(log C)."""
        return self.cols_tree.update_size(col_idx, new_width)

    def get_cell_geometry(self, row_idx: int, col_idx: int) -> CellGeometry:
        """Get absolute geometry for cell (row, col) in O(log R + log C)."""
        y = self.rows_tree.get_offset(row_idx)
        x = self.cols_tree.get_offset(col_idx)
        h = self.rows_tree.get_size(row_idx)
        w = self.cols_tree.get_size(col_idx)
        return CellGeometry(row=row_idx, col=col_idx, y=y, x=x, height=h, width=w)

    def compute_visible_window(self, viewport: Viewport2D) -> VisibleWindow2D:
        """
        Calculates the visible grid window slice for given viewport.
        Binary search / lifting runs in O(log R + log C).
        """
        # Vertical range
        top_offset = max(0.0, viewport.scroll_top)
        bottom_offset = top_offset + max(1.0, viewport.viewport_height)

        raw_start_row = self.rows_tree.find_index_at_offset(top_offset)
        raw_end_row = self.rows_tree.find_index_at_offset(bottom_offset)

        start_row = max(0, raw_start_row - viewport.overscan_rows)
        end_row = min(self.row_count, raw_end_row + 1 + viewport.overscan_rows)

        # Horizontal range
        left_offset = max(0.0, viewport.scroll_left)
        right_offset = left_offset + max(1.0, viewport.viewport_width)

        raw_start_col = self.cols_tree.find_index_at_offset(left_offset)
        raw_end_col = self.cols_tree.find_index_at_offset(right_offset)

        start_col = max(0, raw_start_col - viewport.overscan_cols)
        end_col = min(self.col_count, raw_end_col + 1 + viewport.overscan_cols)

        offset_y = self.rows_tree.get_offset(start_row)
        offset_x = self.cols_tree.get_offset(start_col)

        row_span = max(0, end_row - start_row)
        col_span = max(0, end_col - start_col)

        return VisibleWindow2D(
            start_row=start_row,
            end_row=end_row,
            start_col=start_col,
            end_col=end_col,
            offset_y=offset_y,
            offset_x=offset_x,
            total_height=self.total_height,
            total_width=self.total_width,
            visible_cells=row_span * col_span,
        )
