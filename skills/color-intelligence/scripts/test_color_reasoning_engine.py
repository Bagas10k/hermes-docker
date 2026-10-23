import math
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import color_reasoning_engine as engine


class ColorEngineTest(unittest.TestCase):
    def test_roundtrip(self):
        for color in ('#000000', '#FFFFFF', '#FF0000', '#1A73E8',
                      '#00D8B5', '#F0D83B', '#A020F0'):
            actual = engine.to_hex(engine.oklab_to_rgb(engine.rgb_to_oklab(
                engine.parse_hex(color))))
            self.assertEqual(color, actual)

    def test_w3c_contrast(self):
        self.assertAlmostEqual(engine.contrast('#FFFFFF', '#000000'), 21, places=6)
        self.assertAlmostEqual(engine.contrast('#777777', '#FFFFFF'), 4.478, delta=.003)

    def test_hex_parser_is_strict(self):
        for valid in ('fff', '#fff', '123456', '#123456'):
            self.assertEqual(3, len(engine.parse_hex(valid)))
        for invalid in ('##fff', '###123456', '#12', '#1234', '#1234567',
                        '0x123456', '', None, 123456):
            with self.assertRaises(ValueError, msg=invalid):
                engine.parse_hex(invalid)

    def test_gamut_safe(self):
        for hue in range(0, 360, 17):
            for lightness in (0.15, 0.35, 0.65, .85):
                color = engine.gamut_map(lightness, .33, hue)
                self.assertEqual(7, len(color))
                self.assertTrue(all(0 <= x <= 1 for x in engine.parse_hex(color)))

    def test_seed_invariance(self):
        a = engine.derive('#23A9CE', variants=2, explore=80)
        b = engine.derive('#23A9CE', variants=2, explore=80)
        self.assertEqual(a, b)

    def test_accessibility_recomputed_from_final_hex(self):
        pairs = {
            'body_text_on_surface': ('text', 'surface', 4.5),
            'muted_text_on_surface': ('muted_text', 'surface', 4.5),
            'primary_on_surface': ('primary', 'surface', 3.0),
            'primary_text_on_primary': ('on_primary', 'primary', 4.5),
            'secondary_on_surface': ('secondary', 'surface', 3.0),
            'secondary_text_on_secondary': ('on_secondary', 'secondary', 4.5),
        }
        seeds = ('#FF0000', '#123456', '#FFFFFF', '#000000',
                 '#A08F00', '#DAFF65', '#9200F0', '#00FA80')
        for seed in seeds:
            for mode in ('dark', 'light'):
                data = engine.derive(seed, mode=mode, variants=2, explore=75)
                self.assertGreaterEqual(len(data['variants']), 1)
                for variant in data['variants']:
                    palette = variant['palette']
                    for name, (foreground, background, limit) in pairs.items():
                        actual = engine.contrast(palette[foreground], palette[background])
                        self.assertGreaterEqual(actual, limit, (seed, mode, name, actual))
                        self.assertAlmostEqual(variant['contrast'][name], actual, delta=.00051)

    def test_no_false_neutral_hue(self):
        data = engine.derive('#FFFFFF', explore=35, variants=1)
        self.assertTrue(data['input']['neutral_seed_hue_inferred'])

    def test_nonzero_perceptual_distance(self):
        self.assertGreater(engine.delta_ok('#FF0000', '#0000FF'), .1)

    def test_direct_api_bounds(self):
        for value in (0, 21, 1.5, float('nan'), float('inf'), True, '3'):
            with self.assertRaises(ValueError, msg=f'variants={value!r}'):
                engine.derive('#23A9CE', variants=value, explore=30)
        for value in (29, 2001, 1.5, float('nan'), float('inf'), True, '30'):
            with self.assertRaises(ValueError, msg=f'explore={value!r}'):
                engine.derive('#23A9CE', explore=value)

    def test_public_numeric_boundaries_reject_nonfinite(self):
        nonfinite = (float('nan'), float('inf'), -float('inf'))
        for value in nonfinite:
            probes = (
                lambda: engine.gamut_map(value, .1, 30),
                lambda: engine.gamut_map(.5, value, 30),
                lambda: engine.gamut_map(.5, .1, value),
                lambda: engine.select_active_color(value, .1, '#000000', True, .7),
                lambda: engine.select_active_color(30, value, '#000000', True, .7),
                lambda: engine.select_active_color(30, .1, '#000000', True, value),
                lambda: engine.derive('#23A9CE', expression=value, explore=30),
                lambda: engine.derive('#23A9CE', tension=value, explore=30),
                lambda: engine.derive('#23A9CE', hue=value, explore=30),
            )
            for probe in probes:
                with self.assertRaises(ValueError):
                    probe()

    def test_gamut_cache_is_bounded_and_uses_normalized_keys(self):
        engine.gamut_map.cache_clear()
        first = engine.gamut_map(-1, .1, 370)
        second = engine.gamut_map(0, .1, 10)
        info = engine.gamut_map.cache_info()
        self.assertEqual(first, second)
        self.assertEqual(1, info.hits)
        self.assertEqual(1, info.misses)
        self.assertEqual(16384, info.maxsize)

    @staticmethod
    def _exhaustive_select(hue, chroma, surface, dark, target_L):
        best = None
        for k in range(101):
            lightness = 0.27 + 0.69*k/100
            color = engine.gamut_map(lightness, chroma, hue)
            ink = engine.choose_ink(color)
            if ink is None or engine.contrast(color, surface) < 3:
                continue
            actual_chroma = engine.lab_to_lch(
                engine.rgb_to_oklab(engine.parse_hex(color)))[1]
            score = abs(lightness - target_L) + max(0., chroma - actual_chroma)*0.9
            if best is None or score < best[0]:
                best = (score, color, ink)
        if best is None:
            raise RuntimeError('No feasible accessible active color')
        return best[1], best[2]

    def test_branch_and_bound_matches_exhaustive(self):
        for dark in (False, True):
            surface = '#F7F7F7' if not dark else '#111111'
            for hue in (0, 47, 133, 241, 359):
                for chroma in (.065, .15, .3):
                    for target in (.31, .54, .75, .93):
                        expected = self._exhaustive_select(
                            hue, chroma, surface, dark, target)
                        actual = engine.select_active_color(
                            hue, chroma, surface, dark, target)
                        self.assertEqual(expected, actual,
                                         (dark, hue, chroma, target))

    def test_primary_is_selected_once_per_derive(self):
        original = engine.select_active_color
        with mock.patch.object(engine, 'select_active_color', wraps=original) as wrapped:
            engine.derive('#23A9CE', variants=2, explore=30)
        self.assertEqual(31, wrapped.call_count)


if __name__ == '__main__':
    unittest.main()
