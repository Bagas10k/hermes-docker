import unittest
from collapsible_frozen_header import (
    CollapsibleHierarchicalGrid,
    CollapsibleHeaderNode,
    VisibleCollapsibleHeaderItem
)

class TestCollapsibleHierarchicalGrid(unittest.TestCase):
    def setUp(self):
        # 100 rows, 30 columns, 3 levels
        # row_height = 32, default_col_width = 80, viewport = 640x480, frozen_cols = 2
        self.grid = CollapsibleHierarchicalGrid(
            total_rows=100,
            total_cols=30,
            header_levels=3,
            row_height=32.0,
            default_col_width=80.0,
            viewport_width=640.0,
            viewport_height=480.0,
            frozen_cols=2,
            overscan_cols=1
        )

    def tearDown(self):
        self.grid.close()

    def test_grid_initialization_and_validation(self):
        self.assertEqual(self.grid.header_levels, 3)
        self.assertEqual(self.grid.total_header_height, 96.0)
        geom = self.grid.get_layout_geometry()
        self.assertEqual(geom["frozen_width"], 160.0) # 2 * 80
        self.assertEqual(geom["total_width"], 2400.0)  # 30 * 80
        self.assertEqual(geom["body_total_width"], 2240.0) # 2400 - 160
        self.assertEqual(geom["body_viewport_width"], 480.0) # 640 - 160
        self.assertEqual(geom["max_scroll_x"], 1760.0) # 2240 - 480

        with self.assertRaises(ValueError):
            CollapsibleHierarchicalGrid(0, 10, 2, 30, 80, 600, 400)
        with self.assertRaises(ValueError):
            CollapsibleHierarchicalGrid(10, 10, 0, 30, 80, 600, 400)
        with self.assertRaises(ValueError):
            CollapsibleHierarchicalGrid(10, 10, 2, -10, 80, 600, 400)

    def test_add_collapsible_nodes_and_containment(self):
        # Frozen corner headers: col 0 and 1
        id_col = self.grid.add_header_node(100, "ID", level=0, c0=0, c1=1)
        name_col = self.grid.add_header_node(101, "Name", level=0, c0=1, c1=2)

        # Body Header: 2026 spanning cols 2..14 (12 columns)
        y2026 = self.grid.add_header_node(
            1, "2026", level=0, c0=2, c1=14, collapsible=True, summary_col_width=100.0
        )
        self.assertTrue(y2026.collapsible)
        self.assertFalse(y2026.is_collapsed)

        # Q1 spanning cols 2..8 (6 columns), Q2 spanning cols 8..14 (6 columns)
        q1 = self.grid.add_header_node(2, "Q1", level=1, c0=2, c1=8, parent_id=1, collapsible=True)
        q2 = self.grid.add_header_node(3, "Q2", level=1, c0=8, c1=14, parent_id=1, collapsible=True)

        self.assertIn(2, y2026.child_ids)
        self.assertIn(3, y2026.child_ids)

        # Non-collapsible leaf headers: Months under Q1
        m1 = self.grid.add_header_node(4, "Jan", level=2, c0=2, c1=4, parent_id=2)
        m2 = self.grid.add_header_node(5, "Feb", level=2, c0=4, c1=6, parent_id=2)
        m3 = self.grid.add_header_node(6, "Mar", level=2, c0=6, c1=8, parent_id=2)

        self.assertEqual(q1.child_ids, [4, 5, 6])

    def test_single_level_toggle_collapse_geometry(self):
        # Root group Q1: cols 2..8 (6 columns, initial width = 6 * 80 = 480)
        q1 = self.grid.add_header_node(2, "Q1", level=0, c0=2, c1=8, collapsible=True, summary_col_width=120.0)

        initial_widths = self.grid.get_effective_column_widths()
        self.assertEqual(sum(initial_widths[2:8]), 480.0)
        geom_initial = self.grid.get_layout_geometry()
        self.assertEqual(geom_initial["total_width"], 2400.0)

        # Collapse Q1
        new_state = self.grid.toggle_group(2)
        self.assertTrue(new_state)
        self.assertTrue(q1.is_collapsed)

        collapsed_widths = self.grid.get_effective_column_widths()
        self.assertEqual(collapsed_widths[2], 120.0) # Column 2 takes summary width
        for c in range(3, 8):
            self.assertEqual(collapsed_widths[c], 0.0) # Internal columns zeroed out (Zero-CLS)

        self.assertEqual(sum(collapsed_widths[2:8]), 120.0)
        geom_collapsed = self.grid.get_layout_geometry()
        # Difference = 480 - 120 = 360 px reduction
        self.assertEqual(geom_collapsed["total_width"], 2400.0 - 360.0)
        self.assertEqual(geom_collapsed["body_total_width"], 2240.0 - 360.0)

        # Expand Q1 back
        self.grid.toggle_group(2)
        self.assertFalse(q1.is_collapsed)
        restored_widths = self.grid.get_effective_column_widths()
        self.assertEqual(sum(restored_widths[2:8]), 480.0)
        self.assertEqual(self.grid.get_layout_geometry()["total_width"], 2400.0)

    def test_multi_tier_nested_accordion_collapse(self):
        # Level 0: 2026 [2..14) (12 cols)
        self.grid.add_header_node(1, "2026", level=0, c0=2, c1=14, collapsible=True, summary_col_width=150.0)
        # Level 1: Q1 [2..8) (6 cols), Q2 [8..14) (6 cols)
        self.grid.add_header_node(2, "Q1", level=1, c0=2, c1=8, parent_id=1, collapsible=True, summary_col_width=100.0)
        self.grid.add_header_node(3, "Q2", level=1, c0=8, c1=14, parent_id=1, collapsible=True, summary_col_width=100.0)

        # Level 2: Jan [2..5), Feb [5..8)
        self.grid.add_header_node(4, "Jan", level=2, c0=2, c1=5, parent_id=2)
        self.grid.add_header_node(5, "Feb", level=2, c0=5, c1=8, parent_id=2)

        # 1. Collapse Q1 only
        self.grid.set_collapsed_state(2, True)
        self.assertFalse(self.grid.is_ancestor_collapsed(2))
        self.assertTrue(self.grid.is_ancestor_collapsed(4)) # Jan's ancestor Q1 is collapsed
        self.assertTrue(self.grid.is_ancestor_collapsed(5)) # Feb's ancestor Q1 is collapsed

        widths = self.grid.get_effective_column_widths()
        self.assertEqual(widths[2], 100.0) # Q1 summary col
        self.assertEqual(sum(widths[3:8]), 0.0)
        self.assertEqual(sum(widths[8:14]), 6 * 80.0) # Q2 intact

        # 2. Collapse Root 2026 (supersedes child Q1/Q2)
        self.grid.set_collapsed_state(1, True)
        self.assertTrue(self.grid.is_ancestor_collapsed(2)) # Q1's ancestor 2026 is collapsed
        self.assertTrue(self.grid.is_ancestor_collapsed(3)) # Q2's ancestor 2026 is collapsed

        widths_root = self.grid.get_effective_column_widths()
        self.assertEqual(widths_root[2], 150.0) # 2026 summary col
        self.assertEqual(sum(widths_root[3:14]), 0.0)

    def test_spatial_rtree_queries_on_collapse_and_expand(self):
        self.grid.add_header_node(10, "GroupA", level=0, c0=2, c1=10, collapsible=True, summary_col_width=80.0)
        self.grid.add_header_node(11, "SubA1", level=1, c0=2, c1=6, parent_id=10)
        self.grid.add_header_node(12, "SubA2", level=1, c0=6, c1=10, parent_id=10)

        # Initial query: All should be visible when scrolled to 0
        self.grid.scroll_to(0.0)
        visible = self.grid.query_visible_headers()
        ids = [v.id for v in visible]
        self.assertIn(10, ids)
        self.assertIn(11, ids)
        self.assertIn(12, ids)

        # Collapse GroupA
        self.grid.toggle_group(10)
        visible_collapsed = self.grid.query_visible_headers()
        group_item = next(v for v in visible_collapsed if v.id == 10)
        self.assertEqual(group_item.pixel_width, 80.0)
        self.assertTrue(group_item.is_collapsed)

        # Children SubA1 and SubA2 are hidden by parent
        sub_items = [v for v in visible_collapsed if v.id in (11, 12)]
        for s in sub_items:
            self.assertTrue(s.is_hidden_by_parent)
            self.assertEqual(s.pixel_width, 0.0)

    def test_progressive_sticky_offset_recalculation(self):
        # Group spanning cols 2..10 (8 * 80 = 640px) with summary col width 160px
        self.grid.add_header_node(20, "Financials", level=0, c0=2, c1=10, collapsible=True, summary_col_width=160.0)

        # Scroll right by 200px (viewport covers [360..840], Financials uncollapsed covers [160..800], so it's visible)
        self.grid.scroll_to(200.0)
        visible = self.grid.query_visible_headers()
        item = next(v for v in visible if v.id == 20)
        self.assertGreater(item.sticky_offset_x, 0.0)
        self.assertEqual(item.sticky_offset_x, 200.0)

        # Scroll to 40px so col 2 [160..320] is partially scrolled when collapsed
        self.grid.scroll_to(40.0) # viewport window [200..680] covers [160..320]
        self.grid.toggle_group(20)
        visible_col = self.grid.query_visible_headers()
        item_col = next(v for v in visible_col if v.id == 20)
        self.assertTrue(item_col.is_collapsed)
        # Node starts at 160. active_view_x0 = 160 + 40 = 200. offset = 40. max_sticky = 160 - 80 = 80.
        self.assertEqual(item_col.sticky_offset_x, 40.0)

    def test_composite_render_manifest(self):
        self.grid.add_header_node(1, "2026", level=0, c0=2, c1=8, collapsible=True)
        manifest = self.grid.compute_render_manifest()

        self.assertIn("geometry", manifest)
        self.assertIn("visible_headers", manifest)
        self.assertEqual(manifest["effective_column_count"], 30)
        self.assertGreater(manifest["visible_headers_count"], 0)

        header_entry = manifest["visible_headers"][0]
        self.assertIn("pixel_x", header_entry)
        self.assertIn("pixel_width", header_entry)
        self.assertIn("collapsible", header_entry)
        self.assertIn("is_collapsed", header_entry)

if __name__ == "__main__":
    unittest.main()
