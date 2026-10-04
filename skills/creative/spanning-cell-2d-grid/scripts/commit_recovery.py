"""Deterministic DOM commit failure injection and state restoration model.

Verifies rollback guarantees: if an exception occurs during the DOM commit phase
(e.g., node creation, attribute setting, style mutation, DOM insertion, focus restore),
the grid state, cursor, activeElement, nodes, and appliedRevision must be fully restored
to their pre-commit state with zero corruption.
"""
import copy


class CommitError(RuntimeError):
    """Synthetic DOM commit failure injection."""
    pass


class GridCommitModel:
    """Synchronous simulation model of the DOM adapter and revision gate with rollback."""

    def __init__(self, initial_data):
        self.issued_revision = 0
        self.applied_revision = 0
        self.data = copy.deepcopy(initial_data)
        self.nodes = {c['id']: {'id': c['id'], 'attrs': dict(c), 'style': {}} for c in self.data['cells']}
        self.cursor = list(self.data['window'][:2])  # [r0, c0]
        self.focused_id = self.data['owners'].get(f"{self.cursor[0]},{self.cursor[1]}")
        self.history = []

    def begin_snapshot_request(self):
        self.issued_revision += 1
        return self.issued_revision

    def replace_window(self, next_data, fail_phase=None):
        """
        Executes replaceWindow with checkpointing and rollback.
        fail_phase can be:
          - 'pre_validate': failure before validation
          - 'create_nodes': failure during node instantiation / fragment build
          - 'dom_mutation': failure during container replacement / style / attributes
          - 'focus_restore': failure during focus / cursor restoration
        """
        # 1. Capture exact snapshot checkpoint
        checkpoint = {
            'data': copy.deepcopy(self.data),
            'nodes': copy.deepcopy(self.nodes),
            'cursor': list(self.cursor) if self.cursor is not None else None,
            'focused_id': self.focused_id,
            'applied_revision': self.applied_revision,
        }

        try:
            if fail_phase == 'pre_validate':
                raise CommitError('Simulated failure before validation')

            # Validation phase (pure, no side-effects)
            from snapshot_schema import validate_snapshot
            validate_snapshot(next_data)

            if fail_phase == 'create_nodes':
                raise CommitError('Simulated failure during DOM node / fragment creation')

            # Staging phase
            fresh_nodes = {}
            for cell in next_data['cells']:
                fresh_nodes[cell['id']] = {
                    'id': cell['id'],
                    'attrs': {
                        'aria-rowindex': cell['row'] + 1,
                        'aria-colindex': cell['col'] + 1,
                        'aria-rowspan': cell['rowspan'],
                        'aria-colspan': cell['colspan'],
                    },
                    'style': {
                        'left': f"{cell['left']}px",
                        'top': f"{cell['top']}px",
                        'width': f"{cell['width']}px",
                        'height': f"{cell['height']}px",
                    }
                }

            r0, c0, r1, c1 = next_data['window']
            old_cursor = self.cursor
            point = None if (r0 == r1 or c0 == c1) else [
                min(max(old_cursor[0] if old_cursor else r0, r0), r1 - 1),
                min(max(old_cursor[1] if old_cursor else c0, c0), c1 - 1)
            ]

            if fail_phase == 'dom_mutation':
                # Partially mutate state to test rollback enforcement
                self.nodes = {'corrupted': True}
                self.cursor = [-999, -999]
                raise CommitError('Simulated failure during DOM mutation phase')

            # Commit state
            self.data = copy.deepcopy(next_data)
            self.nodes = fresh_nodes
            self.cursor = point

            if fail_phase == 'focus_restore':
                raise CommitError('Simulated failure during focus restore phase')

            if point is not None:
                self.focused_id = self.data['owners'].get(f"{point[0]},{point[1]}")
            else:
                self.focused_id = '__grid_container__'

            return True

        except Exception as exc:
            # ROLLBACK INVARIANT: Restore entire state from checkpoint
            self.data = checkpoint['data']
            self.nodes = checkpoint['nodes']
            self.cursor = checkpoint['cursor']
            self.focused_id = checkpoint['focused_id']
            self.applied_revision = checkpoint['applied_revision']
            raise exc

    def apply_snapshot(self, revision, next_data, fail_phase=None):
        if revision != self.issued_revision or revision <= self.applied_revision:
            return False
        
        # We attempt replace_window; if it throws, revision must NOT advance
        try:
            self.replace_window(next_data, fail_phase=fail_phase)
            self.applied_revision = revision
            return True
        except Exception:
            # Revision gate invariant: applied revision does not advance on commit error
            return False
