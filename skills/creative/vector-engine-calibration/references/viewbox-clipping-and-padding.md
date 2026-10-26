# ViewBox Boundary Clipping & Stroke Dilation Calibration

Accurate `viewBox` derivation prevents vector clipping when elements are rotated, scaled, or given heavy stroke outlines.

## 1. The Stroke Dilation Invariant

In standard SVG rendering, an outline stroke is centered on the mathematical path boundary (`stroke-alignment: center`). Half of the stroke width dilates outward, and half dilates inward.

### The Clipping Defect
If an SVG bounding box is calculated strictly from vertex coordinates $[x_{\min}, y_{\min}, x_{\max}, y_{\max}]$:
- An element placed at $x = x_{\min}$ with a `stroke-width: 6px` will have $3\text{px}$ of its outer stroke sliced off by the viewBox boundary ($x = 0$).
- Outer corner miters (`stroke-linejoin="miter"`) extend even further outward by a factor of $\frac{w}{2 \cdot \sin(\theta/2)}$.

---

## 2. Calibrated Bounding Envelope Formula

To ensure zero stroke shearing across all geometric elements:

$$\text{dilation} = \max\left( \frac{\text{stroke\_width}}{2} \cdot \text{miter\_limit}, \quad \text{stroke\_width} \right)$$
$$\text{effective\_pad} = \max\left(\text{min\_padding}, \quad \lceil \text{dilation} \rceil \right)$$

### Python Bounding Accumulator
```python
import math

class CalibratedEnvelope:
    def __init__(self, min_padding=8):
        self.minx = self.miny = float('inf')
        self.maxx = self.maxy = float('-inf')
        self.max_stroke = 0
        self.min_padding = min_padding

    def add_points(self, points, stroke_width=0):
        self.max_stroke = max(self.max_stroke, stroke_width)
        for x, y in points:
            self.minx = min(self.minx, x)
            self.miny = min(self.miny, y)
            self.maxx = max(self.maxx, x)
            self.maxy = max(self.maxy, y)

    def get_viewbox(self):
        stroke_bleed = math.ceil(self.max_stroke / 2.0)
        total_pad = max(self.min_padding, stroke_bleed + 4)

        x0 = math.floor(self.minx - total_pad)
        y0 = math.floor(self.miny - total_pad)
        w = math.ceil(self.maxx + total_pad) - x0
        h = math.ceil(self.maxy + total_pad) - y0

        return f"{x0} {y0} {w} {h}", w, h
```

---

## 3. Responsive Scaling & Aspect Ratio Attributes

To guarantee proper behavior across responsive containers:
1. **Always declare `viewBox` with proportional `width` and `height`:**
   ```xml
   <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="auto">
   ```
2. **Aspect Ratio Preservation:**
   - Standard: `preserveAspectRatio="xMidYMid meet"` (centers content without distortion).
   - Full-bleed background patterns: `preserveAspectRatio="none"` (allows decorative mesh/dividers to stretch to container width).
