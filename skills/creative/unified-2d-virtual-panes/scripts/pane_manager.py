"""
Unified 2D Virtual Panes Engine
Provides four-quadrant layout compositing:
- Top-Left (NW): Pinned frozen corner cell
- Top-Right (NE): Sticky header row (scrolls horizontally with body)
- Bottom-Left (SW): Sticky index column (scrolls vertically with body)
- Bottom-Right (SE): 2D Virtualized body viewport (scrolls X & Y)

Features synchronous cross-quadrant scroll coupling, sub-pixel normalization,
and bounded virtual slice rendering with deterministic zero layout shift.
"""
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Optional

@dataclass
class QuadrantOffsets:
    scroll_x: float
    scroll_y: float

@dataclass
class VirtualRange:
    start_row: int
    end_row: int
    start_col: int
    end_col: int

class Unified2DVirtualPaneManager:
    def __init__(
        self,
        total_rows: int,
        total_cols: int,
        row_height: float,
        col_width: float,
        viewport_width: float,
        viewport_height: float,
        pinned_rows: int = 1,
        pinned_cols: int = 1,
        overscan: int = 2
    ):
        assert total_rows >= pinned_rows, "total_rows must be >= pinned_rows"
        assert total_cols >= pinned_cols, "total_cols must be >= pinned_cols"
        self.total_rows = total_rows
        self.total_cols = total_cols
        self.row_height = float(row_height)
        self.col_width = float(col_width)
        self.viewport_width = float(viewport_width)
        self.viewport_height = float(viewport_height)
        self.pinned_rows = pinned_rows
        self.pinned_cols = pinned_cols
        self.overscan = overscan

        # Geometric bounds
        self.frozen_width = self.pinned_cols * self.col_width
        self.frozen_height = self.pinned_rows * self.row_height
        self.body_viewport_w = max(0.0, self.viewport_width - self.frozen_width)
        self.body_viewport_h = max(0.0, self.viewport_height - self.frozen_height)

        self.body_total_w = (self.total_cols - self.pinned_cols) * self.col_width
        self.body_total_h = (self.total_rows - self.pinned_rows) * self.row_height

        self.max_scroll_x = max(0.0, self.body_total_w - self.body_viewport_w)
        self.max_scroll_y = max(0.0, self.body_total_h - self.body_viewport_h)

        # Current scroll position for body
        self.scroll_x = 0.0
        self.scroll_y = 0.0

    def scroll_to(self, x: float, y: float) -> QuadrantOffsets:
        """Clamps and synchronizes scroll state across all 4 quadrants."""
        self.scroll_x = max(0.0, min(self.max_scroll_x, float(x)))
        self.scroll_y = max(0.0, min(self.max_scroll_y, float(y)))
        return self.get_quadrant_offsets()

    def scroll_by(self, delta_x: float, delta_y: float) -> QuadrantOffsets:
        return self.scroll_to(self.scroll_x + delta_x, self.scroll_y + delta_y)

    def get_quadrant_offsets(self) -> QuadrantOffsets:
        return QuadrantOffsets(scroll_x=self.scroll_x, scroll_y=self.scroll_y)

    def get_quadrant_transforms(self) -> Dict[str, Dict[str, float]]:
        """
        Returns exact translation values for each quadrant container:
        - NW: fixed (0, 0)
        - NE: translated X (-scroll_x, 0)
        - SW: translated Y (0, -scroll_y)
        - SE: translated X & Y (-scroll_x, -scroll_y)
        """
        return {
            "NW": {"translate_x": 0.0, "translate_y": 0.0},
            "NE": {"translate_x": -self.scroll_x, "translate_y": 0.0},
            "SW": {"translate_x": 0.0, "translate_y": -self.scroll_y},
            "SE": {"translate_x": -self.scroll_x, "translate_y": -self.scroll_y}
        }

    def compute_visible_range(self) -> VirtualRange:
        """
        Computes visible slice range in the unpinned body grid (0-indexed relative to body).
        """
        if self.body_total_h == 0 or self.body_total_w == 0:
            return VirtualRange(0, 0, 0, 0)

        # Row indices
        start_row = int(self.scroll_y // self.row_height)
        end_row = int((self.scroll_y + self.body_viewport_h) // self.row_height)
        start_row = max(0, start_row - self.overscan)
        end_row = min(self.total_rows - self.pinned_rows - 1, end_row + self.overscan)

        # Col indices
        start_col = int(self.scroll_x // self.col_width)
        end_col = int((self.scroll_x + self.body_viewport_w) // self.col_width)
        start_col = max(0, start_col - self.overscan)
        end_col = min(self.total_cols - self.pinned_cols - 1, end_col + self.overscan)

        return VirtualRange(
            start_row=start_row,
            end_row=max(start_row, end_row),
            start_col=start_col,
            end_col=max(start_col, end_col)
        )

    def render_manifest(self) -> Dict[str, Any]:
        """
        Generates virtual composite manifest detailing cell counts and layout geometry.
        """
        vr = self.compute_visible_range()
        body_rows = (vr.end_row - vr.start_row + 1)
        body_cols = (vr.end_col - vr.start_col + 1)
        body_cells = body_rows * body_cols

        return {
            "geometry": {
                "frozen_width": self.frozen_width,
                "frozen_height": self.frozen_height,
                "body_viewport_w": self.body_viewport_w,
                "body_viewport_h": self.body_viewport_h,
                "max_scroll_x": self.max_scroll_x,
                "max_scroll_y": self.max_scroll_y
            },
            "quadrant_cells": {
                "NW": self.pinned_rows * self.pinned_cols,
                "NE": self.pinned_rows * body_cols,
                "SW": body_rows * self.pinned_cols,
                "SE": body_cells
            },
            "virtual_range": {
                "body_rows": (vr.start_row, vr.end_row),
                "body_cols": (vr.start_col, vr.end_col)
            },
            "offsets": self.get_quadrant_offsets().__dict__,
            "transforms": self.get_quadrant_transforms()
        }
