"""Deterministic unit tests for TransactionJournal (UIUX-042 & UIUX-043)."""

import unittest
from tabular_paste_arbitrator import TabularPasteArbitrator, SelectionBox
from transaction_journal import TransactionJournal, MergeRegionMutation, TransactionRecord


class TestTransactionJournal(unittest.TestCase):

    def setUp(self):
        self.arbitrator = TabularPasteArbitrator(grid_rows=100, grid_cols=50)
        self.journal = TransactionJournal(self.arbitrator, max_history=5)

    def test_initial_state(self):
        self.assertFalse(self.journal.can_undo)
        self.assertFalse(self.journal.can_redo)
        self.assertEqual(self.journal.undo_count, 0)
        self.assertEqual(self.journal.redo_count, 0)

    def test_single_cell_edit_undo_redo(self):
        self.journal.record_cell_edit(5, 5, "Hello")
        self.assertEqual(self.arbitrator.cell_store[(5, 5)], "Hello")
        self.assertTrue(self.journal.can_undo)
        self.assertFalse(self.journal.can_redo)

        # Undo
        tx = self.journal.undo()
        self.assertIsNotNone(tx)
        self.assertNotIn((5, 5), self.arbitrator.cell_store)
        self.assertFalse(self.journal.can_undo)
        self.assertTrue(self.journal.can_redo)

        # Redo
        tx_redo = self.journal.redo()
        self.assertIsNotNone(tx_redo)
        self.assertEqual(self.arbitrator.cell_store[(5, 5)], "Hello")
        self.assertTrue(self.journal.can_undo)
        self.assertFalse(self.journal.can_redo)

    def test_merge_region_topology_undo_redo(self):
        self.journal.record_merge_region('header-span', 0, 0, 1, 5)
        self.assertIn('header-span', self.arbitrator.merges)
        self.assertEqual(self.arbitrator.cell_merge_owners[(0, 0)], 'header-span')
        self.assertEqual(self.arbitrator.cell_merge_owners[(0, 4)], 'header-span')

        # Undo merge
        self.journal.undo()
        self.assertNotIn('header-span', self.arbitrator.merges)
        self.assertNotIn((0, 0), self.arbitrator.cell_merge_owners)

        # Redo merge
        self.journal.redo()
        self.assertIn('header-span', self.arbitrator.merges)
        self.assertEqual(self.arbitrator.cell_merge_owners[(0, 0)], 'header-span')

    def test_unmerge_region_topology_undo_redo(self):
        self.arbitrator.add_merge('box1', 10, 10, 12, 12)
        self.assertIn('box1', self.arbitrator.merges)

        self.journal.record_unmerge_region('box1')
        self.assertNotIn('box1', self.arbitrator.merges)

        # Undo unmerge -> restores merge
        self.journal.undo()
        self.assertIn('box1', self.arbitrator.merges)
        self.assertEqual(self.arbitrator.cell_merge_owners[(10, 10)], 'box1')

        # Redo unmerge -> removes again
        self.journal.redo()
        self.assertNotIn('box1', self.arbitrator.merges)

    def test_compound_paste_with_auto_unmerge_undo_redo(self):
        # Merge exists
        self.arbitrator.add_merge('old-merge', 2, 2, 4, 4)
        self.assertIn('old-merge', self.arbitrator.merges)

        # Paste 2x2 table over [2, 2] to [3, 3] with auto_unmerge
        raw = "V1\tV2\nV3\tV4"
        plan = self.arbitrator.plan_paste(raw, SelectionBox(2, 2, 2, 2), merge_policy='auto_unmerge')
        self.assertFalse(plan.is_vetoed)

        tx = self.journal.record_paste_plan(plan, description='Auto-unmerge paste')
        self.assertIsNotNone(tx)
        self.assertNotIn('old-merge', self.arbitrator.merges)
        self.assertEqual(self.arbitrator.cell_store[(2, 2)], 'V1')
        self.assertEqual(self.arbitrator.cell_store[(3, 3)], 'V4')

        # Undo compound transaction: both cell values revert and merge region is restored
        self.journal.undo()
        self.assertIn('old-merge', self.arbitrator.merges)
        self.assertEqual(self.arbitrator.cell_merge_owners[(2, 2)], 'old-merge')
        self.assertEqual(self.arbitrator.cell_merge_owners[(3, 3)], 'old-merge')
        self.assertNotIn((2, 2), self.arbitrator.cell_store)
        self.assertNotIn((3, 3), self.arbitrator.cell_store)

        # Redo compound transaction: unmerges again and restores cell values
        self.journal.redo()
        self.assertNotIn('old-merge', self.arbitrator.merges)
        self.assertEqual(self.arbitrator.cell_store[(2, 2)], 'V1')
        self.assertEqual(self.arbitrator.cell_store[(3, 3)], 'V4')

    def test_bounded_capacity_eviction(self):
        # Max capacity is 5
        for i in range(10):
            self.journal.record_cell_edit(i, 0, f"Val_{i}")

        self.assertEqual(self.journal.undo_count, 5)
        # Oldest transactions (0..4) were evicted, 5..9 remain
        for i in range(5):
            self.journal.undo()
        self.assertFalse(self.journal.can_undo)
        # Cell (5, 0) was undone
        self.assertNotIn((5, 0), self.arbitrator.cell_store)
        # Cell (4, 0) was evicted from undo stack, so its value remains persisted
        self.assertEqual(self.arbitrator.cell_store[(4, 0)], "Val_4")

    def test_branch_truncation_on_new_commit(self):
        self.journal.record_cell_edit(1, 1, "First")
        self.journal.record_cell_edit(1, 1, "Second")
        self.journal.undo()
        self.assertEqual(self.journal.redo_count, 1)

        # New action truncates redo stack
        self.journal.record_cell_edit(1, 1, "BranchNew")
        self.assertEqual(self.journal.redo_count, 0)
        self.assertFalse(self.journal.can_redo)
        self.assertEqual(self.arbitrator.cell_store[(1, 1)], "BranchNew")

    def test_batch_transaction_grouping_and_abort(self):
        # Successful batch
        self.journal.begin_batch('Multi-action batch')
        self.journal.record_cell_edit(0, 0, "A")
        self.journal.record_cell_edit(0, 1, "B")
        self.journal.record_merge_region('batch-merge', 10, 10, 12, 12)
        record = self.journal.commit_batch()
        self.assertIsNotNone(record)
        self.assertEqual(len(record.cell_mutations), 2)
        self.assertEqual(len(record.topology_mutations), 1)
        self.assertEqual(self.journal.undo_count, 1)

        # Single undo reverts all 3 actions atomically
        self.journal.undo()
        self.assertNotIn((0, 0), self.arbitrator.cell_store)
        self.assertNotIn((0, 1), self.arbitrator.cell_store)
        self.assertNotIn('batch-merge', self.arbitrator.merges)

        # Abort batch test
        self.journal.begin_batch('Aborted batch')
        self.journal.record_cell_edit(5, 5, "Temporary")
        self.assertEqual(self.arbitrator.cell_store[(5, 5)], "Temporary")
        self.journal.abort_batch()
        self.assertNotIn((5, 5), self.arbitrator.cell_store)
        self.assertIsNone(self.journal._active_batch)

    def test_journal_manifest_export(self):
        self.journal.record_cell_edit(2, 2, "TestVal")
        manifest = self.journal.export_journal_manifest()
        self.assertEqual(manifest['max_history'], 5)
        self.assertEqual(manifest['undo_count'], 1)
        self.assertEqual(manifest['redo_count'], 0)
        self.assertTrue(manifest['can_undo'])
        self.assertEqual(manifest['undo_stack'][0]['cells_mutated'], 1)

    # UIUX-043 Unit Tests
    def test_selective_range_undo_single_cell(self):
        # Batch with mutations in multiple regions
        self.journal.begin_batch('Multi-region update')
        self.journal.record_cell_edit(2, 2, "RegionA")
        self.journal.record_cell_edit(8, 8, "RegionB")
        self.journal.commit_batch()

        self.assertEqual(self.arbitrator.cell_store[(2, 2)], "RegionA")
        self.assertEqual(self.arbitrator.cell_store[(8, 8)], "RegionB")

        # Selective undo targeting ONLY RegionA bounding box [2, 2] to [3, 3]
        target_box = [SelectionBox(2, 2, 3, 3)]
        tx = self.journal.undo_selective(target_box)
        self.assertIsNotNone(tx)
        self.assertEqual(len(tx.cell_mutations), 1)
        self.assertEqual(tx.cell_mutations[0].row, 2)

        # RegionA is undone, RegionB remains intact!
        self.assertNotIn((2, 2), self.arbitrator.cell_store)
        self.assertEqual(self.arbitrator.cell_store[(8, 8)], "RegionB")

        # Redo selective restores RegionA
        tx_redo = self.journal.redo_selective(target_box)
        self.assertIsNotNone(tx_redo)
        self.assertEqual(self.arbitrator.cell_store[(2, 2)], "RegionA")

    def test_selective_range_undo_with_merge_topology(self):
        self.journal.begin_batch('Topology and cell mutations')
        self.journal.record_cell_edit(1, 1, "Cell1")
        self.journal.record_merge_region('m_box', 10, 10, 12, 12)
        self.journal.commit_batch()

        self.assertIn('m_box', self.arbitrator.merges)
        self.assertEqual(self.arbitrator.cell_store[(1, 1)], "Cell1")

        # Selective undo on merge region [10, 10] to [12, 12]
        target_box = [SelectionBox(10, 10, 12, 12)]
        tx = self.journal.undo_selective(target_box)
        self.assertIsNotNone(tx)
        self.assertNotIn('m_box', self.arbitrator.merges)
        # Cell1 remains untouched in cell store!
        self.assertEqual(self.arbitrator.cell_store[(1, 1)], "Cell1")

        # Selective redo restores merge
        tx_redo = self.journal.redo_selective(target_box)
        self.assertIsNotNone(tx_redo)
        self.assertIn('m_box', self.arbitrator.merges)

    def test_compressed_delta_export_and_import(self):
        self.journal.record_cell_edit(0, 0, "TopLeft")
        self.journal.record_cell_edit(10, 10, "BottomRight")
        self.journal.record_merge_region('span_test', 4, 4, 6, 6)

        # Export compressed delta package
        package = self.journal.export_compressed_delta()
        self.assertEqual(package['compression'], 'zlib_base64')
        self.assertGreater(package['raw_bytes'], 0)
        self.assertGreater(package['compressed_bytes'], 0)
        self.assertIsInstance(package['data'], str)

        # Create fresh arbitrator and journal
        fresh_arb = TabularPasteArbitrator(grid_rows=100, grid_cols=50)
        fresh_journal = TransactionJournal(fresh_arb, max_history=5)

        # Import compressed delta
        ok = fresh_journal.import_compressed_delta(package)
        self.assertTrue(ok)
        self.assertEqual(fresh_arb.cell_store[(0, 0)], "TopLeft")
        self.assertEqual(fresh_arb.cell_store[(10, 10)], "BottomRight")
        self.assertIn('span_test', fresh_arb.merges)
        self.assertEqual(fresh_journal.undo_count, 3)

        # Can undo from restored session
        tx = fresh_journal.undo()
        self.assertIsNotNone(tx)
        self.assertNotIn('span_test', fresh_arb.merges)


if __name__ == '__main__':
    unittest.main()
