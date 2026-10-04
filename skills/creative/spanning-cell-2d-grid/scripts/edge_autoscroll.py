"""Bounded edge-autoscroll math in CSS pixels; no GPU/browser execution."""
from dataclasses import dataclass
import math


def finite(*values):
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
        raise ValueError('finite numeric values required')


@dataclass(frozen=True)
class ScrollFrame:
    x: float
    y: float
    vx: float
    vy: float
    dx: float
    dy: float


class EdgeAutoScroll:
    """Stateless integration, externally owned drag lifecycle and scroll position.

    Pointer coordinates are relative to the scrollable body (exclude frozen panes).
    Positions/bounds are world pixels; speed is CSS px/s; dt is seconds.
    """
    def __init__(self, edge=48.0, speed=800.0, max_dt=0.05):
        finite(edge, speed, max_dt)
        if edge <= 0 or speed <= 0 or not 0 < max_dt <= 0.1:
            raise ValueError('invalid configuration')
        self.edge, self.speed, self.max_dt = edge, speed, max_dt

    def velocity(self, pointer, extent):
        finite(pointer, extent)
        if extent <= 0:
            raise ValueError('positive extent required')
        band = min(self.edge, extent / 2)
        left = max(0.0, min(1.0, (band - pointer) / band))
        right = max(0.0, min(1.0, (pointer - extent + band) / band))
        return self.speed * (right * right - left * left)

    def step(self, *, pointer, viewport, position, bounds, dt, zoom=1.0,
             dragging=True, visible=True):
        px, py = pointer
        width, height = viewport
        x, y = position
        bx, by = bounds
        finite(px, py, width, height, x, y, bx, by, dt, zoom)
        if (width <= 0 or height <= 0 or zoom <= 0 or dt < 0 or
                bx < 0 or by < 0 or not 0 <= x <= bx or not 0 <= y <= by):
            raise ValueError('invalid geometry/time')
        if type(dragging) is not bool or type(visible) is not bool:
            raise ValueError('boolean lifecycle flags required')
        if not dragging or not visible or dt == 0:
            return ScrollFrame(x, y, 0., 0., 0., 0.)
        vx, vy = self.velocity(px, width), self.velocity(py, height)
        # Cap diagonal magnitude, not each axis alone.
        magnitude = math.hypot(vx, vy)
        if magnitude > self.speed:
            vx, vy = vx * self.speed / magnitude, vy * self.speed / magnitude
        dt = min(dt, self.max_dt)
        nx = min(bx, max(0., x + vx * dt / zoom))
        ny = min(by, max(0., y + vy * dt / zoom))
        dx, dy = nx - x, ny - y
        # Report actual motion after boundary clipping, not unattainable demand.
        return ScrollFrame(nx, ny, dx * zoom / dt, dy * zoom / dt, dx, dy)
