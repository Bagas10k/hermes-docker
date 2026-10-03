"""
Multi-Agent Bounded Consensus Circuit Breaker & Byzantine Fault Tolerance Engine.
Deterministic reference implementation for preventing live-locks, infinite debate loops,
and adversarial voting divergence in multi-agent swarms.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any
import math
import json


class CircuitState(str, Enum):
    CLOSED = "CLOSED"      # Normal consensus rounds permitted
    HALF_OPEN = "HALF_OPEN"  # Single probationary canary probe allowed
    OPEN = "OPEN"          # Tripped: debate halted, fallback/safe default engaged


class VoteDecision(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    ABSTAIN = "ABSTAIN"


@dataclass(frozen=True)
class Ballot:
    agent_id: str
    round_idx: int
    proposal_id: str
    decision: VoteDecision
    weight: float = 1.0
    evidence_hash: str = ""

    def __post_init__(self):
        if not self.agent_id:
            raise ValueError("agent_id cannot be empty")
        if self.round_idx < 0:
            raise ValueError("round_idx cannot be negative")
        if self.weight <= 0.0 or not math.isfinite(self.weight):
            raise ValueError("weight must be a finite positive number")


@dataclass
class RoundResult:
    round_idx: int
    proposal_id: str
    total_weight: float
    approve_weight: float
    reject_weight: float
    abstain_weight: float
    entropy: float
    delta_entropy: float
    consensus_reached: bool
    winning_decision: Optional[VoteDecision]
    circuit_state: CircuitState
    tripped_reason: Optional[str] = None
    byzantine_flagged_agents: List[str] = field(default_factory=list)


class ConsensusCircuitBreaker:
    """
    Guarantees bounded termination and Byzantine fault tolerance for multi-agent debates:
    1. BFT Bound: n >= 3f + 1 where f is maximum tolerated faulty/byzantine nodes.
    2. Zero-Delta Entropy Detection: detects oscillatory or stalled debate loops (delta H < epsilon).
    3. Maximum Debate Rounds: hard bound preventing unbounded token burn.
    4. Circuit Breaker: transitions CLOSED -> OPEN upon consecutive stall or Byzantine breach.
    """

    def __init__(
        self,
        total_nodes: int,
        max_faulty_f: Optional[int] = None,
        max_rounds: int = 5,
        entropy_epsilon: float = 1e-4,
        consecutive_stalls_to_trip: int = 2,
        half_open_recovery_rounds: int = 1,
        fallback_decision: VoteDecision = VoteDecision.ABSTAIN,
    ):
        if total_nodes <= 0:
            raise ValueError("total_nodes must be positive")
        self.total_nodes = total_nodes

        # Standard BFT bound: n >= 3f + 1 => f <= (n - 1) // 3
        max_allowed_f = (total_nodes - 1) // 3
        if max_faulty_f is None:
            self.max_faulty_f = max_allowed_f
        else:
            if max_faulty_f < 0:
                raise ValueError("max_faulty_f cannot be negative")
            if max_faulty_f > max_allowed_f:
                raise ValueError(
                    f"max_faulty_f ({max_faulty_f}) exceeds BFT capacity for n={total_nodes}. "
                    f"Must satisfy n >= 3f + 1 (max f = {max_allowed_f})."
                )
            self.max_faulty_f = max_faulty_f

        if max_rounds <= 0:
            raise ValueError("max_rounds must be positive")
        self.max_rounds = max_rounds

        if entropy_epsilon < 0.0 or not math.isfinite(entropy_epsilon):
            raise ValueError("entropy_epsilon must be non-negative finite")
        self.entropy_epsilon = entropy_epsilon

        if consecutive_stalls_to_trip <= 0:
            raise ValueError("consecutive_stalls_to_trip must be >= 1")
        self.consecutive_stalls_to_trip = consecutive_stalls_to_trip

        self.half_open_recovery_rounds = half_open_recovery_rounds
        self.fallback_decision = fallback_decision

        self.state = CircuitState.CLOSED
        self.current_round = 0
        self.consecutive_stalls = 0
        self.prev_entropy: Optional[float] = None
        self.history: List[RoundResult] = []
        self.known_byzantine_agents: Set[str] = set()

    @property
    def quorum_threshold(self) -> float:
        # BFT supermajority requirement: 2f + 1 out of 3f + 1, or 2/3 of active quorum
        return 2.0 / 3.0

    @staticmethod
    def compute_vote_entropy(approve: float, reject: float, abstain: float, total: float) -> float:
        """Computes Shannon entropy H in bits of the decision distribution."""
        if total <= 0.0:
            return 0.0
        h = 0.0
        for w in (approve, reject, abstain):
            if w > 0.0:
                p = w / total
                h -= p * math.log2(p)
        return h

    def evaluate_round(
        self,
        proposal_id: str,
        ballots: List[Ballot],
    ) -> RoundResult:
        """
        Executes one evaluation round on submitted ballots.
        Enforces single vote per agent, detects Byzantine double-voting or out-of-round ballots,
        and applies circuit breaker invariants.
        """
        round_idx = self.current_round

        if self.state == CircuitState.OPEN:
            # Tripped circuit immediately yields fallback decision without consuming debate
            return RoundResult(
                round_idx=round_idx,
                proposal_id=proposal_id,
                total_weight=0.0,
                approve_weight=0.0,
                reject_weight=0.0,
                abstain_weight=0.0,
                entropy=0.0,
                delta_entropy=0.0,
                consensus_reached=True,
                winning_decision=self.fallback_decision,
                circuit_state=self.state,
                tripped_reason="CIRCUIT_BREAKER_OPEN_FALLBACK_ENGAGED",
                byzantine_flagged_agents=list(self.known_byzantine_agents),
            )

        # 1. Detect Byzantine behavior in current round (Equivocation / Duplicate ballots)
        seen_agents: Dict[str, Ballot] = {}
        byzantine_in_round: Set[str] = set()
        clean_ballots: List[Ballot] = []

        for b in ballots:
            if b.proposal_id != proposal_id or b.round_idx != round_idx:
                # Malformed round or proposal reference
                byzantine_in_round.add(b.agent_id)
                continue

            if b.agent_id in self.known_byzantine_agents:
                # Already quarantined
                continue

            if b.agent_id in seen_agents:
                # Equivocation (double voting) detected
                byzantine_in_round.add(b.agent_id)
            else:
                seen_agents[b.agent_id] = b

        self.known_byzantine_agents.update(byzantine_in_round)

        for agent_id, b in seen_agents.items():
            if agent_id not in byzantine_in_round and agent_id not in self.known_byzantine_agents:
                clean_ballots.append(b)

        # 2. Check if active Byzantine count exceeds theoretical capacity f
        if len(self.known_byzantine_agents) > self.max_faulty_f:
            self.state = CircuitState.OPEN
            res = RoundResult(
                round_idx=round_idx,
                proposal_id=proposal_id,
                total_weight=0.0,
                approve_weight=0.0,
                reject_weight=0.0,
                abstain_weight=0.0,
                entropy=0.0,
                delta_entropy=0.0,
                consensus_reached=True,
                winning_decision=self.fallback_decision,
                circuit_state=self.state,
                tripped_reason=f"BYZANTINE_FAULT_EXCEEDED_BOUND_{len(self.known_byzantine_agents)}_GT_{self.max_faulty_f}",
                byzantine_flagged_agents=sorted(list(self.known_byzantine_agents)),
            )
            self.history.append(res)
            return res

        # 3. Aggregate clean votes
        approve_w = sum(b.weight for b in clean_ballots if b.decision == VoteDecision.APPROVE)
        reject_w = sum(b.weight for b in clean_ballots if b.decision == VoteDecision.REJECT)
        abstain_w = sum(b.weight for b in clean_ballots if b.decision == VoteDecision.ABSTAIN)
        total_w = approve_w + reject_w + abstain_w

        entropy = self.compute_vote_entropy(approve_w, reject_w, abstain_w, total_w)
        delta_entropy = 0.0 if self.prev_entropy is None else abs(self.prev_entropy - entropy)

        # 4. Check Supermajority Consensus
        consensus_reached = False
        winning_decision: Optional[VoteDecision] = None

        if total_w > 0.0:
            if (approve_w / total_w) > self.quorum_threshold:
                consensus_reached = True
                winning_decision = VoteDecision.APPROVE
            elif (reject_w / total_w) > self.quorum_threshold:
                consensus_reached = True
                winning_decision = VoteDecision.REJECT

        # 5. Circuit Breaker Transition Rules
        tripped_reason = None

        if consensus_reached:
            # If in HALF_OPEN and reached clean consensus, reset to CLOSED
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
            self.consecutive_stalls = 0
        else:
            # Check for Zero-Delta Live-lock / Stall
            if self.prev_entropy is not None and delta_entropy < self.entropy_epsilon:
                self.consecutive_stalls += 1
            else:
                self.consecutive_stalls = 0

            # Max rounds boundary check
            if round_idx + 1 >= self.max_rounds:
                self.state = CircuitState.OPEN
                tripped_reason = f"MAX_ROUNDS_REACHED_{self.max_rounds}"
                consensus_reached = True
                winning_decision = self.fallback_decision
            elif self.consecutive_stalls >= self.consecutive_stalls_to_trip:
                self.state = CircuitState.OPEN
                tripped_reason = f"ZERO_DELTA_STALL_CIRCUIT_TRIPPED_{self.consecutive_stalls}_CONSECUTIVE"
                consensus_reached = True
                winning_decision = self.fallback_decision

        self.prev_entropy = entropy
        self.current_round += 1

        result = RoundResult(
            round_idx=round_idx,
            proposal_id=proposal_id,
            total_weight=total_w,
            approve_weight=approve_w,
            reject_weight=reject_w,
            abstain_weight=abstain_w,
            entropy=entropy,
            delta_entropy=delta_entropy,
            consensus_reached=consensus_reached,
            winning_decision=winning_decision,
            circuit_state=self.state,
            tripped_reason=tripped_reason,
            byzantine_flagged_agents=sorted(list(self.known_byzantine_agents)),
        )
        self.history.append(result)
        return result

    def manual_reset_to_half_open(self) -> None:
        """Transitions OPEN circuit into HALF_OPEN probationary mode."""
        if self.state == CircuitState.OPEN:
            self.state = CircuitState.HALF_OPEN
            self.consecutive_stalls = 0
            self.prev_entropy = None
