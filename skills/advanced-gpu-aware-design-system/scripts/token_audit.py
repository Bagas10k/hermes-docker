#!/usr/bin/env python3
"""Validate token JSON and report unresolved/cyclic token references.

Scope limitation: Only supports nested plain JSON objects and whole-value aliases
like '{primitive.color.ink}'. Composite interpolation (e.g. '1px solid {color}')
and complex DTCG specifications are intentionally not covered.
"""
import json, re, sys
from pathlib import Path

REF = re.compile(r'^\{([^{}]+)\}$')

def audit(path):
    p = Path(path)
    if not p.exists() or not p.is_file():
        print(f'ERROR: File not found: {path}')
        return 1
    try:
        raw = p.read_text(encoding='utf-8')
    except Exception as exc:
        print(f'ERROR: Cannot read file {path}: {exc}')
        return 1
    try:
        data = json.loads(raw)
    except Exception as exc:
        print(f'ERROR: Invalid JSON in {path}: {exc}')
        return 1
    if not isinstance(data, dict):
        print(f'ERROR: Root of {path} must be a JSON object (dict), got {type(data).__name__}')
        return 1

    errors = []
    def resolve(key, stack=()):
        if key in stack:
            errors.append('Cycle: ' + ' -> '.join((*stack, key))); return
        cur = data
        for part in key.split('.'):
            if not isinstance(cur, dict) or part not in cur:
                errors.append('Missing reference: ' + key); return
            cur = cur[part]
        if isinstance(cur, str) and (m := REF.fullmatch(cur)):
            resolve(m.group(1), (*stack, key))

    def walk(value):
        if isinstance(value, dict):
            for v in value.values(): walk(v)
        elif isinstance(value, list):
            for v in value: walk(v)
        elif isinstance(value, str) and (m := REF.fullmatch(value)):
            resolve(m.group(1))

    walk(data)
    for e in sorted(set(errors)): print('ERROR:', e)
    print('Token audit:', 'FAIL' if errors else 'PASS')
    return 1 if errors else 0

if __name__ == '__main__':
    if len(sys.argv) != 2: sys.exit('Usage: token_audit.py tokens.json')
    sys.exit(audit(sys.argv[1]))
