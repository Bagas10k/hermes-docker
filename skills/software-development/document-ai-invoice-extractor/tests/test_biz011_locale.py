"""Unit tests for Indonesian locale OCR dialect and noise tolerance verification (BIZ-011)."""
import unittest
from decimal import Decimal
from pathlib import Path
import sys

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from locale_normalizer import IndonesianLocaleOCRNormalizer


class TestIndonesianLocaleOCRNormalizer(unittest.TestCase):
    def setUp(self):
        self.norm = IndonesianLocaleOCRNormalizer

    def test_clean_id_id_numbers_pass_without_anomalies(self):
        cases = [
            ("1.234.567,89", Decimal("1234567.89")),
            ("500.000", Decimal("500000")),
            ("12.500,50", Decimal("12500.50")),
            ("1.000.000.000,00", Decimal("1000000000.00")),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                res = self.norm.inspect_and_clean(raw, "id_ID")
                self.assertEqual(res["decimal_value"], expected)
                self.assertEqual(res["anomalies"], [])
                self.assertFalse(res["requires_review"])

    def test_currency_prefix_cleaned_and_flagged(self):
        cases = [
            ("Rp 1.234.567", Decimal("1234567")),
            ("Rp. 500.000,00", Decimal("500000.00")),
            ("IDR 15.000", Decimal("15000")),
            ("USD 100.50", Decimal("100.50")),
            ("$ 50.25", Decimal("50.25")),
        ]
        for raw, expected in cases[:3]:
            with self.subTest(raw=raw):
                res = self.norm.inspect_and_clean(raw, "id_ID")
                self.assertEqual(res["decimal_value"], expected)
                self.assertTrue(any("currency_prefix_removed" in a for a in res["anomalies"]))
                self.assertTrue(res["requires_review"])

        for raw, expected in cases[3:]:
            with self.subTest(raw=raw):
                res = self.norm.inspect_and_clean(raw, "en_US")
                self.assertEqual(res["decimal_value"], expected)
                self.assertTrue(any("currency_prefix_removed" in a for a in res["anomalies"]))
                self.assertTrue(res["requires_review"])

    def test_indonesian_dash_cents_suffix_normalized(self):
        cases = [
            ("1.500.000,-", Decimal("1500000.00")),
            ("25.000,--", Decimal("25000.00")),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                res = self.norm.inspect_and_clean(raw, "id_ID")
                self.assertEqual(res["decimal_value"], expected)
                self.assertIn("dash_cents_suffix_normalized", res["anomalies"])
                self.assertTrue(res["requires_review"])

    def test_speckle_double_punctuation_collapsed(self):
        cases = [
            ("1..234.567", Decimal("1234567")),
            ("1.234..567,00", Decimal("1234567.00")),
            ("500.000,,50", Decimal("500000.50")),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                res = self.norm.inspect_and_clean(raw, "id_ID")
                self.assertEqual(res["decimal_value"], expected)
                self.assertTrue(any("speckle_double" in a for a in res["anomalies"]))
                self.assertTrue(res["requires_review"])

    def test_whitespace_scanning_jitter_collapsed(self):
        cases = [
            ("1 234 567", Decimal("1234567")),
            ("1. 234. 567", Decimal("1234567")),
            ("1.234. 567, 50", Decimal("1234567.50")),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                res = self.norm.inspect_and_clean(raw, "id_ID")
                self.assertEqual(res["decimal_value"], expected)
                self.assertTrue(any("whitespace" in a for a in res["anomalies"]))
                self.assertTrue(res["requires_review"])

    def test_irregular_grouping_rejected_with_review(self):
        irregular_cases = [
            "1.23.456",     # 2 digits in middle group
            "12.345.6",     # 1 digit in end group
            "1.2345.678",   # 4 digits in group
        ]
        for raw in irregular_cases:
            with self.subTest(raw=raw):
                res = self.norm.inspect_and_clean(raw, "id_ID")
                self.assertIsNone(res["decimal_value"])
                self.assertTrue(res["requires_review"])
                self.assertTrue(any("irregular_grouping" in a for a in res["anomalies"]))

    def test_combined_ocr_speckle_and_prefix_and_dash_suffix(self):
        raw = "Rp. 2..500. 000,-"
        res = self.norm.inspect_and_clean(raw, "id_ID")
        self.assertEqual(res["decimal_value"], Decimal("2500000.00"))
        self.assertTrue(res["requires_review"])
        self.assertGreaterEqual(len(res["anomalies"]), 3)

    def test_parse_with_tolerance_raises_on_unrecoverable(self):
        with self.assertRaises(ValueError):
            self.norm.parse_with_tolerance("NaN", "id_ID")
        with self.assertRaises(ValueError):
            self.norm.parse_with_tolerance("1.23.456", "id_ID")

    def test_unsupported_locale_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.norm.inspect_and_clean("12345", "fr_FR")



    def test_cli_tolerate_noise_flag_end_to_end(self):
        import subprocess, tempfile, json
        script = SCRIPTS / "extract_invoice.py"
        text = (
            "Invoice: INV-ID-001\n"
            "Currency: IDR\n"
            "Item: Layanan Cloud; 2; Rp. 500..000,-; 1.000.000,00\n"
            "Subtotal: Rp. 1.000.000,-\n"
            "Tax: 0\n"
            "Discount: 0\n"
            "Total: 1.000.000,00\n"
        )
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "invoice.txt"
            p.write_text(text)

            # Without --tolerate-noise: exits 2 because invalid item/field
            r_strict = subprocess.run(
                [sys.executable, str(script), str(p), "--locale", "id_ID"],
                capture_output=True, text=True
            )
            self.assertEqual(r_strict.returncode, 2)
            d_strict = json.loads(r_strict.stdout)
            self.assertEqual(d_strict["status"], "needs_review")

            # With --tolerate-noise: arithmetic passes, but flags noise anomalies to needs_review
            r_noisy = subprocess.run(
                [sys.executable, str(script), str(p), "--locale", "id_ID", "--tolerate-noise"],
                capture_output=True, text=True
            )
            self.assertEqual(r_noisy.returncode, 2)
            d_noisy = json.loads(r_noisy.stdout)
            self.assertEqual(d_noisy["status"], "needs_review")
            self.assertTrue(any("ocr_noise_repaired" in issue["code"] for issue in d_noisy["issues"]))
            # Lines parsed correctly
            self.assertEqual(d_noisy["lines"][0]["quantity"], "2")
            self.assertEqual(d_noisy["lines"][0]["unit_price"], "500000.00")
            self.assertEqual(d_noisy["lines"][0]["amount"], "1000000.00")

if __name__ == "__main__":
    unittest.main()
