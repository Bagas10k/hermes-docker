import unittest
from zoom_selection import world_point


class ZoomSelectionTests(unittest.TestCase):
    def test_projection(self):
        self.assertEqual(world_point((200, 100), (20, 0), 2), (120, 50))

    def test_zoom_roundtrip(self):
        for z in (0.25, 0.5, 1, 2, 4):
            for p in ((0, 0), (34, 57), (-12, 64)):
                w = world_point(p, (13, 27), z)
                for actual, expected in zip(((w[0]-13)*z, (w[1]-27)*z), p):
                    self.assertAlmostEqual(actual, expected)

    def test_invalid(self):
        for z in (0, -1, float('nan'), float('inf'), True):
            with self.subTest(z=z), self.assertRaises(ValueError):
                world_point((1, 2), (3, 4), z)

    def test_overflow(self):
        with self.assertRaises(ValueError):
            world_point((1e308, 2), (1e308, 4), 0.1)
