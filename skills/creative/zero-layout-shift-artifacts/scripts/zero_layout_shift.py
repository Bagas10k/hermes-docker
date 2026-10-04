"""Zero-Layout-Shift (CLS 0) Live Artifact Sandbox & Virtual Viewport Engine.

Provides deterministic aspect-ratio clamping, layout reservation math,
and iframe sandbox container synthesis for live code previews.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import math
import json


@dataclass
class ViewportSpec:
    width: float
    height: float
    device_pixel_ratio: float = 1.0
    safe_area_top: float = 0.0
    safe_area_bottom: float = 0.0

    @property
    def aspect_ratio(self) -> float:
        if self.height <= 0:
            raise ValueError("Viewport height must be strictly positive")
        return self.width / self.height


@dataclass
class SkeletonReservation:
    component_id: str
    min_width: float
    min_height: float
    aspect_ratio: Optional[float] = None
    contain_intrinsic_size: Optional[str] = None
    content_visibility: str = "auto"

    def compute_clamped_dimensions(self, parent_width: float) -> Dict[str, float]:
        """Compute exact reserved dimensions to prevent any layout shift during asset loading."""
        if parent_width <= 0:
            w = self.min_width
        else:
            w = max(self.min_width, parent_width)

        if self.aspect_ratio and self.aspect_ratio > 0:
            h = w / self.aspect_ratio
            h = max(h, self.min_height)
        else:
            h = self.min_height

        return {"width": round(w, 2), "height": round(h, 2)}


class LayoutShiftCalculator:
    """Calculates Cumulative Layout Shift (CLS) based on standard W3C Web Vitals formula."""

    @staticmethod
    def calculate_shift(
        viewport_width: float,
        viewport_height: float,
        prev_rect: Dict[str, float],
        curr_rect: Dict[str, float]
    ) -> float:
        """
        CLS = Impact Fraction * Distance Fraction
        Impact Fraction = Area of union of rectangles / Viewport area
        Distance Fraction = Max vertical/horizontal movement / Max viewport dimension
        """
        if viewport_width <= 0 or viewport_height <= 0:
            return 0.0

        vp_area = viewport_width * viewport_height

        # Calculate bounding box of union
        union_min_x = min(prev_rect["x"], curr_rect["x"])
        union_min_y = min(prev_rect["y"], curr_rect["y"])
        union_max_x = max(prev_rect["x"] + prev_rect["width"], curr_rect["x"] + curr_rect["width"])
        union_max_y = max(prev_rect["y"] + prev_rect["height"], curr_rect["y"] + curr_rect["height"])

        union_w = max(0.0, union_max_x - union_min_x)
        union_h = max(0.0, union_max_y - union_min_y)
        union_area = union_w * union_h

        impact_fraction = min(1.0, union_area / vp_area)

        # Distance moved (Euclidean distance along vertical or horizontal dominant axis)
        dx = abs(curr_rect["x"] - prev_rect["x"])
        dy = abs(curr_rect["y"] - prev_rect["y"])
        max_dist = max(dx, dy)
        max_vp_dim = max(viewport_width, viewport_height)

        distance_fraction = min(1.0, max_dist / max_vp_dim)

        return round(impact_fraction * distance_fraction, 6)


class VirtualViewportManager:
    """Manages virtual viewport paging, touch-safe zoom/pan constraints, and zero-shift sandbox envelopes."""

    def __init__(self, spec: ViewportSpec):
        self.spec = spec
        self.reservations: Dict[str, SkeletonReservation] = {}

    def register_reservation(self, reservation: SkeletonReservation) -> None:
        self.reservations[reservation.component_id] = reservation

    def generate_sandbox_container_css(self, component_id: str, parent_width: float) -> Dict[str, Any]:
        """Synthesize CSS variables and styling that guarantees zero layout shift (CLS = 0)."""
        res = self.reservations.get(component_id)
        if not res:
            raise KeyError(f"No skeleton reservation registered for {component_id}")

        dims = res.compute_clamped_dimensions(parent_width)
        aspect = res.aspect_ratio if res.aspect_ratio else (dims["width"] / dims["height"] if dims["height"] > 0 else 1.0)

        css_rules = {
            "width": f"{dims['width']}px",
            "height": f"{dims['height']}px",
            "min-height": f"{res.min_height}px",
            "aspect-ratio": f"{round(aspect, 4)}",
            "content-visibility": res.content_visibility,
            "contain": "paint layout style size",
            "contain-intrinsic-size": f"{dims['width']}px {dims['height']}px",
            "box-sizing": "border-box",
            "overflow": "hidden",
            "transform": "translateZ(0)"
        }
        return {
            "component_id": component_id,
            "computed_dimensions": dims,
            "css": css_rules
        }

    def generate_iframe_sandbox_html(
        self,
        component_id: str,
        content_srcdoc: str,
        parent_width: float,
        csp_policy: Optional[str] = None
    ) -> str:
        """Emits an isolated HTML wrapper with hard structural constraints and security sandboxing."""
        container_meta = self.generate_sandbox_container_css(component_id, parent_width)
        css_map = container_meta["css"]
        css_str = "; ".join([f"{k}: {v}" for k, v in css_map.items()])

        csp = csp_policy or "default-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
        escaped_srcdoc = content_srcdoc.replace('"', '&quot;')

        return (
            f'<div id="sandbox-wrapper-{component_id}" style="{css_str}; position: relative;">'
            f'<div class="cls0-skeleton-placeholder" style="position: absolute; inset: 0; background: #1C1915; z-index: 1;"></div>'
            f'<iframe id="sandbox-frame-{component_id}" '
            f'sandbox="allow-scripts" '
            f'csp="{csp}" '
            f'srcdoc="{escaped_srcdoc}" '
            f'style="width: 100%; height: 100%; border: none; position: relative; z-index: 2;" '
            f'loading="eager" '
            f'onload="this.previousElementSibling.style.display=\'none\';">'
            f'</iframe>'
            f'</div>'
        )

    def calculate_virtual_paging(
        self,
        item_count: int,
        item_height: float,
        scroll_y: float,
        overscan_count: int = 2
    ) -> Dict[str, Any]:
        """
        Determines the visible range and transform offset for high-density virtual lists
        without inducing DOM layout recalculation shifts.
        """
        if item_height <= 0:
            raise ValueError("item_height must be positive")

        visible_count = math.ceil(self.spec.height / item_height)
        start_index = max(0, math.floor(scroll_y / item_height) - overscan_count)
        end_index = min(item_count - 1, start_index + visible_count + (2 * overscan_count))

        top_padding = start_index * item_height
        bottom_padding = max(0.0, (item_count - 1 - end_index) * item_height)
        total_height = item_count * item_height

        return {
            "start_index": start_index,
            "end_index": end_index,
            "visible_count": end_index - start_index + 1,
            "top_padding": top_padding,
            "bottom_padding": bottom_padding,
            "total_height": total_height,
            "scroll_y": scroll_y
        }
