"""Modifier Key Range Selection (Shift+Arrow) & Boundary Jumps (Ctrl+Arrow) Under Active Virtual Edge Autoscroll.

Algorithmic and mathematical oracle arbitrating continuous anchor-lead selection boundaries,
discrete modifier keystroke combinations (Shift+Arrow, Ctrl/Cmd+Arrow, Ctrl+Shift+Arrow),
and focal recovery synchronization during dynamic camera translations and active edge autoscroll gestures.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
import math


def finite_number(*values):
    """Enforce finite numeric floats/ints without boolean traps."""
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
        raise ValueError('Finite numeric values required')


@dataclass(frozen=True)
class CellRange:
    """Normalized half-open or inclusive cell bounding rectangle.

    r0 <= r <= r1, c0 <= c <= c1 (inclusive bounds).
    """
    r0: int
    c0: int
    r1: int
    c1: int

    def __post_init__(self):
        if any(type(x) is not int for x in (self.r0, self.c0, self.r1, self.c1)):
            raise ValueError('Range coordinates must be integers')
        if self.r0 > self.r1 or self.c0 > self.c1:
            raise ValueError('Normalized order required: r0 <= r1 and c0 <= c1')

    def contains(self, r: int, c: int) -> bool:
        return self.r0 <= r <= self.r1 and self.c0 <= c <= self.c1

    def cell_count(self) -> int:
        return (self.r1 - self.r0 + 1) * (self.c1 - self.c0 + 1)


@dataclass
class ModifierSelectionState:
    """Stateful selection model tracking anchor cell, lead focal cursor, and active range."""
    anchor: Tuple[int, int]
    lead: Tuple[int, int]
    is_range_active: bool = False
    active_edge_scroll: bool = False

    @property
    def bounding_box(self) -> CellRange:
        r0 = min(self.anchor[0], self.lead[0])
        r1 = max(self.anchor[0], self.lead[0])
        c0 = min(self.anchor[1], self.lead[1])
        c1 = max(self.anchor[1], self.lead[1])
        return CellRange(r0, c0, r1, c1)


class ModifierRangeSelectionEngine:
    """Orchestrates Shift+Arrow range expansions, Ctrl+Arrow contiguous/empty data jumps,

    and continuous selection bounding reconciliation during active edge autoscroll.
    """
    def __init__(self,
                 row_px: int = 32,
                 col_px: int = 96,
                 rows: int = 100,
                 cols: int = 100,
                 data_matrix: Optional[Dict[Tuple[int, int], Any]] = None):
        if any(type(v) is not int or v <= 0 for v in (row_px, col_px, rows, cols)):
            raise ValueError('Dimensions must be positive integers')
        self.row_px = row_px
        self.col_px = col_px
        self.rows = rows
        self.cols = cols
        self.data_matrix: Set[Tuple[int, int]] = set()
        if data_matrix:
            for (r, c), val in data_matrix.items():
                if val is not None and val != '':
                    self.data_matrix.add((r, c))

        self.merges: Dict[str, Tuple[int, int, int, int]] = {}  # id -> (r0, c0, r1, c1)
        self.cell_owners: Dict[Tuple[int, int], str] = {}

    def set_cell_data(self, r: int, c: int, has_data: bool):
        """Set whether cell (r, c) contains populated data for boundary jumping."""
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            raise IndexError('Coordinate out of grid bounds')
        if has_data:
            self.data_matrix.add((r, c))
        else:
            self.data_matrix.discard((r, c))

    def has_data(self, r: int, c: int) -> bool:
        return (r, c) in self.data_matrix

    def add_merge(self, merge_id: str, r0: int, c0: int, r1: int, c1: int):
        """Add a merged cell region with half-open bounds [r0, r1) x [c0, c1)."""
        if any(type(x) is not int for x in (r0, c0, r1, c1)):
            raise ValueError('Coordinates must be integers')
        if not (0 <= r0 < r1 <= self.rows and 0 <= c0 < c1 <= self.cols):
            raise ValueError('Invalid merge boundary coordinates')
        for r in range(r0, r1):
            for c in range(c0, c1):
                if (r, c) in self.cell_owners:
                    raise ValueError(f'Cell ({r},{c}) overlaps with merge {self.cell_owners[(r,c)]}')
        self.merges[merge_id] = (r0, c0, r1, c1)
        for r in range(r0, r1):
            for c in range(c0, c1):
                self.cell_owners[(r, c)] = merge_id

    def get_owner(self, r: int, c: int) -> str:
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            raise IndexError('Coordinate out of grid bounds')
        return self.cell_owners.get((r, c), f'cell-{r}-{c}')

    def get_cell_bounds_world(self, r: int, c: int) -> Tuple[float, float, float, float]:
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            raise IndexError('Coordinate out of grid bounds')
        owner = self.cell_owners.get((r, c))
        if owner and owner in self.merges:
            r0, c0, r1, c1 = self.merges[owner]
            return (c0 * self.col_px, r0 * self.row_px, c1 * self.col_px, r1 * self.row_px)
        return (c * self.col_px, r * self.row_px, (c + 1) * self.col_px, (r + 1) * self.row_px)

    def navigate_step(self,
                      current: Tuple[int, int],
                      direction: str,
                      ctrl: bool = False) -> Tuple[int, int]:
        """Calculates destination cell after single arrow step or Ctrl boundary jump."""
        r, c = current
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            raise IndexError('Current cell out of bounds')

        dirs = {
            'ArrowRight': (0, 1),
            'ArrowLeft': (0, -1),
            'ArrowDown': (1, 0),
            'ArrowUp': (-1, 0)
        }
        if direction not in dirs:
            raise ValueError(f'Unsupported direction: {direction}')
        dr, dc = dirs[direction]

        if not ctrl:
            # Step outside current merged cell
            current_owner = self.get_owner(r, c)
            nr, nc = r + dr, c + dc
            while 0 <= nr < self.rows and 0 <= nc < self.cols:
                if self.get_owner(nr, nc) != current_owner:
                    return (nr, nc)
                nr += dr
                nc += dc
            return (r, c)  # Reached grid boundary

        # Ctrl+Arrow: Jump along data cluster or boundary
        return self._jump_boundary(r, c, dr, dc)

    def _jump_boundary(self, r: int, c: int, dr: int, dc: int) -> Tuple[int, int]:
        """Excel-standard boundary jumping:

        1. If currently in a data cell and next cell is data: jump to the last contiguous data cell in that run.
        2. If currently in a data cell and next cell is empty: jump across empty cells to the next data cell (or grid edge).
        3. If currently in an empty cell: jump across empty cells to the first encountered data cell (or grid edge).
        """
        nr, nc = r + dr, c + dc
        if not (0 <= nr < self.rows and 0 <= nc < self.cols):
            return (r, c)  # Already at edge

        curr_has_data = self.has_data(r, c)
        next_has_data = self.has_data(nr, nc)

        if curr_has_data and next_has_data:
            # Run of contiguous data cells -> jump to end of run
            last_r, last_c = nr, nc
            while True:
                step_r, step_c = last_r + dr, last_c + dc
                if 0 <= step_r < self.rows and 0 <= step_c < self.cols and self.has_data(step_r, step_c):
                    last_r, last_c = step_r, step_c
                else:
                    break
            return (last_r, last_c)

        if curr_has_data and not next_has_data:
            # Current has data, next is empty -> skip empty cells until next data cell, or grid boundary
            last_r, last_c = nr, nc
            while 0 <= last_r < self.rows and 0 <= last_c < self.cols:
                if self.has_data(last_r, last_c):
                    return (last_r, last_c)
                next_step_r, next_step_c = last_r + dr, last_c + dc
                if not (0 <= next_step_r < self.rows and 0 <= next_step_c < self.cols):
                    return (last_r, last_c)  # Grid boundary
                last_r, last_c = next_step_r, next_step_c
            return (last_r, last_c)

        # Current is empty: seek first data cell or boundary
        last_r, last_c = nr, nc
        while 0 <= last_r < self.rows and 0 <= last_c < self.cols:
            if self.has_data(last_r, last_c):
                return (last_r, last_c)
            next_step_r, next_step_c = last_r + dr, last_c + dc
            if not (0 <= next_step_r < self.rows and 0 <= next_step_c < self.cols):
                return (last_r, last_c)  # Hit edge
            last_r, last_c = next_step_r, next_step_c
        return (last_r, last_c)

    def handle_keyboard_selection(self,
                                  state: ModifierSelectionState,
                                  direction: str,
                                  shift: bool = False,
                                  ctrl: bool = False) -> ModifierSelectionState:
        """Processes keystroke with modifiers:

        - Plain Arrow: collapses selection to target cell (anchor = lead = target).
        - Shift+Arrow: keeps existing anchor, updates lead cursor to target (range expanded).
        - Ctrl+Arrow: jumps to cluster boundary, collapses selection.
        - Ctrl+Shift+Arrow: jumps to cluster boundary, expands selection from anchor to target.
        """
        target = self.navigate_step(state.lead, direction, ctrl=ctrl)
        if shift:
            # Retain anchor, update lead
            return ModifierSelectionState(
                anchor=state.anchor,
                lead=target,
                is_range_active=(state.anchor != target),
                active_edge_scroll=state.active_edge_scroll
            )
        else:
            # Collapse selection to new target
            return ModifierSelectionState(
                anchor=target,
                lead=target,
                is_range_active=False,
                active_edge_scroll=state.active_edge_scroll
            )

    def reconcile_autoscroll_selection(self,
                                       state: ModifierSelectionState,
                                       camera: Tuple[float, float],
                                       viewport: Tuple[float, float],
                                       zoom: float = 1.0,
                                       edge_direction: Optional[Tuple[float, float]] = None) -> Tuple[ModifierSelectionState, str]:
        """Synchronizes range selection boundary when continuous edge autoscroll is actively running.

        If edge_direction is active and range selection is active (Shift held or mouse dragging):
        - Anchor remains anchored in world space.
        - Lead cursor follows the camera autoscroll leading boundary, expanding the active range.
        If camera moves passively:
        - Clamps lead cursor if drifted off-screen.
        Returns updated state and strategy description.
        """
        finite_number(*camera, *viewport, zoom)
        if zoom <= 0 or viewport[0] <= 0 or viewport[1] <= 0:
            raise ValueError('Positive viewport dimensions and zoom required')

        cam_x, cam_y = camera
        vw, vh = viewport
        vx0, vy0 = max(0.0, cam_x), max(0.0, cam_y)
        vx1, vy1 = cam_x + vw / zoom, cam_y + vh / zoom

        r_start = max(0, int(math.floor(vy0 / self.row_px)))
        r_end = min(self.rows, int(math.ceil(vy1 / self.row_px)))
        c_start = max(0, int(math.floor(vx0 / self.col_px)))
        c_end = min(self.cols, int(math.ceil(vx1 / self.col_px)))

        if r_start >= r_end or c_start >= c_end:
            return (state, 'noop_degenerate')

        lead_r, lead_c = state.lead
        cell_x0, cell_y0, cell_x1, cell_y1 = self.get_cell_bounds_world(lead_r, lead_c)
        is_lead_visible = not (cell_x1 <= vx0 or cell_x0 >= vx1 or cell_y1 <= vy0 or cell_y0 >= vy1)

        if is_lead_visible and not edge_direction:
            return (state, 'lead_retained')

        if edge_direction is not None:
            edx, edy = edge_direction
            finite_number(edx, edy)
            # Leading edge selection expansion
            target_c = c_end - 1 if edx > 0 else (c_start if edx < 0 else lead_c)
            target_r = r_end - 1 if edy > 0 else (r_start if edy < 0 else lead_r)
            target_c = min(c_end - 1, max(c_start, target_c))
            target_r = min(r_end - 1, max(r_start, target_r))

            new_lead = (target_r, target_c)
            new_state = ModifierSelectionState(
                anchor=state.anchor,
                lead=new_lead,
                is_range_active=(state.anchor != new_lead),
                active_edge_scroll=True
            )
            return (new_state, 'lead_edge_expanded')

        # Passive camera motion with off-screen lead cursor: clamp lead to visible edge
        clamped_r = min(r_end - 1, max(r_start, lead_r))
        clamped_c = min(c_end - 1, max(c_start, lead_c))
        new_lead = (clamped_r, clamped_c)
        new_state = ModifierSelectionState(
            anchor=state.anchor,
            lead=new_lead,
            is_range_active=(state.anchor != new_lead),
            active_edge_scroll=False
        )
        return (new_state, 'lead_clamped_closest')

    def get_selected_cells(self, state: ModifierSelectionState) -> List[Tuple[int, int]]:
        """Returns all discrete cell coordinates within the active selection range."""
        box = state.bounding_box
        cells = []
        for r in range(box.r0, box.r1 + 1):
            for c in range(box.c0, box.c1 + 1):
                cells.append((r, c))
        return cells
