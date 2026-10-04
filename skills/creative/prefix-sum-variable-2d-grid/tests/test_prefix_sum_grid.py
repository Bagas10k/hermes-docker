import unittest
from scripts.prefix_sum_grid import (
    VariableDimensionIndexer,
    Variable2DVirtualGrid,
    Virtual2DViewport,
)


class TestPrefixSumVariable2DGrid(unittest.TestCase):
    def test_indexer_prefix_sum_properties(self):
        sizes = [30.0, 50.0, 20.0, 100.0, 40.0]
        indexer = VariableDimensionIndexer(sizes)

        self.assertEqual(indexer.total_size, 240.0)
        self.assertEqual(indexer.get_offset(0), 0.0)
        self.assertEqual(indexer.get_offset(1), 30.0)
        self.assertEqual(indexer.get_offset(2), 80.0)
        self.assertEqual(indexer.get_offset(3), 100.0)
        self.assertEqual(indexer.get_offset(4), 200.0)
        self.assertEqual(indexer.get_offset(5), 240.0)

        # Range size O(1)
        self.assertEqual(indexer.get_range_size(1, 4), 170.0)  # 50 + 20 + 100
        self.assertEqual(indexer.get_range_size(2, 2), 0.0)
        self.assertEqual(indexer.get_range_size(4, 2), 0.0)

    def test_indexer_binary_search_find_index(self):
        sizes = [40.0, 60.0, 50.0, 100.0]  # offsets: [0, 40, 100, 150, 250]
        indexer = VariableDimensionIndexer(sizes)

        self.assertEqual(indexer.find_index_at_offset(0.0), 0)
        self.assertEqual(indexer.find_index_at_offset(25.0), 0)
        self.assertEqual(indexer.find_index_at_offset(39.9), 0)
        self.assertEqual(indexer.find_index_at_offset(40.0), 1)
        self.assertEqual(indexer.find_index_at_offset(99.0), 1)
        self.assertEqual(indexer.find_index_at_offset(100.0), 2)
        self.assertEqual(indexer.find_index_at_offset(149.9), 2)
        self.assertEqual(indexer.find_index_at_offset(150.0), 3)
        self.assertEqual(indexer.find_index_at_offset(249.0), 3)
        self.assertEqual(indexer.find_index_at_offset(300.0), 3)  # clamped

    def test_virtual_2d_window_calculation(self):
        # 1,000 variable rows and 200 variable columns
        row_heights = [30.0 + (i % 5) * 10.0 for i in range(1000)]  # 30, 40, 50, 60, 70
        col_widths = [80.0 + (j % 4) * 20.0 for j in range(200)]    # 80, 100, 120, 140

        grid = Variable2DVirtualGrid(row_heights, col_widths)

        viewport = Virtual2DViewport(
            scroll_top=2500.0,
            scroll_left=1200.0,
            viewport_height=600.0,
            viewport_width=800.0,
            overscan_rows=3,
            overscan_cols=2,
        )

        window = grid.compute_visible_window(viewport)

        self.assertGreater(window.start_row, 0)
        self.assertLess(window.start_row, window.end_row)
        self.assertGreater(window.start_col, 0)
        self.assertLess(window.start_col, window.end_col)

        # Verify that start offsets strictly match indexer cumulative sums
        expected_row_offset = grid.row_indexer.get_offset(window.start_row)
        expected_col_offset = grid.col_indexer.get_offset(window.start_col)
        self.assertEqual(window.row_offset, expected_row_offset)
        self.assertEqual(window.col_offset, expected_col_offset)

        # Verify cell count invariant
        expected_cells = (window.end_row - window.start_row) * (window.end_col - window.start_col)
        self.assertEqual(window.visible_cell_count, expected_cells)

    def test_cell_geometry_retrieval(self):
        row_heights = [25.0, 45.0, 65.0]
        col_widths = [100.0, 150.0, 200.0]
        grid = Variable2DVirtualGrid(row_heights, col_widths)

        geom = grid.get_cell_geometry(1, 2)
        self.assertEqual(geom["top"], 25.0)
        self.assertEqual(geom["height"], 45.0)
        self.assertEqual(geom["bottom"], 70.0)
        self.assertEqual(geom["left"], 250.0)  # 100 + 150
        self.assertEqual(geom["width"], 200.0)
        self.assertEqual(geom["right"], 450.0)

    def test_out_of_bounds_handling(self):
        row_heights = [30.0, 30.0]
        col_widths = [50.0, 50.0]
        grid = Variable2DVirtualGrid(row_heights, col_widths)

        with self.assertRaises(IndexError):
            grid.get_cell_geometry(5, 0)

        with self.assertRaises(IndexError):
            grid.get_cell_geometry(0, -1)


if __name__ == "__main__":
    unittest.main()
