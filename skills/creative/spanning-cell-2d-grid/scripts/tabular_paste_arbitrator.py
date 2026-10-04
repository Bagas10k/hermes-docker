"""Tabular Clipboard Paste Arbitration & Rectangular Fill Across Asymmetric Multi-Range Selections.

Mathematical and algorithmic oracle for parsing, arbitrating, and tiling/filling
clipboard tabular data (TSV / CSV) across single-cell, single-range, or
disjoint asymmetric multi-range target selections in virtualized 2D grids,
honoring merged cell boundaries, handling formula relative coordinate translation,
and preventing shape mismatch data corruption.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any, Sequence, Union
import math
import csv
import io
import re

try:
    from .multi_range_selection import SelectionBox, MultiRangeSelectionState, MultiRangeSelectionEngine
except ImportError:
    from multi_range_selection import SelectionBox, MultiRangeSelectionState, MultiRangeSelectionEngine


def finite_number(*values):
    """Enforce finite numeric floats/ints without boolean traps."""
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
        raise ValueError('Finite numeric values required')


def col_to_name(col_idx: int) -> str:
    """Converts 0-indexed column integer to A1-style letters (0 -> A, 25 -> Z, 26 -> AA)."""
    if not isinstance(col_idx, int) or col_idx < 0:
        raise ValueError('Column index must be a non-negative integer')
    name = []
    col = col_idx + 1
    while col > 0:
        col, rem = divmod(col - 1, 26)
        name.append(chr(65 + rem))
    return "".join(reversed(name))


def name_to_col(col_name: str) -> int:
    """Converts A1-style column letters to 0-indexed column integer (A -> 0, Z -> 25, AA -> 26)."""
    if not isinstance(col_name, str) or not col_name.isalpha():
        raise ValueError('Column name must contain alphabetic characters only')
    col = 0
    for char in col_name.upper():
        col = col * 26 + (ord(char) - ord('A') + 1)
    return col - 1


_CELL_REF_REGEX = re.compile(r'(\$?[A-Za-z]+)(\$?[0-9]+)')


def translate_formula_references(formula: str, delta_row: int, delta_col: int, max_rows: int = 1000000, max_cols: int = 16384) -> str:
    """Translates relative cell references in a spreadsheet formula string by (delta_row, delta_col).

    Preserves absolute coordinate references ($A$1, $A1, A$1).
    Out-of-bounds shifted references are transformed to #REF!.
    """
    if not isinstance(formula, str) or not formula.startswith('='):
        return formula
    if delta_row == 0 and delta_col == 0:
        return formula

    def _replace_ref(match: re.Match) -> str:
        col_part = match.group(1)
        row_part = match.group(2)

        is_abs_col = col_part.startswith('$')
        is_abs_row = row_part.startswith('$')

        clean_col = col_part.lstrip('$')
        clean_row = row_part.lstrip('$')

        try:
            col_idx = name_to_col(clean_col)
            row_idx = int(clean_row) - 1  # 0-indexed
        except Exception:
            return match.group(0)

        # Shift column if relative
        new_col_idx = col_idx if is_abs_col else (col_idx + delta_col)
        # Shift row if relative
        new_row_idx = row_idx if is_abs_row else (row_idx + delta_row)

        if new_col_idx < 0 or new_col_idx >= max_cols or new_row_idx < 0 or new_row_idx >= max_rows:
            return '#REF!'

        new_col_str = ('$' if is_abs_col else '') + col_to_name(new_col_idx)
        new_row_str = ('$' if is_abs_row else '') + str(new_row_idx + 1)
        return f"{new_col_str}{new_row_str}"

    return _CELL_REF_REGEX.sub(_replace_ref, formula)


@dataclass(frozen=True)
class ClipboardTable:
    """Parsed 2D rectangular matrix of tabular strings from clipboard payload."""
    rows: int
    cols: int
    data: Tuple[Tuple[str, ...], ...]

    def __post_init__(self):
        if self.rows < 0 or self.cols < 0:
            raise ValueError('Dimensions cannot be negative')
        if len(self.data) != self.rows:
            raise ValueError(f'Data row count {len(self.data)} mismatch with rows {self.rows}')
        for r_idx, row in enumerate(self.data):
            if len(row) != self.cols:
                raise ValueError(f'Data col count at row {r_idx} mismatch with cols {self.cols}')

    def get(self, r: int, c: int) -> str:
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            raise IndexError(f'Cell index ({r}, {c}) out of bounds ({self.rows}, {self.cols})')
        return self.data[r][c]

    def is_empty(self) -> bool:
        return self.rows == 0 or self.cols == 0

    def is_scalar(self) -> bool:
        return self.rows == 1 and self.cols == 1


@dataclass(frozen=True)
class CellMutation:
    """Represents a targeted mutation of a single cell."""
    row: int
    col: int
    old_value: str
    new_value: str


@dataclass(frozen=True)
class MergedCellConflict:
    """Detail of a conflict when a paste attempt touches a merged region."""
    row: int
    col: int
    owner_id: str
    r0: int
    c0: int
    r1: int
    c1: int
    is_top_left: bool


@dataclass(frozen=True)
class PastePlan:
    """Deterministic transaction plan resulting from paste arbitration."""
    mode: str  # 'single_anchor_expand', 'exact_match_fill', 'modulo_repeat_fill', 'asymmetric_multi_target_broadcast', 'empty_noop', 'rejected_conflict'
    target_boxes: Tuple[SelectionBox, ...]
    mutations: Tuple[CellMutation, ...]
    total_cells: int
    affected_rows: int
    affected_cols: int
    clipped_overflow: bool = False
    merged_conflicts: Tuple[MergedCellConflict, ...] = ()
    unmerged_regions: Tuple[str, ...] = ()
    is_vetoed: bool = False


class TabularPasteArbitrator:
    """Engine arbitrating tabular paste ingestion across arbitrary selection topologies."""

    def __init__(self,
                 grid_rows: int = 100,
                 grid_cols: int = 100,
                 cell_store: Optional[Dict[Tuple[int, int], str]] = None,
                 multi_engine: Optional[MultiRangeSelectionEngine] = None,
                 merges: Optional[Dict[str, Tuple[int, int, int, int]]] = None):
        if any(type(x) is not int or x <= 0 for x in (grid_rows, grid_cols)):
            raise ValueError('Grid dimensions must be positive integers')
        self.grid_rows = grid_rows
        self.grid_cols = grid_cols
        self.cell_store = dict(cell_store) if cell_store is not None else {}
        self.multi_engine = multi_engine or MultiRangeSelectionEngine(rows=grid_rows, cols=grid_cols)
        # Merged regions: merge_id -> (r0, c0, r1, c1) where r1, c1 are exclusive bounds [r0, r1) x [c0, c1)
        self.merges: Dict[str, Tuple[int, int, int, int]] = {}
        self.cell_merge_owners: Dict[Tuple[int, int], str] = {}
        if merges:
            for mid, bounds in merges.items():
                self.add_merge(mid, bounds[0], bounds[1], bounds[2], bounds[3])

    def add_merge(self, merge_id: str, r0: int, c0: int, r1: int, c1: int):
        """Register a merged cell region with half-open bounds [r0, r1) x [c0, c1)."""
        if any(type(x) is not int for x in (r0, c0, r1, c1)):
            raise ValueError('Merge coordinates must be integers')
        if not (0 <= r0 < r1 <= self.grid_rows and 0 <= c0 < c1 <= self.grid_cols):
            raise ValueError('Invalid merge boundary coordinates')
        for r in range(r0, r1):
            for c in range(c0, c1):
                if (r, c) in self.cell_merge_owners:
                    raise ValueError(f'Cell ({r},{c}) overlaps with merge {self.cell_merge_owners[(r, c)]}')
        self.merges[merge_id] = (r0, c0, r1, c1)
        for r in range(r0, r1):
            for c in range(c0, c1):
                self.cell_merge_owners[(r, c)] = merge_id

    def remove_merge(self, merge_id: str):
        """Unmerge region by ID."""
        if merge_id in self.merges:
            r0, c0, r1, c1 = self.merges.pop(merge_id)
            for r in range(r0, r1):
                for c in range(c0, c1):
                    self.cell_merge_owners.pop((r, c), None)

    def parse_clipboard_text(self, text: str) -> ClipboardTable:
        """Parses raw clipboard string into ClipboardTable.

        Handles TSV (default spreadsheet format), CRLF/LF normalization,
        and quotes. Strips trailing single newline to avoid spurious empty row.
        """
        if not isinstance(text, str):
            raise TypeError('Clipboard text must be a string')
        if not text:
            return ClipboardTable(0, 0, ())

        normalized = text.rstrip('\r\n')
        if not normalized:
            return ClipboardTable(1, 1, (('',),))

        delimiter = '\t' if '\t' in normalized else (',' if ',' in normalized else '\t')
        reader = csv.reader(io.StringIO(normalized), delimiter=delimiter)
        raw_rows = [list(row) for row in reader]

        if not raw_rows:
            return ClipboardTable(0, 0, ())

        max_cols = max(len(r) for r in raw_rows)
        if max_cols == 0:
            return ClipboardTable(len(raw_rows), 0, tuple(() for _ in raw_rows))

        rect_data: List[Tuple[str, ...]] = []
        for r in raw_rows:
            if len(r) < max_cols:
                r = r + [''] * (max_cols - len(r))
            rect_data.append(tuple(r))

        return ClipboardTable(rows=len(rect_data), cols=max_cols, data=tuple(rect_data))

    def _resolve_cell_value(self, raw_val: str, src_r: int, src_c: int, tgt_r: int, tgt_c: int) -> str:
        """Translates formulas if relative, otherwise returns raw string value."""
        if raw_val.startswith('='):
            delta_r = tgt_r - src_r
            delta_c = tgt_c - src_c
            return translate_formula_references(raw_val, delta_r, delta_c, max_rows=self.grid_rows, max_cols=self.grid_cols)
        return raw_val

    def plan_paste(self,
                   clipboard: Union[str, ClipboardTable],
                   selection: Union[MultiRangeSelectionState, Sequence[SelectionBox], SelectionBox],
                   merge_policy: str = 'veto_partial_overwrite') -> PastePlan:
        """Computes a deterministic PastePlan according to standard spreadsheet arbitration rules:

        merge_policy:
          - 'veto_partial_overwrite': Vetoes the paste if any targeted cell intersects a merged region
                                      partially (does not cover entire merged region or targets non-top-left cell).
          - 'auto_unmerge': Automatically unmerges conflicting merged regions touched by the paste.
          - 'top_left_only': Ignores non-top-left cells of merged regions (standard read-only display mode).

        Case 1: Single 1x1 target cell -> expand clipboard shape rooted at anchor.
        Case 2: Single bounding box of size (H, W):
          - If clipboard (h, w) divides (H, W) or matches exactly -> modulo repeat tiling.
          - If clipboard (h, w) > (H, W) -> paste full clipboard starting at anchor, expanding past selection.
          - If clipboard (h, w) < (H, W) -> repeat/tile clipboard to fill selection (Excel/Sheets standard).
        Case 3: Multiple disjoint target bounding boxes:
          - If clipboard is scalar (1x1) -> fill every cell of every target box with scalar value.
          - If clipboard shape equals each target box shape -> 1:1 paste into each box.
          - If asymmetric -> each disjoint box tiles clipboard via modulo arithmetic (r % h, c % w).
        """
        table = self.parse_clipboard_text(clipboard) if isinstance(clipboard, str) else clipboard
        if table.is_empty():
            return PastePlan(
                mode='empty_noop',
                target_boxes=(),
                mutations=(),
                total_cells=0,
                affected_rows=0,
                affected_cols=0
            )

        if isinstance(selection, MultiRangeSelectionState):
            boxes = tuple(selection.ranges)
            anchor = selection.anchor_cursor
        elif isinstance(selection, SelectionBox):
            boxes = (selection,)
            anchor = (selection.r0, selection.c0)
        elif isinstance(selection, (list, tuple)):
            boxes = tuple(selection)
            anchor = (boxes[0].r0, boxes[0].c0) if boxes else (0, 0)
        else:
            raise TypeError('Unsupported selection type')

        if not boxes:
            boxes = (SelectionBox(anchor[0], anchor[1], anchor[0], anchor[1]),)

        deduped_boxes = tuple(self.multi_engine.deduplicate_ranges(boxes))

        mutations_dict: Dict[Tuple[int, int], CellMutation] = {}
        clipped_overflow = False

        if len(deduped_boxes) == 1 and deduped_boxes[0].cell_count() == 1:
            box = deduped_boxes[0]
            mode = 'single_anchor_expand'
            r_start, c_start = box.r0, box.c0

            for dr in range(table.rows):
                tr = r_start + dr
                if tr >= self.grid_rows:
                    clipped_overflow = True
                    continue
                for dc in range(table.cols):
                    tc = c_start + dc
                    if tc >= self.grid_cols:
                        clipped_overflow = True
                        continue
                    raw_val = table.get(dr, dc)
                    val = self._resolve_cell_value(raw_val, dr, dc, tr, tc)
                    old_val = self.cell_store.get((tr, tc), '')
                    mutations_dict[(tr, tc)] = CellMutation(tr, tc, old_val, val)

            effective_boxes = (SelectionBox(
                r_start,
                c_start,
                min(self.grid_rows - 1, r_start + table.rows - 1),
                min(self.grid_cols - 1, c_start + table.cols - 1)
            ),)

        elif len(deduped_boxes) == 1 and deduped_boxes[0].cell_count() > 1:
            box = deduped_boxes[0]
            tgt_h = box.r1 - box.r0 + 1
            tgt_w = box.c1 - box.c0 + 1

            if table.rows == tgt_h and table.cols == tgt_w:
                mode = 'exact_match_fill'
                for dr in range(tgt_h):
                    tr = box.r0 + dr
                    for dc in range(tgt_w):
                        tc = box.c0 + dc
                        raw_val = table.get(dr, dc)
                        val = self._resolve_cell_value(raw_val, dr, dc, tr, tc)
                        old_val = self.cell_store.get((tr, tc), '')
                        mutations_dict[(tr, tc)] = CellMutation(tr, tc, old_val, val)
                effective_boxes = (box,)

            elif table.rows > tgt_h or table.cols > tgt_w:
                mode = 'overflow_expand'
                r_start, c_start = box.r0, box.c0
                for dr in range(table.rows):
                    tr = r_start + dr
                    if tr >= self.grid_rows:
                        clipped_overflow = True
                        continue
                    for dc in range(table.cols):
                        tc = c_start + dc
                        if tc >= self.grid_cols:
                            clipped_overflow = True
                            continue
                        raw_val = table.get(dr, dc)
                        val = self._resolve_cell_value(raw_val, dr, dc, tr, tc)
                        old_val = self.cell_store.get((tr, tc), '')
                        mutations_dict[(tr, tc)] = CellMutation(tr, tc, old_val, val)
                effective_boxes = (SelectionBox(
                    r_start,
                    c_start,
                    min(self.grid_rows - 1, r_start + table.rows - 1),
                    min(self.grid_cols - 1, c_start + table.cols - 1)
                ),)

            else:
                mode = 'modulo_repeat_fill'
                for dr in range(tgt_h):
                    tr = box.r0 + dr
                    src_r = dr % table.rows
                    for dc in range(tgt_w):
                        tc = box.c0 + dc
                        src_c = dc % table.cols
                        raw_val = table.get(src_r, src_c)
                        val = self._resolve_cell_value(raw_val, src_r, src_c, tr, tc)
                        old_val = self.cell_store.get((tr, tc), '')
                        mutations_dict[(tr, tc)] = CellMutation(tr, tc, old_val, val)
                effective_boxes = (box,)

        else:
            mode = 'asymmetric_multi_target_broadcast'
            effective_boxes = deduped_boxes

            for box in deduped_boxes:
                tgt_h = box.r1 - box.r0 + 1
                tgt_w = box.c1 - box.c0 + 1

                for dr in range(tgt_h):
                    tr = box.r0 + dr
                    src_r = 0 if table.rows == 1 else (dr % table.rows)
                    for dc in range(tgt_w):
                        tc = box.c0 + dc
                        src_c = 0 if table.cols == 1 else (dc % table.cols)
                        raw_val = table.get(src_r, src_c)
                        val = self._resolve_cell_value(raw_val, src_r, src_c, tr, tc)
                        old_val = self.cell_store.get((tr, tc), '')
                        mutations_dict[(tr, tc)] = CellMutation(tr, tc, old_val, val)

        # Audit Merged Cell Invariants & Conflicts
        targeted_coords = set(mutations_dict.keys())
        conflicts: List[MergedCellConflict] = []
        unmerged_to_trigger: Set[str] = set()

        for (r, c) in targeted_coords:
            if (r, c) in self.cell_merge_owners:
                m_id = self.cell_merge_owners[(r, c)]
                r0, c0, r1, c1 = self.merges[m_id]
                is_top_left = (r == r0 and c == c0)

                # Check if the entire merge is covered by targeted_coords
                all_covered = all((mr, mc) in targeted_coords for mr in range(r0, r1) for mc in range(c0, c1))
                if not all_covered or not is_top_left:
                    conflicts.append(MergedCellConflict(
                        row=r,
                        col=c,
                        owner_id=m_id,
                        r0=r0,
                        c0=c0,
                        r1=r1,
                        c1=c1,
                        is_top_left=is_top_left
                    ))
                    unmerged_to_trigger.add(m_id)

        is_vetoed = False
        if conflicts:
            if merge_policy == 'veto_partial_overwrite':
                is_vetoed = True
                return PastePlan(
                    mode='rejected_conflict',
                    target_boxes=effective_boxes,
                    mutations=(),
                    total_cells=0,
                    affected_rows=0,
                    affected_cols=0,
                    clipped_overflow=clipped_overflow,
                    merged_conflicts=tuple(conflicts),
                    unmerged_regions=(),
                    is_vetoed=True
                )
            elif merge_policy == 'auto_unmerge':
                # Policy permits auto-unmerging conflicting merge ranges
                pass
            elif merge_policy == 'top_left_only':
                # Filter out mutations that target non-top-left cells of any merged range
                for conf in conflicts:
                    if not conf.is_top_left:
                        mutations_dict.pop((conf.row, conf.col), None)

        sorted_mutations = tuple(sorted(mutations_dict.values(), key=lambda m: (m.row, m.col)))
        affected_rows = len(set(m.row for m in sorted_mutations))
        affected_cols = len(set(m.col for m in sorted_mutations))

        return PastePlan(
            mode=mode,
            target_boxes=effective_boxes,
            mutations=sorted_mutations,
            total_cells=len(sorted_mutations),
            affected_rows=affected_rows,
            affected_cols=affected_cols,
            clipped_overflow=clipped_overflow,
            merged_conflicts=tuple(conflicts),
            unmerged_regions=tuple(sorted(unmerged_to_trigger)) if merge_policy == 'auto_unmerge' else (),
            is_vetoed=False
        )

    def apply_plan(self, plan: PastePlan) -> Dict[Tuple[int, int], str]:
        """Atomically applies the mutations from a PastePlan into the internal cell_store."""
        if plan.is_vetoed:
            raise ValueError('Cannot apply a vetoed PastePlan')

        # If auto-unmerge was planned, execute unmerging first
        for m_id in plan.unmerged_regions:
            self.remove_merge(m_id)

        for mut in plan.mutations:
            self.cell_store[(mut.row, mut.col)] = mut.new_value
        return self.cell_store

    def rollback_plan(self, plan: PastePlan) -> Dict[Tuple[int, int], str]:
        """Atomically reverts the mutations from a PastePlan."""
        if plan.is_vetoed:
            return self.cell_store

        for mut in reversed(plan.mutations):
            if mut.old_value == '':
                self.cell_store.pop((mut.row, mut.col), None)
            else:
                self.cell_store[(mut.row, mut.col)] = mut.old_value
        return self.cell_store
