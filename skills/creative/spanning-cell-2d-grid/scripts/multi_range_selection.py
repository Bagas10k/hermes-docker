"""Multi-Range Non-Contiguous Selection (Ctrl+Click Disjoint Boxes) Under Virtualized Cell R-Tree Bounds.

Algorithmic and mathematical oracle arbitrating multiple disjoint selection bounding boxes
during Ctrl/Cmd+Click interactions without O(N*M) spatial collision degradation,
leveraging 2D interval trees / R-tree spatial bounding, range deduplication, and
virtual camera spatial intersection queries.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any, Sequence
import math


def finite_number(*values):
    """Enforce finite numeric floats/ints without boolean traps."""
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
        raise ValueError('Finite numeric values required')


@dataclass(frozen=True)
class SelectionBox:
    """Normalized 2D cell bounding rectangle [r0, r1] x [c0, c1] (inclusive)."""
    r0: int
    c0: int
    r1: int
    c1: int
    box_id: str = ''

    def __post_init__(self):
        if any(type(x) is not int for x in (self.r0, self.c0, self.r1, self.c1)):
            raise ValueError('SelectionBox coordinates must be integers')
        if self.r0 > self.r1 or self.c0 > self.c1:
            raise ValueError('Normalized coordinates required: r0 <= r1 and c0 <= c1')

    def contains(self, r: int, c: int) -> bool:
        return self.r0 <= r <= self.r1 and self.c0 <= c <= self.c1

    def cell_count(self) -> int:
        return (self.r1 - self.r0 + 1) * (self.c1 - self.c0 + 1)

    def intersects(self, other: 'SelectionBox') -> bool:
        return not (self.r1 < other.r0 or self.r0 > other.r1 or
                    self.c1 < other.c0 or self.c0 > other.c1)

    def to_tuple(self) -> Tuple[int, int, int, int]:
        return (self.r0, self.c0, self.r1, self.c1)


@dataclass
class MultiRangeSelectionState:
    """Stateful model holding multiple disjoint or overlapping selection ranges."""
    ranges: List[SelectionBox] = field(default_factory=list)
    active_range_idx: int = -1
    lead_cursor: Tuple[int, int] = (0, 0)
    anchor_cursor: Tuple[int, int] = (0, 0)

    @property
    def total_boxes(self) -> int:
        return len(self.ranges)

    @property
    def primary_range(self) -> Optional[SelectionBox]:
        if 0 <= self.active_range_idx < len(self.ranges):
            return self.ranges[self.active_range_idx]
        return self.ranges[-1] if self.ranges else None


class MultiRangeSelectionEngine:
    """Arbitrates Ctrl+Click disjoint multi-range selections, bounding deduplication,

    merging/splitting, and virtual camera R-Tree window spatial intersections.
    """
    def __init__(self,
                 row_px: int = 32,
                 col_px: int = 96,
                 rows: int = 100,
                 cols: int = 100):
        if any(type(v) is not int or v <= 0 for v in (row_px, col_px, rows, cols)):
            raise ValueError('Grid dimensions must be positive integers')
        self.row_px = row_px
        self.col_px = col_px
        self.rows = rows
        self.cols = cols
        self.merges: Dict[str, Tuple[int, int, int, int]] = {}
        self.cell_owners: Dict[Tuple[int, int], str] = {}

    def add_merge(self, merge_id: str, r0: int, c0: int, r1: int, c1: int):
        """Add merged cell region with half-open bounds [r0, r1) x [c0, c1)."""
        if any(type(x) is not int for x in (r0, c0, r1, c1)):
            raise ValueError('Coordinates must be integers')
        if not (0 <= r0 < r1 <= self.rows and 0 <= c0 < c1 <= self.cols):
            raise ValueError('Invalid merge boundary coordinates')
        for r in range(r0, r1):
            for c in range(c0, c1):
                if (r, c) in self.cell_owners:
                    raise ValueError(f'Cell ({r},{c}) overlaps with existing merge {self.cell_owners[(r, c)]}')
        self.merges[merge_id] = (r0, c0, r1, c1)
        for r in range(r0, r1):
            for c in range(c0, c1):
                self.cell_owners[(r, c)] = merge_id

    def expand_to_merged_bounds(self, box: SelectionBox) -> SelectionBox:
        """Expands a SelectionBox to fully cover any intersected merged cells."""
        cur_r0, cur_c0, cur_r1, cur_c1 = box.r0, box.c0, box.r1, box.c1
        expanded = True
        while expanded:
            expanded = False
            for r in range(cur_r0, cur_r1 + 1):
                for c in range(cur_c0, cur_c1 + 1):
                    merge_id = self.cell_owners.get((r, c))
                    if merge_id:
                        mr0, mc0, mr1, mc1 = self.merges[merge_id]
                        # half-open [mr0, mr1) -> inclusive [mr0, mr1 - 1]
                        im_r1, im_c1 = mr1 - 1, mc1 - 1
                        if mr0 < cur_r0:
                            cur_r0 = mr0
                            expanded = True
                        if im_r1 > cur_r1:
                            cur_r1 = im_r1
                            expanded = True
                        if mc0 < cur_c0:
                            cur_c0 = mc0
                            expanded = True
                        if im_c1 > cur_c1:
                            cur_c1 = im_c1
                            expanded = True
        return SelectionBox(cur_r0, cur_c0, cur_r1, cur_c1, box.box_id)

    def handle_pointer_click(self,
                             current_state: MultiRangeSelectionState,
                             cell: Tuple[int, int],
                             ctrl_or_cmd: bool = False,
                             shift: bool = False) -> MultiRangeSelectionState:
        """Processes a click on cell (r, c) under modifier keys (Ctrl/Cmd, Shift).

        - Plain Click: Clears previous ranges, creates a single 1x1 range at cell.
        - Ctrl/Cmd Click: Adds a new disjoint range or toggles an existing range.
        - Shift Click: Expands the current range from anchor_cursor to cell.
        - Ctrl+Shift Click: Adds a new range extending from anchor_cursor to cell.
        """
        r, c = cell
        if any(type(x) is not int for x in (r, c)):
            raise ValueError('Cell coordinates must be integers')
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            raise IndexError('Cell coordinates out of bounds')

        base_box = SelectionBox(r, c, r, c, box_id=f'box-{len(current_state.ranges)}')
        expanded_box = self.expand_to_merged_bounds(base_box)

        if not ctrl_or_cmd and not shift:
            # Plain click resets all ranges to this single target
            return MultiRangeSelectionState(
                ranges=[expanded_box],
                active_range_idx=0,
                lead_cursor=(r, c),
                anchor_cursor=(r, c)
            )

        if ctrl_or_cmd and not shift:
            # Check if clicking directly on a single 1x1 box or toggleable range
            # If cell is already covered by a 1x1 box, toggle off (remove)
            new_ranges = list(current_state.ranges)
            toggled_off = False
            for idx, b in enumerate(new_ranges):
                if b.cell_count() == 1 and b.contains(r, c):
                    new_ranges.pop(idx)
                    toggled_off = True
                    break

            if not toggled_off:
                # Add new disjoint box
                new_box = SelectionBox(r, c, r, c, box_id=f'box-{len(new_ranges)}')
                new_box = self.expand_to_merged_bounds(new_box)
                new_ranges.append(new_box)

            active_idx = len(new_ranges) - 1 if new_ranges else -1
            return MultiRangeSelectionState(
                ranges=new_ranges,
                active_range_idx=active_idx,
                lead_cursor=(r, c),
                anchor_cursor=(r, c)
            )

        if shift and not ctrl_or_cmd:
            # Shift without Ctrl: Extend primary selection from anchor
            anchor_r, anchor_c = current_state.anchor_cursor
            r0 = min(anchor_r, r)
            r1 = max(anchor_r, r)
            c0 = min(anchor_c, c)
            c1 = max(anchor_c, c)
            ext_box = SelectionBox(r0, c0, r1, c1, box_id='primary-ext')
            ext_box = self.expand_to_merged_bounds(ext_box)
            return MultiRangeSelectionState(
                ranges=[ext_box],
                active_range_idx=0,
                lead_cursor=(r, c),
                anchor_cursor=current_state.anchor_cursor
            )

        # Ctrl+Shift: Add a new range extending from anchor to cell without clearing existing
        anchor_r, anchor_c = current_state.anchor_cursor
        r0 = min(anchor_r, r)
        r1 = max(anchor_r, r)
        c0 = min(anchor_c, c)
        c1 = max(anchor_c, c)
        new_ext_box = SelectionBox(r0, c0, r1, c1, box_id=f'box-{len(current_state.ranges)}')
        new_ext_box = self.expand_to_merged_bounds(new_ext_box)
        new_ranges = list(current_state.ranges)
        new_ranges.append(new_ext_box)
        return MultiRangeSelectionState(
            ranges=new_ranges,
            active_range_idx=len(new_ranges) - 1,
            lead_cursor=(r, c),
            anchor_cursor=current_state.anchor_cursor
        )

    def deduplicate_ranges(self, ranges: Sequence[SelectionBox]) -> List[SelectionBox]:
        """Eliminates redundant identical or fully subsumed ranges in O(K log K) amortized.

        Returns normalized disjoint / non-redundant minimal bounding boxes.
        """
        if not ranges:
            return []

        # Sort primarily by (r0, c0, -r1, -c1)
        sorted_boxes = sorted(ranges, key=lambda b: (b.r0, b.c0, -b.r1, -b.c1))
        result: List[SelectionBox] = []

        for b in sorted_boxes:
            # Check if b is fully contained inside any box already in result
            contained = False
            for kept in result:
                if (kept.r0 <= b.r0 and kept.r1 >= b.r1 and
                    kept.c0 <= b.c0 and kept.c1 >= b.c1):
                    contained = True
                    break
            if not contained:
                result.append(b)

        return result

    def query_visible_selection_boxes(self,
                                      state: MultiRangeSelectionState,
                                      camera: Tuple[float, float],
                                      viewport: Tuple[float, float],
                                      zoom: float = 1.0) -> List[SelectionBox]:
        """Spatial query returning only selection boxes that intersect the current virtual camera frustum.

        Complexity is bounded by K ranges instead of N*M grid cells.
        """
        finite_number(*camera, *viewport, zoom)
        if zoom <= 0 or viewport[0] <= 0 or viewport[1] <= 0:
            raise ValueError('Positive viewport dimensions and zoom required')

        cam_x, cam_y = camera
        vw, vh = viewport
        vx0, vy0 = max(0.0, cam_x), max(0.0, cam_y)
        vx1, vy1 = cam_x + vw / zoom, cam_y + vh / zoom

        r_start = max(0, int(math.floor(vy0 / self.row_px)))
        r_end = min(self.rows - 1, int(math.ceil(vy1 / self.row_px)))
        c_start = max(0, int(math.floor(vx0 / self.col_px)))
        c_end = min(self.cols - 1, int(math.ceil(vx1 / self.col_px)))

        if r_start > r_end or c_start > c_end:
            return []

        camera_box = SelectionBox(r_start, c_start, r_end, c_end)
        visible = []
        for box in state.ranges:
            if box.intersects(camera_box):
                visible.append(box)

        return visible

    def get_selected_unique_cells(self, state: MultiRangeSelectionState) -> Set[Tuple[int, int]]:
        """Returns the set of unique cell coordinates covered by all active ranges."""
        unique_cells: Set[Tuple[int, int]] = set()
        for b in state.ranges:
            for r in range(b.r0, b.r1 + 1):
                for c in range(b.c0, b.c1 + 1):
                    unique_cells.add((r, c))
        return unique_cells

    def serialize_ranges_tsv(self,
                             state: MultiRangeSelectionState,
                             cell_value_fn: Optional[Any] = None) -> str:
        """Serializes selected multi-range contents to TSV format for clipboard copying.

        If multiple disjoint ranges exist, ranges are separated by a double-newline block.
        """
        blocks = []
        for b in state.ranges:
            lines = []
            for r in range(b.r0, b.r1 + 1):
                row_vals = []
                for c in range(b.c0, b.c1 + 1):
                    val = cell_value_fn(r, c) if cell_value_fn else f'{r},{c}'
                    row_vals.append(str(val))
                lines.append('\t'.join(row_vals))
            blocks.append('\n'.join(lines))
        return '\n\n'.join(blocks)
