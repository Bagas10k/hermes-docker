#!/usr/bin/env python3
"""
Offline deterministic admission checker for multitier-safety-guardrails.
Pure standard library. Never executes actions. Status: TESTED_OFFLINE_ADMISSION_ONLY.
"""
import argparse
import hashlib
import hmac
import json
import sqlite3
import sys
from typing import Any, Dict, Optional, Tuple

SCHEMA_VERSION = "2026-03-01"


def canonical_json_bytes(obj: Any) -> bytes:
    """Serialize JSON with sorted keys, compact separators, UTF-8."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def parse_strict_json(raw_text: str) -> Dict[str, Any]:
    """Parse JSON rejecting duplicate keys and non-dict root."""
    def pairs_hook(pairs):
        d = {}
        for k, v in pairs:
            if k in d:
                raise ValueError(f"Duplicate key detected: {k}")
            d[k] = v
        return d

    data = json.loads(raw_text, object_pairs_hook=pairs_hook)
    if not isinstance(data, dict):
        raise ValueError("Root payload must be a JSON object")
    return data


def compute_hmac_hex(key_bytes: bytes, data_bytes: bytes) -> str:
    return hmac.new(key_bytes, data_bytes, hashlib.sha256).hexdigest()


def verify_hmac_hex(key_bytes: bytes, data_bytes: bytes, expected_sig: str) -> bool:
    actual_sig = compute_hmac_hex(key_bytes, data_bytes)
    return hmac.compare_digest(actual_sig, expected_sig)


def init_ledger(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, timeout=10.0, isolation_level=None)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS consumed_tokens (
            token_type TEXT NOT NULL,
            token_id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            request_hash TEXT NOT NULL,
            consumed_at_ts INTEGER NOT NULL,
            PRIMARY KEY (token_type, token_id)
        )
    """)
    return conn


def evaluate_admission(
    envelope: Dict[str, Any],
    trust_cfg: Dict[str, Any],
    ledger_conn: sqlite3.Connection,
    now_ts: int,
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Evaluates multi-tier guardrails offline.
    Returns (admitted: bool, reason_code: str, snapshot: Optional[dict]).
    """
    # 1. Structural check
    req = envelope.get("request")
    if not isinstance(req, dict):
        return False, "DENY_MALFORMED_REQUEST", None

    required_req_fields = [
        "request_id", "principal", "tenant", "action", "object",
        "payload_digest", "runtime_instance_id", "policy_version", "deadline_ts"
    ]
    for field in required_req_fields:
        if field not in req or not isinstance(req[field], str) or req[field] == "":
            return False, f"DENY_MISSING_REQ_FIELD_{field.upper()}", None

    deadline_ts_val = req.get("deadline_ts")
    try:
        req_deadline = int(deadline_ts_val)
    except (ValueError, TypeError):
        return False, "DENY_INVALID_DEADLINE", None

    if now_ts > req_deadline:
        return False, "DENY_REQUEST_EXPIRED", None

    # Exact policy version match
    if req["policy_version"] != trust_cfg.get("expected_policy_version"):
        return False, "DENY_POLICY_VERSION_MISMATCH", None

    # Canonical request bytes and hash
    req_bytes = canonical_json_bytes(req)
    req_hash = hashlib.sha256(req_bytes).hexdigest()

    # 2. Deterministic authorization
    tenant_cfg = trust_cfg.get("tenants", {}).get(req["tenant"])
    if not tenant_cfg:
        return False, "DENY_TENANT_NOT_FOUND", None

    allowed_principals = tenant_cfg.get("principals", {})
    if req["principal"] not in allowed_principals:
        return False, "DENY_PRINCIPAL_UNAUTHORIZED", None

    user_rules = allowed_principals[req["principal"]]
    allowed_actions = user_rules.get("actions", {})
    if req["action"] not in allowed_actions:
        return False, "DENY_ACTION_NOT_PERMITTED", None

    target_objects = allowed_actions[req["action"]].get("allowed_objects", [])
    if req["object"] not in target_objects:
        return False, "DENY_OBJECT_NOT_PERMITTED", None

    # 3. Semantic Veto Layer (Semantic clear cannot grant; veto denies)
    sem_ev = envelope.get("semantic_evidence")
    if not isinstance(sem_ev, dict):
        return False, "DENY_MISSING_SEMANTIC_EVIDENCE", None

    sem_claims = sem_ev.get("claims")
    sem_sig = sem_ev.get("signature")
    if not isinstance(sem_claims, dict) or not isinstance(sem_sig, str):
        return False, "DENY_MALFORMED_SEMANTIC_EVIDENCE", None

    # Verify semantic key
    sem_key = trust_cfg.get("keys", {}).get("semantic_issuer", "").encode("utf-8")
    if not sem_key:
        return False, "DENY_TRUST_KEY_SEMANTIC_MISSING", None

    if not verify_hmac_hex(sem_key, canonical_json_bytes(sem_claims), sem_sig):
        return False, "DENY_SEMANTIC_SIGNATURE_INVALID", None

    if sem_claims.get("request_hash") != req_hash:
        return False, "DENY_SEMANTIC_REQUEST_MISMATCH", None

    try:
        sem_exp = int(sem_claims.get("expires_ts", 0))
    except (ValueError, TypeError):
        return False, "DENY_SEMANTIC_EXPIRES_INVALID", None

    if now_ts > sem_exp:
        return False, "DENY_SEMANTIC_EXPIRED", None

    sem_verdict = sem_claims.get("verdict")
    if sem_verdict == "VETO":
        return False, "DENY_SEMANTIC_VETOED", None
    elif sem_verdict != "CLEAR":
        return False, "DENY_SEMANTIC_UNKNOWN_VERDICT", None

    # 4. Sandbox Attestation Layer
    sb_ev = envelope.get("sandbox_evidence")
    if not isinstance(sb_ev, dict):
        return False, "DENY_MISSING_SANDBOX_EVIDENCE", None

    sb_claims = sb_ev.get("claims")
    sb_sig = sb_ev.get("signature")
    if not isinstance(sb_claims, dict) or not isinstance(sb_sig, str):
        return False, "DENY_MALFORMED_SANDBOX_EVIDENCE", None

    sb_key = trust_cfg.get("keys", {}).get("sandbox_issuer", "").encode("utf-8")
    if not sb_key:
        return False, "DENY_TRUST_KEY_SANDBOX_MISSING", None

    if not verify_hmac_hex(sb_key, canonical_json_bytes(sb_claims), sb_sig):
        return False, "DENY_SANDBOX_SIGNATURE_INVALID", None

    if sb_claims.get("request_hash") != req_hash:
        return False, "DENY_SANDBOX_REQUEST_MISMATCH", None

    if sb_claims.get("runtime_instance_id") != req["runtime_instance_id"]:
        return False, "DENY_SANDBOX_INSTANCE_MISMATCH", None

    try:
        sb_exp = int(sb_claims.get("expires_ts", 0))
    except (ValueError, TypeError):
        return False, "DENY_SANDBOX_EXPIRES_INVALID", None

    if now_ts > sb_exp:
        return False, "DENY_SANDBOX_EXPIRED", None

    # Required sandbox profile attributes
    sb_profile = sb_claims.get("profile")
    if not isinstance(sb_profile, dict):
        return False, "DENY_SANDBOX_PROFILE_INVALID", None

    if sb_profile.get("network_disabled") is not True:
        return False, "DENY_SANDBOX_NETWORK_ENABLED", None
    if sb_profile.get("read_only_root") is not True:
        return False, "DENY_SANDBOX_ROOT_NOT_RO", None
    if sb_profile.get("no_new_privs") is not True:
        return False, "DENY_SANDBOX_PRIVS_NOT_DROPPED", None

    # 5. One-Use Consent Layer
    consent_ev = envelope.get("consent_evidence")
    if not isinstance(consent_ev, dict):
        return False, "DENY_MISSING_CONSENT_EVIDENCE", None

    consent_claims = consent_ev.get("claims")
    consent_sig = consent_ev.get("signature")
    if not isinstance(consent_claims, dict) or not isinstance(consent_sig, str):
        return False, "DENY_MALFORMED_CONSENT_EVIDENCE", None

    consent_key = trust_cfg.get("keys", {}).get("consent_issuer", "").encode("utf-8")
    if not consent_key:
        return False, "DENY_TRUST_KEY_CONSENT_MISSING", None

    if not verify_hmac_hex(consent_key, canonical_json_bytes(consent_claims), consent_sig):
        return False, "DENY_CONSENT_SIGNATURE_INVALID", None

    if consent_claims.get("request_hash") != req_hash:
        return False, "DENY_CONSENT_REQUEST_MISMATCH", None

    consent_id = consent_claims.get("consent_id")
    if not consent_id or not isinstance(consent_id, str):
        return False, "DENY_CONSENT_ID_MISSING", None

    try:
        consent_exp = int(consent_claims.get("expires_ts", 0))
    except (ValueError, TypeError):
        return False, "DENY_CONSENT_EXPIRES_INVALID", None

    if now_ts > consent_exp:
        return False, "DENY_CONSENT_EXPIRED", None

    # 6. Atomic Consumption in Durable SQLite Ledger
    req_id = req["request_id"]
    tenant_id = req["tenant"]
    try:
        cursor = ledger_conn.cursor()
        cursor.execute("BEGIN IMMEDIATE")
        # Record request consumption
        cursor.execute(
            "INSERT INTO consumed_tokens (token_type, token_id, tenant_id, request_hash, consumed_at_ts) VALUES (?, ?, ?, ?, ?)",
            ("request", req_id, tenant_id, req_hash, now_ts)
        )
        # Record consent consumption
        cursor.execute(
            "INSERT INTO consumed_tokens (token_type, token_id, tenant_id, request_hash, consumed_at_ts) VALUES (?, ?, ?, ?, ?)",
            ("consent", consent_id, tenant_id, req_hash, now_ts)
        )
        ledger_conn.commit()
    except sqlite3.IntegrityError:
        try:
            ledger_conn.rollback()
        except Exception:
            pass
        return False, "DENY_REPLAY_OR_ALREADY_CONSUMED", None
    except Exception as e:
        try:
            ledger_conn.rollback()
        except Exception:
            pass
        return False, f"DENY_LEDGER_ERROR_{type(e).__name__}", None

    # 7. Admitted: build immutable execution candidate snapshot
    snapshot = {
        "status": "ADMITTED_OFFLINE",
        "admitted_at_ts": now_ts,
        "request_hash": req_hash,
        "request": req,
        "evidence_digests": {
            "semantic": hashlib.sha256(canonical_json_bytes(sem_claims)).hexdigest(),
            "sandbox": hashlib.sha256(canonical_json_bytes(sb_claims)).hexdigest(),
            "consent": hashlib.sha256(canonical_json_bytes(consent_claims)).hexdigest(),
        },
        "limits": {
            "execution_allowed": False,
            "notice": "TESTED_OFFLINE_ADMISSION_ONLY: NO ACTION DISPATCHED"
        }
    }
    return True, "ADMITTED", snapshot


def main():
    parser = argparse.ArgumentParser(description="Multitier Safety Guardrails Offline Admission Checker")
    parser.add_argument("--trust", required=True, help="Path to trusted configuration JSON")
    parser.add_argument("--ledger", required=True, help="Path to SQLite ledger file")
    parser.add_argument("--now", type=int, default=None, help="Mock timestamp for testing")
    args = parser.parse_args()

    import time
    now_ts = args.now if args.now is not None else int(time.time())

    try:
        with open(args.trust, "r", encoding="utf-8") as f:
            trust_cfg = parse_strict_json(f.read())
    except Exception as e:
        sys.stderr.write(f"Error loading trust config: {e}\n")
        sys.exit(2)

    try:
        raw_input = sys.stdin.read()
        envelope = parse_strict_json(raw_input)
    except Exception as e:
        res = {"admitted": False, "reason": f"PARSE_ERROR: {e}", "snapshot": None}
        print(json.dumps(res, indent=2))
        sys.exit(2)

    try:
        ledger_conn = init_ledger(args.ledger)
    except Exception as e:
        res = {"admitted": False, "reason": f"LEDGER_INIT_ERROR: {e}", "snapshot": None}
        print(json.dumps(res, indent=2))
        sys.exit(2)

    admitted, reason, snapshot = evaluate_admission(envelope, trust_cfg, ledger_conn, now_ts)
    output = {
        "admitted": admitted,
        "reason": reason,
        "snapshot": snapshot
    }
    print(json.dumps(output, indent=2))
    sys.exit(0 if admitted else 2)


if __name__ == "__main__":
    main()
