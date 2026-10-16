"""Deterministic synthetic contracts; these do not count as browser evidence."""
import copy
import itertools
import unittest
from clipboard_focus_events import (audit_focus_record, audit_focus_evidence, check_node_identity,
    WIDTHS, SCALES, OUTCOMES, DEPARTURES, REQUIRED_PHASES, SCROLL_KEYS)
from clipboard_focus_reflow import LABELS, STATUS
from test_clipboard_focus_reflow import record as geometry

COPY = {'tag': 'button', 'isCopyBtn': True}
FORWARD = {'tag': 'g', 'role': 'button', 'dataNode': 'alpha'}
BACKWARD = {'tag': 'button', 'dataBreadcrumbNode': 'anak-雪'}


def event(phase, kind, target=COPY, related=None, key=None, shift=False):
    return dict(phase=phase, type=kind, target=copy.deepcopy(target), relatedTarget=copy.deepcopy(related),
                key=key, shiftKey=shift, trusted=True)


def bind(r):
    """Build synthetic contiguous checkpoint times; never rewrites real evidence."""
    rank = {p: i for i, p in enumerate(('setup', *REQUIRED_PHASES))}
    r['eventTrace'].sort(key=lambda e: rank[e['phase']])
    for i, e in enumerate(r['eventTrace'], 1):
        e.update(seq=i, timeStamp=i, observedTime=i)
    for name, p in r['phases'].items():
        prefix = [e for e in r['eventTrace'] if rank[e['phase']] <= rank[name]]
        p.update(eventSeq=len(prefix), checkpointTime=len(prefix) + .5,
                 scrollEventCount=sum(e['type'] == 'scroll' for e in prefix))
    return r


def make(vp=320, scale=1, outcome='success', departure='stay'):
    target = FORWARD if departure == 'forward' else BACKWARD
    trace = [event('setup', 'keydown', key='Tab'), event('setup', 'focusin'),
             event('pending', 'keydown', key='Enter'), event('scrolled', 'scroll', {'id': 'dag-scroll-outer'}),
             event('scrolled', 'scroll', {'id': 'dag-scroll-inner'})]
    if departure != 'stay':
        trace.extend([event('departed', 'keydown', key='Tab', shift=departure == 'backward'),
                      event('departed', 'focusout', COPY, target), event('departed', 'focusin', target, COPY)])
    phases = {}
    for name in REQUIRED_PHASES:
        active = departure == 'stay' or name not in ('departed', 'settled')
        state = 'idle' if name == 'initial' else outcome if name == 'settled' else 'pending'
        m = geometry()
        m.update(viewport=vp, scale=scale, viewportSize={'width': vp, 'height': 900},
                 documentScrollWidth=vp, documentClientWidth=vp, state=state, label=LABELS[state],
                 statusText=STATUS.get(state, 'Versi root.'), copied=state == 'success',
                 focused=active, focusVisible=active, tabCount=1,
                 fontSamples=[{'before': 10, 'after': 10*scale}],
                 trustedClicks=int(name != 'initial'), writeCalls=int(name != 'initial'))
        scroll = dict.fromkeys(SCROLL_KEYS, 0)
        if name not in ('initial', 'pending'):
            scroll.update({'dag-scroll-outerY': 30, 'dag-scroll-innerX': 25})
        phases[name] = dict(phase=name, sameNode=True, isConnected=True, activeElementMatchesBtn=active,
            activeElement=copy.deepcopy(COPY if active else target), measurement=m, anchorPolicy='none',
            trustedClicks=m['trustedClicks'], writeCalls=m['writeCalls'], outerScrollTop=scroll['dag-scroll-outerY'],
            innerScrollLeft=scroll['dag-scroll-innerX'], windowWidth=vp, windowHeight=900, scroll=scroll,
            containerWidth=250 if name == 'shrunk' else 280)
    return bind(dict(viewport=vp, scale=scale, outcome=outcome, departure=departure,
                     anchorPolicy='none', phases=phases, eventTrace=trace))


class TestFocusEvents(unittest.TestCase):
    def rejected(self, r):
        try:
            self.assertFalse(audit_focus_record(r)['passed'])
        except (ValueError, KeyError, TypeError):
            pass

    def test_complete_positive_matrix(self):
        for args in itertools.product(WIDTHS, SCALES, OUTCOMES, DEPARTURES):
            self.assertTrue(audit_focus_record(make(*args))['passed'], args)

    def test_truncated_trace(self):
        r = make(); r['eventTrace'] = r['eventTrace'][:1]; self.rejected(r)

    def test_gap_or_duplicate_sequence(self):
        for v in (1, 99, True, 2.5):
            r = make(); r['eventTrace'][1]['seq'] = v; self.rejected(r)

    def test_missing_setup_focus_even_rebound(self):
        r = make(); r['eventTrace'] = [e for e in r['eventTrace'] if e['type'] != 'focusin']; self.rejected(bind(r))

    def test_missing_native_departure_key(self):
        r = make(departure='forward')
        r['eventTrace'] = [e for e in r['eventTrace'] if not(e['phase'] == 'departed' and e['type'] == 'keydown')]
        self.rejected(bind(r))

    def test_untrusted_key_and_wrong_shift(self):
        for field, val in [('trusted', False), ('shiftKey', True)]:
            r = make(departure='forward')
            next(e for e in r['eventTrace'] if e['phase'] == 'departed' and e['type'] == 'keydown')[field] = val
            self.rejected(r)

    def test_checkpoint_bound_and_relabel(self):
        r = make(); r['phases']['initial']['eventSeq'] += 1; self.rejected(r)
        r = make(); r['eventTrace'][-1]['phase'] = 'setup'; self.rejected(r)

    def test_checkpoint_scroll_counter(self):
        r = make(); r['phases']['settled']['scrollEventCount'] += 1; self.rejected(r)

    def test_nonfinite_clock_and_extents(self):
        for v in (float('nan'), float('inf'), True, '1'):
            r = make(); r['eventTrace'][0]['observedTime'] = v; self.rejected(r)
            r = make(); r['phases']['pending']['containerWidth'] = v; self.rejected(r)

    def test_snapshot_phase_state_binding(self):
        r = make(); r['phases']['shrunk']['measurement'] = copy.deepcopy(r['phases']['settled']['measurement']); self.rejected(r)

    def test_transient_blur_refocus(self):
        r = make(); r['eventTrace'] += [event('shrunk','focusout'),event('shrunk','focusin')]
        a = audit_focus_record(bind(r)); self.assertEqual(a['failures'], ['no-transient-glitch'])

    def test_settlement_steal_return(self):
        r = make(departure='forward')
        r['eventTrace'] += [event('settled','focusout',FORWARD,COPY),event('settled','focusin',COPY,FORWARD),
                            event('settled','focusout',COPY,FORWARD),event('settled','focusin',FORWARD,COPY)]
        self.assertEqual(audit_focus_record(bind(r))['failures'], ['no-focus-theft'])

    def test_scroll_restore_snapshot_unchanged(self):
        r = make(); r['eventTrace'] += [event('settled','scroll',{'id':'dag-scroll-outer'})]
        self.assertEqual(audit_focus_record(bind(r))['failures'], ['settlement-scroll'])

    def test_all_scroll_targets_including_window_and_dag(self):
        for k in SCROLL_KEYS:
            r = make(); r['phases']['settled']['scroll'][k] += 1; self.rejected(r)

    def test_wrong_neighbors_both_directions(self):
        for dep in ('forward', 'backward'):
            r = make(departure=dep); r['phases']['departed']['activeElement'] = COPY; self.rejected(r)

    def test_exact_copy_identity_not_class_substring(self):
        self.assertFalse(check_node_identity({'tag':'button','className':'not-dag-breadcrumb-copy-btn'},'stay'))

    def test_departed_false_focus_and_known_overlay(self):
        r = make(departure='backward'); r['phases']['settled']['measurement']['focused'] = True; self.rejected(r)
        r = make(departure='backward')
        r['phases']['settled']['measurement']['opaqueOverlays'] = [{'left':20,'top':20,'right':30,'bottom':30}]
        self.rejected(r)

    def test_missing_phase_and_wrong_coordinates(self):
        r = make(); del r['phases']['regrown']; self.rejected(r)
        r = make(); r['viewport'] = True; self.rejected(r)

    def test_gate_rejects_duplicate_matrix(self):
        records = [make(*a) for a in itertools.product(WIDTHS, SCALES, OUTCOMES, DEPARTURES)]
        records[-1] = records[0]
        with self.assertRaises(ValueError):
            audit_focus_evidence(dict(target='UIUX-071',pass_=True,errors=[],records=records,**{'pass':True}))

    def test_gate_refuses_empty_negative_controls(self):
        records = [make(*a) for a in itertools.product(WIDTHS, SCALES, OUTCOMES, DEPARTURES)]
        with self.assertRaises(ValueError):
            audit_focus_evidence(dict(target='UIUX-071',errors=[],records=records,negativeControls={},**{'pass':True}))


if __name__ == '__main__':
    unittest.main()
