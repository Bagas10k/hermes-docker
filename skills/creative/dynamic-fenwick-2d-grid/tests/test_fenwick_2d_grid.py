import unittest
import sys
import os

# Ensure script path is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts")))

from fenwick_2d_grid import FenwickTree1D, DynamicFenwick2DGrid, Viewport2D


class TestFenwick2DGrid(unittest.TestCase):
    def test_fenwick_1d_prefix_and_update(self):
        sizes = [30.0, 50.0, 20.0, 40.0, 60.0]
        tree = FenwickTree1D(sizes)
        
        self.assertEqual(tree.total_size, 200.0)
        self.assertEqual(tree.get_offset(0), 0.0)
        self.assertEqual(tree.get_offset(1), 30.0)
        self.assertEqual(tree.get_offset(2), 80.0)
        self.assertEqual(tree.get_offset(5), 200.0)
        self.assertEqual(tree.get_range_size(1, 3), 70.0)

        # Dynamic update size of element 1 (50.0 -> 80.0, delta +30)
        delta = tree.update_size(1, 80.0)
        self.assertEqual(delta, 30.0)
        self.assertEqual(tree.total_size, 230.0)
        self.assertEqual(tree.get_offset(2), 110.0)
        self.assertEqual(tree.get_offset(5), 230.0)

    def test_fenwick_binary_lifting_search(self):
        sizes = [10.0, 20.0, 30.0, 40.0]  # offsets: 0, 10, 30, 60; total: 100
        tree = FenwickTree1D(sizes)

        self.assertEqual(tree.find_index_at_offset(0.0), 0)
        self.assertEqual(tree.find_index_at_offset(5.0), 0)
        self.assertEqual(tree.find_index_at_offset(10.0), 1)
        self.assertEqual(tree.find_index_at_offset(25.0), 1)
        self.assertEqual(tree.find_index_at_offset(30.0), 2)
        self.assertEqual(tree.find_index_at_offset(59.9), 2)
        self.assertEqual(tree.find_index_at_offset(60.0), 3)
        self.assertEqual(tree.find_index_at_offset(99.0), 3)
        self.assertEqual(tree.find_index_at_offset(150.0), 3)

    def test_dynamic_2d_grid_resizing(self):
        row_heights = [20.0] * 100  # Total 2000.0
        col_widths = [50.0] * 50   # Total 2500.0
        grid = DynamicFenwick2DGrid(row_heights, col_widths)

        self.assertEqual(grid.total_height, 2000.0)
        self.assertEqual(grid.total_width, 2500.0)

        # Resize row 10 from 20 to 120 (+100)
        grid.resize_row(10, 120.0)
        self.assertEqual(grid.total_height, 2100.0)
        
        # Verify cell geometry
        geom = grid.get_cell_geometry(10, 5)
        self.assertEqual(geom.y, 200.0)  # 10 * 20.0
        self.assertEqual(geom.height, 120.0)
        self.assertEqual(geom.x, 250.0)  # 5 * 50.0
        self.assertEqual(geom.width, 50.0)

        # Cell at row 11 should have y shifted by +100
        geom_next = grid.get_cell_geometry(11, 5)
        self.assertEqual(geom_next.y, 320.0)

    def test_visible_window_with_overscan(self):
        row_heights = [25.0] * 1000  # 1000 rows
        col_widths = [100.0] * 100   # 100 cols
        grid = DynamicFenwick2DGrid(row_heights, col_widths)

        viewport = Viewport2D(
            scroll_top=500.0,
            scroll_left=400.0,
            viewport_height=300.0,
            viewport_width=500.0,
            overscan_rows=2,
            overscan_cols=1,
        )
        window = grid.compute_visible_window(viewport)

        # scroll_top 500 / 25 = row 20
        # scroll_top + 300 = 800 / 25 = row 32
        # with overscan_rows=2: start_row <= 18, end_row >= 35
        self.assertLessEqual(window.start_row, 18)
        self.assertGreaterEqual(window.end_row, 35)

        # scroll_left 400 / 100 = col 4
        # scroll_left + 500 = 900 / 100 = col 9
        # with overscan_cols=1: start_col <= 3, end_col >= 11
        self.assertLessEqual(window.start_col, 3)
        self.assertGreaterEqual(window.end_col, 11)
        self.assertGreater(window.visible_cells, 0)

    def test_edge_cases_and_clamping(self):
        tree = FenwickTree1D([10.0, 10.0], min_dimension=5.0)
        
        # Clamping below min_dimension
        tree.update_size(0, 1.0)
        self.assertEqual(tree.get_size(0), 5.0)

        # Out of bounds exceptions
        with self.assertRaises(IndexError):
            tree.get_size(5)
        with self.assertRaises(IndexError):
            tree.update_size(-1, 20.0)


if __name__ == "__main__":
    unittest.main()
