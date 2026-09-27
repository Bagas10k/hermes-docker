#!/usr/bin/env python3
import argparse, json, os, re, sys
from pathlib import Path

TEXT_EXTS = {'.js','.jsx','.ts','.tsx','.css','.scss','.html','.md','.json','.vue','.svelte','.astro'}
SKIP_DIRS = {'node_modules','dist','dist-public','build','.git','.next','coverage','artifacts'}

PATTERNS = [
    ('emoji_or_extended_pictographic', re.compile(r'[\U0001F000-\U0001FAFF\u2600-\u27BF]')),
    ('device_simulator_language', re.compile(r'phone mockup|device mockup|bezel|dynamic island|viewport switcher|mobile simulator|desktop simulator|chassis', re.I)),
    ('horizontal_scroll_risk', re.compile(r'overflow-x\s*:\s*(scroll|auto)', re.I)),
    ('focus_outline_removed', re.compile(r'outline\s*:\s*none', re.I)),
    ('layout_animation_risk', re.compile(r'transition[^;]*(width|height|top|left|right|bottom|margin|padding)', re.I)),
    ('generic_slop_copy', re.compile(r'\b(premium|modern|beautiful|stunning|sleek)\b', re.I)),
]

def iter_files(root: Path):
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            p = Path(base) / f
            if p.suffix.lower() in TEXT_EXTS:
                yield p

def scan(root: Path):
    findings = []
    for p in iter_files(root):
        try:
            text = p.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            findings.append({'check':'read_error','file':str(p),'line':0,'text':str(e)})
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for check, rx in PATTERNS:
                if rx.search(line):
                    findings.append({'check':check,'file':str(p.relative_to(root)),'line':i,'text':line.strip()[:220]})
    return findings

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('project_dir')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    root = Path(args.project_dir).resolve()
    findings = scan(root)
    result = {'project_dir': str(root), 'finding_count': len(findings), 'findings': findings}
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Design QA findings: {len(findings)}")
        for f in findings:
            print(f"{f['check']} {f['file']}:{f['line']} {f['text']}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
