"""Synthetic tests for UIUX-070 nested scroll reflow audit logic."""
import copy
import itertools
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).parent))

from test_clipboard_focus_reflow import record as make_base_measure
from clipboard_nested_reflow import (
    audit_nested_record,
    audit_nested_matrix,
    audit_nested_evidence,
    WIDTHS,
    SCALES,
    OUTCOMES,
    REQUIRED_PHASES,
    NEGATIVES,
)


def make_phase(name, vp=320, sc=1, outcome='success', **kwargs):
    m = make_base_measure()
    m['viewport'] = vp
    m['scale'] = sc
    m['viewportSize'] = {'width': vp, 'height': 800}
    m['fontSamples'][0]['after'] = 10 * sc
    m['documentScrollWidth'] = vp
    m['documentClientWidth'] = vp

    outer_scroll = 0
    inner_scroll = 0
    clicks = 0
    writes = 0
    cont_w = 300
    win_w = vp
    win_h = 800

    if name in ('pending', 'scrolled', 'shrunk', 'regrown'):
        m['state'] = 'pending'
        m['label'] = 'Menyalin…'
        m['statusText'] = 'Menyalin silsilah rute ke clipboard…'
        clicks = 1
        writes = 1

    if name in ('scrolled', 'shrunk', 'regrown', 'settled', 'roundtrip'):
        outer_scroll = 40
        inner_scroll = 30

    if name == 'shrunk':
        cont_w = 240
    elif name in ('regrown', 'settled', 'roundtrip'):
        cont_w = 300

    if name in ('settled', 'roundtrip'):
        clicks = 1
        writes = 1
        m['state'] = outcome
        m['label'] = 'Tersalin!' if outcome == 'success' else 'Gagal menyalin'
        m['copied'] = (outcome == 'success')
        m['statusText'] = ('Silsilah rute berhasil disalin ke clipboard'
                           if outcome == 'success'
                           else 'Gagal menyalin silsilah rute ke clipboard')

    m['trustedClicks'] = clicks
    m['writeCalls'] = writes

    data = {
        'phase': name,
        'sameNode': True,
        'isConnected': True,
        'activeElementMatchesBtn': True,
        'trustedClicks': clicks,
        'writeCalls': writes,
        'outerScrollTop': outer_scroll,
        'innerScrollLeft': inner_scroll,
        'containerWidth': cont_w,
        'windowWidth': win_w,
        'windowHeight': win_h,
        'measurement': m,
    }
    if name == 'roundtrip':
        data['neighborMoved'] = True
        data['returnedToCopy'] = True
        data['neighborTag'] = 'g'
        data['neighborNode'] = 'alpha'
        data['neighborRole'] = 'button'
    data.update(kwargs)
    return data


def make_full_record(vp=320, sc=1, outcome='success'):
    phases = {p: make_phase(p, vp=vp, sc=sc, outcome=outcome) for p in REQUIRED_PHASES}
    return {
        'viewport': vp,
        'scale': sc,
        'outcome': outcome,
        'phases': phases,
    }


class TestClipboardNestedReflow(unittest.TestCase):
    def test_valid_record(self):
        r = make_full_record()
        res = audit_nested_record(r)
        self.assertTrue(res['passed'], f"Failures: {res['failures']}")

    def test_missing_or_bad_matrix_coordinates(self):
        r = make_full_record()
        r['viewport'] = 500
        with self.assertRaises(ValueError):
            audit_nested_record(r)

        r = make_full_record()
        r['scale'] = True  # bool coercion rejected
        with self.assertRaises(ValueError):
            audit_nested_record(r)

        r = make_full_record()
        r['outcome'] = 'idle'  # only success / failure
        with self.assertRaises(ValueError):
            audit_nested_record(r)

    def test_missing_phase(self):
        r = make_full_record()
        del r['phases']['scrolled']
        with self.assertRaises(ValueError):
            audit_nested_record(r)

    def test_focus_loss_in_phase(self):
        r = make_full_record()
        r['phases']['shrunk']['activeElementMatchesBtn'] = False
        with self.assertRaises(ValueError):
            audit_nested_record(r)

        r = make_full_record()
        r['phases']['scrolled']['sameNode'] = False
        with self.assertRaises(ValueError):
            audit_nested_record(r)

    def test_scroll_offset_invariant(self):
        r = make_full_record()
        r['phases']['scrolled']['outerScrollTop'] = 0
        res = audit_nested_record(r)
        self.assertFalse(res['passed'])
        self.assertIn('nested-scroll-offsets', res['failures'])

        r = make_full_record()
        r['phases']['scrolled']['innerScrollLeft'] = 0
        res = audit_nested_record(r)
        self.assertFalse(res['passed'])
        self.assertIn('nested-scroll-offsets', res['failures'])

    def test_container_resize_invariants(self):
        # Shrunk width must be strictly less than initial
        r = make_full_record()
        r['phases']['shrunk']['containerWidth'] = 300
        res = audit_nested_record(r)
        self.assertFalse(res['passed'])
        self.assertIn('container-shrink-focus', res['failures'])

        # Window width must NOT change during shrink
        r = make_full_record()
        r['phases']['shrunk']['windowWidth'] = 310
        with self.assertRaises(ValueError):
            audit_nested_record(r)

        # Regrown width must be strictly greater than shrunk
        r = make_full_record()
        r['phases']['regrown']['containerWidth'] = 240
        res = audit_nested_record(r)
        self.assertFalse(res['passed'])
        self.assertIn('container-regrow-focus', res['failures'])

    def test_app_settlement_invariant(self):
        r = make_full_record(outcome='success')
        r['phases']['settled']['measurement']['label'] = 'Gagal menyalin'
        res = audit_nested_record(r)
        self.assertFalse(res['passed'])
        self.assertIn('app-settlement', res['failures'])

    def test_keyboard_roundtrip_invariant(self):
        r = make_full_record()
        r['phases']['roundtrip']['neighborMoved'] = False
        res = audit_nested_record(r)
        self.assertFalse(res['passed'])
        self.assertIn('keyboard-roundtrip', res['failures'])

    def test_complete_matrix_and_negative_evidence(self):
        records = [make_full_record(vp, sc, oc)
                   for vp, sc, oc in itertools.product(WIDTHS, SCALES, OUTCOMES)]
        matrix_res = audit_nested_matrix(records)
        self.assertTrue(matrix_res['passed'])
        self.assertEqual(matrix_res['record_count'], 12)

        # Build negative controls
        base_m = make_base_measure()
        negatives = {}
        for name in NEGATIVES:
            rec = copy.deepcopy(base_m)
            pos = 'static'
            if name == 'stickyOcclusionAuto':
                rec['opaqueOverlays'] = [{'left': 16, 'top': 25, 'right': 18, 'bottom': 40}]
                rec['hitTestPassed'] = False
                pos = 'sticky'
            elif name == 'stickyOcclusionPointerEventsNone':
                rec['opaqueOverlays'] = [{'left': 16, 'top': 25, 'right': 18, 'bottom': 40}]
                rec['hitTestPassed'] = True
                pos = 'sticky'
            elif name == 'clipping':
                rec['clips'] = [{'left': 0, 'top': 0, 'right': 100, 'bottom': 800, 'x': True, 'y': True}]
            elif name == 'outlineOnly':
                rec['opaqueOverlays'] = [{'left': 16, 'top': 25, 'right': 18, 'bottom': 40}]
                rec['hitTestPassed'] = True
            elif name == 'unfocused':
                rec['focused'] = False
            elif name == 'textOverflow':
                rec['btnScrollWidth'] = 200
                rec['btnClientWidth'] = 100

            entry = {'record': rec}
            if name.startswith('sticky'):
                entry.update(overlayPosition=pos, scrollBefore=50, scrollAfter=60,
                             inset=20, clipLeft=10, leftBefore=30, leftAfter=30,
                             normalLeft=-40, pointerEvents='auto' if name == 'stickyOcclusionAuto' else 'none')
            negatives[name] = entry

        evidence = {
            'target': 'UIUX-070',
            'pass': True,
            'errors': [],
            'records': records,
            'negativeControls': negatives,
        }
        res = audit_nested_evidence(evidence)
        self.assertTrue(res['passed'])
        self.assertEqual(res['matrix_records'], 12)
        for k, v in res['negative_controls'].items():
            self.assertTrue(v, f"Negative control {k} failed to trigger gate")

    def test_fake_sticky_rejected(self):
        records = [make_full_record(vp, sc, oc)
                   for vp, sc, oc in itertools.product(WIDTHS, SCALES, OUTCOMES)]
        base_m = make_base_measure()
        negatives = {}
        for name in NEGATIVES:
            rec = copy.deepcopy(base_m)
            entry = {'record': rec}
            if name == 'stickyOcclusionAuto':
                rec['opaqueOverlays'] = [{'left': 16, 'top': 25, 'right': 18, 'bottom': 40}]
                rec['hitTestPassed'] = False
                entry['overlayPosition'] = 'fixed'  # Fake sticky!
            elif name == 'stickyOcclusionPointerEventsNone':
                rec['opaqueOverlays'] = [{'left': 16, 'top': 25, 'right': 18, 'bottom': 40}]
                rec['hitTestPassed'] = True
                entry['overlayPosition'] = 'sticky'
            elif name == 'outlineOnly':
                rec['opaqueOverlays'] = [{'left': 16, 'top': 25, 'right': 18, 'bottom': 40}]
                rec['hitTestPassed'] = True
            elif name == 'clipping':
                rec['clips'] = [{'left': 0, 'top': 0, 'right': 100, 'bottom': 800, 'x': True, 'y': True}]
            elif name == 'unfocused':
                rec['focused'] = False
            elif name == 'textOverflow':
                rec['btnScrollWidth'] = 200
                rec['btnClientWidth'] = 100
            negatives[name] = entry

        evidence = {
            'target': 'UIUX-070',
            'pass': True,
            'errors': [],
            'records': records,
            'negativeControls': negatives,
        }
        with self.assertRaises(ValueError):
            audit_nested_evidence(evidence)


if __name__ == '__main__':
    unittest.main()
