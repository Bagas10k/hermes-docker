"""Unit tests for Multi-Touch Pinch-to-Zoom Camera Matrix & 2D Orthographic Projections.
"""

import unittest
import math
from pinch_zoom_camera import (
    TouchPoint,
    PinchGestureState,
    GestureAnalyzer,
    OrthographicCamera2D,
    ZoomController,
    CameraSyncManifest
)


class TestPinchZoomCameraMatrix(unittest.TestCase):
    """Test suite covering gesture analysis, focal invariance, matrix math, and sync manifests."""

    def setUp(self):
        self.viewport_w = 1280.0
        self.viewport_h = 720.0
        self.analyzer = GestureAnalyzer()
        self.camera = OrthographicCamera2D(
            viewport_width=self.viewport_w,
            viewport_height=self.viewport_h,
            min_zoom=0.25,
            max_zoom=4.0,
            current_zoom=1.0
        )
        self.controller = ZoomController(self.viewport_w, self.viewport_h)

    def test_gesture_analyzer_two_touches(self):
        """Verifies geometric distance, center coordinate, and angle calculation."""
        t1 = TouchPoint(id=0, x=100.0, y=200.0)
        t2 = TouchPoint(id=1, x=400.0, y=600.0)
        state = self.analyzer.analyze_two_touches(t1, t2)

        # Expected dx = 300, dy = 400 -> hypot = 500
        self.assertAlmostEqual(state.distance, 500.0, places=4)
        self.assertAlmostEqual(state.center_x, 250.0, places=4)
        self.assertAlmostEqual(state.center_y, 400.0, places=4)
        self.assertAlmostEqual(state.angle_rad, math.atan2(400.0, 300.0), places=4)

    def test_pinch_ratio_calculation(self):
        """Verifies scaling ratio between initial and ongoing touch distances."""
        init_state = PinchGestureState(distance=200.0, center_x=100.0, center_y=100.0, angle_rad=0.0)
        cur_state = PinchGestureState(distance=300.0, center_x=105.0, center_y=105.0, angle_rad=0.0)
        ratio = self.analyzer.compute_pinch_ratio(init_state, cur_state)
        self.assertAlmostEqual(ratio, 1.5, places=4)

    def test_focal_point_anchoring_invariance(self):
        """CRITICAL: The world point under the focal point must not move during zooming."""
        focal_x = 450.0
        focal_y = 300.0

        # World point under focal before zoom
        world_x_before, world_y_before = self.camera.screen_to_world(focal_x, focal_y)

        # Zoom in from 1.0 to 2.5
        self.camera.set_zoom_immediate(2.5, focal_x=focal_x, focal_y=focal_y)

        # World point under same screen focal after zoom
        world_x_after, world_y_after = self.camera.screen_to_world(focal_x, focal_y)

        self.assertAlmostEqual(world_x_before, world_x_after, places=4)
        self.assertAlmostEqual(world_y_before, world_y_after, places=4)

        # Screen point of that world position must remain exactly focal_x, focal_y
        sx, sy = self.camera.world_to_screen(world_x_before, world_y_before)
        self.assertAlmostEqual(sx, focal_x, places=4)
        self.assertAlmostEqual(sy, focal_y, places=4)

    def test_zoom_clamping_boundaries(self):
        """Verifies min_zoom (0.25) and max_zoom (4.0) bounds enforcement."""
        self.camera.set_zoom_immediate(0.05)
        self.assertAlmostEqual(self.camera.current_zoom, 0.25, places=4)

        self.camera.set_zoom_immediate(10.0)
        self.assertAlmostEqual(self.camera.current_zoom, 4.0, places=4)

    def test_orthographic_matrix_4x4_ndc_mapping(self):
        """Verifies 4x4 matrix projects viewport corners correctly to NDC [-1, 1]."""
        self.camera.set_zoom_immediate(1.5, focal_x=640.0, focal_y=360.0)
        mat = self.camera.get_orthographic_matrix_4x4()

        self.assertEqual(len(mat), 16)
        self.assertEqual(mat[15], 1.0)  # m33

        # Test vertex transform helper: v_ndc = M * v_world
        def project_world(wx, wy):
            x_ndc = mat[0] * wx + mat[12]
            y_ndc = mat[5] * wy + mat[13]
            return x_ndc, y_ndc

        # World bounds corresponding to screen corners (0,0) and (W, H)
        w_left, w_top = self.camera.screen_to_world(0.0, 0.0)
        w_right, w_bottom = self.camera.screen_to_world(self.viewport_w, self.viewport_h)

        ndc_l, ndc_t = project_world(w_left, w_top)
        ndc_r, ndc_b = project_world(w_right, w_bottom)

        # Top (wy = w_top) projects to NDC +1.0 in WebGL (top = +1, bottom = -1)
        # Left (wx = w_left) projects to NDC -1.0, Right to +1.0
        self.assertAlmostEqual(ndc_l, -1.0, places=3)
        self.assertAlmostEqual(ndc_t, 1.0, places=3)
        self.assertAlmostEqual(ndc_r, 1.0, places=3)
        self.assertAlmostEqual(ndc_b, -1.0, places=3)

    def test_spring_smooth_zoom_decay(self):
        """Verifies Symplectic Euler spring dynamics settle cleanly at target zoom."""
        self.camera.current_zoom = 1.0
        self.camera.set_target_zoom(2.0)

        dt = 0.016  # 60 FPS
        active = True
        steps = 0
        while active and steps < 300:
            active = self.camera.step_spring_zoom(dt)
            steps += 1

        self.assertFalse(active)
        self.assertAlmostEqual(self.camera.current_zoom, 2.0, places=4)
        self.assertAlmostEqual(self.camera.zoom_velocity, 0.0, places=4)

    def test_touch_lifecycle_controller_manifest(self):
        """Verifies full touch sequence (start -> move -> end) and sync manifest."""
        t1 = TouchPoint(id=0, x=200.0, y=300.0)
        t2 = TouchPoint(id=1, x=400.0, y=300.0)  # Initial dist = 200
        self.controller.on_touch_start(t1, t2)

        # Move fingers apart to dist = 300 -> 1.5x zoom
        t1_moved = TouchPoint(id=0, x=150.0, y=300.0)
        t2_moved = TouchPoint(id=1, x=450.0, y=300.0)
        manifest = self.controller.on_touch_move(t1_moved, t2_moved)

        self.assertAlmostEqual(manifest.zoom_scale, 1.5, places=4)
        self.assertLess(manifest.subpixel_drift, 1e-4)
        self.assertTrue("matrix3d" in manifest.dom_css_transform)
        self.assertEqual(len(manifest.webgl_ortho_matrix), 16)

        self.controller.on_touch_end()
        self.assertIsNone(self.controller._initial_gesture_state)

    def test_wheel_zoom_focal_manifest(self):
        """Verifies desktop mouse wheel zooming with sub-pixel sync accuracy."""
        manifest = self.controller.on_wheel_zoom(delta_wheel=-100.0, focal_x=500.0, focal_y=250.0)
        self.assertGreater(manifest.zoom_scale, 1.0)
        self.assertLess(manifest.subpixel_drift, 1e-4)


if __name__ == '__main__':
    unittest.main()
