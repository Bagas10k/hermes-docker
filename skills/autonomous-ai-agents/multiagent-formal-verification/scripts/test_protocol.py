"""Predictions: reject circular waits, orphan queues and capacity deadlocks.
Accept handshake and informed branches; bounded exploration is not liveness.
"""
import copy
import json
import unittest
from check_protocol import check


def role(edges, final=None):
    return {'initial': '0', 'final': ['end'] if final is None else final, 'edges': edges}


def handshake():
    return {'A': role([['0','send','B','job','1'], ['1','recv','B','done','end']]), 'B': role([['0','recv','A','job','1'], ['1','send','A','done','end']])}


class ProtocolTests(unittest.TestCase):
    def test_handshake(self):
        for bound in (1, 2, 3):
            r = check(handshake(), bound)
            self.assertEqual(r['status'], 'no_stuck_state_within_bound')
            self.assertEqual(r['terminal_states'], 1)

    def test_circular_wait(self):
        m = {a: role([['0','recv',b,'go','end']]) for a,b in [('A','B'),('B','A')]}
        self.assertEqual(check(m)['trace'], [])
        self.assertEqual(check(m)['status'], 'stuck')

    def test_orphan(self):
        m = {'A':role([['0','send','B','job','end']]), 'B':role([], ['0'])}
        self.assertEqual(check(m)['queues'], {'A->B':['job']})

    def test_wrong_label(self):
        m = handshake()
        m['B']['edges'][0][3] = 'other'
        self.assertEqual(check(m)['status'], 'stuck')

    def test_capacity(self):
        m = {a:role([['0','send',b,'x','1'],['1','send',b,'x','2'],['2','recv',b,'x','3'],['3','recv',b,'x','end']]) for a,b in [('A','B'),('B','A')]}
        self.assertEqual(check(m,1)['status'], 'stuck')
        self.assertEqual(check(m,2)['status'], 'no_stuck_state_within_bound')

    def test_uninformed_choice(self):
        m = {'A':role([['0','send','B',v,'end'] for v in ('yes','no')]), 'B':role([]), 'C':role([['0','recv','B','yes','end']])}
        # Replace B explicitly: no branch silently skips its obligation to C.
        m['B'] = role([['0','recv','A','yes','1'],['1','send','C','yes','end'],['0','recv','A','no','end']])
        self.assertEqual(check(m)['status'], 'stuck')
        m['B']['edges'][-1][-1] = '2'
        m['B']['edges'].append(['2','send','C','no','end'])
        m['C']['edges'].append(['0','recv','B','no','end'])
        self.assertEqual(check(m)['status'], 'no_stuck_state_within_bound')

    def test_limit(self):
        self.assertEqual(check(handshake(),max_states=1)['status'], 'inconclusive')

    def test_no_liveness_claim(self):
        m = {a:role([['0','send',b,'x','1'],['1','recv',b,'x','0']]) for a,b in [('A','B'),('B','A')]}
        r = check(m)
        self.assertEqual(r['terminal_states'], 0)
        self.assertFalse(r['liveness_checked'])

    def test_invalid(self):
        for value in (0, -1, True):
            with self.assertRaises(ValueError): check(handshake(),value)
        m = copy.deepcopy(handshake())
        m['A']['edges'][0][2] = 'unknown'
        with self.assertRaises(ValueError): check(m)


if __name__ == '__main__':
    unittest.main(verbosity=2)
