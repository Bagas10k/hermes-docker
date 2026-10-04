import unittest
from spanning_grid import SpanIndex

class SpanTests(unittest.TestCase):
    def test_anchor_outside_window_is_retained(self):
        with SpanIndex(100, 100) as index:
            index.add(7, 2, 3, 10, 12)
            self.assertEqual(index.query(5, 6, 8, 9), [
                {'id': 7, 'anchor': [2, 3], 'bounds': [2, 3, 10, 12],
                 'clip': [5, 6, 8, 9]}])

    def test_invalid_contract(self):
        for rows, cols in [(0,2), (True,2), (2**31,2)]:
            with self.assertRaises(ValueError):
                SpanIndex(rows, cols)
        with SpanIndex(100,100) as index:
            for box in [(0,0,0,2), (-1,0,2,2), (0,0,101,2), (0.5,0,2,2), (False,0,2,2)]:
                with self.assertRaises(ValueError):
                    index.add(1,*box)
            for ident in [True, 1.5, -1, 2**63]:
                with self.assertRaises(ValueError):
                    index.add(ident,0,0,2,2)
            with self.assertRaises(ValueError):
                index.query(2,0,1,2)

    def test_overlaps_and_duplicate_ids_are_atomic(self):
        with SpanIndex(100,100) as index:
            index.add(1,0,0,4,4)
            for args in [(2,3,3,5,5), (1,10,10,12,12)]:
                with self.assertRaises(ValueError):
                    index.add(*args)
            self.assertEqual(len(index.query(0,0,100,100)),1)

    def test_half_open_and_empty(self):
        with SpanIndex(20,20) as index:
            index.add(1,0,0,4,4)
            index.add(2,4,0,8,4)
            self.assertEqual([x['id'] for x in index.query(4,0,8,4)],[2])
            self.assertEqual(index.query(4,0,4,4),[])
            self.assertEqual(index.query(0,4,8,8),[])

    def test_integer_precision(self):
        with SpanIndex(2**30,10) as index:
            a = 2**25+1
            index.add(1,a,0,a+1,1)
            self.assertEqual(index.query(a+1,0,a+2,1),[])
            self.assertEqual(index.query(a,0,a+1,1)[0]['bounds'],[a,0,a+1,1])

    def test_seeded_differential(self):
        import random
        rng=random.Random(206)
        with SpanIndex(100,100) as index:
            boxes=[]
            for i in range(100):
                r,c=divmod(i,10)
                box=(r*10,c*10,r*10+7,c*10+8)
                boxes.append(box)
                index.add(i,*box)
            for _ in range(500):
                r0,r1=sorted(rng.sample(range(101),2))
                c0,c1=sorted(rng.sample(range(101),2))
                expected=[i for i,(a,b,c,d) in enumerate(boxes) if a<r1 and c>r0 and b<c1 and d>c0]
                self.assertEqual([x['id'] for x in index.query(r0,c0,r1,c1)],expected)

if __name__ == '__main__':
    unittest.main()
