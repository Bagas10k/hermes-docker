import unittest
from hierarchical_frozen_header import (
    HierarchicalFrozenHeaderGrid,
    HeaderNode,
    VisibleHeaderItem
)

class TestHierarchicalFrozenHeaderGrid(unittest.TestCase):
    def setUp(self):
        # 100 rows x 40 cols, 3 levels of header (e.g., Year, Quarter, Month)
        # row_height=32, col_width=80, viewport=640x480, 2 frozen cols, overscan=1
        self.grid = HierarchicalFrozenHeaderGrid(
            total_rows=100,
            total_cols=40,
            header_levels=3,
            row_height=32.0,
            col_width=80.0,
            viewport_width=640.0,
            viewport_height=480.0,
            frozen_cols=2,
            overscan_cols=1
        )

    def tearDown(self):
        self.grid.close()

    def test_grid_initialization_and_validation(self):
        self.assertEqual(self.grid.header_levels, 3)
        self.assertEqual(self.grid.total_header_height, 96.0) # 3 * 32
        self.assertEqual(self.grid.frozen_col_width, 160.0)   # 2 * 80
        self.assertEqual(self.grid.body_viewport_w, 480.0)   # 640 - 160
        self.assertEqual(self.grid.body_total_w, 3040.0)     # 38 * 80
        self.assertEqual(self.grid.max_scroll_x, 2560.0)     # 3040 - 480

        # Invalid arguments
        with self.assertRaises(ValueError):
            HierarchicalFrozenHeaderGrid(0, 10, 1, 30, 50, 400, 300)
        with self.assertRaises(ValueError):
            HierarchicalFrozenHeaderGrid(10, 10, 0, 30, 50, 400, 300)
        with self.assertRaises(ValueError):
            HierarchicalFrozenHeaderGrid(10, 10, 15, 30, 50, 400, 300)
        with self.assertRaises(ValueError):
            HierarchicalFrozenHeaderGrid(10, 10, 2, -10, 50, 400, 300)

    def test_add_header_hierarchy_and_containment(self):
        # Level 0 (Root group 2026): cols 2 to 14 (12 columns)
        y2026 = self.grid.add_header_node(1, "2026", level=0, c0=2, c1=14)
        self.assertEqual(y2026.r0, 0)
        self.assertEqual(y2026.r1, 1)

        # Level 1 (Q1, Q2 under 2026)
        q1 = self.grid.add_header_node(2, "Q1", level=1, c0=2, c1=8, parent_id=1)
        q2 = self.grid.add_header_node(3, "Q2", level=1, c0=8, c1=14, parent_id=1)

        self.assertIn(2, y2026.child_ids)
        self.assertIn(3, y2026.child_ids)

        # Level 2 (Months under Q1)
        m1 = self.grid.add_header_node(4, "Jan", level=2, c0=2, c1=4, parent_id=2)
        m2 = self.grid.add_header_node(5, "Feb", level=2, c0=4, c1=6, parent_id=2)
        m3 = self.grid.add_header_node(6, "Mar", level=2, c0=6, c1=8, parent_id=2)

        self.assertEqual(q1.child_ids, [4, 5, 6])

    def test_containment_violation_rejection(self):
        # Create root [0, 10)
        self.grid.add_header_node(1, "Root", level=0, c0=0, c1=10)

        # Child exceeds right boundary: [5, 12)
        with self.assertRaises(ValueError):
            self.grid.add_header_node(2, "InvalidChild", level=1, c0=5, c1=12, parent_id=1)

        # Child exceeds left boundary: [-1, 5) -> invalid boundary
        with self.assertRaises(ValueError):
            self.grid.add_header_node(3, "InvalidLeft", level=1, c0=-1, c1=5, parent_id=1)

        # Non-level 0 node without parent
        with self.assertRaises(ValueError):
            self.grid.add_header_node(4, "OrphanChild", level=1, c0=2, c1=4)

        # Child with incorrect parent level skip (level 2 child with level 0 parent)
        with self.assertRaises(ValueError):
            self.grid.add_header_node(5, "SkippedLevel", level=2, c0=2, c1=4, parent_id=1)

    def test_sibling_overlap_rejection(self):
        self.grid.add_header_node(10, "GroupA", level=0, c0=0, c1=10)
        # Sibling overlapping [5, 15) on level 0
        with self.assertRaises(ValueError):
            self.grid.add_header_node(11, "OverlapA", level=0, c0=5, c1=15)

        # Sibling touching boundary [10, 20) is valid (half-open)
        node_b = self.grid.add_header_node(12, "GroupB", level=0, c0=10, c1=20)
        self.assertEqual(node_b.c0, 10)

    def test_frozen_and_virtual_column_query(self):
        # Frozen corner headers: col 0 and 1
        self.grid.add_header_node(100, "ID", level=0, c0=0, c1=1)
        self.grid.add_header_node(101, "Name", level=0, c0=1, c1=2)

        # Body headers: Year 2026 [2..26)
        self.grid.add_header_node(1, "2026", level=0, c0=2, c1=26)
        self.grid.add_header_node(2, "H1", level=1, c0=2, c1=14, parent_id=1)
        self.grid.add_header_node(3, "H2", level=1, c0=14, c1=26, parent_id=1)

        # Scroll to 0: viewport covers cols 2 to ~8 (+ overscan 1 -> cols 2..9)
        self.grid.scroll_to(0)
        visible = self.grid.query_visible_headers()
        visible_ids = {h.id for h in visible}

        # ID, Name, 2026, H1 must be visible; H2 starts at col 14, out of range
        self.assertIn(100, visible_ids)
        self.assertIn(101, visible_ids)
        self.assertIn(1, visible_ids)
        self.assertIn(2, visible_ids)
        self.assertNotIn(3, visible_ids)

        # Check clipping on 2026: bounds [0, 2, 1, 26], clip to visible end (e.g. 9)
        h_2026 = next(h for h in visible if h.id == 1)
        self.assertTrue(h_2026.is_partially_clipped)
        self.assertEqual(h_2026.clip[1], 2) # c0 stays 2
        self.assertTrue(h_2026.clip[3] < 26) # c1 is clipped to viewport end

    def test_scroll_and_progressive_stickiness(self):
        # Header [2..20)
        self.grid.add_header_node(1, "LongGroup", level=0, c0=2, c1=20)

        # Initial scroll=0 -> viewport start matches node start (col 2)
        self.grid.scroll_to(0)
        visible_0 = self.grid.query_visible_headers()
        h0 = next(h for h in visible_0 if h.id == 1)
        self.assertEqual(h0.sticky_offset_x, 0.0)

        # Scroll right by 240px (3 columns of 80px)
        # Viewport start moves to col 2 + 3 = 5
        self.grid.scroll_to(240.0)
        visible_scroll = self.grid.query_visible_headers()
        h_scroll = next(h for h in visible_scroll if h.id == 1)
        # sticky offset should equal the scrolled distance (240px)
        self.assertEqual(h_scroll.sticky_offset_x, 240.0)
        self.assertTrue(h_scroll.is_partially_clipped)

    def test_header_render_manifest_and_tree(self):
        self.grid.add_header_node(1, "Main", level=0, c0=0, c1=10)
        self.grid.add_header_node(2, "Sub1", level=1, c0=0, c1=5, parent_id=1)
        self.grid.add_header_node(3, "Sub2", level=1, c0=5, c1=10, parent_id=1)

        manifest = self.grid.compute_header_render_manifest()

        self.assertIn("geometry", manifest)
        self.assertIn("levels", manifest)
        self.assertIn("hierarchy_tree", manifest)
        self.assertEqual(manifest["geometry"]["header_levels"], 3)
        self.assertEqual(manifest["total_visible_header_nodes"], 3)

        tree = manifest["hierarchy_tree"]
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree[0]["title"], "Main")
        self.assertEqual(len(tree[0]["children"]), 2)

if __name__ == "__main__":
    unittest.main()
