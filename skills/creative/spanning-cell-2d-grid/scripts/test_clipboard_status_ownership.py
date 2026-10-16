"""UIUX-074: Deterministic unit tests for dynamic status ownership and race gate."""
import copy
import itertools
import unittest

from clipboard_status_ownership import (
    SCENARIOS, WIDTHS, SCALES, NEGATIVES_074,
    audit_ownership_record as raw_record, audit_ownership_evidence as raw_evidence,
    INITIAL_REVISION_ID, TARGET_REVISION_ID,
    INITIAL_IDLE_TEXT, TARGET_IDLE_TEXT
)


def bind(r):
    for field,counter in (('eventTrace','eventSeq'),('mutationTrace','mutationSeq')):
        for i,e in enumerate(r[field]):
            e['seq'] = i+1
            e['observedTime'] = 90+i
        for p in r['phases'].values():
            p[counter] = len(r[field])
    return r


def audit_ownership_record(r):
    return raw_record(bind(r))


def audit_ownership_evidence(d):
    for r in d['records']:
        bind(r)
    for n in d['negativeControls'].values():
        bind(n['record'])
    return raw_evidence(d)


def event(phase, ev_type, target=None, related=None, seq=1):
    return {
        'seq': seq,
        'phase': phase,
        'type': ev_type,
        'target': target or {'tag': 'button', 'isCopyBtn': True},
        'relatedTarget': related,
        'timeStamp': 100.0,
        'observedTime': 100.0,
        'trusted': True,
        'key': None,
        'shiftKey': False
    }


def mutation(phase, target_id, old_text, new_text, seq=1):
    return {
        'seq': seq,
        'phase': phase,
        'targetId': target_id,
        'oldText': old_text,
        'newText': new_text,
        'observedTime': 100.0 + seq
    }


def make_ownership_record(scenario='pendingCheckoutSuccess', vp=320, scale=1):
    phases = {}
    is_pipelined = scenario == 'pipelinedRequest'
    is_disposed = scenario in ('settledDisposeReset', 'pendingDispose')
    is_settled_race = scenario in ('settledCheckoutReset', 'settledDisposeReset')

    # Base phases: initial, pending, checkout (or action), settled, completed
    phase_names = ['initial', 'pending', 'checkout', 'settled', 'completed']

    seq = 0
    mutations = [
        mutation('initial', 'status', '', INITIAL_IDLE_TEXT, seq=1),
        mutation('initial', 'dag-status-reserve-idle', '', INITIAL_IDLE_TEXT, seq=2),
    ]
    events = [
        event('initial', 'focusin', {'tag': 'button', 'isCopyBtn': True}, seq=1)
    ]

    for name in phase_names:
        if name in ('initial', 'pending'):
            cur_id = INITIAL_REVISION_ID
            idle_text = INITIAL_IDLE_TEXT
        else:
            cur_id = TARGET_REVISION_ID if not is_disposed or scenario == 'settledCheckoutReset' else (
                INITIAL_REVISION_ID if scenario in ('settledDisposeReset', 'pendingDispose') else TARGET_REVISION_ID
            )
            idle_text = INITIAL_IDLE_TEXT if cur_id == INITIAL_REVISION_ID else TARGET_IDLE_TEXT

        # Status & button texts per phase & scenario
        if name == 'initial':
            st_text = INITIAL_IDLE_TEXT
            res_text = INITIAL_IDLE_TEXT
            btn_text = 'Salin Rute'
            copied = False
        elif name == 'pending':
            st_text = 'Menyalin silsilah rute ke clipboard…'
            res_text = INITIAL_IDLE_TEXT
            btn_text = 'Menyalin…'
            copied = False
            mutations.append(mutation('pending', 'status', INITIAL_IDLE_TEXT, st_text, seq=3))
        elif name == 'checkout':
            st_text = idle_text
            res_text = idle_text
            btn_text = 'Salin Rute'
            copied = False
            mutations.append(mutation('checkout', 'status', 'Menyalin silsilah rute ke clipboard…', st_text, seq=4))
            mutations.append(mutation('checkout', 'dag-status-reserve-idle', INITIAL_IDLE_TEXT, res_text, seq=5))
        elif name == 'settled':
            if is_settled_race:
                # Settle happened before checkout in settledCheckoutReset/settledDisposeReset
                st_text = idle_text
                res_text = idle_text
                btn_text = 'Salin Rute'
                copied = False
            elif is_pipelined:
                # Pipelined req2 is pending
                st_text = 'Menyalin silsilah rute ke clipboard…'
                res_text = TARGET_IDLE_TEXT
                btn_text = 'Menyalin…'
                copied = False
            else:
                # Stale old promise settled; must NOT touch current idle status
                st_text = idle_text
                res_text = idle_text
                btn_text = 'Salin Rute'
                copied = False
        elif name == 'completed':
            st_text = idle_text
            res_text = idle_text
            btn_text = 'Salin Rute'
            copied = False

        phases[name] = {
            'phase': name,
            'cursor': cur_id,
            'statusText': st_text,
            'reservationText': res_text,
            'buttonText': btn_text,
            'buttonDisabled': is_disposed and name in ('checkout', 'settled', 'completed'),
            'copied': copied,
            'activeElementMatchesCurrentButton': True if name == 'initial' else (not is_disposed),
            'activeElement': {
                'tag': 'button',
                'isCopyBtn': True,
                'dataBreadcrumbNode': cur_id if name != 'initial' else INITIAL_REVISION_ID
            },
            'statusHeight': 120.0,
            'statusClientWidth': 280.0,
            'statusScrollWidth': 280.0,
            'containerWidth': 280.0,
            'statusTextFits': True,
            'breadcrumbTextFits': True,
            'checkpointTime': 100.0 + len(phases) * 50
        }

    # Timer evidence
    timers = []
    if is_settled_race:
        # Timer was registered on initial revision, but cleared on checkout/dispose
        timers.append({
            'id': 1,
            'delay': 1500,
            'registeredAt': 120.0,
            'clearedAt': 180.0,
            'firedAt': None,
            'calls': 0,
            'cancelled': True
        })
    elif is_pipelined:
        # Req2 timer registered and executed after req2 settled
        timers.append({
            'id': 2,
            'delay': 1500,
            'registeredAt': 200.0,
            'clearedAt': None,
            'firedAt': 1700.5,
            'calls': 1,
            'cancelled': False
        })

    # Deterministic observations: current checkout focus is undo, disposal releases to body.
    for index, name in enumerate(phase_names):
        phases[name]['checkpointTime'] = (100, 150, 250, 300, 2000)[index]
        if name in ('checkout', 'settled', 'completed'):
            phases[name]['activeElement'] = {'tag': 'body' if is_disposed else 'button', 'id': None if is_disposed else 'undo', 'isCopyBtn': False}
    events.append(event('checkout', 'focusout', {'tag':'button','isCopyBtn':True}, seq=2))
    if not is_disposed:
        events.append(event('checkout', 'focusin', {'tag':'button','id':'undo','isCopyBtn':False}, seq=3))
    if timers:
        timers[0]['registeredAt'] = 180 if is_settled_race else 350
        if is_settled_race:
            timers[0]['clearedAt'] = 200
        else:
            timers[0]['firedAt'] = 1850.5

    for name,p in phases.items():
        original = name in ('initial','pending') or is_disposed
        p.update(sameInitialButton=original, initialButtonConnected=original, currentButtonConnected=True,
                 fontScaleVerified=True, eventSeq=len(events), mutationSeq=len(mutations), buttonSeq=0,
                 scroll={'x':0,'y':0}, activeRect={'left':0,'top':0,'right':20,'bottom':20})
    return {
        'buttonTrace': [],
        'scenario': scenario,
        'viewport': vp,
        'scale': scale,
        'initialCursor': INITIAL_REVISION_ID,
        'targetCursor': TARGET_REVISION_ID if not (is_disposed and scenario != 'settledCheckoutReset') else INITIAL_REVISION_ID,
        'phases': phases,
        'mutationTrace': mutations,
        'eventTrace': events,
        'timers': timers,
        'passed': True
    }


class TestClipboardStatusOwnership(unittest.TestCase):
    def test_positive_record_passes(self):
        for scenario in SCENARIOS:
            r = make_ownership_record(scenario=scenario)
            res = audit_ownership_record(r)
            self.assertTrue(res['passed'], f"Scenario {scenario} failed: {res.get('failures')}")
            self.assertEqual(res['failures'], [])

    def test_stale_status_write_fails(self):
        """Old promise settlement writing stale success text to status is rejected."""
        r = make_ownership_record(scenario='pendingCheckoutSuccess')
        r['phases']['settled']['statusText'] = 'Silsilah rute berhasil disalin ke clipboard'
        res = audit_ownership_record(r)
        self.assertFalse(res['passed'])
        self.assertIn('ownership-status-text', res['failures'])

    def test_stale_shadow_write_fails(self):
        """Old settlement writing to shadow idle reservation is rejected."""
        r = make_ownership_record(scenario='pendingCheckoutSuccess')
        r['phases']['settled']['reservationText'] = INITIAL_IDLE_TEXT
        res = audit_ownership_record(r)
        self.assertFalse(res['passed'])
        self.assertIn('ownership-shadow-text', res['failures'])

    def test_transient_stale_write_detected_by_mutation_trace(self):
        """Transient stale write that was quickly restored is caught by continuous mutation trace."""
        r = make_ownership_record(scenario='pendingCheckoutSuccess')
        # Inject transient mutation during settled phase
        r['mutationTrace'].append(mutation('settled', 'status', TARGET_IDLE_TEXT, 'Silsilah rute berhasil disalin ke clipboard', seq=len(r['mutationTrace']) + 1))
        r['mutationTrace'].append(mutation('settled', 'status', 'Silsilah rute berhasil disalin ke clipboard', TARGET_IDLE_TEXT, seq=len(r['mutationTrace']) + 1))
        res = audit_ownership_record(r)
        self.assertFalse(res['passed'])
        self.assertIn('continuous-mutation-violation', res['failures'])

    def test_stale_focus_theft_fails(self):
        """Active focus stolen by old disconnected copy button is rejected."""
        r = make_ownership_record(scenario='pendingCheckoutSuccess')
        r['phases']['settled']['activeElement'] = {'tag': 'button', 'isCopyBtn': True, 'dataBreadcrumbNode': INITIAL_REVISION_ID}
        res = audit_ownership_record(r)
        self.assertFalse(res['passed'])
        self.assertIn('stale-focus-theft', res['failures'])

    def test_transient_focus_steal_return_caught_by_event_trace(self):
        """Focus stolen momentarily and returned is caught by continuous event trace."""
        r = make_ownership_record(scenario='pendingCheckoutSuccess')
        r['eventTrace'].extend([
            event('settled', 'focusout', {'tag': 'button', 'dataBreadcrumbNode': TARGET_REVISION_ID}, seq=len(r['eventTrace']) + 1),
            event('settled', 'focusin', {'tag': 'button', 'dataBreadcrumbNode': INITIAL_REVISION_ID}, seq=len(r['eventTrace']) + 2),
            event('settled', 'focusout', {'tag': 'button', 'dataBreadcrumbNode': INITIAL_REVISION_ID}, seq=len(r['eventTrace']) + 3),
            event('settled', 'focusin', {'tag': 'button', 'dataBreadcrumbNode': TARGET_REVISION_ID}, seq=len(r['eventTrace']) + 4),
        ])
        res = audit_ownership_record(r)
        self.assertFalse(res['passed'])
        self.assertIn('no-focus-theft', res['failures'])

    def test_stale_timer_execution_fails(self):
        """Timer not cancelled in settled checkout race that fires is rejected."""
        r = make_ownership_record(scenario='settledCheckoutReset')
        r['timers'][0]['firedAt'] = 1620.0
        r['timers'][0]['calls'] = 1
        r['timers'][0]['cancelled'] = False
        res = audit_ownership_record(r)
        self.assertFalse(res['passed'])
        self.assertIn('stale-timer-fired', res['failures'])

    def test_disowned_button_active_fails(self):
        """Disowned old button remaining marked as copied is rejected."""
        r = make_ownership_record(scenario='pendingCheckoutSuccess')
        r['phases']['settled']['copied'] = True
        res = audit_ownership_record(r)
        self.assertFalse(res['passed'])
        self.assertIn('disowned-button-state', res['failures'])

    def test_pipelined_contamination_fails(self):
        """In pipelined request, req1 settling cancels or corrupts req2."""
        r = make_ownership_record(scenario='pipelinedRequest')
        r['phases']['settled']['buttonText'] = 'Salin Rute' # Req2 was pending, should still be 'Menyalin…'
        res = audit_ownership_record(r)
        self.assertFalse(res['passed'])
        self.assertIn('pipelined-request-corrupted', res['failures'])

    def test_timer_early_fire_fails(self):
        """Timer in pipelined request firing before 1499ms is rejected."""
        r = make_ownership_record(scenario='pipelinedRequest')
        r['timers'][0]['firedAt'] = r['timers'][0]['registeredAt'] + 500 # fired in 500ms
        res = audit_ownership_record(r)
        self.assertFalse(res['passed'])
        self.assertIn('native-timer-deadline', res['failures'])

    def test_cursor_ownership_mismatch_fails(self):
        """Cursor reported does not match expected revision ID for phase."""
        r = make_ownership_record(scenario='pendingCheckoutSuccess')
        r['phases']['checkout']['cursor'] = 'wrong-cursor-id'
        res = audit_ownership_record(r)
        self.assertFalse(res['passed'])
        self.assertIn('cursor-ownership-mismatch', res['failures'])

    def test_full_evidence_structure_passes(self):
        records = [
            make_ownership_record(scenario=sc, vp=vp, scale=sc_val)
            for sc in SCENARIOS
            for vp in WIDTHS
            for sc_val in SCALES
        ]
        self.assertEqual(len(records), 36)

        # Build negative controls matching NEGATIVES_074
        negs = {}
        for fault in NEGATIVES_074:
            rec = make_ownership_record(scenario='pendingCheckoutSuccess')
            if fault == 'staleStatusWrite':
                rec['phases']['settled']['statusText'] = 'Silsilah rute berhasil disalin ke clipboard'
            elif fault == 'staleShadowWrite':
                rec['phases']['settled']['reservationText'] = INITIAL_IDLE_TEXT
            elif fault == 'transientStaleWrite':
                rec['mutationTrace'].append(mutation('settled', 'status', TARGET_IDLE_TEXT, 'Silsilah rute berhasil disalin ke clipboard', seq=len(rec['mutationTrace']) + 1))
            elif fault == 'staleFocusTheft':
                rec['phases']['settled']['activeElement'] = {'tag': 'button', 'isCopyBtn': True, 'dataBreadcrumbNode': INITIAL_REVISION_ID}
            elif fault == 'transientFocusStealReturn':
                rec['eventTrace'].extend([
                    event('settled', 'focusout', {'tag': 'button', 'dataBreadcrumbNode': TARGET_REVISION_ID}, seq=len(rec['eventTrace']) + 1),
                    event('settled', 'focusin', {'tag': 'button', 'dataBreadcrumbNode': INITIAL_REVISION_ID}, seq=len(rec['eventTrace']) + 2),
                ])
            elif fault == 'staleTimerExecution':
                rec = make_ownership_record(scenario='settledCheckoutReset')
                rec['timers'][0]['firedAt'] = 1620.0
                rec['timers'][0]['calls'] = 1
                rec['timers'][0]['cancelled'] = False
            elif fault == 'disownedButtonActive':
                rec['phases']['settled']['copied'] = True
            elif fault == 'pipelinedContamination':
                rec = make_ownership_record(scenario='pipelinedRequest')
                rec['phases']['settled']['buttonText'] = 'Salin Rute'
            elif fault == 'timerEarlyFire':
                rec = make_ownership_record(scenario='pipelinedRequest')
                rec['timers'][0]['firedAt'] = rec['timers'][0]['registeredAt'] + 500
            elif fault == 'wrongCursorOwnership':
                rec['phases']['checkout']['cursor'] = 'wrong-cursor-id'
            negs[fault] = {'record': rec}

        data = {
            'target': 'UIUX-074',
            'pass': True,
            'browser': 'Chromium 156.0.8078.4',
            'errors': [],
            'records': records,
            'negativeControls': negs
        }
        res = audit_ownership_evidence(data)
        self.assertTrue(res['passed'], f"Audit failed: {res}")
        self.assertEqual(res['matrix_records'], 36)
        self.assertEqual(len(res['negative_controls']), len(NEGATIVES_074))


if __name__ == '__main__':
    unittest.main()
