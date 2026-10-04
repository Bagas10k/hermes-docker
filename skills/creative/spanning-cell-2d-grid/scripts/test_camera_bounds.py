import random
import unittest
from camera_bounds import reconcile_camera


class CameraBoundsTests(unittest.TestCase):
    def test_expand_clamps(self):
        c = reconcile_camera(1900, 1700, 1, 640, 274)
        self.assertEqual((c['x'], c['y']), (1360, 1526))

    def test_shrink_preserves_offset(self):
        self.assertEqual(reconcile_camera(500, 400, 1, 100, 100)['x'], 500)

    def test_zoom_out_clamps(self):
        c = reconcile_camera(1500, 1500, .5, 640, 274)
        self.assertEqual((c['maxX'], c['maxY']), (720, 1252))

    def test_world_smaller_than_viewport(self):
        c = reconcile_camera(100, 100, .25, 640, 500)
        self.assertEqual((c['x'], c['y']), (0, 0))

    def test_zero_body(self):
        self.assertEqual(reconcile_camera(10, 20, 1, 0, 0)['x'], 10)

    def test_invalid(self):
        for index in range(7):
            for bad in (True, float('nan'), float('inf'), '1'):
                args = [0, 0, 1, 100, 100, 2000, 1800]
                args[index] = bad
                with self.assertRaises(ValueError): reconcile_camera(*args)
        for z in (0, -1):
            with self.assertRaises(ValueError): reconcile_camera(0, 0, z, 100, 100)
        with self.assertRaises(ValueError): reconcile_camera(0,0,1,-1,100)
        with self.assertRaises(ValueError): reconcile_camera(0,0,5e-324,100,100)

    def test_seeded_idempotence_and_bounds(self):
        rng = random.Random(34)
        for _ in range(500):
            x,y,w,h = [rng.uniform(0,4000) for _ in range(4)]
            z=rng.choice((.25,.5,1,2,4))
            c=reconcile_camera(x,y,z,w,h)
            self.assertTrue(0 <= c['x'] <= c['maxX'])
            self.assertTrue(0 <= c['y'] <= c['maxY'])
            self.assertEqual(c,reconcile_camera(c['x'],c['y'],z,w,h))


if __name__ == '__main__': unittest.main()
