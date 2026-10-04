"""
Unit tests for Unified 2D Virtual Panes Engine
Validates four-quadrant synchronization, boundary clamping, and zero-CLS ranges.
"""
import unittest
from pane_manager import Unified2DVirtualPaneManager, QuadrantOffsets, VirtualRange

class TestUnified2DVirtualPaneManager(unittest.TestCase):
    def setUp(self):
        # 1000 rows x 500 cols, cell: 30px height, 100px width
        # Viewport: 800w x 600h
        # Pinned: 1 row, 1 col (Corner: 100x30)
        self.mgr = Unified2DVirtualPaneManager(
            total_rows=1000,
            total_cols=500,
            row_height=30.0,
            col_width=100.0,
            viewport_width=800.0,
            viewport_height=600.0,
            pinned_rows=1,
            pinned_cols=1,
            overscan=2
        )

    def test_initial_geometry(self):
        self.assertEqual(self.mgr.frozen_width, 100.0)
        self.assertEqual(self.mgr.frozen_height, 30.0)
        self.assertEqual(self.mgr.body_viewport_w, 700.0)
        self.assertEqual(self.mgr.body_viewport_h, 570.0)
        # 499 body cols * 100 = 49900. max_x = 49900 - 700 = 49200
        self.assertEqual(self.mgr.max_scroll_x, 49200.0)
        # 999 body rows * 30 = 29970. max_y = 29970 - 570 = 29400
        self.assertEqual(self.mgr.max_scroll_y, 29400.0)

    def test_quadrant_coupling_and_transforms(self):
        # Scroll diagonally
        offsets = self.mgr.scroll_to(350.0, 900.0)
        self.assertEqual(offsets.scroll_x, 350.0)
        self.assertEqual(offsets.scroll_y, 900.0)

        transforms = self.mgr.get_quadrant_transforms()
        # NW frozen
        self.assertEqual(transforms["NW"]["translate_x"], 0.0)
        self.assertEqual(transforms["NW"]["translate_y"], 0.0)
        # NE sticky row (scrolls only X)
        self.assertEqual(transforms["NE"]["translate_x"], -350.0)
        self.assertEqual(transforms["NE"]["translate_y"], 0.0)
        # SW sticky col (scrolls only Y)
        self.assertEqual(transforms["SW"]["translate_x"], 0.0)
        self.assertEqual(transforms["SW"]["translate_y"], -900.0)
        # SE body (scrolls X and Y)
        self.assertEqual(transforms["SE"]["translate_x"], -350.0)
        self.assertEqual(transforms["SE"]["translate_y"], -900.0)

    def test_boundary_clamping(self):
        # Negative scroll
        offsets_neg = self.mgr.scroll_to(-50.0, -100.0)
        self.assertEqual(offsets_neg.scroll_x, 0.0)
        self.assertEqual(offsets_neg.scroll_y, 0.0)

        # Overflow scroll
        offsets_over = self.mgr.scroll_to(100000.0, 100000.0)
        self.assertEqual(offsets_over.scroll_x, self.mgr.max_scroll_x)
        self.assertEqual(offsets_over.scroll_y, self.mgr.max_scroll_y)

    def test_visible_range_calculation(self):
        self.mgr.scroll_to(300.0, 600.0)
        # body scroll_y = 600. start_row = 600 // 30 = 20.
        # overscan = 2 -> start_row = 18.
        # end_row = (600 + 570) // 30 = 39 -> + 2 = 41.
        # body scroll_x = 300. start_col = 300 // 100 = 3 -> - 2 = 1.
        # end_col = (300 + 700) // 100 = 10 -> + 2 = 12.
        vr = self.mgr.compute_visible_range()
        self.assertEqual(vr.start_row, 18)
        self.assertEqual(vr.end_row, 41)
        self.assertEqual(vr.start_col, 1)
        self.assertEqual(vr.end_col, 12)

    def test_render_manifest(self):
        manifest = self.mgr.render_manifest()
        self.assertIn("geometry", manifest)
        self.assertIn("quadrant_cells", manifest)
        self.assertEqual(manifest["quadrant_cells"]["NW"], 1)
        # Check that total cells rendered in SE is bounded and tiny relative to total grid (500k cells)
        se_cells = manifest["quadrant_cells"]["SE"]
        self.assertLess(se_cells, 500)  # ~24 rows * 12 cols = 288 cells vs 500,000 cells

if __name__ == "__main__":
    unittest.main()
