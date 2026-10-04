import unittest
from spanning_grid import SpanIndex
from window_focus import replacement, reconcile

class WindowFocusTests(unittest.TestCase):
    def setUp(self):
        self.index=self.enterContext(SpanIndex(20,20))
        self.index.add(7,1,1,4,4)
    def test_overlap(self):
        d=replacement(self.index,(3,3,7,7),[3,3])
        self.assertEqual(d['cursor'],[3,3])
        self.assertEqual(d['owners']['3,3'],'merge-7')
    def test_clamp(self):
        self.assertEqual(replacement(self.index,(8,8,12,12),[3,3])['cursor'],[8,8])
        self.assertEqual(replacement(self.index,(0,0,2,2),[9,9])['cursor'],[1,1])
    def test_empty(self):
        d=replacement(self.index,(2,2,2,4),[3,3])
        self.assertIsNone(d['cursor'])
        self.assertEqual(d['cells'],[])
    def test_initial(self):
        self.assertEqual(replacement(self.index,(2,2,6,6))['cursor'],[2,2])
    def test_invalid_cursor(self):
        for cursor in ([True,1],[1.5,1],[1]):
            with self.assertRaises(ValueError):
                replacement(self.index,(0,0,2,2),cursor)
    def test_exhaustive_bounds(self):
        d={'window':[2,3,6,8]}
        for r in range(-2,12):
            for c in range(-2,12):
                point=reconcile(d,[r,c])
                self.assertTrue(2<=point[0]<6 and 3<=point[1]<8)
                if 2<=r<6 and 3<=c<8:self.assertEqual(point,[r,c])

if __name__=='__main__':unittest.main()
