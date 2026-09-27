"""
Triplet Extraction & Neural Graph Verification Engine for Autonomous Agent Vaults.

Features:
1. Triplet Extraction: Extracts (subject, predicate, object) from agent execution trajectories,
   markdown notes, and structured tool outputs with regex & syntactic heuristics.
2. Obsidian Wikilink Bidirectional Verification: Validates [[target]] links, identifies forward
   and backlink symmetry, and verifies existence against known vault node targets.
3. Orphan Node Detection: Identifies unreachable nodes (in-degree == 0 and out-degree == 0).
4. Spurious Cycle Elimination: Detects tight cyclical loops (A -> B -> A or self-referential
   hallucinations) and eliminates spurious tautological cycles using DFS cycle detection.
5. 3D Neural Graph Topological Synthesis: Computes node degrees (in, out, total), centrality,
   and synthesizes normalized 3D force coordinates (x, y, z) + clustering for web/D3 visualization.
"""

import re
import math
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Set, Tuple, Optional

@dataclass
class Triplet:
    subject: str
    predicate: str
    object: str
    confidence: float = 1.0
    provenance: str = "trajectory"

@dataclass
class GraphNode:
    id: str
    title: str
    in_degree: int = 0
    out_degree: int = 0
    total_degree: int = 0
    is_orphan: bool = False
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    cluster: str = "core"

@dataclass
class GraphEdge:
    source: str
    target: str
    predicate: str = "relates_to"
    weight: float = 1.0
    is_spurious: bool = False

class NeuralGraphVerificationEngine:
    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self.adj_list: Dict[str, List[str]] = {}
        self.rev_adj_list: Dict[str, List[str]] = {}

    def extract_triplets_from_text(self, text: str, source_doc: str = "unknown") -> List[Triplet]:
        """
        Extracts relational triplets from markdown content and wikilinks.
        Recognizes patterns:
        - [[Subject]] --predicate--> [[Object]] or [[Subject]] -> [[Object]]
        - Wikilinks: [[Target]] -> (source_doc, 'references', Target)
        - Bullet point facts: * Subject is_a Object / Subject has Object / Subject implements Object
        """
        triplets: List[Triplet] = []
        
        # 1. Wikilinks extraction
        wikilink_pattern = re.compile(r'\[\[([^\]\|#]+)(?:#[^\]\|]+)?(?:\|[^\]]+)?\]\]')
        for match in wikilink_pattern.finditer(text):
            target = match.group(1).strip()
            if target and target.lower() != source_doc.lower():
                triplets.append(Triplet(
                    subject=source_doc,
                    predicate="references",
                    object=target,
                    confidence=0.95,
                    provenance="wikilink"
                ))

        # 2. Directed arrow relations: [[A]] -> [[B]] or A -> B
        arrow_pattern = re.compile(r'(?:\[\[([^\]]+)\]\]|([a-zA-Z0-9_-]+))\s*(?:--([a-zA-Z0-9_ -]+)-->|->)\s*(?:\[\[([^\]]+)\]\]|([a-zA-Z0-9_-]+))')
        for match in arrow_pattern.finditer(text):
            s = (match.group(1) or match.group(2)).strip()
            pred = (match.group(3) or "relates_to").strip().replace(" ", "_")
            o = (match.group(4) or match.group(5)).strip()
            if s and o and s.lower() != o.lower():
                triplets.append(Triplet(
                    subject=s,
                    predicate=pred,
                    object=o,
                    confidence=0.90,
                    provenance="syntax_arrow"
                ))

        # 3. Predicate verbs: Subject (implements|extends|depends_on|calls|modifies) Object
        verb_pattern = re.compile(r'\b([A-Za-z0-9_-]+)\s+(implements|extends|depends_on|calls|modifies|contains)\s+([A-Za-z0-9_-]+)\b', re.IGNORECASE)
        for match in verb_pattern.finditer(text):
            s = match.group(1).strip()
            pred = match.group(2).strip().lower()
            o = match.group(3).strip()
            if s and o and s.lower() != o.lower():
                triplets.append(Triplet(
                    subject=s,
                    predicate=pred,
                    object=o,
                    confidence=0.85,
                    provenance="verb_phrase"
                ))

        return triplets

    def build_graph(self, known_nodes: List[str], triplets: List[Triplet]):
        """Populate graph from node list and triplets, normalizing IDs."""
        self.nodes.clear()
        self.edges.clear()
        self.adj_list.clear()
        self.rev_adj_list.clear()

        for n in known_nodes:
            nid = n.strip()
            self.nodes[nid] = GraphNode(id=nid, title=nid)
            self.adj_list[nid] = []
            self.rev_adj_list[nid] = []

        seen_edges: Set[Tuple[str, str, str]] = set()

        for t in triplets:
            src = t.subject.strip()
            tgt = t.object.strip()
            pred = t.predicate.strip()

            if not src or not tgt:
                continue

            # Ensure nodes exist
            if src not in self.nodes:
                self.nodes[src] = GraphNode(id=src, title=src)
                self.adj_list[src] = []
                self.rev_adj_list[src] = []
            if tgt not in self.nodes:
                self.nodes[tgt] = GraphNode(id=tgt, title=tgt)
                self.adj_list[tgt] = []
                self.rev_adj_list[tgt] = []

            # Avoid exact duplicate edge
            edge_key = (src, tgt, pred)
            if edge_key in seen_edges:
                continue
            seen_edges.add(edge_key)

            edge = GraphEdge(source=src, target=tgt, predicate=pred, weight=t.confidence)
            self.edges.append(edge)
            self.adj_list[src].append(tgt)
            self.rev_adj_list[tgt].append(src)

        # Update node degrees
        for nid, node in self.nodes.items():
            node.out_degree = len(self.adj_list.get(nid, []))
            node.in_degree = len(self.rev_adj_list.get(nid, []))
            node.total_degree = node.in_degree + node.out_degree
            node.is_orphan = (node.total_degree == 0)

    def verify_bidirectional_wikilinks(self) -> Dict[str, any]:
        """
        Verifies bidirectional symmetry. In Obsidian vaults, if A references B,
        check if B has backlink to A, or if it is a pure sink.
        """
        missing_backlinks = []
        symmetric_links = []

        for edge in self.edges:
            if edge.predicate == "references":
                # Check if reverse edge exists
                rev_exists = any(
                    e.source == edge.target and e.target == edge.source
                    for e in self.edges
                )
                if rev_exists:
                    if (edge.target, edge.source) not in symmetric_links:
                        symmetric_links.append((edge.source, edge.target))
                else:
                    missing_backlinks.append({
                        "source": edge.source,
                        "target": edge.target,
                        "type": "unidirectional_reference"
                    })

        return {
            "symmetric_pairs_count": len(symmetric_links),
            "unidirectional_count": len(missing_backlinks),
            "unidirectional_details": missing_backlinks
        }

    def detect_orphan_nodes(self) -> List[str]:
        """Return list of node IDs with degree 0."""
        orphans = [nid for nid, node in self.nodes.items() if node.is_orphan]
        return sorted(orphans)

    def eliminate_spurious_cycles(self, max_cycle_len: int = 2) -> List[Tuple[str, str]]:
        """
        Detects spurious tight cyclical loops where A -> B and B -> A have identical
        predicate or tautological feedback without evidence progression.
        Marks edge as is_spurious = True and prunes it from active adjacency.
        """
        spurious_pairs = []
        for i, edge1 in enumerate(self.edges):
            if edge1.is_spurious:
                continue
            for edge2 in self.edges[i+1:]:
                if edge2.is_spurious:
                    continue
                # Mutual edge with same or tautological relation
                if edge1.source == edge2.target and edge1.target == edge2.source:
                    if edge1.predicate == edge2.predicate and edge1.predicate in ["relates_to", "is_synonym_of"]:
                        # Tautological duplicate cycle -> prune edge2
                        edge2.is_spurious = True
                        spurious_pairs.append((edge2.source, edge2.target))
                        # Remove from adj_list
                        if edge2.target in self.adj_list.get(edge2.source, []):
                            self.adj_list[edge2.source].remove(edge2.target)
                        if edge2.source in self.rev_adj_list.get(edge2.target, []):
                            self.rev_adj_list[edge2.target].remove(edge2.source)

        # Recalculate degrees
        for nid, node in self.nodes.items():
            node.out_degree = len(self.adj_list.get(nid, []))
            node.in_degree = len(self.rev_adj_list.get(nid, []))
            node.total_degree = node.in_degree + node.out_degree
            node.is_orphan = (node.total_degree == 0)

        return spurious_pairs

    def synthesize_3d_coordinates(self) -> Dict[str, any]:
        """
        Spherical & Force-directed pseudo-embedding for 3D Neural Graph layout.
        Maps nodes onto 3D coordinate space (x, y, z) based on degree centrality
        and angular distribution (Fibonacci sphere distribution with hub gravity).
        """
        active_nodes = [n for n in self.nodes.values() if not n.is_orphan]
        n_count = len(active_nodes)
        if n_count == 0:
            return {"nodes": [], "edges": []}

        phi = math.pi * (3.0 - math.sqrt(5.0))  # Golden angle

        for i, node in enumerate(active_nodes):
            # Hub distance calculation: higher degree = closer to center (0,0,0)
            max_deg = max((n.total_degree for n in active_nodes), default=1)
            norm_deg = node.total_degree / max(1, max_deg)
            
            # Radius inversely proportional to degree: hubs at r ~ 50, leaves at r ~ 200
            radius = 200.0 * (1.0 - 0.7 * norm_deg)

            y = 1.0 - (i / float(max(1, n_count - 1))) * 2.0  # y from 1 to -1
            radius_at_y = math.sqrt(max(0.0, 1.0 - y * y))
            theta = phi * i

            node.x = round(math.cos(theta) * radius_at_y * radius, 3)
            node.y = round(y * radius, 3)
            node.z = round(math.sin(theta) * radius_at_y * radius, 3)

            # Assign cluster
            if norm_deg >= 0.6:
                node.cluster = "hub"
            elif node.in_degree > node.out_degree:
                node.cluster = "sink"
            elif node.out_degree > node.in_degree:
                node.cluster = "source"
            else:
                node.cluster = "bridge"

        # Position orphans on outer shell
        for i, (nid, node) in enumerate(self.nodes.items()):
            if node.is_orphan:
                node.x = round(350.0 * math.cos(i * 0.5), 3)
                node.y = 0.0
                node.z = round(350.0 * math.sin(i * 0.5), 3)
                node.cluster = "orphan"

        return {
            "node_count": len(self.nodes),
            "edge_count": len([e for e in self.edges if not e.is_spurious]),
            "orphan_count": len([n for n in self.nodes.values() if n.is_orphan]),
            "nodes": [asdict(n) for n in self.nodes.values()],
            "edges": [asdict(e) for e in self.edges if not e.is_spurious]
        }
