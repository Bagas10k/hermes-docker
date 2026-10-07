"""Deterministic root identity checks; not browser-layout evidence."""
import unittest
import xml.etree.ElementTree as ET
from branch_history import BranchHistory
from branch_dag_topology import compute_branch_roots, render_dag_minimap_svg
from history_browser import render, export_manifest

class BranchIdentityTests(unittest.TestCase):
    def history(self):
        h = BranchHistory({})
        for root in ('b', 'c', 'd', 'e', 'f', 'g'):
            h.commit(root, 'root', {})
            h.commit(root + '-child', root, {})
        return h

    def test_root_only(self):
        self.assertEqual(compute_branch_roots(BranchHistory({})), {'root': 'root'})

    def test_palette_wrap_is_not_identity(self):
        h = self.history()
        roots = compute_branch_roots(h)
        for root in ('b', 'c', 'd', 'e', 'f', 'g'):
            self.assertEqual(roots[root + '-child'], root)
        self.assertEqual(len(set(roots.values())), 7)

    def test_earlier_sibling_and_checkout_preserve_identity(self):
        h = self.history()
        before = compute_branch_roots(h)
        h.commit('a', 'root', {})
        h.checkout('g-child')
        self.assertEqual({n: compute_branch_roots(h)[n] for n in before}, before)

    def test_insertion_order(self):
        h = BranchHistory({})
        for root in reversed(('b', 'c', 'd', 'e', 'f', 'g')):
            h.commit(root, 'root', {})
            h.commit(root + '-child', root, {})
        self.assertEqual(compute_branch_roots(h), compute_branch_roots(self.history()))

    def test_svg_and_manifest_membership(self):
        h = self.history()
        svg = ET.fromstring(render_dag_minimap_svg(h))
        dots = [e for e in svg.iter() if 'data-node' in e.attrib]
        for dot in dots:
            root = compute_branch_roots(h)[dot.attrib['data-node']]
            self.assertEqual(dot.attrib['data-branch-root'], root)
            self.assertIn('branch root ' + root, dot.attrib['aria-label'])
        self.assertEqual(export_manifest(h)['branch_roots'], compute_branch_roots(h))

    def test_visible_full_labels_escaped(self):
        h = BranchHistory({})
        h.commit('<long&branch>', 'root', {})
        page = render(h)
        self.assertIn('Branch root: &lt;long&amp;branch&gt;', page)
        self.assertIn('id="branch-root-labels"', page)

if __name__ == '__main__':
    unittest.main()
