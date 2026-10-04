"""
Collapsible Accordion Column Grouping on Hierarchical Frozen Headers.

Implements dynamic expand/collapse states for multi-tier column groups with:
- State tracking (expanded vs collapsed)
- Dynamic column width assignment (0 for collapsed internal columns or summary column representation)
- Real-time R-Tree coordinate updates / morphing
- Zero-CLS width updates and progressive sticky offset re-calculation
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set, Tuple
import sqlite3

@dataclass
class CollapsibleHeaderNode:
    id: int
    title: str
    level: int                  # 0 is top-most group, increasing downwards
    r0: int                     # half-open row start
    r1: int                     # half-open row end
    c0: int                     # logical uncollapsed col start
    c1: int                     # logical uncollapsed col end
    parent_id: Optional[int] = None
    child_ids: List[int] = field(default_factory=list)
    collapsible: bool = False
    is_collapsed: bool = False
    summary_col_width: Optional[float] = None  # Width when collapsed (e.g. 1 column wide or custom width)

@dataclass
class VisibleCollapsibleHeaderItem:
    id: int
    title: str
    level: int
    logical_bounds: List[int]   # [r0, c0, r1, c1]
    pixel_x: float              # Start pixel X position after factoring collapsed state
    pixel_width: float          # Actual rendered pixel width
    is_collapsed: bool
    collapsible: bool
    is_hidden_by_parent: bool   # True if ancestor is collapsed
    clip_pixel_x: float         # Clipped to viewport
    clip_pixel_width: float     # Visible width in viewport
    is_partially_clipped: bool
    is_fully_visible: bool
    parent_id: Optional[int]
    child_ids: List[int]
    sticky_offset_x: float      # Sticky header label offset

class CollapsibleHierarchicalGrid:
    """
    Manages multi-tier nested frozen headers with interactive collapsible accordion groups.
    Computes dynamic visual column projections, zero-CLS coordinates, and updates spatial R-Tree.
    """
    def __init__(
        self,
        total_rows: int,
        total_cols: int,
        header_levels: int,
        row_height: float,
        default_col_width: float,
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
        if row_height <= 0 or default_col_width <= 0:
            raise ValueError("Row height and default col width must be positive numbers")
        if viewport_width <= 0 or viewport_height <= 0:
            raise ValueError("Viewport dimensions must be positive numbers")
        if frozen_cols < 0 or frozen_cols > total_cols:
            raise ValueError("Frozen columns must be between 0 and total_cols")

        self.total_rows = total_rows
        self.total_cols = total_cols
        self.header_levels = header_levels
        self.row_height = float(row_height)
        self.default_col_width = float(default_col_width)
        self.viewport_width = float(viewport_width)
        self.viewport_height = float(viewport_height)
        self.frozen_cols = frozen_cols
        self.overscan_cols = overscan_cols

        self.total_header_height = self.header_levels * self.row_height

        # Base column widths (individual column base dimensions)
        self.col_base_widths: List[float] = [self.default_col_width] * self.total_cols

        self.scroll_x = 0.0

        # SQLite database for spatial R-Tree and hierarchical relations
        self.db = sqlite3.connect(":memory:")
        self._init_db()

        self.nodes: Dict[int, CollapsibleHeaderNode] = {}

    def _init_db(self):
        with self.db:
            # Spatial R-Tree: pixel_x0, pixel_x1 as coordinates
            self.db.execute("CREATE VIRTUAL TABLE header_rtree USING rtree(id, r0, r1, x0, x1)")
            self.db.execute("""
                CREATE TABLE header_metadata (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    level INTEGER NOT NULL,
                    c0 INTEGER NOT NULL,
                    c1 INTEGER NOT NULL,
                    parent_id INTEGER,
                    collapsible INTEGER NOT NULL,
                    is_collapsed INTEGER NOT NULL,
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
        parent_id: Optional[int] = None,
        collapsible: bool = False,
        summary_col_width: Optional[float] = None
    ) -> CollapsibleHeaderNode:
        """
        Registers a multi-level header node with optional collapsible accordion capability.
        """
        if type(node_id) is not int or node_id < 0:
            raise ValueError("Node ID must be non-negative integer")
        if not title or not isinstance(title, str):
            raise ValueError("Title must be non-empty string")
        if type(level) is not int or not (0 <= level < self.header_levels):
            raise ValueError(f"Level must be between 0 and {self.header_levels - 1}")
        if type(c0) is not int or type(c1) is not int or not (0 <= c0 < c1 <= self.total_cols):
            raise ValueError(f"Invalid column boundaries [c0={c0}, c1={c1})")
        if node_id in self.nodes:
            raise ValueError(f"Duplicate header node ID: {node_id}")

        r0 = float(level)
        r1 = float(level + 1)

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

        # Sibling overlap check within same level
        for n in self.nodes.values():
            if n.level == level:
                if not (c1 <= n.c0 or c0 >= n.c1):
                    raise ValueError(f"Header node [{c0}, {c1}) overlaps with sibling [{n.c0}, {n.c1})")

        node = CollapsibleHeaderNode(
            id=node_id,
            title=title,
            level=level,
            r0=int(r0),
            r1=int(r1),
            c0=c0,
            c1=c1,
            parent_id=parent_id,
            child_ids=[],
            collapsible=collapsible,
            is_collapsed=False,
            summary_col_width=summary_col_width if summary_col_width is not None else self.default_col_width
        )
        self.nodes[node_id] = node
        if parent_id is not None:
            self.nodes[parent_id].child_ids.append(node_id)

        with self.db:
            self.db.execute(
                "INSERT INTO header_metadata VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (node_id, title, level, c0, c1, parent_id, 1 if collapsible else 0, 0)
            )

        self._recompute_spatial_indices()
        return node

    def is_ancestor_collapsed(self, node_id: int) -> bool:
        """Checks if any ancestor of node_id is collapsed."""
        curr = self.nodes.get(node_id)
        while curr and curr.parent_id is not None:
            parent = self.nodes.get(curr.parent_id)
            if parent and parent.is_collapsed:
                return True
            curr = parent
        return False

    def get_effective_column_widths(self) -> List[float]:
        """
        Computes effective rendered pixel width for each column [0..total_cols-1].
        If a group [c0, c1) is collapsed:
        - The first column c0 takes the group's summary_col_width.
        - The internal detail columns c0+1..c1-1 are shrunk to 0 width (Zero-CLS collapsed).
        Nested collapse rules apply recursively.
        """
        widths = list(self.col_base_widths)

        # Process collapsed groups from top level to bottom level
        sorted_nodes = sorted(self.nodes.values(), key=lambda n: n.level)
        for node in sorted_nodes:
            if node.is_collapsed and not self.is_ancestor_collapsed(node.id):
                # The group collapses to summary_col_width
                # Column c0 takes summary width
                summary_w = float(node.summary_col_width if node.summary_col_width is not None else self.default_col_width)
                widths[node.c0] = summary_w
                for col in range(node.c0 + 1, node.c1):
                    widths[col] = 0.0

        return widths

    def get_column_pixel_offsets(self) -> List[Tuple[float, float]]:
        """
        Returns list of (pixel_start, pixel_end) for each column in order.
        """
        widths = self.get_effective_column_widths()
        offsets = []
        curr = 0.0
        for w in widths:
            offsets.append((curr, curr + w))
            curr += w
        return offsets

    def _recompute_spatial_indices(self):
        """
        Recalculates spatial R-tree bounds for all nodes based on current collapsed states.
        Guarantees zero layout shift / instant synchronization of spatial bounding boxes.
        """
        col_offsets = self.get_column_pixel_offsets()

        with self.db:
            self.db.execute("DELETE FROM header_rtree")
            for node in self.nodes.values():
                is_hidden = self.is_ancestor_collapsed(node.id)
                if is_hidden:
                    # When completely hidden by ancestor collapse, bounding box is zero-width
                    parent = self.nodes[node.parent_id]
                    x0 = col_offsets[parent.c0][0]
                    x1 = x0
                elif node.is_collapsed:
                    x0 = col_offsets[node.c0][0]
                    x1 = col_offsets[node.c0][1] # collapsed to summary width
                else:
                    x0 = col_offsets[node.c0][0]
                    x1 = col_offsets[node.c1 - 1][1]

                self.db.execute(
                    "INSERT INTO header_rtree VALUES (?, ?, ?, ?, ?)",
                    (node.id, float(node.r0), float(node.r1), float(x0), float(x1))
                )
                self.db.execute(
                    "UPDATE header_metadata SET is_collapsed = ? WHERE id = ?",
                    (1 if node.is_collapsed else 0, node.id)
                )

    def toggle_group(self, node_id: int) -> bool:
        """
        Toggles the collapsed state of a collapsible header node.
        Returns the new is_collapsed state.
        Raises ValueError if node is not collapsible or doesn't exist.
        """
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} does not exist")
        node = self.nodes[node_id]
        if not node.collapsible:
            raise ValueError(f"Node {node_id} ({node.title}) is not collapsible")

        return self.set_collapsed_state(node_id, not node.is_collapsed)

    def set_collapsed_state(self, node_id: int, collapsed: bool) -> bool:
        """
        Sets explicit collapsed state for a collapsible header node.
        Updates spatial index and clamps scroll.
        """
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} does not exist")
        node = self.nodes[node_id]
        if not node.collapsible:
            raise ValueError(f"Node {node_id} is not collapsible")

        node.is_collapsed = bool(collapsed)
        self._recompute_spatial_indices()
        self._clamp_scroll()
        return node.is_collapsed

    def get_layout_geometry(self) -> Dict[str, float]:
        """Calculates current dynamic layout geometry after collapse."""
        col_offsets = self.get_column_pixel_offsets()
        frozen_w = col_offsets[self.frozen_cols][0] if self.frozen_cols > 0 else 0.0
        total_w = col_offsets[-1][1] if col_offsets else 0.0
        body_total_w = max(0.0, total_w - frozen_w)
        body_viewport_w = max(0.0, self.viewport_width - frozen_w)
        max_scroll_x = max(0.0, body_total_w - body_viewport_w)

        return {
            "frozen_width": frozen_w,
            "total_width": total_w,
            "body_total_width": body_total_w,
            "body_viewport_width": body_viewport_w,
            "max_scroll_x": max_scroll_x
        }

    def _clamp_scroll(self):
        geom = self.get_layout_geometry()
        self.scroll_x = max(0.0, min(geom["max_scroll_x"], self.scroll_x))

    def scroll_to(self, x: float):
        geom = self.get_layout_geometry()
        self.scroll_x = max(0.0, min(geom["max_scroll_x"], float(x)))

    def query_visible_headers(self) -> List[VisibleCollapsibleHeaderItem]:
        """
        Queries all visible headers intersecting viewport using R-tree spatial query.
        Returns items with precise pixel coordinates, visibility clipping, and sticky titles.
        """
        geom = self.get_layout_geometry()
        frozen_w = geom["frozen_width"]
        body_vp_w = geom["body_viewport_width"]

        # Viewport segments:
        # 1. Frozen pane: [0, frozen_w)
        # 2. Scrolling body viewport: [frozen_w + scroll_x, frozen_w + scroll_x + body_vp_w)
        viewport_segments = []
        if frozen_w > 0:
            viewport_segments.append((0.0, frozen_w, True))
        if body_vp_w > 0:
            scroll_start = frozen_w + self.scroll_x
            scroll_end = scroll_start + body_vp_w
            viewport_segments.append((scroll_start, scroll_end, False))

        visible_node_ids: Set[int] = set()
        for v_x0, v_x1, is_froz in viewport_segments:
            hits = self.db.execute(
                "SELECT id FROM header_rtree WHERE r0 < ? AND r1 > ? AND x0 < ? AND x1 > ?",
                (self.header_levels, 0, v_x1, v_x0)
            ).fetchall()
            for (nid,) in hits:
                visible_node_ids.add(nid)

        sorted_nodes = sorted(
            [self.nodes[nid] for nid in visible_node_ids],
            key=lambda n: (n.level, n.c0)
        )

        col_offsets = self.get_column_pixel_offsets()
        results: List[VisibleCollapsibleHeaderItem] = []

        for node in sorted_nodes:
            is_hidden = self.is_ancestor_collapsed(node.id)

            if is_hidden:
                # Completely hidden by collapsed ancestor
                parent = self.nodes[node.parent_id]
                px_start = col_offsets[parent.c0][0]
                px_w = 0.0
            elif node.is_collapsed:
                px_start = col_offsets[node.c0][0]
                px_w = col_offsets[node.c0][1] - px_start
            else:
                px_start = col_offsets[node.c0][0]
                px_end = col_offsets[node.c1 - 1][1]
                px_w = px_end - px_start

            # Determine clipping against frozen or scroll pane
            is_in_frozen = (col_offsets[node.c1 - 1][1] <= frozen_w)
            if is_in_frozen:
                active_view_x0 = 0.0
                active_view_x1 = frozen_w
            else:
                active_view_x0 = frozen_w + self.scroll_x
                active_view_x1 = frozen_w + self.scroll_x + body_vp_w

            clip_x0 = max(px_start, active_view_x0)
            clip_x1 = min(px_start + px_w, active_view_x1)
            clip_w = max(0.0, clip_x1 - clip_x0)

            is_partial = (clip_w > 0 and clip_w < px_w)
            is_full = (clip_w == px_w and px_w > 0)

            # Progressive sticky title calculation
            sticky_x = 0.0
            if not is_in_frozen and not is_hidden and px_w > 0:
                if active_view_x0 > px_start:
                    max_sticky = max(0.0, px_w - self.default_col_width)
                    offset = active_view_x0 - px_start
                    sticky_x = min(offset, max_sticky)

            results.append(VisibleCollapsibleHeaderItem(
                id=node.id,
                title=node.title,
                level=node.level,
                logical_bounds=[node.r0, node.c0, node.r1, node.c1],
                pixel_x=px_start,
                pixel_width=px_w,
                is_collapsed=node.is_collapsed,
                collapsible=node.collapsible,
                is_hidden_by_parent=is_hidden,
                clip_pixel_x=clip_x0,
                clip_pixel_width=clip_w,
                is_partially_clipped=is_partial,
                is_fully_visible=is_full,
                parent_id=node.parent_id,
                child_ids=list(node.child_ids),
                sticky_offset_x=sticky_x
            ))

        return results

    def compute_render_manifest(self) -> Dict[str, Any]:
        """
        Produces client-ready composite manifest including layout geometry,
        accordion states, visible headers, and effective column metrics.
        """
        geom = self.get_layout_geometry()
        visible = self.query_visible_headers()
        effective_widths = self.get_effective_column_widths()

        return {
            "geometry": geom,
            "scroll_x": self.scroll_x,
            "effective_column_count": len(effective_widths),
            "rendered_total_width": sum(effective_widths),
            "visible_headers_count": len(visible),
            "visible_headers": [
                {
                    "id": item.id,
                    "title": item.title,
                    "level": item.level,
                    "pixel_x": item.pixel_x,
                    "pixel_width": item.pixel_width,
                    "clip_x": item.clip_pixel_x,
                    "clip_width": item.clip_pixel_width,
                    "is_collapsed": item.is_collapsed,
                    "collapsible": item.collapsible,
                    "is_hidden_by_parent": item.is_hidden_by_parent,
                    "sticky_offset_x": item.sticky_offset_x,
                    "parent_id": item.parent_id
                }
                for item in visible
            ]
        }
