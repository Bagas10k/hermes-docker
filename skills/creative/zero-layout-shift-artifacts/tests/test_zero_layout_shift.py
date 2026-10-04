"""Deterministic unit tests for zero_layout_shift.py ensuring 100% test pass rate."""

import unittest
from zero_layout_shift import (
    ViewportSpec,
    SkeletonReservation,
    LayoutShiftCalculator,
    VirtualViewportManager
)


class TestZeroLayoutShift(unittest.TestCase):

    def setUp(self):
        self.spec = ViewportSpec(width=1080.0, height=1920.0, device_pixel_ratio=2.0)
        self.manager = VirtualViewportManager(self.spec)

    def test_viewport_spec_validation(self):
        self.assertAlmostEqual(self.spec.aspect_ratio, 1080.0 / 1920.0)
        with self.assertRaises(ValueError):
            bad_spec = ViewportSpec(width=100.0, height=0.0)
            _ = bad_spec.aspect_ratio

    def test_cls_zero_shift_when_positions_identical(self):
        prev_rect = {"x": 50.0, "y": 100.0, "width": 400.0, "height": 300.0}
        curr_rect = {"x": 50.0, "y": 100.0, "width": 400.0, "height": 300.0}
        shift = LayoutShiftCalculator.calculate_shift(1080.0, 1920.0, prev_rect, curr_rect)
        self.assertEqual(shift, 0.0)

    def test_cls_positive_shift_on_layout_jump(self):
        prev_rect = {"x": 0.0, "y": 100.0, "width": 500.0, "height": 200.0}
        curr_rect = {"x": 0.0, "y": 300.0, "width": 500.0, "height": 200.0} # 200px jump downward
        shift = LayoutShiftCalculator.calculate_shift(1000.0, 1000.0, prev_rect, curr_rect)
        self.assertGreater(shift, 0.0)
        # Verify deterministic calculation
        # union y: 100 to 500 = 400h * 500w = 200,000 area. vp_area = 1,000,000. impact = 0.2
        # distance: 200 / 1000 = 0.2. shift = 0.04
        self.assertAlmostEqual(shift, 0.04, places=4)

    def test_skeleton_reservation_dimension_clamping(self):
        res = SkeletonReservation(
            component_id="hero-card",
            min_width=320.0,
            min_height=200.0,
            aspect_ratio=16.0 / 9.0
        )
        dims = res.compute_clamped_dimensions(parent_width=1600.0)
        self.assertEqual(dims["width"], 1600.0)
        self.assertEqual(dims["height"], 900.0)

        # Test small parent width clamped to min_width (320px). Aspect ratio 16/9 gives 180, clamped to min_height 200.0
        dims_small = res.compute_clamped_dimensions(parent_width=200.0)
        self.assertEqual(dims_small["width"], 320.0)
        self.assertEqual(dims_small["height"], 200.0)

    def test_sandbox_container_css_generation(self):
        res = SkeletonReservation(
            component_id="live-preview-widget",
            min_width=400.0,
            min_height=300.0,
            aspect_ratio=4.0 / 3.0
        )
        self.manager.register_reservation(res)
        result = self.manager.generate_sandbox_container_css("live-preview-widget", parent_width=800.0)

        self.assertEqual(result["computed_dimensions"]["width"], 800.0)
        self.assertEqual(result["computed_dimensions"]["height"], 600.0)
        css = result["css"]
        self.assertEqual(css["contain"], "paint layout style size")
        self.assertEqual(css["overflow"], "hidden")
        self.assertEqual(css["content-visibility"], "auto")

    def test_iframe_sandbox_html_integrity(self):
        res = SkeletonReservation(
            component_id="canvas-box",
            min_width=500.0,
            min_height=500.0,
            aspect_ratio=1.0
        )
        self.manager.register_reservation(res)
        html = self.manager.generate_iframe_sandbox_html(
            component_id="canvas-box",
            content_srcdoc="<h1>Live Preview</h1>",
            parent_width=500.0
        )
        self.assertIn('id="sandbox-wrapper-canvas-box"', html)
        self.assertIn('sandbox="allow-scripts"', html)
        self.assertIn('contain: paint layout style size', html)
        self.assertIn('srcdoc="<h1>Live Preview</h1>"', html)

    def test_virtual_paging_calculation(self):
        # 100 items, each 50px tall. Viewport height = 1920. visible_count = ceil(1920/50) = 39
        paging = self.manager.calculate_virtual_paging(
            item_count=100,
            item_height=50.0,
            scroll_y=500.0,
            overscan_count=2
        )
        self.assertEqual(paging["start_index"], 8) # floor(500/50) - 2 = 10 - 2 = 8
        self.assertGreater(paging["end_index"], paging["start_index"])
        self.assertEqual(paging["total_height"], 5000.0)
        self.assertEqual(paging["top_padding"], 400.0) # 8 * 50 = 400


if __name__ == "__main__":
    unittest.main()
