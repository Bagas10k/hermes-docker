"""Synthetic unit inputs for the bounded feedback evidence gate, not browser evidence."""
import copy
import itertools
import unittest
from feedback_contrast import audit_matrix, audit_record, composite_outline


def record(mode='normal', state='idle', hovered=False, viewport=390):
    dark = mode == 'forced-dark'
    return dict(viewport=viewport, mode=mode, state=state, hovered=hovered,
                hoveredMatch=hovered, forcedColors=mode != 'normal',
                colorScheme='dark' if dark else 'light',
                buttonColor='#fff' if dark else '#000',
                buttonBg='#000' if dark else '#fff',
                adjacentBg='#000' if dark else '#fff',
                outlineColor='rgba(0, 230, 255, 0.8)' if dark else '#000',
                outlineStyle='solid', outlineWidth='2px', outlineOffset='2px',
                focused=True, focusVisible=True, opacity='1', ancestorOpaque=True,
                forcedColorAdjust='auto', animationsRunning=0,
                buttonBackgroundImage='none', adjacentBackgroundImage='none',
                label={'idle':'Salin Rute', 'pending':'Menyalin…',
                       'success':'Tersalin!', 'failure':'Gagal menyalin'}[state],
                statusText={'idle':'Versi root. 1 cabang lanjutan.',
                            'pending':'Menyalin silsilah rute ke clipboard…',
                            'success':'Silsilah rute berhasil disalin ke clipboard',
                            'failure':'Gagal menyalin silsilah rute ke clipboard'}[state],
                ariaBusy=state == 'pending')


def matrix():
    return [record(m, s, h, v) for v, m, s, h in itertools.product(
        (390, 768, 1280), ('normal', 'forced-light', 'forced-dark'),
        ('idle', 'pending', 'success', 'failure'), (False, True))]


class FeedbackContrastTests(unittest.TestCase):
    def test_complete_matrix(self):
        result = audit_matrix(matrix())
        self.assertEqual(result['records'], 72)
        self.assertTrue(result['passed'])
        self.assertEqual(result['text_min'], 21)

    def test_actual_alpha_compositing(self):
        self.assertEqual(composite_outline('rgba(0, 230, 255, 0.8)', '#000'), (0, 184, 204))
        light = composite_outline('rgba(5, 0, 73, 0.8)', '#fff')
        for actual, expected in zip(light, (55, 51, 109.4)):
            self.assertAlmostEqual(actual, expected)
        self.assertEqual(composite_outline('rgba(0,0,0,0)', '#fff'), (255, 255, 255))
        self.assertEqual(composite_outline('#123456', '#fff'), (18, 52, 86))

    def test_reject_malformed_alpha_and_transparent_backdrop(self):
        for color in ('rgba(0,0,0,nan)', 'rgba(0,0,0,1.1)', 'rgba(256,0,0,.5)',
                      'rgba(0,0,0,-.1)', 'rgba(0,0,0,.5) trailing'):
            with self.subTest(color=color), self.assertRaises((ValueError, TypeError)):
                composite_outline(color, '#fff')
        with self.assertRaises(ValueError):
            composite_outline('#000', 'rgba(255,255,255,0.5)')

    def test_low_contrast_and_rounding_never_pass(self):
        r = record(state='success')
        r.update(buttonColor='#fff', buttonBg='#10b981')
        self.assertFalse(audit_record(r)['passed'])
        # Encode a controlled gray whose exact ratio is just below 4.5.
        luminance = 1.05 / 4.49999 - 0.05
        channel = 255 * (1.055 * luminance ** (1 / 2.4) - 0.055)
        r.update(buttonBg=(channel, channel, channel))
        self.assertFalse(audit_record(r)['passed'])
        self.assertFalse(audit_record(dict(record(), outlineColor='#fff'))['passed'])

    def test_exact_matrix_coverage(self):
        rows = matrix()
        for bad in ([], rows[:-1], rows + [rows[0]], [rows[0]] * 72):
            with self.subTest(length=len(bad)), self.assertRaises(ValueError):
                audit_matrix(bad)

    def test_reject_invalid_types_and_missing_values(self):
        for key, value in [('viewport', True), ('hovered', 1), ('state', 'copied'),
                           ('mode', 'unknown'), ('outlineWidth', 'nan'), ('opacity', 'nan')]:
            r = dict(record(), **{key: value})
            with self.subTest(key=key), self.assertRaises((ValueError, TypeError)):
                audit_record(r)
        r = record()
        del r['buttonColor']
        with self.assertRaises((ValueError, KeyError)):
            audit_record(r)

    def test_visibility_media_and_text_guards(self):
        for key, value in [('focused', False), ('focusVisible', False),
                           ('hoveredMatch', True), ('forcedColors', True),
                           ('colorScheme', 'dark'), ('opacity', '.5'),
                           ('ancestorOpaque', False), ('outlineStyle', 'none'),
                           ('outlineWidth', '0px'), ('outlineOffset', '0px'),
                           ('forcedColorAdjust', 'none'), ('animationsRunning', 1),
                           ('buttonBackgroundImage', 'linear-gradient(red,blue)'),
                           ('label', ''), ('ariaBusy', 'true'), ('statusText', '')]:
            with self.subTest(key=key):
                self.assertFalse(audit_record(dict(record(), **{key: value}))['passed'])

    def test_matrix_does_not_trust_precomputed_ratios(self):
        rows = copy.deepcopy(matrix())
        rows[0].update(buttonColor='#fff', textContrastRatio=21)
        self.assertFalse(audit_matrix(rows)['passed'])


if __name__ == '__main__':
    unittest.main()
