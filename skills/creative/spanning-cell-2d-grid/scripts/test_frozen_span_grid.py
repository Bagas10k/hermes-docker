import unittest
from frozen_span_grid import FrozenSpanGridManager, QuadrantWindow, PaneSpanItem

class TestFrozenSpanGrid(unittest.TestCase):
    def setUp(self):
        # 100 rows x 50 cols grid, 30px row height, 100px col width
        # Viewport: 800w x 600h, 2 frozen rows, 2 frozen cols, overscan 1
        self.mgr = FrozenSpanGridManager(
            total_rows=100,
            total_cols=50,
            row_height=30.0,
            col_width=100.0,
            viewport_width=800.0,
            viewport_height=600.0,
            frozen_rows=2,
            frozen_cols=2,
            overscan=1
        )

    def tearDown(self):
        self.mgr.close()

    def test_initial_quadrant_geometry(self):
        self.assertEqual(self.mgr.frozen_width, 200.0) # 2 * 100
        self.assertEqual(self.mgr.frozen_height, 60.0)  # 2 * 30
        self.assertEqual(self.mgr.body_viewport_w, 600.0) # 800 - 200
        self.assertEqual(self.mgr.body_viewport_h, 540.0) # 600 - 60

        windows = self.mgr.get_quadrant_windows()
        # NW
        self.assertEqual(windows["NW"].r0, 0)
        self.assertEqual(windows["NW"].r1, 2)
        self.assertEqual(windows["NW"].c0, 0)
        self.assertEqual(windows["NW"].c1, 2)
        self.assertEqual(windows["NW"].translate_x, 0.0)
        self.assertEqual(windows["NW"].translate_y, 0.0)

        # NE (Frozen rows, body cols)
        self.assertEqual(windows["NE"].r0, 0)
        self.assertEqual(windows["NE"].r1, 2)
        self.assertEqual(windows["NE"].c0, 2) # frozen_cols + 0
        # viewport_w 600 / 100 = 6 cols + overscan 1 = end col
        self.assertTrue(windows["NE"].c1 > 2)
        self.assertEqual(windows["NE"].translate_y, 0.0)

        # SW (Body rows, frozen cols)
        self.assertEqual(windows["SW"].r0, 2)
        self.assertEqual(windows["SW"].c0, 0)
        self.assertEqual(windows["SW"].c1, 2)
        self.assertEqual(windows["SW"].translate_x, 0.0)

    def test_scroll_clamping_and_transforms(self):
        self.mgr.scroll_to(50000.0, 50000.0)
        self.assertEqual(self.mgr.scroll_x, self.mgr.max_scroll_x)
        self.assertEqual(self.mgr.scroll_y, self.mgr.max_scroll_y)

        windows = self.mgr.get_quadrant_windows()
        self.assertEqual(windows["NW"].translate_x, 0.0)
        self.assertEqual(windows["NW"].translate_y, 0.0)
        self.assertEqual(windows["NE"].translate_x, -self.mgr.max_scroll_x)
        self.assertEqual(windows["NE"].translate_y, 0.0)
        self.assertEqual(windows["SW"].translate_x, 0.0)
        self.assertEqual(windows["SW"].translate_y, -self.mgr.max_scroll_y)
        self.assertEqual(windows["SE"].translate_x, -self.mgr.max_scroll_x)
        self.assertEqual(windows["SE"].translate_y, -self.mgr.max_scroll_y)

    def test_span_within_frozen_quadrant(self):
        # Add span inside NW corner: [0, 0, 2, 2)
        self.mgr.add_span(101, 0, 0, 2, 2)
        spans_nw = self.mgr.query_quadrant_spans("NW")
        self.assertEqual(len(spans_nw), 1)
        self.assertEqual(spans_nw[0].id, 101)
        self.assertEqual(spans_nw[0].bounds, [0, 0, 2, 2])
        self.assertEqual(spans_nw[0].clip, [0, 0, 2, 2])
        self.assertFalse(spans_nw[0].crosses_boundary)

        # Should not appear in SE
        spans_se = self.mgr.query_quadrant_spans("SE")
        self.assertEqual(len(spans_se), 0)

    def test_span_crossing_frozen_boundary(self):
        # Span crossing frozen rows boundary: r0=1, c0=1, r1=4, c1=4
        # Frozen boundary is rows=2, cols=2.
        # This span touches NW [0..2, 0..2), NE [0..2, 2..4), SW [2..4, 0..2), SE [2..4, 2..4)
        self.mgr.add_span(202, 1, 1, 4, 4)
        self.mgr.scroll_to(0, 0)

        all_spans = self.mgr.query_all_visible_spans()
        # It must be found in all 4 quadrants and marked as crosses_boundary=True
        self.assertEqual(len(all_spans["NW"]), 1)
        self.assertTrue(all_spans["NW"][0].crosses_boundary)
        self.assertEqual(all_spans["NW"][0].clip, [1, 1, 2, 2])

        self.assertEqual(len(all_spans["NE"]), 1)
        self.assertTrue(all_spans["NE"][0].crosses_boundary)
        self.assertEqual(all_spans["NE"][0].clip, [1, 2, 2, 4])

        self.assertEqual(len(all_spans["SW"]), 1)
        self.assertTrue(all_spans["SW"][0].crosses_boundary)
        self.assertEqual(all_spans["SW"][0].clip, [2, 1, 4, 2])

        self.assertEqual(len(all_spans["SE"]), 1)
        self.assertTrue(all_spans["SE"][0].crosses_boundary)
        self.assertEqual(all_spans["SE"][0].clip, [2, 2, 4, 4])

    def test_virtualized_body_scroll_query(self):
        # Span far down in SE body: rows [50..55), cols [30..35)
        self.mgr.add_span(303, 50, 30, 55, 35)

        # At scroll 0,0: should not be visible
        self.mgr.scroll_to(0, 0)
        self.assertEqual(len(self.mgr.query_quadrant_spans("SE")), 0)

        # Scroll down and right to reveal it
        # row 50 * 30px = 1500px, col 30 * 100px = 3000px
        self.mgr.scroll_to(2800.0, 1400.0)
        spans = self.mgr.query_quadrant_spans("SE")
        self.assertEqual(len(spans), 1)
        self.assertEqual(spans[0].id, 303)
        self.assertFalse(spans[0].crosses_boundary)
        self.assertEqual(spans[0].bounds, [50, 30, 55, 35])

    def test_render_manifest_structure(self):
        self.mgr.add_span(1, 0, 0, 2, 1)
        self.mgr.add_span(2, 5, 5, 8, 8)
        manifest = self.mgr.compute_render_manifest()

        self.assertIn("geometry", manifest)
        self.assertIn("quadrants", manifest)
        self.assertIn("spans", manifest)
        self.assertIn("total_virtual_nodes", manifest)
        self.assertTrue(manifest["total_virtual_nodes"] < 500) # strictly bounded DOM node count

    def test_contract_validations(self):
        # Invalid grid dimension
        with self.assertRaises(ValueError):
            FrozenSpanGridManager(0, 10, 30, 100, 800, 600)
        # Frozen rows exceeding total
        with self.assertRaises(ValueError):
            FrozenSpanGridManager(5, 5, 30, 100, 800, 600, frozen_rows=6)
        # Duplicate or overlapping span
        self.mgr.add_span(1, 0, 0, 2, 2)
        with self.assertRaises(ValueError):
            self.mgr.add_span(1, 2, 2, 4, 4) # duplicate id
        with self.assertRaises(ValueError):
            self.mgr.add_span(2, 1, 1, 3, 3) # overlapping

if __name__ == "__main__":
    unittest.main()
