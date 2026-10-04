"""Frozen pane manager and dual-axis virtualization integrating integer R-tree span queries."""
import sqlite3
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Optional

@dataclass
class QuadrantWindow:
    name: str             # "NW", "NE", "SW", "SE"
    r0: int               # half-open row start
    r1: int               # half-open row end
    c0: int               # half-open col start
    c1: int               # half-open col end
    translate_x: float    # css translate3d x
    translate_y: float    # css translate3d y
    is_frozen_x: bool
    is_frozen_y: bool

@dataclass
class PaneSpanItem:
    id: int
    anchor: List[int]     # [r0, c0]
    bounds: List[int]     # [r0, c0, r1, c1]
    clip: List[int]       # [clipped_r0, clipped_c0, clipped_r1, clipped_c1]
    quadrant: str         # "NW", "NE", "SW", "SE"
    crosses_boundary: bool

class FrozenSpanGridManager:
    """
    Manages dual-axis frozen panes (NW, NE, SW, SE) coupled with an in-memory
    integer R-Tree index for merged cells with deterministic boundary clipping.
    """
    def __init__(
        self,
        total_rows: int,
        total_cols: int,
        row_height: float,
        col_width: float,
        viewport_width: float,
        viewport_height: float,
        frozen_rows: int = 1,
        frozen_cols: int = 1,
        overscan: int = 2
    ):
        if any(type(n) is not int or not 0 < n < 2**31 for n in (total_rows, total_cols)):
            raise ValueError("Grid dimensions must be positive signed 32-bit integers")
        if any(type(n) is not int or n < 0 for n in (frozen_rows, frozen_cols)):
            raise ValueError("Frozen rows and cols must be non-negative integers")
        if frozen_rows > total_rows or frozen_cols > total_cols:
            raise ValueError("Frozen dimensions cannot exceed total grid dimensions")
        if row_height <= 0 or col_width <= 0:
            raise ValueError("Row height and col width must be positive numbers")
        if viewport_width <= 0 or viewport_height <= 0:
            raise ValueError("Viewport dimensions must be positive numbers")

        self.total_rows = total_rows
        self.total_cols = total_cols
        self.row_height = float(row_height)
        self.col_width = float(col_width)
        self.viewport_width = float(viewport_width)
        self.viewport_height = float(viewport_height)
        self.frozen_rows = frozen_rows
        self.frozen_cols = frozen_cols
        self.overscan = overscan

        # Geometry calculations
        self.frozen_width = self.frozen_cols * self.col_width
        self.frozen_height = self.frozen_rows * self.row_height
        self.body_viewport_w = max(0.0, self.viewport_width - self.frozen_width)
        self.body_viewport_h = max(0.0, self.viewport_height - self.frozen_height)

        self.body_total_w = (self.total_cols - self.frozen_cols) * self.col_width
        self.body_total_h = (self.total_rows - self.frozen_rows) * self.row_height

        self.max_scroll_x = max(0.0, self.body_total_w - self.body_viewport_w)
        self.max_scroll_y = max(0.0, self.body_total_h - self.body_viewport_h)

        self.scroll_x = 0.0
        self.scroll_y = 0.0

        # In-memory SQLite R-Tree index for merged cells
        self.db = sqlite3.connect(":memory:")
        self.db.execute("CREATE VIRTUAL TABLE spans USING rtree_i32(id, r0, r1, c0, c1)")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self):
        if self.db:
            self.db.close()
            self.db = None

    def _validate_coords(self, r0: int, c0: int, r1: int, c1: int):
        if any(type(n) is not int for n in (r0, c0, r1, c1)):
            raise ValueError("Coordinates must be integers, not booleans or floats")
        if not (0 <= r0 <= r1 <= self.total_rows and 0 <= c0 <= c1 <= self.total_cols):
            raise ValueError("Coordinates out of bounds or reversed")

    def add_span(self, ident: int, r0: int, c0: int, r1: int, c1: int):
        """Adds a merged cell rectangle [r0, c0, r1, c1) to the spatial R-Tree index."""
        self._validate_coords(r0, c0, r1, c1)
        if type(ident) is not int or not 0 <= ident < 2**63:
            raise ValueError("ID must be a non-negative signed 64-bit integer")
        if r0 == r1 or c0 == c1:
            raise ValueError("Empty merged cell span")

        with self.db:
            if self.db.execute("SELECT 1 FROM spans WHERE id = ?", (ident,)).fetchone():
                raise ValueError(f"Duplicate span ID: {ident}")
            # Check overlap
            hits = self.db.execute(
                "SELECT id FROM spans WHERE r0 < ? AND r1 > ? AND c0 < ? AND c1 > ?",
                (r1, r0, c1, c0)
            ).fetchall()
            if hits:
                raise ValueError("Overlapping merged cell span")
            self.db.execute("INSERT INTO spans VALUES (?, ?, ?, ?, ?)", (ident, r0, r1, c0, c1))

    def scroll_to(self, x: float, y: float):
        """Synchronously updates scroll offset with hard boundary clamping."""
        self.scroll_x = max(0.0, min(self.max_scroll_x, float(x)))
        self.scroll_y = max(0.0, min(self.max_scroll_y, float(y)))

    def get_quadrant_windows(self) -> Dict[str, QuadrantWindow]:
        """
        Computes the active bounding box [r0, r1) x [c0, c1) for all 4 quadrants:
        - NW: [0, frozen_rows) x [0, frozen_cols) (frozen static)
        - NE: [0, frozen_rows) x [body_c0, body_c1) (frozen Y, scroll X)
        - SW: [body_r0, body_r1) x [0, frozen_cols) (frozen X, scroll Y)
        - SE: [body_r0, body_r1) x [body_c0, body_c1) (virtual body)
        """
        # Calculate active body visible ranges
        if self.body_total_h > 0:
            rel_r0 = int(self.scroll_y // self.row_height)
            rel_r1 = int((self.scroll_y + self.body_viewport_h) // self.row_height) + 1
            rel_r0 = max(0, rel_r0 - self.overscan)
            rel_r1 = min(self.total_rows - self.frozen_rows, rel_r1 + self.overscan)
        else:
            rel_r0, rel_r1 = 0, 0

        if self.body_total_w > 0:
            rel_c0 = int(self.scroll_x // self.col_width)
            rel_c1 = int((self.scroll_x + self.body_viewport_w) // self.col_width) + 1
            rel_c0 = max(0, rel_c0 - self.overscan)
            rel_c1 = min(self.total_cols - self.frozen_cols, rel_c1 + self.overscan)
        else:
            rel_c0, rel_c1 = 0, 0

        body_r0 = self.frozen_rows + rel_r0
        body_r1 = self.frozen_rows + rel_r1
        body_c0 = self.frozen_cols + rel_c0
        body_c1 = self.frozen_cols + rel_c1

        return {
            "NW": QuadrantWindow(
                name="NW",
                r0=0, r1=self.frozen_rows,
                c0=0, c1=self.frozen_cols,
                translate_x=0.0, translate_y=0.0,
                is_frozen_x=True, is_frozen_y=True
            ),
            "NE": QuadrantWindow(
                name="NE",
                r0=0, r1=self.frozen_rows,
                c0=body_c0, c1=body_c1,
                translate_x=-self.scroll_x, translate_y=0.0,
                is_frozen_x=False, is_frozen_y=True
            ),
            "SW": QuadrantWindow(
                name="SW",
                r0=body_r0, r1=body_r1,
                c0=0, c1=self.frozen_cols,
                translate_x=0.0, translate_y=-self.scroll_y,
                is_frozen_x=True, is_frozen_y=False
            ),
            "SE": QuadrantWindow(
                name="SE",
                r0=body_r0, r1=body_r1,
                c0=body_c0, c1=body_c1,
                translate_x=-self.scroll_x, translate_y=-self.scroll_y,
                is_frozen_x=False, is_frozen_y=False
            )
        }

    def query_quadrant_spans(self, quadrant_name: str) -> List[PaneSpanItem]:
        """
        Executes spatial R-tree query against a specific quadrant's window
        and calculates deterministic intersection clipping and boundary crossing flags.
        """
        windows = self.get_quadrant_windows()
        if quadrant_name not in windows:
            raise ValueError(f"Invalid quadrant name: {quadrant_name}")

        win = windows[quadrant_name]
        if win.r0 >= win.r1 or win.c0 >= win.c1:
            return []

        hits = self.db.execute(
            "SELECT id, r0, r1, c0, c1 FROM spans "
            "WHERE r0 < ? AND r1 > ? AND c0 < ? AND c1 > ? ORDER BY id",
            (win.r1, win.r0, win.c1, win.c0)
        ).fetchall()

        results = []
        for ident, r0, r1, c0, c1 in hits:
            # Check if span crosses the frozen boundary
            crosses = (
                (r0 < self.frozen_rows < r1) or
                (c0 < self.frozen_cols < c1)
            )
            # Clip span to current quadrant window
            clip = [
                max(r0, win.r0),
                max(c0, win.c0),
                min(r1, win.r1),
                min(c1, win.c1)
            ]
            results.append(PaneSpanItem(
                id=ident,
                anchor=[r0, c0],
                bounds=[r0, c0, r1, c1],
                clip=clip,
                quadrant=quadrant_name,
                crosses_boundary=crosses
            ))
        return results

    def query_all_visible_spans(self) -> Dict[str, List[PaneSpanItem]]:
        """Queries visible spans across all 4 quadrants simultaneously."""
        return {q: self.query_quadrant_spans(q) for q in ("NW", "NE", "SW", "SE")}

    def compute_render_manifest(self) -> Dict[str, Any]:
        """
        Produces complete deterministic composite layout manifest for virtual rendering,
        combining quadrant geometries, transform vectors, active cell counts, and merged spans.
        """
        windows = self.get_quadrant_windows()
        spans_by_quadrant = self.query_all_visible_spans()

        quadrant_summary = {}
        for q_name, win in windows.items():
            cell_count = (win.r1 - win.r0) * (win.c1 - win.c0)
            quadrant_summary[q_name] = {
                "rows": [win.r0, win.r1],
                "cols": [win.c0, win.c1],
                "cell_count": cell_count,
                "span_count": len(spans_by_quadrant[q_name]),
                "transforms": {"x": win.translate_x, "y": win.translate_y},
                "is_frozen": {"x": win.is_frozen_x, "y": win.is_frozen_y}
            }

        total_nodes = sum(q["cell_count"] for q in quadrant_summary.values())

        return {
            "geometry": {
                "frozen_width": self.frozen_width,
                "frozen_height": self.frozen_height,
                "body_viewport_w": self.body_viewport_w,
                "body_viewport_h": self.body_viewport_h,
                "scroll_x": self.scroll_x,
                "scroll_y": self.scroll_y,
                "max_scroll_x": self.max_scroll_x,
                "max_scroll_y": self.max_scroll_y
            },
            "quadrants": quadrant_summary,
            "total_virtual_nodes": total_nodes,
            "spans": {
                q: [
                    {
                        "id": s.id,
                        "anchor": s.anchor,
                        "bounds": s.bounds,
                        "clip": s.clip,
                        "crosses_boundary": s.crosses_boundary
                    }
                    for s in items
                ]
                for q, items in spans_by_quadrant.items()
            }
        }
