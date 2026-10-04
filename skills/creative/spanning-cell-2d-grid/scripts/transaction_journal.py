"""Multi-Tier Undo/Redo Transaction Journal for Cell Values and Topology Merges.

Provides bounded bidirectional transaction history tracking for 2D tabular grids
supporting simultaneous scalar/formula cell mutations, structural merged
cell topology mutations, selective range rollback filtering, and compressed
delta serialization for local persistence.
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple, List, Optional, Sequence, Any, Union, Set
import json
import time
import zlib
import base64

from tabular_paste_arbitrator import PastePlan, CellMutation, TabularPasteArbitrator, SelectionBox


@dataclass(frozen=True)
class MergeRegionMutation:
    """Represents a structural mutation to a merged cell region."""
    action: str  # 'added', 'removed', 'modified'
    merge_id: str
    r0: int
    c0: int
    r1: int
    c1: int
    prev_r0: Optional[int] = None
    prev_c0: Optional[int] = None
    prev_r1: Optional[int] = None
    prev_c1: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'action': self.action,
            'merge_id': self.merge_id,
            'r0': self.r0,
            'c0': self.c0,
            'r1': self.r1,
            'c1': self.c1,
            'prev_r0': self.prev_r0,
            'prev_c0': self.prev_c0,
            'prev_r1': self.prev_r1,
            'prev_c1': self.prev_c1
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'MergeRegionMutation':
        return cls(
            action=d['action'],
            merge_id=d['merge_id'],
            r0=int(d['r0']),
            c0=int(d['c0']),
            r1=int(d['r1']),
            c1=int(d['c1']),
            prev_r0=int(d['prev_r0']) if d.get('prev_r0') is not None else None,
            prev_c0=int(d['prev_c0']) if d.get('prev_c0') is not None else None,
            prev_r1=int(d['prev_r1']) if d.get('prev_r1') is not None else None,
            prev_c1=int(d['prev_c1']) if d.get('prev_c1') is not None else None
        )


@dataclass(frozen=True)
class TransactionRecord:
    """An immutable atomic transaction record containing both cell and topology diffs."""
    tx_id: str
    description: str
    timestamp: float
    cell_mutations: Tuple[CellMutation, ...]
    topology_mutations: Tuple[MergeRegionMutation, ...]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'tx_id': self.tx_id,
            'description': self.description,
            'timestamp': self.timestamp,
            'cell_mutations': [
                {
                    'row': m.row,
                    'col': m.col,
                    'old_value': m.old_value,
                    'new_value': m.new_value,
                } for m in self.cell_mutations
            ],
            'topology_mutations': [m.to_dict() for m in self.topology_mutations],
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'TransactionRecord':
        cells = tuple(
            CellMutation(
                row=int(m['row']),
                col=int(m['col']),
                old_value=str(m['old_value']),
                new_value=str(m['new_value']),
                
                
            ) for m in d.get('cell_mutations', [])
        )
        topos = tuple(
            MergeRegionMutation.from_dict(m) for m in d.get('topology_mutations', [])
        )
        return cls(
            tx_id=d['tx_id'],
            description=d.get('description', ''),
            timestamp=float(d.get('timestamp', 0.0)),
            cell_mutations=cells,
            topology_mutations=topos,
            metadata=d.get('metadata', {})
        )


class TransactionJournal:
    """Bounded multi-tier bidirectional Undo/Redo journal for tabular grids.

    Enforces:
    1. Hard journal capacity bounds (evicts oldest undo records on capacity breach).
    2. Atomic commit: clearing redo branch on new commit.
    3. Bidirectional invertible replay for cell store and merge topology.
    4. Grouping / compound transaction batching.
    5. Selective range rollback: atomic undo/redo restricted to active bounding boxes.
    6. Compressed delta serialization for browser local persistence (zlib + base64).
    """

    def __init__(self,
                 arbitrator: TabularPasteArbitrator,
                 max_history: int = 100):
        if max_history <= 0:
            raise ValueError('max_history must be a positive integer')
        self.arbitrator = arbitrator
        self.max_history = max_history

        self._undo_stack: List[TransactionRecord] = []
        self._redo_stack: List[TransactionRecord] = []
        self._tx_counter: int = 0
        self._active_batch: Optional[Dict[str, Any]] = None

    @property
    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    @property
    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    @property
    def undo_count(self) -> int:
        return len(self._undo_stack)

    @property
    def redo_count(self) -> int:
        return len(self._redo_stack)

    def _next_tx_id(self) -> str:
        self._tx_counter += 1
        return f"tx_{int(time.time()*1000)}_{self._tx_counter}"

    def begin_batch(self, description: str = 'Compound Batch') -> None:
        """Begins an explicit multi-step transaction batch."""
        if self._active_batch is not None:
            raise RuntimeError('Transaction batch already active')
        self._active_batch = {
            'tx_id': self._next_tx_id(),
            'description': description,
            'timestamp': time.time(),
            'cell_mutations': [],
            'topology_mutations': [],
            'metadata': {}
        }

    def commit_batch(self) -> Optional[TransactionRecord]:
        """Finalizes the active batch and registers it as a single undoable record."""
        if self._active_batch is None:
            raise RuntimeError('No active batch to commit')
        batch = self._active_batch
        self._active_batch = None

        if not batch['cell_mutations'] and not batch['topology_mutations']:
            return None

        record = TransactionRecord(
            tx_id=batch['tx_id'],
            description=batch['description'],
            timestamp=batch['timestamp'],
            cell_mutations=tuple(batch['cell_mutations']),
            topology_mutations=tuple(batch['topology_mutations']),
            metadata=batch['metadata']
        )
        self._push_undo(record)
        return record

    def abort_batch(self) -> None:
        """Aborts the active batch, rolling back any actions accumulated during the batch."""
        if self._active_batch is None:
            raise RuntimeError('No active batch to abort')
        batch = self._active_batch
        self._active_batch = None

        # Revert cell mutations in reverse order
        for mut in reversed(batch['cell_mutations']):
            if mut.old_value == '':
                self.arbitrator.cell_store.pop((mut.row, mut.col), None)
            else:
                self.arbitrator.cell_store[(mut.row, mut.col)] = mut.old_value

        # Revert topology in reverse order
        for topo in reversed(batch['topology_mutations']):
            if topo.action == 'added':
                self.arbitrator.remove_merge(topo.merge_id)
            elif topo.action == 'removed':
                self.arbitrator.add_merge(topo.merge_id, topo.r0, topo.c0, topo.r1, topo.c1)

    def record_paste_plan(self, plan: PastePlan, description: str = 'Paste Tabular Data') -> Optional[TransactionRecord]:
        """Executes a PastePlan and records its atomic transaction in the journal."""
        if plan.is_vetoed or (not plan.mutations and not plan.unmerged_regions):
            return None

        # Record auto-unmerged topologies first
        topo_muts: List[MergeRegionMutation] = []
        for merge_id in plan.unmerged_regions:
            if merge_id in self.arbitrator.merges:
                r0, c0, r1, c1 = self.arbitrator.merges[merge_id]
                self.arbitrator.remove_merge(merge_id)
                topo_muts.append(MergeRegionMutation(
                    action='removed',
                    merge_id=merge_id,
                    r0=r0, c0=c0, r1=r1, c1=c1
                ))

        # Apply cell mutations
        for mut in plan.mutations:
            if mut.new_value == '':
                self.arbitrator.cell_store.pop((mut.row, mut.col), None)
            else:
                self.arbitrator.cell_store[(mut.row, mut.col)] = mut.new_value

        record = TransactionRecord(
            tx_id=self._next_tx_id(),
            description=description,
            timestamp=time.time(),
            cell_mutations=plan.mutations,
            topology_mutations=tuple(topo_muts),
            metadata={'pasted_cells': len(plan.mutations), 'unmerged_count': len(topo_muts)}
        )

        if self._active_batch is not None:
            self._active_batch['cell_mutations'].extend(plan.mutations)
            self._active_batch['topology_mutations'].extend(topo_muts)
            return record

        self._push_undo(record)
        return record

    def record_cell_edit(self,
                         row: int,
                         col: int,
                         new_value: str,
                         new_formula: Optional[str] = None,
                         description: str = 'Edit Cell') -> TransactionRecord:
        """Records a single cell scalar or formula edit."""
        old_value = self.arbitrator.cell_store.get((row, col), '')
        mut = CellMutation(
            row=row,
            col=col,
            old_value=old_value,
            new_value=new_value,
            
            
        )

        if new_value == '':
            self.arbitrator.cell_store.pop((row, col), None)
        else:
            self.arbitrator.cell_store[(row, col)] = new_value

        record = TransactionRecord(
            tx_id=self._next_tx_id(),
            description=description,
            timestamp=time.time(),
            cell_mutations=(mut,),
            topology_mutations=(),
            metadata={'row': row, 'col': col}
        )

        if self._active_batch is not None:
            self._active_batch['cell_mutations'].append(mut)
            return record

        self._push_undo(record)
        return record

    def record_merge_region(self,
                            merge_id: str,
                            r0: int,
                            c0: int,
                            r1: int,
                            c1: int,
                            description: str = 'Merge Cells') -> TransactionRecord:
        """Adds a merge region and records the topology transaction."""
        self.arbitrator.add_merge(merge_id, r0, c0, r1, c1)
        topo_mut = MergeRegionMutation(
            action='added',
            merge_id=merge_id,
            r0=r0, c0=c0, r1=r1, c1=c1
        )
        record = TransactionRecord(
            tx_id=self._next_tx_id(),
            description=description,
            timestamp=time.time(),
            cell_mutations=(),
            topology_mutations=(topo_mut,),
            metadata={'merge_id': merge_id}
        )

        if self._active_batch is not None:
            self._active_batch['topology_mutations'].append(topo_mut)
            return record

        self._push_undo(record)
        return record

    def record_unmerge_region(self,
                              merge_id: str,
                              description: str = 'Unmerge Cells') -> TransactionRecord:
        """Removes a merge region and records the topology transaction."""
        if merge_id not in self.arbitrator.merges:
            raise KeyError(f'Merge ID {merge_id} not found')
        r0, c0, r1, c1 = self.arbitrator.merges[merge_id]
        self.arbitrator.remove_merge(merge_id)

        topo_mut = MergeRegionMutation(
            action='removed',
            merge_id=merge_id,
            r0=r0, c0=c0, r1=r1, c1=c1
        )
        record = TransactionRecord(
            tx_id=self._next_tx_id(),
            description=description,
            timestamp=time.time(),
            cell_mutations=(),
            topology_mutations=(topo_mut,),
            metadata={'merge_id': merge_id}
        )

        if self._active_batch is not None:
            self._active_batch['topology_mutations'].append(topo_mut)
            return record

        self._push_undo(record)
        return record

    def _push_undo(self, record: TransactionRecord) -> None:
        self._undo_stack.append(record)
        self._redo_stack.clear()  # Atomic branch clearing
        if len(self._undo_stack) > self.max_history:
            self._undo_stack.pop(0)  # Bounded capacity eviction

    def undo(self) -> Optional[TransactionRecord]:
        """Undoes the most recent transaction, restoring previous values and topology."""
        if not self.can_undo:
            return None

        record = self._undo_stack.pop()

        # Revert cell values in reverse order
        for mut in reversed(record.cell_mutations):
            if mut.old_value == '':
                self.arbitrator.cell_store.pop((mut.row, mut.col), None)
            else:
                self.arbitrator.cell_store[(mut.row, mut.col)] = mut.old_value

        # Revert topology in reverse order
        for topo in reversed(record.topology_mutations):
            if topo.action == 'added':
                self.arbitrator.remove_merge(topo.merge_id)
            elif topo.action == 'removed':
                self.arbitrator.add_merge(topo.merge_id, topo.r0, topo.c0, topo.r1, topo.c1)

        self._redo_stack.append(record)
        return record

    def redo(self) -> Optional[TransactionRecord]:
        """Redoes the most recently undone transaction."""
        if not self.can_redo:
            return None

        record = self._redo_stack.pop()

        # Re-apply topology mutations forward
        for topo in record.topology_mutations:
            if topo.action == 'added':
                self.arbitrator.add_merge(topo.merge_id, topo.r0, topo.c0, topo.r1, topo.c1)
            elif topo.action == 'removed':
                self.arbitrator.remove_merge(topo.merge_id)

        # Re-apply cell mutations forward
        for mut in record.cell_mutations:
            if mut.new_value == '':
                self.arbitrator.cell_store.pop((mut.row, mut.col), None)
            else:
                self.arbitrator.cell_store[(mut.row, mut.col)] = mut.new_value

        self._undo_stack.append(record)
        return record

    @staticmethod
    def _is_cell_in_ranges(row: int, col: int, target_ranges: Sequence[SelectionBox]) -> bool:
        """Determines if (row, col) is within any of the provided SelectionBox bounding boxes."""
        for box in target_ranges:
            if box.r0 <= row <= box.r1 and box.c0 <= col <= box.c1:
                return True
        return False

    @staticmethod
    def _is_topo_in_ranges(topo: MergeRegionMutation, target_ranges: Sequence[SelectionBox]) -> bool:
        """Determines if a merge region intersects with any of the provided SelectionBox bounding boxes."""
        for box in target_ranges:
            # Check AABB intersection: not (r1 < box.r0 or r0 > box.r1 or c1 < box.c0 or c0 > box.c1)
            if not (topo.r1 < box.r0 or topo.r0 > box.r1 or topo.c1 < box.c0 or topo.c0 > box.c1):
                return True
        return False

    def undo_selective(self, target_ranges: Sequence[SelectionBox]) -> Optional[TransactionRecord]:
        """Undoes transactions affecting only cells/regions within the target selection ranges.

        Searches backward from the top of the undo stack for the newest transaction
        that contains mutations within target_ranges.
        If found:
        - Reverts only the matching mutations within target_ranges.
        - Splits the transaction: matching mutations move to redo stack; remaining mutations
          stay in place or are partitioned.
        """
        if not self._undo_stack or not target_ranges:
            return None

        # Search backward from top of stack
        for idx in range(len(self._undo_stack) - 1, -1, -1):
            record = self._undo_stack[idx]

            matching_cells = [m for m in record.cell_mutations if self._is_cell_in_ranges(m.row, m.col, target_ranges)]
            matching_topos = [t for t in record.topology_mutations if self._is_topo_in_ranges(t, target_ranges)]

            if not matching_cells and not matching_topos:
                continue

            # Found target transaction record
            self._undo_stack.pop(idx)

            # Revert matching cells
            for mut in reversed(matching_cells):
                if mut.old_value == '':
                    self.arbitrator.cell_store.pop((mut.row, mut.col), None)
                else:
                    self.arbitrator.cell_store[(mut.row, mut.col)] = mut.old_value

            # Revert matching topology
            for topo in reversed(matching_topos):
                if topo.action == 'added':
                    self.arbitrator.remove_merge(topo.merge_id)
                elif topo.action == 'removed':
                    self.arbitrator.add_merge(topo.merge_id, topo.r0, topo.c0, topo.r1, topo.c1)

            # Create undone record slice
            undone_slice = TransactionRecord(
                tx_id=f"{record.tx_id}_selective_undone",
                description=f"{record.description} (Selective Undo)",
                timestamp=time.time(),
                cell_mutations=tuple(matching_cells),
                topology_mutations=tuple(matching_topos),
                metadata={'selective': True, 'parent_tx_id': record.tx_id}
            )
            self._redo_stack.append(undone_slice)

            # Keep remaining non-matching mutations in undo stack at same index if any
            remaining_cells = [m for m in record.cell_mutations if not self._is_cell_in_ranges(m.row, m.col, target_ranges)]
            remaining_topos = [t for t in record.topology_mutations if not self._is_topo_in_ranges(t, target_ranges)]

            if remaining_cells or remaining_topos:
                kept_record = TransactionRecord(
                    tx_id=record.tx_id,
                    description=record.description,
                    timestamp=record.timestamp,
                    cell_mutations=tuple(remaining_cells),
                    topology_mutations=tuple(remaining_topos),
                    metadata=record.metadata
                )
                self._undo_stack.insert(idx, kept_record)

            return undone_slice

        return None

    def redo_selective(self, target_ranges: Sequence[SelectionBox]) -> Optional[TransactionRecord]:
        """Redoes transactions affecting only cells/regions within target selection ranges."""
        if not self._redo_stack or not target_ranges:
            return None

        # Search backward from top of redo stack
        for idx in range(len(self._redo_stack) - 1, -1, -1):
            record = self._redo_stack[idx]

            matching_cells = [m for m in record.cell_mutations if self._is_cell_in_ranges(m.row, m.col, target_ranges)]
            matching_topos = [t for t in record.topology_mutations if self._is_topo_in_ranges(t, target_ranges)]

            if not matching_cells and not matching_topos:
                continue

            self._redo_stack.pop(idx)

            # Re-apply matching topology
            for topo in matching_topos:
                if topo.action == 'added':
                    self.arbitrator.add_merge(topo.merge_id, topo.r0, topo.c0, topo.r1, topo.c1)
                elif topo.action == 'removed':
                    self.arbitrator.remove_merge(topo.merge_id)

            # Re-apply matching cells
            for mut in matching_cells:
                if mut.new_value == '':
                    self.arbitrator.cell_store.pop((mut.row, mut.col), None)
                else:
                    self.arbitrator.cell_store[(mut.row, mut.col)] = mut.new_value

            redone_slice = TransactionRecord(
                tx_id=f"{record.tx_id}_selective_redone",
                description=f"{record.description} (Selective Redo)",
                timestamp=time.time(),
                cell_mutations=tuple(matching_cells),
                topology_mutations=tuple(matching_topos),
                metadata={'selective': True, 'parent_tx_id': record.tx_id}
            )
            self._undo_stack.append(redone_slice)

            # Keep remaining in redo stack if any
            remaining_cells = [m for m in record.cell_mutations if not self._is_cell_in_ranges(m.row, m.col, target_ranges)]
            remaining_topos = [t for t in record.topology_mutations if not self._is_topo_in_ranges(t, target_ranges)]

            if remaining_cells or remaining_topos:
                kept_record = TransactionRecord(
                    tx_id=record.tx_id,
                    description=record.description,
                    timestamp=record.timestamp,
                    cell_mutations=tuple(remaining_cells),
                    topology_mutations=tuple(remaining_topos),
                    metadata=record.metadata
                )
                self._redo_stack.insert(idx, kept_record)

            return redone_slice

        return None

    def export_compressed_delta(self) -> Dict[str, Any]:
        """Serializes undo/redo journal and cell store deltas to a compressed payload.

        Encodes full state to JSON, compresses via zlib deflate, and base64 encodes
        for safe storage in LocalStorage or IndexedDB with zero whitespace waste.
        """
        raw_payload = {
            'v': 1,
            'timestamp': time.time(),
            'max_history': self.max_history,
            'tx_counter': self._tx_counter,
            'undo_stack': [r.to_dict() for r in self._undo_stack],
            'redo_stack': [r.to_dict() for r in self._redo_stack],
            'merges': {
                k: list(v) for k, v in self.arbitrator.merges.items()
            },
            'cell_store': {
                f"{r},{c}": val for (r, c), val in self.arbitrator.cell_store.items()
            }
        }
        json_bytes = json.dumps(raw_payload, separators=(',', ':')).encode('utf-8')
        compressed = zlib.compress(json_bytes, level=9)
        b64_str = base64.b64encode(compressed).decode('ascii')

        raw_size = len(json_bytes)
        compressed_size = len(compressed)
        ratio = compressed_size / raw_size if raw_size > 0 else 1.0

        return {
            'compression': 'zlib_base64',
            'raw_bytes': raw_size,
            'compressed_bytes': compressed_size,
            'compression_ratio': round(ratio, 4),
            'data': b64_str
        }

    def import_compressed_delta(self, package: Dict[str, Any], restore_cells_and_topology: bool = True) -> bool:
        """Decompresses and restores journal, cell store, and merge topology from package."""
        if package.get('compression') != 'zlib_base64' or 'data' not in package:
            raise ValueError('Invalid compressed delta package')

        compressed = base64.b64decode(package['data'])
        json_bytes = zlib.decompress(compressed)
        payload = json.loads(json_bytes.decode('utf-8'))

        self.max_history = int(payload.get('max_history', self.max_history))
        self._tx_counter = int(payload.get('tx_counter', 0))
        self._undo_stack = [TransactionRecord.from_dict(d) for d in payload.get('undo_stack', [])]
        self._redo_stack = [TransactionRecord.from_dict(d) for d in payload.get('redo_stack', [])]

        if restore_cells_and_topology:
            # Restore cell store
            self.arbitrator.cell_store.clear()
            for key_str, val in payload.get('cell_store', {}).items():
                r_s, c_s = key_str.split(',')
                self.arbitrator.cell_store[(int(r_s), int(c_s))] = val

            # Restore merges
            self.arbitrator.merges.clear()
            self.arbitrator.cell_merge_owners.clear()
            for merge_id, coords in payload.get('merges', {}).items():
                self.arbitrator.add_merge(merge_id, coords[0], coords[1], coords[2], coords[3])

        return True

    def clear(self) -> None:
        """Clears both undo and redo stacks."""
        self._undo_stack.clear()
        self._redo_stack.clear()

    def export_journal_manifest(self) -> Dict[str, Any]:
        """Exports full journal state for telemetry and verification."""
        return {
            'max_history': self.max_history,
            'undo_count': self.undo_count,
            'redo_count': self.redo_count,
            'can_undo': self.can_undo,
            'can_redo': self.can_redo,
            'undo_stack': [
                {
                    'tx_id': r.tx_id,
                    'description': r.description,
                    'cells_mutated': len(r.cell_mutations),
                    'topology_mutated': len(r.topology_mutations)
                } for r in self._undo_stack
            ],
            'redo_stack': [
                {
                    'tx_id': r.tx_id,
                    'description': r.description,
                    'cells_mutated': len(r.cell_mutations),
                    'topology_mutated': len(r.topology_mutations)
                } for r in self._redo_stack
            ]
        }
