"""Unit tests for Tabular Clipboard Paste Arbitration, Merged Cell Overwrite Arbitration & Relative Formula Translation (UIUX-040 & UIUX-041)."""
import unittest

from tabular_paste_arbitrator import (
    ClipboardTable,
    CellMutation,
    PastePlan,
    TabularPasteArbitrator,
    SelectionBox,
    MultiRangeSelectionState,
    col_to_name,
    name_to_col,
    translate_formula_references
)


class TestTabularPasteArbitrator(unittest.TestCase):
    def setUp(self):
        self.arbitrator = TabularPasteArbitrator(grid_rows=50, grid_cols=50)

    def test_parse_clipboard_tsv_and_crlf(self):
        tsv_raw = "Alpha\tBeta\tGamma\r\n100\t200\t300\r\n"
        table = self.arbitrator.parse_clipboard_text(tsv_raw)
        self.assertEqual(table.rows, 2)
        self.assertEqual(table.cols, 3)
        self.assertEqual(table.get(0, 0), "Alpha")
        self.assertEqual(table.get(0, 2), "Gamma")
        self.assertEqual(table.get(1, 1), "200")
        self.assertFalse(table.is_empty())
        self.assertFalse(table.is_scalar())

    def test_parse_clipboard_single_scalar(self):
        raw = "42\n"
        table = self.arbitrator.parse_clipboard_text(raw)
        self.assertEqual(table.rows, 1)
        self.assertEqual(table.cols, 1)
        self.assertEqual(table.get(0, 0), "42")
        self.assertTrue(table.is_scalar())

    def test_parse_clipboard_ragged_normalization(self):
        # Line 1 has 3 cols, Line 2 has 2 cols -> normalized to 3 cols with empty string fill
        raw = "A\tB\tC\nD\tE"
        table = self.arbitrator.parse_clipboard_text(raw)
        self.assertEqual(table.rows, 2)
        self.assertEqual(table.cols, 3)
        self.assertEqual(table.get(1, 2), "")

    def test_single_anchor_expand(self):
        # 2x2 clipboard into single cell anchor (5, 5)
        raw = "V1\tV2\nV3\tV4"
        plan = self.arbitrator.plan_paste(raw, SelectionBox(5, 5, 5, 5))
        self.assertEqual(plan.mode, 'single_anchor_expand')
        self.assertEqual(plan.total_cells, 4)
        self.assertEqual(plan.affected_rows, 2)
        self.assertEqual(plan.affected_cols, 2)
        self.assertEqual(len(plan.target_boxes), 1)
        self.assertEqual(plan.target_boxes[0].to_tuple(), (5, 5, 6, 6))

        # Apply plan
        store = self.arbitrator.apply_plan(plan)
        self.assertEqual(store[(5, 5)], "V1")
        self.assertEqual(store[(5, 6)], "V2")
        self.assertEqual(store[(6, 5)], "V3")
        self.assertEqual(store[(6, 6)], "V4")

        # Rollback plan
        store_rolled = self.arbitrator.rollback_plan(plan)
        self.assertNotIn((5, 5), store_rolled)
        self.assertNotIn((6, 6), store_rolled)

    def test_exact_match_fill(self):
        # 2x3 clipboard into exact 2x3 selection [10, 10, 11, 12]
        raw = "A\tB\tC\nD\tE\tF"
        box = SelectionBox(10, 10, 11, 12)
        plan = self.arbitrator.plan_paste(raw, box)
        self.assertEqual(plan.mode, 'exact_match_fill')
        self.assertEqual(plan.total_cells, 6)
        self.assertEqual(plan.target_boxes[0].to_tuple(), (10, 10, 11, 12))

    def test_modulo_repeat_fill_single_range(self):
        # 1x2 clipboard into 4x4 target range -> repeated tiling
        raw = "Left\tRight"
        box = SelectionBox(0, 0, 3, 3)  # 4 rows x 4 cols = 16 cells
        plan = self.arbitrator.plan_paste(raw, box)
        self.assertEqual(plan.mode, 'modulo_repeat_fill')
        self.assertEqual(plan.total_cells, 16)

        self.arbitrator.apply_plan(plan)
        # Check alternating left/right in columns
        for r in range(4):
            self.assertEqual(self.arbitrator.cell_store[(r, 0)], "Left")
            self.assertEqual(self.arbitrator.cell_store[(r, 1)], "Right")
            self.assertEqual(self.arbitrator.cell_store[(r, 2)], "Left")
            self.assertEqual(self.arbitrator.cell_store[(r, 3)], "Right")

    def test_overflow_expand_larger_than_target(self):
        # 3x3 clipboard into 1x2 target -> expands to full 3x3
        raw = "1\t2\t3\n4\t5\t6\n7\t8\t9"
        box = SelectionBox(2, 2, 2, 3)  # 1 row x 2 cols
        plan = self.arbitrator.plan_paste(raw, box)
        self.assertEqual(plan.mode, 'overflow_expand')
        self.assertEqual(plan.total_cells, 9)
        self.assertEqual(plan.target_boxes[0].to_tuple(), (2, 2, 4, 4))

    def test_asymmetric_multi_target_scalar_broadcast(self):
        # Scalar "ZERO" into 3 disjoint boxes
        b1 = SelectionBox(1, 1, 1, 1)  # 1 cell
        b2 = SelectionBox(5, 5, 6, 7)  # 2x3 = 6 cells
        b3 = SelectionBox(10, 12, 11, 12)  # 2x1 = 2 cells
        # Total = 9 cells

        plan = self.arbitrator.plan_paste("ZERO", [b1, b2, b3])
        self.assertEqual(plan.mode, 'asymmetric_multi_target_broadcast')
        self.assertEqual(plan.total_cells, 9)

        self.arbitrator.apply_plan(plan)
        self.assertEqual(self.arbitrator.cell_store[(1, 1)], "ZERO")
        self.assertEqual(self.arbitrator.cell_store[(5, 5)], "ZERO")
        self.assertEqual(self.arbitrator.cell_store[(6, 7)], "ZERO")
        self.assertEqual(self.arbitrator.cell_store[(10, 12)], "ZERO")

    def test_asymmetric_multi_target_tabular_tiling(self):
        # 2x2 matrix into two disjoint asymmetric boxes
        raw = "10\t20\n30\t40"
        b1 = SelectionBox(0, 0, 1, 1)  # 2x2 exact match
        b2 = SelectionBox(10, 10, 13, 11)  # 4x2 tiled match
        plan = self.arbitrator.plan_paste(raw, [b1, b2])
        self.assertEqual(plan.mode, 'asymmetric_multi_target_broadcast')
        self.assertEqual(plan.total_cells, 4 + 8)

        self.arbitrator.apply_plan(plan)
        # Check b1
        self.assertEqual(self.arbitrator.cell_store[(0, 0)], "10")
        self.assertEqual(self.arbitrator.cell_store[(1, 1)], "40")
        # Check b2 tiling
        self.assertEqual(self.arbitrator.cell_store[(10, 10)], "10")
        self.assertEqual(self.arbitrator.cell_store[(11, 10)], "30")
        self.assertEqual(self.arbitrator.cell_store[(12, 10)], "10")  # row wrapped (12-10)%2 == 0
        self.assertEqual(self.arbitrator.cell_store[(13, 11)], "40")  # (13-10)%2==1, (11-10)%2==1 -> (1, 1) -> 40

    def test_grid_boundary_clip_guard(self):
        # 3x3 paste near bottom-right edge of grid (49, 49) in 50x50 grid
        raw = "A\tB\tC\nD\tE\tF\nG\tH\tI"
        box = SelectionBox(49, 49, 49, 49)
        plan = self.arbitrator.plan_paste(raw, box)
        self.assertTrue(plan.clipped_overflow)
        self.assertEqual(plan.total_cells, 1)  # only (49, 49) fits within 50x50 bounds
        self.assertEqual(plan.mutations[0].row, 49)
        self.assertEqual(plan.mutations[0].col, 49)
        self.assertEqual(plan.mutations[0].new_value, "A")

    def test_empty_clipboard_noop(self):
        plan = self.arbitrator.plan_paste("", SelectionBox(0, 0, 1, 1))
        self.assertEqual(plan.mode, 'empty_noop')
        self.assertEqual(plan.total_cells, 0)
        self.assertEqual(len(plan.mutations), 0)

    def test_invalid_clipboard_types(self):
        with self.assertRaises(TypeError):
            self.arbitrator.parse_clipboard_text(12345)  # type: ignore

    # UIUX-041 Tests: Relative Formula Translation & Merged Cell Overwrite Arbitration
    def test_a1_column_conversions(self):
        self.assertEqual(col_to_name(0), "A")
        self.assertEqual(col_to_name(25), "Z")
        self.assertEqual(col_to_name(26), "AA")
        self.assertEqual(col_to_name(27), "AB")
        self.assertEqual(col_to_name(51), "AZ")
        self.assertEqual(col_to_name(52), "BA")

        self.assertEqual(name_to_col("A"), 0)
        self.assertEqual(name_to_col("Z"), 25)
        self.assertEqual(name_to_col("AA"), 26)
        self.assertEqual(name_to_col("AZ"), 51)
        self.assertEqual(name_to_col("BA"), 52)

    def test_formula_relative_translation(self):
        # Shift =SUM(A1:B2) by row+3, col+2 -> =SUM(C4:D5)
        formula = "=SUM(A1:B2)"
        translated = translate_formula_references(formula, delta_row=3, delta_col=2)
        self.assertEqual(translated, "=SUM(C4:D5)")

    def test_formula_absolute_preservation(self):
        # Shift formula with absolute coordinates $A$1 and mixed A$2, $B3
        formula = "=AVERAGE($A$1, C$5, $D10) + 100"
        # delta_row=5, delta_col=3
        # $A$1 -> unchanged $A$1
        # C$5 -> row abs (5), col relative (C + 3 = F) -> F$5
        # $D10 -> col abs ($D), row relative (10 + 5 = 15) -> $D15
        translated = translate_formula_references(formula, delta_row=5, delta_col=3)
        self.assertEqual(translated, "=AVERAGE($A$1, F$5, $D15) + 100")

    def test_formula_out_of_bounds_ref_error(self):
        # Shifting A1 backwards by (-1, -1) results in #REF!
        formula = "=A1 + 10"
        translated = translate_formula_references(formula, delta_row=-1, delta_col=-1)
        self.assertEqual(translated, "=#REF! + 10")

    def test_paste_formula_relative_tiling(self):
        # Paste formula =A1+B1 across a 1x2 selection at row 10, col 5
        raw = "=A1+B1"
        box = SelectionBox(10, 5, 11, 5)  # 2 rows x 1 col at col 5 (F)
        plan = self.arbitrator.plan_paste(raw, box)
        self.assertEqual(plan.total_cells, 2)

        # Cell (10, 5): delta_r = 10, delta_c = 5 -> A1+B1 shifted by (+10, +5) -> F11+G11
        # Cell (11, 5): delta_r = 11, delta_c = 5 -> A1+B1 shifted by (+11, +5) -> F12+G12
        self.arbitrator.apply_plan(plan)
        self.assertEqual(self.arbitrator.cell_store[(10, 5)], "=F11+G11")
        self.assertEqual(self.arbitrator.cell_store[(11, 5)], "=F12+G12")

    def test_merged_cell_partial_overwrite_veto(self):
        # Grid with 3x3 merge at [10, 10) to [13, 13)
        self.arbitrator.add_merge('hero-merge', 10, 10, 13, 13)

        # Single anchor paste at (11, 11) - non-top-left of merge
        raw = "Data1\tData2"
        plan = self.arbitrator.plan_paste(raw, SelectionBox(11, 11, 11, 11), merge_policy='veto_partial_overwrite')
        self.assertTrue(plan.is_vetoed)
        self.assertEqual(plan.mode, 'rejected_conflict')
        self.assertEqual(len(plan.merged_conflicts), 2)
        self.assertFalse(plan.merged_conflicts[0].is_top_left)

        # Applying a vetoed plan raises an error
        with self.assertRaises(ValueError):
            self.arbitrator.apply_plan(plan)

    def test_merged_cell_auto_unmerge_policy(self):
        # Grid with merge at [5, 5) to [7, 7) (2x2 merge)
        self.arbitrator.add_merge('box-merge', 5, 5, 7, 7)
        self.assertIn('box-merge', self.arbitrator.merges)

        # Paste 2x2 table covering [5, 5) to [7, 7) with auto_unmerge policy
        raw = "M1\tM2\nM3\tM4"
        plan = self.arbitrator.plan_paste(raw, SelectionBox(5, 5, 5, 5), merge_policy='auto_unmerge')
        self.assertFalse(plan.is_vetoed)
        self.assertIn('box-merge', plan.unmerged_regions)

        self.arbitrator.apply_plan(plan)
        # Merge is removed
        self.assertNotIn('box-merge', self.arbitrator.merges)
        self.assertNotIn((5, 5), self.arbitrator.cell_merge_owners)
        # Data written
        self.assertEqual(self.arbitrator.cell_store[(5, 5)], "M1")
        self.assertEqual(self.arbitrator.cell_store[(6, 6)], "M4")

    def test_merged_cell_top_left_only_policy(self):
        # Grid with merge at [20, 20) to [22, 22) (2x2 merge)
        self.arbitrator.add_merge('tl-merge', 20, 20, 22, 22)

        # Paste 2x2 table over [20, 20] to [21, 21] with top_left_only policy
        raw = "TopLeft\tTopRight\nBotLeft\tBotRight"
        plan = self.arbitrator.plan_paste(raw, SelectionBox(20, 20, 20, 20), merge_policy='top_left_only')
        self.assertFalse(plan.is_vetoed)

        self.arbitrator.apply_plan(plan)
        # Only top-left (20, 20) is mutated, non-top-left (20, 21), (21, 20), (21, 21) are skipped
        self.assertEqual(self.arbitrator.cell_store.get((20, 20)), "TopLeft")
        self.assertNotIn((20, 21), self.arbitrator.cell_store)
        self.assertNotIn((21, 21), self.arbitrator.cell_store)


if __name__ == '__main__':
    unittest.main()
