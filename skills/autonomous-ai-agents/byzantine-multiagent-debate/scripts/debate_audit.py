"""Finite audit fixtures, NOT a distributed consensus implementation."""
import itertools
import math
import unittest


def bounds(weights, bad, quorum):
    if not weights or any(type(w) is not int or w <= 0 for w in weights.values()):
        raise ValueError('positive integer weights required')
    if type(bad) is not int or type(quorum) is not int or bad < 0 or quorum <= 0:
        raise ValueError('invalid fault/quorum bounds')
    total = sum(weights.values())
    return 2 * quorum - total > bad and quorum <= total - bad


def certificate(weights, bad, quorum, expected, receipts, verified_claims):
    """IDs are assumed authenticated externally; no crypto or durable locks here.

    expected is (epoch, task, claim_digest, evidence_digest).
    verified_claims is trusted verifier state, never agent-supplied metadata.
    """
    if not bounds(weights, bad, quorum):
        return 'ABSTAIN'
    seen = set()
    for signer, binding in receipts:
        if signer not in weights or signer in seen or binding != expected:
            return 'ABSTAIN'
        seen.add(signer)
    if expected not in verified_claims:
        return 'ABSTAIN'
    return 'CERTIFICATE' if sum(weights[s] for s in seen) >= quorum else 'ABSTAIN'


def calibration(confidences, labels, bins=10):
    if type(bins) is not int or bins < 1 or not confidences or len(confidences) != len(labels):
        raise ValueError('invalid sizes')
    if any(not math.isfinite(p) or not 0 <= p <= 1 for p in confidences):
        raise ValueError('confidence outside [0,1]')
    if any(type(y) is not int or y not in (0, 1) for y in labels):
        raise ValueError('binary labels required')
    groups = [[] for _ in range(bins)]
    for p, y in zip(confidences, labels):
        groups[min(int(p * bins), bins - 1)].append((p, y))
    n = len(labels)
    ece = sum(abs(sum(p-y for p,y in g)) / n for g in groups if g)
    brier = sum((p-y)**2 for p,y in zip(confidences, labels)) / n
    return ece, brier


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.w = dict.fromkeys('abcd', 1)
        self.key = ('epoch1', 'task1', 'claim1', 'evidence1')
        self.r = [(s, self.key) for s in 'abc']

    def check_cert(self, receipts, verified=True):
        return certificate(self.w, 1, 3, self.key, receipts, {self.key} if verified else set())

    def test_safe_intersections(self):
        for n, f in [(4,1), (7,2), (10,3)]:
            q = 2*f+1
            self.assertTrue(bounds(dict.fromkeys(range(n),1),f,q))
            sets = [set(c) for c in itertools.combinations(range(n),q)]
            self.assertTrue(all(len(a & b)>f for a,b in itertools.product(sets,repeat=2)))

    def test_unsafe_counterexample(self):
        self.assertFalse(bounds(self.w,1,2))
        self.assertEqual(len(set('ab') & set('cd')),0)
        self.assertFalse(bounds(dict.fromkeys('abcde',1),1,3))

    def test_availability(self):
        self.assertFalse(bounds(self.w,1,4))

    def test_valid(self):
        self.assertEqual(self.check_cert(self.r),'CERTIFICATE')

    def test_duplicate(self):
        self.assertEqual(self.check_cert([self.r[0]]*3),'ABSTAIN')

    def test_sybil(self):
        self.assertEqual(self.check_cert(self.r+[('unknown',self.key)]),'ABSTAIN')

    def test_replay_and_equivocation(self):
        for i in range(4):
            k=list(self.key); k[i]='wrong'
            self.assertEqual(self.check_cert(self.r[:2]+[('c',tuple(k))]),'ABSTAIN')
        self.assertEqual(self.check_cert(self.r+[('a',('other',)*4)]),'ABSTAIN')

    def test_unsupported_unanimity(self):
        self.assertEqual(self.check_cert([(s,self.key) for s in self.w],False),'ABSTAIN')

    def test_insufficient(self):
        self.assertEqual(self.check_cert(self.r[:2]),'ABSTAIN')

    def test_weighted(self):
        self.assertTrue(bounds({'a':3,'b':3,'c':3,'d':1},1,6))
        self.assertFalse(bounds({'a':3,'b':3,'c':3,'d':1},4,6))

    def test_calibration(self):
        self.assertEqual(calibration([0,1],[0,1]),(0,0))
        self.assertEqual(calibration([1,1],[0,0]),(1,1))
        self.assertEqual(calibration([.5,.5],[0,1]),(0,.25))

    def test_invalid_inputs(self):
        for probs,ys in [([],[]),([float('nan')],[1]),([1.1],[1]),([.2],[2]),([.2],[])]:
            with self.assertRaises(ValueError): calibration(probs,ys)
        with self.assertRaises(ValueError): bounds({'a':-1},0,1)
        with self.assertRaises(ValueError): bounds(self.w,-1,3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
