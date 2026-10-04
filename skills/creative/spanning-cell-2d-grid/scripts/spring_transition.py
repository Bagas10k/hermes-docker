"""
Spring Physics Width Interpolation on Collapsible Column Transitions.

Implements continuous damped spring physics based on Hooke's Law:
    F = -k * (x - target) - c * v
    a = F / m
    v(t + dt) = v(t) + a * dt
    x(t + dt) = x(t) + v(t + dt) * dt

Provides:
- ColumnSpringInterpolator: Multi-column continuous spring dynamics engine
- SpringTransitionState: Tracking position, target, velocity, and settle status
- Integration with CollapsibleHierarchicalGrid:
  * Sub-frame intermediate column widths
  * Real-time SQLite R-Tree spatial boundary sync during animation
  * Frame-by-frame visible header spatial query and progressive sticky title recalculation
  * Zero-CLS virtual DOM layout coordination
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from collapsible_frozen_header import CollapsibleHierarchicalGrid, VisibleCollapsibleHeaderItem

@dataclass
class SpringConfig:
    stiffness: float = 240.0    # k in N/m
    damping: float = 26.0       # c in N*s/m (critically damped near 2*sqrt(m*k))
    mass: float = 1.0           # m in kg
    precision_threshold: float = 0.1   # Pixel distance threshold to snap
    velocity_threshold: float = 0.5    # Pixel/second velocity threshold to snap

    def __post_init__(self):
        if self.stiffness <= 0:
            raise ValueError("Stiffness (k) must be positive")
        if self.damping <= 0:
            raise ValueError("Damping (c) must be positive")
        if self.mass <= 0:
            raise ValueError("Mass (m) must be positive")
        if self.precision_threshold <= 0:
            raise ValueError("Precision threshold must be positive")
        if self.velocity_threshold <= 0:
            raise ValueError("Velocity threshold must be positive")

@dataclass
class ColumnSpringState:
    col_idx: int
    current_width: float
    target_width: float
    velocity: float = 0.0
    is_settled: bool = True

class ColumnSpringInterpolator:
    """
    Manages continuous spring physics for column widths in a grid.
    Steps physics using symplectic Euler integration for stability.
    """
    def __init__(self, initial_widths: List[float], config: Optional[SpringConfig] = None):
        if not initial_widths:
            raise ValueError("initial_widths cannot be empty")
        for w in initial_widths:
            if w < 0:
                raise ValueError("Initial width cannot be negative")

        self.config = config or SpringConfig()
        self.springs: Dict[int, ColumnSpringState] = {}
        for idx, w in enumerate(initial_widths):
            self.springs[idx] = ColumnSpringState(
                col_idx=idx,
                current_width=float(w),
                target_width=float(w),
                velocity=0.0,
                is_settled=True
            )

    @property
    def is_all_settled(self) -> bool:
        return all(s.is_settled for s in self.springs.values())

    def set_target_width(self, col_idx: int, target: float):
        if col_idx not in self.springs:
            raise KeyError(f"Column index {col_idx} not found")
        if target < 0:
            raise ValueError("Target width cannot be negative")

        s = self.springs[col_idx]
        s.target_width = float(target)
        if abs(s.current_width - s.target_width) > self.config.precision_threshold:
            s.is_settled = False

    def set_target_widths(self, targets: Dict[int, float]):
        for col_idx, target in targets.items():
            self.set_target_width(col_idx, target)

    def step(self, dt: float) -> bool:
        """
        Advances the spring simulation by dt seconds.
        Returns True if any spring is still animating, False if all settled.
        """
        if dt <= 0:
            raise ValueError("dt must be positive")

        # Clamp dt to prevent explosion on large frames
        clamped_dt = min(dt, 0.05)
        all_settled = True

        k = self.config.stiffness
        c = self.config.damping
        m = self.config.mass
        p_thresh = self.config.precision_threshold
        v_thresh = self.config.velocity_threshold

        for s in self.springs.values():
            if s.is_settled:
                continue

            displacement = s.current_width - s.target_width
            spring_force = -k * displacement
            damping_force = -c * s.velocity
            total_force = spring_force + damping_force
            accel = total_force / m

            # Symplectic Euler integration
            s.velocity += accel * clamped_dt
            s.current_width += s.velocity * clamped_dt

            # Prevent physical negative width
            if s.current_width < 0.0:
                s.current_width = 0.0
                s.velocity = 0.0

            # Settle test
            dist = abs(s.current_width - s.target_width)
            speed = abs(s.velocity)
            if dist <= p_thresh and speed <= v_thresh:
                s.current_width = s.target_width
                s.velocity = 0.0
                s.is_settled = True
            else:
                all_settled = False

        return not all_settled

    def get_current_widths(self) -> List[float]:
        return [self.springs[i].current_width for i in range(len(self.springs))]

    def snap_to_target(self):
        """Immediately snaps all springs to target width."""
        for s in self.springs.values():
            s.current_width = s.target_width
            s.velocity = 0.0
            s.is_settled = True


class AnimatedCollapsibleGrid(CollapsibleHierarchicalGrid):
    """
    Subclass of CollapsibleHierarchicalGrid with continuous spring physics
    for smooth accordion expand/collapse transitions.
    Synchronizes intermediate column widths with SQLite R-Tree spatial index.
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
        overscan_cols: int = 2,
        spring_config: Optional[SpringConfig] = None
    ):
        super().__init__(
            total_rows=total_rows,
            total_cols=total_cols,
            header_levels=header_levels,
            row_height=row_height,
            default_col_width=default_col_width,
            viewport_width=viewport_width,
            viewport_height=viewport_height,
            frozen_cols=frozen_cols,
            overscan_cols=overscan_cols
        )
        base_widths = self.get_effective_column_widths()
        self.interpolator = ColumnSpringInterpolator(base_widths, spring_config)
        self.is_animating: bool = False

    def toggle_collapse_animated(self, node_id: int) -> bool:
        """
        Initiates a smooth animated expand/collapse transition for node_id.
        Sets logical state and assigns spring targets.
        """
        if node_id not in self.nodes:
            raise KeyError(f"Header node id {node_id} does not exist")
        node = self.nodes[node_id]
        if not node.collapsible:
            raise ValueError(f"Header node '{node.title}' (id={node_id}) is not marked as collapsible")

        new_collapsed_state = not node.is_collapsed
        node.is_collapsed = new_collapsed_state

        # Update metadata in DB
        with self.db:
            self.db.execute(
                "UPDATE header_metadata SET is_collapsed = ? WHERE id = ?",
                (1 if new_collapsed_state else 0, node_id)
            )

        # Calculate logical target widths for all columns
        target_effective_widths = self.get_effective_column_widths()
        for c_idx, tw in enumerate(target_effective_widths):
            self.interpolator.set_target_width(c_idx, tw)

        self.is_animating = not self.interpolator.is_all_settled
        return new_collapsed_state

    def step_animation(self, dt: float = 1.0 / 60.0) -> bool:
        """
        Advances the spring physics by dt seconds and syncs the spatial R-Tree.
        Returns True if animation is still running, False if settled.
        """
        still_animating = self.interpolator.step(dt)
        self.is_animating = still_animating

        # Update spatial R-Tree with current interpolated widths
        self._sync_interpolated_rtree()
        return still_animating

    def get_interpolated_column_widths(self) -> List[float]:
        return self.interpolator.get_current_widths()

    def get_interpolated_pixel_offsets(self) -> List[Tuple[float, float]]:
        """
        Returns [(start_px, end_px), ...] based on current spring positions.
        """
        widths = self.get_interpolated_column_widths()
        offsets: List[Tuple[float, float]] = []
        cur_x = 0.0
        for w in widths:
            offsets.append((cur_x, cur_x + w))
            cur_x += w
        return offsets

    def _sync_interpolated_rtree(self):
        """
        Updates SQLite R-Tree spatial coordinates with sub-frame interpolated positions.
        """
        offsets = self.get_interpolated_pixel_offsets()
        with self.db:
            for node in self.nodes.values():
                is_hidden = self.is_ancestor_collapsed(node.id)
                if is_hidden:
                    parent = self.nodes[node.parent_id]
                    px_start = offsets[parent.c0][0]
                    px_end = px_start
                elif node.is_collapsed:
                    px_start = offsets[node.c0][0]
                    px_end = offsets[node.c0][1]
                else:
                    px_start = offsets[node.c0][0]
                    px_end = offsets[node.c1 - 1][1]

                self.db.execute("DELETE FROM header_rtree WHERE id = ?", (node.id,))
                self.db.execute(
                    "INSERT INTO header_rtree(id, r0, r1, x0, x1) VALUES (?, ?, ?, ?, ?)",
                    (node.id, node.r0, node.r1, px_start, px_end)
                )

    def query_visible_headers_interpolated(self) -> List[VisibleCollapsibleHeaderItem]:
        """
        Queries and clips headers against viewport using current spring interpolated positions.
        """
        col_offsets = self.get_interpolated_pixel_offsets()

        frozen_w = 0.0
        if self.frozen_cols > 0:
            frozen_w = col_offsets[self.frozen_cols - 1][1]

        body_vp_w = max(0.0, self.viewport_width - frozen_w)
        v_x0 = max(0.0, frozen_w + self.scroll_x)
        v_x1 = frozen_w + self.scroll_x + body_vp_w

        visible_node_ids = set()

        with self.db:
            if self.frozen_cols > 0:
                frozen_hits = self.db.execute(
                    "SELECT id FROM header_rtree WHERE r0 < ? AND r1 > ? AND x0 < ? AND x1 > ?",
                    (self.header_levels, 0, frozen_w, 0.0)
                ).fetchall()
                for (nid,) in frozen_hits:
                    visible_node_ids.add(nid)

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

        results: List[VisibleCollapsibleHeaderItem] = []
        for node in sorted_nodes:
            is_hidden = self.is_ancestor_collapsed(node.id)

            if is_hidden:
                parent = self.nodes[node.parent_id]
                px_start = col_offsets[parent.c0][0]
                px_w = 0.0
            elif node.is_collapsed:
                px_start = col_offsets[node.c0][0]
                px_w = max(0.0, col_offsets[node.c0][1] - px_start)
            else:
                px_start = col_offsets[node.c0][0]
                px_end = col_offsets[node.c1 - 1][1]
                px_w = max(0.0, px_end - px_start)

            # Determine clipping
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

            # Sticky title calculation
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

    def compute_render_manifest_animated(self) -> Dict[str, Any]:
        """
        Produces client-ready manifest including real-time animation state.
        """
        widths = self.get_interpolated_column_widths()
        visible = self.query_visible_headers_interpolated()
        geom = self.get_layout_geometry()

        return {
            "geometry": geom,
            "scroll_x": self.scroll_x,
            "is_animating": self.is_animating,
            "effective_column_count": len(widths),
            "rendered_total_width": sum(widths),
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
                    "sticky_offset_x": item.sticky_offset_x
                }
                for item in visible
            ]
        }
