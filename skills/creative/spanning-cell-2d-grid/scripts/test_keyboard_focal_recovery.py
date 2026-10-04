import unittest
import math
from keyboard_focal_recovery import FocalCellRecoveryEngine, KeyboardNavigationState


class KeyboardFocalRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.engine = FocalCellRecoveryEngine(row_px=32, col_px=96, rows=50, cols=50)
        # Add a 3x3 merge at [2, 2) to [5, 5)
        self.engine.add_merge('merge-hero', 2, 2, 5, 5)
        # Add a 2x1 merge at [10, 0) to [12, 1)
        self.engine.add_merge('merge-side', 10, 0, 12, 1)

    def test_owner_and_bounds_resolution(self):
        self.assertEqual(self.engine.get_owner(0, 0), 'cell-0-0')
        self.assertEqual(self.engine.get_owner(2, 2), 'merge-hero')
        self.assertEqual(self.engine.get_owner(4, 4), 'merge-hero')
        self.assertEqual(self.engine.get_owner(5, 5), 'cell-5-5')
        # World bounds
        bounds_hero = self.engine.get_cell_bounds_world(3, 3)
        self.assertEqual(bounds_hero, (2 * 96, 2 * 32, 5 * 96, 5 * 32))
        self.assertEqual(self.engine.get_cell_bounds_world(0, 0), (0, 0, 96, 32))

    def test_arrow_navigation_skips_merged_cells(self):
        # Moving Right from (2, 1) into (2, 2) merges -> jumps into (2, 2)
        pos = self.engine.navigate_arrow((2, 1), 'ArrowRight')
        self.assertEqual(pos, (2, 2))
        # Moving Right from inside merge (2, 2) must jump completely out to col 5
        pos_exit = self.engine.navigate_arrow((2, 2), 'ArrowRight')
        self.assertEqual(pos_exit, (2, 5))
        # Moving Down from inside merge (3, 3) must jump completely out to row 5
        pos_down = self.engine.navigate_arrow((3, 3), 'ArrowDown')
        self.assertEqual(pos_down, (5, 3))
        # Moving Left from (2, 5) jumps into (2, 4) which belongs to merge-hero
        pos_left = self.engine.navigate_arrow((2, 5), 'ArrowLeft')
        self.assertEqual(pos_left, (2, 4))
        # Moving Left from inside merge jumps out to col 1
        pos_left_exit = self.engine.navigate_arrow((2, 4), 'ArrowLeft')
        self.assertEqual(pos_left_exit, (2, 1))

    def test_arrow_navigation_grid_boundaries(self):
        # Top-left corner boundary
        self.assertEqual(self.engine.navigate_arrow((0, 0), 'ArrowUp'), (0, 0))
        self.assertEqual(self.engine.navigate_arrow((0, 0), 'ArrowLeft'), (0, 0))
        # Bottom-right corner boundary
        self.assertEqual(self.engine.navigate_arrow((49, 49), 'ArrowDown'), (49, 49))
        self.assertEqual(self.engine.navigate_arrow((49, 49), 'ArrowRight'), (49, 49))

    def test_visibility_determination(self):
        camera = (0.0, 0.0)
        viewport = (300.0, 200.0)  # ~3.1 cols by 6.2 rows
        self.assertTrue(self.engine.is_visible(0, 0, camera, viewport, zoom=1.0))
        self.assertTrue(self.engine.is_visible(2, 2, camera, viewport, zoom=1.0))
        # Cell at (15, 15) is far out
        self.assertFalse(self.engine.is_visible(15, 15, camera, viewport, zoom=1.0))

    def test_focal_recovery_retains_visible_cursor(self):
        camera = (100.0, 100.0)
        viewport = (400.0, 300.0)
        # Visible cell inside viewport
        recovered = self.engine.recover_focal_cell((4, 3), camera, viewport, zoom=1.0)
        self.assertEqual(recovered, (4, 3, 'retained_visible'))

    def test_focal_recovery_on_offscreen_drift(self):
        # Original cursor was (0, 0), but camera scrolled to (500, 400)
        camera = (500.0, 400.0)
        viewport = (400.0, 300.0)
        # Without edge direction, clamps to closest visible
        r, c, strategy = self.engine.recover_focal_cell((0, 0), camera, viewport, zoom=1.0)
        self.assertEqual(strategy, 'clamped_closest')
        self.assertTrue(self.engine.is_visible(r, c, camera, viewport, zoom=1.0))

    def test_focal_recovery_edge_direction_leading(self):
        # Camera is actively scrolling right and down (positive vx, vy)
        camera = (500.0, 400.0)
        viewport = (400.0, 300.0)
        r, c, strategy = self.engine.recover_focal_cell((0, 0), camera, viewport, zoom=1.0, edge_direction=(800.0, 800.0))
        self.assertEqual(strategy, 'edge_direction_lead')
        # Leading cell must be near the bottom-right of visible area
        self.assertTrue(self.engine.is_visible(r, c, camera, viewport, zoom=1.0))
        self.assertGreaterEqual(r, int(400 / 32))
        self.assertGreaterEqual(c, int(500 / 96))

    def test_focal_recovery_zoom_scaling(self):
        # At zoom 2.0, visible world rectangle is halved
        camera = (0.0, 0.0)
        viewport = (400.0, 300.0)  # world width 200, world height 150
        r, c, _ = self.engine.recover_focal_cell(None, camera, viewport, zoom=2.0)
        self.assertEqual((r, c), (0, 0))

    def test_roving_tab_index_calculation(self):
        visible_cells = [(0, 0), (0, 1), (2, 2), (3, 3)]
        tab_map = self.engine.reconcile_roving_tab_index((2, 2), visible_cells)
        # merge-hero (which owns (2,2) and (3,3)) gets 0
        self.assertEqual(tab_map['merge-hero'], 0)
        self.assertEqual(tab_map['cell-0-0'], -1)
        self.assertEqual(tab_map['cell-0-1'], -1)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            FocalCellRecoveryEngine(row_px=-1)
        with self.assertRaises(ValueError):
            self.engine.add_merge('invalid', 5, 5, 2, 2)
        with self.assertRaises(ValueError):
            # Overlapping merge
            self.engine.add_merge('overlap', 3, 3, 6, 6)
        with self.assertRaises(ValueError):
            self.engine.navigate_arrow((0, 0), 'Space')
        with self.assertRaises(ValueError):
            self.engine.is_visible(0, 0, (0, 0), (-100, 200))
        with self.assertRaises(ValueError):
            self.engine.recover_focal_cell((0, 0), (float('nan'), 0), (300, 200))


if __name__ == '__main__':
    unittest.main()
