"""Offline bounded coordinate transforms; no GUI, IO or input dispatch."""
from dataclasses import dataclass
from enum import Enum
from math import isfinite


class Rejected(ValueError):
    """Invalid or unsafe evidence: do not act."""


class Space(Enum):
    CSS = 'main-frame-viewport-css'
    IMAGE = 'screenshot-raster'
    OS = 'backend-screen-units'


def finite(*values):
    if any(type(v) not in (int, float) or not isfinite(v) for v in values):
        raise Rejected('non-finite or non-numeric value')


def token(value):
    if not isinstance(value, str) or not value.strip():
        raise Rejected('missing identity/generation')


@dataclass(frozen=True)
class Point:
    x: float
    y: float
    space: Space

    def __post_init__(self):
        finite(self.x, self.y)
        if not isinstance(self.space, Space):
            raise Rejected('unknown coordinate space')


@dataclass(frozen=True)
class Box:
    x: float
    y: float
    width: float
    height: float
    space: Space

    def __post_init__(self):
        Point(self.x, self.y, self.space)
        finite(self.width, self.height, self.x + self.width, self.y + self.height)
        if self.width <= 0 or self.height <= 0:
            raise Rejected('empty rectangle')

    def contains(self, p, margin=0, strict=False):
        finite(margin)
        if margin < 0 or p.space != self.space:
            raise Rejected('invalid margin or coordinate space')
        edges = (p.x - margin - self.x, p.y - margin - self.y,
                 self.x + self.width - p.x - margin,
                 self.y + self.height - p.y - margin)
        return all(v > 0 if strict else v >= 0 for v in edges)


@dataclass(frozen=True)
class Transform:
    source: Box
    destination: Box
    sx: float
    sy: float
    tx: float
    ty: float
    error: float
    generation: str
    captured: float

    def __post_init__(self):
        finite(self.sx, self.sy, self.tx, self.ty, self.error, self.captured)
        token(self.generation)
        if min(self.sx, self.sy) <= 0 or self.error < 0 or self.captured < 0:
            raise Rejected('invalid transform')

    def apply(self, p, uncertainty=0):
        finite(uncertainty)
        if uncertainty < 0 or not self.source.contains(p, uncertainty):
            raise Rejected('source envelope outside calibration domain')
        q = Point(self.sx*p.x + self.tx, self.sy*p.y + self.ty,
                  self.destination.space)
        error = max(self.sx, self.sy)*uncertainty + self.error
        finite(error)
        if not self.destination.contains(q, error):
            raise Rejected('output envelope outside calibration domain')
        return q, error


@dataclass(frozen=True)
class Identity:
    scope: str
    document: str
    node: str
    role: str
    name: str

    def __post_init__(self):
        for value in (self.scope, self.document, self.node, self.role, self.name):
            token(value)


@dataclass(frozen=True)
class Evidence:
    generation: str
    captured: float
    identity: Identity
    box: Box
    enabled: bool


@dataclass(frozen=True)
class Hit:
    generation: str
    captured: float
    identity: Identity
    point: Point


def fresh(generation, captured, current, now, max_age):
    token(generation)
    token(current)
    finite(captured, now, max_age)
    if (generation != current or min(captured, now) < 0 or max_age <= 0
            or not 0 <= now-captured <= max_age):
        raise Rejected('stale generation, future evidence or expired evidence')


def admit(point, evidence, expected, hit, *, generation, now, max_age,
          uncertainty, max_uncertainty, viewport, transform=None,
          output_hit=None):
    """Admit CSS point, optionally map it to OS units; return (point, bound).

    Input uncertainty is a conservative L-infinity bound in CSS units.
    max_uncertainty is in the FINAL output space. IMAGE must first be mapped
    to CSS with a separately freshness-checked Transform; pass its bound here.
    Hit identity is resolved by a trusted adapter, never by page instructions.
    """
    finite(uncertainty, max_uncertainty)
    if min(uncertainty, max_uncertainty) < 0:
        raise Rejected('negative uncertainty policy')
    if not isinstance(expected, Identity) or evidence.identity != expected:
        raise Rejected('semantic identity mismatch')
    if evidence.enabled is not True:
        raise Rejected('disabled or unknown target')
    if point.space != Space.CSS or viewport.space != Space.CSS:
        raise Rejected('admission requires main-frame CSS point')
    for item in (evidence, hit):
        fresh(item.generation, item.captured, generation, now, max_age)
    if hit.identity != expected or hit.point != point:
        raise Rejected('occluded, wrong identity or wrong hit-test point')
    if not (evidence.box.contains(point, uncertainty, strict=True)
            and viewport.contains(point, uncertainty, strict=True)):
        raise Rejected('uncertainty envelope crosses target/viewport edge')
    result, error = point, uncertainty
    if transform is not None:
        if (transform.source.space != Space.CSS
                or transform.destination.space != Space.OS):
            raise Rejected('output transform must be CSS to OS')
        fresh(transform.generation, transform.captured, generation, now, max_age)
        result, error = transform.apply(point, uncertainty)
        # Include calibration error when ensuring output still maps into target.
        inverse_error = error / min(transform.sx, transform.sy)
        if not (evidence.box.contains(point, inverse_error, strict=True)
                and viewport.contains(point, inverse_error, strict=True)):
            raise Rejected('calibration error crosses target/viewport edge')
        if output_hit is None:
            raise Rejected('OS hit-test required')
        fresh(output_hit.generation, output_hit.captured, generation, now, max_age)
        if output_hit.identity != expected or output_hit.point != result:
            raise Rejected('OS hit-test mismatch')
    elif output_hit is not None:
        raise Rejected('unexpected output hit-test')
    if error > max_uncertainty:
        raise Rejected('uncertainty budget exceeded')
    return result, error


def calibrate(anchors, source, destination, generation, captured, *,
              residual_limit, measurement_error):
    """Fit diagonal scale/translation, validate >=2 held-out anchors.

    Error is max held-out L-infinity residual plus caller measurement bound.
    This is NOT a confidence interval or an automatic calibration collector.
    """
    finite(residual_limit, measurement_error)
    if min(residual_limit, measurement_error) < 0 or len(anchors) < 4:
        raise Rejected('need four anchors and nonnegative error policy')
    if len({a for a, _ in anchors}) != len(anchors):
        raise Rejected('duplicate source anchors')
    if len({b for _, b in anchors}) != len(anchors):
        raise Rejected('duplicate destination anchors')
    for a, b in anchors:
        if not source.contains(a) or not destination.contains(b):
            raise Rejected('anchor outside domain')
    (a, b), (c, d) = anchors[:2]
    dx, dy = c.x-a.x, c.y-a.y
    if abs(dx) < source.width*1e-6 or abs(dy) < source.height*1e-6:
        raise Rejected('degenerate anchors')
    # Held-out anchors must add 2-D information, not repeat the fit diagonal.
    if not any(abs(dx*(e.y-a.y)-dy*(e.x-a.x)) >
               source.width*source.height*1e-6 for e, _ in anchors[2:]):
        raise Rejected('collinear validation anchors')
    sx, sy = (d.x-b.x)/dx, (d.y-b.y)/dy
    tx, ty = b.x-sx*a.x, b.y-sy*a.y
    residual = max(max(abs(sx*e.x+tx-f.x), abs(sy*e.y+ty-f.y))
                   for e, f in anchors[2:])
    finite(residual)
    if residual > residual_limit:
        raise Rejected('held-out calibration residual')
    return Transform(source, destination, sx, sy, tx, ty,
                     residual+measurement_error, generation, captured)
