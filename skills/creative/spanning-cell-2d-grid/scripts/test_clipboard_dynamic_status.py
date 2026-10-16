"""UIUX-073: Deterministic unit tests for dynamic status reservation validator."""
import copy
import itertools
import unittest
from clipboard_dynamic_status import (
    audit_dynamic_status_record, audit_dynamic_status_evidence,
    NEGATIVES_073, LONG_REVISION_ID
)
from clipboard_scroll_anchor import (
    WIDTHS, SCALES, OUTCOMES, DEPARTURES, REQUIRED_PHASES, SCROLL_KEYS
)
from test_clipboard_scroll_anchor import COPY, FORWARD, BACKWARD, event, bind, target_geo
BACKWARD = dict(BACKWARD, dataBreadcrumbNode=LONG_REVISION_ID)
from test_clipboard_focus_reflow import record as geometry
from clipboard_focus_reflow import LABELS, STATUS


LONG_STATUS = 'Versi feat/virtualized-2d-grid-with-asymmetric-spans-and-history-c98f820b784913c98b671a5392812d4a7536901234567890abcdef. 0 cabang lanjutan.'


def make_dynamic(vp=320, scale=1, outcome='success', departure='stay', anchor='auto', layout='dynamic-reserved'):
    target = FORWARD if departure == 'forward' else BACKWARD
    trace = [
        event('setup', 'keydown', key='Tab'),
        event('setup', 'focusin'),
        event('pending', 'keydown', key='Enter'),
        event('scrolled', 'scroll', {'id': 'dag-scroll-outer'}),
        event('scrolled', 'scroll', {'id': 'dag-scroll-inner'}),
    ]
    if departure != 'stay':
        trace.extend([
            event('departed', 'keydown', key='Tab', shift=departure == 'backward'),
            event('departed', 'focusout', COPY, target),
            event('departed', 'focusin', target, COPY)
        ])
    phases = {}
    for name in REQUIRED_PHASES:
        active = departure == 'stay' or name not in ('departed', 'settled', 'reset')
        state = 'idle' if name in ('initial', 'reset') else outcome if name == 'settled' else 'pending'
        m = geometry()
        text = LONG_STATUS if name in ('initial', 'reset') else STATUS.get(state, LONG_STATUS)
        m.update(viewport=vp, scale=scale, viewportSize={'width': vp, 'height': 900},
                 documentScrollWidth=vp, documentClientWidth=vp, state=state, label=LABELS[state],
                 statusText=text, copied=state == 'success',
                 focused=active, focusVisible=active, tabCount=1,
                 fontSamples=[{'before': 10, 'after': 10*scale}],
                 trustedClicks=int(name != 'initial'), writeCalls=int(name != 'initial'))
        scroll = dict.fromkeys(SCROLL_KEYS, 0)
        if name not in ('initial', 'pending'):
            scroll.update({'dag-scroll-outerY': 30, 'dag-scroll-innerX': 25})
        phases[name] = dict(
            phase=name, sameNode=True, isConnected=True, activeElementMatchesBtn=active,
            activeElement=copy.deepcopy(COPY if active else target),
            activeTarget=dict(target_geo(departure if name in ('departed', 'settled', 'reset') else 'stay'), **({'dataBreadcrumbNode':LONG_REVISION_ID} if departure=='backward' and name in ('departed','settled','reset') else {})),
            measurement=m, anchorPolicy=anchor,
            buttonText='Salin Rute' if name in ('initial', 'reset') else LABELS[state],
            copied=state == 'success', statusText=text, statusHeight=120.0,
            statusTextFits=True, breadcrumbTextFits=True, reservationText=LONG_STATUS,
            statusClientWidth=250 if name == 'shrunk' else 280,
            statusScrollWidth=250 if name == 'shrunk' else 280,
            trustedClicks=m['trustedClicks'], writeCalls=m['writeCalls'],
            outerScrollTop=scroll['dag-scroll-outerY'], innerScrollLeft=scroll['dag-scroll-innerX'],
            windowWidth=vp, windowHeight=900, scroll=scroll,
            containerWidth=250 if name == 'shrunk' else 280
        )
    return bind(dict(
        viewport=vp, scale=scale, outcome=outcome, departure=departure,
        anchorPolicy=anchor, layout=layout, resetTimerExecuted=True,
        timers=[{'delay':1500,'registeredAt':150,'firedAt':1650,'calls':1}], phases=phases, eventTrace=trace
    ))


class TestClipboardDynamicStatus(unittest.TestCase):
    def test_positive_record_passes(self):
        r = make_dynamic()
        res = audit_dynamic_status_record(r)
        self.assertTrue(res['passed'])
        self.assertEqual(res['failures'], [])

    def test_unreserved_counterexample_fails_status_height(self):
        """Counterexample: without dynamic status reservation, pending collapses and reset jumps."""
        r = make_dynamic(layout='unreserved')
        # Simulate unreserved pending & settled collapse
        r['phases']['pending']['statusHeight'] = 40.0
        r['phases']['settled']['statusHeight'] = 40.0
        res = audit_dynamic_status_record(r)
        self.assertFalse(res['passed'])
        self.assertIn('status-height', res['failures'])

    def test_unbroken_text_blowout_fails_status_overflow(self):
        """Without overflow-wrap: anywhere, unbroken text causes horizontal overflow."""
        r = make_dynamic()
        r['phases']['initial']['statusScrollWidth'] = 800.0
        r['phases']['initial']['statusClientWidth'] = 320.0
        res = audit_dynamic_status_record(r)
        self.assertFalse(res['passed'])
        self.assertIn('status-overflow', res['failures'])

    def test_exact_status_reset_continuity(self):
        r = make_dynamic()
        r['phases']['reset']['statusText'] = 'Versi corrupted.'
        res = audit_dynamic_status_record(r)
        self.assertIn('status-reset-text', res['failures'])

    def test_timer_deadline_contract(self):
        r = make_dynamic()
        r['timers'][0]['firedAt'] = 200 # fired too early (< 1499ms)
        res = audit_dynamic_status_record(r)
        self.assertIn('native-timer-deadline', res['failures'])

    def test_full_evidence_structure(self):
        records = [make_dynamic(*a) for a in itertools.product(WIDTHS, SCALES, OUTCOMES, DEPARTURES)]
        negs = {
            'oldUnreservedDynamicReset': {'record': make_dynamic(390, 2, 'failure', 'forward', layout='unreserved')},
            'unbrokenTextBlowout': {'record': make_dynamic(320, 1, 'success', 'stay')},
            'targetClipped': {'record': make_dynamic(320, 1, 'success', 'forward')},
            'targetCovered': {'record': make_dynamic(320, 1, 'success', 'forward')},
            'transientBlurRefocus': {'record': make_dynamic(320, 1, 'success', 'stay')},
            'completionFocusTheft': {'record': make_dynamic(320, 1, 'success', 'forward')},
            'completionStealReturn': {'record': make_dynamic(320, 1, 'success', 'forward')},
            'resetFocusTheft': {'record': make_dynamic(320, 1, 'success', 'forward')},
            'transientResetScroll': {'record': make_dynamic(320, 1, 'success', 'stay')},
            'wrongDepartureIdentity': {'record': make_dynamic(320, 1, 'success', 'forward')},
        }
        # inject expected faults
        negs['oldUnreservedDynamicReset']['record']['phases']['pending']['statusHeight'] = 40.0
        negs['oldUnreservedDynamicReset']['record']['phases']['settled']['statusHeight'] = 40.0
        negs['unbrokenTextBlowout']['record']['phases']['initial']['statusScrollWidth'] = 800.0
        negs['unbrokenTextBlowout']['record']['phases']['initial']['statusClientWidth'] = 320.0
        negs['targetClipped']['record']['phases']['reset']['activeTarget']['clips'] = [{'left':0,'top':0,'right':150,'bottom':900,'x':True,'y':True}]
        negs['targetCovered']['record']['phases']['reset']['activeTarget']['overlays'] = [{'left':100,'top':100,'right':200,'bottom':140}]
        negs['transientBlurRefocus']['record']['eventTrace'] += [event('shrunk', 'focusout'), event('shrunk', 'focusin')]
        bind(negs['transientBlurRefocus']['record'])
        negs['completionFocusTheft']['record']['phases']['settled']['activeElement'] = COPY
        negs['completionFocusTheft']['record']['phases']['settled']['activeTarget'] = target_geo('stay')
        negs['completionStealReturn']['record']['eventTrace'] += [
            event('settled', 'focusout', FORWARD, COPY), event('settled', 'focusin', COPY, FORWARD),
            event('settled', 'focusout', COPY, FORWARD), event('settled', 'focusin', FORWARD, COPY)
        ]
        bind(negs['completionStealReturn']['record'])
        negs['resetFocusTheft']['record']['eventTrace'] += [
            event('reset', 'focusout', FORWARD, COPY), event('reset', 'focusin', COPY, FORWARD),
            event('reset', 'focusout', COPY, FORWARD), event('reset', 'focusin', FORWARD, COPY)
        ]
        bind(negs['resetFocusTheft']['record'])
        negs['transientResetScroll']['record']['eventTrace'] += [event('reset', 'scroll', {'id': 'dag-scroll-outer'})]
        bind(negs['transientResetScroll']['record'])
        negs['wrongDepartureIdentity']['record']['phases']['departed']['activeElement'] = {'id': 'outside'}
        negs['wrongDepartureIdentity']['record']['phases']['departed']['activeTarget'] = dict(target_geo('stay'), id='outside')

        opt = make_dynamic(390, 2, 'failure', 'forward', anchor='none', layout='unreserved')
        opt['phases']['settled']['statusHeight'] += 38
        opt['phases']['settled']['activeTarget']['rect']['top'] += 38
        opt['phases']['settled']['activeTarget']['rect']['bottom'] += 38

        data = {
            'target': 'UIUX-073',
            'pass': True,
            'errors': [],
            'records': records,
            'negativeControls': negs,
            'comparisons': {'optOut': {'record': opt}}
        }
        res = audit_dynamic_status_evidence(data)
        self.assertTrue(res['passed'])
        self.assertEqual(res['matrix_records'], 36)
        self.assertEqual(res['phase_measurements'], 288)


if __name__ == '__main__':
    unittest.main()
