"""Deterministic offline tests; no live GUI claims."""
import importlib.util
import unittest
from pathlib import Path


class Bootstrap(unittest.TestCase):
    def test_helper_exists(self):
        self.assertTrue(Path(__file__).with_name('grounding.py').is_file(),
                        'coordinate helper must be implemented')


class Calibration(unittest.TestCase):
    def test_scale_translation_not_dpr(self):
        import grounding as g
        self.assertTrue(hasattr(g, 'calibrate'), 'calibration API missing')
        css, os = g.Space.CSS, g.Space.OS
        p = lambda x, y, s: g.Point(x, y, s)
        source = g.Box(0, 0, 100, 100, css)
        dest = g.Box(-300, 80, 200, 300, os)
        anchors = [(p(0, 0, css), p(-300, 80, os)),
                   (p(100, 100, css), p(-100, 380, os)),
                   (p(0, 100, css), p(-300, 380, os)),
                   (p(100, 0, css), p(-100, 80, os))]
        m = g.calibrate(anchors, source, dest, 'g1', 1.0,
                        residual_limit=0.1, measurement_error=0.2)
        point, error = m.apply(p(50, 50, css), 0.1)
        self.assertEqual(point, p(-200, 230, os))
        self.assertAlmostEqual(error, 0.5)


class Admission(unittest.TestCase):
    def test_css_admission_preserves_css_pixels(self):
        import grounding as g
        self.assertTrue(hasattr(g, 'admit'), 'admission API missing')
        p = g.Point(50, 40, g.Space.CSS)
        identity = g.Identity('tab1', 'doc1', 'node1', 'button', 'Save')
        e = g.Evidence('g1', 10, identity, g.Box(20, 20, 60, 40, g.Space.CSS), True)
        hit = g.Hit('g1', 10, identity, p)
        result = g.admit(p, e, identity, hit, generation='g1', now=10.1,
                         max_age=0.2, uncertainty=1, max_uncertainty=2,
                         viewport=g.Box(0, 0, 200, 100, g.Space.CSS))
        self.assertEqual(result, (p, 1))


class Adversarial(unittest.TestCase):
    def setUp(self):
        import grounding as g
        self.g = g
        self.p = g.Point(50, 40, g.Space.CSS)
        self.identity = g.Identity('tab', 'doc', 'node', 'button', 'Save')
        self.e = g.Evidence('g', 10, self.identity, g.Box(20, 20, 60, 40, g.Space.CSS), True)
        self.h = g.Hit('g', 10, self.identity, self.p)
        self.kw = dict(generation='g', now=10.1, max_age=0.2, uncertainty=1,
                       max_uncertainty=2, viewport=g.Box(0, 0, 100, 100, g.Space.CSS))

    def run_admit(self, **changes):
        args = dict(point=self.p, evidence=self.e, expected=self.identity,
                    hit=self.h, **self.kw)
        args.update(changes)
        return self.g.admit(**args)

    def test_stale_all_evidence(self):
        from dataclasses import replace
        for key, obj in [('evidence', self.e), ('hit', self.h)]:
            for field in [dict(generation='old'), dict(captured=9), dict(captured=11)]:
                with self.subTest(key=key, field=field), self.assertRaises(self.g.Rejected):
                    self.run_admit(**{key: replace(obj, **field)})

    def test_semantic_scope_node_role_name_and_document(self):
        from dataclasses import replace
        for field in ('scope', 'document', 'node', 'role', 'name'):
            other = replace(self.identity, **{field: 'different'})
            for key, obj in [('evidence', self.e), ('hit', self.h)]:
                with self.subTest(field=field, key=key), self.assertRaises(self.g.Rejected):
                    self.run_admit(**{key: replace(obj, identity=other)})

    def test_disabled_unknown_and_wrong_hit_point(self):
        from dataclasses import replace
        for value in (False, None, 1, 'true'):
            with self.subTest(enabled=value), self.assertRaises(self.g.Rejected):
                self.run_admit(evidence=replace(self.e, enabled=value))
        with self.assertRaises(self.g.Rejected):
            self.run_admit(hit=replace(self.h, point=self.g.Point(51, 40, self.g.Space.CSS)))

    def test_invalid_policies(self):
        for key in ('now', 'max_age', 'uncertainty', 'max_uncertainty'):
            for value in (float('nan'), float('inf'), -1, True, '1'):
                with self.subTest(key=key, value=value), self.assertRaises(self.g.Rejected):
                    self.run_admit(**{key: value})
        with self.assertRaises(self.g.Rejected):
            self.run_admit(max_age=0)

    def test_uncertainty_and_edges(self):
        for changes in (dict(uncertainty=20, max_uncertainty=30),
                        dict(max_uncertainty=0.5),
                        dict(viewport=self.g.Box(0, 0, 50, 100, self.g.Space.CSS))):
            with self.subTest(changes=changes), self.assertRaises(self.g.Rejected):
                self.run_admit(**changes)

    def test_os_mapping_requires_fresh_exact_os_hit(self):
        from dataclasses import replace
        g = self.g
        transform = g.Transform(self.kw['viewport'], g.Box(-500, 0, 500, 500, g.Space.OS),
                                2, 3, -400, 80, 0.2, 'g', 10)
        p, bound = transform.apply(self.p, 1)
        hit = g.Hit('g', 10, self.identity, p)
        self.assertEqual(self.run_admit(transform=transform, output_hit=hit, max_uncertainty=4), (p, bound))
        for t, h in ((transform, None), (replace(transform, generation='old'), hit),
                     (transform, replace(hit, captured=9)), (transform, self.h)):
            with self.subTest(t=t, h=h), self.assertRaises(g.Rejected):
                self.run_admit(transform=t, output_hit=h, max_uncertainty=4)

    def test_calibration_error_cannot_cross_target(self):
        g = self.g
        t = g.Transform(self.kw['viewport'], g.Box(-500, -500, 1000, 1000, g.Space.OS),
                        1, 1, 0, 0, 21, 'g', 10)
        p, _ = t.apply(self.p, 1)
        with self.assertRaises(g.Rejected):
            self.run_admit(transform=t, output_hit=g.Hit('g', 10, self.identity, p), max_uncertainty=30)

    def test_coordinate_validation(self):
        g = self.g
        for v in (float('nan'), float('inf'), True, '2'):
            with self.subTest(value=v), self.assertRaises(g.Rejected):
                g.Point(v, 0, g.Space.CSS)
        for w in (0, -1):
            with self.assertRaises(g.Rejected):
                g.Box(0, 0, w, 1, g.Space.CSS)
        with self.assertRaises(g.Rejected):
            g.Point(0, 0, 'CSS')
        with self.assertRaises(g.Rejected):
            self.run_admit(point=g.Point(50, 40, g.Space.IMAGE))

    def calibration_fixture(self):
        g = self.g
        src = g.Box(0, 0, 100, 100, g.Space.IMAGE)
        dst = g.Box(0, 0, 50, 50, g.Space.CSS)
        anchors = [(g.Point(x, y, src.space), g.Point(x/2, y/2, dst.space))
                   for x, y in [(0, 0), (100, 100), (0, 100), (100, 0)]]
        return src, dst, anchors

    def test_image_resize_and_no_extrapolation(self):
        g = self.g
        src, dst, anchors = self.calibration_fixture()
        t = g.calibrate(anchors, src, dst, 'g', 10, residual_limit=0, measurement_error=0)
        self.assertEqual(t.apply(g.Point(50, 40, src.space)), (g.Point(25, 20, dst.space), 0))
        for p, error in [(g.Point(101, 20, src.space), 0), (g.Point(0, 20, src.space), 1), (self.p, 0)]:
            with self.assertRaises(g.Rejected):
                t.apply(p, error)

    def test_bad_calibration(self):
        g = self.g
        src, dst, anchors = self.calibration_fixture()
        cases = [anchors[:3], [anchors[0]]*4,
                 anchors[:2] + [anchors[0], anchors[1]],
                 anchors[:3] + [(anchors[3][0], g.Point(40, 0, dst.space))]]
        for sample in cases:
            with self.subTest(sample=sample), self.assertRaises(g.Rejected):
                g.calibrate(sample, src, dst, 'g', 10, residual_limit=0.1, measurement_error=0)

    def test_repeated_heldout_anchor_rejected(self):
        g = self.g
        src, dst, anchors = self.calibration_fixture()
        with self.assertRaises(g.Rejected):
            g.calibrate(anchors[:3] + [anchors[2]], src, dst, 'g', 10,
                        residual_limit=0.1, measurement_error=0)

    def test_deterministic_roundtrip_grid(self):
        g = self.g
        src = g.Box(-100, -100, 200, 200, g.Space.CSS)
        dst = g.Box(-500, -500, 1000, 1000, g.Space.OS)
        for sx, sy in [(1, 1), (1.25, 2), (3, 0.5)]:
            forward = g.Transform(src, dst, sx, sy, -10, 30, 0, 'g', 10)
            reverse = g.Transform(dst, src, 1/sx, 1/sy, 10/sx, -30/sy, 0, 'g', 10)
            for x in range(-90, 91, 30):
                for y in range(-90, 91, 30):
                    p = g.Point(x, y, src.space)
                    q, _ = forward.apply(p)
                    r, _ = reverse.apply(q)
                    self.assertAlmostEqual(r.x, p.x)
                    self.assertAlmostEqual(r.y, p.y)


if __name__ == '__main__':
    unittest.main()
