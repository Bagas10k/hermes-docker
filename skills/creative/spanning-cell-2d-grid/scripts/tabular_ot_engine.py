"""Collaborative operational transformation and conflict resolution for 2D tabular cells (UIUX-044).

Implements Lamport / Vector Clock causality, operational transformation for
concurrent tabular cell edits, LWW / priority arbitration, and topology merge collision resolution.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set
import copy
import time


@dataclass
class VectorClock:
    """Logical vector clock tracking causality across distributed clients."""
    clocks: Dict[str, int] = field(default_factory=dict)

    def increment(self, client_id: str) -> None:
        self.clocks[client_id] = self.clocks.get(client_id, 0) + 1

    def update_max(self, other: 'VectorClock') -> None:
        for cid, val in other.clocks.items():
            self.clocks[cid] = max(self.clocks.get(cid, 0), val)

    def is_concurrent(self, other: 'VectorClock') -> bool:
        """Two clocks are concurrent if neither dominates the other across all nodes."""
        greater = False
        lesser = False
        all_keys = set(self.clocks.keys()) | set(other.clocks.keys())
        for k in all_keys:
            v1 = self.clocks.get(k, 0)
            v2 = other.clocks.get(k, 0)
            if v1 > v2:
                greater = True
            elif v1 < v2:
                lesser = True
        return greater and lesser

    def dominates(self, other: 'VectorClock') -> bool:
        """True if self is strictly causally newer than or equal to other."""
        greater_or_equal = True
        strictly_greater = False
        all_keys = set(self.clocks.keys()) | set(other.clocks.keys())
        for k in all_keys:
            v1 = self.clocks.get(k, 0)
            v2 = other.clocks.get(k, 0)
            if v1 < v2:
                return False
            if v1 > v2:
                strictly_greater = True
        return strictly_greater

    def clone(self) -> 'VectorClock':
        return VectorClock(clocks=dict(self.clocks))

    def to_dict(self) -> Dict[str, int]:
        return dict(self.clocks)

    @classmethod
    def from_dict(cls, d: Dict[str, int]) -> 'VectorClock':
        return cls(clocks=dict(d))


@dataclass
class TabularOperation:
    """Atomic tabular operation emitted by a client."""
    op_id: str
    client_id: str
    clock: VectorClock
    timestamp: float
    op_type: str  # 'cell_edit', 'merge_add', 'merge_remove'
    target: Dict[str, Any]  # for cell_edit: {'row', 'col', 'old_val', 'new_val', 'formula'}
                            # for merge_add/remove: {'merge_id', 'r0', 'c0', 'r1', 'c1'}
    priority: int = 0  # Tie-breaking priority (higher wins, or lexicographical client_id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'op_id': self.op_id,
            'client_id': self.client_id,
            'clock': self.clock.to_dict(),
            'timestamp': self.timestamp,
            'op_type': self.op_type,
            'target': copy.deepcopy(self.target),
            'priority': self.priority
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'TabularOperation':
        return cls(
            op_id=d['op_id'],
            client_id=d['client_id'],
            clock=VectorClock.from_dict(d['clock']),
            timestamp=float(d['timestamp']),
            op_type=d['op_type'],
            target=dict(d['target']),
            priority=int(d.get('priority', 0))
        )


class TabularOTEngine:
    """Operational Transformation engine for multi-client 2D grid synchronisation."""

    def __init__(self, client_id: str):
        self.client_id = client_id
        self.vector_clock = VectorClock()
        self.applied_ops: List[TabularOperation] = []
        self.cell_store: Dict[Tuple[int, int], str] = {}
        self.formula_store: Dict[Tuple[int, int], str] = {}
        self.merges: Dict[str, Tuple[int, int, int, int]] = {}
        self.cell_merge_owners: Dict[Tuple[int, int], str] = {}

    def create_cell_edit(self, row: int, col: int, new_val: str, formula: Optional[str] = None, priority: int = 0) -> TabularOperation:
        self.vector_clock.increment(self.client_id)
        old_val = self.cell_store.get((row, col), '')
        op = TabularOperation(
            op_id=f"{self.client_id}_{self.vector_clock.clocks[self.client_id]}",
            client_id=self.client_id,
            clock=self.vector_clock.clone(),
            timestamp=time.time(),
            op_type='cell_edit',
            target={'row': row, 'col': col, 'old_val': old_val, 'new_val': new_val, 'formula': formula},
            priority=priority
        )
        self._apply_local(op)
        return op

    def create_merge(self, merge_id: str, r0: int, c0: int, r1: int, c1: int, priority: int = 0) -> TabularOperation:
        self.vector_clock.increment(self.client_id)
        op = TabularOperation(
            op_id=f"{self.client_id}_{self.vector_clock.clocks[self.client_id]}",
            client_id=self.client_id,
            clock=self.vector_clock.clone(),
            timestamp=time.time(),
            op_type='merge_add',
            target={'merge_id': merge_id, 'r0': r0, 'c0': c0, 'r1': r1, 'c1': c1},
            priority=priority
        )
        self._apply_local(op)
        return op

    def create_unmerge(self, merge_id: str, priority: int = 0) -> Optional[TabularOperation]:
        if merge_id not in self.merges:
            return None
        r0, c0, r1, c1 = self.merges[merge_id]
        self.vector_clock.increment(self.client_id)
        op = TabularOperation(
            op_id=f"{self.client_id}_{self.vector_clock.clocks[self.client_id]}",
            client_id=self.client_id,
            clock=self.vector_clock.clone(),
            timestamp=time.time(),
            op_type='merge_remove',
            target={'merge_id': merge_id, 'r0': r0, 'c0': c0, 'r1': r1, 'c1': c1},
            priority=priority
        )
        self._apply_local(op)
        return op

    def _apply_local(self, op: TabularOperation) -> None:
        self.applied_ops.append(op)
        if op.op_type == 'cell_edit':
            r, c = op.target['row'], op.target['col']
            val = op.target['new_val']
            if val == '':
                self.cell_store.pop((r, c), None)
            else:
                self.cell_store[(r, c)] = val
            if op.target.get('formula'):
                self.formula_store[(r, c)] = op.target['formula']
            else:
                self.formula_store.pop((r, c), None)
        elif op.op_type == 'merge_add':
            m_id = op.target['merge_id']
            coords = (op.target['r0'], op.target['c0'], op.target['r1'], op.target['c1'])
            self.merges[m_id] = coords
            for r in range(coords[0], coords[2]):
                for c in range(coords[1], coords[3]):
                    self.cell_merge_owners[(r, c)] = m_id
        elif op.op_type == 'merge_remove':
            m_id = op.target['merge_id']
            if m_id in self.merges:
                coords = self.merges.pop(m_id)
                for r in range(coords[0], coords[2]):
                    for c in range(coords[1], coords[3]):
                        self.cell_merge_owners.pop((r, c), None)

    def transform(self, incoming: TabularOperation) -> Tuple[Optional[TabularOperation], str]:
        """Transforms incoming remote operation against local history and arbitration rules.

        Returns (transformed_op, status) where status is 'applied', 'superseded', 'vetoed', or 'transformed'.
        """
        # Update our vector clock
        self.vector_clock.update_max(incoming.clock)

        if incoming.op_type == 'cell_edit':
            r = incoming.target['row']
            c = incoming.target['col']

            # Find concurrent operations targeting the exact same cell
            conflicting_ops = [
                op for op in self.applied_ops
                if op.op_type == 'cell_edit'
                and op.target['row'] == r
                and op.target['col'] == c
                and op.clock.is_concurrent(incoming.clock)
            ]

            if conflicting_ops:
                # Concurrent conflict arbitration: Highest priority, then LWW timestamp, then client_id
                for conf in conflicting_ops:
                    incoming_wins = self._arbitrate_tie(incoming, conf)
                    if not incoming_wins:
                        # Local operation takes precedence, incoming is superseded / no-op
                        return None, 'superseded'

            # Apply transformed cell edit
            transformed_op = copy.deepcopy(incoming)
            self._apply_local(transformed_op)
            return transformed_op, 'applied'

        elif incoming.op_type == 'merge_add':
            # Check topology overlap with existing active merges
            new_r0, new_c0, new_r1, new_c1 = incoming.target['r0'], incoming.target['c0'], incoming.target['r1'], incoming.target['c1']
            overlapping_merges = []
            for m_id, (m_r0, m_c0, m_r1, m_c1) in self.merges.items():
                if not (new_r1 <= m_r0 or new_r0 >= m_r1 or new_c1 <= m_c0 or new_c0 >= m_c1):
                    overlapping_merges.append(m_id)

            if overlapping_merges:
                # Conflict resolution: if incoming has higher priority or wins tie-break, auto-unmerge overlapping
                # otherwise incoming merge is vetoed
                can_overwrite = True
                for ov_id in overlapping_merges:
                    # Find op that created ov_id
                    creator_op = next((op for op in self.applied_ops if op.op_type == 'merge_add' and op.target['merge_id'] == ov_id), None)
                    if creator_op and not self._arbitrate_tie(incoming, creator_op):
                        can_overwrite = False
                        break

                if not can_overwrite:
                    return None, 'vetoed'

                # Auto-unmerge overlapping local merges
                for ov_id in overlapping_merges:
                    coords = self.merges.pop(ov_id)
                    for r in range(coords[0], coords[2]):
                        for c in range(coords[1], coords[3]):
                            self.cell_merge_owners.pop((r, c), None)

            transformed_op = copy.deepcopy(incoming)
            self._apply_local(transformed_op)
            return transformed_op, 'applied'

        elif incoming.op_type == 'merge_remove':
            m_id = incoming.target['merge_id']
            if m_id in self.merges:
                transformed_op = copy.deepcopy(incoming)
                self._apply_local(transformed_op)
                return transformed_op, 'applied'
            return None, 'superseded'

        return None, 'vetoed'

    def _arbitrate_tie(self, op1: TabularOperation, op2: TabularOperation) -> bool:
        """Arbitrates between two concurrent operations. True if op1 wins."""
        if op1.priority != op2.priority:
            return op1.priority > op2.priority
        if abs(op1.timestamp - op2.timestamp) > 0.0001:
            return op1.timestamp > op2.timestamp  # Last-Write-Wins
        return op1.client_id > op2.client_id  # Deterministic lexicographical tie-break

    def export_state_manifest(self) -> Dict[str, Any]:
        return {
            'client_id': self.client_id,
            'vector_clock': self.vector_clock.to_dict(),
            'applied_ops_count': len(self.applied_ops),
            'cells_count': len(self.cell_store),
            'merges_count': len(self.merges)
        }
