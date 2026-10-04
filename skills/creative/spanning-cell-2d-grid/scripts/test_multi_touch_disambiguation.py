"""Unit tests for Multi-Touch Dual-Finger Pan and Rotation Disambiguation (UIUX-028)."""

import unittest
import math
from multi_touch_disambiguation import (
    MultiTouchDisambiguationEngine,
    DisambiguationConfig,
    DualTouchPoint,
    DualTouchGestureMode,
    DualTouchVectorState
)


class TestMultiTouchDisambiguation(unittest.TestCase):

    def setUp(self):
        self.config = DisambiguationConfig(
            pan_deadband_px=8.0,
            pinch_scale_threshold=0.08,
            rotation_deadband_deg=5.0,
            angular_lock_ratio=2.0,
            allow_rotation=True,
            rotation_snap_threshold_deg=3.0
        )
        self.engine = MultiTouchDisambiguationEngine(self.config)

    def test_initial_gesture_state(self):
        """Verifies initial touch placement initializes vector state with zero deltas."""
        t1 = DualTouchPoint(id=1, x=100.0, y=200.0)
        t2 = DualTouchPoint(id=2, x=200.0, y=200.0)
        state = self.engine.start_gesture(t1, t2)

        self.assertEqual(self.engine.active_mode, DualTouchGestureMode.UNDETERMINED)
        self.assertAlmostEqual(state.center_x, 150.0)
        self.assertAlmostEqual(state.center_y, 200.0)
        self.assertAlmostEqual(state.span_distance, 100.0)
        self.assertAlmostEqual(state.angle_rad, 0.0)

    def test_pure_translation_pan_disambiguation(self):
        """Pure parallel two-finger translation should lock to PAN mode and zero out rotation."""
        t1 = DualTouchPoint(id=1, x=100.0, y=200.0)
        t2 = DualTouchPoint(id=2, x=200.0, y=200.0)
        self.engine.start_gesture(t1, t2)

        # Move both fingers by +30px horizontally and +10px vertically
        t1_moved = DualTouchPoint(id=1, x=130.0, y=210.0)
        t2_moved = DualTouchPoint(id=2, x=230.0, y=210.0)
        mode, state = self.engine.update_touches(t1_moved, t2_moved)

        self.assertEqual(mode, DualTouchGestureMode.PAN)
        self.assertAlmostEqual(self.engine.viewport_offset_x, 30.0)
        self.assertAlmostEqual(self.engine.viewport_offset_y, 10.0)
        self.assertAlmostEqual(self.engine.viewport_rotation_deg, 0.0)
        self.assertAlmostEqual(self.engine.viewport_zoom, 1.0)
        self.assertAlmostEqual(state.delta_rotation_rad, 0.0)

    def test_pure_pinch_zoom_disambiguation(self):
        """Symmetric expansion without center shift should lock to PINCH_ZOOM."""
        t1 = DualTouchPoint(id=1, x=100.0, y=200.0)
        t2 = DualTouchPoint(id=2, x=200.0, y=200.0)
        self.engine.start_gesture(t1, t2)

        # Expand fingers from 100px to 140px symmetrically around center (150, 200)
        t1_zoom = DualTouchPoint(id=1, x=80.0, y=200.0)
        t2_zoom = DualTouchPoint(id=2, x=220.0, y=200.0)
        mode, state = self.engine.update_touches(t1_zoom, t2_zoom)

        self.assertEqual(mode, DualTouchGestureMode.PINCH_ZOOM)
        self.assertAlmostEqual(self.engine.viewport_zoom, 1.4)
        self.assertAlmostEqual(self.engine.viewport_offset_x, 0.0)
        self.assertAlmostEqual(self.engine.viewport_offset_y, 0.0)
        self.assertAlmostEqual(self.engine.viewport_rotation_deg, 0.0)

    def test_rotation_deadband_and_angular_locking(self):
        """Intentional rotation exceeding deadband should lock to ROTATE mode."""
        t1 = DualTouchPoint(id=1, x=100.0, y=200.0)
        t2 = DualTouchPoint(id=2, x=200.0, y=200.0)
        self.engine.start_gesture(t1, t2)

        # Rotate dual touches around center (150, 200) by approx 15 degrees (~0.2618 rad)
        angle = math.radians(15.0)
        radius = 50.0
        t1_rot = DualTouchPoint(id=1, x=150.0 - radius * math.cos(angle), y=200.0 - radius * math.sin(angle))
        t2_rot = DualTouchPoint(id=2, x=150.0 + radius * math.cos(angle), y=200.0 + radius * math.sin(angle))
        
        mode, state = self.engine.update_touches(t1_rot, t2_rot)
        self.assertEqual(mode, DualTouchGestureMode.ROTATE)
        self.assertGreater(abs(self.engine.viewport_rotation_deg), 10.0)
        self.assertAlmostEqual(self.engine.viewport_offset_x, 0.0, places=2)
        self.assertAlmostEqual(self.engine.viewport_offset_y, 0.0, places=2)

    def test_rotation_suppression_in_grid_spreadsheet_mode(self):
        """When allow_rotation=False (spreadsheet mode), angular motion is strictly suppressed."""
        cfg_no_rot = DisambiguationConfig(allow_rotation=False)
        engine_no_rot = MultiTouchDisambiguationEngine(cfg_no_rot)

        t1 = DualTouchPoint(id=1, x=100.0, y=200.0)
        t2 = DualTouchPoint(id=2, x=200.0, y=200.0)
        engine_no_rot.start_gesture(t1, t2)

        # Apply angular rotation + pan
        angle = math.radians(20.0)
        t1_rot = DualTouchPoint(id=1, x=120.0 - 50.0 * math.cos(angle), y=210.0 - 50.0 * math.sin(angle))
        t2_rot = DualTouchPoint(id=2, x=120.0 + 50.0 * math.cos(angle), y=210.0 + 50.0 * math.sin(angle))

        mode, state = engine_no_rot.update_touches(t1_rot, t2_rot)
        self.assertNotEqual(mode, DualTouchGestureMode.ROTATE)
        self.assertEqual(engine_no_rot.viewport_rotation_deg, 0.0)
        self.assertEqual(state.delta_rotation_rad, 0.0)

    def test_gesture_lifecycle_end_and_reset(self):
        """Verifies lifecycle teardown and transform state retention in summary."""
        t1 = DualTouchPoint(id=1, x=100.0, y=200.0)
        t2 = DualTouchPoint(id=2, x=200.0, y=200.0)
        self.engine.start_gesture(t1, t2)

        # Pan movement
        t1_pan = DualTouchPoint(id=1, x=150.0, y=200.0)
        t2_pan = DualTouchPoint(id=2, x=250.0, y=200.0)
        self.engine.update_touches(t1_pan, t2_pan)

        summary = self.engine.end_gesture()
        self.assertEqual(summary["final_mode"], "PAN")
        self.assertAlmostEqual(summary["viewport_offset"][0], 50.0)
        self.assertEqual(self.engine.active_mode, DualTouchGestureMode.UNDETERMINED)
        self.assertIsNone(self.engine.initial_vector)


if __name__ == "__main__":
    unittest.main()
