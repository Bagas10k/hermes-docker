"""Bounded fixture geometry audit, not a general CSS paint/WCAG validator.

Outline AABB containment is conservative for rounded buttons. Occlusion checks
known foreground opaque rectangles plus sampled button hit-tests, not arbitrary
stacking contexts, pseudo-elements, filters or pixel coverage. No dependencies.
"""
import itertools
import json
import math
import sys
from pathlib import Path

WIDTHS = (320, 390, 768)
CONTAINERS = ('normal', 'narrow')
SCALES = (1, 2)
LABELS = dict(idle='Salin Rute', pending='Menyalin…', success='Tersalin!', failure='Gagal menyalin')
STATUS = dict(pending='Menyalin silsilah rute ke clipboard…',
              success='Silsilah rute berhasil disalin ke clipboard',
              failure='Gagal menyalin silsilah rute ke clipboard')
NEGATIVES = dict(clipping='clipping', occlusionStandard='occlusion',
                 occlusionPointerEventsNone='occlusion', outlineOnly='occlusion',
                 unfocused='focus', textOverflow='text-fit')


def number(value):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError('Expected finite numeric measurement, not bool/string')
    return value


def rect(value):
    v = {k: number(value[k]) for k in ('left', 'top', 'right', 'bottom')}
    if v['left'] >= v['right'] or v['top'] >= v['bottom']:
        raise ValueError('Expected positive rectangle')
    return v


def contains(outer, inner, x=True, y=True):
    return ((not x or outer['left'] <= inner['left'] <= inner['right'] <= outer['right'])
            and (not y or outer['top'] <= inner['top'] <= inner['bottom'] <= outer['bottom']))


def intersects(a, b):
    return (max(a['left'], b['left']) < min(a['right'], b['right'])
            and max(a['top'], b['top']) < min(a['bottom'], b['bottom']))


def audit_record(r):
    key = (r['viewport'], r['container'], r['scale'], r['state'])
    if (type(key[0]) is not int or key[0] not in WIDTHS or key[1] not in CONTAINERS
            or type(key[2]) is not int or key[2] not in SCALES or key[3] not in LABELS):
        raise ValueError('Invalid matrix coordinate')
    for field in ('clips', 'opaqueOverlays', 'fontSamples', 'unsupported'):
        if type(r[field]) is not list:
            raise ValueError('Expected measurement list: ' + field)
    button = rect(r['buttonRect']); bar = rect(r['barRect'])
    width = number(r['outlineWidth']); offset = number(r['outlineOffset'])
    if width < 0 or offset < 0:
        raise ValueError('Unsupported negative outline dimensions')
    expansion = width + offset
    outline = {k: v + (expansion if k in ('right', 'bottom') else -expansion) for k, v in button.items()}
    vp = rect(dict(left=0, top=0, right=r['viewportSize']['width'], bottom=r['viewportSize']['height']))
    if vp['right'] != r['viewport']:
        raise ValueError('Viewport metadata mismatch')
    clips = []
    for c in r['clips']:
        if type(c['x']) is not bool or type(c['y']) is not bool:
            raise ValueError('Clip axes must be boolean')
        clips.append((rect(c), c['x'], c['y']))
    overlays = [rect(o) for o in r['opaqueOverlays']]
    dims = [number(r[k]) for k in ('btnScrollWidth', 'btnClientWidth', 'btnScrollHeight',
                                   'btnClientHeight', 'barScrollWidth', 'barClientWidth')]
    if min(dims) <= 0:
        raise ValueError('Expected positive measured extents')
    fonts = [(number(s['before']), number(s['after'])) for s in r['fontSamples']]
    if not fonts or any(min(pair) <= 0 for pair in fonts):
        raise ValueError('Expected positive observed font sizes')
    state = key[3]
    checks = {
        'focus': r['focused'] is True and r['focusVisible'] is True and r['outlineStyle']=='solid'
                 and width >= 2 and offset >= 2 and 0 < number(r['tabCount']) <= 30,
        'clipping': contains(vp, outline) and all(contains(c, outline, x, y) for c, x, y in clips),
        'bar-clearance': contains(bar, outline),
        'occlusion': r['hitTestPassed'] is True and not any(intersects(outline, o) for o in overlays),
        'text-fit': all(dims[i] <= dims[i+1] for i in (0, 2, 4)),
        'document-overflow': 0 < number(r['documentScrollWidth']) <= number(r['documentClientWidth']) == key[0],
        'font-scale': all(abs(after - before * key[2]) <= 0.01 for before, after in fonts),
        'semantics': r['label']==LABELS[state] and r['copied'] is (state=='success')
                     and (r['statusText'].startswith('Versi ') if state=='idle' else r['statusText']==STATUS[state]),
        'activation': number(r['trustedClicks']) == number(r['writeCalls']) == int(state != 'idle'),
        'motion': r['reducedMotion'] is True and 0 <= number(r['transitionSeconds']) <= 0.00002,
        'supported': not r['unsupported'],
    }
    return dict(key=list(key), passed=all(checks.values()), failures=[k for k,v in checks.items() if not v],
                outline_bounds=outline)


def audit_matrix(records):
    if type(records) is not list:
        raise ValueError('Expected record list')
    audits = [audit_record(r) for r in records]
    keys = [tuple(a['key']) for a in audits]
    expected = set(itertools.product(WIDTHS, CONTAINERS, SCALES, LABELS))
    if len(keys) != len(expected) or set(keys) != expected:
        raise ValueError('Incomplete or duplicate matrix')
    return dict(passed=all(a['passed'] for a in audits), record_count=len(audits), audits=audits)


def audit_evidence(data):
    if data['pass'] is not True or data['errors'] != []:
        raise ValueError('Browser failed or errors present')
    result = audit_matrix(data['records'])
    negatives = data['negativeControls']
    if set(negatives) != set(NEGATIVES):
        raise ValueError('Incomplete negative controls')
    detected = {name: reason in audit_record(negatives[name]['record'])['failures']
                for name, reason in NEGATIVES.items()}
    # These controls must demonstrate hit-test blind spots, not unrelated failures.
    for name in ('occlusionPointerEventsNone', 'outlineOnly'):
        detected[name] &= negatives[name]['record']['hitTestPassed'] is True
    return dict(passed=result['passed'] and all(detected.values()), matrix_records=result['record_count'],
                failed_records=[a for a in result['audits'] if not a['passed']], negative_controls=detected)


if __name__ == '__main__':
    try:
        result = audit_evidence(json.loads(Path(sys.argv[1]).read_text()))
        print(json.dumps(result, indent=2))
        sys.exit(0 if result['passed'] else 1)
    except (ValueError, TypeError, KeyError, IndexError, OSError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(2)
