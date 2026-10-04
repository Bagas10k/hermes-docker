#!/usr/bin/env python3
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from density_surface_engine import (
    ColumnDefinition,
    SurfaceLayoutOptimizer,
    HighDensitySurfaceTheme,
    calculate_contrast_ratio,
    hex_to_rgb
)

class TestHighDensityDataSurfaces(unittest.TestCase):
    def setUp(self):
        self.columns = [
            ColumnDefinition("id", "Transaction ID", min_width=140, priority=1, is_primary=True, sticky=True),
            ColumnDefinition("client", "Client Name", min_width=180, priority=2),
            ColumnDefinition("amount", "Amount (IDR)", min_width=160, priority=1, numeric=True),
            ColumnDefinition("status", "Status", min_width=100, priority=2),
            ColumnDefinition("timestamp", "Timestamp", min_width=160, priority=3),
            ColumnDefinition("gateway", "Payment Gateway", min_width=150, priority=4),
            ColumnDefinition("ip_addr", "IP Address", min_width=130, priority=5),
        ]
        self.optimizer = SurfaceLayoutOptimizer(self.columns, padding_total=32)

    def test_mobile_hybrid_card_transformation(self):
        """Viewport < 640px must trigger hybrid-card mode and eliminate horizontal overflow."""
        res_375 = self.optimizer.compute_layout(viewport_width=375)
        self.assertEqual(res_375["mode"], "hybrid-card")
        self.assertTrue(res_375["zero_blowout_guarantee"])
        self.assertEqual(res_375["header_primary_id"], "id")
        self.assertIn("client", res_375["key_metric_ids"])
        self.assertIn("status", res_375["key_metric_ids"])
        self.assertTrue(res_375["has_drawer_overflow"])

    def test_desktop_dense_table_allocation(self):
        """Wide desktop viewport (1440px) must show all columns with zero blowout."""
        res_1440 = self.optimizer.compute_layout(viewport_width=1440)
        self.assertEqual(res_1440["mode"], "dense-table")
        self.assertTrue(res_1440["zero_blowout_guarantee"])
        self.assertEqual(len(res_1440["visible_column_ids"]), 7)
        self.assertEqual(len(res_1440["collapsed_column_ids"]), 0)
        self.assertFalse(res_1440["has_drawer_overflow"])
        self.assertLessEqual(res_1440["rendered_width"], 1440)

    def test_tablet_dynamic_column_collapse(self):
        """Intermediate tablet viewport (768px) must prioritize priority 1 & 2 and collapse low-priority cols."""
        res_768 = self.optimizer.compute_layout(viewport_width=768)
        self.assertEqual(res_768["mode"], "dense-table")
        self.assertTrue(res_768["zero_blowout_guarantee"])
        self.assertIn("id", res_768["visible_column_ids"])
        self.assertIn("amount", res_768["visible_column_ids"])
        # Priority 5 (ip_addr) and 4 (gateway) should be collapsed
        self.assertIn("ip_addr", res_768["collapsed_column_ids"])
        self.assertTrue(res_768["has_drawer_overflow"])
        self.assertLessEqual(res_768["rendered_width"], 768)

    def test_wcag_aaa_contrast_compliance(self):
        """Audits both dark obsidian and light slate themes for strict contrast."""
        dark_audit = HighDensitySurfaceTheme.audit_contrast_ratios("warm_obsidian")
        # Text primary against surface card must be high contrast
        ratio_primary_dark = dark_audit["text_primary"][0]
        self.assertGreaterEqual(ratio_primary_dark, 12.0)
        
        light_audit = HighDensitySurfaceTheme.audit_contrast_ratios("luminous_slate")
        ratio_primary_light = light_audit["text_primary"][0]
        self.assertGreaterEqual(ratio_primary_light, 12.0)
        
        # Accents must satisfy at least WCAG AA (4.5:1)
        self.assertGreaterEqual(light_audit["accent_emerald"][0], 4.5)
        self.assertGreaterEqual(light_audit["accent_crimson"][0], 4.5)

    def test_zero_blowout_strict_invariant(self):
        """Tests varying viewports across 320px to 2560px for strict W_rendered <= W_viewport invariant."""
        viewports = [320, 360, 390, 480, 600, 640, 720, 768, 800, 1024, 1280, 1440, 1920, 2560]
        for w in viewports:
            layout = self.optimizer.compute_layout(w)
            self.assertTrue(layout["zero_blowout_guarantee"], f"Blowout occurred at viewport {w}px")
            self.assertLessEqual(layout["rendered_width"], w, f"Rendered width exceeded viewport {w}px")

if __name__ == '__main__':
    unittest.main()
