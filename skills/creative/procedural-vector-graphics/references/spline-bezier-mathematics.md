# Spline & Bezier Mathematics for Procedural Vectors

Mathematical formulas and algorithmic implementations for converting discrete coordinate arrays into organic, infinitely scalable SVG curves.

## 1. Catmull-Rom to Cubic Bezier Splines

Given an ordered sequence of 2D control points $P_0, P_1, \dots, P_{n-1}$:
Standard polygon rendering draws rigid, sharp chords between points. A Catmull-Rom spline interpolates smoothly through every point while maintaining $C^1$ continuity (continuous first derivatives).

### Tangent Vector Calculation
For each interior point $P_k$, the tangent vector $T_k$ is computed using central differences between its adjacent neighbors $P_{k-1}$ and $P_{k+1}$:
$$T_k = \frac{(P_{k+1} - P_{k-1}) \cdot \text{smooth}}{2}$$

For a closed loop of $n$ points:
- Point preceding $P_0$ wraps to $P_{n-1}$.
- Point following $P_{n-1}$ wraps to $P_0$.
- Formula: $\text{index}_{\text{prev}} = (k - 1) \pmod n$, $\text{index}_{\text{next}} = (k + 1) \pmod n$.

### Cubic Bezier Control Points
Each segment between $P_k$ and $P_{k+1}$ is represented as a cubic Bezier curve defined by four points: $[P_k, C_{1,k}, C_{2,k}, P_{k+1}]$.
$$C_{1,k} = P_k + \frac{T_k}{3}$$
$$C_{2,k} = P_{k+1} - \frac{T_{k+1}}{3}$$

In SVG path syntax, this maps directly to the `C` command:
```svg
M P0.x P0.y C C1.x C1.y, C2.x C2.y, P1.x P1.y
```

---

## 2. Smoothing Factor Boundaries

The `smooth` parameter scales tangent magnitude, directly affecting curve curvature:

| Smooth Value | Visual Characteristic | Optimal Use Cases |
|---|---|---|
| `smooth = 0.0` | Zero curvature; sharp linear polygon chords ($M \dots L \dots Z$). | Technical diamonds, mechanical brackets, architectural schematics. |
| `smooth = 0.2` | Subtle corner rounding with tight straight spans. | Mechanical casings, stylized shields, tech chassis. |
| `smooth = 0.35` | Balanced organic curvature without ballooning. | **Default Golden Ratio.** Mascot bodies, character limbs, fruit contours. |
| `smooth = 0.5` | High curvature; bulbous and soft transitions. | Water drops, puffy clouds, liquid jelly blobs. |
| `smooth > 0.6` | **Dangerous Overshoot.** Causes curve looping and self-intersecting loops on acute angles. | Generally avoided in production vector pipelines. |

---

## 3. Trigonometric Radial Projections

To procedurally distribute geometric marks around a central hub (e.g., compass dials, technical tick marks, gear teeth, clock indices):

```python
import math

def radial_ticks(cx, cy, radius_inner, radius_outer, count=36):
    lines = []
    step_rad = (2 * math.pi) / count
    for i in range(count):
        theta = i * step_rad
        x1 = cx + radius_inner * math.cos(theta)
        y1 = cy + radius_inner * math.sin(theta)
        x2 = cx + radius_outer * math.cos(theta)
        y2 = cy + radius_outer * math.sin(theta)
        lines.append(((x1, y1), (x2, y2)))
    return lines
```

---

## 4. Automatic Bounding Box & ViewBox Formulation

Never hardcode arbitrary viewBox bounds when generating procedural geometries. Dynamic bounds prevent clipping and guarantee perfect centering:

1. Maintain bounding accumulators initialized to infinity:
   $$\text{min}_x = \infty, \quad \text{min}_y = \infty, \quad \text{max}_x = -\infty, \quad \text{max}_y = -\infty$$
2. For every drawn shape (including control points of Bezier curves and rotated rectangles), expand the envelope:
   $$\text{min}_x = \min(\text{min}_x, x), \quad \text{max}_x = \max(\text{max}_x, x)$$
3. Compute padded viewBox parameters:
   $$x_0 = \lfloor \text{min}_x - \text{pad} \rfloor, \quad y_0 = \lfloor \text{min}_y - \text{pad} \rfloor$$
   $$W = \lceil \text{max}_x + \text{pad} \rceil - x_0, \quad H = \lceil \text{max}_y + \text{pad} \rceil - y_0$$
4. Output: `viewBox="x0 y0 W H" width="W" height="H"`.
