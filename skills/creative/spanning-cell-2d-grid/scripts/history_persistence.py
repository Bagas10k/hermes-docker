"""Strict bounded UTF-8 history codec; single-thread object restore, not disk IO."""
import json
from collections import deque
from branch_history import _identifier
from byte_budget_history import ByteBudgetHistory


def _limit(value):
    if type(value) is not int or value < 1:
        raise ValueError('positive integer wire cap required')


def _pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError('duplicate JSON key')
        out[key] = value
    return out


def _constant(value):
    raise ValueError('nonfinite JSON constant')


def _fields(obj, fields):
    if type(obj) is not dict or set(obj) != set(fields):
        raise ValueError('invalid fields')


def dump_history(history, *, max_wire_bytes=1048576):
    """Emit versioned deltas without trusting/storing derived snapshots or counters."""
    _limit(max_wire_bytes)
    obj = {'version': 1, 'initial': dict(history._nodes['root'].state),
           'cursor': history.cursor,
           'nodes': [{'id': key, 'parent': node.parent, 'changes': dict(node.delta)}
                     for key, node in sorted(history._nodes.items()) if key != 'root']}
    encoder = json.JSONEncoder(ensure_ascii=True, separators=(',', ':'), sort_keys=True)
    output = bytearray()
    for chunk in encoder.iterencode(obj):
        # ASCII output; check before allocating another encoded chunk.
        if len(output) + len(chunk) > max_wire_bytes:
            raise OverflowError('wire byte budget')
        output.extend(chunk.encode('ascii'))
    return bytes(output)


def load_history(raw, *, max_wire_bytes=1048576, max_nodes=1024,
                 max_cells=4096, max_payload_bytes=1048576,
                 max_retained_bytes=16777216):
    """Validate in isolation, then return a complete replacement instance."""
    _limit(max_wire_bytes)
    if type(raw) is not bytes:
        raise ValueError('UTF-8 bytes required')
    if len(raw) > max_wire_bytes:
        raise OverflowError('wire byte budget')
    try:
        obj = json.loads(raw.decode('utf-8', errors='strict'),
                         object_pairs_hook=_pairs, parse_constant=_constant)
    except (UnicodeError, RecursionError, ValueError) as exc:
        raise ValueError('invalid history JSON') from exc
    _fields(obj, ('version', 'initial', 'cursor', 'nodes'))
    if type(obj['version']) is not int or obj['version'] != 1:
        raise ValueError('unsupported version')
    candidate = ByteBudgetHistory(obj['initial'], max_nodes=max_nodes,
                                  max_cells=max_cells, max_payload_bytes=max_payload_bytes,
                                  max_retained_bytes=max_retained_bytes)
    if type(obj['nodes']) is not list:
        raise ValueError('nodes must be list')
    if len(obj['nodes']) + 1 > max_nodes:
        raise OverflowError('node budget')
    records, children = {}, {}
    for record in obj['nodes']:
        _fields(record, ('id', 'parent', 'changes'))
        key, parent = record['id'], record['parent']
        _identifier(key)
        _identifier(parent)
        if key == 'root' or key in records:
            raise ValueError('duplicate/reserved node')
        records[key] = record
        children.setdefault(parent, []).append(key)
    for record in records.values():
        if record['parent'] != 'root' and record['parent'] not in records:
            raise ValueError('missing parent')
    queue = deque(children.get('root', ()))
    count = 0
    while queue:
        key = queue.popleft()
        record = records[key]
        candidate.commit(key, record['parent'], record['changes'], activate=False)
        count += 1
        queue.extend(children.get(key, ()))
    if count != len(records):
        raise ValueError('cyclic or disconnected parent graph')
    candidate.checkout(obj['cursor'])
    return candidate


def restore_history(target, raw, *, max_wire_bytes=1048576):
    """Single-thread all-or-nothing replacement using the receiver's trusted caps.

    Exact class restriction prevents silently bypassing subclass invariants.
    Existing external references to private nodes are not updated.
    """
    if type(target) is not ByteBudgetHistory:
        raise ValueError('exact ByteBudgetHistory target required')
    candidate = load_history(raw, max_wire_bytes=max_wire_bytes,
                             max_nodes=target._max_nodes, max_cells=target._max_cells,
                             max_payload_bytes=target._payload_limit,
                             max_retained_bytes=target._retained_limit)
    target.__dict__ = candidate.__dict__
    return target
