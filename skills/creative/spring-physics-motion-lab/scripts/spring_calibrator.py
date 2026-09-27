#!/usr/bin/env python3
"""
Spring Physics Parameter Calibrator & Keyframe Synthesizer
Zero-dependency Python CLI tool for calibrating UI spring parameters.
"""

import math
import sys
import json

def calculate_spring_properties(mass: float, stiffness: float, damping: float):
    if mass <= 0:
        raise ValueError("Mass must be positive")
    if stiffness <= 0:
        raise ValueError("Stiffness must be positive")
    if damping < 0:
        raise ValueError("Damping must be non-negative")

    omega_0 = math.sqrt(stiffness / mass)
    zeta = damping / (2.0 * math.sqrt(stiffness * mass))

    if zeta < 1.0:
        regime = "underdamped"
        omega_d = omega_0 * math.sqrt(1.0 - zeta**2)
        freq_hz = omega_d / (2.0 * math.pi)
        # Settle time approx (within 1% threshold)
        settle_time_s = 4.6 / (zeta * omega_0) if (zeta * omega_0) > 0 else 999.0
    elif math.isclose(zeta, 1.0, rel_tol=1e-3):
        regime = "critically_damped"
        freq_hz = 0.0
        settle_time_s = 4.75 / omega_0
    else:
        regime = "overdamped"
        freq_hz = 0.0
        r1 = -omega_0 * (zeta - math.sqrt(zeta**2 - 1.0))
        settle_time_s = 4.6 / abs(r1)

    return {
        "mass": mass,
        "stiffness": stiffness,
        "damping": damping,
        "undamped_frequency_rad_s": round(omega_0, 2),
        "damping_ratio_zeta": round(zeta, 3),
        "regime": regime,
        "oscillation_frequency_hz": round(freq_hz, 2),
        "estimated_settle_time_s": round(settle_time_s, 3)
    }

def simulate_trajectory(mass: float, stiffness: float, damping: float, initial_x=0.0, target_x=1.0, duration=0.8, samples=50):
    dt = duration / samples
    x = initial_x
    v = 0.0
    trajectory = []

    for i in range(samples + 1):
        t = i * dt
        trajectory.append({"time": round(t, 4), "position": round(x, 4), "velocity": round(v, 4)})
        # Semi-implicit Euler
        a = (-stiffness * (x - target_x) - damping * v) / mass
        v += a * dt
        x += v * dt

    return trajectory

def main():
    presets = {
        "snappy": (1.0, 400.0, 38.0),
        "bouncy": (1.0, 250.0, 18.0),
        "gentle": (1.0, 120.0, 16.0),
        "stiff": (1.0, 600.0, 48.0),
        "magnetic": (1.0, 320.0, 26.0)
    }

    if len(sys.argv) > 1 and sys.argv[1] in presets:
        name = sys.argv[1]
        m, k, c = presets[name]
        res = calculate_spring_properties(m, k, c)
        print(f"Preset '{name}':")
        print(json.dumps(res, indent=2))
        return

    # Default audit of all presets
    summary = {}
    for name, (m, k, c) in presets.items():
        summary[name] = calculate_spring_properties(m, k, c)

    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
