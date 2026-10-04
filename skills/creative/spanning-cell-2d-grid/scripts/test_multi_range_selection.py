import unittest
from multi_range_selection import (
    MultiRangeSelectionEngine,
    MultiRangeSelectionState,
    SelectionBox,
    finite_number
)


class MultiRangeSelectionTests(unittest.TestCase):
    def setUp(self):
        self.engine = MultiRangeSelectionEngine(row_px=32, col_px=96, rows=50, cols=50)
        # Merged box at [10, 10) to [13, 13) (3x3 merge)
        self.engine.add_merge('hero-merge', 10, 10, 13, 13)

    def test_selection_box_geometry(self):
        b1 = SelectionBox(2, 3, 5, 8, 'b1')
        self.assertEqual(b1.cell_count(), 4 * 6)
        self.assertTrue(b1.contains(3, 4))
        self.assertFalse(b1.contains(1, 4))
        self.assertEqual(b1.to_tuple(), (2, 3, 5, 8))

        # Intersection test
        b2 = SelectionBox(4, 7, 6, 10, 'b2')
        b3 = SelectionBox(6, 9, 8, 12, 'b3')
        b_disjoint = SelectionBox(10, 20, 12, 22, 'disjoint')
        self.assertTrue(b1.intersects(b2))
        self.assertTrue(b2.intersects(b3))
        self.assertFalse(b1.intersects(b_disjoint))

        # Rejection of invalid coordinates
        with self.assertRaises(ValueError):
            SelectionBox(5, 2, 3, 8)  # r0 > r1
        with self.assertRaises(ValueError):
            SelectionBox(1, 5, 3, 2)  # c0 > c1

    def test_plain_click_resets_to_single_cell(self):
        # Initial multi-range state
        init_state = MultiRangeSelectionState(
            ranges=[SelectionBox(0, 0, 1, 1), SelectionBox(5, 5, 6, 6)],
            active_range_idx=1
        )
        new_state = self.engine.handle_pointer_click(init_state, (3, 4), ctrl_or_cmd=False, shift=False)
        self.assertEqual(len(new_state.ranges), 1)
        self.assertEqual(new_state.ranges[0].to_tuple(), (3, 4, 3, 4))
        self.assertEqual(new_state.lead_cursor, (3, 4))
        self.assertEqual(new_state.anchor_cursor, (3, 4))

    def test_ctrl_click_adds_disjoint_ranges(self):
        s0 = MultiRangeSelectionState()
        # Click (2, 2)
        s1 = self.engine.handle_pointer_click(s0, (2, 2), ctrl_or_cmd=False)
        self.assertEqual(len(s1.ranges), 1)

        # Ctrl+Click (5, 8)
        s2 = self.engine.handle_pointer_click(s1, (5, 8), ctrl_or_cmd=True)
        self.assertEqual(len(s2.ranges), 2)
        self.assertEqual(s2.ranges[0].to_tuple(), (2, 2, 2, 2))
        self.assertEqual(s2.ranges[1].to_tuple(), (5, 8, 5, 8))

        # Ctrl+Click (15, 20)
        s3 = self.engine.handle_pointer_click(s2, (15, 20), ctrl_or_cmd=True)
        self.assertEqual(len(s3.ranges), 3)
        self.assertEqual(s3.ranges[2].to_tuple(), (15, 20, 15, 20))

    def test_ctrl_click_toggle_off(self):
        s0 = MultiRangeSelectionState()
        s1 = self.engine.handle_pointer_click(s0, (2, 2), ctrl_or_cmd=False)
        s2 = self.engine.handle_pointer_click(s1, (5, 8), ctrl_or_cmd=True)
        self.assertEqual(len(s2.ranges), 2)

        # Ctrl+Click again on (5, 8) toggles it off
        s3 = self.engine.handle_pointer_click(s2, (5, 8), ctrl_or_cmd=True)
        self.assertEqual(len(s3.ranges), 1)
        self.assertEqual(s3.ranges[0].to_tuple(), (2, 2, 2, 2))

    def test_shift_click_range_extension(self):
        s0 = MultiRangeSelectionState(anchor_cursor=(2, 2), lead_cursor=(2, 2))
        # Shift+Click (4, 6) extends from anchor (2, 2) to (4, 6)
        s1 = self.engine.handle_pointer_click(s0, (4, 6), ctrl_or_cmd=False, shift=True)
        self.assertEqual(len(s1.ranges), 1)
        self.assertEqual(s1.ranges[0].to_tuple(), (2, 2, 4, 6))
        self.assertEqual(s1.ranges[0].cell_count(), 3 * 5)
        self.assertEqual(s1.lead_cursor, (4, 6))
        self.assertEqual(s1.anchor_cursor, (2, 2))

    def test_ctrl_shift_click_adds_extended_range(self):
        s0 = MultiRangeSelectionState(
            ranges=[SelectionBox(0, 0, 1, 1)],
            anchor_cursor=(5, 5),
            lead_cursor=(5, 5)
        )
        # Ctrl+Shift+Click (7, 8) adds a new range [5, 5] to [7, 8] without clearing [0, 0, 1, 1]
        s1 = self.engine.handle_pointer_click(s0, (7, 8), ctrl_or_cmd=True, shift=True)
        self.assertEqual(len(s1.ranges), 2)
        self.assertEqual(s1.ranges[0].to_tuple(), (0, 0, 1, 1))
        self.assertEqual(s1.ranges[1].to_tuple(), (5, 5, 7, 8))

    def test_merge_cell_expansion_invariance(self):
        # Click on cell (11, 11) inside merged region [10, 10) to [13, 13)
        # Inclusive bounds must be [10, 10, 12, 12]
        s0 = MultiRangeSelectionState()
        s1 = self.engine.handle_pointer_click(s0, (11, 11), ctrl_or_cmd=False)
        self.assertEqual(len(s1.ranges), 1)
        self.assertEqual(s1.ranges[0].to_tuple(), (10, 10, 12, 12))
        self.assertEqual(s1.ranges[0].cell_count(), 9)

    def test_deduplicate_ranges(self):
        boxes = [
            SelectionBox(2, 2, 6, 6, 'b1'),
            SelectionBox(3, 3, 4, 4, 'subsumed'),  # inside b1
            SelectionBox(2, 2, 6, 6, 'duplicate'), # identical
            SelectionBox(10, 10, 12, 12, 'disjoint')
        ]
        deduped = self.engine.deduplicate_ranges(boxes)
        self.assertEqual(len(deduped), 2)
        self.assertEqual(deduped[0].to_tuple(), (2, 2, 6, 6))
        self.assertEqual(deduped[1].to_tuple(), (10, 10, 12, 12))

    def test_query_visible_selection_boxes(self):
        # Ranges scattered across the 50x50 grid
        state = MultiRangeSelectionState(ranges=[
            SelectionBox(1, 1, 2, 2, 'box-near-origin'),
            SelectionBox(15, 15, 18, 18, 'box-middle'),
            SelectionBox(40, 40, 42, 42, 'box-far')
        ])
        # Camera at (0, 0), viewport (300, 200). Grid px: row 32, col 96
        # Visible rows: 0 to ceil(200/32)=7, cols: 0 to ceil(300/96)=4
        vis = self.engine.query_visible_selection_boxes(state, camera=(0, 0), viewport=(300, 200), zoom=1.0)
        self.assertEqual(len(vis), 1)
        self.assertEqual(vis[0].box_id, 'box-near-origin')

        # Translate camera to (1400, 500) -> viewport covers middle region
        vis_mid = self.engine.query_visible_selection_boxes(state, camera=(1400, 480), viewport=(400, 300), zoom=1.0)
        box_ids = [b.box_id for b in vis_mid]
        self.assertIn('box-middle', box_ids)
        self.assertNotIn('box-near-origin', box_ids)

    def test_get_selected_unique_cells(self):
        # Overlapping ranges: [0, 0, 1, 1] (4 cells) and [1, 1, 2, 2] (4 cells)
        # Cell (1, 1) is shared
        state = MultiRangeSelectionState(ranges=[
            SelectionBox(0, 0, 1, 1),
            SelectionBox(1, 1, 2, 2)
        ])
        cells = self.engine.get_selected_unique_cells(state)
        # Total unique cells: (0,0),(0,1),(1,0),(1,1),(1,2),(2,1),(2,2) -> 7 cells
        self.assertEqual(len(cells), 7)
        self.assertIn((1, 1), cells)
        self.assertIn((0, 0), cells)
        self.assertIn((2, 2), cells)

    def test_tsv_serialization(self):
        state = MultiRangeSelectionState(ranges=[
            SelectionBox(0, 0, 1, 1),
            SelectionBox(5, 5, 5, 6)
        ])
        tsv = self.engine.serialize_ranges_tsv(state)
        lines = tsv.split('\n\n')
        self.assertEqual(len(lines), 2)  # Two disjoint blocks
        self.assertIn('0,0\t0,1', lines[0])
        self.assertIn('5,5\t5,6', lines[1])

    def test_input_validation(self):
        with self.assertRaises(ValueError):
            finite_number(float('nan'))
        with self.assertRaises(ValueError):
            finite_number(True)
        with self.assertRaises(IndexError):
            self.engine.handle_pointer_click(MultiRangeSelectionState(), (999, 999))


if __name__ == '__main__':
    unittest.main()
