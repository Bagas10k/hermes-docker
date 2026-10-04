"""
Unit tests for Spring Physics Width Interpolation on Collapsible Column Transitions (UIUX-021).
"""

import unittest
from spring_transition import (
    SpringConfig,
    ColumnSpringState,
    ColumnSpringInterpolator,
    AnimatedCollapsibleGrid
)

class TestSpringPhysicsTransitions(unittest.TestCase):
    def setUp(self):
        # Create a 2-level header grid with 8 columns (e.g. Q1=[col 0..3], Q2=[col 4..7])
        self.grid = AnimatedCollapsibleGrid(
            total_rows=20,
            total_cols=8,
            header_levels=2,
            row_height=30.0,
            default_col_width=100.0,
            viewport_width=600.0,
            viewport_height=400.0,
            frozen_cols=0
        )
        # Register Q1 group: cols [0, 4)
        self.q1_id = 1
        self.grid.add_header_node(
            node_id=self.q1_id,
            title="Quarter 1",
            level=0,
            c0=0,
            c1=4,
            collapsible=True,
            summary_col_width=120.0
        )
        # Register Q1 months
        self.m1_id = 2
        self.m2_id = 3
        self.m3_id = 4
        self.m4_id = 5
        self.grid.add_header_node(2, "Jan", 1, 0, 1, parent_id=self.q1_id)
        self.grid.add_header_node(3, "Feb", 1, 1, 2, parent_id=self.q1_id)
        self.grid.add_header_node(4, "Mar", 1, 2, 3, parent_id=self.q1_id)
        self.grid.add_header_node(5, "Q1 Summary", 1, 3, 4, parent_id=self.q1_id)

    def tearDown(self):
        self.grid.close()

    def test_01_spring_config_validation(self):
        """Validates parameters and bounds of SpringConfig."""
        cfg = SpringConfig(stiffness=300.0, damping=30.0, mass=1.0)
        self.assertEqual(cfg.stiffness, 300.0)
        self.assertEqual(cfg.damping, 30.0)

        with self.assertRaises(ValueError):
            SpringConfig(stiffness=0)
        with self.assertRaises(ValueError):
            SpringConfig(damping=-1.0)
        with self.assertRaises(ValueError):
            SpringConfig(mass=0.0)
        with self.assertRaises(ValueError):
            SpringConfig(precision_threshold=-0.5)

    def test_02_interpolator_single_step_dynamics(self):
        """Tests Hooke's law step execution and convergence towards target."""
        interp = ColumnSpringInterpolator([100.0, 100.0, 100.0])
        self.assertTrue(interp.is_all_settled)

        # Set target for col 0 to 0.0 (collapse)
        interp.set_target_width(0, 0.0)
        self.assertFalse(interp.is_all_settled)

        # Step 1 frame (1/60s)
        still_animating = interp.step(1.0 / 60.0)
        self.assertTrue(still_animating)
        w0 = interp.get_current_widths()[0]
        self.assertLess(w0, 100.0)
        self.assertGreater(w0, 0.0)

        # Run until settled
        frames = 0
        while not interp.is_all_settled and frames < 300:
            interp.step(1.0 / 60.0)
            frames += 1

        self.assertTrue(interp.is_all_settled)
        self.assertAlmostEqual(interp.get_current_widths()[0], 0.0, delta=0.1)

    def test_03_animated_collapse_initiates_springs(self):
        """Verifies that toggle_collapse_animated sets target widths and starts animation."""
        self.assertFalse(self.grid.is_animating)
        new_state = self.grid.toggle_collapse_animated(self.q1_id)
        self.assertTrue(new_state)  # is_collapsed = True
        self.assertTrue(self.grid.is_animating)

        # Target widths: col 0 should be 120.0, cols 1..3 should be 0.0
        interp = self.grid.interpolator
        self.assertEqual(interp.springs[0].target_width, 120.0)
        self.assertEqual(interp.springs[1].target_width, 0.0)
        self.assertEqual(interp.springs[2].target_width, 0.0)
        self.assertEqual(interp.springs[3].target_width, 0.0)
        # Cols 4..7 untouched at 100.0
        self.assertEqual(interp.springs[4].target_width, 100.0)

    def test_04_rtree_spatial_sync_during_animation(self):
        """Verifies that each step_animation updates R-Tree bounds with sub-frame values."""
        self.grid.toggle_collapse_animated(self.q1_id)
        initial_widths = self.grid.get_interpolated_column_widths()

        # Step 5 frames
        for _ in range(5):
            self.grid.step_animation(1.0 / 60.0)

        mid_widths = self.grid.get_interpolated_column_widths()
        self.assertNotEqual(initial_widths, mid_widths)

        # Query visible headers in mid-flight
        visible = self.grid.query_visible_headers_interpolated()
        q1_vis = next(v for v in visible if v.id == self.q1_id)
        # Width of Q1 in collapsed mode interpolates col 0 towards 120px with spring overshoot
        self.assertLess(q1_vis.pixel_width, 400.0)
        self.assertGreater(q1_vis.pixel_width, 90.0)

    def test_05_expand_reverses_animation_smoothly(self):
        """Verifies collapsing, then expanding mid-flight reverses target back to 100.0."""
        self.grid.toggle_collapse_animated(self.q1_id)
        for _ in range(10):
            self.grid.step_animation(1.0 / 60.0)

        # Reverse mid-flight
        new_state = self.grid.toggle_collapse_animated(self.q1_id)
        self.assertFalse(new_state)  # Expanded
        self.assertEqual(self.grid.interpolator.springs[1].target_width, 100.0)

        # Run to finish
        for _ in range(200):
            self.grid.step_animation(1.0 / 60.0)

        self.assertFalse(self.grid.is_animating)
        self.assertAlmostEqual(self.grid.get_interpolated_column_widths()[1], 100.0, delta=0.2)

    def test_06_sticky_title_offset_recalculation_during_spring(self):
        """Tests that progressive sticky title offsets track shifting spring boundaries correctly."""
        self.grid.scroll_x = 50.0  # Scroll into Q1
        self.grid.toggle_collapse_animated(self.q1_id)

        # Check manifest before and after 10 frames
        man0 = self.grid.compute_render_manifest_animated()
        self.assertTrue(man0["is_animating"])

        for _ in range(15):
            self.grid.step_animation(1.0 / 60.0)

        man1 = self.grid.compute_render_manifest_animated()
        self.assertLess(man1["rendered_total_width"], man0["rendered_total_width"])

    def test_07_snap_to_target_instant_settle(self):
        """Verifies snap_to_target settles all springs immediately."""
        self.grid.toggle_collapse_animated(self.q1_id)
        self.assertTrue(self.grid.is_animating)

        self.grid.interpolator.snap_to_target()
        self.assertTrue(self.grid.interpolator.is_all_settled)
        self.assertEqual(self.grid.get_interpolated_column_widths()[1], 0.0)
        self.assertEqual(self.grid.get_interpolated_column_widths()[0], 120.0)

if __name__ == "__main__":
    unittest.main()
