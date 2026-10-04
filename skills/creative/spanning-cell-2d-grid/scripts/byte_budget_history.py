"""Logical UTF-8 admission bounds; not heap/RSS or wire-JSON limits."""
from branch_history import BranchHistory, _cells, _identifier


def utf8_size(text):
    # Bounded temporary encoding even for an already-decoded large string.
    return sum(len(text[i:i + 4096].encode('utf-8', errors='strict'))
               for i in range(0, len(text), 4096))


def cell_bytes(cells):
    return sum(utf8_size(k) + (0 if v is None else utf8_size(v))
               for k, v in cells.items())


class ByteBudgetHistory(BranchHistory):
    """Charge each retained snapshot/delta occurrence, even shared strings.

    Root charge: UTF8('root') + initial cells.
    New-node charge: UTF8(id) + UTF8(parent) + delta + resulting snapshot.
    Payload charge: UTF8(id) + UTF8(parent) + delta (root uses root + initial).
    None contributes zero value bytes; keys are always charged.
    """
    def __init__(self, initial=None, *, max_payload_bytes=1048576,
                 max_retained_bytes=16777216, max_nodes=1024, max_cells=4096):
        for limit in (max_payload_bytes, max_retained_bytes):
            if type(limit) is not int or limit < 1:
                raise ValueError('positive integer byte limits required')
        initial = {} if initial is None else initial
        _cells(initial)
        charge = utf8_size('root') + cell_bytes(initial)
        if charge > max_payload_bytes or charge > max_retained_bytes:
            raise OverflowError('initial byte budget')
        super().__init__(initial, max_nodes=max_nodes, max_cells=max_cells)
        self._payload_limit = max_payload_bytes
        self._retained_limit = max_retained_bytes
        self._retained_bytes = charge

    @property
    def retained_bytes(self):
        return self._retained_bytes

    def commit(self, node, parent, changes, *, activate=True):
        _identifier(node)
        base = self._get(parent)
        _cells(changes, deletion=True)
        payload = utf8_size(node) + utf8_size(parent) + cell_bytes(changes)
        if payload > self._payload_limit:
            raise OverflowError('payload byte budget')
        # Let the base validate collision/reserved-ID/activate and preserve replay.
        if node in self._nodes:
            return super().commit(node, parent, changes, activate=activate)
        # Compute the candidate size without allocating its snapshot.
        snapshot_bytes = cell_bytes(base.state)
        for key, value in changes.items():
            if key in base.state:
                snapshot_bytes -= utf8_size(key) + utf8_size(base.state[key])
            if value is not None:
                snapshot_bytes += utf8_size(key) + utf8_size(value)
        charge = payload + snapshot_bytes
        if self._retained_bytes + charge > self._retained_limit:
            raise OverflowError('retained byte budget')
        result = super().commit(node, parent, changes, activate=activate)
        self._retained_bytes += charge
        return result
