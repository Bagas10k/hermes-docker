"""Bounded in-memory immutable branch snapshots for tabular string cells.

Single-parent history is a DAG subset, not CRDT merge or distributed undo.
Remote commits require known parents and never activate unless requested.
"""
from dataclasses import dataclass
from types import MappingProxyType


def _identifier(value):
    if not isinstance(value, str) or not value or len(value) > 256:
        raise ValueError('expected nonempty identifier <=256 characters')


def _cells(values, deletion=False):
    if not isinstance(values, dict):
        raise ValueError('expected dict')
    for key, value in values.items():
        _identifier(key)
        if not isinstance(value, str) and not (deletion and value is None):
            raise ValueError('cell values must be strings; None deletes in a delta')


@dataclass(frozen=True)
class _Node:
    parent: object
    delta: object
    state: object


class BranchHistory:
    def __init__(self, initial=None, *, max_nodes=1024, max_cells=4096):
        for value in (max_nodes, max_cells):
            if type(value) is not int or value < 1:
                raise ValueError('positive integer limits required')
        initial = {} if initial is None else initial
        _cells(initial)
        if len(initial) > max_cells:
            raise OverflowError('cell budget')
        self._max_nodes, self._max_cells = max_nodes, max_cells
        self._nodes = {'root': _Node(None, MappingProxyType({}), MappingProxyType(dict(initial)))}
        self._children = {'root': set()}
        self._cursor = 'root'

    @property
    def cursor(self):
        return self._cursor

    def _get(self, node):
        _identifier(node)
        if node not in self._nodes:
            raise ValueError('unknown node')
        return self._nodes[node]

    def snapshot(self):
        return dict(self._nodes[self._cursor].state)

    def children(self, node):
        self._get(node)
        return tuple(sorted(self._children[node]))

    def commit(self, node, parent, changes, *, activate=True):
        _identifier(node)
        base = self._get(parent)
        _cells(changes, deletion=True)
        if type(activate) is not bool:
            raise ValueError('activate must be bool')
        if node == 'root':
            raise ValueError('reserved root')
        if node in self._nodes:
            old = self._nodes[node]
            if old.parent != parent or dict(old.delta) != changes:
                raise ValueError('node ID collision')
            return False  # replay cannot change the local cursor
        if len(self._nodes) >= self._max_nodes or len(changes) > self._max_cells:
            raise OverflowError('history budget')
        state = dict(base.state)
        for key, value in changes.items():
            if value is None:
                state.pop(key, None)
            else:
                state[key] = value
        if len(state) > self._max_cells:
            raise OverflowError('cell budget')
        record = _Node(parent, MappingProxyType(dict(changes)), MappingProxyType(state))
        self._nodes[node] = record
        self._children[node] = set()
        self._children[parent].add(node)
        if activate:
            self._cursor = node
        return True

    def checkout(self, node):
        record = self._get(node)
        result = dict(record.state)
        self._cursor = node
        return result

    def undo(self):
        parent = self._nodes[self._cursor].parent
        return self.snapshot() if parent is None else self.checkout(parent)

    def redo(self, child=None):
        options = self.children(self._cursor)
        if child is None:
            if not options:
                return self.snapshot()
            if len(options) != 1:
                raise ValueError('choose a branch explicitly')
            child = options[0]
        if child not in options:
            raise ValueError('not a direct child')
        return self.checkout(child)

    def _ancestors(self, node):
        self._get(node)
        result = []
        while node is not None:
            result.append(node)
            node = self._nodes[node].parent
        return result

    def route(self, source, target):
        left, right = self._ancestors(source), self._ancestors(target)
        positions = {node: index for index, node in enumerate(left)}
        for index, node in enumerate(right):
            if node in positions:
                return {'lca': node, 'undo': tuple(left[:positions[node]]),
                        'redo': tuple(reversed(right[:index]))}
        raise RuntimeError('unreachable disconnected history')
