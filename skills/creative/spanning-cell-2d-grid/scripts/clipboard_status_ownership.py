"""UIUX-074: Validator for dynamic status ownership during pending clipboard checkout and stale reset."""
import itertools
import json
import sys
from pathlib import Path

from clipboard_focus_reflow import number

INITIAL_REVISION_ID = 'feat/virtualized-2d-grid-with-asymmetric-spans-and-history-c98f820b784913c98b671a5392812d4a7536901234567890abcdef'
TARGET_REVISION_ID = 'cabang-rekonsiliasi-jejak-audit-terdistribusi-skala-2026'

INITIAL_IDLE_TEXT = f'Versi {INITIAL_REVISION_ID}. 0 cabang lanjutan.'
TARGET_IDLE_TEXT = f'Versi {TARGET_REVISION_ID}. 0 cabang lanjutan.'

SCENARIOS = (
    'pendingCheckoutSuccess',
    'pendingCheckoutFailure',
    'settledCheckoutReset',
    'settledDisposeReset',
    'pipelinedRequest',
    'pendingDispose'
)

WIDTHS = (320, 390, 768)
SCALES = (1, 2)

REQUIRED_PHASES = ('initial', 'pending', 'checkout', 'settled', 'completed')

STALE_MESSAGES = {
    'Silsilah rute berhasil disalin ke clipboard',
    'Gagal menyalin silsilah rute ke clipboard',
    'Menyalin silsilah rute ke clipboard…'
}

NEGATIVES_074 = {
    'staleStatusWrite': 'ownership-status-text',
    'staleShadowWrite': 'ownership-shadow-text',
    'transientStaleWrite': 'continuous-mutation-violation',
    'staleFocusTheft': 'stale-focus-theft',
    'transientFocusStealReturn': 'no-focus-theft',
    'staleTimerExecution': 'stale-timer-fired',
    'disownedButtonActive': 'disowned-button-state',
    'pipelinedContamination': 'pipelined-request-corrupted',
    'wrongCursorOwnership': 'cursor-ownership-mismatch',
    'timerEarlyFire': 'native-timer-deadline',
}


def audit_ownership_record(record):
    """Audit single sequence record across race and ownership lifecycle phases."""
    scenario = record.get('scenario')
    if scenario not in SCENARIOS:
        raise ValueError(f'Invalid scenario: {scenario}')
    vp = record.get('viewport')
    scale = record.get('scale')
    if type(vp) is not int or type(scale) is not int or vp not in WIDTHS or scale not in SCALES:
        raise ValueError(f'Invalid matrix coordinate: vp={vp}, scale={scale}')

    phases = record.get('phases')
    if type(phases) is not dict or set(phases) != set(REQUIRED_PHASES):
        raise ValueError('Phases incomplete or invalid')

    mutations = record.get('mutationTrace', [])
    events = record.get('eventTrace', [])
    timers = record.get('timers', [])

    if type(mutations) is not list or type(events) is not list or type(timers) is not list:
        raise ValueError('Mutation trace, event trace, and timers must be lists')

    failures = []
    is_pipelined = scenario == 'pipelinedRequest'
    is_disposed = scenario in ('settledDisposeReset', 'pendingDispose')
    is_settled_race = scenario in ('settledCheckoutReset', 'settledDisposeReset')

    # No default-empty evidence: a missing trace cannot prove absence of races.
    for field in ('mutationTrace', 'eventTrace', 'timers'):
        if field not in record or type(record[field]) is not list:
            raise ValueError('Missing trace: ' + field)
    if not mutations or not events:
        raise ValueError('Empty continuous trace')
    times = [number(phases[n]['checkpointTime']) for n in REQUIRED_PHASES]
    if times != sorted(times) or len(set(times)) != len(times):
        raise ValueError('Non-monotonic checkpoints')
    for trace in (mutations, events):
        if [e['seq'] for e in trace] != list(range(1, len(trace) + 1)):
            raise ValueError('Trace sequence truncated/duplicated')
        observed = [number(e['observedTime']) for e in trace]
        if observed != sorted(observed) or observed[-1] > times[-1]:
            raise ValueError('Trace outside observation window')
        if any(e['phase'] not in ('setup', *REQUIRED_PHASES) for e in trace):
            raise ValueError('Unknown trace phase')
    if not any(m['phase'] == 'pending' and m['targetId'] == 'status' for m in mutations):
        raise ValueError('Missing pending mutation')
    if not any(m['phase'] == 'checkout' and m['targetId'] == 'dag-status-reserve-idle' for m in mutations):
        raise ValueError('Missing checkout reservation mutation')
    for name, p in phases.items():
        if p.get('statusTextFits') is not True or p.get('breadcrumbTextFits') is not True:
            failures.append('text-fit')
        if number(p['statusHeight']) <= 0 or number(p['statusClientWidth']) <= 0:
            raise ValueError('Empty status geometry')
        if number(p['statusScrollWidth']) > number(p['statusClientWidth']) + 1:
            failures.append('status-overflow')
        if p.get('buttonDisabled') is not (is_disposed and name in ('checkout','settled','completed')):
            failures.append('button-disabled')
    # Different revisions may have different intrinsic heights; only late work must be inert.
    if abs(number(phases['initial']['statusHeight']) - number(phases['pending']['statusHeight'])) > .01:
        failures.append('status-height')
    for name in ('settled', 'completed'):
        if abs(number(phases[name]['statusHeight']) - number(phases['checkout']['statusHeight'])) > .01:
            failures.append('status-height')
        if phases[name]['scroll'] != phases['checkout']['scroll']:
            failures.append('late-scroll')
        if any(abs(number(phases[name]['activeRect'][k])-number(phases['checkout']['activeRect'][k])) > .1 for k in ('left','top','right','bottom')):
            failures.append('late-target-position')
        if phases[name]['activeElement'] != phases['checkout']['activeElement']:
            failures.append('stale-focus-theft')
    for e in events:
        if e['phase'] in ('settled', 'completed') and e['type'] in ('focusin','focusout'):
            failures.append('no-focus-theft')
    checkout_focus = [e for e in events if e['phase'] == 'checkout' and e['type'] == 'focusin']
    if not is_disposed and (len(checkout_focus) != 1 or checkout_focus[0]['target'].get('id') != 'undo'):
        failures.append('checkout-focus-detour')
    if is_disposed and checkout_focus:
        failures.append('checkout-focus-detour')
    for m in mutations:
        if m['phase'] in ('checkout','settled','completed'):
            idle = INITIAL_IDLE_TEXT if is_disposed else TARGET_IDLE_TEXT
            allowed = {idle}
            if is_pipelined and m['targetId'] == 'status':
                if m['phase'] == 'checkout':
                    allowed.add('Menyalin silsilah rute ke clipboard…')
                elif m['phase'] == 'settled':
                    allowed = {'Menyalin silsilah rute ke clipboard…'}
                else:
                    allowed.add('Silsilah rute berhasil disalin ke clipboard')
            if m['targetId'] not in ('status','dag-status-reserve-idle') or m['newText'] not in allowed:
                failures.append('continuous-mutation-violation')
    if len(timers) != (1 if is_settled_race or is_pipelined else 0):
        failures.append('unexpected-timer-count')
    for t in timers:
        registered = number(t['registeredAt'])
        if t['delay'] != 1500 or registered < times[1] or registered > times[-1]:
            failures.append('native-timer-deadline')
        if is_settled_race:
            cleared = number(t['clearedAt'])
            if not registered <= cleared <= times[2] or times[-1] < registered + 1500:
                failures.append('unobserved-cancelled-deadline')
        if is_pipelined:
            fired = number(t['firedAt'])
            if t['calls'] != 1 or t['cancelled'] is not False or not times[3] <= registered <= fired <= times[-1]:
                failures.append('native-timer-deadline')

    # Bind both continuous text and focus traces to checkpoint counters (reject missing suffixes).
    for field, counter in (('eventTrace','eventSeq'), ('mutationTrace','mutationSeq'), ('buttonTrace','buttonSeq')):
        trace = record[field]
        if type(trace) is not list:
            raise ValueError('Invalid trace')
        start = 0
        for name in REQUIRED_PHASES:
            p = phases[name]; end = p[counter]
            if type(end) is not int or not start <= end <= len(trace):
                raise ValueError('Invalid trace checkpoint')
            if any(e['seq'] != i + 1 for i,e in enumerate(trace)):
                raise ValueError('Noncontiguous trace')
            start = end
        if start != len(trace):
            raise ValueError('Unobserved trace suffix')
        if trace and number(trace[-1]['observedTime']) > times[-1]:
            raise ValueError('Unobserved late trace')
    for name,p in phases.items():
        original = name in ('initial','pending') or is_disposed
        if p['sameInitialButton'] is not original or p['initialButtonConnected'] is not original or p['currentButtonConnected'] is not True:
            failures.append('node-ownership')
        if p['fontScaleVerified'] is not True:
            failures.append('font-scale')
    for e in record['buttonTrace']:
        if e['phase'] not in ('settled','completed'):
            continue
        field, value = e['field'], e['value']
        if not is_pipelined or e['phase'] == 'settled':
            failures.append('continuous-button-violation')
        elif field == 'text' and value not in ('Tersalin!', 'Salin Rute'):
            failures.append('continuous-button-violation')
        elif field == 'aria-label' and value not in ('Silsilah rute berhasil disalin ke clipboard','Salin seluruh jejak silsilah rute ke clipboard'):
            failures.append('continuous-button-violation')

    # Continuous mutation trace verification
    # Identify phase sequences
    for m in mutations:
        phase = m.get('phase')
        target_id = m.get('targetId')
        new_text = m.get('newText', '')
        if phase in ('checkout', 'settled', 'completed'):
            if target_id == 'status':
                if not is_pipelined and new_text in STALE_MESSAGES:
                    failures.append('continuous-mutation-violation')
                if not is_pipelined and INITIAL_REVISION_ID in new_text and scenario not in ('settledDisposeReset', 'pendingDispose'):
                    failures.append('continuous-mutation-violation')
            elif target_id == 'dag-status-reserve-idle':
                if INITIAL_REVISION_ID in new_text and scenario not in ('settledDisposeReset', 'pendingDispose'):
                    failures.append('continuous-mutation-violation')

    # Continuous event trace verification
    # After checkout phase begins, focus must not touch old copy button in settled or completed phases
    for e in events:
        phase = e.get('phase')
        ev_type = e.get('type')
        if phase in ('settled', 'completed') and ev_type in ('focusin', 'focusout'):
            t = e.get('target') or {}
            rt = e.get('relatedTarget') or {}
            if (t.get('isInitialCopyBtn') is True or t.get('dataBreadcrumbNode') == INITIAL_REVISION_ID) and not is_disposed:
                failures.append('no-focus-theft')
            if (rt.get('isInitialCopyBtn') is True or rt.get('dataBreadcrumbNode') == INITIAL_REVISION_ID) and not is_disposed:
                failures.append('no-focus-theft')
        elif phase == 'checkout' and ev_type == 'focusin':
            t = e.get('target') or {}
            if (t.get('isInitialCopyBtn') is True or t.get('dataBreadcrumbNode') == INITIAL_REVISION_ID) and not is_disposed:
                failures.append('no-focus-theft')

    # Snapshot audit across required phases
    for name in REQUIRED_PHASES:
        p = phases[name]
        expected_cursor = INITIAL_REVISION_ID if name in ('initial', 'pending') else (
            INITIAL_REVISION_ID if is_disposed and scenario != 'settledCheckoutReset' else TARGET_REVISION_ID
        )
        expected_idle = INITIAL_IDLE_TEXT if expected_cursor == INITIAL_REVISION_ID else TARGET_IDLE_TEXT

        if p.get('cursor') != expected_cursor:
            failures.append('cursor-ownership-mismatch')

        # Status text audit
        st = p.get('statusText')
        if name == 'initial':
            if st != INITIAL_IDLE_TEXT:
                failures.append('ownership-status-text')
        elif name == 'pending':
            if st != 'Menyalin silsilah rute ke clipboard…':
                failures.append('ownership-status-text')
        elif name in ('checkout', 'completed'):
            if st != expected_idle:
                failures.append('ownership-status-text')
        elif name == 'settled':
            if is_pipelined:
                if st != 'Menyalin silsilah rute ke clipboard…':
                    failures.append('ownership-status-text')
            else:
                if st != expected_idle:
                    failures.append('ownership-status-text')

        # Reservation shadow text audit
        res_text = p.get('reservationText')
        if res_text != expected_idle:
            failures.append('ownership-shadow-text')

        # Button state & text
        btn_text = p.get('buttonText')
        if name == 'settled':
            if is_pipelined:
                if btn_text != 'Menyalin…':
                    failures.append('pipelined-request-corrupted')
            else:
                if btn_text != 'Salin Rute':
                    failures.append('disowned-button-state')
            if p.get('copied') is not False:
                failures.append('disowned-button-state')

        if name == 'completed':
            if btn_text != 'Salin Rute':
                failures.append('disowned-button-state')
            if p.get('copied') is not False:
                failures.append('disowned-button-state')

        # Active focus
        active_el = p.get('activeElement') or {}
        if name in ('checkout', 'settled', 'completed'):
            if (active_el.get('isInitialCopyBtn') is True or active_el.get('dataBreadcrumbNode') == INITIAL_REVISION_ID) and not is_disposed:
                failures.append('stale-focus-theft')

    # Timer verification
    if is_settled_race:
        if not timers:
            failures.append('stale-timer-fired')
        else:
            t = timers[0]
            if t.get('firedAt') is not None or t.get('calls', 0) > 0 or not t.get('cancelled', False):
                failures.append('stale-timer-fired')

    if is_pipelined:
        if not timers:
            failures.append('native-timer-deadline')
        else:
            t = timers[0]
            reg = t.get('registeredAt', 0)
            fired = t.get('firedAt', 0) or 0
            if t.get('delay') != 1500 or (fired - reg) < 1499:
                failures.append('native-timer-deadline')

    return {
        'scenario': scenario,
        'viewport': vp,
        'scale': scale,
        'passed': len(failures) == 0,
        'failures': sorted(set(failures))
    }


def audit_ownership_evidence(data):
    """Audit the complete evidence payload for UIUX-074."""
    if data.get('target') != 'UIUX-074' or data.get('pass') is not True or data.get('errors') != []:
        raise ValueError('Browser test failed or invalid target')

    records = data.get('records', [])
    audits = [audit_ownership_record(r) for r in records]

    expected_coords = set(itertools.product(SCENARIOS, WIDTHS, SCALES))
    actual_coords = set((r['scenario'], r['viewport'], r['scale']) for r in records)

    if len(records) != len(actual_coords) or actual_coords != expected_coords:
        raise ValueError(f'Incomplete matrix coordinates. Expected 36, got {len(actual_coords)}')

    # Audit negative controls
    negatives = data.get('negativeControls', {})
    if set(negatives) != set(NEGATIVES_074):
        raise ValueError(f'Incomplete negative controls. Expected {set(NEGATIVES_074)}, got {set(negatives)}')

    controls = {}
    for name, reason in NEGATIVES_074.items():
        r = negatives[name]['record']
        a = audit_ownership_record(r)
        controls[name] = reason in a['failures']

    failed_records = [a for a in audits if not a['passed']]

    return {
        'passed': len(failed_records) == 0 and all(controls.values()),
        'matrix_records': len(records),
        'phase_measurements': sum(len(r.get('phases', {})) for r in records),
        'failed_records': failed_records,
        'negative_controls': controls
    }


if __name__ == '__main__':
    try:
        result = audit_ownership_evidence(json.loads(Path(sys.argv[1]).read_text()))
        print(json.dumps(result, indent=2))
        sys.exit(0 if result['passed'] else 1)
    except (ValueError, TypeError, KeyError, IndexError, OSError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(2)
