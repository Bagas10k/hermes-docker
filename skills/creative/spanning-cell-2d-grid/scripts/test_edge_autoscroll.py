import math
import unittest
from edge_autoscroll import EdgeAutoScroll


class EdgeTests(unittest.TestCase):
    def setUp(self):
        self.engine = EdgeAutoScroll()

    def step(self, **kw):
        args = dict(pointer=(400, 200), viewport=(400, 400),
                    position=(100, 100), bounds=(1000, 1000), dt=.02)
        args.update(kw)
        return self.engine.step(**args)

    def test_quadratic_curve(self):
        self.assertEqual(self.engine.velocity(200, 400), 0)
        self.assertEqual(self.engine.velocity(376, 400), 200)
        self.assertEqual(self.engine.velocity(400, 400), 800)
        self.assertEqual(self.engine.velocity(900, 400), 800)

    def test_symmetry_and_monotonicity(self):
        last = -801
        for p in range(-100, 501):
            v = self.engine.velocity(p, 400)
            self.assertGreaterEqual(v, last)
            self.assertAlmostEqual(v, -self.engine.velocity(400-p, 400))
            last = v

    def test_small_viewport(self):
        self.assertEqual(self.engine.velocity(10, 20), 0)
        self.assertEqual(self.engine.velocity(0, 20), -800)
        self.assertEqual(self.engine.velocity(20, 20), 800)

    def test_delta_and_zoom(self):
        self.assertEqual(self.step().dx, 16)
        self.assertEqual(self.step(zoom=2).dx, 8)
        self.assertEqual(self.step(zoom=.5).dx, 32)

    def test_diagonal_bound(self):
        f = self.step(pointer=(400, 400))
        self.assertLessEqual(math.hypot(f.vx, f.vy), 800.000000001)
        self.assertAlmostEqual(f.dx, f.dy)

    def test_boundary_clipping(self):
        f = self.step(position=(999, 100))
        self.assertEqual((f.x, f.dx, f.vx), (1000, 1, 50))
        self.assertEqual(self.step(position=(1000, 100)).vx, 0)
        self.assertEqual(self.step(pointer=(-100, -100), position=(0, 0)).dx, 0)

    def test_lifecycle(self):
        for flags in [dict(dragging=False), dict(visible=False), dict(dt=0)]:
            f = self.step(**flags)
            self.assertEqual((f.dx, f.dy, f.vx, f.vy), (0, 0, 0, 0))

    def test_stall_capped(self):
        self.assertEqual(self.step(dt=10).dx, 40)

    def test_frame_partition(self):
        positions = []
        for hz in (30, 60, 120):
            pos = (100, 100)
            for _ in range(hz):
                f = self.step(position=pos, dt=1/hz)
                pos = (f.x, f.y)
            positions.append(pos[0])
        for x in positions:
            self.assertAlmostEqual(x, 900)

    def test_invalid_inputs(self):
        for kw in [dict(dt=-1), dict(zoom=0), dict(zoom=True), dict(dt=float('nan')),
                   dict(pointer=(float('inf'), 0)), dict(viewport=(0, 10)),
                   dict(position=(-1, 0)), dict(bounds=(-1, 0)), dict(dragging=1)]:
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                self.step(**kw)
        for kw in [dict(edge=0), dict(speed=-1), dict(max_dt=.2)]:
            with self.assertRaises(ValueError):
                EdgeAutoScroll(**kw)

    def test_zero_scroll_range(self):
        f = self.step(bounds=(0, 0), position=(0, 0))
        self.assertEqual((f.dx, f.dy), (0, 0))

    def test_seeded_bounds(self):
        import random
        rng = random.Random(224)
        for _ in range(500):
            bx, by = rng.uniform(0, 2000), rng.uniform(0, 2000)
            f = self.step(pointer=(rng.uniform(-100, 500), rng.uniform(-100, 500)),
                          bounds=(bx, by), position=(rng.uniform(0, bx), rng.uniform(0, by)))
            self.assertTrue(0 <= f.x <= bx and 0 <= f.y <= by)
            self.assertLessEqual(math.hypot(f.vx, f.vy), 800.00000001)


if __name__ == '__main__':
    unittest.main()
