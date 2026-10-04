import unittest
import time
from typography_buffer import StreamingTypographyBuffer, cubic_bezier


class TestStreamingTypographyBuffer(unittest.TestCase):
    def setUp(self):
        self.buffer = StreamingTypographyBuffer(
            fade_duration_ms=60.0,
            bezier_params=(0.25, 0.1, 0.25, 1.0),
            container_width_px=300.0
        )

    def test_cubic_bezier_bounds(self):
        # t=0 -> 0, t=1 -> 1, monotonic in range
        self.assertAlmostEqual(cubic_bezier(0.25, 0.1, 0.25, 1.0, 0.0), 0.0)
        self.assertAlmostEqual(cubic_bezier(0.25, 0.1, 0.25, 1.0, 1.0), 1.0)
        val_mid = cubic_bezier(0.25, 0.1, 0.25, 1.0, 0.5)
        self.assertGreaterEqual(val_mid, 0.0)
        self.assertLessEqual(val_mid, 1.0)

    def test_token_smooth_fade_progression(self):
        t0 = 1000.0
        node = self.buffer.push_token("Hermes", timestamp=t0)
        
        # Frame at t0 (0ms) -> opacity should be 0.0
        states_0 = self.buffer.advance_frame(t0)
        self.assertEqual(len(states_0), 1)
        self.assertAlmostEqual(states_0[0]["opacity"], 0.0, places=2)
        
        # Frame at t0 + 30ms (50% elapsed) -> opacity should increase
        states_mid = self.buffer.advance_frame(t0 + 0.030)
        self.assertGreater(states_mid[0]["opacity"], 0.0)
        self.assertLess(states_mid[0]["opacity"], 1.0)
        
        # Frame at t0 + 65ms (> 100% elapsed) -> fully committed
        states_end = self.buffer.advance_frame(t0 + 0.065)
        self.assertEqual(len(states_end), 1)
        self.assertAlmostEqual(states_end[0]["opacity"], 1.0, places=2)
        self.assertTrue(states_end[0]["completed"])
        
        # Next frame should show empty in-flight queue
        states_next = self.buffer.advance_frame(t0 + 0.080)
        self.assertEqual(len(states_next), 0)
        self.assertEqual(len(self.buffer.committed_nodes), 1)

    def test_layout_shift_bounded_cls(self):
        # Injeksi kalimat panjang beruntun untuk memicu line wrap
        tokens = ["Sistem ", "penalaran ", "otonom ", "Hermes ", "Agent ", "beroperasi ", "efisien."]
        t = 1000.0
        for tok in tokens:
            self.buffer.push_token(tok, timestamp=t)
            t += 0.02
        
        telemetry = self.buffer.get_layout_telemetry()
        # Verifikasi line count bertambah secara deterministik
        self.assertGreater(telemetry["line_count"], 1)
        # Verifikasi CLS (Cumulative Layout Shift) tetap terkontrol ketat (< 0.05)
        self.assertLess(telemetry["cumulative_cls"], 0.05)

    def test_dynamic_font_weight_burst(self):
        t = 2000.0
        # Fast burst: token datang setiap 15ms (< 35ms threshold)
        for _ in range(5):
            self.buffer.push_token("word ", timestamp=t)
            t += 0.015
        
        node = self.buffer.push_token("fast", timestamp=t)
        self.assertEqual(node.weight, 500)


if __name__ == "__main__":
    unittest.main()
