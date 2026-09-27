#!/usr/bin/env python3
"""
Unit tests for Live Intervention Splicing & Dynamic Topological Task Rescheduling.
Tests:
1. DAG Construction & Kahn's Topological Ordering.
2. Causal Downstream Cone Calculation.
3. Downstream Invalidation upon Intervention.
4. Live Task Splicing without cycle.
5. Cycle Detection & Atomic Rollback upon circular dependency.
6. Dynamic Rescheduling preserving completed tasks.
7. Amdahl Concurrency & Speedup Bounds.
"""

import unittest
from dag_splicing_engine import (
    InterventionDAGSplicer,
    TaskNode,
    TaskState,
    DAGCycleError,
    SplicingConflictError
)


class TestInterventionDAGSplicer(unittest.TestCase):

    def setUp(self):
        self.splicer = InterventionDAGSplicer(dag_id="test-dag")
        # Build initial pipeline:
        # A (fetch) -> B (clean) -> C (model) -> D (report)
        #            \-> E (audit) -/
        self.splicer.add_task(TaskNode("A", "Fetch Data", "fetch", 50.0))
        self.splicer.add_task(TaskNode("B", "Clean Data", "clean", 100.0), dependencies=["A"])
        self.splicer.add_task(TaskNode("E", "Audit Spec", "audit", 80.0), dependencies=["A"])
        self.splicer.add_task(TaskNode("C", "Train Model", "train", 200.0), dependencies=["B", "E"])
        self.splicer.add_task(TaskNode("D", "Generate Report", "report", 40.0), dependencies=["C"])

    def test_01_topological_order(self):
        sched = self.splicer.reschedule_topological_order()
        self.assertEqual(sched[0], "A")
        self.assertEqual(sched[-1], "D")
        self.assertIn("B", sched)
        self.assertIn("E", sched)
        self.assertIn("C", sched)

    def test_02_causal_downstream_cone(self):
        cone_b = self.splicer.get_causal_downstream_cone("B")
        self.assertEqual(cone_b, {"C", "D"})

        cone_a = self.splicer.get_causal_downstream_cone("A")
        self.assertEqual(cone_a, {"B", "E", "C", "D"})

    def test_03_invalidation_causal_cone(self):
        # Mark A, B, E as COMPLETED
        self.splicer.nodes["A"].state = TaskState.COMPLETED
        self.splicer.nodes["B"].state = TaskState.COMPLETED
        self.splicer.nodes["E"].state = TaskState.COMPLETED

        # Mutate B via intervention -> C and D must be invalidated
        inv = self.splicer.invalidate_causal_cone("B", reason="Schema changed in B")
        self.assertIn("C", inv)
        self.assertIn("D", inv)
        self.assertEqual(self.splicer.nodes["C"].state, TaskState.INVALIDATED)
        self.assertEqual(self.splicer.nodes["D"].state, TaskState.INVALIDATED)

    def test_04_live_splicing_success(self):
        # Splice a verification gate V between B and C
        # Old: B -> C
        # New: B -> V -> C
        gate_node = TaskNode("V", "Verify Cleanliness", "verify", 30.0)
        record = self.splicer.splice_intervention_nodes(
            intervention_nodes=[gate_node],
            splice_edges=[("B", "V"), ("V", "C")],
            remove_edges=[("B", "C")],
            reason="Insert runtime verification gate"
        )
        self.assertEqual(record["status"], "SUCCESS")
        self.assertIn("V", self.splicer.nodes)
        self.assertIn("V", self.splicer.edges["B"])
        self.assertIn("C", self.splicer.edges["V"])
        self.assertNotIn("C", self.splicer.edges["B"])

    def test_05_cycle_detection_and_atomic_rollback(self):
        # Attempt to introduce circular edge D -> A via splice
        loop_node = TaskNode("L", "Loop Back", "loop", 10.0)
        with self.assertRaises(DAGCycleError):
            self.splicer.splice_intervention_nodes(
                intervention_nodes=[loop_node],
                splice_edges=[("D", "L"), ("L", "A")],
                reason="Invalid loop attempt"
            )

        # Verify atomic rollback: node L should NOT exist in DAG
        self.assertNotIn("L", self.splicer.nodes)
        self.assertFalse(self.splicer.detect_cycle())

    def test_06_reschedule_preserving_completed_tasks(self):
        # Complete A and E
        self.splicer.nodes["A"].state = TaskState.COMPLETED
        self.splicer.nodes["E"].state = TaskState.COMPLETED

        # Reschedule remaining
        sched = self.splicer.reschedule_topological_order()
        # A and E should not be scheduled to run again
        self.assertNotIn("A", sched)
        self.assertNotIn("E", sched)
        self.assertEqual(sched, ["B", "C", "D"])

    def test_07_amdahl_speedup_bounds(self):
        res = self.splicer.calculate_amdahl_schedule_speedup(parallel_workers=4)
        self.assertGreater(res["theoretical_speedup"], 1.0)
        self.assertGreaterEqual(res["parallel_fraction"], 0.0)
        self.assertLessEqual(res["parallel_fraction"], 1.0)
        self.assertEqual(res["total_sequential_ms"], 470.0)


if __name__ == "__main__":
    unittest.main()
