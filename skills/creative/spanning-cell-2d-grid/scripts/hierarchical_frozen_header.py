"""
Hierarchical Multi-Level Nested Frozen Headers with R-Tree Span Grouping.

Implements multi-tier nested header grouping (e.g., Year -> Quarter -> Month -> Day)
on dual-axis frozen panes with recursive span bounding and parent-child clipping.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Set, Tuple
import sqlite3

@dataclass
class HeaderNode:
    id: int
    title: str
    level: int                  # 0 is top-most group, increasing downwards
    r0: int                     # half-open row start
    r1: int                     # half-open row end
    c0: int                     # half-open col start
    c1: int                     # half-open col end
    parent_id: Optional[int] = None
    child_ids: Optional[List[int]] = None

    def __post_init__(self):
        if self.child_ids is None:
            self.child_ids = []

@dataclass
class VisibleHeaderItem:
    id: int
    title: str
    level: int
    bounds: List[int]           # [r0, c0, r1, c1]
    clip: List[int]             # [clipped_r0, clipped_c0, clipped_r1, clipped_c1]
    is_partially_clipped: bool
    is_fully_visible: bool
    parent_id: Optional[int]
    child_ids: List[int]
    sticky_offset_x: float      # For progressive horizontal stickiness within parent
    sticky_offset_y: float      # For progressive vertical stickiness within parent

class HierarchicalFrozenHeaderGrid:
    """
    Manages multi-tier nested frozen headers on top of a 2D virtualized grid
    using SQLite R-Tree spatial indexing with recursive hierarchical span containment.
    """
    def __init__(
        self,
        total_rows: int,
        total_cols: int,
        header_levels: int,
        row_height: float,
        col_width: float,
        viewport_width: float,
        viewport_height: float,
        frozen_cols: int = 0,
        overscan_cols: int = 2
    ):
        if total_rows <= 0 or total_cols <= 0:
            raise ValueError("Total rows and cols must be positive integers")
        if header_levels <= 0:
            raise ValueError("Header levels must be positive integer >= 1")
        if header_levels > total_rows:
            raise ValueError("Header levels cannot exceed total rows")
        if row_height <= 0 or col_width <= 0:
            raise ValueError("Row height and col width must be positive numbers")
        if viewport_width <= 0 or viewport_height <= 0:
            raise ValueError("Viewport dimensions must be positive numbers")
        if frozen_cols < 0 or frozen_cols > total_cols:
            raise ValueError("Frozen columns must be between 0 and total_cols")

        self.total_rows = total_rows
        self.total_cols = total_cols
        self.header_levels = header_levels
        self.row_height = float(row_height)
        self.col_width = float(col_width)
        self.viewport_width = float(viewport_width)
        self.viewport_height = float(viewport_height)
        self.frozen_cols = frozen_cols
        self.overscan_cols = overscan_cols

        self.total_header_height = self.header_levels * self.row_height
        self.frozen_col_width = self.frozen_cols * self.col_width

        self.body_viewport_w = max(0.0, self.viewport_width - self.frozen_col_width)
        self.body_total_w = (self.total_cols - self.frozen_cols) * self.col_width
        self.max_scroll_x = max(0.0, self.body_total_w - self.body_viewport_w)

        self.scroll_x = 0.0

        # In-memory SQLite database for spatial R-Tree and hierarchical relations
        self.db = sqlite3.connect(":memory:")
        self._init_db()

        self.nodes: Dict[int, HeaderNode] = {}

    def _init_db(self):
        with self.db:
            # Spatial R-Tree table for 2D bounding boxes: id, r0, r1, c0, c1
            self.db.execute("CREATE VIRTUAL TABLE header_rtree USING rtree_i32(id, r0, r1, c0, c1)")
            # Relational table for hierarchy metadata
            self.db.execute("""
                CREATE TABLE header_metadata (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    level INTEGER NOT NULL,
                    parent_id INTEGER,
                    FOREIGN KEY(parent_id) REFERENCES header_metadata(id)
                )
            """)

    def close(self):
        if self.db:
            self.db.close()
            self.db = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def add_header_node(
        self,
        node_id: int,
        title: str,
        level: int,
        c0: int,
        c1: int,
        parent_id: Optional[int] = None
    ) -> HeaderNode:
        """
        Adds a hierarchical header node at a specified level span [c0, c1).
        Row boundaries are deterministically computed as r0 = level, r1 = level + 1.
        Validates strict parent-child containment and sibling disjointness.
        """
        if type(node_id) is not int or node_id < 0 or node_id >= 2**63:
            raise ValueError("Node ID must be non-negative signed 64-bit integer")
        if not title or not isinstance(title, str):
            raise ValueError("Title must be non-empty string")
        if type(level) is not int or not (0 <= level < self.header_levels):
            raise ValueError(f"Level must be between 0 and {self.header_levels - 1}")
        if type(c0) is not int or type(c1) is not int or not (0 <= c0 < c1 <= self.total_cols):
            raise ValueError(f"Invalid column boundaries [c0={c0}, c1={c1})")
        if node_id in self.nodes:
            raise ValueError(f"Duplicate header node ID: {node_id}")

        r0 = level
        r1 = level + 1

        # Parent containment check
        if parent_id is not None:
            if parent_id not in self.nodes:
                raise ValueError(f"Parent ID {parent_id} does not exist")
            parent = self.nodes[parent_id]
            if parent.level != level - 1:
                raise ValueError(f"Parent level must be {level - 1}, but got {parent.level}")
            if not (parent.c0 <= c0 and c1 <= parent.c1):
                raise ValueError(
                    f"Child span [{c0}, {c1}) exceeds parent span [{parent.c0}, {parent.c1})"
                )
        elif level > 0:
            raise ValueError(f"Header node at level {level} must specify a parent_id")

        # Sibling overlap check within the same level
        with self.db:
            overlapping = self.db.execute("""
                SELECT r.id FROM header_rtree r
                JOIN header_metadata m ON r.id = m.id
                WHERE m.level = ? AND r.c0 < ? AND r.c1 > ?
            """, (level, c1, c0)).fetchall()
            if overlapping:
                raise ValueError(f"Header node overlaps with existing node(s) on level {level}")

            self.db.execute("INSERT INTO header_rtree VALUES (?, ?, ?, ?, ?)", (node_id, r0, r1, c0, c1))
            self.db.execute(
                "INSERT INTO header_metadata VALUES (?, ?, ?, ?)",
                (node_id, title, level, parent_id)
            )

        node = HeaderNode(
            id=node_id,
            title=title,
            level=level,
            r0=r0,
            r1=r1,
            c0=c0,
            c1=c1,
            parent_id=parent_id,
            child_ids=[]
        )
        self.nodes[node_id] = node
        if parent_id is not None:
            self.nodes[parent_id].child_ids.append(node_id)

        return node

    def scroll_to(self, x: float):
        """Updates horizontal scroll offset with boundary clamping."""
        self.scroll_x = max(0.0, min(self.max_scroll_x, float(x)))

    def get_visible_column_range(self) -> Tuple[int, int]:
        """Calculates visible half-open column range [col_start, col_end) with overscan."""
        if self.body_total_w <= 0:
            return (self.frozen_cols, self.frozen_cols)

        rel_c0 = int(self.scroll_x // self.col_width)
        rel_c1 = int((self.scroll_x + self.body_viewport_w) // self.col_width) + 1

        rel_c0 = max(0, rel_c0 - self.overscan_cols)
        rel_c1 = min(self.total_cols - self.frozen_cols, rel_c1 + self.overscan_cols)

        return (self.frozen_cols + rel_c0, self.frozen_cols + rel_c1)

    def query_visible_headers(self) -> List[VisibleHeaderItem]:
        """
        Queries all visible headers using R-Tree spatial intersection.
        Calculates parent-child clipping, containment bounds, and sticky title offsets.
        """
        c_vis_start, c_vis_end = self.get_visible_column_range()

        # Any header intersecting either frozen columns or visible body columns
        query_ranges = []
        if self.frozen_cols > 0:
            query_ranges.append((0, self.frozen_cols))
        if c_vis_end > c_vis_start:
            query_ranges.append((c_vis_start, c_vis_end))

        if not query_ranges:
            return []

        # Find intersecting header IDs via R-Tree
        visible_ids: Set[int] = set()
        for q_c0, q_c1 in query_ranges:
            hits = self.db.execute(
                "SELECT id FROM header_rtree WHERE r0 < ? AND r1 > ? AND c0 < ? AND c1 > ?",
                (self.header_levels, 0, q_c1, q_c0)
            ).fetchall()
            for (h_id,) in hits:
                visible_ids.add(h_id)

        # Sort by level ascending, then c0 ascending
        sorted_nodes = sorted(
            [self.nodes[nid] for nid in visible_ids],
            key=lambda n: (n.level, n.c0)
        )

        results: List[VisibleHeaderItem] = []
        for n in sorted_nodes:
            # Active viewport window for this node
            # If node is completely in frozen cols, window is [0, frozen_cols)
            # If node is in scrolling body, window is [c_vis_start, c_vis_end)
            # If crosses frozen boundary:
            is_frozen = n.c1 <= self.frozen_cols
            if is_frozen:
                win_c0, win_c1 = 0, self.frozen_cols
            else:
                win_c0 = max(self.frozen_cols, c_vis_start)
                win_c1 = c_vis_end

            clipped_c0 = max(n.c0, win_c0)
            clipped_c1 = min(n.c1, win_c1)
            clipped_r0 = n.r0
            clipped_r1 = n.r1

            is_partial = (clipped_c0 > n.c0) or (clipped_c1 < n.c1)
            is_full = (clipped_c0 == n.c0) and (clipped_c1 == n.c1)

            # Compute progressive sticky offset for header labels
            # Header title pins to left of visible section while staying within parent & self bounds
            node_pixel_start = n.c0 * self.col_width
            node_pixel_end = n.c1 * self.col_width
            viewport_pixel_start = self.frozen_col_width + self.scroll_x

            # Sticky offset relative to node origin
            sticky_x = 0.0
            if not is_frozen and viewport_pixel_start > node_pixel_start:
                max_sticky = max(0.0, (n.c1 - n.c0 - 1) * self.col_width)
                offset = viewport_pixel_start - node_pixel_start
                sticky_x = min(offset, max_sticky)

            results.append(VisibleHeaderItem(
                id=n.id,
                title=n.title,
                level=n.level,
                bounds=[n.r0, n.c0, n.r1, n.c1],
                clip=[clipped_r0, clipped_c0, clipped_r1, clipped_c1],
                is_partially_clipped=is_partial,
                is_fully_visible=is_full,
                parent_id=n.parent_id,
                child_ids=list(n.child_ids),
                sticky_offset_x=sticky_x,
                sticky_offset_y=0.0
            ))

        return results

    def get_hierarchy_tree(self) -> List[Dict[str, Any]]:
        """Returns the full hierarchical tree structure serialized for client components."""
        def serialize_node(node_id: int) -> Dict[str, Any]:
            n = self.nodes[node_id]
            return {
                "id": n.id,
                "title": n.title,
                "level": n.level,
                "span": [n.c0, n.c1],
                "col_count": n.c1 - n.c0,
                "children": [serialize_node(cid) for cid in n.child_ids]
            }

        root_nodes = [n for n in self.nodes.values() if n.parent_id is None]
        root_nodes.sort(key=lambda n: n.c0)
        return [serialize_node(r.id) for r in root_nodes]

    def compute_header_render_manifest(self) -> Dict[str, Any]:
        """
        Produces complete deterministic composite layout manifest for multi-level nested headers.
        """
        c_vis_start, c_vis_end = self.get_visible_column_range()
        visible_headers = self.query_visible_headers()

        level_summary = {}
        for lvl in range(self.header_levels):
            level_items = [h for h in visible_headers if h.level == lvl]
            level_summary[f"level_{lvl}"] = {
                "level": lvl,
                "top_px": lvl * self.row_height,
                "height_px": self.row_height,
                "visible_count": len(level_items),
                "items": [
                    {
                        "id": h.id,
                        "title": h.title,
                        "bounds": h.bounds,
                        "clip": h.clip,
                        "is_partially_clipped": h.is_partially_clipped,
                        "sticky_offset_x": h.sticky_offset_x,
                        "parent_id": h.parent_id
                    }
                    for h in level_items
                ]
            }

        return {
            "geometry": {
                "header_levels": self.header_levels,
                "total_header_height": self.total_header_height,
                "frozen_cols": self.frozen_cols,
                "frozen_col_width": self.frozen_col_width,
                "scroll_x": self.scroll_x,
                "max_scroll_x": self.max_scroll_x,
                "visible_col_range": [c_vis_start, c_vis_end]
            },
            "levels": level_summary,
            "total_visible_header_nodes": len(visible_headers),
            "hierarchy_tree": self.get_hierarchy_tree()
        }
