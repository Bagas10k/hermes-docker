"""Fail-closed admission checks for externally measured optimization reports."""
import copy
import json
import math
import sys
import unittest


def assess(r):
    reasons = []
    def number(key, lower=None):
        value = r[key]
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError(key + ': finite number required')
        if lower is not None and value < lower:
            raise ValueError(key + ': below minimum')
        return value
    try:
        for key in ('prefix_sha256', 'candidate_prefix_sha256'):
            v = r[key]
            if not isinstance(v, str) or len(v) != 64 or any(c not in '0123456789abcdef' for c in v):
                raise ValueError('invalid prefix digest')
        if r['prefix_sha256'] != r['candidate_prefix_sha256']:
            reasons.append('prefix_drift')
        splits = []
        for key in ('train_ids', 'validation_ids', 'test_ids'):
            v = r[key]
            if not isinstance(v, list) or not v or any(not isinstance(x, str) or not x for x in v):
                raise ValueError('nonempty string ID lists required')
            if len(set(v)) != len(v):
                raise ValueError('duplicate IDs')
            splits.append(set(v))
        if any(splits[i] & splits[j] for i, j in ((0, 1), (0, 2), (1, 2))):
            reasons.append('split_overlap')
        for key in ('grammar_backend_verified', 'semantic_contract_verified', 'protected_slices_pass', 'finalist_frozen_before_test'):
            if r[key] is not True:
                reasons.append(key)
        for key in ('invariant_failures', 'timeouts'):
            if type(r[key]) is not int or r[key] < 0:
                raise ValueError('nonnegative integer counts required')
            if r[key] != 0:
                reasons.append(key)
        lo = number('paired_gain_lower')
        if not -1 <= lo <= 1:
            raise ValueError('gain bound outside normalized metric range')
        margin = number('minimum_gain', 0)
        if margin > 1:
            raise ValueError('margin outside normalized metric range')
        if lo <= margin:
            reasons.append('insufficient_evidence')
        for value, limit in (('p95_ms', 'p95_limit_ms'), ('peak_rss_mb', 'rss_limit_mb'), ('metric_calls', 'metric_call_limit'), ('total_tokens', 'token_limit')):
            if number(value, 0) > number(limit, 0):
                reasons.append(value + '_budget')
    except (KeyError, TypeError, ValueError) as e:
        reasons.append('invalid_report:' + str(e))
    return {'admitted_for_review': not reasons, 'reasons': reasons, 'deployment_authorized': False}


def fixture():
    # Synthetic contract fixture, NOT model results or production measurements.
    return dict(prefix_sha256='a'*64, candidate_prefix_sha256='a'*64,
                train_ids=['train'], validation_ids=['val'], test_ids=['test'],
                grammar_backend_verified=True, semantic_contract_verified=True,
                protected_slices_pass=True, finalist_frozen_before_test=True,
                invariant_failures=0, timeouts=0, paired_gain_lower=.04,
                minimum_gain=.01, p95_ms=10, p95_limit_ms=20, peak_rss_mb=10,
                rss_limit_mb=20, metric_calls=10, metric_call_limit=20,
                total_tokens=100, token_limit=200)


class GateTests(unittest.TestCase):
    def test_valid_is_not_deployment_authority(self):
        self.assertEqual(assess(fixture()), dict(admitted_for_review=True, reasons=[], deployment_authorized=False))

    def test_reject_each_violation(self):
        changes = dict(candidate_prefix_sha256='b'*64, test_ids=['train'],
                       grammar_backend_verified=False, semantic_contract_verified=False,
                       protected_slices_pass=False, finalist_frozen_before_test=False,
                       invariant_failures=1, timeouts=1, paired_gain_lower=.01,
                       p95_ms=21, peak_rss_mb=21, metric_calls=21, total_tokens=201,
                       train_ids=['x', 'x'])
        for key, value in changes.items():
            with self.subTest(key=key):
                r = fixture(); r[key] = value
                self.assertFalse(assess(r)['admitted_for_review'])

    def test_missing_every_field(self):
        for key in fixture():
            with self.subTest(key=key):
                r = fixture(); del r[key]
                self.assertFalse(assess(r)['admitted_for_review'])

    def test_nonfinite_and_wrong_types(self):
        for value in (float('nan'), float('inf'), -1, True, '1', None):
            r = fixture(); r['p95_ms'] = value
            self.assertFalse(assess(r)['admitted_for_review'])
        for value in ('true', 1, None):
            r = fixture(); r['grammar_backend_verified'] = value
            self.assertFalse(assess(r)['admitted_for_review'])


if __name__ == '__main__':
    if sys.argv[1:] == ['--self-test']:
        unittest.main(argv=[sys.argv[0]], verbosity=2)
    else:
        try:
            if len(sys.argv) != 2:
                raise ValueError('usage: promotion_gate.py report.json | --self-test')
            with open(sys.argv[1], encoding='utf-8') as f:
                report = json.load(f)
            if not isinstance(report, dict):
                raise ValueError('JSON object required')
            result = assess(report)
            print(json.dumps(result, allow_nan=False))
            sys.exit(0 if result['admitted_for_review'] else 1)
        except (OSError, ValueError) as e:
            print(str(e), file=sys.stderr)
            sys.exit(2)
