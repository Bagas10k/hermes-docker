"""Validated world-coordinate selection helper; no rendering/GPU execution."""
import math


def world_point(point, offset, zoom):
    values = (*point, *offset, zoom)
    if len(point) != 2 or len(offset) != 2 or any(
        isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v)
        for v in values
    ) or zoom <= 0:
        raise ValueError('finite 2D coordinates and positive zoom required')
    result = tuple(o + p / zoom for p, o in zip(point, offset))
    if not all(math.isfinite(v) for v in result):
        raise ValueError('world coordinate overflow')
    return result
