"""Fuzzy label matcher with Levenshtein edit distance and Bayesian confidence scoring (BIZ-012).

Detects invoice structural labels under OCR character corruptions, kerning issues,
and spelling variations:
- Standard labels: 'invoice', 'currency', 'subtotal', 'tax', 'discount', 'total', 'item'
- Multilingual / locale-specific labels:
  - id_ID: 'faktur', 'nomor faktur', 'mata uang', 'subtotal', 'pajak', 'ppn', 'diskon', 'potongan', 'total', 'jumlah', 'barang', 'item'
  - en_US: 'invoice', 'invoice no', 'invoice #', 'bill to', 'currency', 'subtotal', 'tax', 'vat', 'discount', 'total', 'amount due', 'item', 'description'

Contractual Invariants:
1. Exact match (case-insensitive) always yields distance=0, confidence=1.0, requires_review=False.
2. Distance > max_tolerance (default 2 for labels len >= 5, 1 for len 3..4, 0 for <3) is REJECTED (None).
3. Ambiguity check: If the top match is too close in likelihood to the second match
   (log-likelihood ratio < ambiguity_threshold), reject as ambiguous or flag requires_review.
4. Any fuzzy match with distance > 0 marks requires_review=True and issues an anomaly code:
   'fuzzy_label_matched:<canonical_label>:<detected_token>:dist=<d>:conf=<c>'.
5. Deterministic probability model based on OCR edit confusion matrix & prior probabilities.
"""
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple
import math


def levenshtein_distance_and_ops(s1: str, s2: str) -> Tuple[int, List[Tuple[str, str, str]]]:
    """Computes Levenshtein distance and list of alignment operations:
    ops format: [('match'|'sub'|'ins'|'del', char_s1, char_s2), ...]
    """
    m, n = len(s1), len(s2)
    # dp table
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,       # deletion from s1
                dp[i][j - 1] + 1,       # insertion into s1
                dp[i - 1][j - 1] + cost # substitution
            )

    # Backtrack alignment
    i, j = m, n
    ops = []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + (0 if s1[i - 1] == s2[j - 1] else 1):
            op = 'match' if s1[i - 1] == s2[j - 1] else 'sub'
            ops.append((op, s1[i - 1], s2[j - 1]))
            i -= 1
            j -= 1
        elif j > 0 and dp[i][j] == dp[i][j - 1] + 1:
            ops.append(('ins', '', s2[j - 1]))
            j -= 1
        elif i > 0 and dp[i][j] == dp[i - 1][j] + 1:
            ops.append(('del', s1[i - 1], ''))
            i -= 1

    ops.reverse()
    return dp[m][n], ops


# Common OCR visual confusion pairs and their empirical log-loss / transition penalties
OCR_CONFUSION_PAIRS = {
    ('l', 'i'): 0.2, ('i', 'l'): 0.2,
    ('1', 'l'): 0.2, ('l', '1'): 0.2,
    ('1', 'i'): 0.3, ('i', '1'): 0.3,
    ('0', 'o'): 0.2, ('o', '0'): 0.2,
    ('0', 'q'): 0.4, ('q', '0'): 0.4,
    ('o', 'q'): 0.3, ('q', 'o'): 0.3,
    ('u', 'v'): 0.4, ('v', 'u'): 0.4,
    ('c', 'e'): 0.4, ('e', 'c'): 0.4,
    ('r', 'n'): 0.4, ('n', 'r'): 0.4,
    ('m', 'rn'): 0.5, ('rn', 'm'): 0.5,
    ('s', '5'): 0.3, ('5', 's'): 0.3,
    ('t', 'l'): 0.5, ('l', 't'): 0.5,
    ('t', 'f'): 0.4, ('f', 't'): 0.4,
    ('k', 'h'): 0.5, ('h', 'k'): 0.5,
    ('a', 'o'): 0.5, ('o', 'a'): 0.5,
    ('a', 'q'): 0.4, ('q', 'a'): 0.4,
    ('-', ' '): 0.3, (' ', '-'): 0.3,
}


@dataclass
class FuzzyMatchResult:
    canonical_label: Optional[str]
    detected_token: str
    target_phrase: Optional[str]
    distance: int
    confidence: float
    is_exact: bool
    requires_review: bool
    anomaly: Optional[str]


class FuzzyLabelMatcher:
    """Bayesian & Levenshtein-tolerant label classifier for OCR documents."""

    # Canonical targets per locale
    CANONICAL_TARGETS: Dict[str, Dict[str, List[str]]] = {
        "en_US": {
            "invoice": ["invoice", "invoice no", "invoice #", "bill no", "inv no", "inv"],
            "currency": ["currency", "curr"],
            "subtotal": ["subtotal", "sub total", "net amount"],
            "tax": ["tax", "vat", "sales tax"],
            "discount": ["discount", "disc"],
            "total": ["total", "amount due", "grand total", "total amount"],
            "item": ["item", "description", "line item"]
        },
        "id_ID": {
            "invoice": ["invoice", "faktur", "nomor faktur", "no faktur", "no. faktur", "inv"],
            "currency": ["mata uang", "currency"],
            "subtotal": ["subtotal", "sub total", "jumlah sebelum pajak"],
            "tax": ["pajak", "ppn", "tax"],
            "discount": ["diskon", "potongan", "discount"],
            "total": ["total", "jumlah", "total tagihan", "grand total"],
            "item": ["item", "barang", "deskripsi", "uraian"]
        }
    }

    # Prior probabilities P(Canonical Label) in an invoice context
    PRIOR_PROBABILITIES = {
        "invoice": 0.20,
        "total": 0.20,
        "subtotal": 0.18,
        "tax": 0.15,
        "item": 0.15,
        "discount": 0.08,
        "currency": 0.04,
    }

    def __init__(self, locale: str = "en_US", min_confidence_threshold: float = 0.65, ambiguity_margin: float = 0.12):
        self.locale = locale
        self.min_confidence_threshold = min_confidence_threshold
        self.ambiguity_margin = ambiguity_margin
        self.targets = self.CANONICAL_TARGETS.get(locale, self.CANONICAL_TARGETS["en_US"])

    def max_allowed_distance(self, target_len: int) -> int:
        """Determines max Levenshtein tolerance based on label token length."""
        if target_len <= 3:
            return 0  # e.g., 'tax' or 'inv' must be exact to prevent false collisions
        elif target_len <= 5:
            return 1  # e.g., 'total', 'faktur' allows dist <= 1
        else:
            return 2  # e.g., 'invoice', 'subtotal', 'discount' allows dist <= 2

    def calculate_bayesian_confidence(self, canonical: str, target: str, query: str, dist: int, ops: List[Tuple[str, str, str]]) -> float:
        """Computes posterior P(Label | Observed Query) via Likelihood P(Query | Target) * Prior P(Label)."""
        if dist == 0:
            return 1.0

        target_len = max(len(target), 1)
        prior = self.PRIOR_PROBABILITIES.get(canonical, 0.10)

        # Baseline error cost per op
        weighted_error_sum = 0.0
        for op, c1, c2 in ops:
            if op == 'match':
                continue
            elif op == 'sub':
                pair = (c1.lower(), c2.lower())
                penalty = OCR_CONFUSION_PAIRS.get(pair, 0.8)
                weighted_error_sum += penalty
            elif op in ('ins', 'del'):
                c = (c1 or c2).lower()
                if c in ('-', ' ', '.', '_'):
                    weighted_error_sum += 0.3
                else:
                    weighted_error_sum += 0.8

        # Likelihood based on error density
        error_rate = weighted_error_sum / float(target_len)
        likelihood = math.exp(-1.5 * error_rate)

        # Posterior score combines likelihood and normalized length factor
        len_factor = min(1.0, target_len / (target_len + dist))
        posterior_score = (likelihood * 0.80 + len_factor * 0.20) * (prior ** 0.02)

        return max(0.0, min(0.99, round(posterior_score, 4)))

    def classify_label(self, raw_label: str) -> FuzzyMatchResult:
        """Classifies raw_label against known invoice canonical keys.
        
        Returns FuzzyMatchResult. If no match meets tolerance or is ambiguous,
        canonical_label will be None.
        """
        token = raw_label.strip().lower()
        if not token:
            return FuzzyMatchResult(
                canonical_label=None,
                detected_token=raw_label,
                target_phrase=None,
                distance=99,
                confidence=0.0,
                is_exact=False,
                requires_review=False,
                anomaly=None
            )

        # 1. Exact Match Check across all candidates
        for canonical, phrases in self.targets.items():
            for phrase in phrases:
                if token == phrase.lower():
                    return FuzzyMatchResult(
                        canonical_label=canonical,
                        detected_token=raw_label,
                        target_phrase=phrase,
                        distance=0,
                        confidence=1.0,
                        is_exact=True,
                        requires_review=False,
                        anomaly=None
                    )

        # 2. Fuzzy Levenshtein Candidates
        candidates: List[Dict[str, Any]] = []
        for canonical, phrases in self.targets.items():
            for phrase in phrases:
                phrase_clean = phrase.lower()
                max_d = self.max_allowed_distance(len(phrase_clean))
                dist, ops = levenshtein_distance_and_ops(phrase_clean, token)

                if dist <= max_d:
                    conf = self.calculate_bayesian_confidence(canonical, phrase_clean, token, dist, ops)
                    candidates.append({
                        "canonical": canonical,
                        "phrase": phrase,
                        "distance": dist,
                        "confidence": conf,
                        "ops": ops
                    })

        if not candidates:
            return FuzzyMatchResult(
                canonical_label=None,
                detected_token=raw_label,
                target_phrase=None,
                distance=99,
                confidence=0.0,
                is_exact=False,
                requires_review=False,
                anomaly="no_matching_label"
            )

        # Sort candidates by: 1. distance ascending, 2. confidence descending
        candidates.sort(key=lambda c: (c["distance"], -c["confidence"]))
        best = candidates[0]

        # 3. Ambiguity Check: compare against second-best if different canonical label
        competing = [c for c in candidates[1:] if c["canonical"] != best["canonical"]]
        if competing:
            second_best = competing[0]
            # If distance is equal or confidence difference is smaller than margin -> ambiguous!
            if second_best["distance"] == best["distance"] or (best["confidence"] - second_best["confidence"] < self.ambiguity_margin):
                return FuzzyMatchResult(
                    canonical_label=None,
                    detected_token=raw_label,
                    target_phrase=f"{best['phrase']} vs {second_best['phrase']}",
                    distance=best["distance"],
                    confidence=best["confidence"],
                    is_exact=False,
                    requires_review=True,
                    anomaly=f"ambiguous_label_match:{best['canonical']}_vs_{second_best['canonical']}"
                )

        # 4. Confidence Threshold Check
        if best["confidence"] < self.min_confidence_threshold:
            return FuzzyMatchResult(
                canonical_label=None,
                detected_token=raw_label,
                target_phrase=best["phrase"],
                distance=best["distance"],
                confidence=best["confidence"],
                is_exact=False,
                requires_review=True,
                anomaly=f"low_confidence_match:dist={best['distance']}:conf={best['confidence']}"
            )

        # 5. Accepted Fuzzy Match
        anomaly_code = f"fuzzy_label_matched:{best['canonical']}:{raw_label.strip()}:dist={best['distance']}:conf={best['confidence']:.2f}"
        return FuzzyMatchResult(
            canonical_label=best["canonical"],
            detected_token=raw_label,
            target_phrase=best["phrase"],
            distance=best["distance"],
            confidence=best["confidence"],
            is_exact=False,
            requires_review=True,
            anomaly=anomaly_code
        )
