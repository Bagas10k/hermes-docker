"""
Unit tests for WebGL/WebGPU Instanced Quad Rendering Fallback for Massive Cell Budgets (UIUX-022).
"""

import unittest
from gpu_instanced_grid import (
    InstancedCell,
    GridRenderPipelineDecider,
    InstancedQuadBufferGenerator,
    GpuInstancedGridPipeline,
    INSTANCE_STRIDE_BYTES,
    DOM_BUDGET_CEILING
)

class TestGpuInstancedQuadFallback(unittest.TestCase):
    def setUp(self):
        self.decider = GridRenderPipelineDecider(dom_ceiling=4096)
        self.generator = InstancedQuadBufferGenerator()

    def test_instanced_cell_validation(self):
        # Valid cell
        cell = InstancedCell(
            cell_id=101,
            x=10.0,
            y=20.0,
            width=100.0,
            height=30.0,
            bg_color=(255, 255, 255, 255),
            border_color=(0, 0, 0),
            border_width=1
        )
        self.assertEqual(cell.cell_id, 101)
        self.assertEqual(cell.width, 100.0)

        # Invalid dimensions
        with self.assertRaises(ValueError):
            InstancedCell(cell_id=1, x=0, y=0, width=0.0, height=30.0)
        with self.assertRaises(ValueError):
            InstancedCell(cell_id=1, x=0, y=0, width=50.0, height=-10.0)

        # Invalid colors out of [0, 255]
        with self.assertRaises(ValueError):
            InstancedCell(cell_id=1, x=0, y=0, width=50, height=30, bg_color=(256, 0, 0, 255))
        with self.assertRaises(ValueError):
            InstancedCell(cell_id=1, x=0, y=0, width=50, height=30, border_color=(0, -1, 0))

    def test_render_strategy_decision_bounds(self):
        # Within budget -> DOM
        d1 = self.decider.evaluate(active_cells=1024, dpr=1.0)
        self.assertEqual(d1.mode, "DOM")
        self.assertEqual(d1.active_cell_count, 1024)
        self.assertLess(d1.estimated_dom_cost_ms, 16.6)

        # Exactly at ceiling -> DOM
        d2 = self.decider.evaluate(active_cells=4096, dpr=2.0)
        self.assertEqual(d2.mode, "DOM")

        # Exceeds ceiling (e.g. 8K Retina or 5000 cells) -> INSTANCED_GPU
        d3 = self.decider.evaluate(active_cells=5000, dpr=2.0)
        self.assertEqual(d3.mode, "INSTANCED_GPU")
        self.assertEqual(d3.active_cell_count, 5000)
        # GPU cost must be dramatically lower than DOM reflow cost
        self.assertLess(d3.estimated_gpu_cost_ms, 2.0)
        self.assertGreater(d3.estimated_dom_cost_ms, 20.0) # > 16.6ms threshold
        self.assertIn("GPU instancing preserves 60 FPS", d3.reason)

        # Negative count check
        with self.assertRaises(ValueError):
            self.decider.evaluate(-5)

    def test_binary_vbo_packing_and_stride(self):
        cells = [
            InstancedCell(
                cell_id=1,
                x=0.0,
                y=0.0,
                width=100.0,
                height=30.0,
                bg_color=(255, 0, 0, 255),
                border_color=(0, 255, 0),
                border_width=2,
                text_atlas_uv=(0.1, 0.2, 0.5, 0.5),
                clip_bounds=(0.0, 0.0, 800.0, 600.0)
            ),
            InstancedCell(
                cell_id=2,
                x=100.0,
                y=0.0,
                width=120.0,
                height=30.0,
                bg_color=(0, 0, 255, 200),
                border_color=(255, 255, 255),
                border_width=1,
                text_atlas_uv=(0.0, 0.0, 1.0, 1.0),
                clip_bounds=(100.0, 0.0, 800.0, 600.0)
            )
        ]

        raw_vbo = self.generator.pack_instances(cells)
        # 2 cells * 56 bytes stride = 112 bytes
        self.assertEqual(len(raw_vbo), 2 * INSTANCE_STRIDE_BYTES)
        self.assertEqual(INSTANCE_STRIDE_BYTES, 56)

        # Unpack and verify precision
        inst0 = self.generator.unpack_instance(raw_vbo, 0)
        self.assertAlmostEqual(inst0["x"], 0.0)
        self.assertAlmostEqual(inst0["y"], 0.0)
        self.assertAlmostEqual(inst0["width"], 100.0)
        self.assertAlmostEqual(inst0["height"], 30.0)
        self.assertEqual(inst0["bg_color"], (255, 0, 0, 255))
        self.assertEqual(inst0["border_width"], 2)
        self.assertEqual(inst0["border_color"], (0, 255, 0))
        self.assertAlmostEqual(inst0["text_uv"][0], 0.1)
        self.assertAlmostEqual(inst0["clip_bounds"][2], 800.0)

        inst1 = self.generator.unpack_instance(raw_vbo, 1)
        self.assertAlmostEqual(inst1["x"], 100.0)
        self.assertAlmostEqual(inst1["width"], 120.0)
        self.assertEqual(inst1["bg_color"], (0, 0, 255, 200))
        self.assertEqual(inst1["border_width"], 1)

    def test_gpu_instanced_pipeline_under_massive_viewport(self):
        # Ultra-wide 8K / massive grid test: 200 cols x 100 rows visible = 20,000 cells
        # Set low dom ceiling to 200 to test GPU dispatch
        pipeline = GpuInstancedGridPipeline(
            total_rows=1000,
            total_cols=500,
            row_height=25.0,
            col_width=80.0,
            frozen_rows=1,
            frozen_cols=1,
            dom_ceiling=500
        )
        try:
            # Add a 2x3 merged cell at row 10, col 10
            pipeline.add_merged_cell(merge_id=999, r0=10, c0=10, r1=12, c1=13)

            # Viewport 1920x1080 -> 24 cols x 43 rows = ~1032 cells > 500 ceiling
            manifest = pipeline.build_frame_manifest(
                scroll_x=400.0,
                scroll_y=200.0,
                viewport_width=1920.0,
                viewport_height=1080.0,
                dpr=2.0
            )

            self.assertEqual(manifest["strategy"], "INSTANCED_GPU")
            self.assertGreater(manifest["instance_count"], 500)
            self.assertEqual(manifest["stride_bytes"], 56)
            self.assertEqual(manifest["vbo_byte_length"], manifest["instance_count"] * 56)
            self.assertEqual(len(manifest["binary_vbo"]), manifest["vbo_byte_length"])

            # Verify that the merged cell is present in the packed buffer
            # Find the merged cell in the stream
            found_merged = False
            for i in range(manifest["instance_count"]):
                inst = pipeline.generator.unpack_instance(manifest["binary_vbo"], i)
                # Merged cell width = 3 cols * 80 = 240, height = 2 rows * 25 = 50
                if abs(inst["width"] - 240.0) < 0.01 and abs(inst["height"] - 50.0) < 0.01:
                    found_merged = True
                    # Check amber border
                    self.assertEqual(inst["border_color"], (217, 119, 6))
                    self.assertEqual(inst["border_width"], 2)
                    break

            self.assertTrue(found_merged, "Merged span quad was not found in GPU instanced buffer")
        finally:
            pipeline.close()

    def test_dom_fallback_when_cell_count_within_budget(self):
        pipeline = GpuInstancedGridPipeline(
            total_rows=100,
            total_cols=20,
            row_height=30.0,
            col_width=100.0,
            dom_ceiling=4096
        )
        try:
            # Small viewport 400x300 -> 4 cols x 10 rows = 40 cells << 4096
            manifest = pipeline.build_frame_manifest(
                scroll_x=0.0,
                scroll_y=0.0,
                viewport_width=400.0,
                viewport_height=300.0
            )
            self.assertEqual(manifest["strategy"], "DOM")
            self.assertEqual(manifest["decision"].mode, "DOM")
            self.assertIn("within DOM budget ceiling", manifest["decision"].reason)
        finally:
            pipeline.close()

    def test_out_of_bounds_unpack(self):
        raw = bytearray(INSTANCE_STRIDE_BYTES)
        with self.assertRaises(IndexError):
            self.generator.unpack_instance(bytes(raw), 1) # Index 1 requires 112 bytes
