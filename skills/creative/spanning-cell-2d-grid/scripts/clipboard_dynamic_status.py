"""UIUX-073: Validator for dynamic status reservation layout stability, overflow wrapping & geometry."""
import itertools
import json
import sys
from pathlib import Path

from clipboard_focus_events import (
    WIDTHS, SCALES, OUTCOMES, DEPARTURES, SCROLL_KEYS,
    integer
)
from clipboard_focus_reflow import audit_record, number, intersects, rect, contains
from clipboard_scroll_anchor import REQUIRED_PHASES, audit_scroll_anchor_trace
def audit_target_geometry(target, dep):
    """Validate focus outline, visibility, and geometry for active focused neighbor/button."""
    if type(target) is not dict:
        return ['target-geometry-missing']
    failures = []
    if not check_node_identity(target, dep):
        failures.append('active-target-identity')
    if target.get('focused') is not True:
        failures.append('target-unfocused')
    if target.get('focusVisible') is not True:
        failures.append('target-not-focus-visible')
    if target.get('outlineStyle') != 'solid':
        failures.append('target-outline-style')
    try:
        width = number(target.get('outlineWidth', 0))
        if width < 1.9:
            failures.append('target-outline-width')
    except ValueError:
        failures.append('target-outline-width')
    r = target.get('rect')
    if type(r) is not dict or any(k not in r for k in ('left', 'top', 'right', 'bottom', 'width', 'height')):
        failures.append('target-rect-invalid')
    else:
        for k in ('left', 'top', 'right', 'bottom', 'width', 'height'):
            try:
                number(r[k])
            except ValueError:
                failures.append('target-rect-invalid')
                break
        if r.get('width', 0) <= 0 or r.get('height', 0) <= 0:
            failures.append('target-rect-empty')
    bounds = rect(target['rect'])
    if abs(bounds['right']-bounds['left']-number(target['rect']['width'])) > .01 or abs(bounds['bottom']-bounds['top']-number(target['rect']['height'])) > .01:
        raise ValueError('Target rectangle dimensions mismatch')
    expand = number(target['outlineWidth']) + number(target['outlineOffset'])
    if expand < 0:
        raise ValueError('Negative outline expansion')
    outline = {k:v + (expand if k in ('right','bottom') else -expand) for k,v in bounds.items()}
    if target.get('connected') is not True:
        failures.append('target-disconnected')
    if type(target['clips']) is not list or type(target['overlays']) is not list:
        raise ValueError('Target clips/overlays must be lists')
    clipped = not contains(rect(target['viewport']), outline)
    for c in target['clips']:
        if type(c['x']) is not bool or type(c['y']) is not bool:
            raise ValueError('Clip axes must be boolean')
        clipped |= not contains(rect(c), outline, c['x'], c['y'])
    if clipped:
        failures.append('target-clipping')
    if target.get('hit') is not True or any(intersects(outline,rect(o)) for o in target['overlays']):
        failures.append('target-occlusion')
    return failures

LONG_REVISION_ID = 'feat/virtualized-2d-grid-with-asymmetric-spans-and-history-c98f820b784913c98b671a5392812d4a7536901234567890abcdef'


def check_node_identity(node, departure):
    if type(node) is not dict:
        return False
    if departure == 'stay':
        return node.get('tag') == 'button' and node.get('isCopyBtn') is True
    if departure == 'forward':
        return (node.get('tag'), node.get('role'), node.get('dataNode')) == ('g', 'button', 'alpha')
    return node.get('tag') == 'button' and node.get('dataBreadcrumbNode') == LONG_REVISION_ID

NEGATIVES_073 = {
    'oldUnreservedDynamicReset': 'status-height',
    'unbrokenTextBlowout': 'status-overflow',
    'transientBlurRefocus': 'no-transient-glitch',
    'completionFocusTheft': 'active-target',
    'completionStealReturn': 'no-focus-theft',
    'resetFocusTheft': 'no-focus-theft',
    'transientResetScroll': 'reset-scroll',
    'wrongDepartureIdentity': 'active-target',
    'targetClipped': 'target-clipping',
    'targetCovered': 'target-occlusion',
}


def audit_dynamic_status_record(record):
    """Audit single sequence record across 8 phases under dynamic status reservation."""
    key = (record['viewport'], record['scale'], record['outcome'], record['departure'])
    if (type(key[0]) is not int or key[0] not in WIDTHS or type(key[1]) is not int
            or key[1] not in SCALES or key[2] not in OUTCOMES or key[3] not in DEPARTURES):
        raise ValueError('Invalid matrix coordinate')
    phases = record.get('phases')
    if type(phases) is not dict or set(phases) != set(REQUIRED_PHASES):
        raise ValueError('Incomplete phases')
    events = audit_scroll_anchor_trace(record)
    failures = []
    for name in REQUIRED_PHASES:
        p = phases[name]
        m = p['measurement']
        state = 'idle' if name in ('initial', 'reset') else key[2] if name == 'settled' else 'pending'
        dep = key[3] if name in ('departed', 'settled', 'reset') else 'stay'
        if (p['phase'] != name or p['sameNode'] is not True or p['isConnected'] is not True
                or p['anchorPolicy'] != record['anchorPolicy']):
            raise ValueError('Phase identity/policy mismatch')
        if not check_node_identity(p['activeElement'], dep):
            failures.append('active-target')
        if p['activeElementMatchesBtn'] is not (dep == 'stay') or m['focused'] is not (dep == 'stay'):
            failures.append('active-target')
        if (m['viewport'], m['container'], m['scale'], m['state']) != (key[0], 'normal', key[1], state):
            raise ValueError('Phase/matrix state mismatch')
        for f in ('trustedClicks', 'writeCalls'):
            if integer(p[f]) != int(name != 'initial') or p[f] != m[f]:
                raise ValueError('Activation counter mismatch')
        if (number(p['windowWidth']) != key[0] or number(p['windowHeight']) != 900
                or m['viewportSize'] != {'width': p['windowWidth'], 'height': p['windowHeight']}):
            raise ValueError('Window dimension mismatch')
        if set(p['scroll']) != SCROLL_KEYS or any(number(v) < 0 for v in p['scroll'].values()):
            raise ValueError('Invalid scroll map')
        if (number(p['outerScrollTop']) != p['scroll']['dag-scroll-outerY']
                or number(p['innerScrollLeft']) != p['scroll']['dag-scroll-innerX'] or number(p['containerWidth']) <= 0):
            raise ValueError('Scroll/size metadata mismatch')

        # Check horizontal overflow wrapping on status element
        scroll_w = number(p['statusScrollWidth'])
        client_w = number(p['statusClientWidth'])
        container_w = number(p['containerWidth'])
        if min(scroll_w, client_w, container_w) <= 0:
            raise ValueError('Positive status dimensions required')
        if p['statusTextFits'] is not True or p['breadcrumbTextFits'] is not True:
            failures.append('text-fit')
        expected_status = f'Versi {LONG_REVISION_ID}. 0 cabang lanjutan.'
        if p['reservationText'] != expected_status:
            failures.append('reservation-text')
        if state == 'idle' and p['statusText'] != expected_status:
            failures.append('dynamic-status-identity')
        if p['statusText'] != m['statusText']:
            failures.append('status-snapshot-mismatch')
        if scroll_w > container_w + 1.0 or client_w > container_w + 1.0 or scroll_w > client_w + 1.0:
            failures.append('status-overflow')

        # Copy button geometry audit
        a = audit_record(m)
        allowed = set() if dep == 'stay' else {'focus'}
        if name == 'reset':
            allowed |= {'activation'}
        if dep == 'backward':
            allowed |= {'clipping', 'occlusion'}
            if any(intersects(a['outline_bounds'], o) for o in m['opaqueOverlays']):
                failures.append('known-overlay')
        if set(a['failures']) - allowed:
            failures.append('geometry-' + name)

        # Active target geometry audit for departed, settled, reset
        if name in ('departed', 'settled', 'reset'):
            target_failures = audit_target_geometry(p.get('activeTarget'), dep)
            failures.extend(target_failures)

    initial, pending, scrolled, shrunk, regrown, departed, settled, reset = (phases[p] for p in REQUIRED_PHASES)

    # Status / button text continuity
    if reset.get('buttonText') != 'Salin Rute':
        failures.append('button-reset-text')
    if reset.get('copied') is not False:
        failures.append('button-reset-copied')

    # Timer execution evidence
    if record.get('resetTimerExecuted') is not True:
        failures.append('reset-timer-unexecuted')

    timers = record['timers']
    if type(timers) is not list or len(timers) != 1:
        raise ValueError('Expected one native feedback timer')
    timer = timers[0]
    if (number(timer['delay']) != 1500 or integer(timer['calls']) != 1
            or number(timer['firedAt'])-number(timer['registeredAt']) < 1499
            or not departed['checkpointTime'] <= timer['registeredAt'] <= settled['checkpointTime'] < timer['firedAt'] <= reset['checkpointTime']):
        failures.append('native-timer-deadline')
    if reset['statusText'] != initial['statusText']:
        failures.append('status-reset-text')
    heights = [number(phases[n]['statusHeight']) for n in ('initial','pending','regrown','departed','settled','reset')]
    if min(heights) <= 0 or max(heights)-min(heights) > .01:
        failures.append('status-height')

    # Target position invariance
    if key[3] != 'stay':
        for n in ('settled','reset'):
            if any(abs(number(phases[n]['activeTarget']['rect'][k])-number(departed['activeTarget']['rect'][k])) > .1 for k in ('left','top','right','bottom')):
                failures.append('target-position')

    checks = {
        'nested-scroll': all(abs(scrolled[f] - pending[f]) >= 1 for f in ('outerScrollTop', 'innerScrollLeft')),
        'container-resize': shrunk['containerWidth'] < initial['containerWidth'] == regrown['containerWidth'],
        'resize-scroll': all(phases[p]['scroll'] == scrolled['scroll'] for p in ('shrunk', 'regrown')),
        'stay-scroll': key[3] != 'stay' or departed['scroll'] == regrown['scroll'],
        'settlement-scroll': settled['scroll'] == departed['scroll'] and not any(e['type'] == 'scroll' for e in events['settled']),
        'reset-scroll': reset['scroll'] == settled['scroll'] and not any(e['type'] == 'scroll' for e in events['reset']),
        'no-transient-glitch': not any(e['type'] in ('focusin', 'focusout') for p in REQUIRED_PHASES[:5] for e in events[p]),
        'no-focus-theft': not any(e['type'] in ('focusin', 'focusout') for p in ('settled', 'reset') for e in events[p]),
    }
    for name in REQUIRED_PHASES:
        keys = [e for e in events[name] if e['type'] == 'keydown']
        expected = [('Enter', False)] if name == 'pending' else [('Tab', key[3] == 'backward')] if name == 'departed' and key[3] != 'stay' else []
        checks['input-' + name] = [(e['key'], e['shiftKey']) for e in keys] == expected

    focus = [e for e in events['departed'] if e['type'] in ('focusin', 'focusout')]
    checks['departure-events'] = not focus if key[3] == 'stay' else (
        len(focus) == 2 and focus[0]['type'] == 'focusout' and focus[1]['type'] == 'focusin'
        and check_node_identity(focus[0]['target'], 'stay') and check_node_identity(focus[0]['relatedTarget'], key[3])
        and check_node_identity(focus[1]['target'], key[3]) and check_node_identity(focus[1]['relatedTarget'], 'stay')
        and any(e['type'] and e['seq'] < focus[0]['seq'] for e in events['departed'] if e['type'] == 'keydown'))

    failures.extend(k for k, v in checks.items() if not v)
    return dict(key=list(key), passed=not failures, failures=sorted(set(failures)))


def audit_dynamic_status_evidence(data):
    """Audit the complete evidence payload for UIUX-073."""
    if data.get('target') != 'UIUX-073' or data.get('pass') is not True or data.get('errors') != []:
        raise ValueError('Browser failed or invalid target')
    records = data.get('records', [])
    audits = [audit_dynamic_status_record(r) for r in records]
    keys = [tuple(a['key']) for a in audits]
    if len(keys) != len(set(keys)) or set(keys) != set(itertools.product(WIDTHS, SCALES, OUTCOMES, DEPARTURES)):
        raise ValueError('Incomplete/duplicate matrix')
    if any(r.get('anchorPolicy') != 'auto' for r in records):
        raise ValueError('Positive matrix requires default scroll anchoring (overflow-anchor: auto)')
    if any(r.get('layout') != 'dynamic-reserved' for r in records):
        raise ValueError('Positive matrix requires dynamic-reserved layout')

    # Negative controls
    negatives = data.get('negativeControls', {})
    if set(negatives) != set(NEGATIVES_073):
        raise ValueError('Incomplete controls')
    controls = {}
    for name, reason in NEGATIVES_073.items():
        r = negatives[name]['record']
        a = audit_dynamic_status_record(r)
        controls[name] = reason in a['failures']
        if name in ('transientBlurRefocus', 'completionStealReturn', 'resetFocusTheft'):
            controls[name] &= 'active-target' not in a['failures'] and not any(f.startswith('geometry') for f in a['failures'])
        if name == 'oldUnreservedDynamicReset':
            controls[name] &= r.get('anchorPolicy') == 'auto' and 'status-height' in a['failures']
        if name == 'unbrokenTextBlowout':
            controls[name] &= 'status-overflow' in a['failures']
        if name == 'transientResetScroll':
            controls[name] &= r['phases']['settled']['scroll'] == r['phases']['reset']['scroll']

    # Comparisons
    comparisons = data.get('comparisons', {})
    if set(comparisons) != {'optOut'}:
        raise ValueError('Missing exact opt-out comparison')
    opt = comparisons['optOut']['record']
    opt_audit = audit_dynamic_status_record(opt)
    coord = [390, 2, 'failure', 'forward']
    controls['optOutComparison'] = (opt_audit['key'] == coord and opt.get('anchorPolicy') == 'none'
        and opt.get('layout') == 'unreserved' and 'status-height' in opt_audit['failures']
        and 'target-position' in opt_audit['failures']
        and not {'settlement-scroll','reset-scroll','no-focus-theft'} & set(opt_audit['failures']))

    failed = [a for a in audits if not a['passed']]
    return dict(
        passed=not failed and all(controls.values()),
        matrix_records=len(records),
        phase_measurements=sum(len(r['phases']) for r in records),
        failed_records=failed,
        negative_controls=controls
    )


if __name__ == '__main__':
    try:
        result = audit_dynamic_status_evidence(json.loads(Path(sys.argv[1]).read_text()))
        print(json.dumps(result, indent=2))
        sys.exit(0 if result['passed'] else 1)
    except (ValueError, TypeError, KeyError, IndexError, OSError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(2)
