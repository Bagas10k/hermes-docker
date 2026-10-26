# Insignia, Badge & Technical Icon Geometry

Generating futuristic cybernetic seals, telemetry badges, and precision UI icons using procedural trigonometry, geometric transformations, and concentric layering.

## 1. Radial Dial & Instrument Geometry

Technical insignias rely on high-precision circular symmetry with angular repetition:

### The Circular Index Formula
Distribute radial tick marks across a complete $360^\circ$ circle ($2\pi$ radians):
- Primary ticks at $30^\circ$ intervals ($\frac{\pi}{6}$ rad): longer stroke length, highlighted with primary accent (`#FA5D29`).
- Secondary ticks at $10^\circ$ intervals ($\frac{\pi}{18}$ rad): shorter stroke length, rendered in muted slate (`#4A5263`).
- Concentric enclosing hairlines: 1.5px circles placed directly inside and outside the tick envelope to form a mechanical dial track.

---

## 2. Rotated Rounded Rectangles (Tactile Diamonds)

Placing a square rotated $45^\circ$ with rounded corners creates an authoritative, scientific diamond emblem:
- Standard implementation:
  ```python
  # Outer cyan frosted diamond
  s.rc(x=0, y=0, w=140, h=140, fill="rgba(25, 28, 36, 0.8)", stroke="#49B3FC", stroke_width=1.5, r=16, rot=45)
  # Inner amber highlight diamond
  s.rc(x=0, y=0, w=100, h=100, fill="rgba(250, 93, 41, 0.08)", stroke="rgba(255,255,255,0.15)", stroke_width=1, r=8, rot=45)
  ```
- By combining rotation (`rot=45`) with corner radii (`r=16`), the resulting geometry avoids sharp stabbing edges while projecting structural solidity.

---

## 3. Dynamic Waveform & Telemetry Splines

To break rigid radial symmetry with dynamic organic life, inject an oscillating horizontal signal path across the center:
- Compute sinusoidal control points:
  $$x_i = -x_{\text{span}} + i \cdot \Delta x$$
  $$y_i = A \cdot \sin(i \cdot \omega)$$
- Feed points into Catmull-Rom spline `pth(pts, stroke="#49B3FC", stroke_width=3, smooth=0.4, closed=False)`.
- Symbolism: Indicates live signal reception, heart rate, radio transmission, or continuous real-time verification.

---

## 4. Architectural Typographic Anchors

Never place floating text arbitrarily inside an insignia. Bind typography to structural geometric poles:
1. **Upper Latitude Anchor:** Positioned at $y = -0.35 \cdot H$, rendered in small capital letters (`font-size=11`, `letter-spacing=2px`) in muted metallic silver (`#8E9AA8`).
2. **Lower Latitude Anchor:** Positioned at $y = +0.42 \cdot H$, rendered in high-contrast accent (`font-size=10`, `letter-spacing=2.5px`) in bright ember (`#FA5D29`).
3. **Centering Standard:** Always set `text-anchor="middle"` so text stays perfectly centered regardless of font metrics variations.
