import importlib.util
from pathlib import Path
import unittest
from branch_history import BranchHistory


class HistoryBrowserTests(unittest.TestCase):
    def test_export_preserves_cursor_and_sibling_snapshots(self):
        path = Path(__file__).with_name('history_browser.py')
        self.assertTrue(path.exists(), 'history browser exporter is missing')
        spec = importlib.util.spec_from_file_location('history_browser', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        history = BranchHistory({'A1': 'base'})
        history.commit('alpha', 'root', {'A1': 'alpha'})
        history.commit('beta', 'root', {'A1': 'beta'}, activate=False)
        manifest = module.export_manifest(history)
        self.assertEqual(history.cursor, 'alpha')
        self.assertEqual(manifest['cursor'], 'alpha')
        self.assertEqual(manifest['nodes']['root']['children'], ['alpha', 'beta'])
        self.assertEqual(manifest['nodes']['beta']['cells'], {'A1': 'beta'})

    def test_render_escapes_script_terminators(self):
        from history_browser import render
        text = render(BranchHistory({'A1': '</script><img src=x>'}))
        self.assertNotIn('</script><img', text)
        self.assertIn('aria-live="polite"', text)
        self.assertIn('id="branches"', text)

    def test_empty_children_handling_and_deep_branch_rendering(self):
        from history_browser import render, export_manifest
        history = BranchHistory({'X': '1'})
        history.commit('b1', 'root', {'X': '2'}, activate=True)
        manifest = export_manifest(history)
        self.assertEqual(manifest['cursor'], 'b1')
        self.assertEqual(manifest['nodes']['b1']['children'], [])
        html = render(history)
        self.assertIn('Pratinjau riwayat cabang', html)
        self.assertIn('id="dag-view"', html)
        self.assertIn('class="diff-badge"', html)

    def test_export_manifest_includes_svg_topology_with_badges(self):
        from history_browser import export_manifest
        history = BranchHistory({'X': '1'})
        history.commit('b1', 'root', {'X': '2', 'Y': '3'}, activate=True)
        manifest = export_manifest(history)
        self.assertIn('svg_topology', manifest)
        self.assertIn('diff-badge', manifest['svg_topology'])
        self.assertIn('data-badge-node="b1"', manifest['svg_topology'])

    def test_render_includes_diff_popover_and_spatial_attributes(self):
        from history_browser import render
        history = BranchHistory({'A1': 'init'})
        history.commit('node_alpha', 'root', {'A1': 'updated', 'B1': 'new_col'}, activate=True)
        html = render(history)
        self.assertIn('id="dag-diff-popover"', html)
        self.assertIn('class="diff-popover"', html)
        self.assertIn('data-cx="', html)
        self.assertIn('data-cy="', html)
        self.assertIn('data-diff-json="', html)

    def test_render_includes_breadcrumbs_bar_and_manifest_lineage(self):
        from history_browser import render, export_manifest
        history = BranchHistory({'A1': 'init'})
        history.commit('node_alpha', 'root', {'A1': 'updated'}, activate=True)
        history.commit('node_beta', 'node_alpha', {'B1': 'deep'}, activate=True)
        
        manifest = export_manifest(history)
        self.assertIn('lineage', manifest)
        self.assertEqual(manifest['lineage'], ['root', 'node_alpha', 'node_beta'])
        
        html = render(history)
        self.assertIn('id="dag-breadcrumbs"', html)
        self.assertIn('class="dag-breadcrumbs-bar"', html)
        self.assertIn('aria-label="Jejak silsilah cabang"', html)

    def test_render_includes_minimap_radar_and_manifest_svg_minimap(self):
        from history_browser import render, export_manifest
        history = BranchHistory({'A1': 'init'})
        history.commit('node_alpha', 'root', {'A1': 'updated'}, activate=True)
        
        manifest = export_manifest(history)
        self.assertIn('svg_minimap', manifest)
        self.assertIn('id="minimap-viewport-frame"', manifest['svg_minimap'])
        
        html = render(history)
        self.assertIn('id="dag-minimap-wrap"', html)
        self.assertIn('id="dag-minimap-radar"', html)
        self.assertIn('id="dag-minimap-toggle"', html)
        self.assertIn('RADAR MINI-MAP', html)

    def test_render_includes_minimap_toggle_button_and_collapsed_class(self):
        from history_browser import render
        history = BranchHistory({'A1': 'init'})
        html = render(history)
        self.assertIn('id="dag-minimap-toggle"', html)
        self.assertIn('aria-expanded="true"', html)
        self.assertIn('.dag-minimap-container.collapsed', html)
        self.assertIn('.dag-minimap-toggle-btn', html)

    def test_render_includes_breadcrumb_shortcut_badge_styling(self):
        from history_browser import render
        history = BranchHistory({'A1': 'init'})
        html = render(history)
        self.assertIn('.dag-breadcrumb-badge', html)
        self.assertIn('gap:5px', html)

    def test_render_includes_minimap_scale_controls_and_copy_button(self):
        from history_browser import render
        history = BranchHistory({'A1': 'init'})
        html = render(history)
        self.assertIn('id="dag-minimap-scale-controls"', html)
        self.assertIn('class="dag-minimap-scale-btn', html)
        self.assertIn('data-scale="1.5"', html)
        self.assertIn('data-scale="2"', html)
        self.assertIn('.dag-breadcrumb-copy-btn', html)
        self.assertIn('.dag-minimap-scale-btn.active', html)

    def test_render_includes_search_omnibar_controls_and_styling(self):
        from history_browser import render
        history = BranchHistory({'A1': 'init'})
        html = render(history)
        self.assertIn('id="dag-search-bar"', html)
        self.assertIn('id="dag-search-input"', html)
        self.assertIn('id="dag-search-count"', html)
        self.assertIn('id="dag-search-clear"', html)
        self.assertIn('.dag-search-omnibar', html)
        self.assertIn('.dag-search-input', html)
        self.assertIn('.node-item.search-match', html)
        self.assertIn('.node-item.search-dim', html)

    def test_render_includes_minimap_clustering_and_search_match_styling(self):
        from history_browser import render, export_manifest
        history = BranchHistory({'A1': 'init'})
        history.commit('node_alpha', 'root', {'A1': 'a'}, activate=False)
        history.commit('node_beta', 'root', {'A1': 'b'}, activate=False)
        manifest = export_manifest(history)
        self.assertIn('branch_clusters', manifest)
        self.assertIn('node_alpha', manifest['branch_clusters'])
        self.assertIn('node_beta', manifest['branch_clusters'])
        self.assertEqual(manifest['branch_clusters']['root'], '#94A3B8')

        html = render(history)
        self.assertIn('data-cluster-color="', html)
        self.assertIn('.minimap-node.search-match', html)
        self.assertIn('.minimap-node.search-dim', html)


if __name__ == '__main__':
    unittest.main()
