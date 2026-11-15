#!/usr/bin/env python3
"""QC grafik keyframe dari `hyperframes keyframes <comp.html> --json`.

Pakai:
  python3 kf_qc.py kf_sN.json [--png lanes.png] [--strict]

Mencetak: distribusi ease, back.out berlebih, overlap target+properti,
sambungan patah (kecepatan melompat antar-tween berurutan), lapis kamera
(composedWith), dan puncak tween aktif. --png menggambar grafik lajur
(satu baris per target, batang = tween, merah = sambungan patah/overlap).
--strict: exit 1 bila ada pelanggaran syarat lulus.
"""
import collections, json, re, sys

EPS = 1e-3
CAM_RE = r'cam|rig|drift|zoom|camera|push'  # nama wrapper kamera


def speed_ends(ease):
    """(kecepatan relatif di awal, di akhir): 0 = diam, 1 = bergerak."""
    e = (ease or 'none').lower()
    if e in ('none', 'linear') or e.startswith('steps'):
        return 1, 1
    if e.endswith('.inout') or e.startswith('sine.inout'):
        return 0, 0
    if e.endswith('.in'):
        return 0, 1
    if e.endswith('.out') or '.out(' in e:
        return 1, 0
    if e.startswith('custom') or 'ease' in e:
        return None, None  # CustomEase: tidak bisa ditebak dari nama
    return 1, 0  # GSAP: ease tanpa sufiks = .out


def back_over(ease, limit=2.0):
    m = re.match(r'back\.(?:in|out|inout)\(([\d.]+)\)', (ease or '').lower())
    return bool(m) and float(m.group(1)) > limit


def analyse(d):
    comp = d['compositions'][0]
    semua = comp['tweens']
    # analyzer statis tidak bisa menghitung posisi berbasis variabel/ekspresi:
    # start dilaporkan ~1e9 dan end None. Dihitung terpisah, bukan dianalisis.
    tw = [t for t in semua if t.get('end') is not None and t.get('start', 0) < 1e8]
    rep = {'n': len(tw), 'unresolved': len(semua) - len(tw)}
    eases = collections.Counter(t.get('ease') or 'none' for t in tw)
    rep['ease'] = eases.most_common()
    rep['ease_dominan'] = eases.most_common(1)[0][1] / max(len(tw), 1) if tw else 0
    rep['back_over'] = sorted({t['ease'] for t in tw if back_over(t.get('ease'))})

    by = collections.defaultdict(list)
    for t in tw:
        props = set()
        for k in t.get('keyframes') or []:
            props |= set(k.get('properties') or {})
        for p in props:
            by[(str(t['target']), p)].append(t)
    overlaps, joins = [], []
    for (tgt, p), lst in by.items():
        lst.sort(key=lambda t: t['start'])
        for a, b in zip(lst, lst[1:]):
            if b['start'] < a['end'] - EPS:
                overlaps.append((tgt, p, a['start'], a['end'], b['start'], b['end']))
            elif b['start'] - a['end'] <= 1 / 30 + EPS:
                _, a_end = speed_ends(a.get('ease'))
                b_start, _ = speed_ends(b.get('ease'))
                if None not in (a_end, b_start) and a_end != b_start:
                    joins.append((tgt, p, round(a['end'], 3), a.get('ease'), b.get('ease')))
    rep['overlap'] = overlaps
    rep['patah'] = joins

    # composedWith = semua leluhur beranimasi (termasuk kartu/perangkat induk).
    # Lapis kamera = leluhur/target yang namanya wrapper kamera.
    cam_re = re.compile(CAM_RE)
    cams = {str(t['target']) for t in tw if cam_re.search(str(t['target']))}
    stack = set()
    for t in tw:
        chain = {c.get('selector') for c in t.get('composedWith') or []} | {str(t['target'])}
        hit = {c for c in chain if c and cam_re.search(c)}
        if len(hit) > len(stack):
            stack = hit
    rep['kamera'] = sorted(stack or cams)
    rep['lapis_maks'] = len(rep['kamera'])

    end = max((t['end'] for t in tw), default=0)
    rep['durasi'] = end
    rep['puncak_aktif'] = max((sum(t['start'] <= i / 10 < t['end'] for t in tw)
                               for i in range(int(end * 10) + 1)), default=0)
    rep['tweens'] = tw
    return rep


def gagal(rep):
    alasan = []
    if rep['ease_dominan'] > 0.5:
        alasan.append('satu ease > 50% tween')
    if rep['back_over']:
        alasan.append('back.out > 2: %s' % ', '.join(rep['back_over']))
    if rep['overlap']:
        alasan.append('%d overlap target+properti' % len(rep['overlap']))
    if rep['patah']:
        alasan.append('%d sambungan patah' % len(rep['patah']))
    if rep['unresolved']:
        alasan.append('%d tween buta-QC (generator wajib menulis durasi/posisi literal)' % rep['unresolved'])
    if rep['lapis_maks'] > 1:
        alasan.append('kamera %d lapis bertumpuk (maks 1)' % rep['lapis_maks'])
    return alasan


def lanes_png(rep, path):
    from PIL import Image, ImageDraw
    tw = rep['tweens']
    targets = sorted({str(t['target']) for t in tw}, key=lambda s: min(t['start'] for t in tw if str(t['target']) == s))
    bad = {(o[0], o[2]) for o in rep['patah']} | {(o[0], o[4]) for o in rep['overlap']}
    W, L, H, R = 1600, 260, 22, 20
    sx = (W - L - R) / max(rep['durasi'], 0.1)
    img = Image.new('RGB', (W, 40 + H * len(targets)), '#ffffff')
    g = ImageDraw.Draw(img)
    for s in range(int(rep['durasi']) + 1):
        x = L + s * sx
        g.line([(x, 20), (x, img.height)], fill='#dddddd')
        g.text((x + 2, 4), '%ds' % s, fill='#333333')
    for i, tgt in enumerate(targets):
        y = 30 + i * H
        if i % 2:
            g.rectangle([0, y, W, y + H], fill='#f3f3f3')
        g.text((6, y + 4), tgt[:38], fill='#111111')
        for t in tw:
            if str(t['target']) != tgt:
                continue
            x0 = L + t['start'] * sx
            x1 = max(L + t['end'] * sx, x0 + 5)
            ambient = t['end'] - t['start'] > 0.8 * rep['durasi']
            col = '#c62828' if (tgt, t['start']) in bad or (tgt, round(t['start'], 3)) in bad else ('#b0bec5' if ambient else '#37474f')
            g.rectangle([x0, y + 3, x1, y + H - 3], fill=col)
    img.save(path)
    return path


def main(argv):
    if not argv or argv[0] in ('-h', '--help'):
        print(__doc__)
        return 0
    rep = analyse(json.load(open(argv[0])))
    print('tween', rep['n'], '| tak-terhitung', rep['unresolved'], '| durasi %.2fs' % rep['durasi'], '| puncak aktif', rep['puncak_aktif'])
    print('ease', rep['ease'][:8], '| dominan %.0f%%' % (rep['ease_dominan'] * 100))
    print('back.out>2', rep['back_over'] or '-')
    for o in rep['overlap'][:10]:
        print('OVERLAP', o)
    for j in rep['patah'][:10]:
        print('PATAH', j)
    print('lapis kamera', rep['lapis_maks'], rep['kamera'])
    if '--png' in argv:
        print('png', lanes_png(rep, argv[argv.index('--png') + 1]))
    alasan = gagal(rep)
    print('VONIS', 'LULUS' if not alasan else 'GAGAL: ' + '; '.join(alasan))
    return 1 if alasan and '--strict' in argv else 0


def _selftest():
    d = {'compositions': [{'tweens': [
        {'target': '#a', 'start': 0, 'end': 0.5, 'ease': 'power3.out', 'keyframes': [{'properties': {'x': 0}}]},
        {'target': '#a', 'start': 0.5, 'end': 1, 'ease': 'power3.out', 'keyframes': [{'properties': {'x': 1}}]},
        {'target': '#a', 'start': 0.9, 'end': 1.2, 'ease': 'back.out(3)', 'keyframes': [{'properties': {'x': 2}}],
         'composedWith': [{'selector': '#rig'}, {'selector': '#drift'}, {'selector': '#card'}]},
    ]}]}
    r = analyse(d)
    assert len(r['patah']) == 1 and len(r['overlap']) == 1 and r['back_over'] == ['back.out(3)']
    assert r['lapis_maks'] == 2, r['kamera'] and len(gagal(r)) == 5
    assert speed_ends('power3.in') == (0, 1) and speed_ends('expo') == (1, 0)
    print('selftest ok')


if __name__ == '__main__':
    if sys.argv[1:] == ['--selftest']:
        _selftest()
    else:
        sys.exit(main(sys.argv[1:]))
