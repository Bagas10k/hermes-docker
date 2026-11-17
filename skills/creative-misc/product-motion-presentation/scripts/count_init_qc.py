#!/usr/bin/env python3
"""QC angka berhitung: teks awal elemen harus sama dengan nilai `from` hitungan.

Pakai:
  python3 count_init_qc.py <dir_compositions | berkas.html ...> [--strict]
  python3 count_init_qc.py --selftest

Pola yang dicari (keluaran makro count() setelah diekspansi generator):
  const e=document.querySelector('#id'),o={v:FROM};tl.to(o,{v:TO,...,onUpdate:...},T)

Cacat yang ditangkap: HTML menulis nilai akhir ("480", "22.9 ms") sementara
hitungan mulai dari 0. Selama kartu masuk, penonton melihat angka akhir, lalu
angka itu jatuh ke 0 dan naik lagi. Snapshot di detik puncak tidak menangkapnya,
karena kedipnya hanya 2-5 frame di awal adegan.

Hanya hitungan pertama per id (urutan sumber) yang dicek; hitungan lanjutan
(misal lonjakan 14.8 -> 22.9) wajar mulai dari nilai sebelumnya.
--strict: exit 1 bila ada MISMATCH.
"""
import glob, html, os, re, sys

COUNT_RE = re.compile(
    r"querySelector\(\s*['\"]#([\w-]+)['\"]\s*\)\s*,\s*\w+\s*=\s*\{\s*v\s*:\s*(-?[\d.]+)\s*\}")
NUM_RE = re.compile(r"\d[\d.,]*")


def candidates(tok):
    """Tafsiran angka yang mungkin: desimal titik, ribuan titik (id-ID), desimal koma."""
    tok = tok.rstrip('.,')
    out = set()
    for s in (tok.replace(',', ''), tok.replace('.', '').replace(',', ''),
              tok.replace('.', '').replace(',', '.')):
        try:
            out.add(float(s))
        except ValueError:
            pass
    return out


def initial_text(src, el_id):
    m = re.search(r'id=["\']%s["\'][^>]*>(.*?)</' % re.escape(el_id), src, re.S)
    if not m:
        return None
    return html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip()


def check_source(src, name='?'):
    rows, seen = [], set()
    for m in COUNT_RE.finditer(src):
        el_id, frm = m.group(1), float(m.group(2))
        if el_id in seen:
            continue
        seen.add(el_id)
        text = initial_text(src, el_id)
        if text is None:
            rows.append(('WARN', name, el_id, frm, None, 'elemen tidak ditemukan'))
            continue
        tok = NUM_RE.search(text)
        if not tok:
            rows.append(('WARN', name, el_id, frm, text, 'teks awal tanpa angka; pastikan tersembunyi sampai hitungan mulai'))
            continue
        ok = any(abs(c - frm) < 1e-9 for c in candidates(tok.group(0)))
        rows.append(('OK' if ok else 'MISMATCH', name, el_id, frm, text,
                     '' if ok else 'teks awal != from; tulis teks awal = nilai from (format sama)'))
    return rows


def files(args):
    for a in args:
        if os.path.isdir(a):
            yield from sorted(glob.glob(os.path.join(a, '*.html')))
        else:
            yield a


def main(argv):
    paths = [a for a in argv if not a.startswith('--')]
    if not paths:
        print(__doc__)
        return 0
    rows = []
    for p in files(paths):
        rows += check_source(open(p, encoding='utf-8').read(), os.path.basename(p))
    for st, name, el_id, frm, text, why in rows:
        print('%-8s %-10s #%-14s from=%-10g teks=%r %s' % (st, name, el_id, frm, text, why))
    bad = sum(r[0] == 'MISMATCH' for r in rows)
    print('hitungan %d | MISMATCH %d | WARN %d' % (len(rows), bad, sum(r[0] == 'WARN' for r in rows)))
    print('VONIS', 'LULUS' if not bad else 'GAGAL')
    return 1 if bad and '--strict' in argv else 0


def _selftest():
    src = ("<b id='a'>480</b><b id=\"b\">0%</b><b id=\"c\">4.200.000</b><b id=\"d\">(0)</b><b id=\"e\">22.9 ms</b>"
           "{const e=document.querySelector('#a'),o={v:0};}"
           "{const e=document.querySelector('#b'),o={v:0};}"
           "{const e=document.querySelector('#c'),o={v:4200000};}"
           "{const e=document.querySelector('#d'),o={v:0};}"
           "{const e=document.querySelector('#e'),o={v:22.9};}"
           "{const e=document.querySelector('#a'),o={v:480};}")
    st = {r[2]: r[0] for r in check_source(src)}
    assert st == {'a': 'MISMATCH', 'b': 'OK', 'c': 'OK', 'd': 'OK', 'e': 'OK'}, st
    print('selftest ok')


if __name__ == '__main__':
    if sys.argv[1:] == ['--selftest']:
        _selftest()
    else:
        sys.exit(main(sys.argv[1:]))
