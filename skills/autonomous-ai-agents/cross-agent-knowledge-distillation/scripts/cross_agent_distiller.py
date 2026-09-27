#!/usr/bin/env python3
"""
cross_agent_distiller.py - Deterministic Knowledge Distillation & Absorption Engine
Offline admission and distillation harness for sub-agent ephemeral trajectories into durable knowledge.
"""

import sys
import json
import re
import hashlib
from typing import Dict, Any, List, Tuple, Optional

# Secret / credential regex scrubbing patterns
REDACTION_PATTERNS = [
    (re.compile(r'(?i)(?:api_key|token|secret|password|bearer|auth|access_token|private_key)\s*[:=]\s*["\']?([a-zA-Z0-9_\-\.\$\/]{8,})["\']?'), r'\1'),
    (re.compile(r'ghp_[a-zA-Z0-9]{36}'), 'ghp_[REDACTED]'),
    (re.compile(r'xox[baprs]-[0-9a-zA-Z]{10,48}'), 'slack_[REDACTED]'),
    (re.compile(r'eyJ[a-zA-Z0-9_\-]{10,}\.eyJ[a-zA-Z0-9_\-]{10,}\.[a-zA-Z0-9_\-]{10,}'), 'jwt_[REDACTED]'),
]

# Ephemeral noise patterns (ANSI, terminal escapes, raw progress bytes, base64 data)
ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
RAW_BASE64_DATA = re.compile(r'data:image\/[a-zA-Z\.\+\-]+;base64,[a-zA-Z0-9+/=]{40,}')
PROGRESS_SPAM = re.compile(r'(\r?\n)?(\[\s*\d+%\s*\]|\.{3,}|Downloading\s+[\d\.]+\s*(?:MB|KB|GB)|Progress:\s*\d+%)')

def sanitize_text(text: str) -> str:
    """Scrub ANSI escapes, progress noise, raw data URIs, and credentials."""
    if not isinstance(text, str):
        return str(text)
    
    # Strip ANSI
    cleaned = ANSI_ESCAPE.sub('', text)
    # Strip progress spam
    cleaned = PROGRESS_SPAM.sub('', cleaned)
    # Strip long base64 blocks
    cleaned = RAW_BASE64_DATA.sub('[DATA_URI_REDACTED]', cleaned)
    
    # Redact secrets
    for pattern, target in REDACTION_PATTERNS:
        if callable(target):
            cleaned = pattern.sub(target, cleaned)
        elif target.startswith('\\1'):
            # replace matched group 1 with [REDACTED]
            def _repl(m):
                full = m.group(0)
                sec = m.group(1)
                return full.replace(sec, '[REDACTED]')
            cleaned = pattern.sub(_repl, cleaned)
        else:
            cleaned = pattern.sub(target, cleaned)
            
    return cleaned.strip()

def compute_predicate_hash(subject: str, predicate: str, target_scope: str = "") -> str:
    """Deterministic hash for atomic memory identity: subject + predicate + target_scope."""
    raw = f"{subject.strip().lower()}::{predicate.strip().lower()}::{target_scope.strip().lower()}"
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]

class CrossAgentDistiller:
    def __init__(self, existing_knowledge: Optional[List[Dict[str, Any]]] = None):
        """
        existing_knowledge: List of active knowledge records currently in durable store.
        Each record has: id, subject, predicate, value, confidence, provenance, status, relation_mode ('stable'|'mutable')
        """
        self.durable_store: Dict[str, Dict[str, Any]] = {}
        if existing_knowledge:
            for item in existing_knowledge:
                pid = compute_predicate_hash(item['subject'], item['predicate'], item.get('target_scope', ''))
                self.durable_store[pid] = dict(item)

    def distill_trajectory(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes an ephemeral agent run or batch of candidate facts.
        Enforces schema validation, noise scrubbing, conflict detection, and bayesian score fusion.
        """
        # 1. Structural Validation
        errors = self.validate_payload_schema(payload)
        if errors:
            return {
                "success": False,
                "admitted": False,
                "rejection_reasons": errors,
                "distilled_facts": [],
                "quarantined_conflicts": [],
                "scrubbed_noise_bytes": 0
            }

        agent_id = payload.get("agent_id", "unknown_agent")
        task_id = payload.get("task_id", "unknown_task")
        candidate_facts = payload.get("candidate_facts", [])
        
        distilled = []
        conflicts = []
        total_scrubbed_bytes = 0

        # 2. Fact Extraction, Sanitization & Conflict Resolution
        for fact in candidate_facts:
            subj = sanitize_text(fact.get("subject", ""))
            pred = sanitize_text(fact.get("predicate", ""))
            val = sanitize_text(str(fact.get("value", "")))
            scope = sanitize_text(fact.get("target_scope", "global"))
            mode = fact.get("relation_mode", "mutable").lower()
            conf = float(fact.get("confidence", 0.7))
            obs = sanitize_text(fact.get("observation", ""))
            
            # Count scrubbed difference
            orig_len = len(str(fact.get("subject", ""))) + len(str(fact.get("predicate", ""))) + len(str(fact.get("value", "")))
            new_len = len(subj) + len(pred) + len(val)
            total_scrubbed_bytes += max(0, orig_len - new_len)

            if not subj or not pred:
                continue

            # Bounds check
            if conf < 0.35:
                # Discard low-confidence hallucination candidates
                continue
            conf = min(0.99, max(0.01, conf))

            pid = compute_predicate_hash(subj, pred, scope)
            existing = self.durable_store.get(pid)

            if existing is None:
                # Brand new atomic knowledge
                new_record = {
                    "predicate_id": pid,
                    "subject": subj,
                    "predicate": pred,
                    "value": val,
                    "target_scope": scope,
                    "relation_mode": mode,
                    "confidence": round(conf, 4),
                    "mention_count": 1,
                    "provenance": [{
                        "agent_id": agent_id,
                        "task_id": task_id,
                        "observation": obs,
                        "confidence": conf
                    }],
                    "action": "NEW",
                    "status": "active"
                }
                distilled.append(new_record)
                self.durable_store[pid] = new_record
            else:
                # Existing entry matches subject + predicate + scope
                ext_val = str(existing.get("value", ""))
                ext_mode = existing.get("relation_mode", "mutable")
                
                if ext_val == val:
                    # DUPLICATE: Corroboration increases Bayesian belief
                    prior_conf = float(existing.get("confidence", 0.7))
                    # Bayesian update for independent witness corroboration:
                    # P(H|E) = 1 - (1 - P(prior)) * (1 - P(new))
                    posterior = 1.0 - ((1.0 - prior_conf) * (1.0 - (conf * 0.5)))
                    posterior = min(0.999, round(posterior, 4))
                    
                    existing["confidence"] = posterior
                    existing["mention_count"] = existing.get("mention_count", 1) + 1
                    existing.setdefault("provenance", []).append({
                        "agent_id": agent_id,
                        "task_id": task_id,
                        "observation": obs,
                        "confidence": conf
                    })
                    existing["action"] = "DUPLICATE_CORROBORATED"
                    distilled.append(dict(existing))
                else:
                    # VALUES DIFFER: Update or Conflict?
                    if ext_mode == "stable":
                        # Invariant collision! Cannot mutate silently. Must quarantine.
                        conflict_entry = {
                            "predicate_id": pid,
                            "subject": subj,
                            "predicate": pred,
                            "scope": scope,
                            "existing_value": ext_val,
                            "proposed_value": val,
                            "existing_confidence": existing.get("confidence"),
                            "proposed_confidence": conf,
                            "reporting_agent": agent_id,
                            "task_id": task_id,
                            "reason": "Stable predicate invariant collision - prohibited from silent in-place overwrite."
                        }
                        conflicts.append(conflict_entry)
                    else:
                        # Mutable state evolution: Supersede if proposed confidence is high enough
                        if conf >= float(existing.get("confidence", 0.5)):
                            # Supersede old value, archive to history
                            old_history = existing.get("history", [])
                            old_history.append({
                                "value": ext_val,
                                "superseded_at_task": task_id,
                                "superseded_by_agent": agent_id,
                                "confidence": existing.get("confidence")
                            })
                            existing["history"] = old_history
                            existing["value"] = val
                            existing["confidence"] = round(conf, 4)
                            existing["action"] = "MUTABLE_SUPERSEDED"
                            existing.setdefault("provenance", []).append({
                                "agent_id": agent_id,
                                "task_id": task_id,
                                "observation": obs,
                                "confidence": conf
                            })
                            distilled.append(dict(existing))
                        else:
                            # Proposed update has lower confidence than existing verified knowledge; quarantine
                            conflicts.append({
                                "predicate_id": pid,
                                "subject": subj,
                                "predicate": pred,
                                "scope": scope,
                                "existing_value": ext_val,
                                "proposed_value": val,
                                "existing_confidence": existing.get("confidence"),
                                "proposed_confidence": conf,
                                "reporting_agent": agent_id,
                                "task_id": task_id,
                                "reason": "Proposed mutation confidence lower than established durable memory."
                            })

        return {
            "success": True,
            "admitted": True,
            "agent_id": agent_id,
            "task_id": task_id,
            "distilled_facts": distilled,
            "quarantined_conflicts": conflicts,
            "scrubbed_noise_bytes": total_scrubbed_bytes,
            "durable_store_count": len(self.durable_store)
        }

    def validate_payload_schema(self, payload: Dict[str, Any]) -> List[str]:
        errors = []
        if not isinstance(payload, dict):
            return ["Payload must be a JSON dictionary."]
        
        if not payload.get("agent_id"):
            errors.append("Missing mandatory 'agent_id'.")
        if not payload.get("task_id"):
            errors.append("Missing mandatory 'task_id'.")
        
        candidates = payload.get("candidate_facts")
        if not isinstance(candidates, list):
            errors.append("'candidate_facts' must be a list of atomic statements.")
        else:
            for idx, c in enumerate(candidates):
                if not isinstance(c, dict):
                    errors.append(f"candidate_facts[{idx}] must be a dict.")
                    continue
                if not c.get("subject"):
                    errors.append(f"candidate_facts[{idx}] missing 'subject'.")
                if not c.get("predicate"):
                    errors.append(f"candidate_facts[{idx}] missing 'predicate'.")
                if "value" not in c:
                    errors.append(f"candidate_facts[{idx}] missing 'value'.")
        
        return errors

def main():
    if len(sys.argv) < 2:
        print("Usage: cross_agent_distiller.py <payload.json> [--existing <existing.json>]")
        sys.exit(1)

    payload_path = sys.argv[1]
    existing_path = None
    if "--existing" in sys.argv:
        idx = sys.argv.index("--existing")
        if idx + 1 < len(sys.argv):
            existing_path = sys.argv[idx + 1]

    try:
        with open(payload_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except Exception as e:
        print(json.dumps({"success": False, "error": f"Failed to read payload: {e}"}))
        sys.exit(1)

    existing_knowledge = []
    if existing_path:
        try:
            with open(existing_path, "r", encoding="utf-8") as f:
                existing_knowledge = json.load(f)
        except Exception as e:
            print(json.dumps({"success": False, "error": f"Failed to read existing store: {e}"}))
            sys.exit(1)

    distiller = CrossAgentDistiller(existing_knowledge)
    result = distiller.distill_trajectory(payload)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
