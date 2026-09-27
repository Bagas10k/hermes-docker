import json
import time
import unittest
import numpy as np
from delta import Detector

class Tests(unittest.TestCase):
    def setUp(self):
        self.a = np.zeros((65, 65, 3), dtype=np.uint8)
        self.d = Detector()
        self.d.observe(self.a, 0, 0, 0)
    def test_identical(self):
        self.assertEqual(self.d.observe(self.a,1,1,1)['state'],'unchanged')
    def test_single_pixel_edge(self):
        self.a[64,64,0] = 255
        self.assertEqual(self.d.observe(self.a,1,1,1)['regions'],[(64,64,65,65)])
    def test_signed_difference(self):
        self.a[:] = 255
        self.d.observe(self.a,1,1,1)
        self.a[:] = 0
        self.assertEqual(self.d.observe(self.a,2,2,2)['state'],'changed')
    def test_stale_preserves_baseline(self):
        self.a[:] = 255
        for seq,cap,now in [(1,0,101),(0,1,1),(2,2,1)]:
            self.assertEqual(self.d.observe(self.a,seq,cap,now)['state'],'stale')
            self.assertEqual(self.d.seq,0)
            self.assertFalse(self.d.prev.any())
    def test_shape_reset(self):
        self.assertEqual(self.d.observe(self.a[:20],1,1,1)['state'],'baseline')
    def test_copy_ownership(self):
        self.a[:] = 255
        self.assertFalse(self.d.prev.any())
    def test_threshold(self):
        self.a[:] = 12
        self.assertEqual(self.d.observe(self.a,1,1,1)['state'],'unchanged')
    def test_invalid(self):
        for a in [np.zeros((0,2,3),dtype=np.uint8), self.a.astype(float), self.a[:,:,0]]:
            with self.assertRaises(ValueError): self.d.observe(a,1,1,1)
        with self.assertRaises(ValueError): self.d.observe(self.a,1,float('nan'),1)
        with self.assertRaises(ValueError): Detector(tile=0)

if __name__ == '__main__':
    result = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    if not result.wasSuccessful(): raise SystemExit(1)
    a = np.zeros((720,1280,3),dtype=np.uint8)
    b = a.copy(); b[300:320,400:440] = 255
    d = Detector(); durations=[]
    for i in range(110):
        start=time.perf_counter_ns()
        d.observe(a if i%2 else b,i,i,i)
        elapsed=(time.perf_counter_ns()-start)/1e6
        if i>=10: durations.append(elapsed)
    print(json.dumps({'tests': result.testsRun,'scope':'synthetic 1280x720 CPU observe only; excludes capture, transport, inference','samples':len(durations),'milliseconds':dict(zip(['p50','p95','p99'],np.percentile(durations,[50,95,99]).tolist()))}))
