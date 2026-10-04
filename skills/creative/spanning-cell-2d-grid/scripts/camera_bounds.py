"""Finite world-camera bounds after body resize; no rendering claims."""
import math


def reconcile_camera(x, y, zoom, width, height, world_width=2000, world_height=1800):
    values = (x, y, zoom, width, height, world_width, world_height)
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
        raise ValueError('finite numbers required')
    if zoom <= 0 or min(width, height, world_width, world_height) < 0:
        raise ValueError('positive zoom and nonnegative extents required')
    visible = (width / zoom, height / zoom)
    if not all(math.isfinite(v) for v in visible):
        raise ValueError('viewport overflow')
    mx, my = max(0, world_width-visible[0]), max(0, world_height-visible[1])
    return dict(x=min(mx,max(0,x)), y=min(my,max(0,y)), zoom=zoom, maxX=mx, maxY=my)
