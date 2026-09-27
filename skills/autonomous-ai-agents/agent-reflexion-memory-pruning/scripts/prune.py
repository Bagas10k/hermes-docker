"""Read-only, exact-key memory retrieval planner. No model calls or mutations."""
import argparse
import json
import sys
from collections import defaultdict

FIELDS = {'id', 'scope', 'key', 'value', 'source', 'protected', 'stale', 'verified'}

def plan(records, scope, budget):
    if type(budget) is not int or budget < 0:
        raise ValueError('budget must be a nonnegative integer')
    if not isinstance(scope, str) or not scope:
        raise ValueError('scope required')
    if not isinstance(records, list):
        raise ValueError('records must be a list')
    seen = set()
    for r in records:
        if not isinstance(r, dict) or set(r) != FIELDS:
            raise ValueError('exact record schema required')
        for k in ('id', 'scope', 'key', 'value', 'source'):
            if not isinstance(r[k], str) or not r[k].strip():
                raise ValueError('nonempty string required: ' + k)
        for k in ('protected', 'stale', 'verified'):
            if type(r[k]) is not bool:
                raise ValueError('boolean required: ' + k)
        if r['id'] in seen:
            raise ValueError('duplicate id')
        seen.add(r['id'])
        if r['protected'] and (r['stale'] or not r['verified']):
            raise ValueError('protected record cannot be stale or unverified')
    reasons, groups = {}, defaultdict(list)
    for r in records:
        if r['scope'] != scope:
            reasons[r['id']] = 'out_of_scope'
        elif r['stale']:
            reasons[r['id']] = 'stale'
        elif not r['verified']:
            reasons[r['id']] = 'unverified'
        else:
            groups[r['key']].append(r)
    candidates = []
    for key in sorted(groups):
        group = groups[key]
        if len({r['value'] for r in group}) > 1:
            if any(r['protected'] for r in group):
                raise ValueError('conflict with protected record requires review')
            for r in group:
                reasons[r['id']] = 'conflict'
            continue
        ordered = sorted(group, key=lambda r: (not r['protected'], r['id']))
        candidates.append(ordered[0])
        for r in ordered[1:]:
            if r['protected']:
                candidates.append(r)
            else:
                reasons[r['id']] = 'duplicate:' + ordered[0]['id']
    def render(r):
        return json.dumps({k:r[k] for k in ('id','key','value','source')}, ensure_ascii=False, sort_keys=True) + '\n'
    candidates.sort(key=lambda r: (not r['protected'], r['id']))
    required = sum(len(render(r).encode('utf-8')) for r in candidates if r['protected'])
    if required > budget:
        raise ValueError('protected memory exceeds budget')
    selected, used, context = [], 0, ''
    for r in candidates:
        line = render(r)
        cost = len(line.encode('utf-8'))
        if used + cost <= budget:
            selected.append(r['id'])
            used += cost
            context += line
            reasons[r['id']] = 'selected'
        else:
            reasons[r['id']] = 'budget'
    return {'selected': selected, 'bytes': used, 'context': context,
            'decisions': dict(sorted(reasons.items())), 'mutated': False}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input')
    parser.add_argument('--scope', required=True)
    parser.add_argument('--budget', type=int, required=True)
    args = parser.parse_args()
    try:
        with open(args.input, encoding='utf-8') as f:
            result = plan(json.load(f), args.scope, args.budget)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    except (OSError, ValueError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0

if __name__ == '__main__':
    sys.exit(main())
