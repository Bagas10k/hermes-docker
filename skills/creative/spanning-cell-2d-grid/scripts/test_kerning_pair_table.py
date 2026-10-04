"""
Unit tests for Sub-Pixel Glyph Kerning Pairs Table Integration (UIUX-029).
"""

import unittest
import struct
from kerning_pair_table import (
    KerningPairTable,
    KerningAwareGlyphRenderer,
    STANDARD_KERNING_PAIRS
)
from sdf_glyph_renderer import SDFDynamicGlyphAtlas, MSDF_TEXT_INSTANCE_STRIDE_BYTES


class TestKerningPairTable(unittest.TestCase):
    def setUp(self):
        self.table = KerningPairTable(base_font_size=32.0)

    def test_standard_pairs_lookup(self):
        # 'AV' is a standard contracting kerning pair (-3.0)
        kern_av = self.table.get_kern('A', 'V')
        self.assertAlmostEqual(kern_av, -3.0, places=3)
        
        # 'To' is a contracting pair (-2.0)
        kern_to = self.table.get_kern('T', 'o')
        self.assertAlmostEqual(kern_to, -2.0, places=3)

        # Unrelated pair returns 0.0
        kern_xy = self.table.get_kern('X', 'Y')
        self.assertEqual(kern_xy, 0.0)

    def test_font_size_scaling(self):
        # Base font size = 32.0. At 64.0 (2x), kern amount should double (-6.0)
        scaled_kern = self.table.get_kern('A', 'V', font_size=64.0)
        self.assertAlmostEqual(scaled_kern, -6.0, places=3)

        # At 16.0 (0.5x), kern amount should halve (-1.5)
        scaled_kern_half = self.table.get_kern('A', 'V', font_size=16.0)
        self.assertAlmostEqual(scaled_kern_half, -1.5, places=3)

    def test_custom_pair_mutation(self):
        # Register custom pair
        self.table.set_pair('Q', 'j', 4.5)
        self.assertAlmostEqual(self.table.get_kern('Q', 'j'), 4.5, places=3)

        # Remove pair
        removed = self.table.remove_pair('Q', 'j')
        self.assertTrue(removed)
        self.assertEqual(self.table.get_kern('Q', 'j'), 0.0)

    def test_enable_disable_toggle(self):
        self.table.enabled = False
        self.assertEqual(self.table.get_kern('A', 'V'), 0.0)
        self.table.enabled = True
        self.assertAlmostEqual(self.table.get_kern('A', 'V'), -3.0, places=3)

    def test_binary_gpos_serialization_roundtrip(self):
        binary_data = self.table.export_binary_gpos()
        self.assertIsInstance(binary_data, bytearray)
        self.assertGreater(len(binary_data), 8)

        # Re-import and verify parity
        imported_table = KerningPairTable.import_binary_gpos(bytes(binary_data))
        self.assertEqual(imported_table.pair_count, self.table.pair_count)
        self.assertAlmostEqual(imported_table.get_kern('A', 'V'), -3.0, places=3)
        self.assertAlmostEqual(imported_table.get_kern('W', 'a'), -1.5, places=3)


class TestKerningAwareGlyphRenderer(unittest.TestCase):
    def setUp(self):
        self.atlas = SDFDynamicGlyphAtlas(font_size=32)
        self.renderer = KerningAwareGlyphRenderer(atlas=self.atlas)

    def test_string_width_reduction_with_kerning(self):
        text = "AVATAR"
        width_kerning = self.renderer.calculate_string_width(text)
        
        # Disable kerning and verify string width is larger
        self.renderer.kerning_table.enabled = False
        width_no_kerning = self.renderer.calculate_string_width(text)
        
        self.assertGreater(width_no_kerning, width_kerning)
        # Expected reduction from pairs: 'AV' (-3.0), 'VA' (-3.0), 'AT' (-2.7), 'TA' (-2.7) = -11.4 px
        diff = width_no_kerning - width_kerning
        self.assertAlmostEqual(diff, 11.4, places=2)

    def test_cell_quad_generation_with_subpixel_positions(self):
        text = "AV"
        quads = self.renderer.generate_cell_text_quads(
            text=text,
            cell_x=100.0,
            cell_y=50.0,
            cell_w=200.0,
            cell_h=40.0,
            camera_zoom=1.0,
            align="left"
        )
        self.assertEqual(len(quads), 2)
        q_a, q_v = quads[0], quads[1]

        # First char 'A' start_x = 100.0 + 8.0 = 108.0
        self.assertAlmostEqual(q_a.x, 108.0, places=3)
        
        # Second char 'V' should be placed at q_a.x + advance_a + kern('A', 'V')
        metric_a = self.atlas.allocate_glyph('A')
        expected_v_x = 108.0 + metric_a.advance_width - 3.0
        self.assertAlmostEqual(q_v.x, expected_v_x, places=3)

    def test_binary_quad_buffer_stride_compliance(self):
        quads = self.renderer.generate_cell_text_quads(
            text="Total: $1,000",
            cell_x=0.0,
            cell_y=0.0,
            cell_w=300.0,
            cell_h=30.0,
            camera_zoom=1.5
        )
        buffer = self.renderer.serialize_quad_buffer(quads)
        expected_bytes = len(quads) * MSDF_TEXT_INSTANCE_STRIDE_BYTES
        self.assertEqual(len(buffer), expected_bytes)


if __name__ == "__main__":
    unittest.main()
