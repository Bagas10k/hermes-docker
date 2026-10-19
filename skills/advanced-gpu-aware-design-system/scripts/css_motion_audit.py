#!/usr/bin/env python3
"""Heuristic CSS scan: warnings require manual review, not proof of GPU usage.

Scope limitation: Uses lightweight regex heuristics, not a full CSS parser.
Flags universal will-change, layout animations in transitions and @keyframes,
expensive backdrop blur, and infinite animations. Exit code 0 is intentional
for heuristic warnings; exit 1 on path/read error; exit 2 on empty CSS directory.
"""
import re, sys
from pathlib import Path

PATTERNS = {
    'global will-change': r'\bwill-change\s*:\s*(?:all|auto\s*,)',
    'potential layout animation': r'\b(?:transition(?:-property)?|animation)\s*:[^;{}]*\b(?:(?:min-|max-)?(?:width|height)|top|bottom|left|right|margin(?:-[a-z]+)?|padding(?:-[a-z]+)?|inset(?:-[a-z]+)?|inline-size|block-size)\b',
    'expensive backdrop blur': r'(?:-webkit-)?backdrop-filter\s*:[^;{}]*blur\(',
    'infinite animation': r'\banimation(?:-iteration-count)?\s*:[^;{}]*\binfinite\b',
}

def strip_comments(text):
    return re.sub(r'/\*[\s\S]*?\*/', lambda m: re.sub(r'[^\n]', ' ', m.group(0)), text)

def mask_keyframes(text, src):
    out = list(text)
    warnings = []
    for m in re.finditer(r'@keyframes\s+([^{]+)\{', text, re.I):
        start = m.end()
        depth = 1
        i = start
        while i < len(text) and depth > 0:
            if text[i] == '{': depth += 1
            elif text[i] == '}': depth -= 1
            i += 1
        kf_body = text[start:i-1]
        for lm in re.finditer(r'(?<![-a-zA-Z])(?:(?:min-|max-)?(?:width|height)|top|bottom|left|right|margin(?:-[a-z]+)?|padding(?:-[a-z]+)?|inset(?:-[a-z]+)?|inline-size|block-size)\s*:[^;}]*', kf_body, re.I):
            pos = start + lm.start()
            line = src.count('\n', 0, pos) + 1
            warnings.append((line, 'potential layout animation'))
        for idx in range(m.start(), i):
            if out[idx] != '\n':
                out[idx] = ' '
    return ''.join(out), warnings

def main(root):
    base = Path(root)
    if not base.exists():
        print(f'ERROR: Path not found: {root}')
        return 1
    paths = [base] if base.is_file() else sorted(base.rglob('*.css'))
    if not paths:
        print('NOT RUN: no CSS files found')
        return 2

    count = 0
    for f in paths:
        try:
            src = f.read_text(encoding='utf-8', errors='replace')
        except Exception as exc:
            print(f'ERROR: Cannot read {f}: {exc}')
            return 1

        cleaned = strip_comments(src)
        masked, warnings = mask_keyframes(cleaned, src)

        # Detect universal wildcard selector with non-auto will-change
        for m in re.finditer(r'([^{};]+)\{([^{}]+)\}', masked):
            sel = m.group(1).strip()
            body = m.group(2)
            selectors = [s.strip() for s in sel.split(',')]
            if any(re.fullmatch(r'\*(?:::before|::after)?', s) for s in selectors):
                wc = re.search(r'\bwill-change\s*:\s*([^;]+)', body)
                if wc and wc.group(1).strip() not in ('auto', 'none'):
                    pos = m.start(2) + wc.start()
                    line = src.count('\n', 0, pos) + 1
                    warnings.append((line, 'wildcard will-change'))

        # Pattern heuristics
        for name, pattern in PATTERNS.items():
            target = masked if name == 'potential layout animation' else cleaned
            for match in re.finditer(pattern, target, re.I):
                line = src.count('\n', 0, match.start()) + 1
                warnings.append((line, name))

        for line, name in sorted(set(warnings)):
            print(f'WARN {f}:{line}: {name}')
            count += 1

    print(f'CSS heuristic audit complete: {len(paths)} files, {count} warnings')
    return 0

if __name__ == '__main__':
    if len(sys.argv) != 2: sys.exit('Usage: css_motion_audit.py path/to/styles')
    sys.exit(main(sys.argv[1]))
