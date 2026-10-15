"""Exact sRGB relative luminance and contrast ratio calculations following W3C WCAG 2.1 specifications.

Used to audit focus-visible outline and non-text contrast against adjacent surfaces.
"""
import json
import math
import re
import sys
from pathlib import Path


def parse_color(val):
    """Parse color into opaque (r, g, b) tuple in range [0, 255].

    Accepts:
      - tuple or list of 3 numbers
      - hex string: '#fff', '#ffffff'
      - CSS rgb/rgba string: 'rgb(37, 99, 235)', 'rgba(37, 99, 235, 1)'
    Rejects:
      - non-opaque alpha (alpha != 1)
      - out-of-range values (< 0 or > 255)
      - non-finite numbers (NaN, inf)
      - invalid string formats
    """
    if isinstance(val, (tuple, list)):
        if len(val) == 4:
            if isinstance(val[3], bool) or not isinstance(val[3], (int, float)) or not math.isfinite(val[3]) or val[3] != 1.0:
                raise ValueError("Only opaque colors (alpha=1.0) are supported without compositing")
            val = val[:3]
        if len(val) != 3:
            raise ValueError(f"Color tuple must have 3 components, got {len(val)}")
        res = []
        for c in val:
            if not isinstance(c, (int, float)) or isinstance(c, bool):
                raise TypeError(f"Color component must be int or float, got {type(c).__name__}")
            if math.isnan(c) or math.isinf(c):
                raise ValueError("Color component must be finite number")
            if c < 0 or c > 255:
                raise ValueError(f"Color component out of range [0, 255]: {c}")
            res.append(float(c))
        return (res[0], res[1], res[2])

    if not isinstance(val, str):
        raise TypeError(f"Expected str, tuple, or list, got {type(val).__name__}")

    s = val.strip()
    # Hex format
    if s.startswith('#'):
        hex_digits = s[1:]
        if len(hex_digits) == 3:
            if not all(c in '0123456789abcdefABCDEF' for c in hex_digits):
                raise ValueError(f"Invalid hex color: {val}")
            return (float(int(hex_digits[0] * 2, 16)),
                    float(int(hex_digits[1] * 2, 16)),
                    float(int(hex_digits[2] * 2, 16)))
        elif len(hex_digits) == 6:
            if not all(c in '0123456789abcdefABCDEF' for c in hex_digits):
                raise ValueError(f"Invalid hex color: {val}")
            return (float(int(hex_digits[0:2], 16)),
                    float(int(hex_digits[2:4], 16)),
                    float(int(hex_digits[4:6], 16)))
        elif len(hex_digits) == 8:
            alpha = int(hex_digits[6:8], 16)
            if alpha != 255:
                raise ValueError("Only opaque colors (alpha=255) are supported without compositing")
            return (float(int(hex_digits[0:2], 16)),
                    float(int(hex_digits[2:4], 16)),
                    float(int(hex_digits[4:6], 16)))
        else:
            raise ValueError(f"Invalid hex color length: {val}")

    # rgb(...) or rgba(...) format
    m = re.match(r'^rgba?\(\s*([\d\.]+)\s*,\s*([\d\.]+)\s*,\s*([\d\.]+)(?:\s*,\s*([\d\.]+)\s*)?\)$', s)
    if m:
        r, g, b = float(m.group(1)), float(m.group(2)), float(m.group(3))
        if m.group(4) is not None:
            a = float(m.group(4))
            if a != 1.0:
                raise ValueError(f"Only opaque colors (alpha=1.0) supported, got alpha={a}")
        for c, name in ((r, 'R'), (g, 'G'), (b, 'B')):
            if math.isnan(c) or math.isinf(c) or c < 0 or c > 255:
                raise ValueError(f"{name} channel out of range [0, 255]: {c}")
        return (r, g, b)

    raise ValueError(f"Unrecognized color string format: {val}")


def srgb_to_linear(c_255):
    """Convert sRGB channel in 0..255 to linear luminance component."""
    c = c_255 / 255.0
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(color):
    """Compute exact relative luminance in sRGB color space according to W3C WCAG 2.1."""
    r, g, b = parse_color(color)
    r_lin = srgb_to_linear(r)
    g_lin = srgb_to_linear(g)
    b_lin = srgb_to_linear(b)
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def contrast_ratio(color1, color2):
    """Compute contrast ratio between two colors according to W3C WCAG 2.1.

    Returns float in range [1.0, 21.0].
    """
    l1 = relative_luminance(color1)
    l2 = relative_luminance(color2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def parse_px(val):
    """Extract numeric pixel value from string or number."""
    if isinstance(val, bool) or not isinstance(val, (int, float, str)):
        raise ValueError("Pixel dimension must be numeric, not boolean")
    value = float(val.strip().removesuffix('px') if isinstance(val, str) else val)
    if not math.isfinite(value):
        raise ValueError("Pixel dimension must be finite")
    return value


def audit_focus_visible_record(record, min_nontext_ratio=3.0):
    """Bounded indicator audit, not WCAG conformance or focus-area certification.

    Width >=1 is a local visibility gate; 1.4.11 itself sets contrast, not width.
    Button-background contrast is informational when a positive offset separates it.
    """
    if isinstance(min_nontext_ratio, bool) or not isinstance(min_nontext_ratio, (int, float)) or not math.isfinite(min_nontext_ratio) or not 1 <= min_nontext_ratio <= 21:
        raise ValueError("Contrast threshold must be finite in [1,21]")
    outline_color = record.get('outlineColor') or record.get('outline_color')
    adjacent_bg = record.get('adjacentBg') or record.get('adjacent_bg')
    button_bg = record.get('buttonBg') or record.get('button_bg')
    outline_width_str = record.get('outlineWidth') or record.get('outline_width')
    outline_offset_str = record.get('outlineOffset') or record.get('outline_offset')

    if not outline_color or not adjacent_bg:
        raise ValueError("Record missing required outline or adjacent background color")

    outline_width = parse_px(outline_width_str) if outline_width_str else 0.0
    outline_offset = parse_px(outline_offset_str) if outline_offset_str else 0.0

    ratio_adjacent = contrast_ratio(outline_color, adjacent_bg)
    ratio_button = contrast_ratio(outline_color, button_bg) if button_bg else None

    # WCAG 1.4.11 requires 3.0:1 minimum contrast for focus indicators against adjacent surfaces
    passes_adjacent = ratio_adjacent >= min_nontext_ratio
    passes_button = (ratio_button >= min_nontext_ratio) if ratio_button is not None else True
    passes_width = outline_width >= 1.0
    passes_focus = record.get('focused') is True and record.get('outlineStyle') == 'solid'

    return {
        'outline_width_px': outline_width,
        'outline_offset_px': outline_offset,
        'contrast_against_adjacent': round(ratio_adjacent, 4),
        'contrast_against_button': round(ratio_button, 4) if ratio_button is not None else None,
        'min_required_ratio': min_nontext_ratio,
        'passes_adjacent': passes_adjacent,
        'passes_button': passes_button,
        'passes_width': passes_width,
        'passes_focus': passes_focus,
        'compliant': passes_adjacent and passes_width and passes_focus,
    }


def audit_browser_file(json_path, min_nontext_ratio=3.0):
    """Audit an accessibility browser evidence JSON file."""
    path = Path(json_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {json_path}")
    data = json.loads(path.read_text(encoding='utf-8'))
    records = data.get('records', [])
    focus_audits = []
    all_compliant = True

    for rec in records:
        if rec.get('type') == 'focus_visible' or 'outlineColor' in rec:
            res = audit_focus_visible_record(rec, min_nontext_ratio=min_nontext_ratio)
            focus_audits.append({
                'viewport': rec.get('viewport'),
                'target': rec.get('target', '.dag-breadcrumb-copy-btn'),
                'audit': res
            })
            if not res['compliant']:
                all_compliant = False

    return {
        'total_audited': len(focus_audits),
        'all_compliant': bool(focus_audits) and all_compliant,
        'details': focus_audits,
    }


if __name__ == '__main__':
    if len(sys.argv) > 1:
        result = audit_browser_file(sys.argv[1])
        print(json.dumps(result, indent=2))
        sys.exit(0 if result['all_compliant'] else 1)
    else:
        print("Usage: python3 accessibility_measure.py <path_to_browser_json>", file=sys.stderr)
        sys.exit(2)
