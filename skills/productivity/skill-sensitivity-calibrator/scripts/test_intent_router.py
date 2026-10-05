#!/usr/bin/env python3
"""
Deterministic Unit Tests for Bilingual Skill Intent Router
Menguji kebenaran pemetaan dwibahasa ID-EN, penalti konteks, dan batas kepekaan.
"""

import unittest
from intent_router import IntentRouter

class TestIntentRouter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.router = IntentRouter()

    def test_01_colloquial_bento_query(self):
        """Kueri percakapan: 'tata letak bento grid dasbor' wajib merekomendasikan bento-grid-spatial-composer."""
        results = self.router.route("tata letak bento grid dasbor", tier="balanced")
        self.assertGreater(len(results), 0)
        matched_names = [r.name for r in results]
        self.assertIn("bento-grid-spatial-composer", matched_names)
        self.assertGreaterEqual(results[0].score, 0.40)

    def test_02_autopilot_query(self):
        """Kueri percakapan: 'autopilot jalan mandiri tanpa henti' wajib memicu hermes-autopilot."""
        results = self.router.route("autopilot jalan mandiri tanpa henti", tier="balanced")
        self.assertGreater(len(results), 0)
        matched_names = [r.name for r in results]
        self.assertIn("hermes-autopilot", matched_names)

    def test_03_negative_penalty_backend_vs_audio(self):
        """Kueri backend murni tidak boleh memuat skill audio/soundscape."""
        results = self.router.route("perbaiki database sqlite crash dan restart pm2 daemon", tier="sensitive")
        matched_names = [r.name for r in results]
        # Skill audio tidak boleh masuk rekomendasi teratas
        self.assertNotIn("ambient-binaural-soundscape", matched_names)
        self.assertNotIn("songsee", matched_names)

    def test_04_strict_vs_sensitive_tiers(self):
        """Mode STRICT harus menyaring kueri ambigu, sedangkan SENSITIVE meloloskannya."""
        query = "bikin tampilan sederhana"
        strict_res = self.router.route(query, tier="strict")
        sensitive_res = self.router.route(query, tier="sensitive")
        self.assertLessEqual(len(strict_res), len(sensitive_res))

    def test_05_frontend_ui_ux_routing(self):
        """Kueri frontend antarmuka wajib merekomendasikan frontend-agent-craft."""
        query = "bikin tampilan frontend antarmuka yang rapi dan responsif"
        results = self.router.route(query, tier="balanced")
        matched_names = [r.name for r in results]
        self.assertIn("frontend-agent-craft", matched_names)
        self.assertGreaterEqual(results[0].score, 0.40)

if __name__ == "__main__":
    unittest.main()
