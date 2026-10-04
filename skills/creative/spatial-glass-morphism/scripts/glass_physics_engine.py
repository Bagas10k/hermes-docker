#!/usr/bin/env python3
"""
Spatial Fluid Glassmorphism & Depth Physics Engine
Simulates multi-layer optical refraction, chromatic dispersion (Fresnel-Schlick),
specular highlight falloff, and variable blur kernel compositing for visionOS/iOS UI.
"""

import math
from typing import Dict, List, Tuple, Any

class SpatialGlassMaterial:
    """
    Computes optical physical properties for visionOS fluid glass surfaces.
    """
    def __init__(
        self,
        refractive_index: float = 1.52,  # Standard crown glass / optical acrylic
        roughness: float = 0.15,         # Surface microfacet roughness [0.0 - 1.0]
        thickness_mm: float = 4.0,       # Plate thickness in millimeters
        tint_rgba: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 0.08),
        ambient_luminance: float = 0.85
    ):
        self.ior = max(1.0, refractive_index)
        self.roughness = min(1.0, max(0.01, roughness))
        self.thickness = max(0.1, thickness_mm)
        self.tint = tint_rgba
        self.ambient = ambient_luminance

    def fresnel_schlick(self, cos_theta: float, f0_override: float = None) -> float:
        """
        Fresnel-Schlick approximation for reflectance:
        R(theta) = F0 + (1 - F0) * (1 - cos(theta))^5
        """
        cos_t = min(1.0, max(0.0, cos_theta))
        if f0_override is None:
            # Baseline normal incidence reflectance for dielectric
            f0 = ((self.ior - 1.0) / (self.ior + 1.0)) ** 2
        else:
            f0 = f0_override
        return f0 + (1.0 - f0) * math.pow(1.0 - cos_t, 5)

    def chromatic_aberration_offsets(self, view_angle_deg: float) -> Dict[str, float]:
        """
        Calculates wavelength-dependent refraction offsets (RGB dispersion delta).
        Cauchy formula approximation: n(lambda) = A + B / lambda^2
        """
        rad = math.radians(view_angle_deg)
        sin_i = math.sin(rad)
        
        # Wavelength indices for Red (650nm), Green (532nm), Blue (450nm)
        ior_r = self.ior - 0.015
        ior_g = self.ior
        ior_b = self.ior + 0.022
        
        # Snell's law refraction angles: r = asin(sin(i) / n)
        # Lateral shift: d = thickness * sin(i - r) / cos(r)
        def lateral_shift(n: float) -> float:
            sin_r = sin_i / n
            cos_r = math.sqrt(max(0.0, 1.0 - sin_r * sin_r))
            if cos_r < 1e-6:
                return 0.0
            sin_diff = sin_i * cos_r - math.cos(rad) * sin_r
            return (self.thickness * sin_diff) / cos_r

        shift_r = lateral_shift(ior_r)
        shift_g = lateral_shift(ior_g)
        shift_b = lateral_shift(ior_b)

        return {
            "red_shift_px": round(shift_r, 4),
            "green_shift_px": round(shift_g, 4),
            "blue_shift_px": round(shift_b, 4),
            "dispersion_delta_px": round(abs(shift_b - shift_r), 4)
        }

    def specular_highlight_intensity(
        self,
        light_dir: Tuple[float, float, float],
        view_dir: Tuple[float, float, float],
        surface_normal: Tuple[float, float, float] = (0.0, 0.0, 1.0)
    ) -> float:
        """
        Cook-Torrance / GGX microfacet specular highlight:
        D_GGX(m) = alpha^2 / (pi * ((n.h)^2 * (alpha^2 - 1) + 1)^2)
        """
        # Compute half vector H = normalize(L + V)
        hx = light_dir[0] + view_dir[0]
        hy = light_dir[1] + view_dir[1]
        hz = light_dir[2] + view_dir[2]
        len_h = math.sqrt(hx*hx + hy*hy + hz*hz)
        if len_h < 1e-6:
            return 0.0
        h = (hx/len_h, hy/len_h, hz/len_h)

        n_dot_h = max(0.0, surface_normal[0]*h[0] + surface_normal[1]*h[1] + surface_normal[2]*h[2])
        alpha = self.roughness * self.roughness
        alpha2 = alpha * alpha

        denom = (n_dot_h * n_dot_h * (alpha2 - 1.0) + 1.0)
        denom = math.pi * denom * denom
        if denom < 1e-6:
            return 0.0
        d_ggx = alpha2 / denom

        # Geometric shadowing (Smith GGX correlated)
        n_dot_v = max(1e-4, surface_normal[0]*view_dir[0] + surface_normal[1]*view_dir[1] + surface_normal[2]*view_dir[2])
        n_dot_l = max(1e-4, surface_normal[0]*light_dir[0] + surface_normal[1]*light_dir[1] + surface_normal[2]*light_dir[2])
        g_v = n_dot_l * (n_dot_v * (1.0 - alpha) + alpha)
        g_l = n_dot_v * (n_dot_l * (1.0 - alpha) + alpha)
        g_smith = 0.5 / max(1e-6, (g_v + g_l))

        # Fresnel factor
        f_val = self.fresnel_schlick(n_dot_v)

        specular = d_ggx * g_smith * f_val * n_dot_l
        return max(0.0, min(2.5, specular))

    def evaluate_backdrop_blur_kernel(self, target_elevation_dp: float) -> Dict[str, Any]:
        """
        Calculates optimal multi-pass Gaussian blur radius and saturation boost
        to prevent muddy contrast while respecting visionOS glass standards.
        """
        # Blur radius scales with elevation (z-distance) and roughness
        # Base formula: R = clamp(12 + elevation * 1.8 * roughness, 8, 48)
        blur_radius_px = round(max(8.0, min(50.0, 10.0 + target_elevation_dp * 1.4 * self.roughness)), 1)
        
        # Saturation compensates for opacity scattering:
        # Lower opacity requires higher saturation boost to maintain vibrance.
        sat_boost = round(1.0 + (1.0 - self.tint[3]) * 0.45, 2)
        
        # Contrast curve adjustment
        contrast_boost = round(1.0 + (1.0 - self.roughness) * 0.12, 2)

        return {
            "blur_radius_px": blur_radius_px,
            "saturation_ratio": sat_boost,
            "contrast_ratio": contrast_boost,
            "css_backdrop_filter": f"blur({blur_radius_px}px) saturate({int(sat_boost*100)}%) contrast({int(contrast_boost*100)}%)"
        }

    def generate_vision_os_token_spec(self, elevation_tier: int = 1) -> Dict[str, Any]:
        """
        Generates complete CSS design tokens conforming to visionOS / iOS 18 glass depth.
        """
        elevations = {
            1: {"z_index": 10, "dp": 8, "border_alpha": 0.18, "highlight_alpha": 0.45},
            2: {"z_index": 20, "dp": 16, "border_alpha": 0.28, "highlight_alpha": 0.65},
            3: {"z_index": 30, "dp": 28, "border_alpha": 0.38, "highlight_alpha": 0.85}
        }
        tier_cfg = elevations.get(elevation_tier, elevations[1])
        blur_spec = self.evaluate_backdrop_blur_kernel(tier_cfg["dp"])
        fresnel_rim = round(self.fresnel_schlick(0.15), 3)

        return {
            "tier": elevation_tier,
            "background": f"rgba(255, 255, 255, {self.tint[3]:.2f})",
            "backdrop_filter": blur_spec["css_backdrop_filter"],
            "border": f"1px solid rgba(255, 255, 255, {tier_cfg['border_alpha']:.2f})",
            "box_shadow": (
                f"inset 0 1px 1px 0 rgba(255, 255, 255, {tier_cfg['highlight_alpha']:.2f}), "
                f"inset 0 -1px 2px 0 rgba(0, 0, 0, 0.06), "
                f"0 {tier_cfg['dp']//2}px {tier_cfg['dp']*2}px -4px rgba(0, 0, 0, 0.18)"
            ),
            "fresnel_rim_reflectance": fresnel_rim,
            "optical_ior": self.ior
        }

if __name__ == "__main__":
    glass = SpatialGlassMaterial(refractive_index=1.52, roughness=0.18, thickness_mm=4.0)
    print("Glass Material Specs:")
    print("Normal Reflectance (F0):", round(glass.fresnel_schlick(1.0), 4))
    print("Glancing Reflectance (F90):", round(glass.fresnel_schlick(0.0), 4))
    print("Dispersion at 45 deg:", glass.chromatic_aberration_offsets(45.0))
    print("Tokens Tier 2:", glass.generate_vision_os_token_spec(elevation_tier=2))
