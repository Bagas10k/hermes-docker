import math
import random
import unittest
from frozen_camera_fixture import projected_point, render_html
from zoom_selection import world_point


class FrozenCameraTests(unittest.TestCase):
    def test_origin_border(self):
        self.assertEqual(projected_point((240,160),(40,30),2,(79,59)),(479,319))

    def test_roundtrip(self):
        rng=random.Random(33)
        for _ in range(500):
            w=(rng.uniform(0,2000),rng.uniform(0,1800))
            c=(rng.uniform(0,1000),rng.uniform(0,900))
            o=(rng.uniform(0,100),rng.uniform(0,100))
            z=rng.uniform(.25,4)
            screen=projected_point(w,c,z,o)
            actual=world_point(tuple(a-b for a,b in zip(screen,o)),c,z)
            for a,b in zip(actual,w):self.assertAlmostEqual(a,b,places=9)

    def test_invalid(self):
        for z in [0,-1,True,math.nan,math.inf]:
            with self.assertRaises(ValueError):projected_point((1,2),(0,0),z)
        with self.assertRaises(ValueError):projected_point((1,2,3),(0,0),1)

    def test_overflow(self):
        with self.assertRaises(ValueError):projected_point((1e308,0),(-1e308,0),4)

    def test_fixture_contract(self):
        html=render_html()
        self.assertIn('body.clientLeft-camera.x*z',html)
        self.assertIn('body.clientTop-camera.y*z',html)
        self.assertIn('attachEdgeScroll(body',html)
        self.assertIn('transform-origin:0 0',html)
        self.assertIn('keyboard: {',html)
        self.assertIn('retained_visible',html)
        self.assertIn('edge_direction_lead',html)
        self.assertIn('selection: {',html)
        self.assertIn('lead_edge_expanded',html)
        self.assertIn('multiRange: {',html)
        self.assertIn('deduplicate()',html)
        self.assertIn('queryVisible()',html)


if __name__=='__main__':unittest.main()
