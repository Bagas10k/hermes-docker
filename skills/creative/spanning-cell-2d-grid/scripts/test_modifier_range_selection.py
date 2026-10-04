import unittest
import math
from modifier_range_selection import (
    ModifierRangeSelectionEngine,
    ModifierSelectionState,
    CellRange,
    finite_number
)


class ModifierRangeSelectionTests(unittest.TestCase):
    def setUp(self):
        self.engine = ModifierRangeSelectionEngine(row_px=32, col_px=96, rows=50, cols=50)
        # Populate specific data cells for Ctrl+Arrow testing
        # Row 5: data at cols 2, 3, 4 (contiguous), then empty at 5, 6, data at 7, 8
        for c in (2, 3, 4, 7, 8):
            self.engine.set_cell_data(5, c, True)

        # Col 10: data at rows 10, 11, 12, then empty at 13, data at 14
        for r in (10, 11, 12, 14):
            self.engine.set_cell_data(r, 10, True)

        # Merged region at [20, 20) to [23, 23) (3x3 merge)
        self.engine.add_merge('merge-box', 20, 20, 23, 23)

    def test_cell_range_properties(self):
        rng = CellRange(2, 3, 5, 8)
        self.assertEqual(rng.cell_count(), 4 * 6)
        self.assertTrue(rng.contains(3, 4))
        self.assertFalse(rng.contains(1, 4))
        self.assertFalse(rng.contains(6, 4))
        with self.assertRaises(ValueError):
            CellRange(5, 3, 2, 8)  # Inverted rows

    def test_plain_arrow_navigation_collapses_selection(self):
        state = ModifierSelectionState(anchor=(0, 0), lead=(2, 2), is_range_active=True)
        # Plain ArrowRight moves from lead (2, 2) -> (2, 3) and collapses selection
        new_state = self.engine.handle_keyboard_selection(state, 'ArrowRight', shift=False, ctrl=False)
        self.assertEqual(new_state.anchor, (2, 3))
        self.assertEqual(new_state.lead, (2, 3))
        self.assertFalse(new_state.is_range_active)
        self.assertEqual(new_state.bounding_box, CellRange(2, 3, 2, 3))

    def test_shift_arrow_expands_selection_range(self):
        state = ModifierSelectionState(anchor=(5, 5), lead=(5, 5), is_range_active=False)
        # Shift+ArrowDown expands lead to (6, 5) while anchor stays (5, 5)
        s1 = self.engine.handle_keyboard_selection(state, 'ArrowDown', shift=True, ctrl=False)
        self.assertEqual(s1.anchor, (5, 5))
        self.assertEqual(s1.lead, (6, 5))
        self.assertTrue(s1.is_range_active)
        self.assertEqual(s1.bounding_box, CellRange(5, 5, 6, 5))

        # Shift+ArrowRight expands lead to (6, 6)
        s2 = self.engine.handle_keyboard_selection(s1, 'ArrowRight', shift=True, ctrl=False)
        self.assertEqual(s2.anchor, (5, 5))
        self.assertEqual(s2.lead, (6, 6))
        self.assertEqual(s2.bounding_box, CellRange(5, 5, 6, 6))
        self.assertEqual(s2.bounding_box.cell_count(), 4)

    def test_shift_arrow_shrink_and_invert_selection(self):
        state = ModifierSelectionState(anchor=(5, 5), lead=(7, 7), is_range_active=True)
        # Shift+ArrowUp shrinks from (7, 7) to (6, 7)
        s1 = self.engine.handle_keyboard_selection(state, 'ArrowUp', shift=True, ctrl=False)
        self.assertEqual(s1.lead, (6, 7))
        # Shift+ArrowUp further to (4, 7) (inverts vertical range above anchor)
        s2 = self.engine.handle_keyboard_selection(s1, 'ArrowUp', shift=True, ctrl=False)
        s3 = self.engine.handle_keyboard_selection(s2, 'ArrowUp', shift=True, ctrl=False)
        self.assertEqual(s3.lead, (4, 7))
        self.assertEqual(s3.anchor, (5, 5))
        self.assertEqual(s3.bounding_box, CellRange(4, 5, 5, 7))

    def test_ctrl_arrow_boundary_jumps(self):
        # Starting at (5, 2) which has data, and next (5, 3), (5, 4) has data
        # Ctrl+ArrowRight should jump to end of contiguous run at (5, 4)
        jump1 = self.engine.navigate_step((5, 2), 'ArrowRight', ctrl=True)
        self.assertEqual(jump1, (5, 4))

        # From (5, 4), next cells (5, 5), (5, 6) are empty, then (5, 7) has data
        # Ctrl+ArrowRight should jump across empty cells to (5, 7)
        jump2 = self.engine.navigate_step((5, 4), 'ArrowRight', ctrl=True)
        self.assertEqual(jump2, (5, 7))

        # From (5, 7), next (5, 8) has data, rest is empty
        jump3 = self.engine.navigate_step((5, 7), 'ArrowRight', ctrl=True)
        self.assertEqual(jump3, (5, 8))

        # From (5, 8), rest of row is empty -> jumps to grid boundary col 49
        jump4 = self.engine.navigate_step((5, 8), 'ArrowRight', ctrl=True)
        self.assertEqual(jump4, (5, 49))

        # From (5, 49) which is empty, jumping Left seeks first data cell (5, 8)
        jump_left = self.engine.navigate_step((5, 49), 'ArrowLeft', ctrl=True)
        self.assertEqual(jump_left, (5, 8))

    def test_ctrl_shift_arrow_combination(self):
        # Anchor at (5, 2). Ctrl+Shift+ArrowRight jumps lead to (5, 4) expanding range
        state = ModifierSelectionState(anchor=(5, 2), lead=(5, 2))
        s1 = self.engine.handle_keyboard_selection(state, 'ArrowRight', shift=True, ctrl=True)
        self.assertEqual(s1.anchor, (5, 2))
        self.assertEqual(s1.lead, (5, 4))
        self.assertTrue(s1.is_range_active)
        self.assertEqual(s1.bounding_box, CellRange(5, 2, 5, 4))

        # Next Ctrl+Shift+ArrowRight jumps across empty to (5, 7)
        s2 = self.engine.handle_keyboard_selection(s1, 'ArrowRight', shift=True, ctrl=True)
        self.assertEqual(s2.anchor, (5, 2))
        self.assertEqual(s2.lead, (5, 7))
        self.assertEqual(s2.bounding_box, CellRange(5, 2, 5, 7))

    def test_plain_arrow_across_merged_region(self):
        # Stepping into merge [20, 20) to [23, 23)
        step_into = self.engine.navigate_step((20, 19), 'ArrowRight', ctrl=False)
        self.assertEqual(step_into, (20, 20))
        # Stepping from inside merge jumps completely out to col 23
        step_out = self.engine.navigate_step((20, 20), 'ArrowRight', ctrl=False)
        self.assertEqual(step_out, (20, 23))

    def test_reconcile_autoscroll_retains_visible_lead(self):
        # Anchor at (1, 1), lead at (2, 2). Camera at (0, 0), viewport (400, 300)
        state = ModifierSelectionState(anchor=(1, 1), lead=(2, 2), is_range_active=True)
        camera = (0.0, 0.0)
        viewport = (400.0, 300.0)
        new_state, strategy = self.engine.reconcile_autoscroll_selection(state, camera, viewport, zoom=1.0)
        self.assertEqual(strategy, 'lead_retained')
        self.assertEqual(new_state.lead, (2, 2))
        self.assertEqual(new_state.anchor, (1, 1))

    def test_reconcile_autoscroll_expands_lead_with_edge_direction(self):
        # Anchor at (1, 1), lead at (2, 2). Active edge autoscroll moving right/down
        # Camera translates to (400.0, 300.0)
        state = ModifierSelectionState(anchor=(1, 1), lead=(2, 2), is_range_active=True)
        camera = (400.0, 300.0)
        viewport = (400.0, 300.0)  # visible cols ~[4..8], rows ~[9..18]
        new_state, strategy = self.engine.reconcile_autoscroll_selection(
            state, camera, viewport, zoom=1.0, edge_direction=(500.0, 500.0)
        )
        self.assertEqual(strategy, 'lead_edge_expanded')
        # Anchor remains intact at (1, 1)
        self.assertEqual(new_state.anchor, (1, 1))
        # Lead cursor expanded to leading visible edge
        self.assertTrue(new_state.lead[0] >= int(300 / 32))
        self.assertTrue(new_state.lead[1] >= int(400 / 96))
        self.assertTrue(new_state.is_range_active)

    def test_reconcile_autoscroll_clamps_passive_drift(self):
        # Lead at (0, 0). Camera drifted to (500, 500) passively without edge direction
        state = ModifierSelectionState(anchor=(0, 0), lead=(0, 0))
        camera = (500.0, 500.0)
        viewport = (300.0, 200.0)
        new_state, strategy = self.engine.reconcile_autoscroll_selection(state, camera, viewport, zoom=1.0)
        self.assertEqual(strategy, 'lead_clamped_closest')
        self.assertEqual(new_state.anchor, (0, 0))
        self.assertTrue(new_state.lead[0] >= int(500 / 32))
        self.assertTrue(new_state.lead[1] >= int(500 / 96))

    def test_get_selected_cells_enumeration(self):
        state = ModifierSelectionState(anchor=(2, 3), lead=(3, 4), is_range_active=True)
        cells = self.engine.get_selected_cells(state)
        self.assertEqual(len(cells), 4)
        self.assertEqual(set(cells), {(2, 3), (2, 4), (3, 3), (3, 4)})

    def test_input_validation(self):
        with self.assertRaises(ValueError):
            finite_number(1.0, float('nan'))
        with self.assertRaises(ValueError):
            finite_number(1.0, True)
        with self.assertRaises(IndexError):
            self.engine.navigate_step((100, 100), 'ArrowRight')
        with self.assertRaises(ValueError):
            self.engine.handle_keyboard_selection(
                ModifierSelectionState(anchor=(0, 0), lead=(0, 0)),
                'PageDown'
            )


if __name__ == '__main__':
    unittest.main()
