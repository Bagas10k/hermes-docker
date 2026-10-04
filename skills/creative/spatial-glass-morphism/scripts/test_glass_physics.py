#!/usr/bin/env python3
import unittest
import math
from glass_physics_engine import SpatialGlassMaterial

class TestSpatialGlassPhysics(unittest.TestCase):
    def setUp(self):
        self.glass = SpatialGlassMaterial(
            refractive_index=1.52,
            roughness=0.15,
            thickness_mm=4.0,
            tint_rgba=(1.0, 1.0, 1.0, 0.10)
        )

    def test_fresnel_boundary_conditions(self):
        # Cos(theta) = 1.0 (normal incidence) -> F0 ~ 0.04258
        f0 = self.glass.fresnel_schlick(1.0)
        expected_f0 = ((1.52 - 1.0) / (1.52 + 1.0)) ** 2
        self.assertAlmostEqual(f0, expected_f0, places=4)

        # Cos(theta) = 0.0 (grazing angle) -> 1.0 (100% reflection)
        f90 = self.glass.fresnel_schlick(0.0)
        self.assertAlmostEqual(f90, 1.0, places=4)

        # Monotonicity check
        f_mid = self.glass.fresnel_schlick(0.5)
        self.assertTrue(f0 < f_mid < f90)

    def test_chromatic_aberration_dispersion(self):
        disp = self.glass.chromatic_aberration_offsets(view_angle_deg=45.0)
        self.assertIn("red_shift_px", disp)
        self.assertIn("blue_shift_px", disp)
        self.assertIn("dispersion_delta_px", disp)
        # Blue has higher IOR -> refracts more sharply than red
        self.assertGreater(disp["blue_shift_px"], disp["red_shift_px"])
        self.assertGreater(disp["dispersion_delta_px"], 0.0)

    def test_specular_highlight_energy_conservation(self):
        light_dir = (0.577, 0.577, 0.577)
        view_dir = (0.0, 0.0, 1.0)
        spec = self.glass.specular_highlight_intensity(light_dir, view_dir)
        self.assertGreaterEqual(spec, 0.0)
        self.assertLessEqual(spec, 2.5)

    def test_backdrop_blur_kernel(self):
        kernel = self.glass.evaluate_backdrop_blur_kernel(target_elevation_dp=16.0)
        self.assertGreaterEqual(kernel["blur_radius_px"], 8.0)
        self.assertLessEqual(kernel["blur_radius_px"], 50.0)
        self.assertGreater(kernel["saturation_ratio"], 1.0)
        self.assertIn("blur(", kernel["css_backdrop_filter"])
        self.assertIn("saturate(", kernel["css_backdrop_filter"])

    def test_vision_os_token_generation(self):
        for tier in [1, 2, 3]:
            tokens = self.glass.generate_vision_os_token_spec(elevation_tier=tier)
            self.assertEqual(tokens["tier"], tier)
            self.assertIn("rgba(255, 255, 255,", tokens["background"])
            self.assertIn("backdrop_filter", tokens)
            self.assertIn("box_shadow", tokens)

if __name__ == "__main__":
    unittest.main()
