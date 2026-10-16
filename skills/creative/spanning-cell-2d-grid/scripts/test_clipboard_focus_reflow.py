"""Synthetic geometry contracts, NOT browser evidence."""
import copy
import itertools
import unittest
from clipboard_focus_reflow import audit_record, audit_matrix, audit_evidence


def record():
    return dict(viewport=320, container='normal', scale=1, state='idle',
                label='Salin Rute', statusText='Versi root. 1 cabang lanjutan.', copied=False,
                focused=True, focusVisible=True, outlineStyle='solid', outlineWidth=2,
                outlineOffset=2, buttonRect=dict(left=20, top=20, right=120, bottom=50),
                viewportSize=dict(width=320, height=800),
                barRect=dict(left=10, top=10, right=300, bottom=70), clips=[],
                hitTestPassed=True, opaqueOverlays=[], unsupported=[],
                btnScrollWidth=98, btnClientWidth=98, btnScrollHeight=28, btnClientHeight=28,
                barScrollWidth=288, barClientWidth=288, fontSamples=[dict(before=10, after=10)],
                tabCount=5, trustedClicks=0, writeCalls=0, reducedMotion=True,
                transitionSeconds=0.00001, documentScrollWidth=320, documentClientWidth=320)


class TestClipboardFocusReflow(unittest.TestCase):
    def test_valid_and_exact_outline_boundary(self):
        r = record()
        self.assertTrue(audit_record(r)['passed'])
        r['clips'] = [dict(left=16, top=16, right=124, bottom=54, x=True, y=True)]
        self.assertTrue(audit_record(r)['passed'])
        r['clips'][0]['right'] = 123.9
        self.assertFalse(audit_record(r)['passed'])

    def test_nonfinite_boolean_and_missing_fail_closed(self):
        for value in (float('nan'), float('inf'), True, '20'):
            r = record(); r['buttonRect']['left'] = value
            with self.assertRaises((ValueError, TypeError)):
                audit_record(r)
        for field in ('hitTestPassed', 'opaqueOverlays', 'fontSamples', 'clips'):
            r = record(); del r[field]
            with self.assertRaises((KeyError, ValueError)):
                audit_record(r)
        r = record(); r['scale'] = True
        with self.assertRaises(ValueError):
            audit_record(r)

    def test_nested_axis_clip(self):
        r = record(); r['clips'] = [dict(left=0, top=0, right=123, bottom=800, x=True, y=False)]
        self.assertIn('clipping', audit_record(r)['failures'])
        r['clips'][0]['x'] = False
        self.assertTrue(audit_record(r)['passed'])
        r['clips'].append(dict(left=0, top=19, right=320, bottom=800, x=False, y=True))
        self.assertIn('clipping', audit_record(r)['failures'])

    def test_overlay_covers_only_outline_and_bypasses_pointer(self):
        r = record(); r['opaqueOverlays'] = [dict(left=16, top=25, right=18, bottom=40)]
        self.assertTrue(r['hitTestPassed'])
        self.assertIn('occlusion', audit_record(r)['failures'])
        r['opaqueOverlays'][0]['right'] = 16
        with self.assertRaises(ValueError):
            audit_record(r)

    def test_reflow_both_axes(self):
        for field in ('btnScrollWidth', 'btnScrollHeight', 'barScrollWidth'):
            r = record(); r[field] += 2
            self.assertIn('text-fit', audit_record(r)['failures'])

    def test_document_overflow_rejected(self):
        r = record(); r['documentScrollWidth'] = 461
        self.assertIn('document-overflow', audit_record(r)['failures'])

    def test_observed_font_ratio_and_native_state(self):
        r = record(); r['scale'] = 2
        self.assertIn('font-scale', audit_record(r)['failures'])
        r['fontSamples'][0]['after'] = 20
        self.assertTrue(audit_record(r)['passed'])
        r['fontSamples'][0]['after'] = 40
        self.assertIn('font-scale', audit_record(r)['failures'])
        r = record(); r.update(state='pending', label='Menyalin…', statusText='Menyalin silsilah rute ke clipboard…')
        self.assertIn('activation', audit_record(r)['failures'])
        r.update(trustedClicks=1, writeCalls=1)
        self.assertTrue(audit_record(r)['passed'])

    def test_focus_motion_and_unsupported_context(self):
        for key, val in (('focused', False), ('focusVisible', False), ('reducedMotion', False),
                         ('outlineStyle', 'none'), ('unsupported', ['transform'])):
            r = record(); r[key] = val
            self.assertFalse(audit_record(r)['passed'])

    def test_complete_matrix_and_negative_evidence(self):
        from clipboard_focus_reflow import WIDTHS, CONTAINERS, SCALES, LABELS, STATUS, NEGATIVES
        rows = []
        for vp, c, sc, st in itertools.product(WIDTHS, CONTAINERS, SCALES, LABELS):
            r = record(); r.update(viewport=vp, container=c, scale=sc, state=st,
                label=LABELS[st], statusText=STATUS.get(st, 'Versi root'), copied=st=='success',
                trustedClicks=int(st!='idle'), writeCalls=int(st!='idle'))
            r['viewportSize']['width']=vp; r['fontSamples'][0]['after']=10*sc
            r['documentScrollWidth']=vp; r['documentClientWidth']=vp
            rows.append(r)
        self.assertTrue(audit_matrix(rows)['passed'])
        for bad in (rows[:-1], rows+[rows[0]], rows[:-1]+[rows[0]]):
            with self.assertRaises(ValueError): audit_matrix(bad)
        data = dict(pass_=True, errors=[], records=rows, negativeControls={})
        data['pass'] = data.pop('pass_')
        with self.assertRaises(ValueError): audit_evidence(data)
        # Each negative must fail the SAME gate for its named reason, not a trusted boolean.
        data['negativeControls'] = {name: dict(record=copy.deepcopy(rows[0]), detectedViolation=True) for name in NEGATIVES}
        self.assertFalse(audit_evidence(data)['passed'])


if __name__ == '__main__':
    unittest.main()
