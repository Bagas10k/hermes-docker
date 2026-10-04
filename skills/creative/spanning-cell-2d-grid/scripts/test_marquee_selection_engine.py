"""
Deterministic unit tests for GPU-Accelerated Cell Selection Box & Marquee Drag Math (UIUX-027).
"""

import struct
import unittest
from marquee_selection_engine import (
    MarqueeSelectionEngine,
    SelectionRect,
    CellRange,
    SELECTION_BOX_INSTANCE_STRIDE_BYTES
)


class TestMarqueeSelectionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = MarqueeSelectionEngine(
            default_row_height=30.0,
            default_col_width=120.0,
            viewport_width=1280.0,
            viewport_height=720.0
        )

    def test_screen_to_world_and_inverse_invariance(self):
        # 1:1 camera at origin
        self.engine.update_camera(scroll_x=0.0, scroll_y=0.0, zoom=1.0)
        wx, wy = self.engine.screen_to_world(240.0, 150.0)
        self.assertAlmostEqual(wx, 240.0)
        self.assertAlmostEqual(wy, 150.0)
        sx, sy = self.engine.world_to_screen(wx, wy)
        self.assertAlmostEqual(sx, 240.0)
        self.assertAlmostEqual(sy, 150.0)

        # Scrolled and zoomed camera
        # zoom = 2.0, scroll = (100, 50)
        self.engine.update_camera(scroll_x=100.0, scroll_y=50.0, zoom=2.0)
        screen_pt = (300.0, 200.0)
        wx, wy = self.engine.screen_to_world(screen_pt[0], screen_pt[1])
        # wx = 100 + 300 / 2 = 250
        # wy = 50 + 200 / 2 = 150
        self.assertAlmostEqual(wx, 250.0)
        self.assertAlmostEqual(wy, 150.0)

        # Roundtrip back to screen
        sx, sy = self.engine.world_to_screen(wx, wy)
        self.assertAlmostEqual(sx, screen_pt[0])
        self.assertAlmostEqual(sy, screen_pt[1])

    def test_cell_bounds_and_spatial_mapping(self):
        # Cell (row=2, col=3) with height=30, width=120
        bounds = self.engine.cell_to_world_bounds(row=2, col=3)
        self.assertEqual(bounds.min_x, 360.0)
        self.assertEqual(bounds.min_y, 60.0)
        self.assertEqual(bounds.max_x, 480.0)
        self.assertEqual(bounds.max_y, 90.0)
        self.assertEqual(bounds.width, 120.0)
        self.assertEqual(bounds.height, 30.0)

        # Query point inside cell
        r, c = self.engine.world_to_cell(400.0, 75.0)
        self.assertEqual(r, 2)
        self.assertEqual(c, 3)

    def test_marquee_drag_lifecycle_forward_and_backward(self):
        self.engine.update_camera(scroll_x=0.0, scroll_y=0.0, zoom=1.0)

        # Start drag at (10, 10) -> Cell (0, 0)
        self.engine.start_drag(10.0, 10.0)
        self.assertTrue(self.engine.is_dragging)
        self.assertEqual(self.engine.active_cell, (0, 0))

        # Drag forward to (260, 70) -> Col = 260 // 120 = 2, Row = 70 // 30 = 2
        m_rect = self.engine.update_drag(260.0, 70.0)
        self.assertIsNotNone(m_rect)
        self.assertEqual(m_rect.min_x, 10.0)
        self.assertEqual(m_rect.min_y, 10.0)
        self.assertEqual(m_rect.max_x, 260.0)
        self.assertEqual(m_rect.max_y, 70.0)

        # Intersected cell range
        cell_range = self.engine.compute_intersected_cell_range()
        self.assertIsNotNone(cell_range)
        self.assertEqual(cell_range.start_row, 0)
        self.assertEqual(cell_range.start_col, 0)
        self.assertEqual(cell_range.end_row, 2)
        self.assertEqual(cell_range.end_col, 2)

        # End drag
        final_range = self.engine.end_drag()
        self.assertFalse(self.engine.is_dragging)
        self.assertEqual(final_range, CellRange(0, 0, 2, 2))
        self.assertEqual(final_range.count(), 9)

        # Now test backward drag: start at (250, 80), drag up-left to (50, 20)
        self.engine.start_drag(250.0, 80.0)
        r_start, c_start = self.engine.active_cell
        self.assertEqual(r_start, 2)
        self.assertEqual(c_start, 2)

        b_rect = self.engine.update_drag(50.0, 20.0)
        self.assertIsNotNone(b_rect)
        # Should be normalized min_x <= max_x
        self.assertEqual(b_rect.min_x, 50.0)
        self.assertEqual(b_rect.min_y, 20.0)
        self.assertEqual(b_rect.max_x, 250.0)
        self.assertEqual(b_rect.max_y, 80.0)

        backward_range = self.engine.end_drag()
        self.assertEqual(backward_range, CellRange(0, 0, 2, 2))

    def test_rect_collision_and_containment(self):
        r1 = SelectionRect(0.0, 0.0, 100.0, 100.0)
        r2 = SelectionRect(50.0, 50.0, 150.0, 150.0)
        r3 = SelectionRect(101.0, 101.0, 200.0, 200.0)

        self.assertTrue(r1.intersects(r2))
        self.assertTrue(r2.intersects(r1))
        self.assertFalse(r1.intersects(r3))

        self.assertTrue(r1.contains_point(50.0, 50.0))
        self.assertFalse(r1.contains_point(150.0, 50.0))

    def test_gpu_instanced_selection_box_packing(self):
        rect = SelectionRect(120.0, 30.0, 360.0, 90.0)
        instance_bytes = self.engine.build_gpu_selection_instance(
            rect=rect,
            border_width=2.5,
            corner_radius=4.0,
            fill_opacity=0.2,
            stroke_opacity=1.0,
            color_rgb=(0.2, 0.6, 1.0),
            is_active=True
        )

        self.assertEqual(len(instance_bytes), SELECTION_BOX_INSTANCE_STRIDE_BYTES)

        # Unpack and verify IEEE 754 float32 precision
        unpacked = struct.unpack('<4f4f4f', instance_bytes)
        # Bounding box
        self.assertAlmostEqual(unpacked[0], 120.0)
        self.assertAlmostEqual(unpacked[1], 30.0)
        self.assertAlmostEqual(unpacked[2], 360.0)
        self.assertAlmostEqual(unpacked[3], 90.0)
        # Style
        self.assertAlmostEqual(unpacked[4], 2.5)
        self.assertAlmostEqual(unpacked[5], 4.0)
        self.assertAlmostEqual(unpacked[6], 0.2)
        self.assertAlmostEqual(unpacked[7], 1.0)
        # Color & Active flag
        self.assertAlmostEqual(unpacked[8], 0.2)
        self.assertAlmostEqual(unpacked[9], 0.6)
        self.assertAlmostEqual(unpacked[10], 1.0)
        self.assertAlmostEqual(unpacked[11], 1.0)

    def test_combined_active_selection_and_marquee_serialization(self):
        self.engine.update_camera(scroll_x=50.0, scroll_y=20.0, zoom=1.5)
        self.engine.start_drag(100.0, 100.0)
        self.engine.update_drag(400.0, 300.0)

        buffer_bytes = self.engine.serialize_active_selection_instances()
        # Must serialize exactly 2 instances: 1 active cell range box + 1 dynamic marquee drag box
        expected_size = SELECTION_BOX_INSTANCE_STRIDE_BYTES * 2
        self.assertEqual(len(buffer_bytes), expected_size)

        # First instance is active selection range
        inst1 = struct.unpack('<4f4f4f', buffer_bytes[:48])
        self.assertEqual(inst1[11], 1.0)  # is_active = 1.0

        # Second instance is dynamic marquee
        inst2 = struct.unpack('<4f4f4f', buffer_bytes[48:])
        self.assertEqual(inst2[11], 0.0)  # is_active = 0.0 for marquee

        # End drag -> now only 1 instance (selected range) should remain
        self.engine.end_drag()
        buffer_post_drag = self.engine.serialize_active_selection_instances()
        self.assertEqual(len(buffer_post_drag), SELECTION_BOX_INSTANCE_STRIDE_BYTES)


if __name__ == '__main__':
    unittest.main()
