"""Bounded clipboard-state evidence gate; not a full WCAG or pixel audit.

Opaque text/backgrounds only. Composite translucent system outlines over the
recorded opaque adjacent bar in sRGB. Reject gradients, ancestor opacity and
incomplete matrices; evaluate thresholds before rounding any displayed result.
"""
import itertools
import json
import re
import sys
from pathlib import Path
from accessibility_measure import contrast_ratio, parse_color, parse_px

STATES = {'idle': 'Salin Rute', 'pending': 'Menyalin…',
          'success': 'Tersalin!', 'failure': 'Gagal menyalin'}
STATUS = {'pending': 'Menyalin silsilah rute ke clipboard…',
          'success': 'Silsilah rute berhasil disalin ke clipboard',
          'failure': 'Gagal menyalin silsilah rute ke clipboard'}
MODES = ('normal', 'forced-light', 'forced-dark')
WIDTHS = (390, 768, 1280)


def composite_outline(color, backdrop):
    """Source-over one CSS rgba outline on a known opaque sRGB bar."""
    bg = parse_color(backdrop)
    if isinstance(color, str) and color.startswith('rgba('):
        m = re.fullmatch(r'rgba\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*\)', color)
        if not m:
            raise ValueError('Unsupported rgba syntax')
        fg = parse_color(tuple(float(m[i]) for i in (1, 2, 3)))
        alpha = float(m[4])
        if not 0 <= alpha <= 1:
            raise ValueError('Alpha must be finite in [0,1]')
        return tuple(alpha * f + (1 - alpha) * b for f, b in zip(fg, bg))
    return parse_color(color)


def audit_record(r):
    key = (r['viewport'], r['mode'], r['state'], r['hovered'])
    if (type(key[0]) is not int or key[0] not in WIDTHS or key[1] not in MODES
            or key[2] not in STATES or type(key[3]) is not bool):
        raise ValueError('Invalid matrix coordinate')
    text = contrast_ratio(r['buttonColor'], r['buttonBg'])
    outline = contrast_ratio(composite_outline(r['outlineColor'], r['adjacentBg']), r['adjacentBg'])
    # ponytail: fixed fixture contract, not an arbitrary DOM compositing engine.
    visible = (r['focused'] is True and r['focusVisible'] is True
               and r['outlineStyle'] == 'solid' and parse_px(r['outlineWidth']) >= 2
               and parse_px(r['outlineOffset']) >= 2 and parse_px(r['opacity']) == 1
               and r['ancestorOpaque'] is True and r['animationsRunning'] == 0
               and r['buttonBackgroundImage'] == r['adjacentBackgroundImage'] == 'none')
    media = (r['hoveredMatch'] is key[3]
             and r['forcedColors'] is (key[1] != 'normal')
             and r['colorScheme'] == ('dark' if key[1] == 'forced-dark' else 'light')
             and r['forcedColorAdjust'] == 'auto')
    status = r['statusText']
    status_ok = (isinstance(status, str) and status.startswith('Versi ')
                 if key[2] == 'idle' else status == STATUS[key[2]])
    semantic = (r['label'] == STATES[key[2]] and type(r['ariaBusy']) is bool and status_ok)
    return {'key': list(key), 'text_ratio': text, 'outline_ratio': outline,
            'passed': bool(text >= 4.5 and outline >= 3 and visible and media and semantic)}


def audit_matrix(records):
    if not isinstance(records, list):
        raise ValueError('Records must be a list')
    audits = [audit_record(r) for r in records]
    keys = [tuple(a['key']) for a in audits]
    expected = set(itertools.product(WIDTHS, MODES, STATES, (False, True)))
    if len(keys) != len(expected) or set(keys) != expected:
        raise ValueError('Expected exactly one record per matrix combination')
    return {'records': len(audits), 'passed': all(a['passed'] for a in audits),
            'text_min': min(a['text_ratio'] for a in audits),
            'outline_min': min(a['outline_ratio'] for a in audits), 'audits': audits}


if __name__ == '__main__':
    try:
        data = json.loads(Path(sys.argv[1]).read_text())
        if data.get('pass') is not True or data.get('errors') != []:
            raise ValueError('Browser run failed or missing errors metadata')
        result = audit_matrix(data['records'])
        print(json.dumps(result, indent=2))
        sys.exit(0 if result['passed'] else 1)
    except (ValueError, TypeError, KeyError, IndexError, OSError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(2)
