"""
Unit tests for Dynamic Canvas Glyph Texture Atlas & High-DPI Instanced Text Rendering (UIUX-023).
"""

import unittest
from glyph_texture_atlas import (
    GlyphMetric,
    TextQuadInstance,
    DynamicGlyphTextureAtlas,
    InstancedTextLayoutEngine,
    InstancedTextQuadBufferGenerator,
    GlyphAtlasGridIntegration,
    TEXT_INSTANCE_STRIDE_BYTES
)


class TestGlyphTextureAtlasAndTextRendering(unittest.TestCase):
    def setUp(self):
        self.atlas = DynamicGlyphTextureAtlas(
            atlas_width=512,
            atlas_height=512,
            padding=1,
            font_size=14,
            dpr=2.0
        )
        self.layout_engine = InstancedTextLayoutEngine(self.atlas)
        self.generator = InstancedTextQuadBufferGenerator()

    def test_atlas_initialization_and_ascii_preseed(self):
        # ASCII printable 32 to 126 pre-seeded
        self.assertGreaterEqual(self.atlas.total_packed_glyphs, 95)
        # Check standard glyphs 'A', '0', 'z'
        metric_a = self.atlas.glyphs.get('A')
        self.assertIsNotNone(metric_a)
        self.assertEqual(metric_a.char, 'A')
        self.assertGreater(metric_a.width, 0)
        self.assertGreater(metric_a.height, 0)
        self.assertGreater(metric_a.advance_width, 0.0)

        # UV coordinates must be normalized within [0.0, 1.0]
        self.assertGreaterEqual(metric_a.uv_u, 0.0)
        self.assertLessEqual(metric_a.uv_u + metric_a.uv_w, 1.0)
        self.assertGreaterEqual(metric_a.uv_v, 0.0)
        self.assertLessEqual(metric_a.uv_v + metric_a.uv_h, 1.0)

    def test_dynamic_glyph_packing_and_caching(self):
        initial_count = self.atlas.total_packed_glyphs
        # Insert unicode non-ascii currency symbol '€'
        metric_euro = self.atlas.get_or_insert_glyph('€')
        self.assertEqual(metric_euro.char, '€')
        self.assertEqual(self.atlas.total_packed_glyphs, initial_count + 1)

        # Re-fetching must return cached metric without incrementing
        metric_cached = self.atlas.get_or_insert_glyph('€')
        self.assertEqual(metric_cached.atlas_x, metric_euro.atlas_x)
        self.assertEqual(self.atlas.total_packed_glyphs, initial_count + 1)

    def test_atlas_shelf_overflow_rejection(self):
        # Small atlas 64x64 without pre-seeding to test shelf packing overflow rejection
        small_atlas = DynamicGlyphTextureAtlas(
            atlas_width=64,
            atlas_height=64,
            padding=2,
            font_size=16,
            dpr=1.0,
            preseed_ascii=False
        )
        # Packing larger set of characters must reliably trigger OverflowError
        with self.assertRaises(OverflowError):
            for code in range(32, 128):
                small_atlas.get_or_insert_glyph(chr(code))

    def test_text_layout_engine_alignment_and_vertical_centering(self):
        # Cell: 100x30, text: "ABC"
        quads_left = self.layout_engine.layout_cell_text(
            text="ABC",
            cell_x=50.0,
            cell_y=100.0,
            cell_w=120.0,
            cell_h=30.0,
            padding_x=8.0,
            align="left"
        )
        self.assertEqual(len(quads_left), 3)
        # First character starts at cell_x + padding_x = 58.0
        self.assertAlmostEqual(quads_left[0].x, 58.0)
        # Characters advance strictly to the right
        self.assertGreater(quads_left[1].x, quads_left[0].x)
        self.assertGreater(quads_left[2].x, quads_left[1].x)

        # Center alignment
        quads_center = self.layout_engine.layout_cell_text(
            text="ABC",
            cell_x=50.0,
            cell_y=100.0,
            cell_w=120.0,
            cell_h=30.0,
            align="center"
        )
        self.assertEqual(len(quads_center), 3)
        self.assertGreater(quads_center[0].x, quads_left[0].x)

    def test_text_layout_truncation_with_ellipsis(self):
        # Small cell 40x25 with long text -> must truncate and append '...'
        quads = self.layout_engine.layout_cell_text(
            text="VERY_LONG_COLUMN_IDENTIFIER_EXTREME",
            cell_x=0.0,
            cell_y=0.0,
            cell_w=50.0,
            cell_h=25.0,
            padding_x=4.0
        )
        self.assertGreater(len(quads), 3)
        chars = [q.char for q in quads]
        self.assertEqual(chars[-3:], ['.', '.', '.'])

    def test_binary_text_vbo_packing_and_stride(self):
        quads = [
            TextQuadInstance(
                char='X',
                x=10.0,
                y=15.0,
                width=8.0,
                height=14.0,
                uv_u=0.1,
                uv_v=0.2,
                uv_w=0.05,
                uv_h=0.08,
                color=(255, 0, 0, 255),
                clip_bounds=(0.0, 0.0, 500.0, 500.0)
            ),
            TextQuadInstance(
                char='Y',
                x=18.0,
                y=15.0,
                width=8.0,
                height=14.0,
                uv_u=0.15,
                uv_v=0.2,
                uv_w=0.05,
                uv_h=0.08,
                color=(0, 255, 0, 255),
                clip_bounds=(0.0, 0.0, 500.0, 500.0)
            )
        ]

        raw_vbo = self.generator.pack_text_quads(quads)
        self.assertEqual(len(raw_vbo), 2 * TEXT_INSTANCE_STRIDE_BYTES)
        self.assertEqual(TEXT_INSTANCE_STRIDE_BYTES, 56)

        # Unpack index 0
        unpacked_0 = self.generator.unpack_text_quad(raw_vbo, 0)
        self.assertAlmostEqual(unpacked_0["x"], 10.0)
        self.assertAlmostEqual(unpacked_0["y"], 15.0)
        self.assertAlmostEqual(unpacked_0["width"], 8.0)
        self.assertAlmostEqual(unpacked_0["height"], 14.0)
        self.assertAlmostEqual(unpacked_0["uv"][0], 0.1)
        self.assertEqual(unpacked_0["color"], (255, 0, 0, 255))
        self.assertEqual(unpacked_0["clip_bounds"], (0.0, 0.0, 500.0, 500.0))

        # Unpack index 1
        unpacked_1 = self.generator.unpack_text_quad(raw_vbo, 1)
        self.assertAlmostEqual(unpacked_1["x"], 18.0)
        self.assertEqual(unpacked_1["color"], (0, 255, 0, 255))

    def test_glyph_atlas_grid_integration_batch(self):
        integration = GlyphAtlasGridIntegration(
            atlas_width=1024,
            atlas_height=1024,
            font_size=13,
            dpr=2.0
        )

        cell_strings = [
            (1, 0.0, 0.0, 100.0, 30.0, "Revenue", False),
            (2, 100.0, 0.0, 120.0, 30.0, "Gross Profit", False),
            (99, 220.0, 0.0, 240.0, 60.0, "ANNUAL QUARTERLY REPORT SPAN", True) # Merged cell
        ]

        batch = integration.generate_cell_text_batch(
            cell_strings=cell_strings,
            clip_bounds=(0.0, 0.0, 1920.0, 1080.0)
        )

        self.assertGreater(batch["text_instance_count"], 25)
        self.assertEqual(batch["stride_bytes"], 56)
        self.assertEqual(batch["vbo_byte_length"], batch["text_instance_count"] * 56)
        self.assertEqual(len(batch["binary_vbo"]), batch["vbo_byte_length"])
        self.assertGreater(batch["atlas_occupancy"], 0.0)
        self.assertLessEqual(batch["atlas_occupancy"], 1.0)


if __name__ == '__main__':
    unittest.main()
