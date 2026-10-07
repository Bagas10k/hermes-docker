"""Visual DAG branch topology SVG rendering and branch pruning mechanics.

Pure deterministic SVG generation and branch pruning for BranchHistory.
Invariants:
- Active cursor ancestor path is IMMUTABLE and protected against pruning.
- Root node is protected against pruning.
- Branch pruning eliminates abandoned disconnected subtrees and reclaims node capacity.
- Zero external dependencies (stdlib only). Zero DOM mutations or side-effects.
"""
from typing import Dict, Any, List, Set, Tuple, Optional
import json
from collections import deque
import xml.etree.ElementTree as ET


def compute_node_diff(history, node_id: str) -> Dict[str, Any]:
    """
    Compute diff metrics between node_id and its parent node in BranchHistory.
    
    Returns:
        {
            'added': int,       # keys present in node but not in parent
            'deleted': int,     # keys present in parent but not in node
            'modified': int,    # keys present in both with different values
            'total_mutations': int, # added + deleted + modified
            'badge_text': str   # e.g., '+2 -1', '+1 ~2', or '0'
        }
    """
    if history is None or not hasattr(history, '_nodes'):
        raise ValueError('Invalid BranchHistory instance')
    if node_id not in history._nodes:
        raise KeyError(f'Node {node_id} not found in history')
        
    node = history._nodes[node_id]
    parent_id = node.parent
    if parent_id is None or parent_id not in history._nodes:
        # Root node has no parent mutations
        return {
            'added': 0,
            'deleted': 0,
            'modified': 0,
            'total_mutations': 0,
            'badge_text': '0'
        }
        
    parent_node = history._nodes[parent_id]
    curr_cells = node.state
    parent_cells = parent_node.state
    
    curr_keys = set(curr_cells.keys())
    parent_keys = set(parent_cells.keys())
    
    added = len(curr_keys - parent_keys)
    deleted = len(parent_keys - curr_keys)
    common_keys = curr_keys & parent_keys
    modified = sum(1 for k in common_keys if curr_cells[k] != parent_cells[k])
    total = added + deleted + modified
    
    parts = []
    if added > 0:
        parts.append(f'+{added}')
    if modified > 0:
        parts.append(f'~{modified}')
    if deleted > 0:
        parts.append(f'-{deleted}')
        
    badge_text = ' '.join(parts) if parts else '0'
    return {
        'added': added,
        'deleted': deleted,
        'modified': modified,
        'total_mutations': total,
        'badge_text': badge_text
    }


def compute_node_diff_details(history, node_id: str) -> Dict[str, Any]:
    """
    Compute fine-grained diff mutations (added, deleted, modified keys)
    between node_id and its parent node in BranchHistory.
    
    Returns:
        {
            'added': Dict[str, Any],     # key -> new_val
            'deleted': Dict[str, Any],   # key -> old_val
            'modified': Dict[str, Dict[str, Any]], # key -> {'old': old_val, 'new': new_val}
            'total_mutations': int,
            'parent': Optional[str],
            'summary': str
        }
    """
    if history is None or not hasattr(history, '_nodes'):
        raise ValueError('Invalid BranchHistory instance')
    if node_id not in history._nodes:
        raise KeyError(f'Node {node_id} not found in history')
        
    node = history._nodes[node_id]
    parent_id = node.parent
    if parent_id is None or parent_id not in history._nodes:
        return {
            'added': {},
            'deleted': {},
            'modified': {},
            'total_mutations': 0,
            'parent': None,
            'summary': 'Root revision'
        }
        
    parent_node = history._nodes[parent_id]
    curr_cells = node.state
    parent_cells = parent_node.state
    
    curr_keys = set(curr_cells.keys())
    parent_keys = set(parent_cells.keys())
    
    added = {k: curr_cells[k] for k in sorted(curr_keys - parent_keys)}
    deleted = {k: parent_cells[k] for k in sorted(parent_keys - curr_keys)}
    common_keys = curr_keys & parent_keys
    modified = {
        k: {'old': parent_cells[k], 'new': curr_cells[k]}
        for k in sorted(common_keys)
        if curr_cells[k] != parent_cells[k]
    }
    
    total = len(added) + len(deleted) + len(modified)
    
    parts = []
    if added:
        parts.append(f'+{len(added)}')
    if modified:
        parts.append(f'~{len(modified)}')
    if deleted:
        parts.append(f'-{len(deleted)}')
    summary = ' '.join(parts) if parts else '0'
    
    return {
        'added': added,
        'deleted': deleted,
        'modified': modified,
        'total_mutations': total,
        'parent': parent_id,
        'summary': summary
    }


def format_diff_tooltip_text(diff_details: Dict[str, Any], max_items: int = 5) -> str:
    """Format human-readable single/multi-line diff summary for node title / popover."""
    if not diff_details or diff_details.get('total_mutations', 0) == 0:
        return 'Root revision (no parent mutations)'
    
    lines = []
    parent = diff_details.get('parent', '?')
    lines.append(f"Changes from {parent} ({diff_details.get('summary', '')}):")
    
    count = 0
    for k, v in diff_details.get('added', {}).items():
        if count >= max_items: break
        lines.append(f"  + {k}: {v}")
        count += 1
    for k, info in diff_details.get('modified', {}).items():
        if count >= max_items: break
        lines.append(f"  ~ {k}: {info['old']} -> {info['new']}")
        count += 1
    for k, v in diff_details.get('deleted', {}).items():
        if count >= max_items: break
        lines.append(f"  - {k} (was {v})")
        count += 1
        
    remaining = diff_details.get('total_mutations', 0) - count
    if remaining > 0:
        lines.append(f"  ... and {remaining} more")
        
    return "\n".join(lines)


def prune_abandoned_branches(
    history,
    *,
    protected_nodes: Optional[Set[str]] = None,
    max_retained_nodes: Optional[int] = None
) -> Tuple[int, Set[str]]:
    """
    Prune unreferenced/abandoned branch subtrees from BranchHistory.
    
    Protected by invariant:
    1. 'root' node is ALWAYS protected.
    2. Current active cursor and all its ancestors are ALWAYS protected.
    3. Any explicitly passed protected_nodes (and their ancestors) are protected.
    
    If max_retained_nodes is specified and total nodes exceed it,
    prunes candidate non-protected leaves/subtrees (in FIFO or furthest branch order)
    until node count <= max_retained_nodes.
    
    Returns:
        (pruned_count, set_of_pruned_node_ids)
    """
    if history is None or not hasattr(history, '_nodes'):
        raise ValueError('Invalid BranchHistory instance')
    
    # Compute immutable protected set: root + cursor path + explicit protected
    protected: Set[str] = {'root'}
    
    def _add_lineage(node_id: str):
        curr = node_id
        while curr is not None and curr in history._nodes:
            protected.add(curr)
            curr = history._nodes[curr].parent

    _add_lineage(history.cursor)
    
    if protected_nodes:
        for p in protected_nodes:
            if p in history._nodes:
                _add_lineage(p)
                
    # Candidate nodes that are NOT in protected lineage
    all_nodes = set(history._nodes.keys())
    prunable_candidates = all_nodes - protected
    
    if not prunable_candidates:
        return 0, set()
        
    nodes_to_prune: Set[str] = set()
    
    if max_retained_nodes is not None:
        if type(max_retained_nodes) is not int or max_retained_nodes < 1:
            raise ValueError('max_retained_nodes must be positive integer')
        # Only prune if we exceed budget
        excess = len(history._nodes) - max_retained_nodes
        if excess <= 0:
            return 0, set()
            
        # Target pruning subtrees bottom-up (leaves first)
        # Sort candidates by depth descending to prune cleanly
        def _get_depth(n: str) -> int:
            d = 0
            curr = n
            while curr != 'root' and curr in history._nodes and history._nodes[curr].parent is not None:
                d += 1
                curr = history._nodes[curr].parent
            return d
            
        sorted_candidates = sorted(prunable_candidates, key=lambda n: _get_depth(n), reverse=True)
        nodes_to_prune = set(sorted_candidates[:excess])
    else:
        # Prune all abandoned candidates
        nodes_to_prune = prunable_candidates

    # If a node is pruned, all its descendants MUST also be pruned to maintain tree integrity
    def _collect_descendants(n: str, acc: Set[str]):
        acc.add(n)
        for child in history._children.get(n, set()):
            _collect_descendants(child, acc)

    final_pruned: Set[str] = set()
    for n in nodes_to_prune:
        _collect_descendants(n, final_pruned)
        
    # Safety invariant check: NEVER prune any protected node
    final_pruned -= protected
    if not final_pruned:
        return 0, set()
        
    # Execute atomic deletion in history internal structures
    for n in final_pruned:
        parent = history._nodes[n].parent
        if parent is not None and parent in history._children:
            history._children[parent].discard(n)
            
    for n in final_pruned:
        history._nodes.pop(n, None)
        history._children.pop(n, None)
        
    return len(final_pruned), final_pruned


def compute_node_lineage(history, node_id: str) -> List[str]:
    """
    Compute ordered ancestor lineage path from 'root' to target node_id.
    
    Returns list of node keys, e.g. ['root', 'b1', 'b2', 'b3'].
    If node_id is unknown, returns empty list.
    """
    if history is None or not hasattr(history, '_nodes') or node_id not in history._nodes:
        return []
    path = []
    curr = node_id
    while curr is not None and curr in history._nodes:
        path.append(curr)
        curr = history._nodes[curr].parent
    path.reverse()
    return path


def compute_branch_roots(history) -> Dict[str, str]:
    """Stable root-child IDs, independent of palette, insertion order or cursor."""
    roots = {'root': 'root'}
    queue = deque(['root'])
    while queue:
        parent = queue.popleft()
        for child in history.children(parent):
            roots[child] = child if parent == 'root' else roots[parent]
            queue.append(child)
    return roots


def compute_branch_clusters(history) -> Dict[str, str]:
    """
    Compute lineage branch cluster hues for nodes in BranchHistory.
    
    Nodes sharing the same root-origin branch partition inherit consistent,
    harmonized color tokens (Hex hues):
    - Cluster 0: Emerald Mint (#10B981)
    - Cluster 1: Violet Purple (#8B5CF6)
    - Cluster 2: Rose Coral (#F43F5E)
    - Cluster 3: Amber Gold (#F59E0B)
    - Cluster 4: Cyan Sky (#0EA5E9)
    - Root / Fallback: Slate (#94A3B8)
    
    Returns:
        Mapping of node_id -> hex color string.
    """
    if history is None or not hasattr(history, '_nodes'):
        return {}
    
    nodes = history._nodes
    if 'root' not in nodes:
        return {}
        
    palette = [
        '#10B981',  # 0: Emerald
        '#8B5CF6',  # 1: Violet
        '#F43F5E',  # 2: Rose
        '#F59E0B',  # 3: Amber
        '#0EA5E9',  # 4: Cyan
    ]
    
    root_children = sorted(history.children('root'))
    clusters: Dict[str, str] = {'root': '#94A3B8'}
    
    for idx, child in enumerate(root_children):
        color = palette[idx % len(palette)]
        queue = deque([child])
        while queue:
            curr = queue.popleft()
            clusters[curr] = color
            for grand in sorted(history.children(curr)):
                queue.append(grand)
                
    # Fallback for any disconnected nodes
    for n in nodes:
        if n not in clusters:
            clusters[n] = '#94A3B8'
            
    return clusters


def render_dag_minimap_svg(
    history,
    *,
    map_width: int = 180,
    map_height: int = 90,
    col_spacing: int = 120,
    row_spacing: int = 50,
    padding: int = 40
) -> str:
    """
    Generate miniature proportional SVG radar minimap of the BranchHistory DAG.
    
    Contains:
    - Background radar backdrop (<rect class="minimap-bg">).
    - Lightweight miniature branch edges (<path class="minimap-edge">).
    - Miniature node dots (<circle class="minimap-node">) with active cursor highlight,
      color-coded branch cluster hue, and search match pulsing indicators.
    - Dynamic draggable viewport indicator frame (<rect id="minimap-viewport-frame" class="minimap-viewport-rect">).
    - Exposes data-world-width and data-world-height attributes for client-side viewport pan synchronization.
    """
    if history is None or not hasattr(history, '_nodes'):
        raise ValueError('Invalid BranchHistory instance')
        
    nodes = history._nodes
    cursor = history.cursor
    clusters = compute_branch_clusters(history)
    branch_roots = compute_branch_roots(history)
    
    depths: Dict[str, int] = {'root': 0}
    def _assign_depths(n: str, d: int):
        depths[n] = d
        for child in sorted(history.children(n)):
            _assign_depths(child, d + 1)
    _assign_depths('root', 0)
    
    y_positions: Dict[str, float] = {}
    next_y = 0.0
    def _assign_y(n: str) -> float:
        nonlocal next_y
        children = sorted(history.children(n))
        if not children:
            y = next_y
            next_y += 1.0
            y_positions[n] = y
            return y
        child_ys = [_assign_y(c) for c in children]
        y = sum(child_ys) / len(child_ys)
        y_positions[n] = y
        return y
    _assign_y('root')
    
    max_depth = max(depths.values()) if depths else 0
    max_y_idx = max(y_positions.values()) if y_positions else 0.0
    node_radius = 18
    world_width = int(padding * 2 + max_depth * col_spacing + node_radius * 2)
    world_height = int(padding * 2 + max_y_idx * row_spacing + node_radius * 2)
    if world_width < 300: world_width = 300
    if world_height < 160: world_height = 160
    
    scale_x = map_width / world_width
    scale_y = map_height / world_height
    
    svg = ET.Element('svg', {
        'xmlns': 'http://www.w3.org/2000/svg',
        'viewBox': f'0 0 {map_width} {map_height}',
        'width': str(map_width),
        'height': str(map_height),
        'role': 'img',
        'aria-label': 'DAG Mini-Map Radar',
        'class': 'dag-minimap-svg',
        'data-world-width': str(world_width),
        'data-world-height': str(world_height),
        'data-scale-x': f"{scale_x:.5f}",
        'data-scale-y': f"{scale_y:.5f}"
    })
    
    title = ET.SubElement(svg, 'title')
    title.text = 'DAG Mini-Map Radar'
    
    defs = ET.SubElement(svg, 'defs')
    style = ET.SubElement(defs, 'style')
    style.text = """
        .minimap-bg { fill: #0F172A; rx: 6px; ry: 6px; opacity: 0.92; }
        .minimap-edge { stroke: #475569; stroke-width: 1.2px; fill: none; }
        .minimap-edge.active { stroke: #38BDF8; stroke-width: 1.8px; }
        .minimap-node { fill: #94A3B8; stroke: #0F172A; stroke-width: 0.8px; transition: all 0.2s; }
        .minimap-node.active { fill: #38BDF8; stroke: #FFFFFF; stroke-width: 1.4px; }
        .minimap-node.search-match { stroke: #F59E0B !important; stroke-width: 1.8px !important; }
        .minimap-node.search-dim { opacity: 0.2; }
        .minimap-viewport-rect { fill: rgba(56, 189, 248, 0.15); stroke: #38BDF8; stroke-width: 1.5px; rx: 3px; ry: 3px; cursor: grab; }
        .minimap-viewport-rect:active { cursor: grabbing; stroke: #F59E0B; }
    """
    
    ET.SubElement(svg, 'rect', {
        'width': str(map_width),
        'height': str(map_height),
        'class': 'minimap-bg'
    })
    
    # Active path
    active_path: Set[str] = set()
    curr = cursor
    while curr is not None and curr in nodes:
        active_path.add(curr)
        curr = nodes[curr].parent
        
    coords: Dict[str, Tuple[float, float]] = {}
    for n in nodes:
        wx = padding + depths.get(n, 0) * col_spacing + node_radius
        wy = padding + y_positions.get(n, 0.0) * row_spacing + node_radius
        coords[n] = (wx * scale_x, wy * scale_y)
        
    edges_g = ET.SubElement(svg, 'g', {'class': 'minimap-edges'})
    for n, node_data in nodes.items():
        parent = node_data.parent
        if parent is not None and parent in coords:
            x1, y1 = coords[parent]
            x2, y2 = coords[n]
            is_active = (parent in active_path and n in active_path)
            dx = (x2 - x1) / 2
            path_d = f"M {x1:.1f} {y1:.1f} C {x1 + dx:.1f} {y1:.1f}, {x2 - dx:.1f} {y2:.1f}, {x2:.1f} {y2:.1f}"
            ET.SubElement(edges_g, 'path', {
                'd': path_d,
                'class': 'minimap-edge active' if is_active else 'minimap-edge'
            })
            
    nodes_g = ET.SubElement(svg, 'g', {'class': 'minimap-nodes'})
    for n in sorted(nodes.keys()):
        mx, my = coords[n]
        is_cursor = (n == cursor)
        cluster_color = clusters.get(n, '#94A3B8')
        node_elem_attrs = {
            'cx': f"{mx:.1f}",
            'cy': f"{my:.1f}",
            'r': '3' if is_cursor else '2',
            'class': 'minimap-node active' if is_cursor else 'minimap-node',
            'data-node': n,
            'data-cluster-color': cluster_color,
            'data-branch-root': branch_roots[n],
            'aria-label': f'Node {n}; branch root {branch_roots[n]}',
            'style': f"fill: {cluster_color};" if not is_cursor else "fill: #38BDF8;"
        }
        ET.SubElement(nodes_g, 'circle', node_elem_attrs)
        
    # Draggable viewport indicator rectangle
    # Default initial width proportional to standard 400px view
    init_vw = min(map_width, max(24, int(400 * scale_x)))
    init_vh = min(map_height, max(18, int(world_height * scale_y)))
    ET.SubElement(svg, 'rect', {
        'id': 'minimap-viewport-frame',
        'x': '0',
        'y': '0',
        'width': str(init_vw),
        'height': str(init_vh),
        'class': 'minimap-viewport-rect'
    })
    
    return ET.tostring(svg, encoding='unicode')


def render_dag_svg(
    history,
    *,
    node_radius: int = 18,
    col_spacing: int = 120,
    row_spacing: int = 50,
    padding: int = 40,
    show_diff_badges: bool = True
) -> str:
    """
    Generate deterministic, accessible SVG diagram of the BranchHistory DAG.
    
    Layout:
    - X-axis: Tree depth (Root at col 0, descendants to the right).
    - Y-axis: Topological vertical allocation per branch.
    - Styling: Warm Paper & Obsidian theme (#14120e dark strokes, #1669e8 active cursor, #FAF6EF canvas).
    - Accessibility: <title>, <desc>, aria labels, clean SVG vector math.
    """
    if history is None or not hasattr(history, '_nodes'):
        raise ValueError('Invalid BranchHistory instance')
        
    nodes = history._nodes
    cursor = history.cursor
    
    # 1. Calculate depth & ancestor path
    active_path: Set[str] = set()
    curr = cursor
    while curr is not None and curr in nodes:
        active_path.add(curr)
        curr = nodes[curr].parent

    # 2. Assign tree depth (column)
    depths: Dict[str, int] = {'root': 0}
    
    def _assign_depths(n: str, d: int):
        depths[n] = d
        for child in sorted(history.children(n)):
            _assign_depths(child, d + 1)
            
    _assign_depths('root', 0)
    
    # 3. Assign vertical positions (row) using deterministic layout
    # Post-order traversal or leaf allocation
    y_positions: Dict[str, float] = {}
    next_y = 0.0
    
    def _assign_y(n: str) -> float:
        nonlocal next_y
        children = sorted(history.children(n))
        if not children:
            y = next_y
            next_y += 1.0
            y_positions[n] = y
            return y
        child_ys = [_assign_y(c) for c in children]
        y = sum(child_ys) / len(child_ys)
        y_positions[n] = y
        return y
        
    _assign_y('root')
    
    max_depth = max(depths.values()) if depths else 0
    max_y_idx = max(y_positions.values()) if y_positions else 0.0
    
    width = int(padding * 2 + max_depth * col_spacing + node_radius * 2)
    height = int(padding * 2 + max_y_idx * row_spacing + node_radius * 2)
    if width < 300: width = 300
    if height < 160: height = 160
    
    # 4. Map to pixel coordinates
    coords: Dict[str, Tuple[float, float]] = {}
    for n in nodes:
        cx = padding + depths.get(n, 0) * col_spacing + node_radius
        cy = padding + y_positions.get(n, 0.0) * row_spacing + node_radius
        coords[n] = (cx, cy)
        
    # 5. Build SVG Elements
    svg = ET.Element('svg', {
        'xmlns': 'http://www.w3.org/2000/svg',
        'viewBox': f'0 0 {width} {height}',
        'width': str(width),
        'height': str(height),
        'role': 'img',
        'aria-label': 'Visual DAG Branch Topology',
        'class': 'branch-dag-svg'
    })
    
    title = ET.SubElement(svg, 'title')
    title.text = 'Visual DAG Branch Topology'
    desc = ET.SubElement(svg, 'desc')
    desc.text = f'Branch history tree with {len(nodes)} nodes. Current active cursor is {cursor}.'
    
    # Definitions for arrows / gradients
    defs = ET.SubElement(svg, 'defs')
    style = ET.SubElement(defs, 'style')
    style.text = """
        .edge { stroke: #94A3B8; stroke-width: 2px; fill: none; }
        .edge.active { stroke: #1669E8; stroke-width: 3px; stroke-dasharray: 4,2; }
        .node-circle { fill: #FFFFFF; stroke: #334155; stroke-width: 2px; transition: all 0.2s; cursor: pointer; }
        .node-circle.active { fill: #1669E8; stroke: #0F172A; stroke-width: 3px; }
        .node-circle.path { stroke: #1669E8; stroke-width: 2.5px; }
        .node-label { font-family: ui-monospace, monospace; font-size: 11px; fill: #0F172A; text-anchor: middle; dominant-baseline: central; pointer-events: none; }
        .node-label.active { fill: #FFFFFF; font-weight: bold; }
        .node-item { cursor: pointer; }
        .node-item:focus { outline: none; }
        .node-item:focus .node-circle { stroke: #F59E0B; stroke-width: 3.5px; }
        .diff-badge-rect { fill: #0F172A; rx: 4px; ry: 4px; opacity: 0.85; }
        .diff-badge-text { font-family: ui-monospace, monospace; font-size: 9px; fill: #F8FAFC; text-anchor: middle; dominant-baseline: central; font-weight: 600; }
    """
    
    # Edges layer
    edges_g = ET.SubElement(svg, 'g', {'class': 'edges'})
    for n, node_data in nodes.items():
        parent = node_data.parent
        if parent is not None and parent in coords:
            x1, y1 = coords[parent]
            x2, y2 = coords[n]
            is_active_edge = (parent in active_path and n in active_path)
            edge_class = 'edge active' if is_active_edge else 'edge'
            
            # Cubic bezier curve for smooth horizontal branch split
            dx = (x2 - x1) / 2
            path_d = f"M {x1} {y1} C {x1 + dx} {y1}, {x2 - dx} {y2}, {x2} {y2}"
            ET.SubElement(edges_g, 'path', {
                'd': path_d,
                'class': edge_class,
                'data-parent': parent,
                'data-child': n
            })
            
    # Nodes layer
    nodes_g = ET.SubElement(svg, 'g', {'class': 'nodes'})
    for n in sorted(nodes.keys()):
        cx, cy = coords[n]
        is_cursor = (n == cursor)
        in_path = (n in active_path)
        
        diff_info = compute_node_diff(history, n) if show_diff_badges else None
        diff_details = compute_node_diff_details(history, n) if show_diff_badges else None
        mutations_desc = f", {diff_info['badge_text']} mutations" if diff_info and diff_info['total_mutations'] > 0 else ""
        
        node_class = 'node-circle active' if is_cursor else ('node-circle path' if in_path else 'node-circle')
        label_class = 'node-label active' if is_cursor else 'node-label'
        
        node_attrs = {
            'class': 'node-item',
            'data-node': n,
            'data-cx': f"{cx:.1f}",
            'data-cy': f"{cy:.1f}",
            'tabindex': '0',
            'role': 'button',
            'aria-label': f'Node {n}' + (' (Active Cursor)' if is_cursor else '') + mutations_desc
        }
        if diff_details is not None:
            node_attrs['data-diff-json'] = json.dumps(diff_details, ensure_ascii=True)
            node_attrs['data-summary'] = diff_details.get('summary', '0')
            node_attrs['data-mutations'] = str(diff_details.get('total_mutations', 0))
        
        g = ET.SubElement(nodes_g, 'g', node_attrs)
        
        # Native SVG tooltip title element
        tooltip_title = ET.SubElement(g, 'title')
        tooltip_title.text = format_diff_tooltip_text(diff_details) if diff_details else f"Node {n}"
        
        ET.SubElement(g, 'circle', {
            'cx': f"{cx:.1f}",
            'cy': f"{cy:.1f}",
            'r': str(node_radius),
            'class': node_class
        })
        
        # Display label (abbreviated if long)
        lbl_text = n if len(n) <= 6 else (n[:5] + '…')
        text_el = ET.SubElement(g, 'text', {
            'x': f"{cx:.1f}",
            'y': f"{cy:.1f}",
            'class': label_class
        })
        text_el.text = lbl_text
        
        # Badge metrics overlay if node has mutations from parent
        if show_diff_badges and diff_info and diff_info['total_mutations'] > 0:
            badge_text = diff_info['badge_text']
            # Position badge at top-right of node circle
            bx = cx + node_radius * 0.7
            by = cy - node_radius * 0.7
            badge_w = max(24, len(badge_text) * 6 + 8)
            badge_h = 14
            
            badge_g = ET.SubElement(g, 'g', {
                'class': 'diff-badge',
                'data-badge-node': n,
                'data-mutations': str(diff_info['total_mutations'])
            })
            ET.SubElement(badge_g, 'rect', {
                'x': f"{bx - badge_w / 2:.1f}",
                'y': f"{by - badge_h / 2:.1f}",
                'width': str(badge_w),
                'height': str(badge_h),
                'class': 'diff-badge-rect'
            })
            b_text = ET.SubElement(badge_g, 'text', {
                'x': f"{bx:.1f}",
                'y': f"{by:.1f}",
                'class': 'diff-badge-text'
            })
            b_text.text = badge_text
        
    return ET.tostring(svg, encoding='unicode')
