"""Finite per-channel FIFO exploration; NOT an MPST proof checker."""
import argparse
from collections import deque
import json
import sys


def check(model, bound=2, max_states=100000):
    if type(bound) is not int or bound < 1 or type(max_states) is not int or max_states < 1:
        raise ValueError('positive integer limits required')
    if not isinstance(model, dict) or not model:
        raise ValueError('nonempty role map required')
    roles = tuple(sorted(model))
    channels = tuple((a, b) for a in roles for b in roles if a != b)
    ci = {c: i for i, c in enumerate(channels)}
    for role, spec in model.items():
        if not isinstance(spec['initial'], str) or not isinstance(spec['final'], list) or not isinstance(spec['edges'], list):
            raise ValueError('invalid role schema')
        if not all(isinstance(x, str) for x in spec['final']):
            raise ValueError('final states must be strings')
        for edge in spec['edges']:
            if not isinstance(edge, list) or len(edge) != 5 or not all(isinstance(x, str) for x in edge):
                raise ValueError('edge must contain five strings')
            src, op, peer, label, dst = edge
            if op not in ('send', 'recv') or peer not in roles or peer == role or src in spec['final']:
                raise ValueError('invalid transition')
    start = (tuple(model[r]['initial'] for r in roles), tuple(() for _ in channels))
    todo = deque([start])
    parent = {start: None}
    terminal = 0
    while todo:
        current = todo.popleft()
        states, queues = current
        if all(states[i] in model[r]['final'] for i, r in enumerate(roles)) and not any(queues):
            terminal += 1
            continue
        successors = []
        for i, role in enumerate(roles):
            for src, op, peer, label, dst in model[role]['edges']:
                if src != states[i]:
                    continue
                channel = (role, peer) if op == 'send' else (peer, role)
                j = ci[channel]
                q = queues[j]
                if op == 'send':
                    if len(q) >= bound:
                        continue
                    nq = q + (label,)
                else:
                    if not q or q[0] != label:
                        continue
                    nq = q[1:]
                ss, qq = list(states), list(queues)
                ss[i], qq[j] = dst, nq
                successors.append(((tuple(ss), tuple(qq)), [role, op, peer, label]))
        if not successors:
            path, node = [], current
            while parent[node] is not None:
                prev, action = parent[node]
                path.append(action)
                node = prev
            return {'status': 'stuck', 'states': len(parent), 'bound': bound, 'trace': list(reversed(path)), 'local_states': dict(zip(roles, states)), 'queues': {f'{a}->{b}': list(queues[j]) for j, (a, b) in enumerate(channels) if queues[j]}}
        for nxt, action in successors:
            if nxt not in parent:
                if len(parent) >= max_states:
                    return {'status': 'inconclusive', 'states': len(parent), 'bound': bound}
                parent[nxt] = (current, action)
                todo.append(nxt)
    return {'status': 'no_stuck_state_within_bound', 'states': len(parent), 'bound': bound, 'terminal_states': terminal, 'liveness_checked': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('model')
    parser.add_argument('--bound', type=int, default=2)
    parser.add_argument('--max-states', type=int, default=100000)
    args = parser.parse_args()
    try:
        with open(args.model, encoding='utf-8') as stream:
            result = check(json.load(stream), args.bound, args.max_states)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(json.dumps({'status': 'invalid', 'error': str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return {'stuck': 1, 'inconclusive': 2}.get(result['status'], 0)


if __name__ == '__main__':
    sys.exit(main())
