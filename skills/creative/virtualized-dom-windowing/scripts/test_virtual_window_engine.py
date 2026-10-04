#!/usr/bin/env python3
"""
Deterministic Unit Tests for Virtualized DOM Windowing Engine.
Tests:
1. Empty table handling (N=0).
2. Hard DOM node budget bounding for 100,000 rows (O(1) DOM pool).
3. Exact pixel offset calculation and spacer height matching.
4. Binary search overscan windowing for variable height rows.
5. Invariant: top_spacer + rendered_heights + bottom_spacer == total_height.
"""

import unittest
from virtual_window_engine import VirtualWindowEngine

class TestVirtualWindowEngine(unittest.TestCase):

    def test_empty_rows(self):
        engine = VirtualWindowEngine(total_rows=0, viewport_height=600.0)
        window = engine.compute_window(scroll_y=0.0)
        self.assertEqual(window["total_rows"], 0)
        self.assertEqual(window["rendered_count"], 0)
        self.assertEqual(window["total_height"], 0.0)

    def test_massive_fixed_rows_dom_budget(self):
        # 100,000 rows, 36px each, viewport 600px, overscan 5
        # Visible rows = ceil(600/36) + 1 = 17 or 18 rows.
        # Rendered count with overscan = 18 + 10 = ~28 rows.
        total_rows = 100_000
        engine = VirtualWindowEngine(
            total_rows=total_rows,
            viewport_height=600.0,
            row_height=36.0,
            overscan=5
        )

        self.assertEqual(engine.get_total_height(), 3_600_000.0)

        # Budget verification across scroll points
        self.assertTrue(engine.verify_dom_budget(max_allowed_nodes=40))

        # Check scroll at middle (row 50,000)
        scroll_middle = 50_000 * 36.0
        window = engine.compute_window(scroll_middle)

        self.assertLessEqual(window["rendered_count"], 35)
        self.assertGreaterEqual(window["rendered_count"], 15)
        self.assertGreaterEqual(window["visible_start"], 49_990)
        self.assertLessEqual(window["visible_start"], 50_010)

        # Invariant: spacer sum matches total height
        rendered_height_sum = sum(item["height"] for item in window["rendered_items"])
        computed_total = (
            window["top_spacer_height"] + rendered_height_sum + window["bottom_spacer_height"]
        )
        self.assertAlmostEqual(computed_total, engine.get_total_height(), places=3)

    def test_spacer_height_exact_conservation(self):
        # Test conservation at top, quarter, middle, bottom
        engine = VirtualWindowEngine(
            total_rows=10_000,
            viewport_height=500.0,
            row_height=40.0,
            overscan=4
        )

        scroll_points = [0.0, 120.0, 4500.0, 200_000.0, 399_500.0]
        total_h = engine.get_total_height()

        for sp in scroll_points:
            w = engine.compute_window(sp)
            rendered_h = sum(item["height"] for item in w["rendered_items"])
            total_sum = w["top_spacer_height"] + rendered_h + w["bottom_spacer_height"]
            self.assertAlmostEqual(total_sum, total_h, places=4)

    def test_variable_row_heights_binary_search(self):
        # Alternating heights: 30px and 60px
        heights = [30.0 if i % 2 == 0 else 60.0 for i in range(1000)]
        engine = VirtualWindowEngine(
            total_rows=1000,
            viewport_height=400.0,
            overscan=3,
            variable_heights=heights
        )

        # Check total height: 500 * 30 + 500 * 60 = 45,000px
        self.assertEqual(engine.get_total_height(), 45_000.0)

        # Check offset search
        self.assertEqual(engine.get_row_offset(0), 0.0)
        self.assertEqual(engine.get_row_offset(1), 30.0)
        self.assertEqual(engine.get_row_offset(2), 90.0)

        w = engine.compute_window(scroll_y=350.0)
        self.assertTrue(w["render_start"] <= w["visible_start"])
        self.assertTrue(w["render_end"] >= w["visible_end"])

        # Check node budget
        self.assertTrue(engine.verify_dom_budget(max_allowed_nodes=30))

        # Check height conservation
        rendered_h = sum(item["height"] for item in w["rendered_items"])
        self.assertAlmostEqual(
            w["top_spacer_height"] + rendered_h + w["bottom_spacer_height"],
            engine.get_total_height(),
            places=4
        )

    def test_overscan_flagging(self):
        engine = VirtualWindowEngine(
            total_rows=100,
            viewport_height=200.0,
            row_height=50.0,
            overscan=2
        )
        # scroll = 100.0 -> visible rows = row 2, 3, 4, 5
        w = engine.compute_window(100.0)
        for item in w["rendered_items"]:
            if item["index"] < w["visible_start"] or item["index"] > w["visible_end"]:
                self.assertTrue(item["is_overscan"])
            else:
                self.assertFalse(item["is_overscan"])

if __name__ == '__main__':
    unittest.main()
