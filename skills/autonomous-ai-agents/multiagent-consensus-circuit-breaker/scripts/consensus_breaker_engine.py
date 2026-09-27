"""
Multi-Agent Consensus, Subagent Delegation & Cascade Hallucination Circuit Breaker Engine
Deterministic Python prototype verifying invariants:
1. Isolated Subagent Delegation Envelope (Task boundary with contract).
2. Majority/Weighted Voting Consensus with Ambiguity Detection.
3. Cascade Hallucination Detector (Taint propagation & semantic divergence).
4. Exponential Loop & Cycle Circuit Breaker (Anti-doom loop).
"""

import hashlib
import time
from typing import Dict, List, Any, Optional

class DelegationEnvelope:
    def __init__(self, task_id: str, sender: str, receiver: str, objective: str, constraints: List[str], max_turns: int = 5):
        self.task_id = task_id
        self.sender = sender
        self.receiver = receiver
        self.objective = objective
        self.constraints = constraints
        self.max_turns = max_turns
        self.turn_count = 0
        self.is_closed = False
        self.result: Optional[str] = None
        self.evidence_hashes: List[str] = []

    def record_turn(self, action_signature: str) -> bool:
        self.turn_count += 1
        if self.turn_count > self.max_turns:
            self.is_closed = True
            return False
        h = hashlib.sha256(action_signature.encode('utf-8')).hexdigest()[:8]
        self.evidence_hashes.append(h)
        return True

    def complete(self, result: str):
        self.result = result
        self.is_closed = True


class MultiAgentConsensusBreaker:
    def __init__(self, loop_threshold: int = 3, divergence_threshold: float = 0.5):
        self.loop_threshold = loop_threshold
        self.divergence_threshold = divergence_threshold
        self.action_history: List[str] = []
        self.tripped = False
        self.trip_reason = ""

    def check_loop_circuit(self, action_sig: str) -> bool:
        """Deteksi pengulangan aksi persis (Doom Loop)."""
        self.action_history.append(action_sig)
        recent = self.action_history[-self.loop_threshold:]
        if len(recent) == self.loop_threshold and all(a == action_sig for a in recent):
            self.tripped = True
            self.trip_reason = f"DOOM_LOOP_DETECTED: Repeated action '{action_sig}' {self.loop_threshold} times."
            return False
        return True

    def calculate_consensus(self, agent_opinions: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Voting konsensus berbasis bobot keyakinan (confidence-weighted voting).
        Format: agent_name -> {"decision": str, "confidence": float, "is_verified": bool}
        """
        tally: Dict[str, float] = {}
        total_weight = 0.0

        for agent, data in agent_opinions.items():
            decision = data["decision"]
            # Bobot dinaikkan jika ada verifikasi empiris nyata
            base_weight = data.get("confidence", 0.5)
            multiplier = 1.5 if data.get("is_verified", False) else 1.0
            weight = base_weight * multiplier

            tally[decision] = tally.get(decision, 0.0) + weight
            total_weight += weight

        if not tally:
            return {"consensus": None, "confidence": 0.0, "status": "NO_OPINIONS"}

        # Cari pemenang
        sorted_decisions = sorted(tally.items(), key=lambda x: x[1], reverse=True)
        winner, win_score = sorted_decisions[0]
        consensus_ratio = win_score / total_weight if total_weight > 0 else 0

        # Cek margin kemenangan untuk ambiguitas (deadlock risk)
        if len(sorted_decisions) > 1:
            runner_up, runner_score = sorted_decisions[1]
            margin = (win_score - runner_score) / total_weight
            if margin < 0.15:
                return {
                    "consensus": None,
                    "confidence": consensus_ratio,
                    "status": "DEADLOCK_OR_AMBIGUITY",
                    "margin": margin,
                    "tally": tally
                }

        return {
            "consensus": winner,
            "confidence": consensus_ratio,
            "status": "AGREED",
            "tally": tally
        }

    def detect_cascade_hallucination(self, parent_facts: List[str], child_inferences: List[str]) -> bool:
        """
        Mendeteksi apakah kesimpulan agen anak menyimpang tanpa dasar dari fakta awal agen induk.
        Jika rasio fakta terverifikasi < threshold, flag sebagai kontaminasi halusinasi.
        """
        parent_set = set(p.lower().strip() for p in parent_facts)
        grounded_count = 0
        unsupported = []

        for inference in child_inferences:
            inf_lower = inference.lower().strip()
            # Cek keterikatan leksikal / substring sederhana sebagai model dasar
            is_grounded = any(p in inf_lower or inf_lower in p for p in parent_set)
            if is_grounded:
                grounded_count += 1
            else:
                unsupported.append(inference)

        total_inferences = len(child_inferences)
        if total_inferences == 0:
            return False

        grounded_ratio = grounded_count / total_inferences
        # Jika proporsi yang grounded di bawah threshold, picu cascade alert
        if grounded_ratio < self.divergence_threshold:
            self.tripped = True
            self.trip_reason = f"CASCADE_HALLUCINATION_TRIPPED: Grounded ratio {grounded_ratio:.2f} < {self.divergence_threshold}. Unsupported: {unsupported}"
            return True

        return False


def test_invariants():
    print("[TEST 1] Testing Isolated Subagent Envelope...")
    env = DelegationEnvelope(
        task_id="TASK-001",
        sender="Master-GeneralManager",
        receiver="Worker-CodeAuditor",
        objective="Inspect auth token expiration logic",
        constraints=["read_only", "no_network_mutations"],
        max_turns=3
    )
    assert env.record_turn("search_files(pattern='auth.py')") == True
    assert env.record_turn("read_file(path='auth.py')") == True
    assert env.record_turn("read_file(path='tests.py')") == True
    # Turn ke-4 harus ditolak karena melebihi max_turns
    assert env.record_turn("another_call()") == False
    assert env.is_closed == True
    print("  -> Passed: Turn bound strictly enforced.")

    print("[TEST 2] Testing Anti-Doom Loop Circuit Breaker...")
    cb = MultiAgentConsensusBreaker(loop_threshold=3)
    assert cb.check_loop_circuit("terminal(cmd='ls -la')") == True
    assert cb.check_loop_circuit("terminal(cmd='ls -la')") == True
    # Loop ke-3 dengan aksi persis sama harus memicu breaker
    assert cb.check_loop_circuit("terminal(cmd='ls -la')") == False
    assert cb.tripped == True
    print(f"  -> Passed: Circuit tripped cleanly ({cb.trip_reason}).")

    print("[TEST 3] Testing Weighted Consensus & Deadlock Detection...")
    cb_consensus = MultiAgentConsensusBreaker()
    # Kasus A: Mayoritas kuat dengan verifikasi
    opinions_clear = {
        "Researcher_Alpha": {"decision": "PATCH_CONFIG", "confidence": 0.8, "is_verified": True},
        "Architect_Beta": {"decision": "PATCH_CONFIG", "confidence": 0.7, "is_verified": False},
        "Safety_Gamma": {"decision": "RESTART_DAEMON", "confidence": 0.6, "is_verified": False}
    }
    res_clear = cb_consensus.calculate_consensus(opinions_clear)
    assert res_clear["status"] == "AGREED"
    assert res_clear["consensus"] == "PATCH_CONFIG"
    print(f"  -> Passed: Clear consensus identified ({res_clear['consensus']}, conf: {res_clear['confidence']:.2f}).")

    # Kasus B: Deadlock / Ambiguitas ketat
    opinions_deadlock = {
        "Researcher_Alpha": {"decision": "OPTION_A", "confidence": 0.7, "is_verified": False},
        "Architect_Beta": {"decision": "OPTION_B", "confidence": 0.7, "is_verified": False}
    }
    res_deadlock = cb_consensus.calculate_consensus(opinions_deadlock)
    assert res_deadlock["status"] == "DEADLOCK_OR_AMBIGUITY"
    assert res_deadlock["consensus"] is None
    print("  -> Passed: Deadlock / ambiguity correctly flagged for escalation.")

    print("[TEST 4] Testing Cascade Hallucination Detector...")
    cb_hallucination = MultiAgentConsensusBreaker(divergence_threshold=0.5)
    parent_facts = [
        "Port 3000 is open and bound to Node.js backend",
        "SQLite database state.db is locked with SQLITE_BUSY error",
        "Process 1234 consumed 95% CPU"
    ]
    # Inferences yang menyimpang drastis tanpa rujukan fakta
    wild_child_inferences = [
        "Kubernetes cluster DNS is down across region us-east-1",
        "Payment gateway Stripe API key was leaked to pastebin",
        "Docker container needs AWS S3 bucket re-creation"
    ]
    has_cascade = cb_hallucination.detect_cascade_hallucination(parent_facts, wild_child_inferences)
    assert has_cascade == True
    assert cb_hallucination.tripped == True
    print(f"  -> Passed: Cascade hallucination successfully quarantined ({cb_hallucination.trip_reason}).")

    print("\n[ALL MULTIAGENT CONSENSUS & CIRCUIT BREAKER INVARIANTS TESTED SUCCESSFULLY]")


if __name__ == "__main__":
    test_invariants()
