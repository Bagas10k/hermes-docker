"""Bounded, data-only pre-execution admission. Never executes plan contents."""
import argparse
from dataclasses import dataclass
from graphlib import TopologicalSorter, CycleError
import json
import math
from pathlib import Path
import re


class PlanError(ValueError):
    pass


@dataclass(frozen=True)
class Limits:
    max_bytes: int = 262144
    max_nodes: int = 128
    max_depth: int = 8
    max_branching: int = 8
    max_edges: int = 512
    max_budget: int = 100000
    max_critical_path: int = 10000


def need(ok, message):
    if not ok:
        raise PlanError(message)


def fields(value, required, label):
    need(type(value) is dict and set(value) == set(required.split()), label + ': fields')


def integer(value, label):
    need(type(value) is int and 0 <= value <= 10**12, label + ': nonnegative bounded integer required')


def text(value, label):
    need(type(value) is str and 0 < len(value) <= 256 and bool(value.strip()), label + ': text required')


def ident(value):
    need(type(value) is str and re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,63}', value) is not None, 'invalid id')


def validate(plan, limits=Limits()):
    """Accept a plain JSON-decoded dict; return declared estimates only."""
    for key, value in vars(limits).items():
        integer(value, key)
    fields(plan, 'root nodes dependencies budget_unit duration_unit', 'plan')
    ident(plan['root'])
    text(plan['budget_unit'], 'budget_unit')
    text(plan['duration_unit'], 'duration_unit')
    nodes = plan['nodes']
    need(type(nodes) is list and 1 <= len(nodes) <= limits.max_nodes, 'node limit')
    registry = {}
    total = 0
    for node in nodes:
        fields(node, 'id children cost duration acceptance', 'node')
        ident(node['id'])
        need(node['id'] not in registry, 'duplicate id')
        children = node['children']
        need(type(children) is list and len(children) <= limits.max_branching, 'branching limit')
        for child in children:
            ident(child)
        need(len(set(children)) == len(children), 'duplicate child')
        integer(node['cost'], 'cost')
        integer(node['duration'], 'duration')
        total += node['cost']
        need(total <= limits.max_budget, 'budget limit')
        if children:
            need(node['acceptance'] is None and node['duration'] == 0, 'internal contract')
        else:
            acceptance = node['acceptance']
            fields(acceptance, 'metric op threshold unit evidence', 'acceptance')
            for key in ('metric', 'unit', 'evidence'):
                text(acceptance[key], key)
            need(type(acceptance['op']) is str and acceptance['op'] in ('==', '<=', '>='), 'acceptance operator')
            threshold = acceptance['threshold']
            need(type(threshold) in (int, float) and abs(threshold) <= 10**12 and math.isfinite(threshold), 'acceptance threshold')
        registry[node['id']] = node
    need(plan['root'] in registry, 'unknown root')
    parents = {key: 0 for key in registry}
    for node in nodes:
        for child in node['children']:
            need(child in registry, 'unknown child')
            parents[child] += 1
    need(parents[plan['root']] == 0, 'root has parent')
    need(all(count == 1 for key, count in parents.items() if key != plan['root']), 'parent ownership')
    seen = set()
    stack = [(plan['root'], 0)]
    depth = 0
    while stack:
        key, level = stack.pop()
        need(key not in seen, 'tree cycle')
        need(level <= limits.max_depth, 'depth limit')
        seen.add(key)
        depth = max(depth, level)
        stack.extend((child, level + 1) for child in registry[key]['children'])
    need(len(seen) == len(registry), 'unreachable nodes or tree cycle')
    leaves = {key for key, node in registry.items() if not node['children']}
    records = plan['dependencies']
    need(type(records) is list and len(records) == len(leaves), 'dependency coverage')
    graph = {}
    edges = 0
    for record in records:
        fields(record, 'id requires', 'dependency')
        ident(record['id'])
        key = record['id']
        need(key in leaves and key not in graph, 'unknown/nonleaf/duplicate dependency target')
        prerequisites = record['requires']
        need(type(prerequisites) is list, 'requires list')
        edges += len(prerequisites)
        need(edges <= limits.max_edges, 'edge limit')
        for predecessor in prerequisites:
            ident(predecessor)
            need(predecessor in leaves, 'unknown/nonleaf prerequisite')
        need(len(set(prerequisites)) == len(prerequisites), 'duplicate prerequisite')
        graph[key] = prerequisites
    try:
        order = list(TopologicalSorter(graph).static_order())
    except CycleError as error:
        raise PlanError('dependency cycle') from error
    finish = {}
    previous = {}
    for key in order:
        predecessor = max(graph[key], key=lambda item: (finish[item], item), default=None)
        previous[key] = predecessor
        finish[key] = registry[key]['duration'] + (finish[predecessor] if predecessor else 0)
    last = max(order, key=lambda item: (finish[item], item))
    critical = finish[last]
    need(critical <= limits.max_critical_path, 'critical path limit')
    path = []
    while last is not None:
        path.append(last)
        last = previous[last]
    return {'admitted': True, 'nodes': len(nodes), 'leaves': len(leaves), 'depth': depth,
            'edges': edges, 'total_budget': total, 'budget_unit': plan['budget_unit'],
            'critical_path': critical, 'duration_unit': plan['duration_unit'],
            'critical_path_ids': path[::-1], 'topological_order': order,
            'evidence_scope': 'offline structural validation; estimates, not execution'}


def reject_constant(value):
    raise PlanError('nonfinite JSON constant: ' + value)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def load_plan(path, limits=Limits()):
    with Path(path).open('rb') as stream:
        data = stream.read(limits.max_bytes + 1)
    need(len(data) <= limits.max_bytes, 'byte limit')
    try:
        return json.loads(data, object_pairs_hook=unique_object, parse_constant=reject_constant)
    except (ValueError, UnicodeError, RecursionError) as error:
        raise PlanError('invalid JSON: ' + str(error)) from error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan')
    args = parser.parse_args()
    try:
        result = validate(load_plan(args.plan))
    except (PlanError, OSError) as error:
        print(json.dumps({'admitted': False, 'error': str(error)}))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
