"""Bounded nested-scroll evidence gate; shared geometry, no general paint proof."""
import itertools
import json
import sys
from pathlib import Path
from clipboard_focus_reflow import audit_record, number, STATUS

WIDTHS = (320, 390, 768)
SCALES = (1, 2)
OUTCOMES = ('success', 'failure')
REQUIRED_PHASES = ('initial', 'pending', 'scrolled', 'shrunk', 'regrown', 'settled', 'roundtrip')
NEGATIVES = dict(stickyOcclusionAuto='occlusion', stickyOcclusionPointerEventsNone='occlusion',
                 clipping='clipping', outlineOnly='occlusion', unfocused='focus', textOverflow='text-fit')


def audit_phase(name, phase, record):
    if type(phase) is not dict or phase.get('phase') != name:
        raise ValueError('Missing or mismatched phase')
    for field in ('sameNode', 'isConnected', 'activeElementMatchesBtn'):
        if phase.get(field) is not True:
            raise ValueError('Focus/identity failed: ' + field)
    for field in ('trustedClicks', 'writeCalls', 'outerScrollTop', 'innerScrollLeft',
                  'containerWidth', 'windowWidth', 'windowHeight'):
        value = number(phase.get(field))
        if value < 0 or (field.endswith(('Width', 'Height')) and value == 0):
            raise ValueError('Invalid measured extent: ' + field)
    measurement = phase['measurement']
    expected_state = ('idle' if name == 'initial' else record['outcome']
                      if name in ('settled', 'roundtrip') else 'pending')
    if (measurement['viewport'], measurement['container'], measurement['scale'], measurement['state']) != (
            record['viewport'], 'normal', record['scale'], expected_state):
        raise ValueError('Phase/matrix binding mismatch')
    for field in ('trustedClicks', 'writeCalls'):
        if phase[field] != measurement[field] or phase[field] != int(name != 'initial'):
            raise ValueError('Activation counter mismatch')
    initial = record['phases']['initial']
    if (phase['windowWidth'] != record['viewport'] or phase['windowHeight'] != initial['windowHeight']
            or measurement['viewportSize'] != {'width': phase['windowWidth'], 'height': phase['windowHeight']}):
        raise ValueError('Window changed or geometry metadata mismatch')
    return audit_record(measurement)


def audit_nested_record(record):
    key = (record['viewport'], record['scale'], record['outcome'])
    if (type(key[0]) is not int or key[0] not in WIDTHS or type(key[1]) is not int
            or key[1] not in SCALES or key[2] not in OUTCOMES):
        raise ValueError('Invalid matrix coordinate')
    phases = record['phases']
    if type(phases) is not dict or set(phases) != set(REQUIRED_PHASES):
        raise ValueError('Incomplete phases')
    audits = {p: audit_phase(p, phases[p], record) for p in REQUIRED_PHASES}
    initial, pending, scrolled, shrunk, regrown, settled, roundtrip = (phases[p] for p in REQUIRED_PHASES)
    checks = {
        'nested-scroll-offsets': all(abs(scrolled[f] - pending[f]) >= 1
                                    for f in ('outerScrollTop', 'innerScrollLeft')),
        'container-shrink-focus': shrunk['containerWidth'] < initial['containerWidth'],
        'container-regrow-focus': regrown['containerWidth'] == initial['containerWidth'] > shrunk['containerWidth'],
        'pending-scroll-preserved': all(phases[p][f] == scrolled[f]
            for p in ('shrunk', 'regrown') for f in ('outerScrollTop', 'innerScrollLeft')),
        'app-settlement': settled['measurement']['statusText'] == STATUS[key[2]]
                          and settled['measurement']['label'] == ('Tersalin!' if key[2] == 'success' else 'Gagal menyalin'),
        'keyboard-roundtrip': roundtrip.get('neighborMoved') is True
            and roundtrip.get('returnedToCopy') is True and roundtrip.get('neighborTag') == 'g'
            and roundtrip.get('neighborNode') == 'alpha' and roundtrip.get('neighborRole') == 'button',
    }
    checks.update({f'phase-{p}-geometry': a['passed'] for p, a in audits.items()})
    return dict(key=list(key), passed=all(checks.values()), failures=[k for k, v in checks.items() if not v])


def audit_nested_matrix(records):
    if type(records) is not list:
        raise ValueError('Expected records')
    audits = [audit_nested_record(r) for r in records]
    keys = [tuple(a['key']) for a in audits]
    expected = set(itertools.product(WIDTHS, SCALES, OUTCOMES))
    if len(keys) != len(expected) or set(keys) != expected:
        raise ValueError('Incomplete or duplicate matrix')
    return dict(passed=all(a['passed'] for a in audits), record_count=len(audits), audits=audits)


def audit_sticky(proof):
    """Require a crossed horizontal threshold and viewport-stable stuck rect."""
    if proof['overlayPosition'] != 'sticky' or proof['pointerEvents'] not in ('auto', 'none'):
        raise ValueError('Not a supported sticky control')
    values = {k: number(proof[k]) for k in ('scrollBefore', 'scrollAfter', 'inset',
                                          'clipLeft', 'leftBefore', 'leftAfter', 'normalLeft')}
    target = values['clipLeft'] + values['inset']
    if (not 0 <= values['scrollBefore'] < values['scrollAfter'] or values['inset'] < 0
            or values['normalLeft'] >= target - 1
            or any(abs(values[k] - target) > .5 for k in ('leftBefore', 'leftAfter'))):
        raise ValueError('Sticky threshold/scroll/stuck geometry not demonstrated')
    return True


def audit_nested_evidence(data):
    if data.get('target') != 'UIUX-070' or data.get('pass') is not True or data.get('errors') != []:
        raise ValueError('Browser failed or wrong target')
    result = audit_nested_matrix(data['records'])
    negatives = data['negativeControls']
    if set(negatives) != set(NEGATIVES):
        raise ValueError('Incomplete negative controls')
    detected = {name: reason in audit_record(negatives[name]['record'])['failures']
                for name, reason in NEGATIVES.items()}
    for name in ('stickyOcclusionAuto', 'stickyOcclusionPointerEventsNone'):
        entry = negatives[name]
        audit_sticky(entry)
        wanted = 'none' if name.endswith('None') else 'auto'
        if entry['pointerEvents'] != wanted:
            raise ValueError('Wrong pointer control')
        # All other geometry gates must stay good; don't let unrelated clipping fake occlusion.
        if audit_record(entry['record'])['failures'] != ['occlusion']:
            raise ValueError('Sticky control has unrelated failures')
    for name in ('stickyOcclusionPointerEventsNone', 'outlineOnly'):
        detected[name] &= negatives[name]['record']['hitTestPassed'] is True
    detected['stickyOcclusionAuto'] &= negatives['stickyOcclusionAuto']['record']['hitTestPassed'] is False
    return dict(passed=result['passed'] and all(detected.values()), matrix_records=result['record_count'],
                failed_records=[a for a in result['audits'] if not a['passed']], negative_controls=detected)


if __name__ == '__main__':
    try:
        result = audit_nested_evidence(json.loads(Path(sys.argv[1]).read_text()))
        print(json.dumps(result, indent=2))
        sys.exit(0 if result['passed'] else 1)
    except (ValueError, KeyError, TypeError, IndexError, OSError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(2)
