"""
Unit tests for Signed Distance Field (SDF / MSDF) Glyph Rendering Matrix Integration (UIUX-026).
"""

import unittest
from sdf_glyph_renderer import (
    SDFDynamicGlyphAtlas,
    SDFMatrixShaderIntegrator,
    MSDFTextQuad,
    median3,
    evaluate_msdf_sample,
    evaluate_sdf_sample,
    MSDF_TEXT_INSTANCE_STRIDE_BYTES
)


class TestSDFGlyphRenderer(unittest.TestCase):
    def setUp(self):
        self.atlas = SDFDynamicGlyphAtlas(
            atlas_width=512,
            atlas_height=512,
            distance_range=4.0,
            font_size=32
        )
        self.integrator = SDFMatrixShaderIntegrator(self.atlas)

    def test_median3_corner_preservation(self):
        # Median of (0.2, 0.5, 0.8) is 0.5
        self.assertAlmostEqual(median3(0.2, 0.5, 0.8), 0.5)
        self.assertAlmostEqual(median3(0.8, 0.2, 0.5), 0.5)
        self.assertAlmostEqual(median3(0.5, 0.8, 0.2), 0.5)
        # Identical channels
        self.assertAlmostEqual(median3(0.7, 0.7, 0.7), 0.7)
        # Binary step
        self.assertAlmostEqual(median3(1.0, 0.0, 1.0), 1.0)
        self.assertAlmostEqual(median3(0.0, 0.0, 1.0), 0.0)

    def test_msdf_sample_evaluation(self):
        # Exactly on the contour boundary: sd = 0.5 -> opacity should be 0.5
        sample_boundary = (0.5, 0.5, 0.5)
        opacity = evaluate_msdf_sample(sample_boundary, screen_px_range=4.0)
        self.assertAlmostEqual(opacity, 0.5)

        # Deep inside the glyph: sd = 0.9 -> opacity should be 1.0
        sample_inside = (0.9, 0.85, 0.92)
        opacity_inside = evaluate_msdf_sample(sample_inside, screen_px_range=4.0)
        self.assertEqual(opacity_inside, 1.0)

        # Deep outside the glyph: sd = 0.1 -> opacity should be 0.0
        sample_outside = (0.1, 0.05, 0.12)
        opacity_outside = evaluate_msdf_sample(sample_outside, screen_px_range=4.0)
        self.assertEqual(opacity_outside, 0.0)

    def test_screen_pixel_range_derivation(self):
        # Base distance range = 4.0
        # Zoom = 1.0 -> pxRange = 4.0
        self.assertAlmostEqual(self.integrator.calculate_screen_pixel_range(1.0), 4.0)
        # Zoom = 0.25 -> raw = 1.0 -> pxRange = 1.0 (clamped lower bound)
        self.assertAlmostEqual(self.integrator.calculate_screen_pixel_range(0.25), 1.0)
        # Zoom = 4.0 -> raw = 16.0 -> pxRange = 16.0
        self.assertAlmostEqual(self.integrator.calculate_screen_pixel_range(4.0), 16.0)
        # Extreme zoom = 10.0 -> raw = 40.0 -> clamped to 32.0 max
        self.assertAlmostEqual(self.integrator.calculate_screen_pixel_range(10.0), 32.0)

    def test_camera_uniforms_structure(self):
        uniforms = self.integrator.get_camera_uniforms(camera_zoom=2.0, camera_offset=(100.0, 50.0))
        self.assertAlmostEqual(uniforms.zoom_scale, 2.0)
        self.assertAlmostEqual(uniforms.screen_pixel_range, 8.0)
        self.assertEqual(uniforms.tex_size, (512.0, 512.0))
        self.assertEqual(uniforms.camera_offset, (100.0, 50.0))
        self.assertTrue(uniforms.subpixel_aa_enabled)
        self.assertAlmostEqual(uniforms.edge_value, 0.5)

    def test_cell_text_quads_layout(self):
        text = "HERMES"
        quads = self.integrator.generate_cell_text_quads(
            text=text,
            cell_x=10.0,
            cell_y=20.0,
            cell_w=200.0,
            cell_h=40.0,
            camera_zoom=1.5,
            align="center"
        )
        self.assertEqual(len(quads), len(text))
        # Quads should have increasing x positions
        for i in range(len(quads) - 1):
            self.assertLess(quads[i].x, quads[i + 1].x)
            self.assertEqual(quads[i].y, quads[i + 1].y)
            self.assertAlmostEqual(quads[i].px_range, 6.0)  # 4.0 * 1.5
            self.assertEqual(quads[i].mode, 1.0)

    def test_serialization_binary_stride(self):
        text = "API"
        quads = self.integrator.generate_cell_text_quads(
            text=text,
            cell_x=0.0,
            cell_y=0.0,
            cell_w=100.0,
            cell_h=30.0,
            camera_zoom=1.0
        )
        buf = self.integrator.serialize_quad_buffer(quads)
        expected_len = len(text) * MSDF_TEXT_INSTANCE_STRIDE_BYTES
        self.assertEqual(len(buf), expected_len)
        self.assertEqual(MSDF_TEXT_INSTANCE_STRIDE_BYTES, 68)

    def test_subpixel_aa_contrast_stability(self):
        # Compare opacity transition sharpness at zoom 0.5 vs zoom 2.0
        # Transition occurs within distance delta = 1.0 / px_range
        px_range_low = self.integrator.calculate_screen_pixel_range(0.5)   # 2.0
        px_range_high = self.integrator.calculate_screen_pixel_range(2.0)  # 8.0

        # At distance = 0.55 (0.05 inside edge):
        op_low = evaluate_msdf_sample((0.55, 0.55, 0.55), screen_px_range=px_range_low)
        op_high = evaluate_msdf_sample((0.55, 0.55, 0.55), screen_px_range=px_range_high)

        # Higher zoom provides sharper, steeper sigmoid boundary
        self.assertGreater(op_high, op_low)
        self.assertAlmostEqual(op_low, 2.0 * 0.05 + 0.5)   # 0.60
        self.assertAlmostEqual(op_high, 8.0 * 0.05 + 0.5)  # 0.90


if __name__ == "__main__":
    unittest.main()
