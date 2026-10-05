"""Unit tests for branch DAG topology SVG rendering and branch pruning mechanics."""
import unittest
import xml.etree.ElementTree as ET
from branch_history import BranchHistory
from branch_dag_topology import prune_abandoned_branches, render_dag_svg, compute_node_diff


class BranchDAGTopologyTests(unittest.TestCase):
    def setUp(self):
        self.history = BranchHistory({'A1': 'init'})
        self.history.commit('b1', 'root', {'A1': 'b1'}, activate=True)
        self.history.commit('b2', 'b1', {'A1': 'b2'}, activate=True)
        self.history.undo()
        self.history.commit('b3', 'b1', {'A1': 'b3'}, activate=False)

    def test_svg_rendering_structure(self):
        svg_str = render_dag_svg(self.history)
        self.assertIn('<svg', svg_str)
        self.assertIn('viewBox', svg_str)
        self.assertIn('aria-label="Visual DAG Branch Topology"', svg_str)
        self.assertIn('data-node="root"', svg_str)
        self.assertIn('data-node="b1"', svg_str)
        self.assertIn('data-node="b2"', svg_str)
        self.assertIn('data-node="b3"', svg_str)
        
        # Verify active edge / cursor highlighting
        self.assertIn('class="node-circle active"', svg_str)
        
        # Valid XML parsing
        root = ET.fromstring(svg_str)
        self.assertEqual(root.tag, '{http://www.w3.org/2000/svg}svg')

    def test_compute_node_diff_metrics(self):
        # Root has 0 mutations
        root_diff = compute_node_diff(self.history, 'root')
        self.assertEqual(root_diff['total_mutations'], 0)
        self.assertEqual(root_diff['badge_text'], '0')

        # b1 modifies A1 (from 'init' to 'b1')
        b1_diff = compute_node_diff(self.history, 'b1')
        self.assertEqual(b1_diff['added'], 0)
        self.assertEqual(b1_diff['deleted'], 0)
        self.assertEqual(b1_diff['modified'], 1)
        self.assertEqual(b1_diff['total_mutations'], 1)
        self.assertEqual(b1_diff['badge_text'], '~1')

        # Create commit with added keys
        self.history.commit('b4', 'root', {'B1': 'new', 'C1': 'new2'}, activate=False)
        b4_diff = compute_node_diff(self.history, 'b4')
        # In BranchHistory.commit(), state is shallow copy overlay of parent state plus delta
        # So B1 and C1 are added, A1 is preserved
        self.assertEqual(b4_diff['added'], 2)
        self.assertEqual(b4_diff['deleted'], 0)
        self.assertEqual(b4_diff['modified'], 0)
        self.assertEqual(b4_diff['total_mutations'], 2)
        self.assertEqual(b4_diff['badge_text'], '+2')

        # If we directly create a node state with a deleted key
        NodeClass = type(self.history._nodes['root'])
        self.history._nodes['b5'] = NodeClass(parent='root', delta={'B1': 'isolated'}, state={'B1': 'isolated'})
        b5_diff = compute_node_diff(self.history, 'b5')
        self.assertEqual(b5_diff['added'], 1)
        self.assertEqual(b5_diff['deleted'], 1)  # A1 missing
        self.assertEqual(b5_diff['modified'], 0)
        self.assertEqual(b5_diff['total_mutations'], 2)
        self.assertIn('+1', b5_diff['badge_text'])
        self.assertIn('-1', b5_diff['badge_text'])

    def test_svg_diff_badge_rendering(self):
        svg_str = render_dag_svg(self.history, show_diff_badges=True)
        # Check badge rect and text presence
        self.assertIn('class="diff-badge"', svg_str)
        self.assertIn('class="diff-badge-rect"', svg_str)
        self.assertIn('class="diff-badge-text"', svg_str)
        self.assertIn('data-badge-node="b1"', svg_str)
        self.assertIn('data-mutations="1"', svg_str)
        
        # When show_diff_badges=False, badges should not be rendered
        svg_no_badges = render_dag_svg(self.history, show_diff_badges=False)
        self.assertNotIn('class="diff-badge"', svg_no_badges)

    def test_prune_protects_root_and_active_cursor(self):
        # Cursor is at b1. Path is root -> b1.
        # Abandoned leaves are b2 and b3 (neither is an ancestor of b1).
        count, pruned = prune_abandoned_branches(self.history)
        self.assertEqual(count, 2)
        self.assertEqual(pruned, {'b2', 'b3'})
        self.assertIn('root', self.history._nodes)
        self.assertIn('b1', self.history._nodes)
        self.assertNotIn('b2', self.history._nodes)
        self.assertNotIn('b3', self.history._nodes)
        self.assertEqual(self.history.children('b1'), ())

    def test_prune_respects_explicit_protected_nodes(self):
        # If b3 is protected, only b2 should be pruned
        count, pruned = prune_abandoned_branches(self.history, protected_nodes={'b3'})
        self.assertEqual(count, 1)
        self.assertEqual(pruned, {'b2'})
        self.assertIn('b3', self.history._nodes)
        self.assertEqual(self.history.children('b1'), ('b3',))

    def test_prune_with_max_retained_nodes_budget(self):
        # Add deep branches
        self.history.commit('c1', 'root', {'B1': 'c1'}, activate=False)
        self.history.commit('c2', 'c1', {'B1': 'c2'}, activate=False)
        # Total nodes: root, b1, b2, b3, c1, c2 = 6 nodes
        self.assertEqual(len(self.history._nodes), 6)
        
        # Cursor is at b1. If max_retained_nodes=5, should prune 1 node.
        count, pruned = prune_abandoned_branches(self.history, max_retained_nodes=5)
        self.assertEqual(count, 1)
        self.assertEqual(len(self.history._nodes), 5)
        # Root and b1 must remain
        self.assertIn('root', self.history._nodes)
        self.assertIn('b1', self.history._nodes)

    def test_compute_node_diff_details(self):
        from branch_dag_topology import compute_node_diff_details, format_diff_tooltip_text
        
        # Root node diff
        root_diff = compute_node_diff_details(self.history, 'root')
        self.assertEqual(root_diff['total_mutations'], 0)
        self.assertIsNone(root_diff['parent'])
        self.assertEqual(root_diff['summary'], 'Root revision')
        self.assertIn('Root revision', format_diff_tooltip_text(root_diff))
        
        # Child node b1 diff from root: A1 modified ('init' -> 'b1')
        b1_diff = compute_node_diff_details(self.history, 'b1')
        self.assertEqual(b1_diff['total_mutations'], 1)
        self.assertEqual(b1_diff['parent'], 'root')
        self.assertIn('A1', b1_diff['modified'])
        self.assertEqual(b1_diff['modified']['A1']['old'], 'init')
        self.assertEqual(b1_diff['modified']['A1']['new'], 'b1')
        
        tooltip_b1 = format_diff_tooltip_text(b1_diff)
        self.assertIn('Changes from root', tooltip_b1)
        self.assertIn('~ A1: init -> b1', tooltip_b1)
        
        # Test node with additions and deletions
        self.history.commit('b_multi', 'root', {'A1': 'new_val', 'B1': 'added_val'}, activate=False)
        multi_diff = compute_node_diff_details(self.history, 'b_multi')
        self.assertEqual(multi_diff['total_mutations'], 2)
        self.assertIn('B1', multi_diff['added'])
        self.assertIn('A1', multi_diff['modified'])
        tooltip_multi = format_diff_tooltip_text(multi_diff)
        self.assertIn('+ B1: added_val', tooltip_multi)
        self.assertIn('~ A1: init -> new_val', tooltip_multi)

    def test_svg_spatial_coordinates_and_diff_popover_metadata(self):
        from branch_dag_topology import render_dag_svg
        svg_str = render_dag_svg(self.history, show_diff_badges=True)
        
        # Verify spatial coordinate attributes
        self.assertIn('data-cx="', svg_str)
        self.assertIn('data-cy="', svg_str)
        
        # Verify diff metadata attributes and tooltip element
        self.assertIn('data-diff-json="', svg_str)
        self.assertIn('data-mutations="1"', svg_str)
        self.assertIn('<title>', svg_str)
        self.assertIn('Changes from root', svg_str)

    def test_compute_node_lineage_and_ancestor_path(self):
        from branch_dag_topology import compute_node_lineage
        
        # Lineage from root
        self.assertEqual(compute_node_lineage(self.history, 'root'), ['root'])
        
        # Lineage from b1
        self.assertEqual(compute_node_lineage(self.history, 'b1'), ['root', 'b1'])
        
        # Lineage from b2 (child of b1)
        self.assertEqual(compute_node_lineage(self.history, 'b2'), ['root', 'b1', 'b2'])
        
        # Non-existent node
        self.assertEqual(compute_node_lineage(self.history, 'nonexistent'), [])
        self.assertEqual(compute_node_lineage(None, 'root'), [])

    def test_render_dag_minimap_svg_proportions_and_attributes(self):
        from branch_dag_topology import render_dag_minimap_svg
        minimap_str = render_dag_minimap_svg(self.history)
        
        self.assertIn('class="dag-minimap-svg"', minimap_str)
        self.assertIn('data-world-width="', minimap_str)
        self.assertIn('data-world-height="', minimap_str)
        self.assertIn('data-scale-x="', minimap_str)
        self.assertIn('data-scale-y="', minimap_str)
        self.assertIn('id="minimap-viewport-frame"', minimap_str)
        self.assertIn('class="minimap-viewport-rect"', minimap_str)
        self.assertIn('class="minimap-bg"', minimap_str)
        self.assertIn('class="minimap-node active"', minimap_str)
        self.assertIn('data-cluster-color="', minimap_str)

    def test_compute_branch_clusters_color_partitioning(self):
        from branch_dag_topology import compute_branch_clusters
        clusters = compute_branch_clusters(self.history)
        self.assertEqual(clusters['root'], '#94A3B8')
        # b1 is child of root -> cluster 0 (#10B981)
        self.assertEqual(clusters['b1'], '#10B981')
        # b2 and b3 are descendants of b1 -> inherit #10B981
        self.assertEqual(clusters['b2'], '#10B981')
        self.assertEqual(clusters['b3'], '#10B981')

        # Add parallel branch from root
        self.history.commit('parallel_branch', 'root', {'B1': 'p'}, activate=False)
        clusters_2 = compute_branch_clusters(self.history)
        # Second root child receives cluster 1 (#8B5CF6)
        self.assertEqual(clusters_2['parallel_branch'], '#8B5CF6')


if __name__ == '__main__':
    unittest.main()
