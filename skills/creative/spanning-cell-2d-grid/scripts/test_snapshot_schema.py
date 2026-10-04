import copy
import unittest
from spanning_grid import SpanIndex
from dom_adapter import snapshot
from snapshot_schema import validate_snapshot


def cases():
    with SpanIndex(20,20) as index:
        index.add(7,1,1,4,4)
        good=snapshot(index,(2,2,6,6))
    bad=[]
    def add(label, fn):
        d=copy.deepcopy(good);fn(d);bad.append((label,d))
    add('bool rows',lambda d:d.update(rows=True))
    add('unknown field',lambda d:d.update(extra=1))
    add('window reversed',lambda d:d.update(window=[6,2,2,6]))
    add('area cap',lambda d:d.update(rows=100,cols=100,window=[0,0,100,100]))
    add('missing owner',lambda d:d['owners'].pop('2,2'))
    add('wrong owner',lambda d:d['owners'].update({'2,2':'missing'}))
    add('duplicate id',lambda d:d['cells'][1].update(id=d['cells'][0]['id']))
    add('invalid id',lambda d:d['cells'][0].update(id='<script>'))
    add('negative span',lambda d:d['cells'][0].update(rowspan=-1))
    add('geometry mismatch',lambda d:d['cells'][0].update(left=0))
    add('out of bounds',lambda d:d['cells'][0].update(rowspan=100))
    add('bad dimension',lambda d:d.update(width=-1))
    add('overlap',lambda d:d['cells'].__setitem__(1,dict(d['cells'][0],id='merge-8')))
    add('unknown cell field',lambda d:d['cells'][0].update(extra=1))
    return good,bad

class SchemaTests(unittest.TestCase):
    def test_valid_and_immutable(self):
        good,_=cases();before=copy.deepcopy(good)
        self.assertIs(validate_snapshot(good),good);self.assertEqual(before,good)
    def test_malformed_matrix(self):
        _,bad=cases()
        for label,d in bad:
            with self.subTest(label=label),self.assertRaises(ValueError):validate_snapshot(d)
    def test_nonfinite_and_wrong_types(self):
        for val in [None,True,float('inf'),float('nan'),'32']:
            d,_=cases();d['cells'][0]['width']=val
            with self.subTest(value=val),self.assertRaises(ValueError):validate_snapshot(d)
    def test_empty(self):
        with SpanIndex(20,20) as i:
            for w in [(0,0,0,4),(0,0,4,0),(0,0,0,0)]:validate_snapshot(snapshot(i,w))
    def test_budget_edge(self):
        with SpanIndex(64,64) as i:validate_snapshot(snapshot(i,(0,0,64,64)))

if __name__=='__main__':unittest.main()
