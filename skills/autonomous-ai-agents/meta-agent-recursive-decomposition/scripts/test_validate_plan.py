"""Synthetic offline invariants, not model-performance tests."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from validate_plan import validate, load_plan, PlanError, Limits


def leaf(key, duration=2):
    return {'id': key, 'children': [], 'cost': 3, 'duration': duration,
            'acceptance': {'metric': 'passed_checks', 'op': '>=', 'threshold': 1,
                           'unit': 'count', 'evidence': 'local-report'}}


def fixture():
    return {'root': 'root', 'budget_unit': 'tokens', 'duration_unit': 'seconds',
            'nodes': [{'id': 'root', 'children': ['a', 'b', 'c'], 'cost': 1,
                       'duration': 0, 'acceptance': None}, leaf('a', 2), leaf('b', 5), leaf('c', 3)],
            'dependencies': [{'id': 'a', 'requires': []}, {'id': 'b', 'requires': []},
                             {'id': 'c', 'requires': ['a', 'b']}]}


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.plan = fixture()

    def reject(self, message=None, **limits):
        with self.assertRaisesRegex(PlanError, message or '.'):
            validate(self.plan, Limits(**limits))

    def test_parallel_critical_path(self):
        result = validate(self.plan)
        self.assertEqual(result['critical_path'], 8)
        self.assertEqual(result['critical_path_ids'], ['b', 'c'])
        self.assertEqual(result['total_budget'], 10)
        self.assertEqual(result['depth'], 1)

    def test_single_leaf_zero_depth(self):
        self.plan['root'] = 'a'
        self.plan['nodes'] = [leaf('a')]
        self.plan['dependencies'] = [{'id': 'a', 'requires': []}]
        self.assertEqual(validate(self.plan, Limits(max_depth=0))['leaves'], 1)

    def test_exact_bounds(self):
        self.assertTrue(validate(self.plan, Limits(max_nodes=4, max_depth=1, max_branching=3,
                                                  max_edges=2, max_budget=10, max_critical_path=8))['admitted'])

    def test_duplicate_ids(self):
        self.plan['nodes'][2]['id'] = 'a'
        self.reject('duplicate id')

    def test_unknown_child(self):
        self.plan['nodes'][0]['children'][0] = 'missing'
        self.reject('unknown child')

    def test_multiple_parents(self):
        self.plan['nodes'][1].update(children=['c'], acceptance=None, duration=0)
        self.reject('parent ownership')

    def test_unreachable(self):
        self.plan['nodes'].append(leaf('orphan'))
        self.reject('parent ownership')

    def test_disconnected_tree_cycle(self):
        for key, child in [('x', 'y'), ('y', 'x')]:
            self.plan['nodes'].append({'id': key, 'children': [child], 'cost': 0, 'duration': 0, 'acceptance': None})
        self.reject('unreachable')

    def test_root_cycle(self):
        self.plan['nodes'][1].update(children=['root'], acceptance=None, duration=0)
        self.reject('root has parent')

    def test_depth_limit(self):
        self.reject('depth limit', max_depth=0)

    def test_node_limit(self):
        self.reject('node limit', max_nodes=3)

    def test_branching_limit(self):
        self.reject('branching limit', max_branching=2)

    def test_budget_limit(self):
        self.reject('budget limit', max_budget=9)

    def test_critical_path_limit(self):
        self.reject('critical path limit', max_critical_path=7)

    def test_dependency_cycle(self):
        self.plan['dependencies'][0]['requires'] = ['c']
        self.reject('dependency cycle')

    def test_self_dependency(self):
        self.plan['dependencies'][0]['requires'] = ['a']
        self.reject('dependency cycle')

    def test_unknown_dependency(self):
        self.plan['dependencies'][0]['requires'] = ['missing']
        self.reject('unknown/nonleaf')

    def test_nonleaf_dependency(self):
        self.plan['dependencies'][0]['requires'] = ['root']
        self.reject('unknown/nonleaf')

    def test_dependency_coverage(self):
        self.plan['dependencies'].pop()
        self.reject('coverage')

    def test_duplicate_dependency_record(self):
        self.plan['dependencies'][1]['id'] = 'a'
        self.reject('duplicate dependency')

    def test_duplicate_prerequisite(self):
        self.plan['dependencies'][2]['requires'] = ['a', 'a']
        self.reject('duplicate prerequisite')

    def test_edge_limit(self):
        self.reject('edge limit', max_edges=1)

    def test_missing_acceptance(self):
        self.plan['nodes'][1]['acceptance'] = None
        self.reject('acceptance')

    def test_nonfinite_threshold(self):
        self.plan['nodes'][1]['acceptance']['threshold'] = float('nan')
        self.reject('threshold')

    def test_boolean_cost(self):
        self.plan['nodes'][1]['cost'] = True
        self.reject('integer')

    def test_negative_duration(self):
        self.plan['nodes'][1]['duration'] = -1
        self.reject('integer')

    def test_code_field_rejected(self):
        self.plan['nodes'][1]['command'] = 'this is not executable'
        self.reject('fields')

    def test_invalid_literal_id_not_normalized(self):
        self.plan['root'] = ' root '
        self.reject('invalid id')

    def test_does_not_mutate(self):
        original = copy.deepcopy(self.plan)
        validate(self.plan)
        self.assertEqual(original, self.plan)

    def test_json_loader(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'plan.json'
            path.write_text(json.dumps(self.plan))
            self.assertEqual(load_plan(path), self.plan)
            with self.assertRaisesRegex(PlanError, 'byte limit'):
                load_plan(path, Limits(max_bytes=4))
            for invalid in ['{"root":"a","root":"b"}', '{"x":NaN}', '[' * 2000, '{} trailing']:
                path.write_text(invalid)
                with self.assertRaises(PlanError):
                    load_plan(path)


if __name__ == '__main__':
    unittest.main()
