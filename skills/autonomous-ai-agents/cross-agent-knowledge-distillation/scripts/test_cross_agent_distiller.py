#!/usr/bin/env python3
"""
Unit tests for cross_agent_distiller.py
Validates:
1. Schema rejection for missing agent_id, task_id, or candidate_facts
2. Credential scrubbing (API keys, tokens, bearer, passwords)
3. Noise removal (ANSI escapes, base64 data, progress output)
4. Atomic identity deduction and deduplication (NEW vs DUPLICATE_CORROBORATED)
5. Bayesian confidence updating upon repeated observation
6. Invariant protection: stable predicate conflict quarantine
7. Mutable predicate state superseding with historical archiving
"""

import unittest
import json
from cross_agent_distiller import CrossAgentDistiller, sanitize_text, compute_predicate_hash

class TestCrossAgentDistiller(unittest.TestCase):

    def test_schema_validation_rejection(self):
        distiller = CrossAgentDistiller()
        
        # Missing agent_id
        res1 = distiller.distill_trajectory({"task_id": "T1", "candidate_facts": []})
        self.assertFalse(res1["success"])
        self.assertIn("Missing mandatory 'agent_id'.", res1["rejection_reasons"])

        # Missing task_id
        res2 = distiller.distill_trajectory({"agent_id": "A1", "candidate_facts": []})
        self.assertFalse(res2["success"])
        self.assertIn("Missing mandatory 'task_id'.", res2["rejection_reasons"])

        # Invalid candidate_facts format
        res3 = distiller.distill_trajectory({"agent_id": "A1", "task_id": "T1", "candidate_facts": "not_a_list"})
        self.assertFalse(res3["success"])
        self.assertIn("'candidate_facts' must be a list of atomic statements.", res3["rejection_reasons"])

        # Missing required atomic fact fields
        res4 = distiller.distill_trajectory({
            "agent_id": "A1", "task_id": "T1",
            "candidate_facts": [{"subject": "Server"}]
        })
        self.assertFalse(res4["success"])
        self.assertTrue(any("missing 'predicate'" in r for r in res4["rejection_reasons"]))

    def test_credential_and_noise_scrubbing(self):
        raw_dirty = "\x1b[32mSUCCESS:\x1b[0m api_key: ghp_123456789012345678901234567890123456 data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg== Progress: 50%"
        cleaned = sanitize_text(raw_dirty)
        
        self.assertNotIn("\x1b[32m", cleaned)
        self.assertNotIn("ghp_123456789012345678901234567890123456", cleaned)
        self.assertIn("[REDACTED]", cleaned)
        self.assertNotIn("iVBORw0KGgo", cleaned)
        self.assertIn("[DATA_URI_REDACTED]", cleaned)

    def test_atomic_new_fact_registration(self):
        distiller = CrossAgentDistiller()
        payload = {
            "agent_id": "worker_python",
            "task_id": "inspect_env",
            "candidate_facts": [
                {
                    "subject": "python_runtime",
                    "predicate": "version",
                    "value": "3.11.16",
                    "target_scope": "environment",
                    "relation_mode": "stable",
                    "confidence": 0.95,
                    "observation": "Extracted via sys.version"
                }
            ]
        }
        res = distiller.distill_trajectory(payload)
        self.assertTrue(res["success"])
        self.assertEqual(len(res["distilled_facts"]), 1)
        fact = res["distilled_facts"][0]
        self.assertEqual(fact["action"], "NEW")
        self.assertEqual(fact["subject"], "python_runtime")
        self.assertEqual(fact["value"], "3.11.16")
        self.assertEqual(fact["confidence"], 0.95)
        self.assertEqual(fact["mention_count"], 1)

    def test_bayesian_corroboration_duplicate(self):
        existing = [{
            "predicate_id": compute_predicate_hash("redis_server", "port", "network"),
            "subject": "redis_server",
            "predicate": "port",
            "value": "6379",
            "target_scope": "network",
            "relation_mode": "stable",
            "confidence": 0.70,
            "mention_count": 1,
            "status": "active"
        }]
        distiller = CrossAgentDistiller(existing_knowledge=existing)
        
        # Another agent independently discovers and confirms the same port
        payload = {
            "agent_id": "worker_network_probe",
            "task_id": "probe_ports",
            "candidate_facts": [
                {
                    "subject": "redis_server",
                    "predicate": "port",
                    "value": "6379",
                    "target_scope": "network",
                    "confidence": 0.80,
                    "observation": "Socket connect to 6379 succeeded"
                }
            ]
        }
        res = distiller.distill_trajectory(payload)
        self.assertTrue(res["success"])
        fact = res["distilled_facts"][0]
        self.assertEqual(fact["action"], "DUPLICATE_CORROBORATED")
        self.assertEqual(fact["mention_count"], 2)
        # Bayesian updated confidence must be strictly higher than prior 0.70
        self.assertGreater(fact["confidence"], 0.70)

    def test_stable_invariant_conflict_quarantine(self):
        existing = [{
            "predicate_id": compute_predicate_hash("root_filesystem", "partition_type", "disk"),
            "subject": "root_filesystem",
            "predicate": "partition_type",
            "value": "ext4",
            "target_scope": "disk",
            "relation_mode": "stable",
            "confidence": 0.98,
            "status": "active"
        }]
        distiller = CrossAgentDistiller(existing_knowledge=existing)
        
        # Erroneous or hallucinating agent claims it's btrfs
        payload = {
            "agent_id": "worker_hallucinator",
            "task_id": "disk_scan",
            "candidate_facts": [
                {
                    "subject": "root_filesystem",
                    "predicate": "partition_type",
                    "value": "btrfs",
                    "target_scope": "disk",
                    "confidence": 0.75,
                    "observation": "Guessed from random string"
                }
            ]
        }
        res = distiller.distill_trajectory(payload)
        self.assertTrue(res["success"])
        self.assertEqual(len(res["quarantined_conflicts"]), 1)
        conflict = res["quarantined_conflicts"][0]
        self.assertEqual(conflict["existing_value"], "ext4")
        self.assertEqual(conflict["proposed_value"], "btrfs")
        self.assertIn("Stable predicate invariant collision", conflict["reason"])
        # The durable store must remain untouched as ext4
        self.assertEqual(distiller.durable_store[conflict["predicate_id"]]["value"], "ext4")

    def test_mutable_state_superseding(self):
        existing = [{
            "predicate_id": compute_predicate_hash("build_pipeline", "status", "ci"),
            "subject": "build_pipeline",
            "predicate": "status",
            "value": "in_progress",
            "target_scope": "ci",
            "relation_mode": "mutable",
            "confidence": 0.85,
            "status": "active"
        }]
        distiller = CrossAgentDistiller(existing_knowledge=existing)
        
        # New task completes the build
        payload = {
            "agent_id": "ci_watcher",
            "task_id": "poll_build",
            "candidate_facts": [
                {
                    "subject": "build_pipeline",
                    "predicate": "status",
                    "value": "passed",
                    "target_scope": "ci",
                    "relation_mode": "mutable",
                    "confidence": 0.95,
                    "observation": "Build exit code 0"
                }
            ]
        }
        res = distiller.distill_trajectory(payload)
        self.assertTrue(res["success"])
        self.assertEqual(len(res["distilled_facts"]), 1)
        fact = res["distilled_facts"][0]
        self.assertEqual(fact["action"], "MUTABLE_SUPERSEDED")
        self.assertEqual(fact["value"], "passed")
        self.assertEqual(len(fact["history"]), 1)
        self.assertEqual(fact["history"][0]["value"], "in_progress")

if __name__ == "__main__":
    unittest.main()
