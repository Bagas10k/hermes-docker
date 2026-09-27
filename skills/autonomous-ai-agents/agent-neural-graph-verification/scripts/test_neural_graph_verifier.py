"""
Deterministic Unit Tests for Neural Graph Verifier
Verifies:
1. Triplet extraction from markdown wikilinks, directed arrows, and verb phrases.
2. Bidirectional wikilink audit (identifies symmetric links vs unidirectional references).
3. Orphan node detection (detects disconnected nodes accurately).
4. Spurious cycle elimination (prunes redundant self-referential tautological loops).
5. 3D Neural Graph layout synthesis (hub clustering, golden angle distribution, valid 3D coordinates).
"""

import unittest
import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from neural_graph_verifier import NeuralGraphVerificationEngine, Triplet

class TestNeuralGraphVerifier(unittest.TestCase):
    def setUp(self):
        self.engine = NeuralGraphVerificationEngine()

    def test_01_triplet_extraction(self):
        sample_doc = """
        # Note on Architecture
        This module links to [[SYSTEM/KNOWLEDGE_ENGINE]] and [[KNOWLEDGE/INDEX]].
        Frontend -> Backend
        Agent implements TaskRunner
        [[AgentA]] --orchestrates--> [[AgentB]]
        """
        triplets = self.engine.extract_triplets_from_text(sample_doc, source_doc="DocArchitecture")
        
        preds = {t.predicate for t in triplets}
        self.assertIn("references", preds)
        self.assertIn("implements", preds)
        self.assertIn("orchestrates", preds)
        
        # Verify wikilink target
        targets = [t.object for t in triplets if t.predicate == "references"]
        self.assertIn("SYSTEM/KNOWLEDGE_ENGINE", targets)
        self.assertIn("KNOWLEDGE/INDEX", targets)

    def test_02_bidirectional_wikilink_verification(self):
        triplets = [
            Triplet(subject="NodeA", predicate="references", object="NodeB"),
            Triplet(subject="NodeB", predicate="references", object="NodeA"),
            Triplet(subject="NodeA", predicate="references", object="NodeC"),
        ]
        self.engine.build_graph(known_nodes=["NodeA", "NodeB", "NodeC"], triplets=triplets)
        
        audit = self.engine.verify_bidirectional_wikilinks()
        self.assertEqual(audit["symmetric_pairs_count"], 1) # NodeA <-> NodeB
        self.assertEqual(audit["unidirectional_count"], 1)   # NodeA -> NodeC
        self.assertEqual(audit["unidirectional_details"][0]["source"], "NodeA")
        self.assertEqual(audit["unidirectional_details"][0]["target"], "NodeC")

    def test_03_orphan_node_detection(self):
        known = ["Connected1", "Connected2", "Orphan1", "Orphan2"]
        triplets = [
            Triplet(subject="Connected1", predicate="relates_to", object="Connected2")
        ]
        self.engine.build_graph(known_nodes=known, triplets=triplets)
        
        orphans = self.engine.detect_orphan_nodes()
        self.assertEqual(orphans, ["Orphan1", "Orphan2"])

    def test_04_spurious_cycle_elimination(self):
        # Mutual tautological relation with relates_to
        triplets = [
            Triplet(subject="ConceptA", predicate="relates_to", object="ConceptB"),
            Triplet(subject="ConceptB", predicate="relates_to", object="ConceptA"),
            Triplet(subject="ConceptA", predicate="depends_on", object="ConceptC"),
        ]
        self.engine.build_graph(known_nodes=["ConceptA", "ConceptB", "ConceptC"], triplets=triplets)
        
        spurious = self.engine.eliminate_spurious_cycles()
        self.assertEqual(len(spurious), 1)
        self.assertIn(("ConceptB", "ConceptA"), spurious)
        
        # Verify edge status
        active_edges = [e for e in self.engine.edges if not e.is_spurious]
        self.assertEqual(len(active_edges), 2)

    def test_05_3d_neural_graph_synthesis(self):
        known = ["Hub1", "Node1", "Node2", "Node3", "OrphanA"]
        triplets = [
            Triplet(subject="Hub1", predicate="calls", object="Node1"),
            Triplet(subject="Hub1", predicate="calls", object="Node2"),
            Triplet(subject="Hub1", predicate="calls", object="Node3"),
            Triplet(subject="Node1", predicate="calls", object="Hub1"),
        ]
        self.engine.build_graph(known_nodes=known, triplets=triplets)
        graph_3d = self.engine.synthesize_3d_coordinates()
        
        self.assertEqual(graph_3d["node_count"], 5)
        self.assertEqual(graph_3d["orphan_count"], 1)
        
        # Check hub node
        hub_node = next(n for n in graph_3d["nodes"] if n["id"] == "Hub1")
        self.assertEqual(hub_node["cluster"], "hub")
        self.assertLess(math.sqrt(hub_node["x"]**2 + hub_node["y"]**2 + hub_node["z"]**2), 150.0)
        
        # Check orphan node coordinates
        orphan_node = next(n for n in graph_3d["nodes"] if n["id"] == "OrphanA")
        self.assertEqual(orphan_node["cluster"], "orphan")
        self.assertAlmostEqual(orphan_node["y"], 0.0)

if __name__ == "__main__":
    unittest.main()
