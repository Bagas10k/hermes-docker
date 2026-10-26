# Text-to-Path Vectorization & Kinetic Typography Animation

Converting text strings from font tables (TTF/OTF) directly into mathematical SVG vector paths (`<path d="M... C... Z"/>`) enables font-independent rendering, laser stroke draw animations, and per-glyph physics.

## 1. Why Text-to-Path is Superior to `<text>` Tags

In standard SVG, `<text>` relies on fonts installed on the client machine:
- If the font is missing, the browser substitutes a generic fallback, breaking alignment.
- You cannot animate the outline drawing of individual character strokes (`stroke-dashoffset`).
- You cannot apply separate spring physics, 3D rotations, or morphing to individual letters.

Converting text into SVG `<path>` shapes:
1. Renders 100% identically across all devices and OSs with zero font installation required.
2. Allows per-glyph manipulation (`#glyph-0`, `#glyph-1`) with staggered timing.
3. Supports laser stroke reveal animations where letters draw themselves on the screen.

---

## 2. Mathematical Conversion via fontTools

Using `fontTools.ttLib` and `fontTools.pens.svgPathPen.SVGPathPen`:

```python
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

def text_to_svg_paths(text, font_path, font_size=72):
    font = TTFont(font_path)
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    scale = font_size / font['head'].unitsPerEm

    paths = []
    current_x = 0

    for idx, char in enumerate(text):
        if char == " ":
            current_x += font_size * 0.3
            continue
        glyph_name = cmap[ord(char)]
        glyph = glyph_set[glyph_name]

        char_pen = SVGPathPen(glyph_set)
        # Font Y is bottom-up; transform to SVG top-down
        tpen = TransformPen(char_pen, (scale, 0, 0, -scale, current_x, font_size))
        glyph.draw(tpen)
        d = char_pen.getCommands()

        if d:
            paths.append(f'<path id="glyph-{idx}" class="glyph glyph-{idx}" d="{d}"/>')
        current_x += glyph.width * scale

    return paths, current_x
```

---

## 3. Kinetic Animation Modes

### A. Laser Stroke Draw Animation
Simulates laser etching or precision handwriting:
```css
@keyframes drawStroke {
  0% { stroke-dashoffset: 600; fill-opacity: 0; }
  70% { stroke-dashoffset: 0; fill-opacity: 0.2; }
  100% { stroke-dashoffset: 0; fill-opacity: 1; }
}
.glyph {
  stroke: #FA5D29;
  stroke-width: 2;
  stroke-dasharray: 600;
  animation: drawStroke 2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
```

### B. Staggered Wave Bounce
Applies a traveling sine wave across letters in video loops:
$$y_i(t) = A \cdot \sin\left(2\pi t + \frac{2\pi \cdot i}{N}\right)$$
Each letter translates vertically with harmonic phase offset, producing a fluid rolling wave.
