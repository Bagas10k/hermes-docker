#!/usr/bin/env python3
"""
Deterministic Unit Tests for HapticAcousticFSM.
Verifies state transitions, hysteresis bounds, haptic pulse safety invariants, and audio envelope specs.
"""

import unittest
from fsm_engine import HapticAcousticFSM, InteractionState, GestureType

class TestHapticAcousticFSM(unittest.TestCase):

    def setUp(self):
        self.fsm = HapticAcousticFSM(gesture_type=GestureType.SWIPE_DISMISS, threshold_px=100.0)

    def test_initial_state(self):
        self.assertEqual(self.fsm.current_state, InteractionState.IDLE)
        self.assertEqual(len(self.fsm.history), 1)

    def test_full_swipe_trigger_flow(self):
        # 1. Pointer Down
        state, fb = self.fsm.transition("POINTER_DOWN")
        self.assertEqual(state, InteractionState.TOUCH_START)
        self.assertIsNotNone(fb)
        self.assertEqual(fb.vibration_pattern, [8])
        self.assertAlmostEqual(fb.audio_cue.gain_peak, 0.15)

        # 2. Drag sub threshold (50px / 100px = 0.5 < 0.75)
        state, fb = self.fsm.update_drag(50.0)
        self.assertEqual(state, InteractionState.DRAGGING)
        self.assertIsNone(fb)

        # 3. Drag approach threshold (80px / 100px = 0.8 >= 0.75)
        state, fb = self.fsm.update_drag(80.0)
        self.assertEqual(state, InteractionState.THRESHOLD_APPROACH)
        self.assertIsNotNone(fb)
        self.assertEqual(fb.vibration_pattern, [12])

        # 4. Drag crossed threshold (105px / 100px = 1.05 >= 1.0)
        state, fb = self.fsm.update_drag(105.0)
        self.assertEqual(state, InteractionState.THRESHOLD_CROSSED)
        self.assertIsNotNone(fb)
        self.assertEqual(fb.vibration_pattern, [18, 20, 24])

        # 5. Pointer Up -> Action Triggered
        state, fb = self.fsm.transition("POINTER_UP")
        self.assertEqual(state, InteractionState.ACTION_TRIGGERED)
        self.assertIsNotNone(fb)
        self.assertEqual(fb.vibration_pattern, [15, 30, 25])
        self.assertEqual(fb.audio_cue.oscillator_type, "sine")

    def test_hysteresis_anti_chattering(self):
        """
        Tests that slight jitter near the threshold doesn't rapidly bounce states.
        Threshold: 100px. Fallback threshold from CROSSED requires ratio < 0.90 (90px).
        """
        self.fsm.transition("POINTER_DOWN")
        self.fsm.update_drag(80.0)  # THRESHOLD_APPROACH
        self.fsm.update_drag(102.0) # THRESHOLD_CROSSED
        self.assertEqual(self.fsm.current_state, InteractionState.THRESHOLD_CROSSED)

        # Drop to 95px (0.95 ratio) -> should stay THRESHOLD_CROSSED due to hysteresis
        state, fb = self.fsm.update_drag(95.0)
        self.assertEqual(self.fsm.current_state, InteractionState.THRESHOLD_CROSSED)
        self.assertIsNone(fb)

        # Drop to 88px (0.88 ratio < 0.90) -> should transition back to THRESHOLD_APPROACH
        state, fb = self.fsm.update_drag(88.0)
        self.assertEqual(self.fsm.current_state, InteractionState.THRESHOLD_APPROACH)

    def test_abort_and_cancel_flow(self):
        self.fsm.transition("POINTER_DOWN")
        self.fsm.update_drag(60.0)
        state, fb = self.fsm.transition("POINTER_CANCEL")
        self.assertEqual(state, InteractionState.RELEASE_CANCELLED)
        self.assertIsNotNone(fb)
        self.assertEqual(fb.vibration_pattern, [10])

        # Reset back to IDLE
        state, fb = self.fsm.transition("RESET")
        self.assertEqual(state, InteractionState.IDLE)

    def test_web_contract_export(self):
        contract = self.fsm.export_web_contract()
        self.assertIn("states", contract)
        self.assertIn("THRESHOLD_CROSSED", contract["states"])
        crossed = contract["states"]["THRESHOLD_CROSSED"]
        self.assertEqual(crossed["vibration_pattern"], [18, 20, 24])
        self.assertIn("audio_cue", crossed)
        self.assertEqual(crossed["audio_cue"]["oscillator_type"], "sine")
        self.assertAlmostEqual(contract["hysteresis_margin_px"], 10.0)

if __name__ == "__main__":
    unittest.main()
