import unittest
from spanning_grid import SpanIndex
from dom_adapter import snapshot, render_html

class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.index=SpanIndex(20,20)
        self.index.add(7,1,1,4,4)
    def tearDown(self):
        self.index.db.close()
    def test_offscreen_owner_and_geometry(self):
        s=snapshot(self.index,(2,2,6,6))
        m=next(c for c in s['cells'] if c['id']=='merge-7')
        self.assertEqual((m['left'],m['top'],m['width'],m['height']),(-96,-32,288,96))
        self.assertEqual(len(s['cells']),13)
    def test_coverage_partition(self):
        s=snapshot(self.index,(2,2,6,6))
        self.assertEqual(len(s['owners']),16)
        self.assertEqual(sum(x=='merge-7' for x in s['owners'].values()),4)
        self.assertEqual(set(s['owners'].values()),{c['id'] for c in s['cells']})
    def test_empty(self):
        self.assertEqual(snapshot(self.index,(2,2,2,6))['cells'],[])
    def test_budget_and_invalid(self):
        for kwargs in ({'budget':3},{'row_px':False},{'col_px':0}):
            with self.assertRaises(ValueError):snapshot(self.index,(2,2,6,6),**kwargs)
    def test_edge_touch(self):
        s=snapshot(self.index,(4,4,6,6))
        self.assertEqual(len(s['cells']),4)
        self.assertNotIn('merge-7',s['owners'].values())
    def test_semantics_template(self):
        html=render_html(snapshot(self.index,(2,2,6,6)))
        for required in ['role="grid"','aria-rowcount','aria-colspan','ArrowRight','preventScroll']:
            self.assertIn(required,html)

if __name__=='__main__':unittest.main()
