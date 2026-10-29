#!/usr/bin/env python3
"""Photo-first news cover: 2 slides (hook + CTA), text placed by the photograph.

Two hard rules encoded here, both learned the hard way:
  1. Never typeset with Liberation/DejaVu — they read like office documents and
     the user rates them far below editorial type. Use the Google Fonts stack.
  2. Never estimate the headline block height with a size*0.94 formula. Measure
     real glyph bounds with draw.textbbox() and shrink until the block clears
     the subject. A formula is off by ~80px on a 3-line Anton headline.

Usage:
    python3 photo_cover.py '<jobs-json>' <out-dir>
    jobs-json: [{"src": "/path/photo.jpg", "kicker": "DEEPMIND · 28 OKT 2026",
                "lines": ["AI terkuat Google,", "tak bisa kamu pakai."], "tag": "a"}]
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageStat

W, H, M = 1080, 1350, 74
RED, WHITE, INK = '#C8201E', '#FFFFFF', '#141414'
SAFE_GAP = 40          # minimum px between headline block and subject
FONT_DIR = Path(os.path.expanduser('~/.local/share/fonts'))

FONTS = {
    'display_serif': 'InstrumentSerif-Regular.ttf',   # prestige, most editorial
    'display_sans': 'InterTight.ttf',                 # Swiss, fastest to read
    'display_posters': 'Anton-Regular.ttf',           # loud cond, use sparingly
    'label': 'JetBrainsMono.ttf',
}
SOURCES = {
    'InstrumentSerif-Regular.ttf': 'instrumentserif/InstrumentSerif-Regular.ttf',
    'InterTight.ttf': 'intertight/InterTight%5Bwght%5D.ttf',
    'Anton-Regular.ttf': 'anton/Anton-Regular.ttf',
    'JetBrainsMono.ttf': 'jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf',
}
BASE = 'https://raw.githubusercontent.com/google/fonts/main/ofl/'


def ensure_fonts():
    """Download the editorial stack once. Skips files already present."""
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    for name, path in SOURCES.items():
        dest = FONT_DIR / name
        if dest.exists() and dest.stat().st_size > 10_000:
            continue
        req = urllib.request.Request(BASE + path, headers={'User-Agent': 'Mozilla/5.0'})
        dest.write_bytes(urllib.request.urlopen(req, timeout=30).read())


def load(name, size, weight=None):
    f = ImageFont.truetype(str(FONT_DIR / FONTS[name]), size)
    if weight is not None:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def crop45(src: Image.Image) -> Image.Image:
    sw, sh = src.size
    cw = int(sh * W / H)
    if cw > sw:
        ch = int(sw * H / W)
        top = (sh - ch) // 2
        return src.crop((0, top, sw, top + ch)).resize((W, H), Image.Resampling.LANCZOS)
    left = (sw - cw) // 2
    return src.crop((left, 0, left + cw, sh)).resize((W, H), Image.Resampling.LANCZOS)


def edge_map(im):
    return im.convert('L').filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(6))


def band_scores(edges):
    bands = {'top': (0, 0, W, int(H * 0.34)), 'bottom': (0, int(H * 0.62), W, H)}
    return {k: ImageStat.Stat(edges.crop(b)).mean[0] for k, b in bands.items()}


def zone_lum(im, box):
    return ImageStat.Stat(im.convert('L').crop(box)).mean[0]


def subject_top(edges, default=420):
    """First row (top-down) whose detail clearly exceeds the calm baseline."""
    prof = list(edges.resize((1, H)).getdata())
    vals = sorted(prof)
    median = vals[len(vals) // 2] or 1
    for y in range(90, H):
        if prof[y] > median * 1.8 and prof[y] > 6:
            return y
    return default


def scrim(im, y0, y1, peak):
    layer = Image.new('L', (1, H), 0)
    d = ImageDraw.Draw(layer)
    for y in range(y0, y1):
        t = (y - y0) / max(1, (y1 - y0))
        d.point((0, y), fill=int(peak * (1 - t) ** 1.35))
    im.paste(Image.new('RGB', (W, H), '#080A0E'), (0, 0), layer.resize((W, H)))


def tracked_w(font, text, tr):
    return sum(font.getlength(c) for c in text) + tr * (len(text) - 1)


def draw_tracked(d, xy, text, font, tr, fill):
    x, y = xy
    for c in text:
        d.text((x, y), c, font=font, fill=fill)
        x += font.getlength(c) + tr


def fit_lines(d, lines, face, weight, tr, lh, y0, ceiling, start=138, floor=58):
    """Shrink until both width and REAL glyph bottom satisfy the constraints."""
    size = start
    while size > floor:
        f = load(face, size, weight)
        widest = max(tracked_w(f, l, tr) for l in lines)
        y, bottom = y0, 0
        for l in lines:
            bottom = max(bottom, d.textbbox((0, y), l, font=f)[3])
            y += int(size * lh)
        if widest <= W - 2 * M + 8 and bottom <= ceiling:
            return f, size
        size -= 2
    return load(face, floor, weight), floor


def build(src_path, kicker, lines, out_dir: Path, tag, face='display_serif',
          weight=None, tr=0.0, lh=1.06):
    src = Image.open(src_path).convert('RGB')
    base = crop45(src)
    base = ImageEnhance.Contrast(base).enhance(1.06)
    edges = edge_map(base)

    scores = band_scores(edges)
    where = min(scores, key=scores.get)
    head_top = subject_top(edges)

    if where == 'top':
        y0 = 168
        ceiling = head_top - SAFE_GAP
        band = (0, 0, W, max(int(H * 0.34), y0 + 60))
    else:
        y0 = int(H * 0.66)
        ceiling = H - 150
        band = (0, int(H * 0.60), W, H)

    im = base.copy()
    lum = zone_lum(im, band)
    fg = INK if lum > 148 else WHITE
    busy = scores[where]
    peak = (0.36 + min(0.24, busy / 180)) if fg == INK else (0.40 + min(0.24, busy / 150))
    scrim(im, band[1], band[3], int(peak * 255))
    scrim(im, H - 170, H, 175)

    d = ImageDraw.Draw(im)
    lab = load('label', 20, 500)
    draw_tracked(d, (M, 92), kicker.upper(), lab, 6, fg)
    d.line((M, 128, M + 118, 128), fill=RED, width=5)

    f, size = fit_lines(d, lines[:2], face, weight, tr, lh, y0, ceiling)
    y = y0
    for l in lines[:2]:
        draw_tracked(d, (M - 4, y), l, f, tr, fg)
        y += int(size * lh)

    draw_tracked(d, (M, H - 92), '@SPUTARAI', load('label', 18, 500), 5, WHITE)
    d.text((W - M, H - 92), '01 / 02', font=load('label', 18, 400), fill=WHITE, anchor='ra')
    p1 = out_dir / f'{tag}-01.png'
    im.save(p1, optimize=True)

    bg = base.filter(ImageFilter.GaussianBlur(30))
    bg = ImageEnhance.Brightness(bg).enhance(0.24)
    bg = ImageEnhance.Color(bg).enhance(0.6)
    d2 = ImageDraw.Draw(bg)
    cy = H // 2 - 150
    d2.line((M, cy - 40, M + 120, cy - 40), fill=RED, width=4)
    q = ['Kenapa kamu', 'tidak bisa pakai?']
    fq, sq = fit_lines(d2, q, face, weight, tr, lh, cy + 10, H - 320, start=110)
    y = cy + 10
    for l in q:
        draw_tracked(d2, (M - 4, y), l, fq, tr, WHITE)
        y += int(sq * lh)
    d2.text((M, y + 34), 'Konteks, angka, dan sumber lengkap ada di caption.',
            font=load('display_sans', 30, 400), fill='#E8E4DC')
    d2.text((M, y + 76), 'Baca di bawah.', font=load('display_sans', 30, 400), fill=WHITE)
    draw_tracked(d2, (M, H - 92), '@SPUTARAI', load('label', 18, 500), 5, WHITE)
    d2.text((W - M, H - 92), '02 / 02', font=load('label', 18, 400), fill=WHITE, anchor='ra')
    p2 = out_dir / f'{tag}-02.png'
    bg.save(p2, optimize=True)

    return {'tag': tag, 'band': where, 'subject_top': head_top,
            'headline_bottom_limit': ceiling, 'font_size': size,
            'ink': 'dark' if fg == INK else 'light', 'slides': [str(p1), str(p2)]}


if __name__ == '__main__':
    ensure_fonts()
    jobs = json.loads(sys.argv[1])
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    face = os.environ.get('COVER_FACE', 'display_serif')
    print(json.dumps([build(j['src'], j['kicker'], j['lines'], out, j['tag'], face=face)
                      for j in jobs], indent=1))
