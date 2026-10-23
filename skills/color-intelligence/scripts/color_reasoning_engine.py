#!/usr/bin/env python3
"""Generate role-based color systems from any HEX seed.

Standard library only. Contrast uses WCAG 2.x sRGB relative luminance;
color manipulation uses OKLab/OKLCH. Creative scores are heuristics.
"""
import argparse
import hashlib
import json
import math
import random
from functools import lru_cache
from pathlib import Path


def _finite(value, name):
    try:
        if not math.isfinite(value):
            raise ValueError(f'{name} must be finite')
    except TypeError as exc:
        raise ValueError(f'{name} must be numeric and finite') from exc
    return float(value)


def _finite_triplet(values, name):
    try:
        items = tuple(values)
    except TypeError as exc:
        raise ValueError(f'{name} must contain three finite numbers') from exc
    if len(items) != 3:
        raise ValueError(f'{name} must contain three finite numbers')
    return tuple(_finite(value, name) for value in items)


def parse_hex(value):
    if not isinstance(value, str):
        raise ValueError('Expected #RRGGBB or #RGB without alpha')
    h = value.strip()
    if h.startswith('#'):
        h = h[1:]
    if len(h) not in (3, 6) or any(c not in '0123456789abcdefABCDEF' for c in h):
        raise ValueError('Expected #RRGGBB or #RGB without alpha')
    if len(h) == 3:
        h = ''.join(c + c for c in h)
    return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))


def to_hex(rgb):
    values = _finite_triplet(rgb, 'rgb')
    return '#' + ''.join(f'{max(0, min(255, round(c * 255))):02X}' for c in values)


def decode(v):
    v = _finite(v, 'sRGB channel')
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055)**2.4


def encode(v):
    v = _finite(v, 'linear RGB channel')
    return 12.92 * v if v <= 0.0031308 else 1.055 * (v ** (1 / 2.4)) - 0.055


def rgb_to_oklab(rgb):
    r, g, b = [decode(v) for v in _finite_triplet(rgb, 'rgb')]
    l = 0.4122214708*r + 0.5363325363*g + 0.0514459929*b
    m = 0.2119034982*r + 0.6806995451*g + 0.1073969566*b
    s = 0.0883024619*r + 0.2817188376*g + 0.6299787005*b
    l_, m_, s_ = l**(1/3), m**(1/3), s**(1/3)
    return (0.2104542553*l_ + 0.7936177850*m_ - 0.0040720468*s_,
            1.9779984951*l_ - 2.4285922050*m_ + 0.4505937099*s_,
            0.0259040371*l_ + 0.7827717662*m_ - 0.8086757660*s_)


def oklab_to_rgb(lab):
    L, a, b = _finite_triplet(lab, 'oklab')
    l_ = L + 0.3963377774*a + 0.2158037573*b
    m_ = L - 0.1055613458*a - 0.0638541728*b
    s_ = L - 0.0894841775*a - 1.2914855480*b
    l, m, s = l_**3, m_**3, s_**3
    return tuple(encode(v) for v in (
        +4.0767416621*l - 3.3077115913*m + 0.2309699292*s,
        -1.2684380046*l + 2.6097574011*m - 0.3413193965*s,
        -0.0041960863*l - 0.7034186147*m + 1.7076147010*s
    ))


def lab_to_lch(lab):
    L, a, b = _finite_triplet(lab, 'oklab')
    return (L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360)


def lch_to_lab(L, C, H):
    L, C, H = (_finite(L, 'lightness'), _finite(C, 'chroma'), _finite(H, 'hue'))
    a = C * math.cos(math.radians(H))
    b = C * math.sin(math.radians(H))
    return (L, a, b)


@lru_cache(maxsize=16384)
def _gamut_map_cached(L, C, H):
    def fits(c):
        rgb = oklab_to_rgb(lch_to_lab(L, c, H))
        return all(-1e-8 <= v <= 1 + 1e-8 for v in rgb)

    if not fits(C):
        lo, hi = 0., C
        for _ in range(35):
            mid = (lo + hi) / 2
            if fits(mid):
                lo = mid
            else:
                hi = mid
        C = lo
    rgb = oklab_to_rgb(lch_to_lab(L, C, H))
    return to_hex(tuple(max(0., min(1., v)) for v in rgb))


def gamut_map(L, C, H):
    """Reduce chroma at fixed L/H into sRGB; not CSS Color 4 local-MINDE."""
    L = max(0., min(1., _finite(L, 'lightness')))
    C = max(0., _finite(C, 'chroma'))
    H = _finite(H, 'hue') % 360
    return _gamut_map_cached(L, C, H)


gamut_map.cache_clear = _gamut_map_cached.cache_clear
gamut_map.cache_info = _gamut_map_cached.cache_info


def luminance(hex_color):
    r, g, b = [decode(v) for v in parse_hex(hex_color)]
    return 0.2126*r + 0.7152*g + 0.0722*b


def contrast(c1, c2):
    l1, l2 = sorted((luminance(c1), luminance(c2)), reverse=True)
    return (l1 + .05) / (l2 + .05)


def delta_ok(c1, c2):
    a, b = rgb_to_oklab(parse_hex(c1)), rgb_to_oklab(parse_hex(c2))
    return math.sqrt(sum((x-y)**2 for x, y in zip(a, b)))


def hue_distance(h1, h2):
    h1, h2 = _finite(h1, 'hue'), _finite(h2, 'hue')
    d = abs(h1-h2) % 360
    return min(d, 360-d)


def choose_ink(bg, required=4.5):
    parse_hex(bg)
    required = _finite(required, 'required contrast')
    if required <= 0:
        raise ValueError('required contrast must be positive')
    candidates = ['#0A0A0A', '#FFFFFF']
    selected = max(candidates, key=lambda x: contrast(x, bg))
    return selected if contrast(selected, bg) >= required else None


def select_active_color(hue, chroma, surface, dark, target_L):
    """Find a color >=3:1 to surface with readable ink >=4.5:1."""
    hue = _finite(hue, 'hue') % 360
    chroma = _finite(chroma, 'chroma')
    target_L = _finite(target_L, 'target lightness')
    if chroma < 0:
        raise ValueError('chroma must be non-negative')
    if not isinstance(dark, bool):
        raise ValueError('dark must be boolean')
    surface = to_hex(parse_hex(surface))
    levels = [(abs((0.27 + 0.69*k/100) - target_L), k) for k in range(101)]
    levels.sort()
    best = None
    for distance, k in levels:
        if best is not None and distance > best[0]:
            break
        L = 0.27 + 0.69*k/100
        color = gamut_map(L, chroma, hue)
        ink = choose_ink(color)
        if ink is None or contrast(color, surface) < 3:
            continue
        actual_chroma = lab_to_lch(rgb_to_oklab(parse_hex(color)))[1]
        score = distance + max(0., chroma - actual_chroma)*0.9
        if best is None or (score, k) < (best[0], best[1]):
            best = (score, k, color, ink)
    if best is None:
        raise RuntimeError('No feasible accessible active color')
    return best[2], best[3]


def derive(seed, mode='dark', expression=0.85, tension=0.78,
           variants=3, explore=320, hue=None):
    if mode not in ('dark', 'light'):
        raise ValueError('mode must be dark or light')
    expression = _finite(expression, 'expression')
    tension = _finite(tension, 'tension')
    if not (0 <= expression <= 1 and 0 <= tension <= 1):
        raise ValueError('expression and tension must be within [0, 1]')
    if not isinstance(variants, int) or isinstance(variants, bool) or not 1 <= variants <= 20:
        raise ValueError('variants must be an integer within [1, 20]')
    if not isinstance(explore, int) or isinstance(explore, bool) or not 30 <= explore <= 2000:
        raise ValueError('explore must be an integer within [30, 2000]')
    if hue is not None:
        hue = _finite(hue, 'hue')
    canonical_seed = to_hex(parse_hex(seed))
    seed_L, seed_C, seed_H = lab_to_lch(rgb_to_oklab(parse_hex(canonical_seed)))
    neutral = seed_C < 0.015
    if hue is not None:
        H = hue % 360
    elif neutral:
        H = int(hashlib.sha256(canonical_seed.encode()).hexdigest()[:6], 16) % 360
    else:
        H = seed_H
    dark = mode == 'dark'
    surface = gamut_map(.135 if dark else .975, min(.012, seed_C*.075), H)
    card = gamut_map(.195 if dark else .998, min(.015, seed_C*.095), H)
    text = gamut_map(.945 if dark else .18, .006, H)
    muted = gamut_map(.73 if dark else .445, .012, H)
    seed_int = int(hashlib.sha256(
        f'{canonical_seed}|{mode}|{expression}|{tension}'.encode()
    ).hexdigest()[:15], 16)
    rng = random.Random(seed_int)
    target_separation = 35 + 130*tension
    c_primary = min(.3, max(.065, seed_C * (.95 + .25*expression) + .04*expression))
    primary, ink = select_active_color(H, c_primary, surface, dark, .75 if dark else .54)
    specs = []
    for _ in range(explore):
        sign = -1 if rng.randrange(2) else 1
        angle = max(20, min(178, rng.gauss(target_separation, 32)))
        secondary_h = (H + sign*angle) % 360
        c_secondary = rng.uniform(.075, .14 + .13*expression)
        secondary, secondary_ink = select_active_color(
            secondary_h, c_secondary, surface, dark, .72 if dark else .54)
        highlight = gamut_map(
            .82 if dark else .62, min(.28, c_secondary*1.12),
            (secondary_h + (18 if sign > 0 else -18)) % 360)
        ratios = {
            'body_text_on_surface': contrast(text, surface),
            'muted_text_on_surface': contrast(muted, surface),
            'primary_on_surface': contrast(primary, surface),
            'primary_text_on_primary': contrast(ink, primary),
            'secondary_on_surface': contrast(secondary, surface),
            'secondary_text_on_secondary': contrast(secondary_ink, secondary),
        }
        limits = {
            'body_text_on_surface': 4.5,
            'muted_text_on_surface': 4.5,
            'primary_on_surface': 3.0,
            'primary_text_on_primary': 4.5,
            'secondary_on_surface': 3.0,
            'secondary_text_on_secondary': 4.5,
        }
        if any(ratios[k] + 1e-9 < threshold for k, threshold in limits.items()):
            continue
        actual_secondary_c = lab_to_lch(rgb_to_oklab(parse_hex(secondary)))[1]
        separation = hue_distance(H, secondary_h)
        harmony = math.exp(-((separation-target_separation)/46)**2)
        chromatic = min(1, actual_secondary_c/.19)
        accessibility = min(1, min(ratios[k]/limits[k] for k in limits)/1.55)
        spatial = max(.015, .105-.085*expression)
        score = round(100*(.45*harmony + .30*chromatic + .25*accessibility), 2)
        specs.append({
            'score_heuristic': score,
            'palette': {
                'surface': surface, 'card': card, 'text': text,
                'muted_text': muted, 'primary': primary, 'on_primary': ink,
                'secondary': secondary, 'on_secondary': secondary_ink,
                'decorative_glow': highlight,
            },
            'contrast': {k: round(v, 3) for k, v in ratios.items()},
            'hue_separation_degrees': round(separation, 2),
            'deltaEOK_primary_secondary': round(delta_ok(primary, secondary), 4),
            'accent_area_fraction_suggestion': round(spatial, 4),
            'score_parts': {
                'hue_dialogue': round(harmony, 4),
                'chroma_energy': round(chromatic, 4),
                'contrast_margin': round(accessibility, 4),
            },
        })
    specs.sort(key=lambda x: x['score_heuristic'], reverse=True)
    diverse = []
    for candidate in specs:
        if all(delta_ok(candidate['palette']['secondary'], p['palette']['secondary']) >= .08
               for p in diverse):
            diverse.append(candidate)
            if len(diverse) >= variants:
                break
    if not diverse:
        raise RuntimeError('No feasible palette')
    return {
        'input': {
            'seed': canonical_seed, 'mode': mode, 'expression': expression,
            'tension': tension, 'neutral_seed_hue_inferred': neutral and hue is None,
            'hue_override': hue, 'explore': explore,
        },
        'seed_oklch': {
            'L': round(seed_L, 4), 'C': round(seed_C, 4), 'H': round(seed_H, 1),
        },
        'rules': {
            'contrast_normative': 'WCAG 2.x 4.5:1 text; 3:1 graphics/active boundaries',
            'gamut': 'Fixed L and H, reduce C into sRGB; educational simplified mapper',
            'score': 'Non-normative design heuristic. Visual review required.',
            'disclaimer': 'Does not certify UI accessibility: test actual states, opacity, gradients, focus and color vision.',
        },
        'variants': diverse,
    }


def css_output(result, variant=0):
    palette = result['variants'][variant]['palette']
    lines = (f'  --hermes-{key.replace("_", "-")}: {value};'
             for key, value in palette.items())
    return ':root {\n' + '\n'.join(lines) + '\n}\n'


def main():
    parser = argparse.ArgumentParser(
        description='Compute palettes from any HEX seed using OKLCH + WCAG')
    parser.add_argument('--seed', required=True, help='Any #RRGGBB or #RGB')
    parser.add_argument('--mode', default='dark', choices=['dark', 'light'])
    parser.add_argument('--expression', type=float, default=.85)
    parser.add_argument('--tension', type=float, default=.78)
    parser.add_argument('--variants', type=int, default=3)
    parser.add_argument('--explore', type=int, default=320)
    parser.add_argument('--hue', type=float, default=None,
                        help='Optional explicit hue anchor for neutral seed')
    parser.add_argument('--json-out', type=Path)
    parser.add_argument('--css-out', type=Path)
    args = parser.parse_args()
    if not (1 <= args.variants <= 20 and 30 <= args.explore <= 2000):
        parser.error('variants must be 1..20 and explore must be 30..2000')
    try:
        result = derive(args.seed, args.mode, args.expression, args.tension,
                        args.variants, args.explore, args.hue)
    except (ValueError, RuntimeError) as exc:
        parser.error(str(exc))
    payload = json.dumps(result, indent=2)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(payload + '\n', encoding='utf-8')
    if args.css_out:
        args.css_out.parent.mkdir(parents=True, exist_ok=True)
        args.css_out.write_text(css_output(result), encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
