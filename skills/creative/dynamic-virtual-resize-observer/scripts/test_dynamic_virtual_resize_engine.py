#!/usr/bin/env python3
"""
Unit tests for Dynamic Content Height Virtualization & Asynchronous ResizeObserver Invalidation Engine.
Verifies:
1. Fenwick Tree prefix sum and point update precision.
2. Binary lifting search for row boundary resolution.
3. DOM node recycling bounds (O(1) active nodes for N = 100,000 rows).
4. Asynchronous ResizeObserver batch measurement and dynamic height mutations.
5. Zero-CLS scroll anchoring invariant (relative position preserved when content above shifts).
6. Height conservation invariant (top_spacer + rendered_heights + bottom_spacer == total_height).
"""

import unittest
from dynamic_virtual_resize_engine import FenwickTree, DynamicVirtualResizeEngine

class TestDynamicVirtualResizeEngine(unittest.TestCase):
    def test_fenwick_tree_primitives(self):
        arr = [10.0, 20.0, 30.0, 40.0, 50.0]
        ft = FenwickTree.from_array(arr)

        self.assertEqual(ft.prefix_sum(1), 10.0)
        self.assertEqual(ft.prefix_sum(3), 60.0)
        self.assertEqual(ft.prefix_sum(5), 150.0)
        self.assertEqual(ft.range_sum(2, 4), 90.0)

        # Update index 2 (+15.0) -> [10, 35, 30, 40, 50]
        ft.add(2, 15.0)
        self.assertEqual(ft.prefix_sum(2), 45.0)
        self.assertEqual(ft.prefix_sum(5), 165.0)

        # Test binary lifting find_index_of_offset
        # Offsets: row 1 (0..10), row 2 (10..45), row 3 (45..75), row 4 (75..115), row 5 (115..165)
        self.assertEqual(ft.find_index_of_offset(0.0), 1)
        self.assertEqual(ft.find_index_of_offset(5.0), 1)
        self.assertEqual(ft.find_index_of_offset(10.0), 2)
        self.assertEqual(ft.find_index_of_offset(44.9), 2)
        self.assertEqual(ft.find_index_of_offset(45.0), 3)
        self.assertEqual(ft.find_index_of_offset(100.0), 4)
        self.assertEqual(ft.find_index_of_offset(150.0), 5)

    def test_massive_scale_bounded_dom_recycling(self):
        # 100,000 rows with estimated height 40px
        total_rows = 100000
        viewport_height = 600.0
        overscan = 5
        engine = DynamicVirtualResizeEngine(
            total_rows=total_rows,
            viewport_height=viewport_height,
            estimated_row_height=40.0,
            overscan=overscan,
            min_row_height=20.0
        )

        self.assertEqual(engine.get_total_height(), 4000000.0)

        # Check window at scroll_y = 500,000.0 (middle of the list)
        win = engine.compute_window(scroll_y=500000.0)
        self.assertLessEqual(win["rendered_count"], win["max_dom_nodes_bound"])
        # Expected rendered count around (600/40) = 15 + 2*5 overscan = ~25-27 rows
        self.assertLess(win["rendered_count"], 45)

        # Test height conservation invariant
        top_spacer = win["top_spacer_height"]
        bottom_spacer = win["bottom_spacer_height"]
        rendered_height = sum(r["height"] for r in win["rows"])
        reconstructed_total = top_spacer + rendered_height + bottom_spacer

        self.assertAlmostEqual(reconstructed_total, win["total_height"], places=4)

    def test_resize_observer_batch_mutation(self):
        # 100 rows with default 30px
        engine = DynamicVirtualResizeEngine(
            total_rows=100,
            viewport_height=400.0,
            estimated_row_height=30.0,
            overscan=3
        )
        self.assertEqual(engine.get_total_height(), 3000.0)

        # Simulate ResizeObserver callback measuring dynamic card expansions:
        # row 10 expands to 80px (+50px)
        # row 15 expands to 60px (+30px)
        batch = [(10, 80.0), (15, 60.0)]
        res = engine.handle_resize_observer_batch(batch, current_scroll_y=0.0)

        self.assertEqual(res["updated_count"], 2)
        self.assertEqual(res["total_height_delta"], 80.0)
        self.assertEqual(engine.get_total_height(), 3080.0)
        self.assertEqual(engine.get_row_height(10), 80.0)
        self.assertEqual(engine.get_row_height(15), 60.0)

        # Check row 11 offset before vs after
        # Rows 0..9 = 10 * 30 = 300. Row 10 is at 300.
        self.assertEqual(engine.get_row_offset(10), 300.0)
        # Row 11 offset was 330, now 300 + 80 = 380 (+50px)
        self.assertEqual(engine.get_row_offset(11), 380.0)

    def test_scroll_anchoring_zero_cls_invariant(self):
        """
        Crucial UI/UX invariant:
        When a user is viewing row 50 (e.g. reading a comment), and rows 10..20 above it
        expand due to asynchronous image/avatar loads, the viewport must adjust scroll_y
        by the exact delta so the user does NOT experience visual jump (Zero CLS).
        """
        engine = DynamicVirtualResizeEngine(
            total_rows=200,
            viewport_height=500.0,
            estimated_row_height=40.0,
            overscan=4
        )

        anchor_index = 50
        # Offset of row 50 initially is 50 * 40 = 2000.0
        initial_scroll_y = engine.get_row_offset(anchor_index) # 2000.0

        # Viewport displays row 50 at the very top (screen offset = 0)
        initial_relative_top = engine.get_row_offset(anchor_index) - initial_scroll_y
        self.assertEqual(initial_relative_top, 0.0)

        # Now async ResizeObserver fires for rows above the anchor:
        # row 5 expands by +60px (40 -> 100)
        # row 20 expands by +40px (40 -> 80)
        # row 60 (below anchor) expands by +50px (40 -> 90)
        batch = [
            (5, 100.0),  # delta +60 (above anchor)
            (20, 80.0),  # delta +40 (above anchor)
            (60, 90.0)   # delta +50 (below anchor, should NOT shift scroll_y)
        ]

        result = engine.handle_resize_observer_batch(
            measurements=batch,
            current_scroll_y=initial_scroll_y,
            anchor_index=anchor_index
        )

        # Cumulative delta above anchor = 60 + 40 = 100.0
        self.assertEqual(result["scroll_delta"], 100.0)
        new_scroll_y = result["adjusted_scroll_y"]
        self.assertEqual(new_scroll_y, 2100.0)

        # Row 50's new offset should also be 2000 + 100 = 2100.0
        new_anchor_offset = engine.get_row_offset(anchor_index)
        self.assertEqual(new_anchor_offset, 2100.0)

        # Relative visual position in viewport: new_anchor_offset - new_scroll_y == 0.0!
        # Visual position is perfectly preserved!
        new_relative_top = new_anchor_offset - new_scroll_y
        self.assertEqual(new_relative_top, 0.0)

    def test_window_computation_with_mixed_heights(self):
        engine = DynamicVirtualResizeEngine(
            total_rows=10,
            viewport_height=100.0,
            estimated_row_height=20.0,
            overscan=1
        )
        # Update row 2 to 60px, row 5 to 10px
        engine.handle_resize_observer_batch([(2, 60.0), (5, 10.0)], current_scroll_y=0.0)

        # Offsets:
        # 0: 0 (h=20)
        # 1: 20 (h=20)
        # 2: 40 (h=60)
        # 3: 100 (h=20)
        # 4: 120 (h=20)
        # 5: 140 (h=10)
        # 6: 150 (h=20)...
        self.assertEqual(engine.get_row_offset(0), 0.0)
        self.assertEqual(engine.get_row_offset(2), 40.0)
        self.assertEqual(engine.get_row_offset(3), 100.0)
        self.assertEqual(engine.get_row_offset(6), 150.0)

        win = engine.compute_window(scroll_y=45.0)
        # scroll_y 45 falls inside row 2 (offset 40 to 100)
        self.assertEqual(win["visible_start"], 2)
        # viewport_bottom = 45 + 100 = 145, falls inside row 5 (offset 140 to 150)
        self.assertEqual(win["visible_end"], 5)
        # render_start = max(0, 2 - 1) = 1
        self.assertEqual(win["render_start"], 1)
        # render_end = min(9, 5 + 1) = 6
        self.assertEqual(win["render_end"], 6)

        # Verify conservation
        rendered_h = sum(r["height"] for r in win["rows"])
        self.assertAlmostEqual(win["top_spacer_height"] + rendered_h + win["bottom_spacer_height"], engine.get_total_height(), places=5)

if __name__ == "__main__":
    unittest.main()
