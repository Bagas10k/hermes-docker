"""
WebGL/WebGPU Instanced Quad Rendering Fallback for Massive Cell Budgets (UIUX-022).

Provides:
- InstancedCellGeometry: Metadata representing a visible grid cell for GPU batching.
- InstancedQuadBufferGenerator: Packs per-instance cell geometry into contiguous
  binary vertex attribute buffers (Float32Array / Uint8Array) matching standard WebGL2/WebGPU layouts.
- GridRenderPipelineDecider: Deterministic cost model comparing DOM vs Instanced Canvas/GPU
  rendering based on visible active cell count, pixel density (DPR), and frame budget (16.6ms).
- GpuInstancedGridRenderer: Orchestrates R-Tree spatial indexing, viewport culling,
  binary buffer generation, and manifest generation for WebGL2/WebGPU shaders.
"""

import struct
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from spanning_grid import SpanIndex

# Standard GPU Instance Stride:
# vec4 a_pos_size   : [x, y, width, height] (4 * float32 = 16 bytes)
# vec4 a_bg_color   : [r, g, b, a]           (4 * uint8   = 4 bytes, normalized)
# vec4 a_border     : [border_w, r, g, b]    (4 * uint8   = 4 bytes, normalized)
# vec4 a_text_uv    : [atlas_u, atlas_v, atlas_w, atlas_h] (4 * float32 = 16 bytes)
# vec2 a_clip_rect0 : [clip_x0, clip_y0]     (2 * float32 = 8 bytes)
# vec2 a_clip_rect1 : [clip_x1, clip_y1]     (2 * float32 = 8 bytes)
# Total stride per instance = 56 bytes.
INSTANCE_STRIDE_BYTES = 56
DOM_BUDGET_CEILING = 4096


@dataclass
class InstancedCell:
    cell_id: int
    x: float
    y: float
    width: float
    height: float
    bg_color: Tuple[int, int, int, int] = (255, 255, 255, 255) # RGBA 0-255
    border_color: Tuple[int, int, int] = (226, 232, 240)       # RGB 0-255
    border_width: int = 1                                      # Pixels
    text_atlas_uv: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0) # u, v, w, h
    clip_bounds: Tuple[float, float, float, float] = (0.0, 0.0, 100000.0, 100000.0) # x0, y0, x1, y1
    is_merged: bool = False
    is_frozen: bool = False

    def __post_init__(self):
        if self.width <= 0 or self.height <= 0:
            raise ValueError(f"Cell dimensions must be strictly positive: {self.width}x{self.height}")
        for c in self.bg_color:
            if not (0 <= c <= 255):
                raise ValueError("bg_color components must be in [0, 255]")
        for c in self.border_color:
            if not (0 <= c <= 255):
                raise ValueError("border_color components must be in [0, 255]")


@dataclass
class RenderStrategyDecision:
    mode: str                    # "DOM" or "INSTANCED_GPU"
    active_cell_count: int
    cell_budget_ceiling: int
    estimated_dom_cost_ms: float
    estimated_gpu_cost_ms: float
    reason: str


class GridRenderPipelineDecider:
    """
    Evaluates system constraints and decides whether to use DOM recycling or GPU instancing.
    Amdahl and DOM throughput model:
    - DOM reflow/reconciliation for N nodes scales O(N) with high memory overhead.
    - Each DOM element consumes ~1.2KB - 2KB in V8 / Blink DOM tree.
    - Above 4096 cells (e.g. 8K Retina viewports or high-density grids), DOM reconciliation
      exceeds 16.6ms (60 FPS limit), causing frame drops and GC pressure.
    - Instanced GPU rendering dispatches 1 draw call (glDrawArraysInstanced) with fixed O(1) CPU overhead.
    """
    def __init__(self, dom_ceiling: int = DOM_BUDGET_CEILING):
        self.dom_ceiling = dom_ceiling

    def evaluate(self, active_cells: int, dpr: float = 1.0) -> RenderStrategyDecision:
        if active_cells < 0:
            raise ValueError("Active cell count cannot be negative")

        # Empirical model: DOM reconciliation takes ~0.005ms per node + 1.2ms base style calc
        # Scaled by DPR if CSS pixel layout complexity increases
        est_dom_ms = 1.2 + (active_cells * 0.0048 * (1.0 + 0.1 * (dpr - 1.0)))

        # GPU Instancing: Binary buffer packing (~0.00015ms per instance) + 1 Draw Call dispatch (~0.25ms)
        est_gpu_ms = 0.25 + (active_cells * 0.00018)

        if active_cells > self.dom_ceiling:
            return RenderStrategyDecision(
                mode="INSTANCED_GPU",
                active_cell_count=active_cells,
                cell_budget_ceiling=self.dom_ceiling,
                estimated_dom_cost_ms=est_dom_ms,
                estimated_gpu_cost_ms=est_gpu_ms,
                reason=f"Active cell count ({active_cells}) exceeds DOM budget ceiling ({self.dom_ceiling}). "
                       f"GPU instancing preserves 60 FPS ({est_gpu_ms:.2f}ms vs {est_dom_ms:.2f}ms DOM)."
            )
        else:
            return RenderStrategyDecision(
                mode="DOM",
                active_cell_count=active_cells,
                cell_budget_ceiling=self.dom_ceiling,
                estimated_dom_cost_ms=est_dom_ms,
                estimated_gpu_cost_ms=est_gpu_ms,
                reason=f"Active cell count ({active_cells}) within DOM budget ceiling ({self.dom_ceiling}). "
                       f"DOM recycling provides native accessibility and text selection."
            )


class InstancedQuadBufferGenerator:
    """
    Packs a collection of InstancedCell items into contiguous binary buffers.
    Format is directly compatible with WebGL2 (UNSIGNED_BYTE / FLOAT vertex attrib pointers)
    and WebGPU (GPUVertexBufferLayout).
    """
    def __init__(self, capacity: int = 8192):
        self.capacity = capacity

    def pack_instances(self, cells: List[InstancedCell]) -> bytes:
        """
        Packs N cells into binary bytes of length len(cells) * 56.
        Layout per instance (56 bytes, little-endian):
        offset 00: 4 floats (16B) -> x, y, width, height
        offset 16: 4 uint8  (04B) -> bg_r, bg_g, bg_b, bg_a
        offset 20: 4 uint8  (04B) -> border_w, b_r, b_g, b_b
        offset 24: 4 floats (16B) -> atlas_u, atlas_v, atlas_w, atlas_h
        offset 40: 2 floats (08B) -> clip_x0, clip_y0
        offset 48: 2 floats (08B) -> clip_x1, clip_y1
        """
        buffer = bytearray()
        for c in cells:
            # 16 bytes: pos & size
            buffer.extend(struct.pack("<4f", c.x, c.y, c.width, c.height))
            # 4 bytes: bg color
            buffer.extend(struct.pack("<4B", *c.bg_color))
            # 4 bytes: border width & color
            buffer.extend(struct.pack("<4B", c.border_width, *c.border_color))
            # 16 bytes: text UV
            buffer.extend(struct.pack("<4f", *c.text_atlas_uv))
            # 8 bytes: clip rect min
            buffer.extend(struct.pack("<2f", c.clip_bounds[0], c.clip_bounds[1]))
            # 8 bytes: clip rect max
            buffer.extend(struct.pack("<2f", c.clip_bounds[2], c.clip_bounds[3]))

        return bytes(buffer)

    def unpack_instance(self, raw_bytes: bytes, index: int) -> Dict[str, Any]:
        """
        Helper for unit tests and verification to unpack binary instance data.
        """
        offset = index * INSTANCE_STRIDE_BYTES
        if offset + INSTANCE_STRIDE_BYTES > len(raw_bytes):
            raise IndexError("Instance index out of range")

        chunk = raw_bytes[offset:offset + INSTANCE_STRIDE_BYTES]
        x, y, w, h = struct.unpack_from("<4f", chunk, 0)
        bg = struct.unpack_from("<4B", chunk, 16)
        bw, br, bg_b, bb = struct.unpack_from("<4B", chunk, 20)
        u, v, tw, th = struct.unpack_from("<4f", chunk, 24)
        cx0, cy0 = struct.unpack_from("<2f", chunk, 40)
        cx1, cy1 = struct.unpack_from("<2f", chunk, 48)

        return {
            "x": x, "y": y, "width": w, "height": h,
            "bg_color": bg,
            "border_width": bw,
            "border_color": (br, bg_b, bb),
            "text_uv": (u, v, tw, th),
            "clip_bounds": (cx0, cy0, cx1, cy1)
        }


class GpuInstancedGridPipeline:
    """
    Coordinates spatial queries on spanning grids with the Instanced Quad GPU buffer generator.
    Handles:
    - Viewport frustum calculation
    - Regular unmerged cell instancing
    - Merged cell R-Tree spatial query integration
    - Frozen pane multi-quadrant separation with clipping planes
    - Binary VBO generation & manifest output
    """
    def __init__(
        self,
        total_rows: int,
        total_cols: int,
        row_height: float,
        col_width: float,
        frozen_rows: int = 0,
        frozen_cols: int = 0,
        dom_ceiling: int = DOM_BUDGET_CEILING
    ):
        self.total_rows = total_rows
        self.total_cols = total_cols
        self.row_height = row_height
        self.col_width = col_width
        self.frozen_rows = frozen_rows
        self.frozen_cols = frozen_cols

        self.decider = GridRenderPipelineDecider(dom_ceiling=dom_ceiling)
        self.generator = InstancedQuadBufferGenerator()
        self.span_index = SpanIndex(total_rows, total_cols)

    def add_merged_cell(self, merge_id: int, r0: int, c0: int, r1: int, c1: int):
        self.span_index.add(merge_id, r0, c0, r1, c1)

    def build_frame_manifest(
        self,
        scroll_x: float,
        scroll_y: float,
        viewport_width: float,
        viewport_height: float,
        dpr: float = 1.0
    ) -> Dict[str, Any]:
        """
        Determines visible cells in the viewport, decides rendering pipeline,
        and generates either DOM payload or GPU instanced binary buffer.
        """
        # Calculate row & column ranges in scroll body
        # Frozen bounds
        frozen_w = self.frozen_cols * self.col_width
        frozen_h = self.frozen_rows * self.row_height

        scroll_view_w = max(0.0, viewport_width - frozen_w)
        scroll_view_h = max(0.0, viewport_height - frozen_h)

        c_start = int(scroll_x // self.col_width)
        c_end = min(self.total_cols, int((scroll_x + scroll_view_w + self.col_width - 1) // self.col_width))
        r_start = int(scroll_y // self.row_height)
        r_end = min(self.total_rows, int((scroll_y + scroll_view_h + self.row_height - 1) // self.row_height))

        scroll_cols_count = max(0, c_end - c_start)
        scroll_rows_count = max(0, r_end - r_start)

        frozen_cell_count = (self.frozen_rows * self.total_cols) + (self.frozen_cols * self.total_rows)
        active_cell_count = (scroll_cols_count * scroll_rows_count) + frozen_cell_count

        decision = self.decider.evaluate(active_cell_count, dpr=dpr)

        cells: List[InstancedCell] = []

        if decision.mode == "INSTANCED_GPU":
            # Generate InstancedCell records
            # 1. Pinned Top-Left Corner (if any)
            if self.frozen_rows > 0 and self.frozen_cols > 0:
                for r in range(self.frozen_rows):
                    for c in range(self.frozen_cols):
                        cells.append(InstancedCell(
                            cell_id=r * self.total_cols + c,
                            x=c * self.col_width,
                            y=r * self.row_height,
                            width=self.col_width,
                            height=self.row_height,
                            bg_color=(248, 250, 252, 255),
                            border_color=(203, 213, 225),
                            clip_bounds=(0.0, 0.0, frozen_w, frozen_h),
                            is_frozen=True
                        ))

            # 2. Frozen Header Row
            if self.frozen_rows > 0:
                for r in range(self.frozen_rows):
                    for c in range(c_start, c_end):
                        cells.append(InstancedCell(
                            cell_id=r * self.total_cols + c,
                            x=frozen_w + (c * self.col_width - scroll_x),
                            y=r * self.row_height,
                            width=self.col_width,
                            height=self.row_height,
                            bg_color=(241, 245, 249, 255),
                            border_color=(203, 213, 225),
                            clip_bounds=(frozen_w, 0.0, viewport_width, frozen_h),
                            is_frozen=True
                        ))

            # 3. Frozen Left Column
            if self.frozen_cols > 0:
                for r in range(r_start, r_end):
                    for c in range(self.frozen_cols):
                        cells.append(InstancedCell(
                            cell_id=r * self.total_cols + c,
                            x=c * self.col_width,
                            y=frozen_h + (r * self.row_height - scroll_y),
                            width=self.col_width,
                            height=self.row_height,
                            bg_color=(241, 245, 249, 255),
                            border_color=(203, 213, 225),
                            clip_bounds=(0.0, frozen_h, frozen_w, viewport_height),
                            is_frozen=True
                        ))

            # 4. Scroll Body Grid Cells
            # First, check for merged cells via R-tree spatial query
            merges = self.span_index.query(r_start, c_start, r_end, c_end)
            covered_cells = set()
            for m in merges:
                r0, c0, r1, c1 = m['bounds']
                for r in range(r0, r1):
                    for c in range(c0, c1):
                        covered_cells.add((r, c))

                # Merged cell instance
                m_x = frozen_w + (c0 * self.col_width - scroll_x)
                m_y = frozen_h + (r0 * self.row_height - scroll_y)
                m_w = (c1 - c0) * self.col_width
                m_h = (r1 - r0) * self.row_height
                cells.append(InstancedCell(
                    cell_id=m['id'],
                    x=m_x,
                    y=m_y,
                    width=m_w,
                    height=m_h,
                    bg_color=(254, 243, 199, 255), # Amber accent for merged span
                    border_color=(217, 119, 6),
                    border_width=2,
                    clip_bounds=(frozen_w, frozen_h, viewport_width, viewport_height),
                    is_merged=True
                ))

            # Regular unmerged scroll cells
            for r in range(r_start, r_end):
                for c in range(c_start, c_end):
                    if (r, c) in covered_cells:
                        continue
                    cell_x = frozen_w + (c * self.col_width - scroll_x)
                    cell_y = frozen_h + (r * self.row_height - scroll_y)
                    cells.append(InstancedCell(
                        cell_id=r * self.total_cols + c,
                        x=cell_x,
                        y=cell_y,
                        width=self.col_width,
                        height=self.row_height,
                        bg_color=(255, 255, 255, 255),
                        border_color=(226, 232, 240),
                        border_width=1,
                        clip_bounds=(frozen_w, frozen_h, viewport_width, viewport_height)
                    ))

            # Pack instances into binary GPU buffer
            binary_vbo = self.generator.pack_instances(cells)

            return {
                "strategy": "INSTANCED_GPU",
                "instance_count": len(cells),
                "stride_bytes": INSTANCE_STRIDE_BYTES,
                "vbo_byte_length": len(binary_vbo),
                "binary_vbo": binary_vbo,
                "decision": decision,
                "viewport": {
                    "width": viewport_width,
                    "height": viewport_height,
                    "scroll_x": scroll_x,
                    "scroll_y": scroll_y,
                    "dpr": dpr
                }
            }
        else:
            # Fallback to DOM mode manifest
            return {
                "strategy": "DOM",
                "active_cell_count": active_cell_count,
                "decision": decision,
                "viewport": {
                    "width": viewport_width,
                    "height": viewport_height,
                    "scroll_x": scroll_x,
                    "scroll_y": scroll_y
                }
            }

    def close(self):
        if hasattr(self.span_index, 'db') and self.span_index.db:
            self.span_index.db.close()
