#!/usr/bin/env python3
"""Comprehensive offline admission tests for multitier-safety-guardrails."""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest

from admission import (
    canonical_json_bytes,
    compute_hmac_hex,
    evaluate_admission,
    init_ledger,
    parse_strict_json,
)

SECRET_SEMANTIC = "key_semantic_secret_123"
SECRET_SANDBOX = "key_sandbox_secret_456"
SECRET_CONSENT = "key_consent_secret_789"


def make_trust_cfg():
    return {
        "expected_policy_version": "v1.0",
        "keys": {
            "semantic_issuer": SECRET_SEMANTIC,
            "sandbox_issuer": SECRET_SANDBOX,
            "consent_issuer": SECRET_CONSENT,
        },
        "tenants": {
            "tenant_alpha": {
                "principals": {
                    "agent_orchestrator": {
                        "actions": {
                            "read_file": {"allowed_objects": ["/safe/data.csv", "/safe/metrics.json"]},
                            "archive_log": {"allowed_objects": ["/logs/app.log"]}
                        }
                    }
                }
            }
        }
    }


def make_valid_envelope(now_ts=1000, req_id="req_001", consent_id="cons_001"):
    req = {
        "action": "read_file",
        "deadline_ts": str(now_ts + 300),
        "object": "/safe/data.csv",
        "payload_digest": hashlib.sha256(b"dummy payload").hexdigest(),
        "policy_version": "v1.0",
        "principal": "agent_orchestrator",
        "request_id": req_id,
        "runtime_instance_id": "inst_worker_99",
        "tenant": "tenant_alpha"
    }
    req_hash = hashlib.sha256(canonical_json_bytes(req)).hexdigest()

    sem_claims = {
        "expires_ts": str(now_ts + 120),
        "request_hash": req_hash,
        "verdict": "CLEAR"
    }
    sem_sig = compute_hmac_hex(SECRET_SEMANTIC.encode("utf-8"), canonical_json_bytes(sem_claims))

    sb_claims = {
        "expires_ts": str(now_ts + 120),
        "profile": {
            "network_disabled": True,
            "no_new_privs": True,
            "read_only_root": True
        },
        "request_hash": req_hash,
        "runtime_instance_id": "inst_worker_99"
    }
    sb_sig = compute_hmac_hex(SECRET_SANDBOX.encode("utf-8"), canonical_json_bytes(sb_claims))

    consent_claims = {
        "consent_id": consent_id,
        "expires_ts": str(now_ts + 60),
        "request_hash": req_hash
    }
    consent_sig = compute_hmac_hex(SECRET_CONSENT.encode("utf-8"), canonical_json_bytes(consent_claims))

    return {
        "request": req,
        "semantic_evidence": {"claims": sem_claims, "signature": sem_sig},
        "sandbox_evidence": {"claims": sb_claims, "signature": sb_sig},
        "consent_evidence": {"claims": consent_claims, "signature": consent_sig},
    }


class TestOfflineAdmission(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp_dir.name, "test_ledger.sqlite")
        self.ledger_conn = init_ledger(self.db_path)
        self.trust_cfg = make_trust_cfg()
        self.now_ts = 1000

    def tearDown(self):
        self.ledger_conn.close()
        self.tmp_dir.cleanup()

    def test_happy_path_admission(self):
        env = make_valid_envelope(self.now_ts, "req_1", "cons_1")
        admitted, reason, snap = evaluate_admission(env, self.trust_cfg, self.ledger_conn, self.now_ts)
        self.assertTrue(admitted)
        self.assertEqual(reason, "ADMITTED")
        self.assertIsNotNone(snap)
        self.assertEqual(snap["status"], "ADMITTED_OFFLINE")
        self.assertEqual(snap["limits"]["execution_allowed"], False)

    def test_replay_request_denied(self):
        env1 = make_valid_envelope(self.now_ts, "req_dup", "cons_1")
        admitted, reason, _ = evaluate_admission(env1, self.trust_cfg, self.ledger_conn, self.now_ts)
        self.assertTrue(admitted)

        # Second try with same request_id but new consent
        env2 = make_valid_envelope(self.now_ts, "req_dup", "cons_2")
        admitted2, reason2, _ = evaluate_admission(env2, self.trust_cfg, self.ledger_conn, self.now_ts)
        self.assertFalse(admitted2)
        self.assertEqual(reason2, "DENY_REPLAY_OR_ALREADY_CONSUMED")

    def test_replay_consent_denied(self):
        env1 = make_valid_envelope(self.now_ts, "req_1", "cons_dup")
        admitted, reason, _ = evaluate_admission(env1, self.trust_cfg, self.ledger_conn, self.now_ts)
        self.assertTrue(admitted)

        # Second try with new request_id but same consent_id
        env2 = make_valid_envelope(self.now_ts, "req_2", "cons_dup")
        admitted2, reason2, _ = evaluate_admission(env2, self.trust_cfg, self.ledger_conn, self.now_ts)
        self.assertFalse(admitted2)
        self.assertEqual(reason2, "DENY_REPLAY_OR_ALREADY_CONSUMED")

    def test_semantic_veto(self):
        env = make_valid_envelope(self.now_ts, "req_veto", "cons_veto")
        env["semantic_evidence"]["claims"]["verdict"] = "VETO"
        env["semantic_evidence"]["signature"] = compute_hmac_hex(
            SECRET_SEMANTIC.encode("utf-8"),
            canonical_json_bytes(env["semantic_evidence"]["claims"])
        )
        admitted, reason, _ = evaluate_admission(env, self.trust_cfg, self.ledger_conn, self.now_ts)
        self.assertFalse(admitted)
        self.assertEqual(reason, "DENY_SEMANTIC_VETOED")

    def test_semantic_unknown_verdict(self):
        env = make_valid_envelope(self.now_ts, "req_unk", "cons_unk")
        env["semantic_evidence"]["claims"]["verdict"] = "PASS_MAYBE"
        env["semantic_evidence"]["signature"] = compute_hmac_hex(
            SECRET_SEMANTIC.encode("utf-8"),
            canonical_json_bytes(env["semantic_evidence"]["claims"])
        )
        admitted, reason, _ = evaluate_admission(env, self.trust_cfg, self.ledger_conn, self.now_ts)
        self.assertFalse(admitted)
        self.assertEqual(reason, "DENY_SEMANTIC_UNKNOWN_VERDICT")

    def test_tampered_signature(self):
        env = make_valid_envelope(self.now_ts, "req_tamper", "cons_tamper")
        env["semantic_evidence"]["signature"] = "deadbeef" * 8
        admitted, reason, _ = evaluate_admission(env, self.trust_cfg, self.ledger_conn, self.now_ts)
        self.assertFalse(admitted)
        self.assertEqual(reason, "DENY_SEMANTIC_SIGNATURE_INVALID")

    def test_request_hash_mismatch(self):
        env = make_valid_envelope(self.now_ts, "req_mut", "cons_mut")
        # Mutate object without updating evidence claims
        env["request"]["object"] = "/safe/metrics.json"
        admitted, reason, _ = evaluate_admission(env, self.trust_cfg, self.ledger_conn, self.now_ts)
        self.assertFalse(admitted)
        self.assertEqual(reason, "DENY_SEMANTIC_REQUEST_MISMATCH")

    def test_unauthorized_action(self):
        env = make_valid_envelope(self.now_ts, "req_act", "cons_act")
        env["request"]["action"] = "delete_file"
        admitted, reason, _ = evaluate_admission(env, self.trust_cfg, self.ledger_conn, self.now_ts)
        self.assertFalse(admitted)
        self.assertEqual(reason, "DENY_ACTION_NOT_PERMITTED")

    def test_unauthorized_object(self):
        env = make_valid_envelope(self.now_ts, "req_obj", "cons_obj")
        env["request"]["object"] = "/etc/shadow"
        admitted, reason, _ = evaluate_admission(env, self.trust_cfg, self.ledger_conn, self.now_ts)
        self.assertFalse(admitted)
        self.assertEqual(reason, "DENY_OBJECT_NOT_PERMITTED")

    def test_expired_deadline(self):
        env = make_valid_envelope(self.now_ts, "req_exp", "cons_exp")
        admitted, reason, _ = evaluate_admission(env, self.trust_cfg, self.ledger_conn, self.now_ts + 400)
        self.assertFalse(admitted)
        self.assertEqual(reason, "DENY_REQUEST_EXPIRED")

    def test_sandbox_network_enabled(self):
        env = make_valid_envelope(self.now_ts, "req_net", "cons_net")
        env["sandbox_evidence"]["claims"]["profile"]["network_disabled"] = False
        env["sandbox_evidence"]["signature"] = compute_hmac_hex(
            SECRET_SANDBOX.encode("utf-8"),
            canonical_json_bytes(env["sandbox_evidence"]["claims"])
        )
        admitted, reason, _ = evaluate_admission(env, self.trust_cfg, self.ledger_conn, self.now_ts)
        self.assertFalse(admitted)
        self.assertEqual(reason, "DENY_SANDBOX_NETWORK_ENABLED")

    def test_sandbox_instance_mismatch(self):
        env = make_valid_envelope(self.now_ts, "req_inst", "cons_inst")
        env["sandbox_evidence"]["claims"]["runtime_instance_id"] = "inst_other"
        env["sandbox_evidence"]["signature"] = compute_hmac_hex(
            SECRET_SANDBOX.encode("utf-8"),
            canonical_json_bytes(env["sandbox_evidence"]["claims"])
        )
        admitted, reason, _ = evaluate_admission(env, self.trust_cfg, self.ledger_conn, self.now_ts)
        self.assertFalse(admitted)
        self.assertEqual(reason, "DENY_SANDBOX_INSTANCE_MISMATCH")

    def test_duplicate_key_json_rejected(self):
        raw = '{"request": {"request_id": "1"}, "request": {"request_id": "2"}}'
        with self.assertRaises(ValueError) as cm:
            parse_strict_json(raw)
        self.assertIn("Duplicate key", str(cm.exception))


class TestCLIExecution(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp_dir.name, "cli_ledger.sqlite")
        self.trust_path = os.path.join(self.tmp_dir.name, "trust.json")
        with open(self.trust_path, "w", encoding="utf-8") as f:
            json.dump(make_trust_cfg(), f)
        self.script_path = os.path.join(os.path.dirname(__file__), "admission.py")

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_cli_success(self):
        env = make_valid_envelope(1000, "cli_req_1", "cli_cons_1")
        proc = subprocess.run(
            [sys.executable, self.script_path, "--trust", self.trust_path, "--ledger", self.db_path, "--now", "1000"],
            input=json.dumps(env).encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.assertEqual(proc.returncode, 0)
        res = json.loads(proc.stdout.decode("utf-8"))
        self.assertTrue(res["admitted"])
        self.assertEqual(res["reason"], "ADMITTED")

    def test_cli_denial(self):
        env = make_valid_envelope(1000, "cli_req_2", "cli_cons_2")
        env["request"]["object"] = "/etc/passwd"
        proc = subprocess.run(
            [sys.executable, self.script_path, "--trust", self.trust_path, "--ledger", self.db_path, "--now", "1000"],
            input=json.dumps(env).encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.assertEqual(proc.returncode, 2)
        res = json.loads(proc.stdout.decode("utf-8"))
        self.assertFalse(res["admitted"])
        self.assertEqual(res["reason"], "DENY_OBJECT_NOT_PERMITTED")


if __name__ == "__main__":
    unittest.main()
