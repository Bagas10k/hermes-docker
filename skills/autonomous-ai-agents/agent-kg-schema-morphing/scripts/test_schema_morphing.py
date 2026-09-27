import unittest
import time
from scripts.schema_morphing_engine import KnowledgeGraphSchemaEngine

class TestKGSchemaMorphing(unittest.TestCase):
    def setUp(self):
        self.engine = KnowledgeGraphSchemaEngine()

    def test_active_schema_query(self):
        schema = self.engine.get_active_schema()
        self.assertEqual(schema["version"], 1)
        self.assertIn("Agent", schema["entity_types"])
        self.assertIn("EXECUTES", schema["relation_types"])

    def test_disjointness_and_domain_range_veto(self):
        schema = self.engine.get_active_schema()
        # Invalid domain: Resource cannot EXECUTE Task
        ok, err = self.engine.check_ontological_compatibility(schema, "Resource", "EXECUTES", "Task")
        self.assertFalse(ok)
        self.assertIn("Domain mismatch", err)

        # Invalid range: Agent cannot EXECUTE Resource
        ok, err = self.engine.check_ontological_compatibility(schema, "Agent", "EXECUTES", "Resource")
        self.assertFalse(ok)
        self.assertIn("Range mismatch", err)

        # Disjoint violation directly
        ok, err = self.engine.check_ontological_compatibility(schema, "Agent", "USES", "Agent")
        self.assertFalse(ok)

    def test_dynamic_edge_reweighting(self):
        self.engine.graph["edges"].append({
            "source": "A1",
            "target": "T1",
            "relation": "EXECUTES",
            "weight": 0.5,
            "evidence_count": 1,
            "updated_at": 1000.0
        })
        # After 1 day (86400s), decay is 0.5, new utility is 1.0
        edge = self.engine.reweight_edge(0, utility_observed=1.0, current_time=1000.0 + 86400.0)
        self.assertGreater(edge["weight"], 0.5)
        self.assertEqual(edge["evidence_count"], 2)

    def test_double_buffered_schema_morphism(self):
        # Stage new relation
        v, staged = self.engine.stage_schema_morphism("ADD_RELATION", {
            "relation": "COLLABORATES_WITH",
            "domain": "Agent",
            "range": "Agent",
            "inverse": "COLLABORATES_WITH"
        })
        self.assertEqual(v, 2)
        # Active schema should still be version 1
        self.assertEqual(self.engine.active_schema_version, 1)

        # Commit morphism
        commit_info = self.engine.commit_schema_morphism(2)
        self.assertEqual(self.engine.active_schema_version, 2)
        self.assertIn("COLLABORATES_WITH", self.engine.get_active_schema()["relation_types"])

    def test_relation_merging_migration(self):
        self.engine.graph["entities"] = {
            "a": {"type": "Agent"},
            "t": {"type": "Task"}
        }
        self.engine.graph["edges"] = [
            {"source": "a", "target": "t", "relation": "EXECUTES", "weight": 0.9}
        ]
        # Stage merge
        v, staged = self.engine.stage_schema_morphism("MERGE_RELATIONS", {
            "source_relations": ["EXECUTES"],
            "target_relation": "PERFORMS",
            "domain": "Agent",
            "range": "Task"
        })
        self.engine.commit_schema_morphism(v)
        active_edges = self.engine.graph["edges"]
        self.assertEqual(len(active_edges), 1)
        self.assertEqual(active_edges[0]["relation"], "PERFORMS")
        self.assertEqual(active_edges[0]["original_relation"], "EXECUTES")

if __name__ == "__main__":
    unittest.main()
