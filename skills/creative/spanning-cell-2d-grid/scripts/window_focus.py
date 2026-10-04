"""Pure focus reconciliation for bounded viewport replacement."""
def reconcile(data, cursor):
    """Keep a visible coordinate, otherwise clamp; empty window has no cursor."""
    if cursor is not None and (len(cursor) != 2 or any(type(x) is not int for x in cursor)):
        raise ValueError('Cursor must be two integers or None')
    r0, c0, r1, c1 = data['window']
    if r0 == r1 or c0 == c1:
        return None
    r, c = cursor if cursor is not None else (r0, c0)
    return [min(max(r, r0), r1-1), min(max(c, c0), c1-1)]


def replacement(index, window, cursor=None, **kwargs):
    from dom_adapter import snapshot
    data = snapshot(index, window, **kwargs)
    data['cursor'] = reconcile(data, cursor)
    return data
