"""
GPU-Accelerated Cell Selection Box & Marquee Drag Math (UIUX-027).

Provides mathematical camera inverse transformations, dynamic marquee box calculation,
cell collision intersection checks against virtual grid layouts, and GPU instanced
selection border overlay serialization for high-performance WebGL/WebGPU 2D grids.
"""

from dataclasses import dataclass
import math
import struct
from typing import List, Tuple, Optional, Dict, Any

# 12 floats = 48 bytes per instance:
# float32 min_x, min_y, max_x, max_y (16 bytes) - world space bounding box
# float32 border_width, corner_radius (8 bytes)
# float32 r, g, b, a (16 bytes) - border stroke color
# float32 fill_r, fill_g, fill_b, fill_a (16 bytes) -> wait, let's keep exact layout
# Layout:
# a_box_rect: min_x, min_y, max_x, max_y (vec4 - 16 bytes)
# a_box_style: border_width, corner_radius, fill_opacity, stroke_opacity (vec4 - 16 bytes)
# a_box_color: r, g, b, is_active (vec4 - 16 bytes)
# Total stride: 48 bytes
SELECTION_BOX_INSTANCE_STRIDE_BYTES = 48


@dataclass
class SelectionRect:
    min_x: float
    min_y: float
    max_x: float
    max_y: float

    @property
    def width(self) -> float:
        return max(0.0, self.max_x - self.min_x)

    @property
    def height(self) -> float:
        return max(0.0, self.max_y - self.min_y)

    def contains_point(self, px: float, py: float) -> bool:
        return (self.min_x <= px <= self.max_x) and (self.min_y <= py <= self.max_y)

    def intersects(self, other: 'SelectionRect') -> bool:
        return not (
            self.max_x < other.min_x or
            self.min_x > other.max_x or
            self.max_y < other.min_y or
            self.min_y > other.max_y
        )


@dataclass
class CellRange:
    start_row: int
    start_col: int
    end_row: int
    end_col: int

    def normalize(self) -> 'CellRange':
        r1, r2 = sorted([self.start_row, self.end_row])
        c1, c2 = sorted([self.start_col, self.end_col])
        return CellRange(r1, c1, r2, c2)

    def count(self) -> int:
        norm = self.normalize()
        return (norm.end_row - norm.start_row + 1) * (norm.end_col - norm.start_col + 1)


class MarqueeSelectionEngine:
    """
    Manages continuous 2D pointer dragging, screen-to-world inverse projection,
    marquee rectangle calculation, and spatial collision queries against virtual grid cells.
    """

    def __init__(
        self,
        default_row_height: float = 28.0,
        default_col_width: float = 100.0,
        viewport_width: float = 1280.0,
        viewport_height: float = 720.0
    ):
        self.default_row_height = default_row_height
        self.default_col_width = default_col_width
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height

        # Drag state
        self.is_dragging = False
        self.drag_start_screen: Optional[Tuple[float, float]] = None
        self.drag_current_screen: Optional[Tuple[float, float]] = None
        self.drag_start_world: Optional[Tuple[float, float]] = None
        self.drag_current_world: Optional[Tuple[float, float]] = None

        # Camera state (matching UIUX-025 PinchZoomCamera)
        self.camera_scroll_x: float = 0.0
        self.camera_scroll_y: float = 0.0
        self.camera_zoom: float = 1.0

        # Active cell selection
        self.active_cell: Optional[Tuple[int, int]] = None
        self.selected_range: Optional[CellRange] = None

    def update_camera(self, scroll_x: float, scroll_y: float, zoom: float) -> None:
        self.camera_scroll_x = scroll_x
        self.camera_scroll_y = scroll_y
        self.camera_zoom = max(0.1, zoom)

    def screen_to_world(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """
        Invert 2D orthographic camera projection:
        world = scroll + screen / zoom
        """
        world_x = self.camera_scroll_x + (screen_x / self.camera_zoom)
        world_y = self.camera_scroll_y + (screen_y / self.camera_zoom)
        return world_x, world_y

    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[float, float]:
        """
        Forward 2D orthographic projection:
        screen = (world - scroll) * zoom
        """
        screen_x = (world_x - self.camera_scroll_x) * self.camera_zoom
        screen_y = (world_y - self.camera_scroll_y) * self.camera_zoom
        return screen_x, screen_y

    def world_to_cell(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """
        Maps continuous world coordinates to row and column indices.
        """
        col = max(0, int(world_x // self.default_col_width))
        row = max(0, int(world_y // self.default_row_height))
        return row, col

    def cell_to_world_bounds(self, row: int, col: int) -> SelectionRect:
        """
        Computes the world bounding box of a cell.
        """
        min_x = col * self.default_col_width
        min_y = row * self.default_row_height
        max_x = min_x + self.default_col_width
        max_y = min_y + self.default_row_height
        return SelectionRect(min_x, min_y, max_x, max_y)

    def start_drag(self, screen_x: float, screen_y: float) -> None:
        """
        Initiates pointer down marquee drag.
        """
        self.is_dragging = True
        self.drag_start_screen = (screen_x, screen_y)
        self.drag_current_screen = (screen_x, screen_y)

        wx, wy = self.screen_to_world(screen_x, screen_y)
        self.drag_start_world = (wx, wy)
        self.drag_current_world = (wx, wy)

        r, c = self.world_to_cell(wx, wy)
        self.active_cell = (r, c)
        self.selected_range = CellRange(r, c, r, c)

    def update_drag(self, screen_x: float, screen_y: float) -> Optional[SelectionRect]:
        """
        Updates pointer position during drag.
        Returns the current marquee world rectangle.
        """
        if not self.is_dragging:
            return None

        self.drag_current_screen = (screen_x, screen_y)
        wx, wy = self.screen_to_world(screen_x, screen_y)
        self.drag_current_world = (wx, wy)

        r, c = self.world_to_cell(wx, wy)
        if self.active_cell is not None:
            self.selected_range = CellRange(
                self.active_cell[0],
                self.active_cell[1],
                r,
                c
            )

        return self.get_marquee_world_rect()

    def end_drag(self) -> Optional[CellRange]:
        """
        Finalizes drag operation. Returns normalized selected cell range.
        """
        self.is_dragging = False
        if self.selected_range is not None:
            norm = self.selected_range.normalize()
            self.selected_range = norm
            return norm
        return None

    def get_marquee_world_rect(self) -> Optional[SelectionRect]:
        """
        Computes the normalized world bounding rectangle of the marquee selection.
        """
        if not self.is_dragging or self.drag_start_world is None or self.drag_current_world is None:
            return None

        x1, y1 = self.drag_start_world
        x2, y2 = self.drag_current_world

        min_x, max_x = sorted([x1, x2])
        min_y, max_y = sorted([y1, y2])

        return SelectionRect(min_x, min_y, max_x, max_y)

    def get_marquee_screen_rect(self) -> Optional[SelectionRect]:
        """
        Computes the normalized screen rectangle of the active marquee.
        """
        if not self.is_dragging or self.drag_start_screen is None or self.drag_current_screen is None:
            return None

        sx1, sy1 = self.drag_start_screen
        sx2, sy2 = self.drag_current_screen

        min_x, max_x = sorted([sx1, sx2])
        min_y, max_y = sorted([sy1, sy2])

        return SelectionRect(min_x, min_y, max_x, max_y)

    def compute_intersected_cell_range(self) -> Optional[CellRange]:
        """
        Computes the discrete cell range [r_min..r_max, c_min..c_max]
        covered by the current marquee world rectangle.
        """
        m_rect = self.get_marquee_world_rect()
        if m_rect is None:
            return None

        c_min = max(0, int(m_rect.min_x // self.default_col_width))
        c_max = max(0, int((m_rect.max_x - 0.0001) // self.default_col_width))
        r_min = max(0, int(m_rect.min_y // self.default_row_height))
        r_max = max(0, int((m_rect.max_y - 0.0001) // self.default_row_height))

        return CellRange(r_min, c_min, r_max, c_max)

    def get_range_world_bounds(self, cell_range: CellRange) -> SelectionRect:
        """
        Computes the continuous world bounding box spanning the given cell range.
        """
        norm = cell_range.normalize()
        min_x = norm.start_col * self.default_col_width
        min_y = norm.start_row * self.default_row_height
        max_x = (norm.end_col + 1) * self.default_col_width
        max_y = (norm.end_row + 1) * self.default_row_height
        return SelectionRect(min_x, min_y, max_x, max_y)

    def build_gpu_selection_instance(
        self,
        rect: SelectionRect,
        border_width: float = 2.0,
        corner_radius: float = 0.0,
        fill_opacity: float = 0.12,
        stroke_opacity: float = 0.95,
        color_rgb: Tuple[float, float, float] = (0.05, 0.45, 0.95),  # Accent blue
        is_active: bool = True
    ) -> bytes:
        """
        Packs a 48-byte GPU instanced vertex buffer representation for a selection quad:
        - vec4 a_box_rect: [min_x, min_y, max_x, max_y] (16 bytes)
        - vec4 a_box_style: [border_width, corner_radius, fill_opacity, stroke_opacity] (16 bytes)
        - vec4 a_box_color: [r, g, b, is_active (1.0 or 0.0)] (16 bytes)
        """
        r, g, b = color_rgb
        packed = struct.pack(
            '<4f4f4f',
            float(rect.min_x), float(rect.min_y), float(rect.max_x), float(rect.max_y),
            float(border_width), float(corner_radius), float(fill_opacity), float(stroke_opacity),
            float(r), float(g), float(b), 1.0 if is_active else 0.0
        )
        assert len(packed) == SELECTION_BOX_INSTANCE_STRIDE_BYTES
        return packed

    def serialize_active_selection_instances(self) -> bytes:
        """
        Serializes both the active cell range selection box and the dynamic marquee drag box (if any)
        into a contiguous GPU instanced buffer.
        """
        instances = bytearray()

        # 1. Selected range bounding box
        if self.selected_range is not None:
            range_bounds = self.get_range_world_bounds(self.selected_range)
            range_bytes = self.build_gpu_selection_instance(
                rect=range_bounds,
                border_width=2.0,
                corner_radius=2.0,
                fill_opacity=0.08,
                stroke_opacity=0.95,
                color_rgb=(0.09, 0.45, 0.95),  # Cobalt Blue
                is_active=True
            )
            instances.extend(range_bytes)

        # 2. Dynamic marquee box during active drag
        if self.is_dragging:
            marquee_bounds = self.get_marquee_world_rect()
            if marquee_bounds is not None and (marquee_bounds.width > 0 or marquee_bounds.height > 0):
                marquee_bytes = self.build_gpu_selection_instance(
                    rect=marquee_bounds,
                    border_width=1.0,
                    corner_radius=0.0,
                    fill_opacity=0.15,
                    stroke_opacity=0.75,
                    color_rgb=(0.15, 0.65, 1.0),  # Cyan marquee
                    is_active=False
                )
                instances.extend(marquee_bytes)

        return bytes(instances)
