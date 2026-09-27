#!/usr/bin/env python3
"""
Bayesian Belief Calibration & Epistemic Uncertainty Quantification Engine.
Autonomous Agent Knowledge Graph & Cross-Session Fact Validation.
Zero external dependencies (pure Python 3.11+ stdlib).
"""

import math
import time
from typing import Dict, Any, List, Optional, Tuple

class BayesianBeliefEngine:
    """
    Manages probabilistic beliefs over assertions and knowledge graph triples.
    
    Belief state:
      beta_alpha (a): accumulated supporting pseudo-observations (> 0)
      beta_beta (b): accumulated contradictory pseudo-observations (> 0)
      expected_p: a / (a + b) (point estimate of probability)
      epistemic_uncertainty: 1.0 / (a + b + 1.0) (epistemic ignorance / sample insufficiency)
      aleatoric_uncertainty: 4.0 * expected_p * (1.0 - expected_p) (intrinsic variance / stochasticity)
      half_life_seconds: temporal decay rate for pseudo-counts towards non-informative prior
    """
    
    def __init__(self, prior_alpha: float = 1.0, prior_beta: float = 1.0, default_half_life: float = 86400.0 * 7.0):
        self.prior_alpha = prior_alpha
        self.prior_beta = prior_beta
        self.default_half_life = default_half_life
        self.beliefs: Dict[str, Dict[str, Any]] = {}

    def register_claim(self, claim_id: str, statement: str, 
                       init_alpha: Optional[float] = None, 
                       init_beta: Optional[float] = None, 
                       half_life_seconds: Optional[float] = None,
                       timestamp: Optional[float] = None) -> Dict[str, Any]:
        """Registers a proposition or fact in the belief registry."""
        t = timestamp if timestamp is not None else time.time()
        a = init_alpha if init_alpha is not None else self.prior_alpha
        b = init_beta if init_beta is not None else self.prior_beta
        hl = half_life_seconds if half_life_seconds is not None else self.default_half_life
        
        self.beliefs[claim_id] = {
            "claim_id": claim_id,
            "statement": statement,
            "alpha": float(a),
            "beta": float(b),
            "last_updated": float(t),
            "half_life_seconds": float(hl),
            "update_count": 0
        }
        return self.get_belief(claim_id, current_time=t)

    def _apply_temporal_decay(self, claim: Dict[str, Any], current_time: float) -> Tuple[float, float]:
        """
        Applies exponential temporal decay towards the uninformative prior (prior_alpha, prior_beta).
        Decays the evidence excess (alpha - prior_alpha, beta - prior_beta).
        """
        dt = max(0.0, current_time - claim["last_updated"])
        hl = claim["half_life_seconds"]
        decay_factor = math.pow(0.5, dt / hl) if hl > 0 else 1.0
        
        excess_a = max(0.0, claim["alpha"] - self.prior_alpha)
        excess_b = max(0.0, claim["beta"] - self.prior_beta)
        
        decayed_alpha = self.prior_alpha + excess_a * decay_factor
        decayed_beta = self.prior_beta + excess_b * decay_factor
        return decayed_alpha, decayed_beta

    def update_evidence(self, claim_id: str, 
                        evidence_type: str, 
                        weight: float = 1.0, 
                        likelihood_ratio: Optional[float] = None,
                        current_time: Optional[float] = None) -> Dict[str, Any]:
        """
        Updates belief using incoming evidence.
        evidence_type:
          - 'supporting': increases alpha by weight
          - 'contradicting': increases beta by weight
          - 'likelihood': multiplies prior odds by likelihood_ratio (Bayesian Odds Form)
        """
        if claim_id not in self.beliefs:
            raise KeyError(f"Claim ID '{claim_id}' not found in registry.")
        
        t = current_time if current_time is not None else time.time()
        claim = self.beliefs[claim_id]
        
        # 1. Decay accumulated excess up to time t
        cur_alpha, cur_beta = self._apply_temporal_decay(claim, t)
        
        # 2. Ingest new evidence
        if evidence_type == "supporting":
            cur_alpha += max(0.0, weight)
        elif evidence_type == "contradicting":
            cur_beta += max(0.0, weight)
        elif evidence_type == "likelihood":
            if likelihood_ratio is None or likelihood_ratio <= 0.0:
                raise ValueError("likelihood_ratio must be positive when evidence_type is 'likelihood'")
            # Transform Beta parameters via likelihood ratio
            # Effective update on Beta distribution maintaining total pseudo-count or scaling odds:
            # posterior_odds = prior_odds * LR
            prior_mean = cur_alpha / (cur_alpha + cur_beta)
            prior_odds = prior_mean / max(1e-12, (1.0 - prior_mean))
            post_odds = prior_odds * likelihood_ratio
            post_mean = post_odds / (1.0 + post_odds)
            total_count = cur_alpha + cur_beta + max(0.0, weight)
            cur_alpha = post_mean * total_count
            cur_beta = (1.0 - post_mean) * total_count
        else:
            raise ValueError(f"Unknown evidence_type '{evidence_type}'. Must be 'supporting', 'contradicting', or 'likelihood'.")
        
        # Clamp minimums
        cur_alpha = max(self.prior_alpha, cur_alpha)
        cur_beta = max(self.prior_beta, cur_beta)
        
        claim["alpha"] = cur_alpha
        claim["beta"] = cur_beta
        claim["last_updated"] = t
        claim["update_count"] += 1
        
        return self.get_belief(claim_id, current_time=t)

    def get_belief(self, claim_id: str, current_time: Optional[float] = None) -> Dict[str, Any]:
        """Returns the current state and epistemic metrics for a claim."""
        if claim_id not in self.beliefs:
            raise KeyError(f"Claim ID '{claim_id}' not found in registry.")
            
        t = current_time if current_time is not None else time.time()
        claim = self.beliefs[claim_id]
        cur_alpha, cur_beta = self._apply_temporal_decay(claim, t)
        
        total_pseudo_count = cur_alpha + cur_beta
        p_mean = cur_alpha / total_pseudo_count
        
        # Variance of Beta distribution: (a*b) / ((a+b)^2 * (a+b+1))
        beta_variance = (cur_alpha * cur_beta) / (math.pow(total_pseudo_count, 2) * (total_pseudo_count + 1.0))
        
        # Epistemic Uncertainty (Uncertainty due to lack of evidence, bounded [0, 1])
        # Decreases asymptotically as total_pseudo_count -> infinity
        epistemic = 1.0 / (total_pseudo_count - (self.prior_alpha + self.prior_beta) + 1.0)
        epistemic = max(0.0, min(1.0, epistemic))
        
        # Aleatoric Uncertainty (Normalized Entropy-like measure: 4 * p * (1 - p))
        # Maximized at p=0.5, minimized at p=0 or p=1
        aleatoric = 4.0 * p_mean * (1.0 - p_mean)
        
        # Qualitative status category
        if epistemic > 0.45:
            status = "UNCERTAIN_INSUFFICIENT_EVIDENCE"
        elif p_mean >= 0.85 and epistemic <= 0.20:
            status = "VERIFIED_HIGH_CONFIDENCE"
        elif p_mean <= 0.15 and epistemic <= 0.20:
            status = "REFUTED_HIGH_CONFIDENCE"
        elif 0.35 <= p_mean <= 0.65:
            status = "DISPUTED_MAXIMAL_VARIANCE"
        else:
            status = "PROVISIONAL"
            
        return {
            "claim_id": claim_id,
            "statement": claim["statement"],
            "alpha": round(cur_alpha, 4),
            "beta": round(cur_beta, 4),
            "expected_probability": round(p_mean, 4),
            "variance": round(beta_variance, 6),
            "epistemic_uncertainty": round(epistemic, 4),
            "aleatoric_uncertainty": round(aleatoric, 4),
            "status": status,
            "update_count": claim["update_count"],
            "last_updated": claim["last_updated"]
        }

    def compute_value_of_information(self, claim_id: str, probe_cost: float, expected_diagnostic_power: float = 0.8) -> Dict[str, Any]:
        """
        Computes the Net Value of Information (VOI) for probing a claim.
        VOI = E[Reduction in Epistemic Uncertainty * Diagnostic Power] - probe_cost
        Returns whether the probe should be executed.
        """
        belief = self.get_belief(claim_id)
        epistemic = belief["epistemic_uncertainty"]
        
        # Expected epistemic reduction if probe executes
        expected_gain = epistemic * expected_diagnostic_power
        net_voi = expected_gain - probe_cost
        
        should_probe = net_voi > 0.0 and epistemic > 0.25
        return {
            "claim_id": claim_id,
            "epistemic_uncertainty": epistemic,
            "probe_cost": probe_cost,
            "expected_gain": round(expected_gain, 4),
            "net_voi": round(net_voi, 4),
            "should_probe": should_probe,
            "recommendation": "EXECUTE_PROBE" if should_probe else "SKIP_PROBE_INSUFFICIENT_VOI"
        }
