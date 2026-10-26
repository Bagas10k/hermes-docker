# Spline Tension, Curvature Tuning & Overshoot Prevention

Tuning Catmull-Rom to Cubic Bezier conversions requires balancing organic curvature against mathematical overshoot anomalies.

## 1. The Anatomy of Tangent Overshoot

When converting control points $P_0, P_1, \dots, P_n$ into cubic Bezier segments, the tangent at $P_k$ is computed from neighbors $P_{k-1}$ and $P_{k+1}$:
$$T_k = \frac{(P_{k+1} - P_{k-1}) \cdot \alpha}{2}$$
Where $\alpha$ represents the smoothing tension coefficient.

### The Acute Angle Failure Mode (Loop Inversion)
When the angle $\theta = \angle(P_{k-1}, P_k, P_{k+1})$ is sharp ($\theta < 45^\circ$):
- The vector $(P_{k+1} - P_{k-1})$ points perpendicular to the bisector.
- If $\alpha$ is too high ($\alpha \ge 0.55$), the control points $C_1 = P_k + \frac{T_k}{3}$ extend past the vertex envelope.
- **Result:** The Bezier curve loops back on itself, creating an unintended teardrop knot (*self-intersection loop*) at the vertex.

---

## 2. Dynamic Tangent Damping Algorithm

To guarantee smooth curves on wide arcs while preventing loops on acute corners, calibrate the tension dynamically based on the vertex angle:

```python
import math

def compute_damped_tangent(p_prev, p_curr, p_next, base_smooth=0.35):
    # Vector from prev to curr and curr to next
    v1 = (p_curr[0] - p_prev[0], p_curr[1] - p_prev[1])
    v2 = (p_next[0] - p_curr[0], p_next[1] - p_curr[1])

    # Segment lengths
    d1 = math.hypot(*v1)
    d2 = math.hypot(*v2)

    if d1 < 1e-4 or d2 < 1e-4:
        return (0.0, 0.0)

    # Dot product to calculate angle cosine
    cos_theta = (v1[0] * v2[0] + v1[1] * v2[1]) / (d1 * d2)
    cos_theta = max(-1.0, min(1.0, cos_theta))

    # Angle in radians (0 = straight line, pi = complete hairpin 180 deg reverse)
    turn_angle = math.acos(cos_theta)

    # Angle damping factor: reduce smooth as turn approaches acute hairpin
    damping = 1.0 - (turn_angle / math.pi) * 0.65
    effective_smooth = base_smooth * max(0.2, damping)

    # Central difference tangent
    raw_tx = (p_next[0] - p_prev[0]) * effective_smooth / 2.0
    raw_ty = (p_next[1] - p_prev[1]) * effective_smooth / 2.0

    return (raw_tx, raw_ty)
```

---

## 3. Calibration Test Matrix

| Shape Profile | Point Coordinates | Uncalibrated ($\alpha = 0.6$) | Calibrated ($\alpha = 0.35$ + Damping) | Status |
|---|---|---|---|---|
| **Acute Arrow** | `[(0,0), (10, 50), (20, 0)]` | Unwanted loop knot | Crisp rounded vertex | **CALIBRATED** |
| **Right Triangle** | `[(0,0), (50, 0), (0, 50)]` | Bulbous ballooning | Architectural soft bevel | **CALIBRATED** |
| **Organic Belly** | Circular 8-point polygon | Smooth plump curve | Smooth plump curve | **OPTIMAL** |
| **Waveform** | `sin(x)` sine oscillation | Phase shift distortion | Pure harmonic wave | **OPTIMAL** |
