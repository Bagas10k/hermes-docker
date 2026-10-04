"""Keyboard Arrow Navigation and Focal Cell Recovery for Edge-Autoscrolling Virtual Grids.

Mathematical and algorithmic oracle for coordinating keyboard arrow navigation, roving tab index,
and focal cell cursor recovery during dynamic camera translations and active edge autoscroll gestures.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import math


def finite_number(*values):
    """Enforce finite numeric floats/ints without boolean traps."""
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
        raise ValueError('Finite numeric values required')


@dataclass(frozen=True)
class FocalCell:
    row: int
    col: int
    owner_id: str
    rect_world: Tuple[float, float, float, float]  # (x0, y0, x1, y1) in world px
    visible: bool


@dataclass
class KeyboardNavigationState:
    """Stateful oracle tracking roving tab index and focal cell coordinates."""
    cursor: Optional[Tuple[int, int]] = None
    focused_id: Optional[str] = None
    roving_tab_index: int = 0
    active_edge_scroll: bool = False
    viewport_rect: Tuple[float, float, float, float] = (0.0, 0.0, 600.0, 400.0)  # (cam_x, cam_y, cam_x+vw, cam_y+vh)


class FocalCellRecoveryEngine:
    """Calculates directional arrow jumps across merged cells and recovers focal cells

    when camera translation causes the active cell to drift off-screen during edge autoscroll.
    """
    def __init__(self, row_px: int = 32, col_px: int = 96, rows: int = 100, cols: int = 100):
        if any(type(v) is not int or v <= 0 for v in (row_px, col_px, rows, cols)):
            raise ValueError('Dimensions must be positive integers')
        self.row_px = row_px
        self.col_px = col_px
        self.rows = rows
        self.cols = cols
        self.merges: Dict[str, Tuple[int, int, int, int]] = {}  # id -> (r0, c0, r1, c1)
        self.cell_owners: Dict[Tuple[int, int], str] = {}

    def add_merge(self, merge_id: str, r0: int, c0: int, r1: int, c1: int):
        """Add a merged cell region with half-open bounds [r0, r1) x [c0, c1)."""
        if any(type(x) is not int for x in (r0, c0, r1, c1)):
            raise ValueError('Coordinates must be integers')
        if not (0 <= r0 < r1 <= self.rows and 0 <= c0 < c1 <= self.cols):
            raise ValueError('Invalid merge boundary coordinates')
        # Check overlaps
        for r in range(r0, r1):
            for c in range(c0, c1):
                if (r, c) in self.cell_owners:
                    raise ValueError(f'Cell ({r},{c}) overlaps with merge {self.cell_owners[(r,c)]}')
        self.merges[merge_id] = (r0, c0, r1, c1)
        for r in range(r0, r1):
            for c in range(c0, c1):
                self.cell_owners[(r, c)] = merge_id

    def get_owner(self, r: int, c: int) -> str:
        """Resolve owner identifier: either merge_id or standard 'cell-r-c'."""
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            raise IndexError('Coordinate out of grid bounds')
        return self.cell_owners.get((r, c), f'cell-{r}-{c}')

    def get_cell_bounds_world(self, r: int, c: int) -> Tuple[float, float, float, float]:
        """Compute bounding rectangle (x0, y0, x1, y1) in world pixels."""
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            raise IndexError('Coordinate out of grid bounds')
        owner = self.cell_owners.get((r, c))
        if owner and owner in self.merges:
            r0, c0, r1, c1 = self.merges[owner]
            return (c0 * self.col_px, r0 * self.row_px, c1 * self.col_px, r1 * self.row_px)
        return (c * self.col_px, r * self.row_px, (c + 1) * self.col_px, (r + 1) * self.row_px)

    def navigate_arrow(self, cursor: Tuple[int, int], direction: str) -> Tuple[int, int]:
        """Navigate arrow key across cells, stepping completely outside the current merged owner."""
        r, c = cursor
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            raise IndexError('Initial cursor out of bounds')
        dirs = {
            'ArrowRight': (0, 1),
            'ArrowLeft': (0, -1),
            'ArrowDown': (1, 0),
            'ArrowUp': (-1, 0)
        }
        if direction not in dirs:
            raise ValueError(f'Unsupported direction key: {direction}')
        dr, dc = dirs[direction]
        current_owner = self.get_owner(r, c)

        nr, nc = r + dr, c + dc
        while 0 <= nr < self.rows and 0 <= nc < self.cols:
            if self.get_owner(nr, nc) != current_owner:
                return (nr, nc)
            nr += dr
            nc += dc
        # If boundary reached, clamp to boundary of current cell or retain
        return (r, c)

    def is_visible(self, r: int, c: int, camera: Tuple[float, float], viewport: Tuple[float, float], zoom: float = 1.0) -> bool:
        """Check if any portion of cell (r, c) is inside the camera viewport."""
        finite_number(*camera, *viewport, zoom)
        if zoom <= 0 or viewport[0] <= 0 or viewport[1] <= 0:
            raise ValueError('Positive viewport dimensions and zoom required')
        cam_x, cam_y = camera
        vw, vh = viewport
        vx0, vy0 = cam_x, cam_y
        vx1, vy1 = cam_x + vw / zoom, cam_y + vh / zoom

        x0, y0, x1, y1 = self.get_cell_bounds_world(r, c)
        # Intersection test
        return not (x1 <= vx0 or x0 >= vx1 or y1 <= vy0 or y0 >= vy1)

    def recover_focal_cell(self,
                           cursor: Optional[Tuple[int, int]],
                           camera: Tuple[float, float],
                           viewport: Tuple[float, float],
                           zoom: float = 1.0,
                           edge_direction: Optional[Tuple[float, float]] = None) -> Tuple[int, int, str]:
        """Recovers an authoritative focal cell within the visible viewport during edge autoscrolling.

        If cursor is still visible, retain it.
        If cursor has drifted off-screen due to camera motion:
        - If edge_direction is given (e.g., autoscrolling right/down), snap focal cursor to the leading visible cell.
        - Otherwise, snap to the closest visible boundary cell (minimum Euclidean distance).
        Returns: (recovered_row, recovered_col, strategy_used)
        """
        finite_number(*camera, *viewport, zoom)
        if zoom <= 0 or viewport[0] <= 0 or viewport[1] <= 0:
            raise ValueError('Positive viewport dimensions and zoom required')
        cam_x, cam_y = camera
        vw, vh = viewport
        vx0, vy0 = max(0.0, cam_x), max(0.0, cam_y)
        vx1, vy1 = cam_x + vw / zoom, cam_y + vh / zoom

        # Calculate visible row/col ranges (half-open)
        r_start = max(0, int(math.floor(vy0 / self.row_px)))
        r_end = min(self.rows, int(math.ceil(vy1 / self.row_px)))
        c_start = max(0, int(math.floor(vx0 / self.col_px)))
        c_end = min(self.cols, int(math.ceil(vx1 / self.col_px)))

        if r_start >= r_end or c_start >= c_end:
            # Degenerate visible region
            r_fallback = min(self.rows - 1, max(0, r_start))
            c_fallback = min(self.cols - 1, max(0, c_start))
            return (r_fallback, c_fallback, 'clamped_fallback')

        # Check if current cursor is already visible
        if cursor is not None:
            cr, cc = cursor
            if 0 <= cr < self.rows and 0 <= cc < self.cols:
                if self.is_visible(cr, cc, camera, viewport, zoom):
                    return (cr, cc, 'retained_visible')

        # If edge_direction is provided and nonzero:
        if edge_direction is not None:
            edx, edy = edge_direction
            finite_number(edx, edy)
            # If scrolling rightwards, leading cell is rightmost visible
            target_c = c_end - 1 if edx > 0 else (c_start if edx < 0 else (cursor[1] if cursor else c_start))
            target_r = r_end - 1 if edy > 0 else (r_start if edy < 0 else (cursor[0] if cursor else r_start))
            target_c = min(c_end - 1, max(c_start, target_c))
            target_r = min(r_end - 1, max(r_start, target_r))
            return (target_r, target_c, 'edge_direction_lead')

        # Otherwise, find cell closest to original cursor
        if cursor is not None:
            cr, cc = cursor
            clamped_r = min(r_end - 1, max(r_start, cr))
            clamped_c = min(c_end - 1, max(c_start, cc))
            return (clamped_r, clamped_c, 'clamped_closest')

        # Default: top-left of visible viewport
        return (r_start, c_start, 'top_left_viewport')

    def reconcile_roving_tab_index(self, active_cursor: Optional[Tuple[int, int]], visible_cells: List[Tuple[int, int]]) -> Dict[str, int]:
        """Calculates roving tabIndex mapping:

        The active focal cell receives tabIndex = 0; all other visible cells receive tabIndex = -1.
        If no cell is focused, container receives 0.
        """
        tab_map: Dict[str, int] = {}
        active_owner = self.get_owner(*active_cursor) if active_cursor else None

        for r, c in visible_cells:
            owner = self.get_owner(r, c)
            if owner not in tab_map:
                tab_map[owner] = 0 if owner == active_owner else -1

        return tab_map
