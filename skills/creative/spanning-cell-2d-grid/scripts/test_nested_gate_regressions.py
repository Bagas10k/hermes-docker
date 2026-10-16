"""Parent falsification checks; synthetic data are not browser evidence."""
import copy
import unittest
import clipboard_nested_reflow as gate
from clipboard_nested_reflow import audit_nested_record

def audit_sticky(value):
    return gate.audit_sticky(value)
from test_clipboard_nested_reflow import make_full_record


class NestedGateRegressions(unittest.TestCase):
    def test_phase_cannot_claim_success_before_settlement(self):
        r = make_full_record()
        r['phases']['shrunk']['measurement'] = copy.deepcopy(r['phases']['settled']['measurement'])
        with self.assertRaises(ValueError):
            audit_nested_record(r)

    def test_coordinate_and_counter_binding(self):
        for field, value in [('viewport', 390), ('scale', 2), ('writeCalls', 2)]:
            r = make_full_record()
            r['phases']['scrolled']['measurement'][field] = value
            with self.assertRaises(ValueError):
                audit_nested_record(r)

    def test_window_fixed_in_every_phase(self):
        r = make_full_record()
        r['phases']['scrolled']['windowHeight'] += 1
        with self.assertRaises(ValueError):
            audit_nested_record(r)

    def test_neighbor_identity_is_not_just_some_element(self):
        r = make_full_record()
        r['phases']['roundtrip']['neighborNode'] = 'wrong-node'
        self.assertFalse(audit_nested_record(r)['passed'])

    def test_nonfinite_and_negative_metrics(self):
        for value in (True, '3', float('nan'), float('inf'), -1):
            r = make_full_record()
            r['phases']['shrunk']['containerWidth'] = value
            with self.assertRaises(ValueError):
                audit_nested_record(r)

    def test_sticky_requires_scroll_and_stuck_geometry(self):
        good = dict(overlayPosition='sticky', scrollBefore=50, scrollAfter=60,
                    inset=20, clipLeft=10, leftBefore=30, leftAfter=30,
                    normalLeft=-40, pointerEvents='none')
        self.assertTrue(audit_sticky(good))
        for field, value in [('overlayPosition', 'fixed'), ('scrollAfter', 50),
                             ('leftAfter', 20), ('normalLeft', 35), ('inset', float('nan'))]:
            bad = dict(good, **{field: value})
            with self.assertRaises(ValueError):
                audit_sticky(bad)


if __name__ == '__main__':
    unittest.main()
