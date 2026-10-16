"""Bounded recorded-event gate, not proof against forged traces or browser omissions."""
import itertools
import json
import sys
from pathlib import Path
from clipboard_focus_reflow import audit_record, number, intersects

WIDTHS = (320, 390, 768)
SCALES = (1, 2)
OUTCOMES = ('success', 'failure')
DEPARTURES = ('stay', 'forward', 'backward')
REQUIRED_PHASES = ('initial', 'pending', 'scrolled', 'shrunk', 'regrown', 'departed', 'settled')
NEGATIVES = {'transientBlurRefocus': 'no-transient-glitch',
             'completionFocusTheft': 'active-target', 'completionStealReturn': 'no-focus-theft',
             'transientScrollRestore': 'settlement-scroll', 'wrongDepartureIdentity': 'active-target',
             'nativeAnchoring': 'settlement-scroll'}
SCROLL_KEYS = {'windowX', 'windowY', 'dag-scroll-outerX', 'dag-scroll-outerY',
               'dag-scroll-innerX', 'dag-scroll-innerY', 'dag-viewX', 'dag-viewY'}


def check_node_identity(node, departure):
    if type(node) is not dict:
        return False
    if departure == 'stay':
        return node.get('tag') == 'button' and node.get('isCopyBtn') is True
    if departure == 'forward':
        return (node.get('tag'), node.get('role'), node.get('dataNode')) == ('g', 'button', 'alpha')
    return node.get('tag') == 'button' and node.get('dataBreadcrumbNode') == 'anak-雪'


def integer(v):
    if type(v) is not int or v < 0:
        raise ValueError('Expected nonnegative integer counter')
    return v


def audit_event_trace(record):
    """Bind complete contiguous trace slices to measured checkpoint counters/time."""
    trace = record['eventTrace']
    if type(trace) is not list or not trace:
        raise ValueError('Missing event trace')
    phases = record['phases']
    rank = {p: i for i, p in enumerate(('setup', *REQUIRED_PHASES))}
    last_rank, last_time = 0, 0
    for seq, e in enumerate(trace, 1):
        if integer(e['seq']) != seq or e['type'] not in ('focusin', 'focusout', 'scroll', 'keydown'):
            raise ValueError('Noncontiguous sequence or invalid event type')
        if e['phase'] not in rank or rank[e['phase']] < last_rank:
            raise ValueError('Nonmonotonic event phase')
        last_rank = rank[e['phase']]
        t = number(e['observedTime'])
        if t < last_time or number(e['timeStamp']) < 0 or e['trusted'] is not True:
            raise ValueError('Invalid event clock or untrusted event')
        last_time = t
        if type(e['target']) is not dict or (e.get('relatedTarget') is not None and type(e['relatedTarget']) is not dict):
            raise ValueError('Invalid event target')
        if e['type'] == 'keydown' and (e['key'] not in ('Tab', 'Enter') or type(e['shiftKey']) is not bool):
            raise ValueError('Invalid keyboard evidence')
    previous_seq, previous_time = 0, 0
    for name in REQUIRED_PHASES:
        p = phases[name]
        end, t = integer(p['eventSeq']), number(p['checkpointTime'])
        if not previous_seq <= end <= len(trace) or t < previous_time:
            raise ValueError('Invalid checkpoint bounds')
        events = trace[previous_seq:end]
        allowed = ('setup', 'initial') if name == 'initial' else (name,)
        if any(e['phase'] not in allowed or not previous_time <= e['observedTime'] <= t for e in events):
            raise ValueError('Trace/checkpoint binding mismatch')
        if integer(p['scrollEventCount']) != sum(e['type'] == 'scroll' for e in trace[:end]):
            raise ValueError('Scroll counter mismatch')
        previous_seq, previous_time = end, t
    if previous_seq != len(trace):
        raise ValueError('Unaccounted trace suffix')
    setup = [e for e in trace if e['phase'] == 'setup']
    focus = [e for e in setup if e['type'] == 'focusin']
    if not focus or not check_node_identity(focus[-1]['target'], 'stay'):
        raise ValueError('No observed initial copy focus')
    tabs = [e for e in setup if e['type'] == 'keydown' and e['key'] == 'Tab' and not e['shiftKey']]
    if len(tabs) != phases['initial']['measurement']['tabCount'] or not tabs or tabs[-1]['seq'] >= focus[-1]['seq']:
        raise ValueError('Missing initial native Tab provenance')
    return {p: [e for e in trace if e['phase'] == p] for p in REQUIRED_PHASES}


def audit_focus_record(record):
    key = (record['viewport'], record['scale'], record['outcome'], record['departure'])
    if (type(key[0]) is not int or key[0] not in WIDTHS or type(key[1]) is not int
            or key[1] not in SCALES or key[2] not in OUTCOMES or key[3] not in DEPARTURES):
        raise ValueError('Invalid matrix coordinate')
    phases = record['phases']
    if type(phases) is not dict or set(phases) != set(REQUIRED_PHASES):
        raise ValueError('Incomplete phases')
    events = audit_event_trace(record)
    failures = []
    for name in REQUIRED_PHASES:
        p = phases[name]; m = p['measurement']
        state = 'idle' if name == 'initial' else key[2] if name == 'settled' else 'pending'
        dep = key[3] if name in ('departed', 'settled') else 'stay'
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
        a = audit_record(m)
        allowed = set() if dep == 'stay' else {'focus'}
        if dep == 'backward':
            # The copy control may scroll offscreen after native Shift+Tab. This
            # exception applies only to the departed button, never the new focus target.
            allowed |= {'clipping', 'occlusion'}
            if any(intersects(a['outline_bounds'], o) for o in m['opaqueOverlays']):
                failures.append('known-overlay')
        if set(a['failures']) - allowed:
            failures.append('geometry-' + name)
    initial, pending, scrolled, shrunk, regrown, departed, settled = (phases[p] for p in REQUIRED_PHASES)
    checks = {
        'nested-scroll': all(abs(scrolled[f] - pending[f]) >= 1 for f in ('outerScrollTop', 'innerScrollLeft')),
        'container-resize': shrunk['containerWidth'] < initial['containerWidth'] == regrown['containerWidth'],
        'resize-scroll': all(phases[p]['scroll'] == scrolled['scroll'] for p in ('shrunk', 'regrown')),
        'stay-scroll': key[3] != 'stay' or departed['scroll'] == regrown['scroll'],
        'settlement-scroll': settled['scroll'] == departed['scroll'] and not any(e['type'] == 'scroll' for e in events['settled']),
        'no-transient-glitch': not any(e['type'] in ('focusin', 'focusout') for p in REQUIRED_PHASES[:5] for e in events[p]),
        'no-focus-theft': not any(e['type'] in ('focusin', 'focusout') for e in events['settled']),
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
        and any(e['type'] == 'keydown' and e['seq'] < focus[0]['seq'] for e in events['departed']))
    failures.extend(k for k, v in checks.items() if not v)
    return dict(key=list(key), passed=not failures, failures=sorted(set(failures)))


def audit_focus_evidence(data):
    if data['target'] != 'UIUX-071' or data['pass'] is not True or data['errors'] != []:
        raise ValueError('Browser failed or invalid target')
    records = data['records']; audits = [audit_focus_record(r) for r in records]
    keys = [tuple(a['key']) for a in audits]
    if len(keys) != len(set(keys)) or set(keys) != set(itertools.product(WIDTHS, SCALES, OUTCOMES, DEPARTURES)):
        raise ValueError('Incomplete/duplicate matrix')
    if any(r['anchorPolicy'] != 'none' for r in records):
        raise ValueError('Positive matrix requires explicit anchor opt-out')
    negatives = data['negativeControls']
    if set(negatives) != set(NEGATIVES):
        raise ValueError('Incomplete controls')
    controls = {}
    for name, reason in NEGATIVES.items():
        r = negatives[name]['record']; a = audit_focus_record(r)
        controls[name] = reason in a['failures']
        if name in ('transientBlurRefocus', 'completionStealReturn'):
            controls[name] &= 'active-target' not in a['failures'] and not any(f.startswith('geometry') for f in a['failures'])
        if name == 'transientScrollRestore':
            controls[name] &= r['phases']['departed']['scroll'] == r['phases']['settled']['scroll']
        if name == 'nativeAnchoring':
            controls[name] &= r['anchorPolicy'] == 'auto' and a['failures'] == ['settlement-scroll']
    failed = [a for a in audits if not a['passed']]
    return dict(passed=not failed and all(controls.values()), matrix_records=len(records),
                phase_measurements=sum(len(r['phases']) for r in records), failed_records=failed, negative_controls=controls)


if __name__ == '__main__':
    try:
        result = audit_focus_evidence(json.loads(Path(sys.argv[1]).read_text()))
        print(json.dumps(result, indent=2)); sys.exit(0 if result['passed'] else 1)
    except (ValueError, TypeError, KeyError, IndexError, OSError) as error:
        print(str(error), file=sys.stderr); sys.exit(2)
