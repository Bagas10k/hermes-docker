"""
Unit tests for ConsensusCircuitBreaker.
Deterministic, non-flaky verification of BFT bounds, entropy delta stall detection,
and circuit breaker state transitions.
"""

import unittest
from multiagent_consensus_circuit_breaker import (
    ConsensusCircuitBreaker,
    Ballot,
    VoteDecision,
    CircuitState,
)


class TestConsensusCircuitBreaker(unittest.TestCase):

    def test_bft_parameter_validation(self):
        # n = 4 nodes allows f = (4 - 1) // 3 = 1
        cb = ConsensusCircuitBreaker(total_nodes=4)
        self.assertEqual(cb.max_faulty_f, 1)

        # Asking for f=2 with n=4 violates n >= 3f + 1
        with self.assertRaises(ValueError):
            ConsensusCircuitBreaker(total_nodes=4, max_faulty_f=2)

        # Invalid node count
        with self.assertRaises(ValueError):
            ConsensusCircuitBreaker(total_nodes=0)

    def test_clean_supermajority_consensus(self):
        # 4 nodes, 3 approve (75% > 66.6%)
        cb = ConsensusCircuitBreaker(total_nodes=4, max_rounds=3)
        ballots = [
            Ballot("a1", 0, "prop-1", VoteDecision.APPROVE),
            Ballot("a2", 0, "prop-1", VoteDecision.APPROVE),
            Ballot("a3", 0, "prop-1", VoteDecision.APPROVE),
            Ballot("a4", 0, "prop-1", VoteDecision.REJECT),
        ]
        res = cb.evaluate_round("prop-1", ballots)
        self.assertTrue(res.consensus_reached)
        self.assertEqual(res.winning_decision, VoteDecision.APPROVE)
        self.assertEqual(res.circuit_state, CircuitState.CLOSED)
        self.assertEqual(res.byzantine_flagged_agents, [])

    def test_byzantine_equivocation_detection(self):
        # Agent a4 submits two different ballots in round 0 (equivocation)
        cb = ConsensusCircuitBreaker(total_nodes=4, max_rounds=3)
        ballots = [
            Ballot("a1", 0, "prop-1", VoteDecision.APPROVE),
            Ballot("a2", 0, "prop-1", VoteDecision.APPROVE),
            Ballot("a3", 0, "prop-1", VoteDecision.APPROVE),
            Ballot("a4", 0, "prop-1", VoteDecision.APPROVE),
            Ballot("a4", 0, "prop-1", VoteDecision.REJECT),  # Double vote
        ]
        res = cb.evaluate_round("prop-1", ballots)
        self.assertIn("a4", res.byzantine_flagged_agents)
        self.assertEqual(res.total_weight, 3.0)  # a4 excluded
        self.assertTrue(res.consensus_reached)
        self.assertEqual(res.winning_decision, VoteDecision.APPROVE)

    def test_byzantine_threshold_breach_trips_circuit(self):
        # 4 nodes (max_faulty_f = 1). If 2 agents cheat, circuit opens immediately
        cb = ConsensusCircuitBreaker(total_nodes=4, max_rounds=3)
        ballots = [
            Ballot("a1", 0, "prop-1", VoteDecision.APPROVE),
            Ballot("a2", 0, "prop-1", VoteDecision.APPROVE),
            Ballot("a3", 0, "prop-1", VoteDecision.APPROVE),
            Ballot("a3", 0, "prop-1", VoteDecision.REJECT),  # cheat 1
            Ballot("a4", 0, "prop-1", VoteDecision.APPROVE),
            Ballot("a4", 0, "prop-1", VoteDecision.REJECT),  # cheat 2
        ]
        res = cb.evaluate_round("prop-1", ballots)
        self.assertEqual(res.circuit_state, CircuitState.OPEN)
        self.assertTrue(res.consensus_reached)
        self.assertEqual(res.winning_decision, VoteDecision.ABSTAIN)
        self.assertIn("BYZANTINE_FAULT_EXCEEDED_BOUND", res.tripped_reason)

    def test_zero_delta_stall_detection(self):
        # 4 nodes, perfectly split 2 vs 2 (entropy constant = 1.0)
        # Should trip circuit on consecutive stall
        cb = ConsensusCircuitBreaker(
            total_nodes=4,
            max_rounds=10,
            consecutive_stalls_to_trip=2,
        )

        def make_split_ballots(r):
            return [
                Ballot("a1", r, "prop-split", VoteDecision.APPROVE),
                Ballot("a2", r, "prop-split", VoteDecision.APPROVE),
                Ballot("a3", r, "prop-split", VoteDecision.REJECT),
                Ballot("a4", r, "prop-split", VoteDecision.REJECT),
            ]

        # Round 0: baseline entropy
        r0 = cb.evaluate_round("prop-split", make_split_ballots(0))
        self.assertFalse(r0.consensus_reached)
        self.assertEqual(r0.circuit_state, CircuitState.CLOSED)

        # Round 1: identical split (stall count = 1)
        r1 = cb.evaluate_round("prop-split", make_split_ballots(1))
        self.assertFalse(r1.consensus_reached)
        self.assertEqual(r1.circuit_state, CircuitState.CLOSED)

        # Round 2: identical split (stall count = 2 -> TRIPPED)
        r2 = cb.evaluate_round("prop-split", make_split_ballots(2))
        self.assertTrue(r2.consensus_reached)
        self.assertEqual(r2.circuit_state, CircuitState.OPEN)
        self.assertEqual(r2.winning_decision, VoteDecision.ABSTAIN)
        self.assertIn("ZERO_DELTA_STALL_CIRCUIT_TRIPPED", r2.tripped_reason)

    def test_max_rounds_hard_timeout(self):
        cb = ConsensusCircuitBreaker(
            total_nodes=4,
            max_rounds=2,
            consecutive_stalls_to_trip=5,  # high so stall doesn't trip first
        )
        # Round 0
        r0 = cb.evaluate_round("prop-x", [
            Ballot("a1", 0, "prop-x", VoteDecision.APPROVE),
            Ballot("a2", 0, "prop-x", VoteDecision.REJECT),
            Ballot("a3", 0, "prop-x", VoteDecision.ABSTAIN),
        ])
        self.assertFalse(r0.consensus_reached)

        # Round 1 (reaches max_rounds=2)
        r1 = cb.evaluate_round("prop-x", [
            Ballot("a1", 1, "prop-x", VoteDecision.APPROVE),
            Ballot("a2", 1, "prop-x", VoteDecision.APPROVE),
            Ballot("a3", 1, "prop-x", VoteDecision.REJECT),
        ])
        self.assertTrue(r1.consensus_reached)
        self.assertEqual(r1.circuit_state, CircuitState.OPEN)
        self.assertEqual(r1.winning_decision, VoteDecision.ABSTAIN)
        self.assertIn("MAX_ROUNDS_REACHED_2", r1.tripped_reason)

    def test_half_open_recovery(self):
        cb = ConsensusCircuitBreaker(total_nodes=4, max_rounds=2)
        # Force OPEN state
        cb.state = CircuitState.OPEN
        self.assertEqual(cb.state, CircuitState.OPEN)

        # Immediate evaluation while OPEN yields fallback
        res = cb.evaluate_round("p", [])
        self.assertEqual(res.winning_decision, VoteDecision.ABSTAIN)

        # Reset to HALF_OPEN
        cb.manual_reset_to_half_open()
        self.assertEqual(cb.state, CircuitState.HALF_OPEN)

        # In HALF_OPEN, if consensus reached, reverts to CLOSED
        ballots = [
            Ballot("a1", cb.current_round, "p", VoteDecision.APPROVE),
            Ballot("a2", cb.current_round, "p", VoteDecision.APPROVE),
            Ballot("a3", cb.current_round, "p", VoteDecision.APPROVE),
            Ballot("a4", cb.current_round, "p", VoteDecision.REJECT),
        ]
        res2 = cb.evaluate_round("p", ballots)
        self.assertTrue(res2.consensus_reached)
        self.assertEqual(res2.winning_decision, VoteDecision.APPROVE)
        self.assertEqual(res2.circuit_state, CircuitState.CLOSED)


if __name__ == "__main__":
    unittest.main()
