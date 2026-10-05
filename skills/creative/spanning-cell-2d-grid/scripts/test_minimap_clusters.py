"""Deterministic minimap cluster contracts; no browser claims."""
import unittest
import xml.etree.ElementTree as ET
from branch_history import BranchHistory
from branch_dag_topology import compute_branch_clusters, render_dag_minimap_svg

class MinimapClusters(unittest.TestCase):
    def history(self, order=('alpha', 'beta')):
        h = BranchHistory({})
        for name in order:
            h.commit(name, 'root', {'A1': name}, activate=False)
        h.commit('child', 'alpha', {}, activate=False)
        return h

    def test_insertion_order_independent(self):
        self.assertEqual(compute_branch_clusters(self.history()),
                         compute_branch_clusters(self.history(('beta', 'alpha'))))

    def test_checkout_does_not_reassign_clusters(self):
        h = self.history()
        before = compute_branch_clusters(h)
        h.checkout('child')
        self.assertEqual(before, compute_branch_clusters(h))
        self.assertEqual(before['alpha'], before['child'])

    def test_svg_metadata_escaped_and_complete(self):
        h = self.history()
        h.commit('x<&"', 'root', {}, activate=False)
        svg = ET.fromstring(render_dag_minimap_svg(h))
        dots = [e for e in svg.iter() if 'minimap-node' in e.get('class', '').split()]
        self.assertEqual({e.get('data-node') for e in dots}, set(h._nodes))
        self.assertTrue(all(e.get('data-cluster-color') for e in dots))

    def test_palette_wrap_is_explicit_not_unique_identity(self):
        h = BranchHistory({})
        for i in range(6):
            h.commit(str(i), 'root', {}, activate=False)
        colors = compute_branch_clusters(h)
        self.assertEqual(colors['0'], colors['5'])

    def test_root_only(self):
        self.assertEqual(compute_branch_clusters(BranchHistory({})), {'root': '#94A3B8'})

if __name__ == '__main__':
    unittest.main()
