import unittest
import copy
from spanning_grid import SpanIndex
from dom_adapter import snapshot
from commit_recovery import GridCommitModel, CommitError


class CommitRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.index = SpanIndex(20, 20)
        self.index.add(7, 1, 1, 4, 4)
        self.snap_initial = snapshot(self.index, (2, 2, 6, 6))
        self.snap_next = snapshot(self.index, (3, 3, 7, 7))

    def tearDown(self):
        self.index.db.close()

    def test_successful_commit_advances_revision_and_state(self):
        model = GridCommitModel(self.snap_initial)
        rev = model.begin_snapshot_request()
        ok = model.apply_snapshot(rev, self.snap_next)
        self.assertTrue(ok)
        self.assertEqual(model.applied_revision, rev)
        self.assertEqual(model.data['window'], [3, 3, 7, 7])
        self.assertEqual(model.cursor, [3, 3])
        self.assertEqual(model.focused_id, 'merge-7')

    def test_rollback_on_pre_validate_failure(self):
        model = GridCommitModel(self.snap_initial)
        rev = model.begin_snapshot_request()
        ok = model.apply_snapshot(rev, self.snap_next, fail_phase='pre_validate')
        self.assertFalse(ok)
        self.assertEqual(model.applied_revision, 0)
        self.assertEqual(model.data['window'], [2, 2, 6, 6])
        self.assertEqual(model.cursor, [2, 2])
        self.assertEqual(model.focused_id, 'merge-7')

    def test_rollback_on_create_nodes_failure(self):
        model = GridCommitModel(self.snap_initial)
        rev = model.begin_snapshot_request()
        ok = model.apply_snapshot(rev, self.snap_next, fail_phase='create_nodes')
        self.assertFalse(ok)
        self.assertEqual(model.applied_revision, 0)
        self.assertEqual(model.data['window'], [2, 2, 6, 6])
        self.assertEqual(model.cursor, [2, 2])
        self.assertEqual(model.focused_id, 'merge-7')
        self.assertEqual(len(model.nodes), len(self.snap_initial['cells']))

    def test_rollback_on_dom_mutation_failure(self):
        model = GridCommitModel(self.snap_initial)
        rev = model.begin_snapshot_request()
        ok = model.apply_snapshot(rev, self.snap_next, fail_phase='dom_mutation')
        self.assertFalse(ok)
        self.assertEqual(model.applied_revision, 0)
        self.assertEqual(model.data['window'], [2, 2, 6, 6])
        self.assertEqual(model.cursor, [2, 2])
        self.assertNotIn('corrupted', model.nodes)
        self.assertEqual(model.focused_id, 'merge-7')

    def test_rollback_on_focus_restore_failure(self):
        model = GridCommitModel(self.snap_initial)
        rev = model.begin_snapshot_request()
        ok = model.apply_snapshot(rev, self.snap_next, fail_phase='focus_restore')
        self.assertFalse(ok)
        self.assertEqual(model.applied_revision, 0)
        self.assertEqual(model.data['window'], [2, 2, 6, 6])
        self.assertEqual(model.cursor, [2, 2])
        self.assertEqual(model.focused_id, 'merge-7')

    def test_retry_after_failed_commit_succeeds_on_same_revision(self):
        model = GridCommitModel(self.snap_initial)
        rev = model.begin_snapshot_request()
        # First attempt fails at dom_mutation
        ok1 = model.apply_snapshot(rev, self.snap_next, fail_phase='dom_mutation')
        self.assertFalse(ok1)
        self.assertEqual(model.applied_revision, 0)
        # Retry without failure succeeds on same issued token
        ok2 = model.apply_snapshot(rev, self.snap_next)
        self.assertTrue(ok2)
        self.assertEqual(model.applied_revision, rev)
        self.assertEqual(model.data['window'], [3, 3, 7, 7])


if __name__ == '__main__':
    unittest.main()
