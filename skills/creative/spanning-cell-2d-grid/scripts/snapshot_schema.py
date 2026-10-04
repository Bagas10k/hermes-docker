"""Validate decoded JSON snapshots before renderer mutation; bounded visible work."""
import math
import re

LIMIT = 4096
PIXEL_LIMIT = 1_000_000_000
TOP = {'rows', 'cols', 'window', 'width', 'height', 'cells', 'owners'}
CELL = {'id', 'row', 'col', 'rowspan', 'colspan', 'left', 'top', 'width', 'height'}


def validate_snapshot(data):
    def require(ok):
        if not ok:
            raise ValueError('Invalid bounded grid snapshot')

    def integer(x, low, high):
        return type(x) is int and low <= x <= high

    def pixel(x):
        return type(x) in (int, float) and math.isfinite(x) and abs(x) <= PIXEL_LIMIT

    require(type(data) is dict and set(data) == TOP)
    require(all(integer(data[k], 1, 2**31-1) for k in ('rows', 'cols')))
    w = data['window']
    require(type(w) is list and len(w) == 4 and all(integer(v, 0, 2**31-1) for v in w))
    r0, c0, r1, c1 = w
    require(r0 <= r1 <= data['rows'] and c0 <= c1 <= data['cols'])
    area = (r1-r0)*(c1-c0)
    require(area <= LIMIT)
    require(all(pixel(data[k]) and data[k] >= 0 for k in ('width', 'height')))
    require(type(data['cells']) is list and len(data['cells']) <= area)
    require(type(data['owners']) is dict and len(data['owners']) == area)
    require((data['width'] == 0) == (c0 == c1) and (data['height'] == 0) == (r0 == r1))
    if not area:
        return data
    rh, cw = data['height']/(r1-r0), data['width']/(c1-c0)
    expected, ids = {}, set()
    for cell in data['cells']:
        require(type(cell) is dict and set(cell) == CELL)
        ident = cell['id']
        require(type(ident) is str and len(ident) <= 80 and re.fullmatch(r'(?:merge-[0-9]+|cell-[0-9]+-[0-9]+)', ident) is not None and ident not in ids)
        ids.add(ident)
        require(all(integer(cell[k], 0, 2**31-1) for k in ('row', 'col')))
        require(all(integer(cell[k], 1, 2**31-1) for k in ('rowspan', 'colspan')))
        a,b = cell['row'],cell['col']
        z,t = a+cell['rowspan'], b+cell['colspan']
        require(z <= data['rows'] and t <= data['cols'])
        require(a < r1 and z > r0 and b < c1 and t > c0)
        geometry = dict(left=(b-c0)*cw, top=(a-r0)*rh, width=cell['colspan']*cw, height=cell['rowspan']*rh)
        require(all(pixel(cell[k]) and abs(cell[k]-v) <= 1e-6 for k,v in geometry.items()))
        for r in range(max(a,r0), min(z,r1)):
            for c in range(max(b,c0), min(t,c1)):
                key = f'{r},{c}'
                require(key not in expected)
                expected[key] = ident
    require(expected == data['owners'])
    return data
