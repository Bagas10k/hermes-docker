import unittest
import math
from bidirectional_2d_grid_engine import FenwickTree1D, Bidirectional2DVirtualGrid

class TestBidirectional2DVirtualGrid(unittest.TestCase):

    def test_01_fenwick_tree_primitives(self):
        """Test point updates, range queries, and binary lifting search in 1D tree."""
        size = 1000
        val = 40.0
        ft = FenwickTree1D(size, val)
        self.assertAlmostEqual(ft.prefix_sum(size), 40000.0)
        self.assertAlmostEqual(ft.range_sum(10, 19), 400.0)

        # Update index 15: +10.0
        ft.update(15, 10.0)
        self.assertAlmostEqual(ft.get_value(15), 50.0)
        self.assertAlmostEqual(ft.range_sum(10, 19), 410.0)

        # Binary lifting search
        idx = ft.find_index_for_offset(80.0) # indices 0, 1 = 80.0 -> returns index 2 or 1
        self.assertTrue(idx in (1, 2))
        self.assertAlmostEqual(ft.prefix_sum(0), 0.0)

    def test_02_massive_grid_bounded_cell_pool(self):
        """
        Verify that a massive grid (100,000 rows x 500 columns = 50,000,000 cells)
        maintains strict O(1) active cell pool allocation under viewport budget.
        """
        rows = 100_000
        cols = 500
        vp_w = 1200.0
        vp_h = 800.0
        row_h = 32.0
        col_w = 100.0

        grid = Bidirectional2DVirtualGrid(
            total_rows=rows,
            total_cols=cols,
            viewport_width=vp_w,
            viewport_height=vp_h,
            default_row_height=row_h,
            default_col_width=col_w,
            overscan_rows=2,
            overscan_cols=2
        )

        # Total dimensions
        expected_total_h = rows * row_h
        expected_total_w = cols * col_w
        self.assertAlmostEqual(grid.get_total_height(), expected_total_h)
        self.assertAlmostEqual(grid.get_total_width(), expected_total_w)

        # Compute window at scroll (x=5000, y=100000)
        win = grid.compute_2d_window(scroll_x=5000.0, scroll_y=100_000.0)

        # Visible visible capacity:
        # rows: ceil(800 / 32) = 25 + 1 = ~26 rows + 2*2 overscan = ~30 rows
        # cols: ceil(1200 / 100) = 12 + 1 = ~13 cols + 2*2 overscan = ~17 cols
        # Total cells rendered <= 35 * 20 = 700 cells << 50,000,000 cells!
        rendered_rows = win["rows"]["rendered_count"]
        rendered_cols = win["cols"]["rendered_count"]
        active_cells = win["active_cell_pool_count"]

        self.assertLessEqual(rendered_rows, 35)
        self.assertLessEqual(rendered_cols, 20)
        self.assertLessEqual(active_cells, 700)
        self.assertEqual(active_cells, rendered_rows * rendered_cols)

    def test_03_spacers_and_dimension_conservation(self):
        """Verify height and width conservation invariant across rendered slices and spacers."""
        grid = Bidirectional2DVirtualGrid(
            total_rows=5000,
            total_cols=200,
            viewport_width=1000.0,
            viewport_height=600.0,
            default_row_height=30.0,
            default_col_width=80.0,
            overscan_rows=3,
            overscan_cols=2
        )

        win = grid.compute_2d_window(scroll_x=2400.0, scroll_y=45000.0)

        # Height conservation: top_spacer + rendered_height + bottom_spacer == total_height
        r = win["rows"]
        h_sum = r["top_spacer"] + r["rendered_height"] + r["bottom_spacer"]
        self.assertAlmostEqual(h_sum, r["total_height"], places=4)

        # Width conservation: left_spacer + rendered_width + right_spacer == total_width
        c = win["cols"]
        w_sum = c["left_spacer"] + c["rendered_width"] + c["right_spacer"]
        self.assertAlmostEqual(w_sum, c["total_width"], places=4)

    def test_04_bidirectional_dynamic_resize_and_zero_cls_anchoring(self):
        """
        Verify asynchronous 2D resize mutations on rows and columns
        preserve exact pixel position of the active anchor cell (CLS = 0).
        """
        grid = Bidirectional2DVirtualGrid(
            total_rows=10_000,
            total_cols=1_000,
            viewport_width=1000.0,
            viewport_height=700.0,
            default_row_height=30.0,
            default_col_width=100.0
        )

        cur_x = 500.0
        cur_y = 1500.0
        anchor_row = 100
        anchor_col = 20

        # Anchor row starts at offset = 100 * 30.0 = 3000.0
        # Relative pos to viewport = 3000.0 - 1500.0 = 1500.0
        # Anchor col starts at offset = 20 * 100.0 = 2000.0
        # Relative pos to viewport = 2000.0 - 500.0 = 1500.0

        # Asynchronous batch mutation above and below the anchor
        row_updates = [
            (10, 60.0),   # +30.0 (above anchor)
            (50, 45.0),   # +15.0 (above anchor)
            (150, 80.0)   # +50.0 (below anchor, should NOT affect scroll_y)
        ]
        col_updates = [
            (5, 140.0),   # +40.0 (above anchor)
            (12, 120.0),  # +20.0 (above anchor)
            (40, 200.0)   # +100.0 (below anchor, should NOT affect scroll_x)
        ]

        res = grid.handle_2d_resize_batch(
            row_updates=row_updates,
            col_updates=col_updates,
            current_scroll_x=cur_x,
            current_scroll_y=cur_y,
            anchor_row=anchor_row,
            anchor_col=anchor_col
        )

        # Expected compensations:
        # row: +30 + 15 = +45.0
        # col: +40 + 20 = +60.0
        self.assertAlmostEqual(res["row_anchor_compensation"], 45.0)
        self.assertAlmostEqual(res["col_anchor_compensation"], 60.0)
        self.assertAlmostEqual(res["adjusted_scroll_y"], cur_y + 45.0)
        self.assertAlmostEqual(res["adjusted_scroll_x"], cur_x + 60.0)

        # Verify relative visual position of anchor cell is identical (CLS = 0)
        new_anchor_y = grid.row_tree.prefix_sum(anchor_row)
        new_anchor_x = grid.col_tree.prefix_sum(anchor_col)

        rel_y_after = new_anchor_y - res["adjusted_scroll_y"]
        rel_x_after = new_anchor_x - res["adjusted_scroll_x"]

        # Initial relative positions:
        # initial anchor_y = 100 * 30 = 3000.0 -> rel = 3000 - 1500 = 1500.0
        # initial anchor_x = 20 * 100 = 2000.0 -> rel = 2000 - 500 = 1500.0
        self.assertAlmostEqual(rel_y_after, 1500.0, places=5)
        self.assertAlmostEqual(rel_x_after, 1500.0, places=5)

    def test_05_extreme_scroll_edge_cases(self):
        """Test boundary conditions: negative scroll, beyond maximum scroll, and empty ranges."""
        grid = Bidirectional2DVirtualGrid(
            total_rows=100,
            total_cols=20,
            viewport_width=500.0,
            viewport_height=300.0,
            default_row_height=25.0,
            default_col_width=80.0
        )

        # Negative scroll
        win_neg = grid.compute_2d_window(-50.0, -100.0)
        self.assertEqual(win_neg["rows"]["render_start"], 0)
        self.assertEqual(win_neg["cols"]["render_start"], 0)

        # Beyond maximum scroll
        win_max = grid.compute_2d_window(999999.0, 999999.0)
        self.assertEqual(win_max["rows"]["render_end"], 99)
        self.assertEqual(win_max["cols"]["render_end"], 19)


if __name__ == "__main__":
    unittest.main()
