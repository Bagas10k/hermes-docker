"""Deterministic unit tests for TabularOTEngine (UIUX-044)."""

import unittest
import time
from tabular_ot_engine import TabularOTEngine, VectorClock, TabularOperation


class TestTabularOTEngine(unittest.TestCase):

    def test_vector_clock_causality_and_concurrency(self):
        vc1 = VectorClock({'A': 1, 'B': 0})
        vc2 = VectorClock({'A': 1, 'B': 1})
        self.assertTrue(vc2.dominates(vc1))
        self.assertFalse(vc1.dominates(vc2))
        self.assertFalse(vc1.is_concurrent(vc2))

        # Concurrent clocks: A has higher clock for A, B has higher clock for B
        vc_a = VectorClock({'A': 2, 'B': 1})
        vc_b = VectorClock({'A': 1, 'B': 2})
        self.assertTrue(vc_a.is_concurrent(vc_b))
        self.assertTrue(vc_b.is_concurrent(vc_a))
        self.assertFalse(vc_a.dominates(vc_b))

    def test_independent_cell_edits_convergence(self):
        client_a = TabularOTEngine('client_A')
        client_b = TabularOTEngine('client_B')

        op_a = client_a.create_cell_edit(1, 1, 'ValueA')
        op_b = client_b.create_cell_edit(2, 2, 'ValueB')

        # Cross propagate
        res_b, status_b = client_b.transform(op_a)
        res_a, status_a = client_a.transform(op_b)

        self.assertEqual(status_b, 'applied')
        self.assertEqual(status_a, 'applied')

        # Both clients converge to identical state
        self.assertEqual(client_a.cell_store, client_b.cell_store)
        self.assertEqual(client_a.cell_store[(1, 1)], 'ValueA')
        self.assertEqual(client_a.cell_store[(2, 2)], 'ValueB')

    def test_concurrent_cell_collision_arbitration_priority_and_lww(self):
        client_a = TabularOTEngine('client_A')
        client_b = TabularOTEngine('client_B')

        # Both edit cell (5, 5) concurrently
        op_a = client_a.create_cell_edit(5, 5, 'ValA', priority=10)
        op_b = client_b.create_cell_edit(5, 5, 'ValB', priority=5)

        # Cross propagate
        # Client B receives op_a (higher priority) -> op_a applies and overwrites
        res_b, status_b = client_b.transform(op_a)
        self.assertEqual(status_b, 'applied')
        self.assertEqual(client_b.cell_store[(5, 5)], 'ValA')

        # Client A receives op_b (lower priority) -> op_b is superseded
        res_a, status_a = client_a.transform(op_b)
        self.assertEqual(status_a, 'superseded')
        self.assertEqual(client_a.cell_store[(5, 5)], 'ValA')

        # Converged!
        self.assertEqual(client_a.cell_store[(5, 5)], client_b.cell_store[(5, 5)])

    def test_concurrent_merge_topology_conflict_resolution(self):
        client_a = TabularOTEngine('client_A')
        client_b = TabularOTEngine('client_B')

        # Client A merges [0,0] to [2,2] with higher priority
        op_a = client_a.create_merge('spanA', 0, 0, 2, 2, priority=20)
        # Client B merges overlapping [1,1] to [3,3] with lower priority
        op_b = client_b.create_merge('spanB', 1, 1, 3, 3, priority=10)

        # Client B receives op_a -> overlapping spanB is auto-unmerged in favour of spanA
        res_b, status_b = client_b.transform(op_a)
        self.assertEqual(status_b, 'applied')
        self.assertIn('spanA', client_b.merges)
        self.assertNotIn('spanB', client_b.merges)

        # Client A receives op_b -> vetoed because spanA has higher priority
        res_a, status_a = client_a.transform(op_b)
        self.assertEqual(status_a, 'vetoed')
        self.assertIn('spanA', client_a.merges)
        self.assertNotIn('spanB', client_a.merges)

        # Topology converged across clients!
        self.assertEqual(client_a.merges, client_b.merges)


if __name__ == '__main__':
    unittest.main()
