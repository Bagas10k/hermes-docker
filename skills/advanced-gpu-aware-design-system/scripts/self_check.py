#!/usr/bin/env python3
"""Neutral self-check for token and CSS motion audits.

Runs real positive and negative subprocess checks across all acceptance cases.
"""
import json, subprocess, sys, tempfile
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
TOKEN_SCRIPT = SCRIPTS_DIR / 'token_audit.py'
CSS_SCRIPT = SCRIPTS_DIR / 'css_motion_audit.py'
BUNDLED_TOKENS = SCRIPTS_DIR.parent / 'assets' / 'tokens.example.json'

def run_cmd(cmd):
    p = subprocess.run([sys.executable, *cmd], capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()

def main():
    checks = 0
    passed = 0

    def check(desc, cmd, exp_rc, exp_in=(), exp_not=()):
        nonlocal checks, passed
        checks += 1
        rc, out, err = run_cmd(cmd)
        comb = f'{out} {err}'
        assert rc == exp_rc, f'{desc}: expected rc={exp_rc}, got {rc} ({comb})'
        for s in exp_in:
            assert s in comb, f'{desc}: expected {s!r} in ({comb})'
        for s in exp_not:
            assert s not in comb, f'{desc}: unexpected {s!r} in ({comb})'
        passed += 1

    with tempfile.TemporaryDirectory(prefix='audit-self-check-') as td:
        tmp = Path(td)
        # Token positive/negative checks
        check('Bundled tokens', [str(TOKEN_SCRIPT), str(BUNDLED_TOKENS)], 0, ('Token audit: PASS',))
        v = tmp / 'v.json'; v.write_text(json.dumps({'a': {'x': '1'}, 'b': '{a.x}'}))
        check('Valid alias', [str(TOKEN_SCRIPT), str(v)], 0, ('Token audit: PASS',))
        m = tmp / 'm.json'; m.write_text(json.dumps({'a': '{missing.token}'}))
        check('Missing ref', [str(TOKEN_SCRIPT), str(m)], 1, ('Missing reference: missing.token',))
        c = tmp / 'c.json'; c.write_text(json.dumps({'a': '{b}', 'b': '{a}'}))
        check('Cycle ref', [str(TOKEN_SCRIPT), str(c)], 1, ('Cycle: a -> b -> a',))
        b = tmp / 'b.json'; b.write_text('{bad')
        check('Malformed JSON', [str(TOKEN_SCRIPT), str(b)], 1, ('ERROR:',), ('Traceback',))
        r = tmp / 'r.json'; r.write_text('"primitive string root"')
        check('Non-dict root', [str(TOKEN_SCRIPT), str(r)], 1, ('ERROR:', 'dict'))
        check('Nonexistent token', [str(TOKEN_SCRIPT), str(tmp / 'none.json')], 1, ('ERROR:',), ('Traceback',))

        # CSS positive/negative checks
        cl = tmp / 'cl.css'; cl.write_text('.box { transform: scale(1); opacity: 1; }')
        check('CSS clean', [str(CSS_SCRIPT), str(cl)], 0, ('0 warnings',), ('WARN',))
        wc = tmp / 'wc.css'; wc.write_text('* { will-change: transform; }\n*, *::before, *::after { will-change: opacity; }')
        check('CSS wildcard', [str(CSS_SCRIPT), str(wc)], 0, ('wildcard will-change',))
        kf = tmp / 'kf.css'; kf.write_text('@keyframes s { from { height: 0; } to { height: 10px; } }')
        check('CSS keyframes', [str(CSS_SCRIPT), str(kf)], 0, ('potential layout animation',))
        br = tmp / 'br.css'; br.write_text('.d { transition: bottom 1s, right 1s; }')
        check('CSS bottom/right', [str(CSS_SCRIPT), str(br)], 0, ('potential layout animation',))
        inf = tmp / 'inf.css'; inf.write_text('.s { animation-iteration-count: infinite; }')
        check('CSS longhand infinite', [str(CSS_SCRIPT), str(inf)], 0, ('infinite animation',))
        cm = tmp / 'cm.css'; cm.write_text('/* * { will-change: transform; } transition: width 1s; */')
        check('CSS comment', [str(CSS_SCRIPT), str(cm)], 0, ('0 warnings',), ('WARN',))
        ed = tmp / 'empty'; ed.mkdir()
        check('CSS empty dir', [str(CSS_SCRIPT), str(ed)], 2, ('NOT RUN: no CSS files found',))
        check('CSS nonexistent', [str(CSS_SCRIPT), str(tmp / 'none.css')], 1, ('ERROR:',))

    print(f'Self-check PASS: {passed}/{checks} checks verified successfully')
    return 0

if __name__ == '__main__':
    sys.exit(main())
