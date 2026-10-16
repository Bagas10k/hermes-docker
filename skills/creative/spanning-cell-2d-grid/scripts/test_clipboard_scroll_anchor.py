"""Deterministic synthetic contracts for UIUX-072; these do not count as browser evidence."""
import copy
import itertools
import unittest
from clipboard_scroll_anchor import (
    audit_scroll_anchor_record, audit_scroll_anchor_evidence, audit_target_geometry,
    WIDTHS, SCALES, OUTCOMES, DEPARTURES, REQUIRED_PHASES, SCROLL_KEYS, NEGATIVES
)
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
        e.update(seq=i, timeStamp=i, observedTime=i*10 if e['phase']!='reset' else 1800+i*10)
    for name, p in r['phases'].items():
        prefix = [e for e in r['eventTrace'] if rank[e['phase']] <= rank[name]]
        p.update(eventSeq=len(prefix), checkpointTime=(2100 if name=='reset' else 200 if name=='settled' else len(prefix)*10+.5),
                 scrollEventCount=sum(e['type'] == 'scroll' for e in prefix))
    return r


def target_geo(dep):
    return {
        'tag': 'button' if dep != 'forward' else 'g',
        'role': 'button' if dep == 'forward' else None,
        'dataNode': 'alpha' if dep == 'forward' else None,
        'dataBreadcrumbNode': 'anak-雪' if dep == 'backward' else None,
        'isCopyBtn': dep == 'stay',
        'focused': True, 'connected': True, 'hit': True,
        'viewport': {'left':0,'top':0,'right':768,'bottom':900}, 'clips': [], 'overlays': [],
        'focusVisible': True,
        'outlineStyle': 'solid',
        'outlineWidth': 2.0,
        'outlineOffset': 2.0,
        'rect': {'left': 100, 'top': 100, 'right': 200, 'bottom': 140, 'width': 100, 'height': 40},
    }


def make(vp=320, scale=1, outcome='success', departure='stay', anchor='auto'):
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
        m.update(viewport=vp, scale=scale, viewportSize={'width': vp, 'height': 900},
                 documentScrollWidth=vp, documentClientWidth=vp, state=state, label=LABELS[state],
                 statusText=STATUS.get(state, 'Versi root.'), copied=state == 'success',
                 focused=active, focusVisible=active, tabCount=1,
                 fontSamples=[{'before': 10, 'after': 10*scale}],
                 trustedClicks=int(name != 'initial'), writeCalls=int(name != 'initial'))
        scroll = dict.fromkeys(SCROLL_KEYS, 0)
        if name not in ('initial', 'pending'):
            scroll.update({'dag-scroll-outerY': 30, 'dag-scroll-innerX': 25})
        phases[name] = dict(
            phase=name, sameNode=True, isConnected=True, activeElementMatchesBtn=active,
            activeElement=copy.deepcopy(COPY if active else target),
            activeTarget=target_geo(departure if name in ('departed', 'settled', 'reset') else 'stay'),
            measurement=m, anchorPolicy=anchor,
            buttonText='Salin Rute' if name in ('initial', 'reset') else LABELS[state],
            copied=state == 'success', statusText=m['statusText'], statusHeight=100,
            trustedClicks=m['trustedClicks'], writeCalls=m['writeCalls'],
            outerScrollTop=scroll['dag-scroll-outerY'], innerScrollLeft=scroll['dag-scroll-innerX'],
            windowWidth=vp, windowHeight=900, scroll=scroll,
            containerWidth=250 if name == 'shrunk' else 280
        )
    return bind(dict(
        viewport=vp, scale=scale, outcome=outcome, departure=departure,
        anchorPolicy=anchor, layout='reserved', resetTimerExecuted=True,
        timers=[{'delay':1500,'registeredAt':150,'firedAt':1650,'calls':1}], phases=phases, eventTrace=trace
    ))


class TestClipboardScrollAnchor(unittest.TestCase):
    def rejected(self, r):
        try:
            self.assertFalse(audit_scroll_anchor_record(r)['passed'])
        except (ValueError, KeyError, TypeError):
            pass

    def test_complete_positive_matrix(self):
        for args in itertools.product(WIDTHS, SCALES, OUTCOMES, DEPARTURES):
            res = audit_scroll_anchor_record(make(*args))
            self.assertTrue(res['passed'], f"{args} -> {res.get('failures')}")

    def test_truncated_trace(self):
        r = make()
        r['eventTrace'] = r['eventTrace'][:1]
        self.rejected(r)

    def test_noncontiguous_sequence(self):
        for v in (99, 0, True, 2.5):
            r = make()
            r['eventTrace'][1]['seq'] = v
            self.rejected(r)

    def test_missing_native_departure_key(self):
        r = make(departure='forward')
        r['eventTrace'] = [e for e in r['eventTrace'] if not(e['phase'] == 'departed' and e['type'] == 'keydown')]
        self.rejected(bind(r))

    def test_untrusted_event(self):
        r = make()
        r['eventTrace'][0]['trusted'] = False
        self.rejected(r)

    def test_reset_timer_unexecuted(self):
        r = make()
        r['resetTimerExecuted'] = False
        self.assertEqual(audit_scroll_anchor_record(r)['failures'], ['reset-timer-unexecuted'])

    def test_reset_scroll_displacement(self):
        r = make()
        r['phases']['reset']['scroll']['dag-scroll-outerY'] += 38
        r['phases']['reset']['outerScrollTop'] += 38
        self.assertEqual(audit_scroll_anchor_record(r)['failures'], ['reset-scroll'])

    def test_settlement_scroll_displacement(self):
        r = make()
        r['phases']['settled']['scroll']['dag-scroll-outerY'] += 38
        r['phases']['settled']['outerScrollTop'] += 38
        r['phases']['reset']['scroll']['dag-scroll-outerY'] += 38
        r['phases']['reset']['outerScrollTop'] += 38
        self.assertEqual(audit_scroll_anchor_record(r)['failures'], ['settlement-scroll'])

    def test_reset_button_text_not_restored(self):
        r = make()
        r['phases']['reset']['buttonText'] = 'Tersalin!'
        self.assertEqual(audit_scroll_anchor_record(r)['failures'], ['button-reset-text'])

    def test_reset_focus_theft(self):
        r = make(departure='forward')
        r['eventTrace'] += [
            event('reset', 'focusout', FORWARD, COPY),
            event('reset', 'focusin', COPY, FORWARD),
            event('reset', 'focusout', COPY, FORWARD),
            event('reset', 'focusin', FORWARD, COPY)
        ]
        self.assertEqual(audit_scroll_anchor_record(bind(r))['failures'], ['no-focus-theft'])

    def test_target_geometry_failures(self):
        tg = target_geo('forward')
        self.assertEqual(audit_target_geometry(tg, 'forward'), [])

        tg_none = copy.deepcopy(tg); tg_none['outlineStyle'] = 'none'
        self.assertIn('target-outline-style', audit_target_geometry(tg_none, 'forward'))

        tg_thin = copy.deepcopy(tg); tg_thin['outlineWidth'] = 1.0
        self.assertIn('target-outline-width', audit_target_geometry(tg_thin, 'forward'))

        tg_unfocused = copy.deepcopy(tg); tg_unfocused['focused'] = False
        self.assertIn('target-unfocused', audit_target_geometry(tg_unfocused, 'forward'))

        tg_not_vis = copy.deepcopy(tg); tg_not_vis['focusVisible'] = False
        self.assertIn('target-not-focus-visible', audit_target_geometry(tg_not_vis, 'forward'))

    def test_target_offscreen_and_clip_axis(self):
        for changes in ({'rect':{'left':-200,'top':100,'right':-100,'bottom':140,'width':100,'height':40}},
                        {'clips':[{'left':0,'top':0,'right':150,'bottom':900,'x':True,'y':False}]}):
            self.assertIn('target-clipping',audit_target_geometry(dict(target_geo('forward'),**changes),'forward'))

    def test_pointer_events_none_overlay(self):
        t=target_geo('forward'); t['overlays']=[dict(left=196,top=100,right=204,bottom=140)]
        self.assertTrue(t['hit'])
        self.assertIn('target-occlusion',audit_target_geometry(t,'forward'))

    def test_invalid_target_geometry_fail_closed(self):
        for field,value in (('left',float('nan')),('width',True),('right',float('inf'))):
            r=make(departure='forward'); r['phases']['settled']['activeTarget']['rect'][field]=value
            self.rejected(r)

    def test_native_timer_deadline_and_execution(self):
        for patch in ({'firedAt':1600},{'calls':0},{'calls':2},{'delay':1000}):
            r=make(); r['timers'][0].update(patch)
            self.assertIn('native-timer-deadline',audit_scroll_anchor_record(r)['failures'])

    def test_layout_change_without_scroll(self):
        r=make(departure='forward'); p=r['phases']['settled']
        p['statusHeight']+=38; p['activeTarget']['rect']['top']+=38; p['activeTarget']['rect']['bottom']+=38
        self.assertEqual(audit_scroll_anchor_record(r)['failures'],['status-height','target-position'])

    def test_exact_status_reset(self):
        r=make(); r['phases']['reset']['statusText']='Versi stale.'
        self.assertIn('status-reset-text',audit_scroll_anchor_record(r)['failures'])

    def test_evidence_structure_and_duplicate_matrix(self):
        records = [make(*a) for a in itertools.product(WIDTHS, SCALES, OUTCOMES, DEPARTURES)]
        negs = {
            'targetClipped': {'record': make(320, 1, 'success', 'forward')},
            'targetCovered': {'record': make(320, 1, 'success', 'forward')},
            'oldUnstableAuto': {'record': make(390, 2, 'failure', 'forward')},
            'transientBlurRefocus': {'record': make(320, 1, 'success', 'stay')},
            'completionFocusTheft': {'record': make(320, 1, 'success', 'forward')},
            'completionStealReturn': {'record': make(320, 1, 'success', 'forward')},
            'resetFocusTheft': {'record': make(320, 1, 'success', 'forward')},
            'transientResetScroll': {'record': make(320, 1, 'success', 'stay')},
            'wrongDepartureIdentity': {'record': make(320, 1, 'success', 'forward')},
        }
        # inject expected faults
        negs['oldUnstableAuto']['record']['layout']='unreserved'
        negs['targetClipped']['record']['phases']['reset']['activeTarget']['clips']=[{'left':0,'top':0,'right':150,'bottom':900,'x':True,'y':True}]
        negs['targetCovered']['record']['phases']['reset']['activeTarget']['overlays']=[{'left':100,'top':100,'right':200,'bottom':140}]
        negs['oldUnstableAuto']['record']['phases']['settled']['scroll']['dag-scroll-outerY'] += 38
        negs['oldUnstableAuto']['record']['phases']['settled']['outerScrollTop'] += 38
        negs['oldUnstableAuto']['record']['phases']['reset']['scroll']['dag-scroll-outerY'] += 38
        negs['oldUnstableAuto']['record']['phases']['reset']['outerScrollTop'] += 38
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

        data = {
            'target': 'UIUX-072',
            'pass': True,
            'errors': [],
            'records': records,
            'negativeControls': negs,
            'comparisons': {'optOut': {'record': make(390, 2, 'failure', 'forward', anchor='none')}}
        }
        opt=data['comparisons']['optOut']['record']; opt['layout']='unreserved'
        opt['phases']['settled']['statusHeight']+=38
        opt['phases']['settled']['activeTarget']['rect']['top']+=38
        opt['phases']['settled']['activeTarget']['rect']['bottom']+=38
        res = audit_scroll_anchor_evidence(data)
        self.assertTrue(res['passed'])
        self.assertEqual(res['matrix_records'], 36)
        self.assertEqual(res['phase_measurements'], 288)
        absent=copy.deepcopy(data); absent['comparisons']={}
        with self.assertRaises(ValueError): audit_scroll_anchor_evidence(absent)
        duplicated=copy.deepcopy(data); duplicated['records'].append(copy.deepcopy(duplicated['records'][0]))
        with self.assertRaises(ValueError): audit_scroll_anchor_evidence(duplicated)


if __name__ == '__main__':
    unittest.main()
