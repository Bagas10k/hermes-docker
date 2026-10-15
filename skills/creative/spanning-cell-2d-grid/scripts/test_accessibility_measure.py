"""Deterministic tests for accessibility measurement helper.

Validates exact W3C WCAG 2.1 relative luminance and contrast ratio calculations,
strict input validation boundaries, and focus-visible record auditing.
"""
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from accessibility_measure import (
    parse_color,
    srgb_to_linear,
    relative_luminance,
    contrast_ratio,
    parse_px,
    audit_focus_visible_record,
    audit_browser_file,
)


class AccessibilityMeasureTests(unittest.TestCase):
    def test_w3c_reference_contrast_values(self):
        # 1. Black vs White is exact 21:1
        black = (0, 0, 0)
        white = (255, 255, 255)
        self.assertAlmostEqual(relative_luminance(black), 0.0, places=5)
        self.assertAlmostEqual(relative_luminance(white), 1.0, places=5)
        self.assertAlmostEqual(contrast_ratio(black, white), 21.0, places=4)

        # 2. Symmetry: contrast(a, b) == contrast(b, a)
        self.assertEqual(contrast_ratio(black, white), contrast_ratio(white, black))

        # 3. Identical color is exact 1:1
        self.assertAlmostEqual(contrast_ratio(black, black), 1.0, places=4)
        self.assertAlmostEqual(contrast_ratio(white, white), 1.0, places=4)
        self.assertAlmostEqual(contrast_ratio('#2563eb', '#2563eb'), 1.0, places=4)

        # 4. Pure blue vs White
        pure_blue = (0, 0, 255)
        self.assertAlmostEqual(relative_luminance(pure_blue), 0.0722, places=4)
        self.assertAlmostEqual(contrast_ratio(pure_blue, white), 8.5925, places=3)

        # 5. UIUX-067 focus indicator: #2563eb vs #f1f5f9
        blue = '#2563eb'
        bar_bg = '#f1f5f9'
        btn_bg = '#e2e8f0'
        ratio_bar = contrast_ratio(blue, bar_bg)
        ratio_btn = contrast_ratio(blue, btn_bg)
        self.assertGreaterEqual(ratio_bar, 3.0)  # WCAG 1.4.11 non-text minimum
        self.assertGreaterEqual(ratio_btn, 3.0)
        self.assertAlmostEqual(ratio_bar, 4.7179, places=3)
        self.assertAlmostEqual(ratio_btn, 4.1926, places=3)

    def test_color_format_parsing(self):
        # Hex 3
        self.assertEqual(parse_color('#fff'), (255.0, 255.0, 255.0))
        self.assertEqual(parse_color('#000'), (0.0, 0.0, 0.0))
        # Hex 6
        self.assertEqual(parse_color('#2563eb'), (37.0, 99.0, 235.0))
        # Hex 8 opaque
        self.assertEqual(parse_color('#2563ebff'), (37.0, 99.0, 235.0))
        # CSS rgb string
        self.assertEqual(parse_color('rgb(37, 99, 235)'), (37.0, 99.0, 235.0))
        # CSS rgba string opaque
        self.assertEqual(parse_color('rgba(37, 99, 235, 1)'), (37.0, 99.0, 235.0))
        self.assertEqual(parse_color('rgba(37, 99, 235, 1.0)'), (37.0, 99.0, 235.0))
        # Tuple / list
        self.assertEqual(parse_color((37, 99, 235)), (37.0, 99.0, 235.0))
        self.assertEqual(parse_color([37, 99, 235, 1.0]), (37.0, 99.0, 235.0))

    def test_negative_input_validation(self):
        # Non-opaque alpha
        with self.assertRaises(ValueError):
            parse_color('rgba(37, 99, 235, 0.5)')
        with self.assertRaises(ValueError):
            parse_color('#2563eb80')
        with self.assertRaises(ValueError):
            parse_color([37, 99, 235, 0.8])

        # Out of bounds
        with self.assertRaises(ValueError):
            parse_color((256, 0, 0))
        with self.assertRaises(ValueError):
            parse_color((-1, 0, 0))
        with self.assertRaises(ValueError):
            parse_color('rgb(300, 0, 0)')

        # Non-finite values
        with self.assertRaises(ValueError):
            parse_color((float('nan'), 0, 0))
        with self.assertRaises(ValueError):
            parse_color((float('inf'), 0, 0))

        # Invalid string format
        with self.assertRaises(ValueError):
            parse_color('#12')
        with self.assertRaises(ValueError):
            parse_color('#gggggg')
        with self.assertRaises(ValueError):
            parse_color('invalid-color')

        # Type errors
        with self.assertRaises(TypeError):
            parse_color(None)
        with self.assertRaises(TypeError):
            parse_color({'r': 255})
        with self.assertRaises(TypeError):
            parse_color((True, 0, 0))

    def test_parse_px(self):
        self.assertEqual(parse_px('2px'), 2.0)
        self.assertEqual(parse_px('0.5px'), 0.5)
        self.assertEqual(parse_px(3), 3.0)
        self.assertEqual(parse_px(1.5), 1.5)
        with self.assertRaises(ValueError):
            parse_px('auto')
        with self.assertRaises(ValueError):
            parse_px(float('nan'))

    def test_audit_focus_visible_record(self):
        record_compliant = {
            'outlineStyle': 'solid', 'focused': True,
            'outlineColor': 'rgb(37, 99, 235)',
            'outlineWidth': '2px',
            'outlineOffset': '2px',
            'adjacentBg': 'rgb(241, 245, 249)',
            'buttonBg': 'rgb(226, 232, 240)',
        }
        res = audit_focus_visible_record(record_compliant)
        self.assertTrue(res['compliant'])
        self.assertTrue(res['passes_adjacent'])
        self.assertTrue(res['passes_button'])
        self.assertTrue(res['passes_width'])
        self.assertAlmostEqual(res['contrast_against_adjacent'], 4.7179, places=3)
        self.assertAlmostEqual(res['contrast_against_button'], 4.1926, places=3)

        # Fails width (< 1px)
        record_thin = dict(record_compliant, outlineWidth='0.5px')
        res_thin = audit_focus_visible_record(record_thin)
        self.assertFalse(res_thin['compliant'])
        self.assertFalse(res_thin['passes_width'])

        # Fails contrast (< 3.0)
        record_low_contrast = dict(record_compliant, outlineColor='rgb(240, 244, 248)')
        res_low = audit_focus_visible_record(record_low_contrast)
        self.assertFalse(res_low['compliant'])
        self.assertFalse(res_low['passes_adjacent'])

    def test_audit_browser_file(self):
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
            data = {
                'records': [
                    {
                        'type': 'focus_visible',
                        'viewport': 390,
                        'outlineStyle': 'solid', 'focused': True,
            'outlineColor': 'rgb(37, 99, 235)',
                        'outlineWidth': '2px',
                        'outlineOffset': '2px',
                        'adjacentBg': 'rgb(241, 245, 249)',
                        'buttonBg': 'rgb(226, 232, 240)',
                    },
                    {
                        'type': 'focus_visible',
                        'viewport': 768,
                        'outlineStyle': 'solid', 'focused': True,
            'outlineColor': 'rgb(37, 99, 235)',
                        'outlineWidth': '2px',
                        'outlineOffset': '2px',
                        'adjacentBg': 'rgb(241, 245, 249)',
                        'buttonBg': 'rgb(226, 232, 240)',
                    }
                ]
            }
            json.dump(data, f)
            temp_path = f.name

        try:
            audit = audit_browser_file(temp_path)
            self.assertEqual(audit['total_audited'], 2)
            self.assertTrue(audit['all_compliant'])
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_audit_actual_browser_evidence(self):
        evidence_path = Path(__file__).resolve().parent.parent / 'references' / 'uiux-067-accessibility-browser.json'
        if not evidence_path.is_file():
            self.skipTest('Browser evidence absent; run test_accessibility_chromium.cjs')
        if evidence_path.is_file():
            audit = audit_browser_file(str(evidence_path))
            self.assertEqual(audit['total_audited'], 3)
            self.assertTrue(audit['all_compliant'])
            for item in audit['details']:
                self.assertIn(item['viewport'], [390, 768, 1280])
                self.assertEqual(item['audit']['outline_width_px'], 2.0)
                self.assertEqual(item['audit']['outline_offset_px'], 2.0)
                self.assertAlmostEqual(item['audit']['contrast_against_adjacent'], 4.7179, places=3)
                self.assertAlmostEqual(item['audit']['contrast_against_button'], 4.1926, places=3)

    def test_empty_or_malformed_evidence_never_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'evidence.json'
            for records in ([], [{'type': 'motion_styles'}]):
                target.write_text(json.dumps({'records': records}))
                self.assertFalse(audit_browser_file(target)['all_compliant'])
        record = dict(outlineColor='#2563eb', adjacentBg='#f1f5f9',
                      outlineWidth='2px', outlineOffset='2px',
                      outlineStyle='none', focused=False)
        self.assertFalse(audit_focus_visible_record(record)['compliant'])

    def test_measurement_gate_rejects_nonfinite_bounds(self):
        for value in ('nan', 'inf', '1e999', True):
            with self.subTest(value=value), self.assertRaises((ValueError, TypeError)):
                parse_px(value)
        with self.assertRaises((ValueError, TypeError)):
            parse_color([0, 0, 0, True])


if __name__ == '__main__':
    unittest.main()