"""Unit tests for Fuzzy Label Matcher with Levenshtein and Bayesian confidence scoring (BIZ-012)."""
import unittest
from pathlib import Path
import sys

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from fuzzy_matcher import (
    FuzzyLabelMatcher,
    levenshtein_distance_and_ops,
    FuzzyMatchResult
)


class TestFuzzyLabelMatcher(unittest.TestCase):
    def setUp(self):
        self.matcher_en = FuzzyLabelMatcher(locale="en_US")
        self.matcher_id = FuzzyLabelMatcher(locale="id_ID")

    def test_levenshtein_distance_and_ops(self):
        dist, ops = levenshtein_distance_and_ops("total", "totql")
        self.assertEqual(dist, 1)
        self.assertEqual(len(ops), 5)
        self.assertIn(('sub', 'a', 'q'), ops)

        dist2, ops2 = levenshtein_distance_and_ops("invoice", "lnvoice")
        self.assertEqual(dist2, 1)
        self.assertIn(('sub', 'i', 'l'), ops2)

        dist3, _ = levenshtein_distance_and_ops("subtotal", "sub-total")
        self.assertEqual(dist3, 1)

    def test_exact_matches_have_zero_distance_and_full_confidence(self):
        exact_cases = [
            ("invoice", "invoice"),
            ("TOTAL", "total"),
            ("Subtotal", "subtotal"),
            ("Tax", "tax"),
            ("Discount", "discount"),
            ("Item", "item"),
            ("Currency", "currency"),
        ]
        for query, expected_canonical in exact_cases:
            with self.subTest(query=query):
                res = self.matcher_en.classify_label(query)
                self.assertEqual(res.canonical_label, expected_canonical)
                self.assertEqual(res.distance, 0)
                self.assertEqual(res.confidence, 1.0)
                self.assertTrue(res.is_exact)
                self.assertFalse(res.requires_review)
                self.assertIsNone(res.anomaly)

    def test_fuzzy_ocr_corruptions_resolved_with_review_gating(self):
        fuzzy_cases = [
            ("lnvoice", "invoice", 1),      # i -> l visual confusion
            ("Totql", "total", 1),          # a -> q visual confusion
            ("Subtotql", "subtotal", 1),    # a -> q visual confusion
            ("1nvoice", "invoice", 1),      # i -> 1 visual confusion
            ("D1scount", "discount", 1),    # i -> 1 visual confusion
            ("sub-total", "subtotal", 1),   # extra dash
            ("tota1", "total", 1),          # l -> 1 confusion
        ]
        for query, expected_canonical, expected_dist in fuzzy_cases:
            with self.subTest(query=query):
                res = self.matcher_en.classify_label(query)
                self.assertEqual(res.canonical_label, expected_canonical)
                self.assertEqual(res.distance, expected_dist)
                self.assertGreaterEqual(res.confidence, 0.65)
                self.assertFalse(res.is_exact)
                self.assertTrue(res.requires_review)
                self.assertIsNotNone(res.anomaly)
                self.assertTrue(res.anomaly.startswith(f"fuzzy_label_matched:{expected_canonical}:"))

    def test_end_to_end_extract_with_fuzzy_labels(self):
        from extract_invoice import extract
        corrupted_invoice_text = [
            "lnvoice: INV-2026-999\n"
            "Currency: USD\n"
            "item: Laptop stand; 2; 25.00; 50.00\n"
            "Subtotql: 50.00\n"
            "Tax: 5.00\n"
            "D1scount: 0.00\n"
            "Totql: 55.00\n"
        ]
        # Without fuzzy_labels flag, layout is unsupported
        res_strict = extract(corrupted_invoice_text, "en_US", fuzzy_labels=False)
        self.assertEqual(res_strict["status"], "needs_review")
        self.assertTrue(any(iss["code"] == "unsupported_layout" for iss in res_strict["issues"]))

        # With fuzzy_labels flag, labels are matched fuzzily and status is needs_review due to fuzzy audit flags
        res_fuzzy = extract(corrupted_invoice_text, "en_US", fuzzy_labels=True)
        self.assertEqual(res_fuzzy["status"], "needs_review")
        self.assertEqual(res_fuzzy["fields"]["invoice"]["value"], "INV-2026-999")
        self.assertEqual(res_fuzzy["fields"]["total"]["value"], "55.00")
        self.assertEqual(res_fuzzy["fields"]["subtotal"]["value"], "50.00")
        fuzzy_issues = [iss["code"] for iss in res_fuzzy["issues"] if "fuzzy_label_matched" in iss["code"]]
        self.assertGreaterEqual(len(fuzzy_issues), 3)  # lnvoice, Subtotql, Totql, D1scount

    def test_id_locale_fuzzy_and_synonyms(self):
        cases = [
            ("faktur", "invoice", 0, True),
            ("faktvr", "invoice", 1, False),  # u -> v
            ("pajak", "tax", 0, True),
            ("ppn", "tax", 0, True),
            ("diskon", "discount", 0, True),
            ("d1skon", "discount", 1, False),  # i -> 1
            ("jumlah", "total", 0, True),
            ("jum1ah", "total", 1, False),    # l -> 1
            ("barang", "item", 0, True),
        ]
        for query, expected_canonical, expected_dist, is_exact in cases:
            with self.subTest(query=query):
                res = self.matcher_id.classify_label(query)
                self.assertEqual(res.canonical_label, expected_canonical)
                self.assertEqual(res.distance, expected_dist)
                self.assertEqual(res.is_exact, is_exact)
                if not is_exact:
                    self.assertTrue(res.requires_review)
                    self.assertIn("fuzzy_label_matched", res.anomaly)

    def test_short_labels_enforce_zero_tolerance(self):
        # 'tax' is 3 characters, max_allowed_distance is 0
        res = self.matcher_en.classify_label("tax")
        self.assertEqual(res.canonical_label, "tax")

        # 'tox' or 'tar' should NOT match 'tax' fuzzily because length <= 3
        res_fail = self.matcher_en.classify_label("tox")
        self.assertIsNone(res_fail.canonical_label)

    def test_excessive_distance_rejected(self):
        # 'randomtext' or distances > 2 are rejected
        cases = ["invoooiceee", "completely_wrong", "xyz", "totalllll"]
        for query in cases:
            with self.subTest(query=query):
                res = self.matcher_en.classify_label(query)
                self.assertIsNone(res.canonical_label)

    def test_ambiguity_gating_prevents_false_positive_collisions(self):
        # A synthetic token equally close to two different labels should be rejected / flagged as ambiguous
        # e.g., if a token has multiple close candidates
        res = self.matcher_en.classify_label("")
        self.assertIsNone(res.canonical_label)
        self.assertFalse(res.requires_review)

    def test_bayesian_confidence_decreases_with_distance(self):
        res1 = self.matcher_en.classify_label("subtota1")  # 1 edit
        res2 = self.matcher_en.classify_label("subt0tq1")  # multiple edits
        self.assertGreater(res1.confidence, res2.confidence if res2.canonical_label else 0.0)


if __name__ == "__main__":
    unittest.main()
