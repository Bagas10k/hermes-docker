"""
Signed Distance Field (SDF / MSDF) Glyph Rendering Matrix Integration (UIUX-026).

Connects:
- Multi-Channel Signed Distance Field (MSDF) / Single-Channel Signed Distance Field (SDF) glyph metrics.
- Dynamic Orthographic Camera Zoom Scale (0.25x - 4.0x) matrix integration.
- Analytical screen-pixel-range (pxRange) uniform derivation for fragment shader antialiasing.
- Fragment shader distance testing with median3(R, G, B) for sharp corner preservation.
- Sub-pixel crispness verification across scale boundaries.
- Continuous 64-byte GPU Instanced Text Quad Serialization with camera scale matrix uniforms.
"""

import math
import struct
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any

# MSDF Text Instance Stride Layout:
# vec4 a_char_pos_size  : [quad_x, quad_y, quad_w, quad_h] (4 * float32 = 16 bytes)
# vec4 a_glyph_uv       : [uv_u, uv_v, uv_w, uv_h]          (4 * float32 = 16 bytes)
# vec4 a_text_color     : [r, g, b, a]                      (4 * uint8   = 4 bytes, normalized)
# vec4 a_sdf_params     : [px_range, distance_offset, mode, reserved] (4 * float32 = 16 bytes)
# vec2 a_clip_min       : [clip_x0, clip_y0]                (2 * float32 = 8 bytes)
# vec2 a_clip_max       : [clip_x1, clip_y1]                (2 * float32 = 8 bytes)
# Total stride per MSDF text quad instance = 68 bytes
MSDF_TEXT_INSTANCE_STRIDE_BYTES = 68


@dataclass
class SDFGlyphMetric:
    char: str
    atlas_x: int
    atlas_y: int
    width: int
    height: int
    advance_width: float
    bearing_x: float = 0.0
    bearing_y: float = 0.0
    # Normalized UV in [0.0, 1.0] relative to atlas dimensions
    uv_u: float = 0.0
    uv_v: float = 0.0
    uv_w: float = 0.0
    uv_h: float = 0.0
    # SDF / MSDF specific attributes
    distance_range: float = 4.0  # Range in texels mapped to distance field (e.g. 4.0 px)
    is_msdf: bool = True         # Multi-channel (RGB) vs Single-channel (monochrome SDF)


@dataclass
class SDFCameraUniforms:
    """
    Uniforms passed to the WebGL/WebGPU SDF text rendering pipeline.
    """
    zoom_scale: float
    screen_pixel_range: float  # Dynamic pxRange scaled by camera zoom
    tex_size: Tuple[float, float]
    camera_offset: Tuple[float, float]
    subpixel_aa_enabled: bool = True
    edge_value: float = 0.5    # Median threshold for glyph contour boundary


def median3(r: float, g: float, b: float) -> float:
    """
    Computes the median of three channels: max(min(r, g), min(max(r, g), b)).
    Standard Chlumsky MSDF reconstruction operator preserving sharp corners.
    """
    return max(min(r, g), min(max(r, g), b))


def evaluate_msdf_sample(
    sample_rgb: Tuple[float, float, float],
    screen_px_range: float,
    edge_value: float = 0.5
) -> float:
    """
    Simulates the fragment shader MSDF contour evaluation:
    vec2 unitRange = vec2(pxRange) / vec2(textureSize(msdfTexture, 0));
    vec2 screenTexSize = vec2(1.0) / fwidth(v_uv);
    float screenPxRange = max(0.5 * dot(unitRange, screenTexSize), 1.0);
    float sd = median(msdf.r, msdf.g, msdf.b);
    float screenPxDistance = screenPxRange * (sd - 0.5);
    float opacity = clamp(screenPxDistance + 0.5, 0.0, 1.0);
    """
    sd = median3(sample_rgb[0], sample_rgb[1], sample_rgb[2])
    screen_px_distance = screen_px_range * (sd - edge_value)
    opacity = max(0.0, min(1.0, screen_px_distance + 0.5))
    return opacity


def evaluate_sdf_sample(
    sample_distance: float,
    screen_px_range: float,
    edge_value: float = 0.5
) -> float:
    """
    Simulates single-channel SDF evaluation for comparison.
    """
    screen_px_distance = screen_px_range * (sample_distance - edge_value)
    opacity = max(0.0, min(1.0, screen_px_distance + 0.5))
    return opacity


class SDFDynamicGlyphAtlas:
    """
    Manages MSDF / SDF glyph metrics and texture atlas layout for high-precision text rendering.
    """
    def __init__(
        self,
        atlas_width: int = 1024,
        atlas_height: int = 1024,
        distance_range: float = 4.0,
        font_size: int = 32, # MSDF is typically rasterized at baseline 32px or 48px
        padding: int = 4     # Generous padding to prevent distance field overlap
    ):
        if atlas_width <= 0 or atlas_height <= 0:
            raise ValueError("Atlas dimensions must be positive")
        if distance_range <= 0.0:
            raise ValueError("Distance range must be positive")
        if font_size <= 0:
            raise ValueError("Font size must be positive")

        self.atlas_width = atlas_width
        self.atlas_height = atlas_height
        self.distance_range = distance_range
        self.font_size = font_size
        self.padding = padding

        self.glyphs: Dict[str, SDFGlyphMetric] = {}
        self.cursor_x = self.padding
        self.cursor_y = self.padding
        self.current_shelf_height = 0

        self._preseed_ascii_glyphs()

    def _preseed_ascii_glyphs(self):
        for code in range(32, 127):
            char = chr(code)
            self.allocate_glyph(char)

    def allocate_glyph(self, char: str) -> SDFGlyphMetric:
        if char in self.glyphs:
            return self.glyphs[char]

        # Deterministic dimension approximation based on ASCII typography
        if char == " ":
            char_w = int(self.font_size * 0.35)
            char_h = int(self.font_size * 0.70)
        elif char in "ijl|!:,.'":
            char_w = int(self.font_size * 0.28)
            char_h = int(self.font_size * 0.75)
        elif char in "mwMW@#%":
            char_w = int(self.font_size * 0.85)
            char_h = int(self.font_size * 0.75)
        else:
            char_w = int(self.font_size * 0.55)
            char_h = int(self.font_size * 0.75)

        total_w = char_w + self.padding * 2
        total_h = char_h + self.padding * 2

        if self.cursor_x + total_w > self.atlas_width:
            self.cursor_x = self.padding
            self.cursor_y += self.current_shelf_height + self.padding
            self.current_shelf_height = 0

        if self.cursor_y + total_h > self.atlas_height:
            raise RuntimeError(f"MSDF Atlas capacity exceeded for glyph '{char}'")

        glyph_x = self.cursor_x + self.padding
        glyph_y = self.cursor_y + self.padding

        metric = SDFGlyphMetric(
            char=char,
            atlas_x=glyph_x,
            atlas_y=glyph_y,
            width=char_w,
            height=char_h,
            advance_width=float(char_w),
            bearing_x=0.0,
            bearing_y=float(char_h),
            uv_u=glyph_x / self.atlas_width,
            uv_v=glyph_y / self.atlas_height,
            uv_w=char_w / self.atlas_width,
            uv_h=char_h / self.atlas_height,
            distance_range=self.distance_range,
            is_msdf=True
        )

        self.glyphs[char] = metric
        self.cursor_x += total_w
        if total_h > self.current_shelf_height:
            self.current_shelf_height = total_h

        return metric


@dataclass
class MSDFTextQuad:
    char: str
    x: float
    y: float
    width: float
    height: float
    uv_u: float
    uv_v: float
    uv_w: float
    uv_h: float
    color: Tuple[int, int, int, int] = (15, 23, 42, 255)
    px_range: float = 4.0
    distance_offset: float = 0.0
    mode: float = 1.0  # 1.0 = MSDF (RGB), 0.0 = SDF (Monochrome)
    clip_bounds: Tuple[float, float, float, float] = (0.0, 0.0, 100000.0, 100000.0)


class SDFMatrixShaderIntegrator:
    """
    Coordinates the camera matrix zoom scale, viewport projection, and
    screen-pixel-range calculation for MSDF glyph shader antialiasing.
    """
    def __init__(self, atlas: SDFDynamicGlyphAtlas):
        self.atlas = atlas

    def calculate_screen_pixel_range(self, camera_zoom: float) -> float:
        """
        Calculates screen-pixel-range (pxRange) for fragment anti-aliasing:
        pxRange = distanceRange * (glyphScreenSize / glyphAtlasSize) = distanceRange * camera_zoom
        Bounded by [1.0, 32.0] for stable derivatives and subpixel anti-aliasing.
        """
        if camera_zoom <= 0.0:
            raise ValueError("Camera zoom must be strictly positive")
        raw_range = self.atlas.distance_range * camera_zoom
        return max(1.0, min(32.0, raw_range))

    def get_camera_uniforms(
        self,
        camera_zoom: float,
        camera_offset: Tuple[float, float] = (0.0, 0.0),
        subpixel_aa: bool = True
    ) -> SDFCameraUniforms:
        px_range = self.calculate_screen_pixel_range(camera_zoom)
        return SDFCameraUniforms(
            zoom_scale=camera_zoom,
            screen_pixel_range=px_range,
            tex_size=(float(self.atlas.atlas_width), float(self.atlas.atlas_height)),
            camera_offset=camera_offset,
            subpixel_aa_enabled=subpixel_aa,
            edge_value=0.5
        )

    def generate_cell_text_quads(
        self,
        text: str,
        cell_x: float,
        cell_y: float,
        cell_w: float,
        cell_h: float,
        camera_zoom: float,
        color: Tuple[int, int, int, int] = (15, 23, 42, 255),
        align: str = "left",
        valign: str = "middle"
    ) -> List[MSDFTextQuad]:
        """
        Lays out MSDF text quads inside a virtual cell with camera scale awareness.
        """
        if not text:
            return []

        px_range = self.calculate_screen_pixel_range(camera_zoom)
        metrics = [self.atlas.allocate_glyph(c) for c in text]

        total_text_w = sum(m.advance_width for m in metrics)
        base_h = max((m.height for m in metrics), default=self.atlas.font_size)

        # Horizontal alignment
        if align == "center":
            start_x = cell_x + (cell_w - total_text_w) / 2.0
        elif align == "right":
            start_x = cell_x + cell_w - total_text_w - 8.0
        else:  # left
            start_x = cell_x + 8.0

        # Vertical alignment
        if valign == "middle":
            start_y = cell_y + (cell_h - base_h) / 2.0
        elif valign == "bottom":
            start_y = cell_y + cell_h - base_h - 4.0
        else:  # top
            start_y = cell_y + 4.0

        quads = []
        cur_x = start_x

        for char, m in zip(text, metrics):
            quad = MSDFTextQuad(
                char=char,
                x=cur_x,
                y=start_y,
                width=float(m.width),
                height=float(m.height),
                uv_u=m.uv_u,
                uv_v=m.uv_v,
                uv_w=m.uv_w,
                uv_h=m.uv_h,
                color=color,
                px_range=px_range,
                distance_offset=0.0,
                mode=1.0 if m.is_msdf else 0.0,
                clip_bounds=(cell_x, cell_y, cell_x + cell_w, cell_y + cell_h)
            )
            quads.append(quad)
            cur_x += m.advance_width

        return quads

    def serialize_quad_buffer(self, quads: List[MSDFTextQuad]) -> bytearray:
        """
        Serializes text quads into contiguous 68-byte binary vertex attribute buffer.
        """
        buf = bytearray(len(quads) * MSDF_TEXT_INSTANCE_STRIDE_BYTES)
        offset = 0

        for q in quads:
            # 1. vec4 a_char_pos_size (16 bytes float32)
            struct.pack_into("<4f", buf, offset, q.x, q.y, q.width, q.height)
            offset += 16

            # 2. vec4 a_glyph_uv (16 bytes float32)
            struct.pack_into("<4f", buf, offset, q.uv_u, q.uv_v, q.uv_w, q.uv_h)
            offset += 16

            # 3. vec4 a_text_color (4 bytes uint8)
            struct.pack_into("<4B", buf, offset, q.color[0], q.color[1], q.color[2], q.color[3])
            offset += 4

            # 4. vec4 a_sdf_params (16 bytes float32: px_range, distance_offset, mode, reserved)
            struct.pack_into("<4f", buf, offset, q.px_range, q.distance_offset, q.mode, 0.0)
            offset += 16

            # 5. vec2 a_clip_min (8 bytes float32)
            struct.pack_into("<2f", buf, offset, q.clip_bounds[0], q.clip_bounds[1])
            offset += 8

            # 6. vec2 a_clip_max (8 bytes float32)
            struct.pack_into("<2f", buf, offset, q.clip_bounds[2], q.clip_bounds[3])
            offset += 8

        return buf
