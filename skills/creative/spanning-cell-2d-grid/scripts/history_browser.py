"""Export trusted local history into a standalone, read-only browser preview with SVG DAG topology."""
import json
from html import escape
from pathlib import Path
from branch_history import BranchHistory
from branch_dag_topology import (
    render_dag_svg,
    render_dag_minimap_svg,
    prune_abandoned_branches,
    compute_node_diff_details,
    compute_node_lineage,
    compute_branch_clusters,
    compute_branch_roots
)


def export_manifest(history):
    # Read immutable nodes without temporary checkout or cursor side effects.
    lineage = compute_node_lineage(history, history.cursor)
    branch_clusters = compute_branch_clusters(history)
    return {
        'cursor': history.cursor,
        'lineage': lineage,
        'branch_clusters': branch_clusters,
        'branch_roots': compute_branch_roots(history),
        'svg_topology': render_dag_svg(history),
        'svg_minimap': render_dag_minimap_svg(history),
        'nodes': {
            key: {
                'parent': node.parent,
                'children': list(history.children(key)),
                'cells': dict(node.state)
            } for key, node in history._nodes.items()
        }
    }


def render(history):
    manifest = export_manifest(history)
    svg_topo = manifest.pop('svg_topology')
    # Full textual membership stays readable even when palette colors wrap.
    roots = manifest['branch_roots']
    members = {}
    for node, owner in roots.items():
        members.setdefault(owner, []).append(node)
    legend = '<ul id="branch-root-labels" aria-label="Branch roots">' + ''.join(
        '<li data-branch-root="' + escape(root, quote=True) + '">Branch root: ' +
        escape(root) + ' — Nodes: ' + escape(', '.join(sorted(members[root]))) + '</li>'
        for root in sorted(members)) + '</ul>'
    data = json.dumps(manifest, ensure_ascii=True).replace('<', '\\u003c')
    script = Path(__file__).with_name('history_browser.js').read_text()
    return '''<!doctype html><html lang="id"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pratinjau riwayat cabang</title>
<style>body{font:16px system-ui;margin:20px;background:#faf6ef;color:#14120e}
main{max-width:820px}button{font:inherit;margin:4px;padding:12px;max-width:100%;overflow-wrap:anywhere}
:focus-visible{outline:3px solid #1669e8;outline-offset:3px}pre{white-space:pre-wrap;overflow-wrap:anywhere}
.dag-container{position:relative;background:#fff;border:1px solid #cbd5e1;border-radius:8px;padding:0;margin:16px 0;overflow-x:auto;scroll-behavior:auto}
.dag-breadcrumbs-bar{display:flex;align-items:center;flex-wrap:wrap;gap:6px;background:#f1f5f9;border:1px solid #cbd5e1;border-radius:6px;padding:8px 12px;margin:12px 0;font-family:ui-monospace,monospace;font-size:12px;color:#334155}
.dag-breadcrumb-copy-btn{display:inline-flex;align-items:center;background:#e2e8f0;border:1px solid #94a3b8;border-radius:4px;padding:3px 7px;cursor:pointer;color:#334155;font-size:10px;font-family:inherit;font-weight:600;margin-left:auto;transition:all 0.15s ease;line-height:1}
.dag-breadcrumb-copy-btn:hover{background:#cbd5e1;color:#0f172a}
.dag-breadcrumb-copy-btn.copied{background:#10b981;color:#fff;border-color:#059669}
.dag-breadcrumb-item{display:inline-flex;align-items:center;background:#fff;border:1px solid #94a3b8;border-radius:4px;padding:3px 8px;cursor:pointer;color:#0f172a;transition:all 0.15s ease;gap:5px}
.dag-breadcrumb-item:hover{background:#e2e8f0;border-color:#64748b}
.dag-breadcrumb-item.active{background:#1669e8;color:#fff;border-color:#0f172a;font-weight:600}
.dag-breadcrumb-badge{display:inline-block;font-size:9px;font-family:ui-monospace,monospace;font-weight:700;line-height:1;padding:1px 4px;border-radius:3px;background:#e2e8f0;color:#475569;border:1px solid #cbd5e1}
.dag-breadcrumb-item.active .dag-breadcrumb-badge{background:rgba(255,255,255,0.25);color:#fff;border-color:rgba(255,255,255,0.4)}
.dag-breadcrumb-sep{color:#94a3b8;user-select:none;font-weight:bold}
.diff-popover{position:absolute;display:none;background:#0f172a;color:#f8fafc;padding:10px 14px;border-radius:6px;font-family:ui-monospace,monospace;font-size:12px;box-shadow:0 10px 25px -5px rgba(0,0,0,0.3);z-index:100;pointer-events:none;max-width:320px;line-height:1.4}
.diff-popover.visible{display:block}
.diff-popover-title{font-weight:700;color:#93c5fd;margin-bottom:6px;border-bottom:1px solid #334155;padding-bottom:4px}
.diff-item-added{color:#34d399}
.diff-item-modified{color:#fbbf24}
.diff-item-deleted{color:#f87171}
.diff-item-empty{color:#94a3b8;font-style:italic}
.dag-minimap-container{position:relative;width:fit-content;max-width:100%;box-sizing:border-box;background:#0f172a;border:1px solid #334155;border-radius:8px;padding:6px;box-shadow:0 10px 25px -5px rgba(0,0,0,0.4);z-index:90;user-select:none;transition:all 0.2s cubic-bezier(0.16,1,0.3,1)}
.dag-minimap-container.collapsed .dag-minimap-radar{display:none}
.dag-minimap-container.collapsed .dag-minimap-scale-group{display:none}
.dag-minimap-container.collapsed{padding:4px 8px}
.dag-minimap-header{display:flex;justify-content:space-between;align-items:center;font-family:ui-monospace,monospace;font-size:10px;color:#94a3b8;margin-bottom:4px;padding:0 2px;gap:8px}
.dag-minimap-scale-group{display:inline-flex;align-items:center;gap:3px}
.dag-minimap-scale-btn{background:#1e293b;border:1px solid #475569;color:#94a3b8;border-radius:3px;font-size:9px;padding:1px 5px;cursor:pointer;font-family:inherit;line-height:1.1}
.dag-minimap-scale-btn:hover{background:#334155;color:#f8fafc}
.dag-minimap-scale-btn.active{background:#1669e8;color:#fff;border-color:#3b82f6;font-weight:700}
.dag-minimap-toggle-btn{background:#1e293b;border:1px solid #475569;color:#cbd5e1;border-radius:4px;font-size:9px;padding:2px 6px;cursor:pointer;font-family:inherit;line-height:1}
.dag-minimap-toggle-btn:hover{background:#334155;color:#f8fafc}
#branch-root-labels{overflow-wrap:anywhere}.dag-minimap-header{flex-wrap:wrap}.dag-minimap-svg{display:block;max-width:100%}.dag-minimap-radar{display:block;cursor:crosshair;overflow:hidden;border-radius:4px}
.dag-search-omnibar{display:flex;align-items:center;gap:8px;background:#f8fafc;border:1px solid #cbd5e1;border-radius:6px;padding:6px 10px;margin:8px 0;font-family:ui-monospace,monospace;font-size:12px}
.dag-search-input{flex:1;background:#fff;border:1px solid #94a3b8;border-radius:4px;padding:4px 8px;font-family:inherit;font-size:12px;color:#0f172a;outline:none;transition:border-color 0.15s ease}
.dag-search-input:focus{border-color:#1669e8;box-shadow:0 0 0 2px rgba(22,105,232,0.2)}
.dag-search-count{font-size:11px;color:#64748b;font-weight:600;min-width:60px;text-align:right}
.dag-search-clear-btn{background:#e2e8f0;border:1px solid #94a3b8;border-radius:4px;padding:2px 6px;cursor:pointer;color:#475569;font-size:10px;font-family:inherit;line-height:1}
.dag-search-clear-btn:hover{background:#cbd5e1;color:#0f172a}
.node-item.search-match .node-circle{stroke:#f59e0b!important;stroke-width:4px!important;filter:drop-shadow(0 0 6px rgba(245,158,11,0.7))}
.node-item.search-dim{opacity:0.25;transition:opacity 0.2s ease}
.minimap-node.search-match{stroke:#f59e0b!important;stroke-width:2px!important;r:3.5px!important}
.minimap-node.search-dim{opacity:0.25!important}
</style><main><h1>Riwayat cabang</h1><p>Pratinjau lokal. Dokumen bersama tidak diubah.</p>
<button id="outside">Kontrol di luar riwayat</button>
<section aria-label="Navigasi riwayat"><button id="undo">Kembali ke induk</button>
<p id="status" role="status" aria-live="polite" aria-atomic="true"></p>
<h2>Topologi Cabang (Visual DAG)</h2>
<div id="dag-search-bar" class="dag-search-omnibar" role="search" aria-label="Pencarian Simpul DAG"><input type="search" id="dag-search-input" class="dag-search-input" placeholder="Cari simpul (ID atau diff)..." aria-label="Cari simpul"><span id="dag-search-count" class="dag-search-count" aria-live="polite"></span><button type="button" id="dag-search-clear" class="dag-search-clear-btn" aria-label="Hapus pencarian">Batal</button></div>
<nav id="dag-breadcrumbs" class="dag-breadcrumbs-bar" aria-label="Jejak silsilah cabang"></nav>
<div id="dag-view" class="dag-container">''' + svg_topo + '''<div id="dag-diff-popover" class="diff-popover" role="tooltip" aria-hidden="true"></div></div><div id="dag-minimap-wrap" class="dag-minimap-container" aria-label="Radar Mini-Map"><div class="dag-minimap-header"><span>RADAR MINI-MAP</span><div style="display:flex;align-items:center;gap:6px"><span id="dag-minimap-status">100%</span><div id="dag-minimap-scale-controls" class="dag-minimap-scale-group" role="group" aria-label="Skala Mini-Map"><button type="button" class="dag-minimap-scale-btn active" data-scale="1" aria-pressed="true">1x</button><button type="button" class="dag-minimap-scale-btn" data-scale="1.5" aria-pressed="false">1.5x</button><button type="button" class="dag-minimap-scale-btn" data-scale="2" aria-pressed="false">2x</button></div><button type="button" id="dag-minimap-toggle" class="dag-minimap-toggle-btn" aria-label="Kecilkan atau buka Radar Mini-Map" aria-expanded="true">Tutup</button></div></div><div id="dag-minimap-radar" class="dag-minimap-radar">''' + manifest.get('svg_minimap', '') + '''</div></div>
''' + legend + '''<h2>Pilih cabang lanjutan</h2><div id="branches"></div>
<h2>Isi pratinjau</h2><pre id="preview"></pre></section></main>
<script type="application/json" id="history-data">''' + data + '''</script><script>''' + script + '''</script></html>'''


if __name__ == '__main__':
    import sys
    history = BranchHistory({'A1': 'awal'})
    history.commit('alpha', 'root', {'A1': 'versi alpha'}, activate=False)
    history.commit('beta', 'root', {'A1': 'versi beta'}, activate=False)
    history.commit('alpha-child', 'alpha', {'B1': 'lanjutan'}, activate=False)
    Path(sys.argv[1]).write_text(render(history))
