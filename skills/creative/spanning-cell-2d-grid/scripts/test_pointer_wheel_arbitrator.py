"""Unit Tests for Virtual Pointer Wheel Gesture Arbitration & Momentum Decay (UIUX-024).

Validates:
1. Pointer wheel gesture arbitration between WebGL canvas and DOM header controls.
2. Prevention of default event leakage and double-scroll.
3. Frozen corner event veto/absorption.
4. Directional axis lock (horizontal vs vertical vs bidirectional).
5. Kinetic velocity estimation from sliding window delta samples.
6. Inertial kinetic momentum scroll decay (exponential decay).
7. Rubberband overscroll spring restitution and bounce-back.
8. Zero-CLS synchronization manifest between WebGL uniform and DOM headers (drift = 0.000px).
"""

import math
import unittest

from pointer_wheel_arbitrator import (
    GestureArbitrator,
    GesturePhase,
    KineticScrollEngine,
    PointerWheelEvent,
    ScrollAxis,
    SyncManifest,
    TargetLayer,
    VelocityEstimator,
    ViewportBoundary,
)


class TestPointerWheelArbitrationAndMomentum(unittest.TestCase):

    def setUp(self):
        self.boundary = ViewportBoundary(
            min_x=0.0,
            max_x=5000.0,
            min_y=0.0,
            max_y=20000.0,
            enable_rubberband=True,
            rubberband_stiffness=200.0,
            rubberband_damping=25.0,
        )
        self.engine = KineticScrollEngine(self.boundary, friction_decay=3.5, min_velocity_cutoff=5.0)

    def test_gesture_arbitration_and_prevent_default(self):
        """Verifies canvas and DOM header events are arbitrated and default browser scroll is prevented."""
        event_canvas = PointerWheelEvent(
            timestamp_ms=1000.0,
            delta_x=0.0,
            delta_y=25.0,
            client_x=300.0,
            client_y=400.0,
            target_layer=TargetLayer.WEBGL_CANVAS,
        )
        manifest = self.engine.handle_wheel_event(event_canvas)
        self.assertTrue(event_canvas.default_prevented)
        self.assertEqual(manifest.phase, GesturePhase.BEGAN.value)
        self.assertEqual(manifest.scroll_y, 25.0)
        self.assertEqual(manifest.drift_delta, 0.0)

    def test_frozen_corner_veto_absorption(self):
        """Verifies frozen corner absorbs pointer events without modifying grid scroll position."""
        event_corner = PointerWheelEvent(
            timestamp_ms=1050.0,
            delta_x=15.0,
            delta_y=15.0,
            client_x=20.0,
            client_y=20.0,
            target_layer=TargetLayer.FROZEN_CORNER,
        )
        manifest = self.engine.handle_wheel_event(event_corner)
        self.assertTrue(event_corner.default_prevented)
        # Position must remain unchanged at 0.0
        self.assertEqual(manifest.scroll_x, 0.0)
        self.assertEqual(manifest.scroll_y, 0.0)

    def test_axis_locking_horizontal_dominance(self):
        """Verifies dominant horizontal delta locks scroll axis and suppresses vertical jitter."""
        arbitrator = GestureArbitrator(lock_axis_threshold=5.0)

        event = PointerWheelEvent(
            timestamp_ms=1000.0,
            delta_x=30.0,
            delta_y=2.0,
            client_x=200.0,
            client_y=200.0,
            target_layer=TargetLayer.WEBGL_CANVAS,
        )
        should_handle, locked_axis = arbitrator.arbitrate(event)
        self.assertTrue(should_handle)
        self.assertEqual(locked_axis, ScrollAxis.HORIZONTAL)

    def test_axis_locking_vertical_dominance(self):
        """Verifies dominant vertical delta locks scroll axis to vertical."""
        arbitrator = GestureArbitrator(lock_axis_threshold=5.0)

        event = PointerWheelEvent(
            timestamp_ms=1000.0,
            delta_x=1.0,
            delta_y=45.0,
            client_x=200.0,
            client_y=200.0,
            target_layer=TargetLayer.DOM_HEADER,
        )
        should_handle, locked_axis = arbitrator.arbitrate(event)
        self.assertTrue(should_handle)
        self.assertEqual(locked_axis, ScrollAxis.VERTICAL)

    def test_velocity_estimator_kinetics(self):
        """Verifies sliding window velocity estimation calculates correct pixels/second."""
        estimator = VelocityEstimator(window_size=5, max_history_ms=100.0)

        # 4 samples spaced 16ms apart with 16px delta -> 1000 px/s
        t = 1000.0
        for _ in range(4):
            estimator.record_delta(t, 0.0, 16.0)
            t += 16.0

        vx, vy = estimator.get_velocity(t)
        self.assertEqual(vx, 0.0)
        self.assertAlmostEqual(vy, 1000.0, delta=20.0)

    def test_inertial_momentum_decay_simulation(self):
        """Verifies momentum velocity decays exponentially until cutoff."""
        # Initial displacement
        self.engine.handle_wheel_event(
            PointerWheelEvent(1000.0, 0.0, 20.0, 100.0, 100.0, TargetLayer.WEBGL_CANVAS)
        )
        self.engine.handle_wheel_event(
            PointerWheelEvent(1016.0, 0.0, 20.0, 100.0, 100.0, TargetLayer.WEBGL_CANVAS)
        )

        # Release gesture -> triggers momentum
        self.engine.release_gesture(1032.0)
        self.assertEqual(self.engine.state.phase, GesturePhase.MOMENTUM_BEGAN)
        self.assertTrue(self.engine.state.is_animating)
        self.assertGreater(self.engine.state.velocity_y, 500.0)

        # Step simulation forward multiple frames
        t = 1032.0
        prev_pos = self.engine.state.y
        for _ in range(30):
            t += 16.0
            manifest = self.engine.step_simulation(t)
            self.assertGreaterEqual(manifest.scroll_y, prev_pos)
            prev_pos = manifest.scroll_y
            self.assertEqual(manifest.drift_delta, 0.0)

        # Verify deceleration occurred
        self.assertLess(self.engine.state.velocity_y, 500.0)

    def test_overscroll_rubberband_spring_restitution(self):
        """Verifies overscroll position bounces back to boundary limit via spring physics."""
        # Pull past boundary min_y (0.0) into negative territory
        for i in range(5):
            self.engine.handle_wheel_event(
                PointerWheelEvent(
                    1000.0 + i * 16.0,
                    0.0,
                    -25.0,
                    100.0,
                    100.0,
                    TargetLayer.WEBGL_CANVAS,
                )
            )

        manifest = self.engine.get_sync_manifest()
        self.assertTrue(manifest.is_in_overscroll)
        self.assertLess(manifest.scroll_y, 0.0)

        # Release and step simulation -> rubberband spring should pull back to >= 0.0
        self.engine.release_gesture(1100.0)
        t = 1100.0
        for _ in range(60):
            t += 16.0
            self.engine.step_simulation(t)

        final_manifest = self.engine.get_sync_manifest()
        # Should have settled back at 0.0 bound
        self.assertAlmostEqual(final_manifest.scroll_y, 0.0, delta=0.1)
        self.assertFalse(final_manifest.is_in_overscroll)
        self.assertEqual(final_manifest.phase, GesturePhase.ENDED.value)
        self.assertEqual(final_manifest.drift_delta, 0.0)

    def test_zero_cls_bidirectional_sync_manifest(self):
        """Verifies strict 0.000px drift between WebGL uniform and DOM header tracking."""
        # Arbitrary diagonal pan
        self.engine.handle_wheel_event(
            PointerWheelEvent(1000.0, 123.456, 789.012, 100.0, 100.0, TargetLayer.WEBGL_CANVAS)
        )
        manifest = self.engine.get_sync_manifest()

        self.assertEqual(manifest.dom_header_x, manifest.webgl_uniform_x)
        self.assertEqual(manifest.dom_header_y, manifest.webgl_uniform_y)
        self.assertEqual(manifest.drift_delta, 0.0)


if __name__ == "__main__":
    unittest.main()
